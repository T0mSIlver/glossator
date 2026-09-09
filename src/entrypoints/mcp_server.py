"""Read-only MCP tools for search, page navigation, and cited answers."""

import argparse
import asyncio
import hmac
import json
import os
import time
from pathlib import Path
from typing import Any

import structlog
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware
from mistralai.search.toolkit.retrieval.errors import RetrieverException
from mistralai.search.toolkit.search import GrepMode
from mistralai.search.toolkit.search.errors import IndexException, SourceNotFoundError
from pydantic import ValidationError
from starlette.middleware import Middleware as StarletteMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from entrypoints.param_suggestions import suggest_fields
from glossator import history as history_service
from glossator.answer import cite as cite_engine
from glossator.answer import service as answer_service
from glossator.answer.citations import Answer, RejectionReason
from glossator.answer.cite import (
    CiteInputError,
    CiteQuote,
    entries_with_headings,
    sources_markdown,
)
from glossator.answer.config import (
    DEFAULT_VARIANT,
    MISTRAL_MEDIUM_3_5,
    PRICES,
    AnswerConfig,
    known_serving_model,
)
from glossator.answer.context import chunk_body
from glossator.corpus.snapshots import configured_manifest
from glossator.index.variants import VARIANTS
from glossator.retrieval.config import KINDS, RetrievalConfig
from glossator.retrieval.engine import Hit, SearchEngine
from glossator.retrieval.probe import check_embedding_once

load_dotenv(override=True)

logger = structlog.get_logger(__name__)

if not os.environ.get("MISTRAL_API_KEY"):
    raise RuntimeError("MISTRAL_API_KEY is not set. Check your .env file.")

# Which index variant this server serves. Schema names are owned by the index
# package, so the environment names a variant rather than a Vespa collection.
_variant_name = os.environ.get("GLOSSATOR_VARIANT", DEFAULT_VARIANT)
if _variant_name not in VARIANTS:
    raise RuntimeError(
        f"GLOSSATOR_VARIANT={_variant_name!r} is unknown; known variants: {sorted(VARIANTS)}"
    )

CORPUS_DIR = Path(os.environ.get("GLOSSATOR_CORPUS_DIR", "corpus/mistral-docs"))
SNAPSHOT_MANIFEST = configured_manifest()

# Bearer token for the HTTP transport (D-037). When set, every MCP HTTP
# request except GET /health must carry `Authorization: Bearer <token>`.
_MCP_TOKEN = os.environ.get("GLOSSATOR_MCP_TOKEN", "")

SERVER_NAME = "mistral-docs"
SERVER_TITLE = "Mistral documentation search"

# Tools are namespaced by service and named by the resource they read, so a
# model choosing between them sees the corpus in the name and never confuses
# one with its own filesystem or web tools.
SEARCH = "mistral_docs_search"
OPEN_SECTION = "mistral_docs_open_section"
STEP = "mistral_docs_step"
READ_PAGE = "mistral_docs_read_page"
FIND_ON_PAGE = "mistral_docs_find_on_page"
ANSWER = "mistral_docs_answer"
VERIFY_QUOTES = "mistral_docs_verify_quotes"
HISTORY = "mistral_docs_history"

_TOOL_ORDER = (
    SEARCH,
    OPEN_SECTION,
    STEP,
    READ_PAGE,
    FIND_ON_PAGE,
    ANSWER,
    VERIFY_QUOTES,
    HISTORY,
)
"""Every tool this server can register, in guide order."""

_RENAMED_TOOLS = {
    "search": SEARCH,
    "open": OPEN_SECTION,
    "navigate": STEP,
    "read": READ_PAGE,
    "grep": FIND_ON_PAGE,
    "ask": ANSWER,
    "cite": VERIFY_QUOTES,
    "history": HISTORY,
}
"""The names the allowlist took before the tools were namespaced. Accepted for
one release so a deployment's existing `.env.deploy` keeps working."""

_TOOL_TITLES = {
    SEARCH: "Search Mistral documentation",
    OPEN_SECTION: "Open a documentation section",
    STEP: "Step through a documentation page",
    READ_PAGE: "Read a documentation page",
    FIND_ON_PAGE: "Find text on a documentation page",
    ANSWER: "Answer from Mistral documentation",
    VERIFY_QUOTES: "Verify quotes against the documentation",
    HISTORY: "Documentation history",
}
"""Human-readable names for clients that display a tool list."""


def _parse_tool_allowlist(raw: str) -> frozenset[str]:
    """Which tools to register from GLOSSATOR_MCP_TOOLS.

    Unset or blank means every tool. The names the tools had before they were
    namespaced are accepted and translated, so an existing deployment file
    keeps working. Unknown names are ignored with a warning: a typo must not
    take down the tools that were named correctly.
    """
    if not raw.strip():
        return frozenset(_TOOL_ORDER)
    wanted = {part.strip() for part in raw.split(",") if part.strip()}
    renamed = sorted(wanted & set(_RENAMED_TOOLS))
    if renamed:
        logger.warning(
            "GLOSSATOR_MCP_TOOLS uses the pre-namespace tool names",
            renamed={old: _RENAMED_TOOLS[old] for old in renamed},
        )
        wanted = {_RENAMED_TOOLS.get(name, name) for name in wanted}
    unknown = sorted(wanted - set(_TOOL_ORDER))
    if unknown:
        logger.warning(
            "Ignoring unknown tool names in GLOSSATOR_MCP_TOOLS",
            unknown=unknown,
            known=sorted(_TOOL_ORDER),
        )
    return frozenset(wanted & set(_TOOL_ORDER))


_ENABLED_TOOLS = _parse_tool_allowlist(os.environ.get("GLOSSATOR_MCP_TOOLS", ""))

# Generation model for the ask tool. The default is the shipped configuration
# (D-017); a deployment on the free tier points this at a reachable model
# (D-017a) without widening the tool's parameter surface.
_model_env = os.environ.get("GLOSSATOR_MODEL", "")


def _answer_config() -> AnswerConfig:
    if _model_env and not known_serving_model(_model_env):
        # Same refusal the API's /ask makes: a model this deployment cannot
        # price is deterministic misconfiguration, unless a local chat server
        # is configured (D-035c).
        raise ValueError(
            f"no price for model {_model_env!r}; priced models: {sorted(PRICES)} "
            "(or set GLOSSATOR_CHAT_SERVER_URL to serve from a local server)"
        )
    return AnswerConfig(model=_model_env) if _model_env else AnswerConfig()


# Construction checks the variant, embedding model, and navigation support.
_engine = SearchEngine(RetrievalConfig.shipped(variant=_variant_name, check_lexical_footing=True))

# Extra engines for the other variants, for the context resource's document
# counts. Built lazily, reused once built; counts are cached briefly so a
# client re-reading the resource does not re-probe Vespa.
_extra_engines: dict[str, SearchEngine] = {}
_COUNT_CACHE_SECONDS = 300.0
_count_cache: dict[str, tuple[float, int | None]] = {}

# One engine operation at a time past this many concurrent calls; beyond it the
# caller gets E_BUSY with "retry the identical call", never a silent queue.
_ADMISSION_SLOTS = 4
_admission = asyncio.Semaphore(_ADMISSION_SLOTS)

PREVIEW_CHARS = 400
OPEN_PREVIEW_CHARS = 1200

READ_MAX_CHARS = 16_000
"""Per-call ceiling on a page read. Pages average about eleven chunks but the
longest run far past that, and one call must not spend a small model's whole
window; the footer names the offset to continue from."""

HISTORY_MAX_CHARS = 12_000
"""Per-call ceiling on rendered snapshots. The diff clamp is per state and the
manifest holds eight, so a heavily edited section would otherwise render eight
clamped diffs in one response."""

CONCISE = "concise"
DETAILED = "detailed"
RESPONSE_FORMATS = (CONCISE, DETAILED)

LIMITS: dict[str, tuple[int, int, int]] = {
    f"{SEARCH}.max_hits": (1, 50, 5),
    f"{OPEN_SECTION}.window": (1, 10, 2),
    f"{STEP}.steps": (1, 10, 1),
    f"{READ_PAGE}.max_chunks": (1, 100, 8),
    f"{FIND_ON_PAGE}.max_matches": (1, 25, 5),
    f"{VERIFY_QUOTES}.quotes": (1, 20, 20),
}
"""name -> (low, high, default). Published in glossator://context."""


