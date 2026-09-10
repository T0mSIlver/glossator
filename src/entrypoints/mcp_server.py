"""Three read-only MCP tools for searching, reading and tracking Mistral's documentation.

Tools identify sections only by their docs.mistral.ai ``url#anchor``. Answer
generation and citation verification remain in the package and HTTP API (D-044).
"""

import argparse
import asyncio
import hmac
import json
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
from mistralai.search.toolkit.retrieval.errors import RetrieverException
from mistralai.search.toolkit.search.errors import IndexException, SourceNotFoundError
from starlette.applications import Starlette
from starlette.middleware import Middleware as StarletteMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send

from entrypoints.param_suggestions import suggest_fields
from glossator import history as history_service
from glossator import package_version
from glossator.answer.config import DEFAULT_VARIANT
from glossator.answer.context import chunk_body
from glossator.corpus.snapshots import configured_manifest
from glossator.index.variants import VARIANTS
from glossator.ingest.pages import iter_page_paths, load_page
from glossator.retrieval.config import KINDS, RetrievalConfig
from glossator.retrieval.engine import Hit, SearchEngine
from glossator.retrieval.probe import check_embedding_once

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

SEARCH = "mistral_docs_search"
READ_PAGE = "mistral_docs_read_page"
HISTORY = "mistral_docs_history"
_TOOL_ORDER = (SEARCH, READ_PAGE, HISTORY)
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
        return frozenset(_TOOL_ORDER)
    unknown = sorted(names - set(_TOOL_ORDER))
    if unknown:
        raise RuntimeError(
            f"GLOSSATOR_MCP_TOOLS names unknown tools {unknown}; known: {list(_TOOL_ORDER)}"
        )
    return frozenset(names)


_ENABLED_TOOLS = _parse_tool_allowlist(os.environ.get("GLOSSATOR_MCP_TOOLS", ""))
if SEARCH not in _ENABLED_TOOLS:
    raise RuntimeError(f"GLOSSATOR_MCP_TOOLS must include {SEARCH}")

_engine = SearchEngine(RetrievalConfig.shipped(variant=_variant_name, rerank=False))

_ADMISSION_SLOTS = 4
_admission = asyncio.Semaphore(_ADMISSION_SLOTS)

MAX_HITS = 20
SNIPPET_CHARS = 400
READ_MAX_CHARS = 24_000
"""Per-call ceiling on a page read. Three pages in four are under it whole;
the rest arrive section by section (D-043)."""
LARGE_PAGE_CHARS = 32_000
"""A page this long is read by section: a hit on it says so, and read_page
without a section returns the first part with the remaining sections named."""
READ_TOP_K = 400
"""Vespa's configured hit limit; the longest page holds under a hundred chunks."""
HISTORY_MAX_CHARS = 12_000
DIFF_LIMIT_NOTE = f"note: diff cut at {history_service.DIFF_MAX_CHARS} characters"


def _page_sizes() -> dict[str, int]:
    """Characters of markdown per page URL, from the vendored corpus."""
    sizes: dict[str, int] = {}
    if not CORPUS_DIR.is_dir():
        return sizes
    for path in iter_page_paths(CORPUS_DIR):
        page = load_page(path)
        sizes[page.url] = len(page.body)
    return sizes


_PAGE_SIZES = _page_sizes()


def _is_large(url: str) -> bool:
    return _PAGE_SIZES.get(url, 0) >= LARGE_PAGE_CHARS


def _error(code: str, message: str, next_hint: str) -> ToolError:
    return ToolError("\n".join([f"error: {code}", message, f"next: {next_hint}"]))


def _bad_param(message: str, next_hint: str) -> ToolError:
    return _error("E_BAD_PARAM", message, next_hint)


def _unknown_page(page_url: str) -> ToolError:
    return _error(
        "E_UNKNOWN_PAGE",
        f'no indexed page has the URL "{page_url}".',
        f"pass a page URL exactly as a {SEARCH} hit printed it, without the #anchor.",
    )


def _busy() -> ToolError:
    return _error(
        "E_BUSY",
        f"the server is already running {_ADMISSION_SLOTS} concurrent calls.",
        "retry the identical call; do not reformulate it.",
    )


def _upstream(operation: str, cause: Exception) -> ToolError:
    logger.warning("Upstream failure", operation=operation, error=str(cause))
    return _error(
        "E_UPSTREAM",
        f"{operation} failed against the search index: {cause}",
        "retry the identical call; if it repeats, say the documentation server is down.",
    )


