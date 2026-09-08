"""FastAPI service over the glossator engine.

One engine per index variant, built lazily and shared by every route; ``ask``
goes through :mod:`glossator.answer.service` so the API, the CLI and the eval
grid make the same call. Handlers are async end to end — the engine and the
answer service are async, and a sync call in the request path would block the
event loop for the length of a model round-trip.

Errors share one JSON shape, code + message + ``next`` hint, so a client can
react to the code without parsing prose.
"""

import asyncio
import json
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Annotated, Any, Literal

import structlog
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from glossator.answer import service as answer_service
from glossator.answer.config import DEFAULT_VARIANT, PRICES, AnswerConfig, ModelPrice
from glossator.index.variants import VARIANTS, get_variant
from glossator.retrieval.config import KINDS, RetrievalConfig
from glossator.retrieval.engine import SearchEngine

load_dotenv(override=True)

logger = structlog.get_logger(__name__)

CORPUS_DIR = Path("corpus/mistral-docs")
PAGE_SECTION_CAP = 100


def _package_version() -> str:
    try:
        return version("glossator")
    except PackageNotFoundError:  # running from a source tree without metadata
        return "0.0.0+unknown"


# ---------------------------------------------------------------------------
# Typed errors
# ---------------------------------------------------------------------------


class ApiError(Exception):
    """One typed failure: a code, a message, and the next call to make."""

    def __init__(self, status_code: int, code: str, message: str, next_hint: str | None = None):
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


# ---------------------------------------------------------------------------
# The engine registry: one SearchEngine per variant, built lazily
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Request and response models
# ---------------------------------------------------------------------------


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
    corpus: dict[str, Any] | None
    version: str


class VersionResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    version: str
    variants: list[str]
    generation_models: list[str]


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

registry = EngineRegistry()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Fail fast on a missing key, the way the MCP server does; Vespa is not
    # contacted until the first query, so it is probed by /health, not here.
    if not registry.engines:
        registry.get(DEFAULT_VARIANT)
    logger.info("Startup", default_variant=DEFAULT_VARIANT, variants=sorted(VARIANTS))
    yield


app = FastAPI(
    title="glossator",
    version=_package_version(),
    description="Answers technical questions over Mistral's documentation, with cited sources.",
    lifespan=lifespan,
)
app.state.engines = registry


@app.middleware("http")
async def request_id_middleware(request: Request, call_next: Any) -> Any:
    """Echo or mint an X-Request-Id; it rides the logs and every response."""
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:16]
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
    request_id = request.headers.get("x-request-id") or getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.code, exc.message, exc.next_hint, request_id),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    fields = ", ".join(
        ".".join(str(part) for part in error["loc"][1:]) or str(error["loc"][0])
        for error in exc.errors()
    )
    return JSONResponse(
        status_code=422,
        content=_error_body(
            "E_BAD_PARAM",
            f"invalid request: {fields}",
            "the response's 'message' names the fields; see /openapi.json for the schema",
            request.headers.get("x-request-id"),
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
            request.headers.get("x-request-id"),
        ),
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


def _answer_config(model: str | None) -> AnswerConfig:
    """AnswerConfig for the request, pricing any model the default table lacks at zero.

    The account's free tier (D-017a) makes reachable-but-unpriced model ids the
    normal case for live checks, and token usage is recorded either way, so an
    unknown id is priced at 0 with a log line rather than rejected here — the
    API itself will say whether the id exists.
    """
    if model is None:
        return AnswerConfig()
    if model in PRICES:
        return AnswerConfig(model=model)
    logger.warning("No price for model, cost recorded as zero", model=model)
    return AnswerConfig(
        model=model,
        prices={**PRICES, model: ModelPrice(input_usd_per_mtok=0.0, output_usd_per_mtok=0.0)},
    )


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
    answer = await answer_service.ask(
        body.question,
        strategy=body.strategy,
        variant=body.variant,
        engine=engine,
        config=_answer_config(body.model),
    )
    payload: dict[str, Any] = answer.model_dump()
    for citation in payload["citations"]:
        citation["citation_url"] = _citation_url(citation["url"], citation["anchor"])
    for citation in payload["trace"]["unverified_citations"]:
        if citation["url"]:
            citation["citation_url"] = _citation_url(citation["url"], citation["anchor"])
    payload["trace_summary"] = answer.trace.summary()
    payload["request_id"] = request.headers.get("x-request-id")
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
    try:
        RetrievalConfig(
            variant=body.variant,
            top_k=body.top_k,
            kinds=body.kinds,
            locales=body.locales,
        )
    except ValidationError as exc:
        raise ApiError(400, "E_BAD_PARAM", str(exc)) from exc
    engine = registry.get(body.variant)
    hits = await engine.search(
        body.query,
        exclude_ids=set(body.exclude_ids) or None,
        top_k=body.top_k,
        kinds=body.kinds or None,
        locales=body.locales or None,
    )
    return SearchResponse(
        query=body.query,
        variant=body.variant,
        hits=[_hit_out(hit) for hit in hits],
    )


@app.get("/pages/{page_path:path}", response_model=PageResponse)
async def page(page_path: str, variant: str = DEFAULT_VARIANT) -> PageResponse:
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
    sections = await engine.navigation_at(url).read(None, None, top_k=PAGE_SECTION_CAP)
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
        truncated=len(sections) == PAGE_SECTION_CAP,
    )


def _corpus_info() -> dict[str, Any] | None:
    manifest_path = CORPUS_DIR / "manifest.json"
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


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    counts: dict[str, VariantHealth] = {}
    reachable = 0
    for name in sorted(VARIANTS):
        try:
            count = await asyncio.wait_for(registry.get(name).document_count(), timeout=5.0)
        except Exception as exc:
            logger.warning("Health probe failed", variant=name, error=str(exc))
            counts[name] = VariantHealth(schema_name=VARIANTS[name].schema_name, documents=None)
        else:
            reachable += 1
            counts[name] = VariantHealth(schema_name=VARIANTS[name].schema_name, documents=count)
    vespa: Literal["reachable", "unreachable"] = "reachable" if reachable else "unreachable"
    status: Literal["ok", "degraded", "down"] = (
        "ok" if reachable == len(VARIANTS) else "degraded" if reachable else "down"
    )
    if status == "down":
        raise ApiError(
            503,
            "E_UPSTREAM",
            "Vespa is not reachable; no index variant answered a count query",
            next_hint="start it with `make setup-vespa`, then retry GET /health",
        )
    return HealthResponse(
        status=status,
        vespa=vespa,
        default_variant=DEFAULT_VARIANT,
        variants=counts,
        corpus=_corpus_info(),
        version=_package_version(),
    )


@app.get("/version", response_model=VersionResponse)
async def version_route() -> VersionResponse:
    return VersionResponse(
        name="glossator",
        version=_package_version(),
        variants=sorted(VARIANTS),
        generation_models=sorted(PRICES),
    )


__all__ = ["app", "registry"]