def _manifest_pages() -> list[dict[str, Any]]:
    manifest = CORPUS_DIR / "manifest.json"
    if not manifest.is_file():
        return []
    try:
        pages = json.loads(manifest.read_text())
    except (OSError, json.JSONDecodeError):
        return []
    return pages if isinstance(pages, list) else []


def _corpus_commit(pages: list[dict[str, Any]]) -> str:
    commits = {str(page.get("source_commit")) for page in pages if page.get("source_commit")}
    if len(commits) == 1:
        return next(iter(commits))
    return f"{len(commits)} commits"


def _error(code: str, message: str, next_hint: str) -> ToolError:
    return ToolError("\n".join([f"error: {code}", message, f"next: {next_hint}"]))


def _bad_param(message: str, next_hint: str) -> ToolError:
    return _error("E_BAD_PARAM", message, next_hint)


def _unknown_chunk(chunk_id: str) -> ToolError:
    return _error(
        "E_UNKNOWN_CHUNK",
        f'chunk id "{chunk_id}" is not in the index.',
        "use a chunk id exactly as a search or open result printed it; never use one "
        f"recalled from memory. {SEARCH}(query=...) lists chunk ids.",
    )


def _unknown_page(page_url: str) -> ToolError:
    return _error(
        "E_UNKNOWN_PAGE",
        f'no indexed page has page_url "{page_url}".',
        "use the page_url exactly as a hit printed it; never use a URL recalled from "
        "memory. glossator://index lists every indexed page.",
    )


def _empty_query(noun: str, echo: str) -> ToolError:
    return _error(
        "E_EMPTY_QUERY",
        f"{noun} is empty or only whitespace (echo: {echo!r}).",
        "send the words to match; for search, two or three distinctive words work best.",
    )


def _busy() -> ToolError:
    return _error(
        "E_BUSY",
        f"the server is already running {_ADMISSION_SLOTS} concurrent engine calls.",
        "retry the IDENTICAL call in 1s; do not reformulate the query. A different "
        "one is refused exactly as fast. The limit is on concurrent calls, not on "
        "what a query costs.",
    )


def _upstream(operation: str, cause: Exception) -> ToolError:
    logger.warning("Upstream failure", operation=operation, error=str(cause))
    return _error(
        "E_UPSTREAM",
        f"{operation} failed against the search index: {cause}",
        "retry the identical call in 1s; if it repeats, the index or the Mistral API "
        "may be down. Ask again later instead of rephrasing.",
    )


def _clamp(kind: str, value: int | None) -> tuple[int, str | None]:
    """Clamp a numeric parameter to its published range, announcing the move."""
    low, high, default = LIMITS[kind]
    if value is None:
        return default, None
    applied = max(low, min(high, value))
    if applied == value:
        return value, None
    name = kind.split(".", 1)[1]
    return applied, f"note: clamped server-side: {name}={value} → {applied}"


def _rendering(response_format: str) -> bool:
    """True when the caller asked for the detailed rendering of a result."""
    if response_format not in RESPONSE_FORMATS:
        raise _bad_param(
            f'response_format={response_format!r} is not one of "{CONCISE}", "{DETAILED}".',
            f'"{CONCISE}" prints the citation, heading path, snippet and chunk id; '
            f'"{DETAILED}" adds scores, offsets, counts and untruncated text.',
        )
    return response_format == DETAILED


def _hint(*choices: tuple[str, str]) -> str:
    """The first suggestion whose tool this deployment registered (D-029).

    A `next:` line, a truncation marker, or a DO NOT USE clause that names a
    tool the allowlist turned off is the same trap as one naming a parameter
    the tool lacks: the model calls it, gets "unknown tool", and has no failure
    to act on. The choices are tried in order and the last one is the fallback
    that assumes nothing.
    """
    for tool, text in choices:
        if tool in _ENABLED_TOOLS:
            return text
    return "read `glossator://guide` for the tools this deployment registered"


def _next(*choices: tuple[str, str]) -> str:
    return f"next: {_hint(*choices)}"


def _registered(*choices: tuple[str, str]) -> str:
    """Every clause whose tool this deployment registered, as one sentence."""
    kept = [text for tool, text in choices if tool in _ENABLED_TOOLS]
    if not kept:
        return "for anything outside Mistral's documentation."
    return "; ".join(kept) + "."


def _hit_block(
    hit: Hit,
    n: int,
    chars: int | None,
    mark: bool = False,
    detailed: bool = False,
) -> str:
    """One retrieved unit: its citation, its heading path, its handle, its text.

    Long payloads print the anchor on each unit so a citation never reuses the
    page-top link for a section further down (D-029). The detailed rendering
    adds the retrieval apparatus an engineer reads: score, kind and offsets.
    """
    star = "*" if mark else ""
    lines = [f"[{n}]{star} {hit.citation_url}"]
    if hit.heading_line:
        lines.append(f"    {hit.heading_line}")
    if detailed:
        meta = [f"score {hit.score:.3f}"]
        if hit.kind:
            meta.append(hit.kind)
        if hit.start_offset is not None and hit.end_offset is not None:
            meta.append(f"offsets {hit.start_offset}..{hit.end_offset}")
        lines.append(f"    {' · '.join(meta)}")
    lines.append(f'    chunk id "{hit.chunk_id}"')
    # The chunker prefixes every chunk with its heading path; the line above
    # already carries it, so the snippet does not repeat it.
    body = chunk_body(hit)
    preview = body if chars is None else " ".join(body.split())
    if chars is not None and len(preview) > chars:
        preview = preview[:chars] + TRUNCATED
    lines.append(f"    {preview}")
    return "\n".join(lines)


TRUNCATED = " …[truncated]"
"""What a cut snippet ends with. One line under the block names the tool that
returns the rest, instead of one paste-ready call per hit."""


def _truncation_note(blocks: list[str], chars: int) -> list[str]:
    """One line for a page of cut snippets, naming a registered tool once."""
    if not any(TRUNCATED in block for block in blocks):
        return []
    whole = _hint(
        (OPEN_SECTION, f'{OPEN_SECTION}(chunk_id="…") for a hit and its neighbours'),
        (READ_PAGE, f'{READ_PAGE}(page_url="…") for the whole page'),
    )
    return [
        f"note: snippets clamped server-side to {chars} chars; "
        f'{whole}, or response_format="{DETAILED}" for the untruncated text'
    ]


def _deeper_search_line(query: str, ids: list[str], **fixed: Any) -> str:
    """A copy-pasteable call that excludes exactly what this page returned."""
    id_list = ", ".join(json.dumps(i) for i in ids)
    parts = [f"query={json.dumps(query)}", f"exclude_ids=[{id_list}]"]
    parts += [f"{k}={json.dumps(v)}" for k, v in fixed.items()]
    return f"{SEARCH}({', '.join(parts)})"


def _instructions() -> str:
    """The whole surface, for a client that can read nothing else.

    Work never reads `glossator://guide` (D-037a), so the corpus scope, the
    never-fabricate rule, the refusal path and the `next:` rule live here. A
    deployment that disables tools through GLOSSATOR_MCP_TOOLS must not promise
    a flow it cannot run, so each clause is conditional on its tool.
    """
    pages = len(_manifest_pages())
    scope = f"{pages} pages of Mistral's documentation" if pages else "Mistral's documentation"
    flow = f"Start with {SEARCH}"
    if OPEN_SECTION in _ENABLED_TOOLS:
        flow += f", then {OPEN_SECTION} to read a hit in context"
    else:
        flow += " to find the sections that state each claim"
    if VERIFY_QUOTES in _ENABLED_TOOLS:
        flow += (
            f"; write the answer with [n] markers and verbatim quotes, call {VERIFY_QUOTES}, "
            "keep only what it verified and paste its Sources block"
        )
    if ANSWER in _ENABLED_TOOLS:
        flow += f"; {ANSWER} answers end to end instead"
    if HISTORY in _ENABLED_TOOLS:
        flow += f"; {HISTORY} tracks changes across stored dates"
    return (
        f"Searches {scope}: docs.mistral.ai guides, API reference and model cards "
        "at a pinned commit. Use it for any question about Mistral models, the "
        "API, SDKs, pricing, limits, Studio, Work, Vibe or La Plateforme.\n\n"
        f"{flow}.\n\n"
        "Never fabricate a URL, anchor or id: cite a url#anchor exactly as a tool "
        "printed it, and pass ids back exactly as printed.\n\n"
        "It is not the whole internet. When it does not cover the question, say "
        "so; never answer from memory.\n\n"
        "Read the `next:` line ending every response: it names the call that fits "
        "what you just got."
    )