class _admission_or_busy:
    async def __aenter__(self) -> None:
        if _admission.locked():
            raise _busy()
        await _admission.acquire()

    async def __aexit__(self, *exc: object) -> None:
        _admission.release()


def _instructions() -> str:
    """The rules for a host that reads nothing but this string (D-037a)."""
    pages = len(_PAGE_SIZES)
    scope = f"{pages} pages of Mistral's documentation" if pages else "Mistral's documentation"
    steps = [f"{SEARCH} finds the sections that state a fact"]
    if READ_PAGE in _ENABLED_TOOLS:
        steps.append(f"{READ_PAGE} reads the page a hit is on")
    if HISTORY in _ENABLED_TOOLS:
        steps.append(f"{HISTORY} shows when a fact or a section changed")
    return (
        f"Searches {scope} (docs.mistral.ai guides, API reference, model cards) at a "
        "pinned commit. Use it for any question about Mistral models, the API, SDKs, "
        "pricing, limits, Studio, Work, Vibe or La Plateforme.\n\n"
        f"{'; '.join(steps)}.\n\n"
        "Cite the url#anchor a hit printed, as a Markdown link, next to each claim it "
        "supports. Never write a docs.mistral.ai URL from memory. When the documentation "
        "does not answer the question, say so instead of answering from memory."
    )


mcp: FastMCP = FastMCP(SERVER_NAME, instructions=_instructions())


class _ParamGuard(Middleware):
    """Unknown argument names are a typed error naming the likely parameter.

    Arguments whose name starts with an underscore belong to the host: Mistral
    Work sends `_confirmationReason` on the call that asks the user for
    approval (D-037b). They are dropped before validation.
    """

    def __init__(self, server: FastMCP) -> None:
        self.server = server

    async def on_call_tool(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        call_next: CallNext[mt.CallToolRequestParams, ToolResult],
    ) -> ToolResult:
        name = context.message.name
        arguments = dict(context.message.arguments or {})
        tool = await self.server.get_tool(name)
        if tool is None:
            return await call_next(context)
        for key in [k for k in arguments if k.startswith("_")]:
            arguments.pop(key)
        context.message.arguments = arguments
        known = set(tool.parameters["properties"])
        unknown = [k for k in arguments if k not in known]
        if unknown:
            suggestions = suggest_fields(unknown, known)
            raise _bad_param(
                f"unknown parameter(s) for {name}: {', '.join(unknown)}; the call was not run.",
                ("did you mean " + ", ".join(suggestions) + "? " if suggestions else "")
                + f"{name} accepts: {', '.join(sorted(known))}.",
            )
        return await call_next(context)


mcp.add_middleware(_ParamGuard(mcp))


def _section_header(hit: Hit, n: int | None = None) -> list[str]:
    prefix = f"[{n}] " if n is not None else "## "
    lines = [f"{prefix}{hit.citation_url}"]
    if hit.heading_line:
        lines.append(f"    {hit.heading_line}")
    return lines


def _snippet(hit: Hit) -> str:
    body = chunk_body(hit)
    # The heading path above the snippet already names the section, so a
    # leading markdown heading line would only repeat it.
    if body.lstrip().startswith("#"):
        body = body.lstrip().split("\n", 1)[1] if "\n" in body.lstrip() else ""
    text = " ".join(body.split())
    if len(text) > SNIPPET_CHARS:
        return text[:SNIPPET_CHARS].rstrip() + " …"
    return text


def _distinct_sections(hits: list[Hit]) -> list[Hit]:
    """One hit per section, at its best rank. A long section is several chunks
    and they crowd the top of the ranking (D-012a); the model reads the section
    once either way."""
    seen: set[str] = set()
    kept: list[Hit] = []
    for hit in hits:
        key = hit.citation_url
        if key in seen:
            continue
        seen.add(key)
        kept.append(hit)
    return kept


def _section_key(hit: Hit) -> str | None:
    """What read_page's `section` accepts for this chunk: its anchor, or the
    heading text when the page's headings carry no anchor (D-003a)."""
    if hit.anchor:
        return hit.anchor
    return hit.heading_path[-1] if hit.heading_path else None


def _section_matches(hit: Hit, wanted: str) -> bool:
    key = _section_key(hit)
    if key is None:
        return False
    return key.casefold() == wanted.casefold()


def _large_page_line(hit: Hit) -> str:
    key = _section_key(hit)
    section = f', section="{key}"' if key else ""
    return f'    large page: {READ_PAGE}(page_url="{hit.url}"{section}) reads this section'


