"""Three read-only MCP tools for searching, reading and tracking Mistral's documentation.

Tools identify pages by URL and sections by the keys printed with search hits.
Answer generation and citation verification remain in the package and HTTP API (D-044).
What each tool does and prints lives in ``glossator.surface``; this module
configures the server, registers the tools and serves them.
"""

import argparse
import asyncio
import os
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import mcp.types as mt
import structlog
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from fastmcp.tools.base import ToolResult
from starlette.applications import Starlette
from starlette.middleware import Middleware as StarletteMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response

from entrypoints.mcp_http import FAVICON_SVG, BearerAuthMiddleware, landing_page
from glossator import history as history_service
from glossator import package_version
from glossator.answer.config import DEFAULT_VARIANT
from glossator.corpus.snapshots import configured_manifest
from glossator.index.variants import VARIANTS
from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.engine import SearchEngine
from glossator.retrieval.probe import check_embedding_once
from glossator.surface import history_render, read, search
from glossator.surface.context import Surface
from glossator.surface.descriptions import DESCRIPTIONS, instructions
from glossator.surface.errors import SurfaceError
from glossator.surface.history import query_history, resolve_history_form
from glossator.surface.names import HISTORY, READ_PAGE, SEARCH, TOOL_ORDER
from glossator.surface.pages import PageCatalog
from glossator.surface.params import guard_arguments

load_dotenv()
logger = structlog.get_logger(__name__)

if not os.environ.get("MISTRAL_API_KEY"):
    raise RuntimeError("MISTRAL_API_KEY is not set. Check your .env file.")

_variant_name = os.environ.get("GLOSSATOR_VARIANT", DEFAULT_VARIANT)
if _variant_name not in VARIANTS:
    raise RuntimeError(
        f"GLOSSATOR_VARIANT={_variant_name!r} is unknown; known variants: {sorted(VARIANTS)}"
    )
CORPUS_DIR = Path(os.environ.get("GLOSSATOR_CORPUS_DIR", "corpus/mistral-docs"))
SNAPSHOT_MANIFEST = configured_manifest()
_MCP_TOKEN = os.environ.get("GLOSSATOR_MCP_TOKEN", "")

SERVER_NAME = "mistral-docs"
SERVER_TITLE = "Mistral documentation search"
REPOSITORY_URL = "https://github.com/T0mSIlver/glossator"

_TOOL_TITLES = {
    SEARCH: "Search Mistral documentation",
    READ_PAGE: "Read a documentation page",
    HISTORY: "Track documentation changes",
}


def _parse_tool_allowlist(raw: str) -> frozenset[str]:
    """GLOSSATOR_MCP_TOOLS names the tools to register; empty means all.

    The evaluation harness serves one arm of a consumer run per deployment
    (D-040), so a disabled tool is absent from discovery rather than an error.
    """
    names = {item.strip() for item in raw.split(",") if item.strip()}
    if not names:
        return frozenset(TOOL_ORDER)
    unknown = sorted(names - set(TOOL_ORDER))
    if unknown:
        raise RuntimeError(
            f"GLOSSATOR_MCP_TOOLS names unknown tools {unknown}; known: {list(TOOL_ORDER)}"
        )
    return frozenset(names)


_ENABLED_TOOLS = _parse_tool_allowlist(os.environ.get("GLOSSATOR_MCP_TOOLS", ""))
if SEARCH not in _ENABLED_TOOLS:
    raise RuntimeError(f"GLOSSATOR_MCP_TOOLS must include {SEARCH}")

_engine = SearchEngine(RetrievalConfig.shipped(variant=_variant_name, rerank=False))
_ADMISSION_SLOTS = 4
_admission = asyncio.Semaphore(_ADMISSION_SLOTS)
_catalog = PageCatalog.load(CORPUS_DIR)
_PAGE_SIZES = _catalog.sizes

# The per-call budgets are module attributes read on every call, so a test can
# lower one without rebuilding the server.
READ_MAX_CHARS = read.READ_MAX_CHARS
HISTORY_MAX_CHARS = history_render.HISTORY_MAX_CHARS


def _surface() -> Surface:
    return Surface(
        engine=_engine,
        pages=_catalog,
        admission=_admission,
        admission_slots=_ADMISSION_SLOTS,
        enabled=_ENABLED_TOOLS,
        read_max_chars=READ_MAX_CHARS,
        history_max_chars=HISTORY_MAX_CHARS,
        snapshot_manifest=SNAPSHOT_MANIFEST,
    )


def _tool_error(error: SurfaceError) -> ToolError:
    return ToolError("\n".join([f"error: {error.code}", error.message, f"next: {error.next_hint}"]))


def _instructions() -> str:
    return instructions(len(_PAGE_SIZES), _ENABLED_TOOLS)


mcp: FastMCP = FastMCP(SERVER_NAME, instructions=_instructions())