mcp: FastMCP = FastMCP(SERVER_NAME, instructions=_instructions())


class _ParamGuard(Middleware):
    """Unknown argument names are a typed error, not a silent drop (D-029).

    The schema already says ``additionalProperties: false``, but the default
    failure is a pydantic stack trace the model cannot act on. This guard sits
    at ``tools/call``, where the raw arguments still exist, and answers with
    ``E_BAD_PARAM`` naming the parameter the caller probably meant.

    Arguments whose name starts with an underscore belong to the host, not to
    the model: Mistral Work sends ``_confirmationReason`` on the call that asks
    the user for approval, and every one of those calls failed validation
    before it ran. They are dropped before the tool sees them and named in a
    ``note:`` line, because a silently discarded argument is the trap D-029
    forbids.
    """

    def __init__(self, server: FastMCP) -> None:
        self.server = server

    async def on_call_tool(self, context: Any, call_next: Any) -> Any:
        name = context.message.name
        arguments = dict(context.message.arguments or {})
        tool = await self.server.get_tool(name)
        if tool is None:
            return await call_next(context)
        host_args = sorted(k for k in arguments if k.startswith("_"))
        if host_args:
            for key in host_args:
                arguments.pop(key)
            context.message.arguments = arguments
        known = set(tool.parameters["properties"])
        unknown = [k for k in arguments if k not in known]
        if unknown:
            suggestions = suggest_fields(unknown, known)
            many = len(unknown) > 1
            raise _bad_param(
                f"unknown parameter{'s' if many else ''} for {name}: "
                f"{', '.join(f'{w}=' for w in unknown)}; "
                f"{'they were' if many else 'it was'} rejected, not applied; a filter you "
                "think you passed was not.",
                ("did you mean " + ", ".join(suggestions) + "? " if suggestions else "")
                + f"{name} accepts: {', '.join(sorted(known))}.",
            )
        result = await call_next(context)
        if not host_args:
            return result
        return _with_note(
            result,
            f"note: ignored host argument{'s' if len(host_args) > 1 else ''} "
            f"{', '.join(host_args)}",
        )


def _with_note(result: Any, note: str) -> Any:
    """The same result with one more announced line under its text."""
    blocks = list(getattr(result, "content", None) or [])
    for block in blocks:
        if getattr(block, "type", None) == "text":
            block.text = f"{block.text}\n{note}"
            return result
    return result


_guard = _ParamGuard(mcp)
mcp.add_middleware(_guard)


def _search_description() -> str:
    return f"""Search Mistral's documentation for the sections that state something.
    Each hit prints its url#anchor, heading path, snippet and chunk id.

    USE WHEN: you need a documented Mistral parameter, limit, model, price or
    error.

    DO NOT USE: {
        _registered(
            (ANSWER, f"to answer end to end ({ANSWER})"),
            (OPEN_SECTION, f"to read inside a page you hold a hit in ({OPEN_SECTION})"),
        )
    }

    START WITH max_hits=5 and rerank=False: about 9 ms, and search again
    rather than paying for a better order. rerank=True costs about 5 s and is
    for one decisive search.

    Args:
        query: Two or three distinctive words beat a sentence.
        max_hits: Maximum hits, 1-50 (clamped, announced).
        rerank: False (default) ranks with the index alone, in about 9 ms. True reorders
            with a model: about 5 s, much better rank 1, for a single decisive search.
        response_format: "concise" (default) or "detailed" (scores, offsets, full
            text, a paginated re-search call).
        kinds: Keep only "doc", "api" or "model" pages. Omit for all.
        locales: Keep only these locales, e.g. ["en"]. Omit for all.
        exclude_ids: Chunk ids to skip, exactly as printed, so a repeat search brings new context.
    """


async def mistral_docs_search(
    query: str,
    max_hits: int = 5,
    rerank: bool = False,
    response_format: str = CONCISE,
    kinds: list[str] | None = None,
    locales: list[str] | None = None,
    exclude_ids: list[str] | None = None,
) -> str:
    """Rank the corpus for one query and render the hits."""
    if not query.strip():
        raise _empty_query("query", query)
    detailed = _rendering(response_format)
    applied, note = _clamp(f"{SEARCH}.max_hits", max_hits)
    kinds_set = frozenset(kinds or ())
    locales_set = frozenset(locales or ())
    bad_kinds = sorted(kinds_set - KINDS)
    if bad_kinds:
        raise _bad_param(
            f"unknown page kind(s) {bad_kinds} in kinds.",
            'kinds are "doc", "api", "model"; omit the parameter for no filter.',
        )
    filter_note = None
    if kinds_set or locales_set:
        try:
            RetrievalConfig.shipped(variant=_variant_name, kinds=kinds_set, locales=locales_set)
        except ValueError as exc:
            raise _bad_param(
                str(exc), 'locales look like "en" or "pt-BR"; kinds are doc, api, model.'
            ) from exc
        filter_note = f"note: filtered to kinds={sorted(kinds_set)} locales={sorted(locales_set)}"

    async with _admission_or_busy():
        try:
            hits, trace = await _engine.search_with_trace(
                query,
                exclude_ids=set(exclude_ids) if exclude_ids else None,
                top_k=applied,
                rerank=rerank,
                kinds=kinds_set or None,
                locales=locales_set or None,
            )
        except RetrieverException as exc:
            raise _upstream(f"search({query!r})", exc) from exc

    header = f'query: "{query}"'
    if detailed:
        header += f" · variant {_variant_name} · hybrid bm25+vector"
    lines = [header]
    if note:
        lines.append(note)
    if filter_note:
        lines.append(filter_note)
    if not rerank:
        # An agent searches several times, so the reranker's five seconds are
        # charged per query; the default leaves it off and says the order is
        # the index's (D-034, and the audit's cost section).
        lines.append("note: index ranking only; rerank=true reorders with a model (about 5 s)")
    if trace.lexical_footing is False:
        lines.append(
            "note: no lexical footing in the corpus; vector retrieval still ran, "
            f"missing terms={list(trace.missing_terms)}"
        )
    lines.append("")
    chars = None if detailed else PREVIEW_CHARS
    blocks = [_hit_block(hit, i, chars, detailed=detailed) for i, hit in enumerate(hits, 1)]
    for block in blocks:
        lines.append(block)
        lines.append("")
    if not hits:
        lines.extend(_empty_search(query, kinds_set, locales_set, exclude_ids or []))
        return "\n".join(lines).rstrip()
    if not detailed:
        lines.extend(_truncation_note(blocks, PREVIEW_CHARS))
    if len(hits) == applied:
        lines.append(
            f"Results: {trace.kept}/{trace.considered} kept/considered "
            f"(max_hits={applied} was full; more may exist)"
        )
        if detailed:
            lines.append("go deeper, copy-paste:")
            seen_ids = list(dict.fromkeys([*(exclude_ids or []), *(hit.chunk_id for hit in hits)]))
            fixed: dict[str, Any] = {}
            if kinds:
                fixed["kinds"] = kinds
            if locales:
                fixed["locales"] = locales
            lines.append("  " + _deeper_search_line(query, seen_ids, **fixed))
    else:
        lines.append(
            f"Results: {trace.kept}/{trace.considered} kept/considered "
            f"(all that matched within max_hits={applied})"
        )
    lines.append(_search_next(query, hits[0]))
    return "\n".join(lines).rstrip()