def _search_description() -> str:
    return f"""Search Mistral's documentation for the sections that state something.
    Each hit prints its url#anchor, its heading path and a snippet.

    USE WHEN: the question is about a Mistral model, parameter, limit, price,
    error or product feature.

    DO NOT USE: to read a page you already hold a hit on ({READ_PAGE}).

    Args:
        q: Two or three distinctive words.
        max_hits: Hits to return, 1-{MAX_HITS}.
        kind: Keep only "doc", "api" or "model" pages. Omit for all.
    """


async def mistral_docs_search(q: str, max_hits: int = 5, kind: str | None = None) -> str:
    if not q.strip():
        raise _bad_param("q is empty.", "send two or three distinctive words in q.")
    if kind is not None and kind not in KINDS:
        raise _bad_param(
            f'unknown kind "{kind}".', 'kind is "doc", "api" or "model"; omit it for all pages.'
        )
    top_k = max(1, min(MAX_HITS, max_hits))
    async with _admission_or_busy():
        try:
            ranked = await _engine.search(
                q, top_k=top_k * 3, rerank=False, kinds=frozenset({kind}) if kind else None
            )
        except RetrieverException as exc:
            raise _upstream(f"search({q!r})", exc) from exc
    hits = _distinct_sections(ranked)[:top_k]
    lines = [f"q: {json.dumps(q)}" + (f" | kind: {kind}" if kind else ""), ""]
    for n, hit in enumerate(hits, 1):
        lines.extend(_section_header(hit, n))
        lines.append(f"    {_snippet(hit)}")
        if _is_large(hit.url):
            lines.append(_large_page_line(hit))
        lines.append("")
    if not hits:
        lines.append("Results: no section matched.")
        lines.append(
            "next: search again with other words from the question; if nothing matches, "
            "the documentation does not cover it."
        )
        return "\n".join(lines)
    lines.append(f"Results: {len(hits)} hits")
    if READ_PAGE in _ENABLED_TOOLS:
        first = hits[0]
        target = f'page_url="{first.url}"'
        key = _section_key(first)
        if _is_large(first.url) and key:
            target += f', section="{key}"'
        lines.append(f"next: {READ_PAGE}({target}) to read hit 1 on its page")
    return "\n".join(lines)


def _read_page_description() -> str:
    return f"""Read one Mistral documentation page in reading order, or one section of it.

    USE WHEN: a search hit names the page and you need the surrounding text,
    a table, or a code block before answering.

    DO NOT USE: to find where something is said ({SEARCH}).

    Args:
        page_url: The page URL exactly as a hit printed it, without the #anchor.
        section: An anchor from a hit's url#anchor, to read that section and its
            neighbours instead of the whole page.
    """


async def mistral_docs_read_page(page_url: str, section: str | None = None) -> str:
    page_url = page_url.split("#", 1)[0].strip()
    if not page_url:
        raise _bad_param("page_url is empty.", f"pass a page URL from a {SEARCH} hit.")
    async with _admission_or_busy():
        try:
            navigation = _engine.navigation_at(page_url)
            chunks = await navigation.read(None, None, top_k=READ_TOP_K)
        except SourceNotFoundError as exc:
            raise _unknown_page(page_url) from exc
        except IndexException as exc:
            raise _upstream(f"read_page({page_url!r})", exc) from exc
    if not chunks:
        raise _unknown_page(page_url)
    title = chunks[0].page_title
    if section is not None:
        wanted = section.strip().lstrip("#")
        positions = [i for i, hit in enumerate(chunks) if _section_matches(hit, wanted)]
        if not positions:
            keys = list(dict.fromkeys(k for k in map(_section_key, chunks) if k))
            raise _bad_param(
                f'page {page_url} has no section "{wanted}".',
                f"sections on this page: {', '.join(keys) or '(none)'}; "
                "omit section to read the whole page.",
            )
        start = max(0, positions[0] - 1)
        stop = min(len(chunks), positions[-1] + 2)
        selected = chunks[start:stop]
        heading = f'page: {page_url} | "{title}" | section: {wanted}'
    else:
        selected = chunks
        heading = f'page: {page_url} | "{title}"'
    lines = [heading, ""]
    spent = 0
    shown = 0
    last_key: str | None = None
    for hit in selected:
        block: list[str] = []
        if _section_key(hit) != last_key or shown == 0:
            block.extend(_section_header(hit))
            last_key = _section_key(hit)
        block.append(chunk_body(hit).rstrip())
        block.append("")
        size = sum(len(line) + 1 for line in block)
        if shown and spent + size > READ_MAX_CHARS:
            break
        spent += size
        shown += 1
        lines.extend(block)
    remaining = selected[shown:]
    if remaining:
        rest = list(dict.fromkeys(k for k in map(_section_key, remaining) if k))
        lines.append(f"Results: {shown} of {len(selected)} sections; the page continues.")
        if rest:
            lines.append(
                f'next: {READ_PAGE}(page_url="{page_url}", section="{rest[0]}") for the next '
                f"section; remaining sections: {', '.join(rest)}"
            )
    else:
        lines.append(f"Results: {shown} sections, the whole {'section' if section else 'page'}.")
    return "\n".join(lines).rstrip()


