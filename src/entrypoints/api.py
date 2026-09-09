"""FastAPI routes for retrieval, cited answers, health, and version data."""

import asyncio
import json
import os
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Annotated, Any, Literal

import structlog
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from mistralai.search.toolkit.retrieval.errors import RetrieverException
from mistralai.search.toolkit.search.errors import IndexException, SourceNotFoundError
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from entrypoints.param_suggestions import suggest_fields
from glossator.answer import service as answer_service
from glossator.answer.config import DEFAULT_VARIANT, PRICES, AnswerConfig
from glossator.answer.llm import CALL_ERRORS
from glossator.index.variants import VARIANTS, get_variant
from glossator.retrieval.config import KINDS, RetrievalConfig
from glossator.retrieval.engine import SearchEngine
from glossator.retrieval.probe import check_embedding_once

load_dotenv(override=True)

logger = structlog.get_logger(__name__)

PAGE_SECTION_CAP = 100


def _package_version() -> str:
    try:
        return version("glossator")
    except PackageNotFoundError:  # running from a source tree without metadata
        return "0.0.0+unknown"


PACKAGE_VERSION = _package_version()


def _corpus_dir() -> Path:
    return Path(os.environ.get("GLOSSATOR_CORPUS_DIR", "corpus/mistral-docs"))


class ApiError(Exception):
    """One typed failure: a code, a message, and the next call to make."""

    def __init__(self, status_code: int, code: str, message: str, next_hint: str):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.next_hint = next_hint


def _error_body(
    code: str, message: str, next_hint: str | None, request_id: str | None
) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message}
    if next_hint:
        error["next"] = next_hint
    if request_id:
        error["request_id"] = request_id
    return {"error": error}


class EngineRegistry:
    """Engines are cheap to hold and expensive to rebuild; one per variant.

    ``engines`` is the injection seam the tests use: a pre-built (fake) engine
    under a variant name is served as-is and the real one is never built.
    """

    def __init__(self) -> None:
        self.engines: dict[str, Any] = {}

    def get(self, variant: str) -> SearchEngine:
        _require_variant(variant)
        engine = self.engines.get(variant)
        if engine is None:
            engine = SearchEngine(RetrievalConfig(variant=variant))
            self.engines[variant] = engine
        return engine


def _require_variant(variant: str) -> None:
    try:
        get_variant(variant)
    except ValueError as exc:
        raise ApiError(
            400,
            "E_BAD_PARAM",
            str(exc),
            next_hint=f"use one of {sorted(VARIANTS)}",
        ) from exc


class AskRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    question: str = Field(min_length=1, max_length=2000)
    strategy: str = "single_pass"
    variant: str = DEFAULT_VARIANT
    model: str | None = None


class SearchRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    query: str = Field(min_length=1, max_length=2000)
    top_k: Annotated[int, Field(ge=1, le=100)] = 10
    kinds: frozenset[str] = frozenset()
    locales: frozenset[str] = frozenset()
    exclude_ids: list[str] = Field(default_factory=list)
    variant: str = DEFAULT_VARIANT


_BODY_MODELS: dict[str, type[BaseModel]] = {"/ask": AskRequest, "/search": SearchRequest}
"""Route path -> its request model, so validation errors can suggest field names."""


class HitOut(BaseModel):
    model_config = ConfigDict(frozen=True)

    chunk_id: str
    score: float
    url: str
    anchor: str | None
    citation_url: str
    heading_path: list[str]
    page_title: str
    kind: str
    locale: str
    preview: str
    source_id: str
    start_offset: int | None
    end_offset: int | None


class SearchResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    query: str
    variant: str
    hits: list[HitOut]


class SectionOut(BaseModel):
    model_config = ConfigDict(frozen=True)

    section_index: int | None
    chunk_id: str
    heading_path: list[str]
    anchor: str | None
    citation_url: str
    start_offset: int | None
    end_offset: int | None
    content: str


class PageResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str
    title: str
    sections: list[SectionOut]
    truncated: bool


class VariantHealth(BaseModel):
    model_config = ConfigDict(frozen=True)

    schema_name: str
    documents: int | None


class HealthResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: Literal["ok", "degraded", "down"]
    vespa: Literal["reachable", "unreachable"]
    default_variant: str
    variants: dict[str, VariantHealth]
    embedding_probe: dict[str, Any]
    corpus: dict[str, Any] | None
    version: str


class VersionResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    version: str
    variants: list[str]
    generation_models: list[str]


registry = EngineRegistry()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # A startup probe that fails degrades /health instead of killing the
    # process: an operator can then see what is broken through the API itself,
    # which never answers if the lifespan raises (D-031).
    probe: dict[str, Any] = {"status": "passed"}
    try:
        if not registry.engines:
            registry.get(DEFAULT_VARIANT)
        probe.update((await check_embedding_once(DEFAULT_VARIANT)).as_dict())
    except Exception as exc:
        probe = {"status": "failed", "error": str(exc)}
        logger.warning("Startup probe failed", default_variant=DEFAULT_VARIANT, error=str(exc))
    app.state.embedding_probe = probe
    logger.info("Startup", default_variant=DEFAULT_VARIANT, variants=sorted(VARIANTS))
    yield


app = FastAPI(
    title="glossator",
    version=PACKAGE_VERSION,
    description="Answers technical questions over Mistral's documentation, with cited sources.",
    lifespan=lifespan,
)
app.state.engines = registry