def _search_next(query: str, first: Hit) -> str:
    """What to do with a hit, over the tools this deployment registered."""
    reading = _hint(
        (OPEN_SECTION, f'{OPEN_SECTION}(chunk_id="{first.chunk_id}") to read hit 1 in context'),
        (READ_PAGE, f'{READ_PAGE}(page_url="{first.source_id}") to read hit 1\'s page'),
    )
    if ANSWER in _ENABLED_TOOLS:
        return f'next: {reading}, or {ANSWER}(question="{query}") for a grounded answer'
    if VERIFY_QUOTES in _ENABLED_TOOLS:
        return f"next: {reading}, then {VERIFY_QUOTES}(draft=…, quotes=[…]) to check what you quote"
    return f"next: {reading}"


def _empty_search(
    query: str, kinds: frozenset[str], locales: frozenset[str], exclude_ids: list[str]
) -> list[str]:
    """Say which kind of empty this is, echo the query, and name the next call."""
    why: list[str] = []
    if exclude_ids:
        why.append("every matching chunk was in exclude_ids")
    if kinds or locales:
        why.append("no page matched the kind/locale filter")
    why.append(
        "the corpus may lack the topic, or the phrasing may differ. This index "
        "covers docs.mistral.ai guides, API reference and model cards only"
    )
    lines = [
        f'Results: 0 sections matched for query "{query}" ({_variant_name})',
        *(f"- {reason}." for reason in why),
    ]
    if kinds or locales:
        lines.append(
            "next: re-run without kinds/locales, or rephrase with two or three distinctive words"
        )
    else:
        lines.append(
            "next: rephrase with two or three distinctive words, "
            "or check glossator://index for what exists"
        )
    return lines


def _page_next(page_url: str, chunk_id: str | None = None) -> str:
    """Where to go from a page, over the tools this deployment registered."""
    choices = [
        (READ_PAGE, f'{READ_PAGE}(page_url="{page_url}") for the whole page'),
        (
            FIND_ON_PAGE,
            f'{FIND_ON_PAGE}(page_url="{page_url}", pattern="…") for an exact phrase on it',
        ),
    ]
    if chunk_id is not None:
        choices.append(
            (OPEN_SECTION, f'{OPEN_SECTION}(chunk_id="{chunk_id}") for context around it')
        )
    choices.append((SEARCH, f"{SEARCH}(query=…) to change page"))
    return _next(*choices)


class _admission_or_busy:
    """Acquire an admission slot or fail immediately with the typed retry hint."""

    async def __aenter__(self) -> None:
        if _admission.locked():
            raise _busy()
        await _admission.acquire()

    async def __aexit__(self, *exc: object) -> None:
        _admission.release()


def _open_section_description() -> str:
    return f"""Read a Mistral documentation section with its neighbours in page order.
    The chunk you pass is marked *; window chunks each side come with it.

    USE WHEN: a search hit looks promising and you need its context, such as a
    definition before a sentence or rows cut off from a table.

    DO NOT USE: {
        _registered(
            (READ_PAGE, f"to fetch a whole page or an offset range ({READ_PAGE})"),
            (SEARCH, f"to find hits in the first place ({SEARCH})"),
        )
    }

    START WITH window=2.

    Args:
        chunk_id: Chunk id exactly as a result printed it.
        window: Chunks each side of it, 1-10 (clamped, announced).
        response_format: "concise" (default) or "detailed" (scores, offsets, full text).
    """


async def mistral_docs_open_section(
    chunk_id: str, window: int = 2, response_format: str = CONCISE
) -> str:
    """Fetch one chunk and its neighbours on the same page."""
    detailed = _rendering(response_format)
    applied, note = _clamp(f"{OPEN_SECTION}.window", window)
    async with _admission_or_busy():
        try:
            anchor = await _engine.get_chunk(chunk_id)
        except IndexException as exc:
            raise _upstream(f"open_section({chunk_id!r})", exc) from exc
        if anchor is None or anchor.navigation is None:
            raise _unknown_chunk(chunk_id)
        try:
            hits = await anchor.navigation.around(window=applied)
        except IndexException as exc:
            raise _upstream(f"open_section({chunk_id!r})", exc) from exc

    lines = [f'page: {anchor.url} | "{anchor.page_title}"']
    if note:
        lines.append(note)
    lines.append(
        f"window: {len(hits)} chunks around {json.dumps(chunk_id)} (* marks it), reading order"
    )
    lines.append("")
    center = next((h for h in hits if h.chunk_id == chunk_id), None)
    chars = None if detailed else OPEN_PREVIEW_CHARS
    blocks = [
        _hit_block(hit, i, chars, mark=hit is center, detailed=detailed)
        for i, hit in enumerate(hits, 1)
    ]
    for block in blocks:
        lines.append(block)
        lines.append("")
    if not detailed:
        lines.extend(_truncation_note(blocks, OPEN_PREVIEW_CHARS))
    lines.append(f"Results: {len(hits)} chunks")
    lines.append(_page_next(anchor.source_id))
    return "\n".join(lines).rstrip()


def _step_description() -> str:
    return f"""Step to the next or previous section of a Mistral documentation page.
    Pass the chunk id you are stepping from; the server holds its position.

    USE WHEN: you are walking a page section by section, or the end of an
    open-section window cut a passage off.

    DO NOT USE: {
        _registered(
            (OPEN_SECTION, f"to expand both directions at once ({OPEN_SECTION})"),
            (READ_PAGE, f"to fetch a whole page in one call ({READ_PAGE})"),
        )
    }

    START WITH steps=1.

    Args:
        chunk_id: Chunk id exactly as a result printed it; the step starts there.
        direction: "next" (forward in reading order) or "previous" (backward).
        steps: Chunks to fetch that way, 1-10 (clamped, announced).
    """


async def mistral_docs_step(chunk_id: str, direction: str, steps: int = 1) -> str:
    """Walk one page forward or backward from a chunk the caller holds."""
    if direction not in {"next", "previous"}:
        raise _bad_param(
            f'direction={direction!r} is not one of "next", "previous".',
            'use direction="next" to move forward in reading order, "previous" to move back.',
        )
    applied, note = _clamp(f"{STEP}.steps", steps)
    async with _admission_or_busy():
        try:
            anchor = await _engine.get_chunk(chunk_id)
        except IndexException as exc:
            raise _upstream(f"step({chunk_id!r})", exc) from exc
        if anchor is None or anchor.navigation is None:
            raise _unknown_chunk(chunk_id)
        try:
            hits = await (
                anchor.navigation.previous(top_k=applied)
                if direction == "previous"
                else anchor.navigation.next(top_k=applied)
            )
        except SourceNotFoundError as exc:
            raise _unknown_page(anchor.source_id) from exc
        except IndexException as exc:
            raise _upstream(f"step({chunk_id!r}, {direction})", exc) from exc
    if not hits:
        return "\n".join(
            [
                f'Results: 0 chunks {direction} from chunk "{chunk_id}" on {anchor.source_id}',
                f"- you are at the {'start' if direction == 'previous' else 'end'} of the page; "
                "there is nothing further in that direction.",
                _next(
                    (
                        OPEN_SECTION,
                        f'{OPEN_SECTION}(chunk_id="{chunk_id}") for context around it, '
                        f"or {SEARCH}(query=…) to change page",
                    ),
                    (SEARCH, f"{SEARCH}(query=…) to change page"),
                ),
            ]
        )
    count = f'{direction} {len(hits)} chunk(s) from chunk "{chunk_id}" on {anchor.source_id}'
    if len(hits) == applied:
        count += f" (steps={applied} was full; more may exist)"
    else:
        count += " (every chunk in this direction)"
    lines = [count]
    if note:
        lines.append(note)
    lines.append("")
    blocks = [_hit_block(hit, i, OPEN_PREVIEW_CHARS) for i, hit in enumerate(hits, 1)]
    for block in blocks:
        lines.append(block)
        lines.append("")
    lines.extend(_truncation_note(blocks, OPEN_PREVIEW_CHARS))
    lines.append(
        f'next: {STEP}(chunk_id="{hits[-1].chunk_id}", direction="{direction}") to keep walking'
    )
    return "\n".join(lines).rstrip()