def _history_description() -> str:
    return f"""Track what changed in Mistral's documentation across dated snapshots.
    Snapshots run from {_first_snapshot()} to the pinned commit.

    USE WHEN: the question is when something appeared, changed or disappeared,
    or what an alias like `-latest` pointed to on a date.

    DO NOT USE: to read the current documentation ({SEARCH}, {READ_PAGE}).

    Pass exactly one of:
        text: An exact phrase; returns its first and last appearance with links.
        section: A docs.mistral.ai url#anchor or page; returns its state at each
            date with the diff when it changed.
        question: A question; returns the top matching section at each date.
    """


def _first_snapshot() -> str:
    try:
        snapshots = history_service.available_snapshots(SNAPSHOT_MANIFEST)
    except (OSError, ValueError):
        return "the first stored snapshot"
    return snapshots[0].date if snapshots else "the first stored snapshot"


async def mistral_docs_history(
    text: str | None = None,
    section: str | None = None,
    question: str | None = None,
) -> str:
    forms = [("text", text), ("section", section), ("question", question)]
    selected = [(name, value) for name, value in forms if value is not None]
    if len(selected) != 1:
        raise _bad_param(
            "history takes exactly one of text, section or question.",
            f'{HISTORY}(text="phrase"), {HISTORY}(section="url#anchor") or '
            f'{HISTORY}(question="question").',
        )
    name, value = selected[0]
    if value is None or not value.strip():
        raise _bad_param(f"{name} is empty.", f"send text in {name}.")
    try:
        if name == "text":
            result = await asyncio.to_thread(
                history_service.phrase_history, value, SNAPSHOT_MANIFEST
            )
        elif name == "section":
            result = await asyncio.to_thread(
                history_service.section_history, value, SNAPSHOT_MANIFEST
            )
        else:
            async with _admission_or_busy():
                result = await history_service.question_history(
                    value, SNAPSHOT_MANIFEST, engine_factory=_snapshot_engine
                )
    except (OSError, ValueError) as exc:
        raise _bad_param(str(exc), "pass one documented history form.") from exc
    lines = [f"history {name}: {json.dumps(value)}"]
    if name == "text":
        first, last = result["first"], result["last"]
        if first is None:
            lines.append("Results: the phrase is absent from every stored snapshot.")
        else:
            lines.append(f"first: {first['snapshot']} | {first['page']}")
            lines.append(f"last: {last['snapshot']} | {last['page']}")
            lines.append(f"Results: present in {result['snapshots_found']} snapshots")
        return "\n".join(lines)
    states = result["states"]
    spent = 0
    rendered = 0
    for state in states:
        block: list[str] = []
        target = state.get("page") or "(absent)"
        if state.get("anchor"):
            target += f"#{state['anchor']}"
        block.append(f"{state['snapshot']}: {state['state']} | {target}")
        if state.get("diff"):
            block.extend(["```diff", state["diff"], "```"])
            if state.get("diff_truncated"):
                block.append(DIFF_LIMIT_NOTE)
        if state.get("text"):
            block.append(state["text"])
        size = sum(len(line) + 1 for line in block)
        if rendered and spent + size > HISTORY_MAX_CHARS:
            break
        spent += size
        rendered += 1
        lines.extend(block)
    lines.append(f"Results: {rendered} of {len(states)} stored snapshots")
    if rendered < len(states):
        lines.append(
            f'next: {HISTORY}(section="{value}") again names the same section; the dates '
            f"after {states[rendered - 1]['snapshot']} were not rendered in this call."
        )
    return "\n".join(lines)


def _snapshot_engine(config: RetrievalConfig) -> SearchEngine:
    return SearchEngine(config.model_copy(update={"rerank": False}))