@app.middleware("http")
async def request_id_middleware(request: Request, call_next: Any) -> Any:
    """Echo or mint an X-Request-Id; it rides the logs and every response."""
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:16]
    request.state.request_id = request_id
    structlog.contextvars.bind_contextvars(request_id=request_id)
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    logger.info(
        "Request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=round((time.perf_counter() - started) * 1000, 1),
    )
    structlog.contextvars.unbind_contextvars("request_id")
    return response


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.code, exc.message, exc.next_hint, request_id),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    model = _BODY_MODELS.get(request.url.path)
    known = set(model.model_fields) if model is not None else set()
    fields: list[str] = []
    suggestions: list[str] = []
    for error in exc.errors():
        field = ".".join(str(part) for part in error["loc"][1:]) or str(error["loc"][0])
        if error["type"] == "extra_forbidden" and known:
            right = suggest_fields([field], known)[0]
            suggestions.append(right)
        fields.append(field)
    next_hint = "the response's 'message' names the fields; see /openapi.json for the schema"
    if suggestions:
        next_hint = (
            f"did you mean {'; '.join(suggestions)}? "
            f"{request.url.path} accepts: {', '.join(sorted(known))}; "
            "unknown names are rejected, not applied; see /openapi.json for the schema"
        )
    return JSONResponse(
        status_code=422,
        content=_error_body(
            "E_BAD_PARAM",
            f"invalid request: {', '.join(fields)}",
            next_hint,
            getattr(request.state, "request_id", None),
        ),
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error", error=str(exc))
    return JSONResponse(
        status_code=500,
        content=_error_body(
            "E_INTERNAL",
            "the request failed in an unexpected way; it has been logged",
            "retry; if it repeats, check GET /health before reporting",
            getattr(request.state, "request_id", None),
        ),
    )


def _answer_config(model: str | None) -> AnswerConfig:
    """Build a validated answer configuration for one request."""
    return AnswerConfig(model=model) if model is not None else AnswerConfig()


_ASK_UPSTREAM_ERRORS: tuple[type[Exception], ...] = (
    RetrieverException,
    IndexException,
    RuntimeError,
    *CALL_ERRORS,
)
"""What the answer path fails with that is upstream's fault rather than a bug
here: retrieval and index errors, a missing key, and every generation-client
error after the service layer has exhausted its own retries."""


@app.post("/ask")
async def ask(body: AskRequest, request: Request) -> dict[str, Any]:
    if body.strategy not in answer_service.STRATEGIES:
        raise ApiError(
            400,
            "E_BAD_PARAM",
            f"unknown strategy {body.strategy!r}",
            next_hint=f"use one of {sorted(answer_service.STRATEGIES)}",
        )
    engine = registry.get(body.variant)
    try:
        config = _answer_config(body.model)
    except ValidationError as exc:
        raise ApiError(
            400,
            "E_BAD_PARAM",
            str(exc),
            next_hint=f"model must be one of {sorted(PRICES)}",
        ) from exc
    try:
        answer = await answer_service.ask(
            body.question,
            strategy=body.strategy,
            variant=body.variant,
            engine=engine,
            config=config,
        )
    except _ASK_UPSTREAM_ERRORS as exc:
        # CALL_ERRORS are the generation client's own failures (a zero-quota
        # 429 included, D-017a); they reach here only after the service layer
        # exhausted its retries, so the caller hears 503, not a 500 the
        # /health dashboard cannot explain.
        raise ApiError(
            503,
            "E_UPSTREAM",
            f"answer generation failed: {exc}",
            "retry the identical request; if it repeats, check GET /health",
        ) from exc
    payload: dict[str, Any] = answer.model_dump()
    for citation in payload["citations"]:
        citation["citation_url"] = _citation_url(citation["url"], citation["anchor"])
    for citation in payload["trace"]["unverified_citations"]:
        if citation["url"]:
            citation["citation_url"] = _citation_url(citation["url"], citation["anchor"])
    payload["trace_summary"] = answer.trace.summary()
    payload["request_id"] = request.state.request_id
    return payload


def _citation_url(url: str, anchor: str | None) -> str:
    return f"{url}#{anchor}" if anchor else url


def _hit_out(hit: Any) -> HitOut:
    return HitOut(
        chunk_id=hit.chunk_id,
        score=hit.score,
        url=hit.url,
        anchor=hit.anchor,
        citation_url=hit.citation_url,
        heading_path=list(hit.heading_path),
        page_title=hit.page_title,
        kind=hit.kind,
        locale=hit.locale,
        preview=hit.preview(),
        source_id=hit.source_id,
        start_offset=hit.start_offset,
        end_offset=hit.end_offset,
    )


@app.post("/search", response_model=SearchResponse)
async def search(body: SearchRequest) -> SearchResponse:
    bad_kinds = sorted(body.kinds - KINDS)
    if bad_kinds:
        raise ApiError(
            400,
            "E_BAD_PARAM",
            f"unknown page kind(s) {bad_kinds}",
            next_hint=f"kinds are {sorted(KINDS)}; omit for no filter",
        )
    # First, so an unknown variant never surfaces as a locale hint: the config
    # constructor validates the variant too, but with a message this handler
    # would wrongly answer as if locales were the problem.
    _require_variant(body.variant)
    try:
        RetrievalConfig(
            variant=body.variant,
            top_k=body.top_k,
            kinds=body.kinds,
            locales=body.locales,
        )
    except ValidationError as exc:
        raise ApiError(
            400,
            "E_BAD_PARAM",
            str(exc),
            "locales look like 'en' or 'pt-BR'; kinds are doc, api, model",
        ) from exc
    engine = registry.get(body.variant)
    try:
        hits = await engine.search(
            body.query,
            exclude_ids=set(body.exclude_ids) or None,
            top_k=body.top_k,
            kinds=body.kinds or None,
            locales=body.locales or None,
        )
    except RetrieverException as exc:
        raise ApiError(
            503,
            "E_UPSTREAM",
            f"search failed: {exc}",
            "retry the identical request; if it repeats, check GET /health",
        ) from exc
    return SearchResponse(
        query=body.query,
        variant=body.variant,
        hits=[_hit_out(hit) for hit in hits],
    )


@app.get("/pages/{page_path:path}", response_model=PageResponse)
async def page(
    page_path: str,
    variant: str = DEFAULT_VARIANT,
    start_offset: Annotated[int, Query(ge=0)] = 0,
    top_k: Annotated[int, Query(ge=1, le=PAGE_SECTION_CAP)] = PAGE_SECTION_CAP,
) -> PageResponse:
    """One page's sections in reading order; `start_offset` continues a truncated
    read from the last returned section's `end_offset`, mirroring MCP read."""
    clean = page_path.strip("/")
    if not clean:
        raise ApiError(
            404,
            "E_UNKNOWN_PAGE",
            "no page path given",
            next_hint="page paths look like 'api/endpoint/chat'; POST /search finds the right one",
        )
    url = f"https://docs.mistral.ai/{clean}"
    engine = registry.get(variant)
    try:
        sections = await engine.navigation_at(url).read(start_offset or None, None, top_k=top_k)
    except SourceNotFoundError as exc:
        raise ApiError(
            404,
            "E_UNKNOWN_PAGE",
            f"no indexed page at /{clean}",
            "use the url exactly as a search hit printed it; POST /search to find pages",
        ) from exc
    except IndexException as exc:
        raise ApiError(
            503,
            "E_UPSTREAM",
            f"page read failed: {exc}",
            "retry the identical request; if it repeats, check GET /health",
        ) from exc
    if not sections:
        raise ApiError(
            404,
            "E_UNKNOWN_PAGE",
            f"no indexed page at /{clean}",
            next_hint="use the url exactly as a search hit printed it; POST /search to find pages",
        )
    return PageResponse(
        url=url,
        title=sections[0].page_title,
        sections=[
            SectionOut(
                section_index=hit.section_index,
                chunk_id=hit.chunk_id,
                heading_path=list(hit.heading_path),
                anchor=hit.anchor,
                citation_url=hit.citation_url,
                start_offset=hit.start_offset,
                end_offset=hit.end_offset,
                content=hit.content,
            )
            for hit in sections
        ],
        truncated=len(sections) == top_k,
    )


def _corpus_info() -> dict[str, Any] | None:
    manifest_path = _corpus_dir() / "manifest.json"
    if not manifest_path.is_file():
        return None
    try:
        pages = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    commits = {page.get("source_commit") for page in pages if page.get("source_commit")}
    kinds: dict[str, int] = {}
    for page_ in pages:
        kind = str(page_.get("kind", "?"))
        kinds[kind] = kinds.get(kind, 0) + 1
    return {
        "pages": len(pages),
        "source_commit": sorted(commits)[0] if len(commits) == 1 else sorted(commits),
        "source_repo": "mistralai/platform-docs-public",
        "license": "Apache-2.0",
        "kinds": kinds,
    }


async def _variant_health(name: str) -> tuple[VariantHealth, bool]:
    """One variant's document count, or the failure of asking for it."""
    try:
        count = await asyncio.wait_for(registry.get(name).document_count(), timeout=5.0)
    except Exception as exc:
        logger.warning("Health probe failed", variant=name, error=str(exc))
        return VariantHealth(schema_name=VARIANTS[name].schema_name, documents=None), False
    return VariantHealth(schema_name=VARIANTS[name].schema_name, documents=count), True


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    # Concurrently: three serial 5 s timeouts are a 15 s answer, and a health
    # endpoint that slow is its own outage.
    names = sorted(VARIANTS)
    probed = await asyncio.gather(*(_variant_health(name) for name in names))
    counts = {name: health_ for name, (health_, _ok) in zip(names, probed, strict=True)}
    reachable = sum(1 for _health, ok in probed if ok)
    vespa: Literal["reachable", "unreachable"] = "reachable" if reachable else "unreachable"
    probe = getattr(app.state, "embedding_probe", {"status": "not_run"})
    # "not_run" is the un-started state (the lifespan has not answered yet), not
    # a failure; only a probe that ran and failed degrades the verdict.
    status: Literal["ok", "degraded", "down"] = (
        "ok"
        if reachable == len(VARIANTS) and probe.get("status") != "failed"
        else "degraded"
        if reachable
        else "down"
    )
    if status == "down":
        raise ApiError(
            503,
            "E_UPSTREAM",
            "Vespa is not reachable; no index variant answered a count query",
            next_hint="start it with `make setup-vespa`, then retry GET /health",
        )
    # Read per request, so a corpus refresh shows without a restart and the
    # directory can move through GLOSSATOR_CORPUS_DIR.
    return HealthResponse(
        status=status,
        vespa=vespa,
        default_variant=DEFAULT_VARIANT,
        variants=counts,
        embedding_probe=probe,
        corpus=await asyncio.to_thread(_corpus_info),
        version=PACKAGE_VERSION,
    )


@app.get("/version", response_model=VersionResponse)
async def version_route() -> VersionResponse:
    return VersionResponse(
        name="glossator",
        version=PACKAGE_VERSION,
        variants=sorted(VARIANTS),
        generation_models=sorted(PRICES),
    )


__all__ = ["app", "registry"]