def _read_page_description() -> str:
    return f"""Read one whole Mistral documentation page, or an offset range of it.
    Chunks come back in reading order, verbatim.

    USE WHEN: you know the page and want it in one call, such as following an
    outline or re-reading a section without ranking anything.

    DO NOT USE: {
        _registered(
            (OPEN_SECTION, f"to expand around one hit ({OPEN_SECTION} is cheaper)"),
            (SEARCH, f"to find where something is said ({SEARCH})"),
        )
    }

    START WITH no offsets and max_chunks=8, then follow the next: line; a long
    page arrives a page of chunks at a time.

    Args:
        page_url: Page URL exactly as a hit printed it.
        start_offset: Lower bound on chunk start (None = start of page).
        end_offset: A chunk is kept when it ends by this offset (None = end of page).
        max_chunks: Maximum chunks, 1-100 (clamped, announced), under a per-call character budget.
        response_format: "concise" (default) or "detailed" (scores and offsets).
    """


async def mistral_docs_read_page(
    page_url: str,
    start_offset: int | None = None,
    end_offset: int | None = None,
    max_chunks: int = 8,
    response_format: str = CONCISE,
) -> str:
    """Return the chunks of one page, in reading order."""
    detailed = _rendering(response_format)
    applied, note = _clamp(f"{READ_PAGE}.max_chunks", max_chunks)
    async with _admission_or_busy():
        try:
            navigation = _engine.navigation_at(page_url)
            hits = await navigation.read(start_offset, end_offset, top_k=applied)
        except SourceNotFoundError as exc:
            raise _unknown_page(page_url) from exc
        except IndexException as exc:
            raise _upstream(f"read_page({page_url!r})", exc) from exc
    if not hits:
        if start_offset is None and end_offset is None:
            return "\n".join(
                [
                    f"Results: 0 content chunks on indexed page {page_url}",
                    _next((SEARCH, f"{SEARCH}(query=…) to find another page with content")),
                ]
            )
        raise _error(
            "E_BAD_PARAM",
            f"no chunk of {page_url} lies inside offsets "
            f"{start_offset}..{end_offset if end_offset is not None else 'end'}.",
            "this is an offset problem, not a missing page. read_page with no offsets "
            "returns the whole page; or open_section(chunk_id=…) around a hit you hold.",
        )
    lines = [f'page: {page_url} | "{hits[0].page_title}"']
    if note:
        lines.append(note)
    if start_offset is not None or end_offset is not None:
        lines.append(
            f"range: {start_offset if start_offset is not None else 0}"
            f"..{end_offset if end_offset is not None else 'end'}"
        )
    lines.append("")
    # A page read is the one call that can return a whole document, so the
    # character budget bounds it even when max_chunks did not (D-029: the cut
    # is announced and the footer names where to continue).
    shown: list[Hit] = []
    spent = 0
    for i, hit in enumerate(hits, 1):
        block = _hit_block(hit, i, None, detailed=detailed)
        if shown and spent + len(block) > READ_MAX_CHARS:
            lines.append(
                f"note: clamped server-side: {len(shown)}/{len(hits)} chunks fit the "
                f"{READ_MAX_CHARS}-character per-call budget"
            )
            break
        spent += len(block)
        shown.append(hit)
        lines.append(block)
        lines.append("")
    more = len(shown) < len(hits) or len(hits) == applied
    if more:
        lines.append(f"Results: {len(shown)} chunks (the page has more)")
        if shown[-1].end_offset is not None:
            lines.append(
                f'next: {READ_PAGE}(page_url="{page_url}", start_offset={shown[-1].end_offset}, '
                f"max_chunks={applied}) to continue after this page of chunks"
            )
        else:
            lines.append(_page_next(page_url))
    else:
        lines.append(f"Results: {len(shown)} chunks (the whole requested range; none dropped)")
        lines.append(_page_next(page_url))
    return "\n".join(lines).rstrip()


def _find_on_page_description() -> str:
    return f"""Find an exact phrase or set of terms on one Mistral documentation page.
    It matches words, not meaning.

    USE WHEN: you have a page and need an exact error string, parameter name,
    or heading on it.

    DO NOT USE: {
        _registered(
            (SEARCH, f"to search the whole corpus, or to match by meaning ({SEARCH})"),
            (READ_PAGE, f"to read the page from end to end ({READ_PAGE})"),
        )
    }

    START WITH mode="phrase".

    Args:
        page_url: Page URL exactly as a hit printed it.
        pattern: The words to find, in order for mode="phrase".
        mode: "phrase" (exact order, default) or "term" (all words, any order).
        max_matches: Maximum matching chunks, 1-25 (clamped, announced).
        response_format: "concise" (default) or "detailed" (scores, offsets, full text).
    """


async def mistral_docs_find_on_page(
    page_url: str,
    pattern: str,
    mode: str = "phrase",
    max_matches: int = 5,
    response_format: str = CONCISE,
) -> str:
    """Lexical match inside one page."""
    if mode not in {"phrase", "term"}:
        raise _bad_param(
            f'mode={mode!r} is not one of "phrase", "term".',
            'mode="phrase" matches the words in order; "term" matches all words in any order.',
        )
    if not pattern.strip():
        raise _empty_query("pattern", pattern)
    detailed = _rendering(response_format)
    applied, note = _clamp(f"{FIND_ON_PAGE}.max_matches", max_matches)
    async with _admission_or_busy():
        try:
            navigation = _engine.navigation_at(page_url)
            hits = await navigation.grep(pattern, mode=GrepMode(mode), top_k=applied)
        except SourceNotFoundError as exc:
            raise _unknown_page(page_url) from exc
        except IndexException as exc:
            raise _upstream(f"find_on_page({page_url!r}, {pattern!r})", exc) from exc
    lines = [f"matches for {json.dumps(pattern)} (mode={mode}) on {page_url}"]
    if note:
        lines.append(note)
    lines.append("")
    if not hits:
        lines.append(
            f"Results: 0 chunks on this page contain the "
            f"{'phrase' if mode == 'phrase' else 'terms'} "
            f"{json.dumps(pattern)}. The page is indexed; the words are not on it."
        )
        lines.append(
            _next(
                (
                    SEARCH,
                    f'{SEARCH}(query="{pattern}") corpus-wide, or mode="term" to relax the order',
                ),
                (FIND_ON_PAGE, 'retry with mode="term" to relax the order'),
            )
        )
        return "\n".join(lines).rstrip()
    chars = None if detailed else OPEN_PREVIEW_CHARS
    blocks = [_hit_block(hit, i, chars, detailed=detailed) for i, hit in enumerate(hits, 1)]
    for block in blocks:
        lines.append(block)
        lines.append("")
    if not detailed:
        lines.extend(_truncation_note(blocks, OPEN_PREVIEW_CHARS))
    count = f"Results: {len(hits)} chunks matched"
    if len(hits) == applied:
        count += f" (max_matches={applied} was full; more matches may exist)"
    else:
        count += " (every match on this page)"
    lines.append(count)
    lines.append(_page_next(page_url, hits[0].chunk_id))
    return "\n".join(lines).rstrip()


def _answer_description() -> str:
    return f"""Answer a question from Mistral's documentation, with verified quotes.
    Returns the answer with [n] markers and a Sources block of links.

    USE WHEN: the user wants an answer rather than a document list. The server
    retrieves, generates, and checks every quote itself.

    DO NOT USE: {
        _registered(
            (SEARCH, f"to browse or explore ({SEARCH})"),
            (OPEN_SECTION, f"when you must quote the docs yourself ({OPEN_SECTION})"),
        )
    }

    START WITH strategy="single_pass": one reranked retrieval, about 12 s and
    $0.001. "search_loop" reads around its hits over up to four rounds for a
    few points more accuracy, about 35 s and $0.006.

    Args:
        question: Any phrasing; it is embedded, not matched verbatim.
        strategy: "single_pass" (default), "search_loop" (thorough), or "outline"
            (experimental: picks pages from the site outline).
    """