class _ParamGuard(Middleware):
    """Unknown argument names are a typed error naming the likely parameter."""

    def __init__(self, server: FastMCP) -> None:
        self.server = server

    async def on_call_tool(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        call_next: CallNext[mt.CallToolRequestParams, ToolResult],
    ) -> ToolResult:
        name = context.message.name
        tool = await self.server.get_tool(name)
        if tool is None:
            return await call_next(context)
        arguments = dict(context.message.arguments or {})
        try:
            context.message.arguments = guard_arguments(
                name, arguments, tool.parameters["properties"]
            )
        except SurfaceError as exc:
            raise _tool_error(exc) from exc
        return await call_next(context)


mcp.add_middleware(_ParamGuard(mcp))


async def mistral_docs_search(q: str = "", max_hits: int = 5, under: str | None = None) -> str:
    try:
        return await search.search(_surface(), q, max_hits, under)
    except SurfaceError as exc:
        raise _tool_error(exc) from exc


async def mistral_docs_read_page(
    page_url: str, section: str | None = None, lang: str = "python"
) -> str:
    try:
        return await read.read_page(_surface(), page_url, section, lang)
    except SurfaceError as exc:
        raise _tool_error(exc) from exc


async def mistral_docs_history(
    text: str | None = None,
    page_url: str | None = None,
    section: str | None = None,
    under: str | None = None,
    since: str | None = None,
) -> str:
    surface = _surface()
    try:
        form = resolve_history_form(text, page_url, section, under, since)
        result = await query_history(form, surface.snapshot_manifest)
    except SurfaceError as exc:
        raise _tool_error(exc) from exc
    return history_render.render_history(form, result, surface.history_max_chars)


_TOOL_IMPLS: dict[str, Callable[..., Awaitable[str]]] = {
    SEARCH: mistral_docs_search,
    READ_PAGE: mistral_docs_read_page,
    HISTORY: mistral_docs_history,
}
TOOL_ANNOTATIONS = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
}
"""Every tool reads one pinned corpus. Without these hints a host asks the user
to approve every call (D-037b) and a headless consumer never calls at all
(D-037c)."""

for _tool_name in TOOL_ORDER:
    if _tool_name in _ENABLED_TOOLS:
        _impl = _TOOL_IMPLS[_tool_name]
        _impl.__doc__ = DESCRIPTIONS[_tool_name]
        mcp.tool(title=_TOOL_TITLES[_tool_name], annotations=TOOL_ANNOTATIONS)(_impl)


@mcp.custom_route("/health", methods=["GET"])
async def _mcp_health(request: Request) -> Response:
    """Unauthenticated, for the Connectors Debugger and the tunnel (D-037)."""
    try:
        chunks = await asyncio.wait_for(_engine.document_count(), timeout=5.0)
    except Exception as exc:
        logger.warning("MCP health count failed", error=str(exc))
        chunks = None
    try:
        probe = await check_embedding_once(_variant_name)
        probe_passed: bool | None = True
        probe_detail: dict[str, Any] = probe.as_dict()
    except Exception as exc:
        probe_passed = False
        probe_detail = {"error": str(exc)}
    return JSONResponse(
        {
            "status": "ok" if chunks is not None and probe_passed else "degraded",
            "name": SERVER_NAME,
            "title": SERVER_TITLE,
            "variant": _variant_name,
            "pages": len(_PAGE_SIZES),
            "chunks": chunks,
            "snapshots": history_service.snapshot_availability(SNAPSHOT_MANIFEST),
            "embedding_probe": {"passed": probe_passed, **probe_detail},
            "tools": [name for name in TOOL_ORDER if name in _ENABLED_TOOLS],
            "version": package_version(),
        }
    )


@mcp.custom_route("/favicon.svg", methods=["GET"])
@mcp.custom_route("/favicon.ico", methods=["GET"])
async def _favicon(request: Request) -> Response:
    return Response(FAVICON_SVG, media_type="image/svg+xml")


@mcp.custom_route("/", methods=["GET"])
async def _landing(request: Request) -> Response:
    tools = [name for name in TOOL_ORDER if name in _ENABLED_TOOLS]
    return HTMLResponse(landing_page(SERVER_TITLE, len(_PAGE_SIZES), tools, REPOSITORY_URL))


def http_middleware() -> list[StarletteMiddleware]:
    if not _MCP_TOKEN:
        logger.warning("GLOSSATOR_MCP_TOKEN is not set; the MCP HTTP server is open to any client.")
        return []
    return [StarletteMiddleware(BearerAuthMiddleware, token=_MCP_TOKEN)]


def build_http_app() -> Starlette:
    """The Starlette app the HTTP transport serves, with auth when configured."""
    return mcp.http_app(middleware=http_middleware())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Mistral documentation MCP server.")
    parser.add_argument(
        "--http", action="store_true", help="Serve Streamable HTTP instead of stdio."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    asyncio.run(check_embedding_once(_variant_name))
    if args.http:
        mcp.run(transport="http", host=args.host, port=args.port, middleware=http_middleware())
    else:
        mcp.run()
