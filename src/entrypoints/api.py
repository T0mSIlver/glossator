"""FastAPI routes for retrieval, cited answers, history, health, and version data.

Each route validates its request model and calls ``glossator.surface``; a
``SurfaceError`` becomes a typed JSON error with the status its code maps to.
"""

import asyncio
import os
import time
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Any, Literal

import structlog
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.responses import Response

from glossator import history as history_service
from glossator import package_version
from glossator.answer.cite import CiteQuote, CiteResult
from glossator.answer.config import DEFAULT_VARIANT, PRICES
from glossator.corpus.snapshots import configured_manifest
from glossator.index.variants import VARIANTS
from glossator.retrieval.engine import Hit
from glossator.retrieval.probe import check_embedding_once
from glossator.surface import answers
from glossator.surface.engines import EngineRegistry
from glossator.surface.errors import ErrorCode, SurfaceError
from glossator.surface.health import corpus_summary, variant_documents
from glossator.surface.history import query_history, resolve_history_form
from glossator.surface.params import invalid_body
from glossator.surface.read import page_sections
from glossator.surface.search import search_hits

load_dotenv()

logger = structlog.get_logger(__name__)

PAGE_SECTION_CAP = 100
PACKAGE_VERSION = package_version()

_STATUS: dict[ErrorCode, int] = {
    "E_BAD_PARAM": 400,
    "E_UNKNOWN_PAGE": 404,
    "E_BUSY": 503,
    "E_UPSTREAM": 503,
}


def _corpus_dir() -> Path:
    return Path(os.environ.get("GLOSSATOR_CORPUS_DIR", "corpus/mistral-docs"))


def _error_response(
    request: Request, status_code: int, code: str, message: str, next_hint: str
) -> JSONResponse:
    """The one error shape every route answers with, carrying the request ID."""
    error: dict[str, Any] = {"code": code, "message": message}
    if next_hint:
        error["next"] = next_hint
    request_id = getattr(request.state, "request_id", None)
    if request_id:
        error["request_id"] = request_id
    return JSONResponse(status_code=status_code, content={"error": error})


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


class CiteRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    draft: str = Field(min_length=1, max_length=200000)
    quotes: list[CiteQuote] = Field(default_factory=list, max_length=100)
    variant: str = DEFAULT_VARIANT


class CiteResponse(CiteResult):
    model_config = ConfigDict(frozen=True)

    request_id: str


_BODY_MODELS: dict[str, type[BaseModel]] = {
    "/ask": AskRequest,
    "/search": SearchRequest,
    "/cite": CiteRequest,
}


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
    snapshots: dict[str, int]
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
async def request_id_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
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


@app.exception_handler(SurfaceError)
async def surface_error_handler(request: Request, exc: SurfaceError) -> JSONResponse:
    return _error_response(request, _STATUS[exc.code], exc.code, exc.message, exc.next_hint)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    model = _BODY_MODELS.get(request.url.path)
    known = set(model.model_fields) if model is not None else set()
    error = invalid_body(request.url.path, known, exc.errors())
    return _error_response(request, 422, error.code, error.message, error.next_hint)


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error", error=str(exc))
    return _error_response(
        request,
        500,
        "E_INTERNAL",
        "the request failed in an unexpected way; it has been logged",
        "retry; if it repeats, check GET /health before reporting",
    )


@app.post("/ask")
async def ask(body: AskRequest, request: Request) -> dict[str, Any]:
    answer = await answers.ask(
        registry, body.question, strategy=body.strategy, variant=body.variant, model=body.model
    )
    return answers.answer_payload(answer, request.state.request_id)


@app.post("/cite", response_model=CiteResponse)
async def cite(body: CiteRequest, request: Request) -> CiteResponse:
    """Verify a consumer's own quotes against the chunks they name.

    The consumer gathered context itself through ``POST /search`` and
    ``GET /pages``; this route checks each submitted quote against the chunk
    (or page) it claims to come from and names the draft markers no verified
    quote covers. It never rewrites the answer and never calls a model.
    """
    result = await answers.cite(registry, body.draft, list(body.quotes), variant=body.variant)
    return CiteResponse(**result.model_dump(), request_id=request.state.request_id)


def _out[M: BaseModel](model: type[M], hit: Hit, **computed: Any) -> M:
    """A response model filled from the hit's attributes of the same names."""
    fields = {name: getattr(hit, name) for name in model.model_fields if name not in computed}
    return model(**fields, **computed)


@app.post("/search", response_model=SearchResponse)
async def search(body: SearchRequest) -> SearchResponse:
    hits = await search_hits(
        registry,
        body.query,
        variant=body.variant,
        top_k=body.top_k,
        kinds=body.kinds,
        locales=body.locales,
        exclude_ids=set(body.exclude_ids) or None,
    )
    return SearchResponse(
        query=body.query,
        variant=body.variant,
        hits=[_out(HitOut, hit, preview=hit.preview()) for hit in hits],
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
    url, sections = await page_sections(
        registry, page_path, variant=variant, start_offset=start_offset, top_k=top_k
    )
    return PageResponse(
        url=url,
        title=sections[0].page_title,
        sections=[_out(SectionOut, hit) for hit in sections],
        truncated=len(sections) == top_k,
    )


@app.get("/history")
async def history(
    text: str | None = None,
    page_url: str | None = None,
    section: str | None = None,
    under: str | None = None,
    since: str | None = None,
) -> dict[str, object]:
    """Track a phrase, a page or section key, or changes under a path."""
    form = resolve_history_form(text, page_url, section, under, since)
    return await query_history(form, configured_manifest())


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    # Concurrently: three serial 5 s timeouts are a 15 s answer, and a health
    # endpoint that slow is its own outage.
    names = sorted(VARIANTS)
    documents = await asyncio.gather(*(variant_documents(registry, name) for name in names))
    counts = {
        name: VariantHealth(schema_name=VARIANTS[name].schema_name, documents=count)
        for name, count in zip(names, documents, strict=True)
    }
    reachable = sum(1 for count in documents if count is not None)
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
        raise SurfaceError(
            "E_UPSTREAM",
            "Vespa is not reachable; no index variant answered a count query",
            "start it with `make setup-vespa`, then retry GET /health",
        )
    # Read per request, so a corpus refresh shows without a restart and the
    # directory can move through GLOSSATOR_CORPUS_DIR.
    return HealthResponse(
        status=status,
        vespa=vespa,
        default_variant=DEFAULT_VARIANT,
        variants=counts,
        embedding_probe=probe,
        corpus=await asyncio.to_thread(corpus_summary, _corpus_dir()),
        snapshots=history_service.snapshot_availability(configured_manifest()),
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