async def mistral_docs_answer(question: str, strategy: str = "single_pass") -> str:
    """Generate a cited answer with the server's own model."""
    if not question.strip():
        raise _empty_query("question", question)
    if strategy not in answer_service.STRATEGIES:
        raise _bad_param(
            f"strategy={strategy!r} is not one of {sorted(answer_service.STRATEGIES)}.",
            f"choose from {sorted(answer_service.STRATEGIES)}; single_pass is the cheapest.",
        )
    try:
        config = _answer_config()
    except (ValidationError, ValueError) as exc:
        # A bad GLOSSATOR_MODEL is deterministic misconfiguration: retrying the
        # identical call, as E_UPSTREAM tells a client to, can never fix it.
        raise _bad_param(
            f"the GLOSSATOR_MODEL setting is invalid: {exc}",
            f"GLOSSATOR_MODEL must be one of {sorted(PRICES)} "
            "(or set GLOSSATOR_CHAT_SERVER_URL for a local server)",
        ) from exc
    async with _admission_or_busy():
        try:
            answer = await answer_service.ask(
                question,
                strategy=strategy,
                variant=_variant_name,
                engine=_engine,
                config=config,
            )
        except Exception as exc:  # the service already retries its own transient errors
            raise _upstream(f"answer({question!r})", exc) from exc
    return _answer_text(question, answer)


def _verify_quotes_description() -> str:
    return f"""Verify your quotes against the Mistral documentation chunks they name.
    Returns a paste-ready Sources block, the failures, and uncovered markers.

    USE WHEN: you wrote an answer from documentation hits. Always verify before
    you show it: an unverified quote is an unsupported claim.

    DO NOT USE: {
        _registered(
            (ANSWER, f"to have the answer written for you ({ANSWER})"),
            (SEARCH, f"to find sources in the first place ({SEARCH})"),
        )
    }

    START WITH the draft and every quote you relied on, each naming a chunk_id
    exactly as a result printed it, or a page url with an optional #anchor.

    Args:
        draft: Your answer text with [n] markers, up to 20,000 characters (clamped, announced).
        quotes: The quotes behind the markers: each has n, quote, and either chunk_id
            or url. At most 20 are checked (clamped, announced).
    """


async def mistral_docs_verify_quotes(draft: str, quotes: list[CiteQuote]) -> str:
    """Check a consumer's quotes against the chunks they name."""
    if not draft.strip():
        raise _bad_param(
            "the draft is empty or only whitespace.",
            "send the answer text you wrote, with [n] markers where each claim leans.",
        )
    async with _admission_or_busy():
        try:
            result = await cite_engine.cite_draft(draft, quotes, engine=_engine)
        except CiteInputError as exc:
            raise _bad_param(str(exc), _cite_next_hint()) from exc
        except (IndexException, RetrieverException) as exc:
            raise _upstream("verify_quotes()", exc) from exc
    return _cite_text(result)


def _cite_next_hint() -> str:
    return (
        "each quote needs n, quote, and either chunk_id (exactly as a result "
        "printed it) or a page url with an optional #anchor."
    )


def _cite_text(result: cite_engine.CiteResult) -> str:
    """One cite result as text: failures, a count, uncovered markers, sources.

    A verified quote used to print its fragment URL in a verdict line and again
    under its source entry, and a fragment URL is 170 characters of encoded
    quote. The link is printed once, in the Sources block; what a caller has to
    act on is the list of failures, so those stay in full.
    """
    lines = []
    for line in result.notes:
        lines.append(line)
    if result.notes:
        lines.append("")
    verified = [item for item in result.quotes if item.verified]
    for item in result.quotes:
        if item.verified:
            continue
        lines.append(
            f"[{item.n}] NOT verified: {item.reason or 'unverified'} — {_cite_remedy(item.reason)}"
        )
    if result.quotes:
        named = ", ".join(f"[{item.n}]" for item in verified)
        emphasis = [item.n for item in verified if item.emphasis_normalized]
        count = f"verified: {len(verified)} of {len(result.quotes)} quotes"
        if named:
            count += f" ({named})"
        if emphasis:
            count += f"; {', '.join(f'[{n}]' for n in emphasis)} after emphasis normalization"
        lines.append(count)
    lines.append("")
    if result.unverified_markers:
        named = ", ".join(f"[{n}]" for n in result.unverified_markers)
        lines.append(
            f"markers with no verified quote: {named}; remove them or fix them "
            "against a quoted source."
        )
        lines.append("")
    lines.append(result.sources_markdown)
    lines.append("")
    lines.append(f"next: {result.next}")
    return "\n".join(lines).rstrip()


def _cite_remedy(reason: str | None) -> str:
    """What to do about one failed quote, by the reason it failed."""
    if reason == RejectionReason.TOO_SHORT:
        return "quote a whole sentence from the chunk"
    if reason == RejectionReason.FABRICATED:
        return _hint(
            (OPEN_SECTION, f"{OPEN_SECTION}(chunk_id=…) and copy the sentence verbatim"),
            (SEARCH, f"{SEARCH}(query=…) for a source that states the claim"),
        )
    return "check the chunk_id or url against the result that printed it"


def _answer_text(question: str, answer: Answer) -> str:
    headings = {source.n: " > ".join(source.heading_path) for source in answer.trace.sources}
    verified = answer.citations
    rejected = answer.trace.unverified_citations
    total = len(verified) + len(rejected)

    lines = [answer.answer_markdown, ""]
    if answer.insufficient_evidence:
        lines.append(
            "insufficient evidence: no citation could be verified against the retrieved "
            "sources. Treat the text above as unsupported."
        )
        lines.append("")
    # One entry per distinct (url, anchor); markers keep their numbers and the
    # entry lists the numbers that point at it (D-027b).
    entries = entries_with_headings(verified, headings)
    lines.append(sources_markdown(entries))
    lines.append("")
    for citation in rejected:
        shown = citation.quote if len(citation.quote) <= 60 else citation.quote[:60] + "…"
        lines.append(
            f"[{citation.n}] dropped, no link | {citation.reason or 'unverified'} "
            f"(quote: {json.dumps(shown)}); do not cite it"
        )
    verified_count = (
        f"citations verified: {len(verified)}/{total}" if total else "no citations were proposed"
    )
    lines.append(
        f"{verified_count} · strategy {answer.strategy} on "
        f"{answer.trace.variant} · {answer.usage.prompt_tokens} in / "
        f"{answer.usage.completion_tokens} out tokens · {answer.latency_ms / 1000:.1f}s"
    )
    first_id = verified[0].chunk_id if verified else None
    nxt = (
        _next((OPEN_SECTION, f'{OPEN_SECTION}(chunk_id="{first_id}") to read source 1 in context'))
        if first_id
        else _next((SEARCH, f'{SEARCH}(query="{question}") to look for sources yourself'))
    )
    if answer.insufficient_evidence:
        nxt += (
            ', or answer with strategy="search_loop" to search in several rounds before answering'
        )
    lines.append(nxt)
    return "\n".join(lines)


def _history_description() -> str:
    return f"""Track a phrase, a section or a question across dated Mistral doc snapshots.
    Reads stored corpora only; no model writes anything here.

    USE WHEN: you need a phrase's first and last appearance, a section's dated
    diffs, or the top retrieved section for one question at every date.

    DO NOT USE: {
        _registered(
            (SEARCH, f"to search today's documentation ({SEARCH})"),
            (ANSWER, f"to generate an answer ({ANSWER})"),
        )
    }

    START WITH exactly one of text, section, or question.

    Args:
        text: Exact phrase to track with whitespace-normalized matching.
        section: docs.mistral.ai URL with optional anchor, or a page path.
        question: Question retrieved once per snapshot with the shipped reranker.
    """