_TOOL_IMPLS: dict[str, Callable[..., Awaitable[str]]] = {
    SEARCH: mistral_docs_search,
    READ_PAGE: mistral_docs_read_page,
    HISTORY: mistral_docs_history,
}
_DESCRIPTIONS: dict[str, Callable[[], str]] = {
    SEARCH: _search_description,
    READ_PAGE: _read_page_description,
    HISTORY: _history_description,
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

for _tool_name in _TOOL_ORDER:
    if _tool_name in _ENABLED_TOOLS:
        _impl = _TOOL_IMPLS[_tool_name]
        _impl.__doc__ = _DESCRIPTIONS[_tool_name]()
        mcp.tool(title=_TOOL_TITLES[_tool_name], annotations=TOOL_ANNOTATIONS)(_impl)


_PUBLIC_PATHS = frozenset({"/", "/health", "/favicon.ico", "/favicon.svg"})

FAVICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
    '<rect width="64" height="64" rx="12" fill="#1f1f1f"/>'
    '<rect x="14" y="14" width="36" height="36" rx="4" fill="#ff7000"/>'
    '<rect x="20" y="22" width="24" height="4" fill="#1f1f1f"/>'
    '<rect x="20" y="30" width="24" height="4" fill="#1f1f1f"/>'
    '<rect x="20" y="38" width="16" height="4" fill="#1f1f1f"/>'
    "</svg>"
)


class _BearerAuthMiddleware:
    """One shared secret on the HTTP transport (D-037). The landing page, the
    health check and the favicon need no token."""

    def __init__(self, app: ASGIApp, token: str) -> None:
        self.app = app
        self.token = token

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "lifespan":
            await self.app(scope, receive, send)
            return
        if scope["type"] != "http":
            if scope["type"] == "websocket":
                await send({"type": "websocket.close", "code": 1008})
            return
        if scope.get("path") in _PUBLIC_PATHS:
            await self.app(scope, receive, send)
            return
        headers = {
            name.decode("latin-1").lower(): value.decode("latin-1")
            for name, value in scope.get("headers", [])
        }
        if not hmac.compare_digest(headers.get("authorization", ""), f"Bearer {self.token}"):
            response = JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": "E_UNAUTHORIZED",
                        "message": "send 'Authorization: Bearer <token>'.",
                        "next": "retry with the GLOSSATOR_MCP_TOKEN value; GET /health needs none.",
                    }
                },
            )
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)


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
            "embedding_probe": {"passed": probe_passed, **probe_detail},
            "tools": [name for name in _TOOL_ORDER if name in _ENABLED_TOOLS],
            "version": package_version(),
        }
    )


@mcp.custom_route("/favicon.svg", methods=["GET"])
async def _favicon_svg(request: Request) -> Response:
    return Response(FAVICON_SVG, media_type="image/svg+xml")


@mcp.custom_route("/favicon.ico", methods=["GET"])
async def _favicon_ico(request: Request) -> Response:
    return Response(FAVICON_SVG, media_type="image/svg+xml")


@mcp.custom_route("/", methods=["GET"])
async def _landing(request: Request) -> Response:
    tools = "".join(
        f"<li><code>{name}</code></li>" for name in _TOOL_ORDER if name in _ENABLED_TOOLS
    )
    body = (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        f"<title>{SERVER_TITLE}</title>"
        "<link rel='icon' type='image/svg+xml' href='/favicon.svg'>"
        "<style>body{font:16px/1.5 system-ui,sans-serif;max-width:40rem;margin:4rem auto;"
        "padding:0 1rem;color:#1f1f1f}code{background:#f2f2f2;padding:0 .3em}</style>"
        f"</head><body><h1>{SERVER_TITLE}</h1>"
        f"<p>An MCP server over {len(_PAGE_SIZES)} pages of docs.mistral.ai at a pinned commit. "
        "The endpoint is <code>/mcp</code> over Streamable HTTP with a bearer token; "
        "<code>/health</code> is open.</p>"
        f"<ul>{tools}</ul>"
        f"<p><a href='{REPOSITORY_URL}'>Source and evaluation</a></p></body></html>"
    )
    return HTMLResponse(body)


def http_middleware() -> list[StarletteMiddleware]:
    if not _MCP_TOKEN:
        logger.warning("GLOSSATOR_MCP_TOKEN is not set; the MCP HTTP server is open to any client.")
        return []
    return [StarletteMiddleware(_BearerAuthMiddleware, token=_MCP_TOKEN)]


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