async def mistral_docs_history(
    text: str | None = None,
    section: str | None = None,
    question: str | None = None,
) -> str:
    """Read the stored snapshots for one phrase, section, or question."""
    forms = [("text", text), ("section", section), ("question", question)]
    selected = [(name, value) for name, value in forms if value is not None]
    if len(selected) != 1:
        raise _bad_param(
            "history requires exactly one of text, section, or question.",
            f'use {HISTORY}(text="phrase"), {HISTORY}(section="/page#anchor"), '
            f'or {HISTORY}(question="question").',
        )
    name, value = selected[0]
    if value is None or not value.strip():
        raise _bad_param(
            f"history {name} is empty or only whitespace.",
            f"send non-whitespace text in {name}.",
        )
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
                result = await history_service.question_history(value, SNAPSHOT_MANIFEST)
    except (OSError, ValueError) as exc:
        raise _bad_param(
            str(exc),
            "check eval/snapshots/manifest.json and pass one documented history form.",
        ) from exc
    lines = [f"history {name}: {json.dumps(value)}"]
    if name == "text":
        first = result["first"]
        last = result["last"]
        if first is None:
            lines.append("Results: the phrase is absent from every stored snapshot.")
        else:
            lines.append(f"first: {first['snapshot']} | {first['page']} | {first['fragment_url']}")
            lines.append(f"last: {last['snapshot']} | {last['page']} | {last['fragment_url']}")
            lines.append(f"Results: found in {result['snapshots_found']} snapshot(s)")
    else:
        states = result["states"]
        # The diff clamp is per state; this one is per call, so eight edited
        # snapshots cannot arrive as eight clamped diffs in one response.
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
                    block.append(
                        f"note: diff clamped server-side to {history_service.DIFF_MAX_CHARS} chars"
                    )
            if state.get("text"):
                block.append(state["text"])
                if state.get("text_truncated"):
                    block.append(
                        "note: section text clamped server-side to "
                        f"{history_service.QUESTION_TEXT_MAX_CHARS} chars"
                    )
            size = sum(len(line) for line in block)
            if rendered and spent + size > HISTORY_MAX_CHARS:
                lines.append(
                    f"note: clamped server-side: {rendered}/{len(states)} snapshots fit the "
                    f"{HISTORY_MAX_CHARS}-character per-call budget"
                )
                break
            spent += size
            rendered += 1
            lines.extend(block)
        lines.append(f"Results: {rendered} of {len(states)} stored snapshot(s)")
    lines.append(
        _hint(
            (
                SEARCH,
                f"next: use {HISTORY} with another form, or {SEARCH}(query=...) to inspect the "
                "current index",
            ),
            (HISTORY, f"next: use {HISTORY} with another form"),
        )
    )
    return "\n".join(lines)


_TOOL_IMPLS: dict[str, Any] = {
    SEARCH: mistral_docs_search,
    OPEN_SECTION: mistral_docs_open_section,
    STEP: mistral_docs_step,
    READ_PAGE: mistral_docs_read_page,
    FIND_ON_PAGE: mistral_docs_find_on_page,
    ANSWER: mistral_docs_answer,
    VERIFY_QUOTES: mistral_docs_verify_quotes,
    HISTORY: mistral_docs_history,
}
"""Every tool this server can register. Only the allowlisted ones are
registered below, so a disabled tool is absent from discovery, not an error."""

_DESCRIPTIONS: dict[str, Any] = {
    SEARCH: _search_description,
    OPEN_SECTION: _open_section_description,
    STEP: _step_description,
    READ_PAGE: _read_page_description,
    FIND_ON_PAGE: _find_on_page_description,
    ANSWER: _answer_description,
    VERIFY_QUOTES: _verify_quotes_description,
    HISTORY: _history_description,
}
"""What each tool tells a model about itself. Built at registration, because a
DO NOT USE clause must never name a tool the allowlist turned off (D-029)."""

TOOL_ANNOTATIONS = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
}
"""What every tool here is: a read of one pinned corpus.

No tool writes anything (D-026), the same arguments return the same sections,
and the index is a vendored snapshot rather than the open web. A host that sees
no hints has to assume the worst and ask the user to approve every call; Mistral
Work does, and sends `_confirmationReason` on the attempt that asks."""

for _tool_name in _TOOL_ORDER:
    if _tool_name in _ENABLED_TOOLS:
        _impl = _TOOL_IMPLS[_tool_name]
        _impl.__doc__ = _DESCRIPTIONS[_tool_name]()
        mcp.tool(title=_TOOL_TITLES[_tool_name], annotations=TOOL_ANNOTATIONS)(_impl)


@mcp.resource(
    "glossator://guide",
    name="How to use the Mistral documentation tools",
    description="The tool flow and the shared rules every tool assumes.",
    mime_type="text/markdown",
)
def guide_resource() -> str:
    return _guide_text()


def _guide_steps_rows() -> str:
    """The tool-flow table over the registered tools only."""
    rows = []
    step = 0
    if SEARCH in _ENABLED_TOOLS:
        step += 1
        rows.append(
            f"| {step} | {SEARCH} | you need where the docs say something. START WITH max_hits=5 |"
        )
    if OPEN_SECTION in _ENABLED_TOOLS:
        step += 1
        rows.append(
            f"| {step} | {OPEN_SECTION} | a hit looks promising; read it and its neighbours |"
        )
    nav = [name for name in (FIND_ON_PAGE, READ_PAGE, STEP) if name in _ENABLED_TOOLS]
    if nav:
        step += 1
        rows.append(
            f"| {step} | {' · '.join(nav)} | follow an exact phrase, a range, or walk the page |"
        )
    if VERIFY_QUOTES in _ENABLED_TOOLS:
        step += 1
        rows.append(
            f"| {step} | {VERIFY_QUOTES} | you wrote the answer yourself; verify each quote, "
            "keep only verified quotes, paste the Sources block |"
        )
    if ANSWER in _ENABLED_TOOLS:
        step += 1
        rows.append(f"| {step} | {ANSWER} | you owe the user an answer, with verified citations |")
    if HISTORY in _ENABLED_TOOLS:
        rows.append(
            f"| any | {HISTORY} | track a phrase, section, or question across stored dates |"
        )
    return "\n".join(rows)


def _guide_limits_rows() -> str:
    """The limits table over the registered tools only."""
    return "\n".join(
        f"| `{name}` | {low}-{high} | {default} |"
        for name, (low, high, default) in LIMITS.items()
        if name.split(".", 1)[0] in _ENABLED_TOOLS
    )


def _guide_preference_line() -> str:
    if ANSWER in _ENABLED_TOOLS and VERIFY_QUOTES in _ENABLED_TOOLS:
        return (
            f"Prefer `{ANSWER}` for questions and the page tools for exploration. "
            f"When you write the answer yourself, verify it with `{VERIFY_QUOTES}`."
        )
    if ANSWER in _ENABLED_TOOLS:
        return f"Prefer `{ANSWER}` for questions and the page tools for exploration."
    if VERIFY_QUOTES in _ENABLED_TOOLS:
        return (
            "Search, open or read the sections you rely on, write the answer with "
            f"`[n]` markers and verbatim quotes, then call `{VERIFY_QUOTES}`."
        )
    return "Search the index, then read the sections you rely on before answering."


def _guide_text() -> str:
    limits_rows = _guide_limits_rows()
    steps_rows = _guide_steps_rows()
    preference = _guide_preference_line()
    cite_rules = (
        "- Write the answer with `[n]` markers and verbatim quotes, then call "
        f"`{VERIFY_QUOTES}` with the draft and the quotes. Keep only quotes it "
        "verified, drop every marker it names as uncovered, and paste its "
        "Sources block.\n"
        if VERIFY_QUOTES in _ENABLED_TOOLS
        else ""
    )
    return f"""# Using the Mistral documentation tools

Mistral's documentation, indexed as citable sections. Every hit prints its
citation target as `url#anchor`. Cite that exact string, never a URL or anchor
from memory. Many sections have no anchor, and a made-up one points a reader
nowhere.

| Step | Tool | When |
|---|---|---|
{steps_rows}

{preference}

## Resources

There are exactly three:

- `glossator://guide`: shared rules and tool flow.
- `glossator://index`: every page, with url, title, and kind on one line.
- `glossator://context`: limits, id formats, corpus commit, document counts, and model ids.

There are no other URIs. `glossator://help` and `glossator://page/<url>` do not
exist. Use tools to drill down instead of inventing resource URIs.

## Server-side limits

Values outside these ranges are clamped. A `note:` line names every
value the server moved:

| Parameter | Range | Default |
|---|---|---|
{limits_rows}

The expensive paths use independent caps. `{ANSWER}` runs at most 4 retrieval
rounds with a retrieval depth of 8. Tool parameters cannot raise these caps.

## Rules

- Never fabricate documentation URLs or anchors. Cite only a `url#anchor`
  exactly as a tool printed it; quote only text that appears in a hit's
  content.
{cite_rules}- Pass ids exactly as printed: chunk ids and `page_url` values come from
  results. Do not construct or recall ids.
- Read the last line of every response: `next:` names the call that fits what
  you just got. `response_format="{DETAILED}"` restores the scores, offsets and
  pagination calls the concise rendering leaves out.
- An empty result says which kind of empty it is and echoes your query. A
  `note:` line names a value the server moved or a leg that could not apply.
- Unknown parameter names are rejected with `E_BAD_PARAM` naming the right one
  before running. A call that returns results applied every argument you sent.
- Errors are typed (`E_BAD_PARAM`, `E_UNKNOWN_PAGE`, `E_UNKNOWN_CHUNK`,
  `E_EMPTY_QUERY`, `E_BUSY`, `E_UPSTREAM`) and carry a `next:` line. `E_BUSY`
  says retry the identical call; rephrasing is refused exactly as fast.
- The index covers docs.mistral.ai guides, API reference and model cards
  (commit and counts in `glossator://context`). It is not the whole internet:
  if the corpus lacks a topic, say so. Do not answer from memory.
- `{HISTORY}` reads stored corpora for text and section forms. Its question form
  runs retrieval with the shipped reranker once per date and never generates text.
"""


@mcp.resource(
    "glossator://index",
    name="Indexed pages",
    description="Every indexed page with its url, title, and kind on one line.",
    mime_type="text/tab-separated-values",
)
def index_resource() -> str:
    pages = _manifest_pages()
    lines = [f"# glossator corpus · {len(pages)} pages · docs commit {_corpus_commit(pages)}"]
    lines.append("url\ttitle\tkind")
    for page in pages:
        title = str(page.get("title", "")).replace("\t", " ")
        lines.append(f"{page.get('url', '')}\t{title}\t{page.get('kind', '')}")
    lines.append("# the url column is the page_url the tools take")
    return "\n".join(lines)


async def _variant_documents(name: str) -> int | None:
    """Document count for a variant, best-effort, briefly cached."""
    cached = _count_cache.get(name)
    now = time.monotonic()
    if cached and now - cached[0] < _COUNT_CACHE_SECONDS:
        return cached[1]
    try:
        if name == _variant_name:
            engine: SearchEngine = _engine
        else:
            engine = _extra_engines.get(name) or SearchEngine(RetrievalConfig.shipped(variant=name))
            _extra_engines[name] = engine
        count = await asyncio.wait_for(engine.document_count(), timeout=5.0)
    except Exception as exc:
        logger.warning("Document count failed", variant=name, error=str(exc))
        count = None
    _count_cache[name] = (now, count)
    return count


@mcp.resource(
    "glossator://context",
    name="Server context",
    description="Limits, id formats, corpus commit and freshness, document counts, model ids.",
    mime_type="application/json",
)
async def context_resource() -> str:
    # The manifest is a file read inside an async handler; threaded so a slow
    # disk never blocks the event loop.
    pages = await asyncio.to_thread(_manifest_pages)
    kinds: dict[str, int] = {}
    for page in pages:
        kind = str(page.get("kind", "?"))
        kinds[kind] = kinds.get(kind, 0) + 1
    variants: dict[str, Any] = {}
    for name in sorted(VARIANTS):
        variants[name] = {
            "schema": VARIANTS[name].schema_name,
            "served": name == _variant_name,
            "documents": await _variant_documents(name),
        }
    payload = {
        "corpus": {
            "pages": len(pages),
            "source_commit": _corpus_commit(pages) if pages else None,
            "source_repo": "mistralai/platform-docs-public",
            "license": "Apache-2.0",
            "kinds": kinds,
        },
        "variant_served": _variant_name,
        "variants": variants,
        "limits": {name: [low, high] for name, (low, high, _) in LIMITS.items()},
        "id_formats": {
            "chunk_id": f"opaque id printed by every hit; pass to {OPEN_SECTION}",
            "page_url": f"the page url, as hits print it; pass to {READ_PAGE} and {FIND_ON_PAGE}",
            "offsets": "character offsets into the page body; end is exclusive",
        },
        "models": {
            "generation_default": MISTRAL_MEDIUM_3_5,
            "generation_served": _answer_config().model,
            "generation_available": sorted(PRICES),
            "embedding": VARIANTS[_variant_name].embedding_model_name,
        },
        "resources": ["glossator://guide", "glossator://index", "glossator://context"],
    }
    return json.dumps(payload, indent=2)


class _BearerAuthMiddleware:
    """One shared secret for the HTTP transport (D-037).

    Work's custom Connector tab auto-detects HTTP bearer auth and sends a
    static ``Authorization`` header; this middleware checks it on every HTTP
    request except the unauthenticated ``GET /health`` the Connectors Debugger
    and the tunnel use to check the server. Plain ASGI, so it also covers the
    MCP endpoint itself rather than only the tool calls inside it.
    """

    def __init__(self, app: Any, token: str) -> None:
        self.app = app
        self.token = token

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] == "lifespan":
            await self.app(scope, receive, send)
            return
        if scope["type"] != "http":
            # A connection that is not a request carries no header to check, so
            # it is refused rather than waved through: a transport added later
            # must not inherit an exemption written for startup.
            await _reject_scope(scope, send)
            return
        if scope.get("path") == "/health":
            await self.app(scope, receive, send)
            return
        headers = {
            name.decode("latin-1").lower(): value.decode("latin-1")
            for name, value in scope.get("headers", [])
        }
        # Constant time: a byte-by-byte comparison leaks the token's prefix to
        # anyone who can time the 401.
        if not hmac.compare_digest(headers.get("authorization", ""), f"Bearer {self.token}"):
            response = JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": "E_UNAUTHORIZED",
                        "message": (
                            "missing or wrong Authorization header: send "
                            "'Authorization: Bearer <token>'."
                        ),
                        "next": (
                            "retry with the Authorization header set to the "
                            "GLOSSATOR_MCP_TOKEN value; GET /health needs no header."
                        ),
                    }
                },
            )
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)


async def _reject_scope(scope: Any, send: Any) -> None:
    """Close a non-HTTP connection the bearer check cannot apply to."""
    if scope["type"] == "websocket":
        await send({"type": "websocket.close", "code": 1008})


def _package_version() -> str:
    try:
        from importlib.metadata import PackageNotFoundError, version

        return version("glossator")
    except PackageNotFoundError:  # running from a source tree without metadata
        return "0.0.0+unknown"


@mcp.custom_route("/health", methods=["GET"])
async def _mcp_health(request: Request) -> Response:
    """Plain health for the Connectors Debugger and the tunnel (D-037).

    Unauthenticated on purpose: the Debugger must check a server it has no
    credentials for yet. Reports the served variant, the chunk count, whether
    the embedding probe passed, and the registered tool names.
    """
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
            "chunks": chunks,
            "embedding_probe": {"passed": probe_passed, **probe_detail},
            "tools": sorted(_ENABLED_TOOLS),
            "version": _package_version(),
        }
    )


def http_middleware() -> list[StarletteMiddleware]:
    """The HTTP transport's middleware: the bearer check, when a token is set.

    One list for both entry points, so the stack the tests drive through
    ``build_http_app`` is the stack ``--http`` serves.
    """
    if not _MCP_TOKEN:
        logger.warning("GLOSSATOR_MCP_TOKEN is not set; the MCP HTTP server is open to any client.")
        return []
    return [StarletteMiddleware(_BearerAuthMiddleware, token=_MCP_TOKEN)]


def build_http_app() -> Any:
    """The Starlette app the HTTP transport serves, with auth when configured.

    When GLOSSATOR_MCP_TOKEN is set every request except GET /health must
    carry it as a bearer token. Factored out so tests can drive the transport
    without a socket.
    """
    return mcp.http_app(middleware=http_middleware())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the glossator MCP server.")
    parser.add_argument(
        "--http",
        action="store_true",
        help="Start in HTTP (streamable-HTTP) mode instead of the default stdio mode.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind host (HTTP mode only, default: 127.0.0.1).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Bind port (HTTP mode only, default: 8000).",
    )
    args = parser.parse_args()

    asyncio.run(check_embedding_once(_variant_name))

    if args.http:
        mcp.run(transport="http", host=args.host, port=args.port, middleware=http_middleware())
    else:
        mcp.run()
