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
from glossator.answer.citations import Answer
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
SNAPSHOT_MANIFEST = Path(
    os.environ.get("GLOSSATOR_SNAPSHOT_MANIFEST", "eval/snapshots/manifest.json")
)

# Bearer token for the HTTP transport (D-037). When set, every MCP HTTP
# request except GET /health must carry `Authorization: Bearer <token>`.
_MCP_TOKEN = os.environ.get("GLOSSATOR_MCP_TOKEN", "")

_TOOL_ORDER = ("search", "open", "navigate", "read", "grep", "ask", "cite", "history")
"""Every tool this server can register, in guide order."""


def _parse_tool_allowlist(raw: str) -> frozenset[str]:
    """Which tools to register from GLOSSATOR_MCP_TOOLS.

    Unset or blank means every tool. Unknown names are ignored with a warning:
    a typo must not take down the tools that were named correctly.
    """
    if not raw.strip():
        return frozenset(_TOOL_ORDER)
    wanted = {part.strip() for part in raw.split(",") if part.strip()}
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

LIMITS: dict[str, tuple[int, int, int]] = {
    "search.top_k": (1, 50, 5),
    "open.window": (1, 10, 2),
    "navigate.top_k": (1, 10, 1),
    "read.top_k": (1, 100, 20),
    "grep.top_k": (1, 25, 5),
    "cite.quotes": (1, 20, 20),
}
"""name -> (low, high, default). Published in glossator://context."""


def _error(code: str, message: str, next_hint: str) -> ToolError:
    return ToolError("\n".join([f"error: {code}", message, f"next: {next_hint}"]))


def _bad_param(message: str, next_hint: str) -> ToolError:
    return _error("E_BAD_PARAM", message, next_hint)


def _unknown_chunk(chunk_id: str) -> ToolError:
    return _error(
        "E_UNKNOWN_CHUNK",
        f'chunk id "{chunk_id}" is not in the index.',
        "use a chunk id exactly as a search or open result printed it; never use one "
        "recalled from memory. search(query=...) lists chunk ids.",
    )


def _unknown_page(source_id: str) -> ToolError:
    return _error(
        "E_UNKNOWN_PAGE",
        f'no indexed page has source_id "{source_id}".',
        "use the source_id exactly as a hit printed it; never use a URL recalled from "
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


def _hint(*choices: tuple[str, str]) -> str:
    """The first suggestion whose tool this deployment registered (D-029).

    A `next:` line, or a truncation marker, that names a tool the allowlist
    turned off is the same trap as one naming a parameter the tool lacks: the
    model calls it, gets "unknown tool", and has no failure to act on. The
    choices are tried in order and the last one is the fallback that assumes
    nothing.
    """
    for tool, text in choices:
        if tool in _ENABLED_TOOLS:
            return text
    return "read `glossator://guide` for the tools this deployment registered"


def _next(*choices: tuple[str, str]) -> str:
    return f"next: {_hint(*choices)}"


def _hit_block(hit: Hit, n: int, chars: int | None, mark: bool = False) -> str:
    """One retrieved unit, always carrying its own citation url and handle.

    Long payloads print the anchor on each unit so a citation never reuses the
    page-top link for a section further down (D-029).
    """
    star = "*" if mark else ""
    lines = [f"[{n}]{star} {hit.citation_url}"]
    meta = [f"score {hit.score:.3f}"]
    if hit.kind:
        meta.append(hit.kind)
    if hit.heading_line:
        meta.append(hit.heading_line)
    lines.append(f"    {' · '.join(meta)}")
    handle = f'chunk id "{hit.chunk_id}"'
    if hit.start_offset is not None and hit.end_offset is not None:
        handle += f" · offsets {hit.start_offset}..{hit.end_offset}"
    lines.append(f"    {handle}")
    preview = hit.content if chars is None else " ".join(hit.content.split())
    if chars is not None and len(preview) > chars:
        if hit.start_offset is not None and hit.end_offset is not None:
            ranged = (
                f'read(source_id="{hit.source_id}", start_offset={hit.start_offset}, '
                f"end_offset={hit.end_offset}, top_k=1)"
            )
        else:
            ranged = f'read(source_id="{hit.source_id}", top_k=1)'
        continuation = _hint(
            ("read", ranged),
            ("open", f'open(chunk_id="{hit.chunk_id}", window=1)'),
            ("grep", f'grep(source_id="{hit.source_id}", pattern="…")'),
        )
        preview = preview[:chars] + f" …[truncated; use {continuation}]"
    lines.append(f"    {preview}")
    return "\n".join(lines)


def _deeper_search_line(query: str, ids: list[str], **fixed: Any) -> str:
    """A copy-pasteable call that excludes exactly what this page returned."""
    id_list = ", ".join(json.dumps(i) for i in ids)
    parts = [f"query={json.dumps(query)}", f"exclude_ids=[{id_list}]"]
    parts += [f"{k}={json.dumps(v)}" for k, v in fixed.items()]
    return f"search({', '.join(parts)})"


def _instructions() -> str:
    """Server instructions naming the flow over the registered tools only.

    A deployment that disables tools through GLOSSATOR_MCP_TOOLS must not
    promise a flow it cannot run, so each clause is conditional on its tool.
    """
    flow = "Start with search"
    if "open" in _ENABLED_TOOLS:
        flow += ", then open the hit to read the section in context before answering"
    else:
        flow += " to find the sections that state each claim"
    if "cite" in _ENABLED_TOOLS:
        flow += (
            "; write the answer with [n] markers and verbatim quotes, then call "
            "`cite` and keep only verified quotes"
        )
    if "ask" in _ENABLED_TOOLS:
        flow += "; prefer `ask` for questions and the navigation tools for exploration"
    elif "cite" in _ENABLED_TOOLS:
        flow += "; use the navigation tools for exploration"
    if "history" in _ENABLED_TOOLS:
        flow += "; use `history` for changes over time"
    return (
        f"{flow}. Read `glossator://guide` for the shared rules; never "
        "fabricate documentation URLs or anchors: cite only a URL and anchor "
        "exactly as a tool printed them."
    )


mcp: FastMCP = FastMCP("glossator", instructions=_instructions())


class _ParamGuard(Middleware):
    """Unknown argument names are a typed error, not a silent drop (D-029).

    The schema already says ``additionalProperties: false``, but the default
    failure is a pydantic stack trace the model cannot act on. This guard sits
    at ``tools/call``, where the raw arguments still exist, and answers with
    ``E_BAD_PARAM`` naming the parameter the caller probably meant.
    """

    def __init__(self, server: FastMCP) -> None:
        self.server = server

    async def on_call_tool(self, context: Any, call_next: Any) -> Any:
        name = context.message.name
        arguments = dict(context.message.arguments or {})
        tool = await self.server.get_tool(name)
        if tool is None:
            return await call_next(context)
        known = set(tool.parameters["properties"])
        unknown = [k for k in arguments if k not in known and not k.startswith("_")]
        if not unknown:
            return await call_next(context)
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


_guard = _ParamGuard(mcp)
mcp.add_middleware(_guard)


async def search(
    query: str,
    top_k: int = 5,
    kinds: list[str] | None = None,
    locales: list[str] | None = None,
    exclude_ids: list[str] | None = None,
) -> str:
    """Search the indexed Mistral documentation by meaning or keywords.
    Every hit carries its own url#anchor and a chunk id for open().

    USE WHEN: you need a documented parameter, limit, concept, or code pattern.

    DO NOT USE: to answer a question end to end (ask does that with verified
    citations); to read inside a page you already have a hit in (open, grep,
    read).

    START WITH top_k=5.

    Args:
        query: Words to find, in natural language; two or three distinctive words beat a sentence.
        top_k: Maximum hits to return, 1-50 (clamped, announced in a note: line).
        kinds: Page kinds to keep: any of "doc", "api", "model". Omit for all kinds.
        locales: Locales to keep, e.g. ["en"]. Omit for every locale.
        exclude_ids: Chunk ids to skip, exactly as earlier results printed them, so each search
            surfaces fresh context.
    """
    if not query.strip():
        raise _empty_query("query", query)
    applied, note = _clamp("search.top_k", top_k)
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
                kinds=kinds_set or None,
                locales=locales_set or None,
            )
        except RetrieverException as exc:
            raise _upstream(f"search({query!r})", exc) from exc

    lines = [f'query: "{query}" · variant {_variant_name} · hybrid bm25+vector']
    if note:
        lines.append(note)
    if filter_note:
        lines.append(filter_note)
    lines.append(f"hits: {trace.kept}/{trace.considered} kept/considered")
    if trace.lexical_footing is False:
        lines.append(
            "note: no lexical footing in the corpus; vector retrieval still ran, "
            f"missing terms={list(trace.missing_terms)}"
        )
    lines.append("")
    for i, hit in enumerate(hits, 1):
        lines.append(_hit_block(hit, i, PREVIEW_CHARS))
        lines.append("")
    if not hits:
        lines.extend(_empty_search(query, kinds_set, locales_set, exclude_ids or []))
    elif len(hits) == applied:
        lines.append(
            f"Results: {trace.kept}/{trace.considered} kept/considered "
            f"(top_k={applied} was full; more may exist)"
        )
        lines.append("go deeper, copy-paste:")
        seen_ids = list(dict.fromkeys([*(exclude_ids or []), *(hit.chunk_id for hit in hits)]))
        fixed: dict[str, Any] = {}
        if kinds:
            fixed["kinds"] = kinds
        if locales:
            fixed["locales"] = locales
        lines.append("  " + _deeper_search_line(query, seen_ids, **fixed))
        lines.append(_search_next(query, hits[0]))
    else:
        lines.append(
            f"Results: {trace.kept}/{trace.considered} kept/considered "
            f"(all that matched within top_k={applied})"
        )
        lines.append(_search_next(query, hits[0]))
    return "\n".join(lines).rstrip()


def _search_next(query: str, first: Hit) -> str:
    """What to do with a hit, over the tools this deployment registered."""
    reading = _hint(
        ("open", f'open(chunk_id="{first.chunk_id}") to read hit 1 in context'),
        ("read", f'read(source_id="{first.source_id}") to read hit 1\'s page'),
    )
    if "ask" in _ENABLED_TOOLS:
        return f'next: {reading}, or ask(question="{query}") for a grounded answer'
    if "cite" in _ENABLED_TOOLS:
        return f"next: {reading}, then cite(draft=…, quotes=[…]) to verify what you quote"
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


def _page_next(source_id: str, chunk_id: str | None = None) -> str:
    """Where to go from a page, over the tools this deployment registered."""
    choices = [
        ("read", f'read(source_id="{source_id}") for the whole page'),
        ("grep", f'grep(source_id="{source_id}", pattern="…") for an exact phrase on it'),
    ]
    if chunk_id is not None:
        choices.append(("open", f'open(chunk_id="{chunk_id}") for context around it'))
    choices.append(("search", "search(query=…) to change page"))
    return _next(*choices)


class _admission_or_busy:
    """Acquire an admission slot or fail immediately with the typed retry hint."""

    async def __aenter__(self) -> None:
        if _admission.locked():
            raise _busy()
        await _admission.acquire()

    async def __aexit__(self, *exc: object) -> None:
        _admission.release()


async def open(chunk_id: str, window: int = 2) -> str:
    """Read a chunk and its neighbours in reading order, on its own page.
    The hit you pass is marked *; window chunks each side, offsets shown.

    USE WHEN: a search hit looks promising and you need its context, such as a
    definition before a sentence or rows cut off from a table.

    DO NOT USE: to fetch a known offset range verbatim (read); to step one
    chunk at a time (navigate); to find hits (search).

    START WITH window=2.

    Args:
        chunk_id: Chunk id exactly as a search or open result printed it.
        window: Chunks to fetch each side of the anchor chunk, 1-10 (clamped, announced).
    """
    applied, note = _clamp("open.window", window)
    async with _admission_or_busy():
        try:
            anchor = await _engine.get_chunk(chunk_id)
        except IndexException as exc:
            raise _upstream(f"open({chunk_id!r})", exc) from exc
        if anchor is None or anchor.navigation is None:
            raise _unknown_chunk(chunk_id)
        try:
            hits = await anchor.navigation.around(window=applied)
        except IndexException as exc:
            raise _upstream(f"open({chunk_id!r})", exc) from exc

    lines = [f'page: {anchor.url} | "{anchor.page_title}"']
    if note:
        lines.append(note)
    lines.append(
        f"window: {len(hits)} chunks around {json.dumps(chunk_id)} (* marks it), reading order"
    )
    lines.append("")
    center = next((h for h in hits if h.chunk_id == chunk_id), None)
    for i, hit in enumerate(hits, 1):
        lines.append(_hit_block(hit, i, OPEN_PREVIEW_CHARS, mark=hit is center))
        lines.append("")
    lines.append(f"Results: {len(hits)} chunks")
    lines.append(_page_next(anchor.source_id))
    return "\n".join(lines).rstrip()


async def navigate(
    source_id: str, start_offset: int, end_offset: int, direction: str, top_k: int = 1
) -> str:
    """Step to the chunk before or after a known position on one page.
    Pass the source_id and offsets exactly as the hit you are stepping from.

    USE WHEN: you are walking a page section by section from a hit, or the end
    of an open() window cut a passage off.

    DO NOT USE: to expand around one hit in both directions at once (open);
    to fetch a whole range in one call (read).

    START WITH top_k=1.

    Args:
        source_id: Page source_id exactly as a hit printed it.
        start_offset: start_offset of the chunk you step from.
        end_offset: end_offset of the chunk you step from.
        direction: "next" (forward in reading order) or "previous" (backward).
        top_k: Chunks to fetch in that direction, 1-10 (clamped, announced).
    """
    if direction not in {"next", "previous"}:
        raise _bad_param(
            f'direction={direction!r} is not one of "next", "previous".',
            'use direction="next" to move forward in reading order, "previous" to move back.',
        )
    applied, note = _clamp("navigate.top_k", top_k)
    navigation = _engine.navigation_at(source_id, start_offset, end_offset)
    async with _admission_or_busy():
        try:
            hits = await (
                navigation.previous(top_k=applied)
                if direction == "previous"
                else navigation.next(top_k=applied)
            )
        except SourceNotFoundError as exc:
            raise _unknown_page(source_id) from exc
        except IndexException as exc:
            raise _upstream(f"navigate({source_id!r}, {direction})", exc) from exc
    if not hits:
        lines = [
            f"Results: 0 chunks {direction} from offsets "
            f"{start_offset}..{end_offset} on {source_id}",
            f"- you are at the {'start' if direction == 'previous' else 'end'} of the page; "
            "there is nothing further in that direction.",
            _next(
                (
                    "open",
                    "open(chunk_id=…) around a hit you hold, or search(query=…) to change page",
                ),
                ("search", "search(query=…) to change page"),
            ),
        ]
        return "\n".join(lines)
    count = (
        f"{direction} {len(hits)} chunk(s) from offsets {start_offset}..{end_offset} on {source_id}"
    )
    if len(hits) == applied:
        count += f" (top_k={applied} was full; more may exist)"
    else:
        count += " (every chunk in this direction)"
    lines = [count]
    if note:
        lines.append(note)
    lines.append("")
    for i, hit in enumerate(hits, 1):
        lines.append(_hit_block(hit, i, OPEN_PREVIEW_CHARS))
        lines.append("")
    further = "previous" if direction == "previous" else "next"
    lines.append(
        f'next: navigate(source_id="{source_id}", start_offset={hits[-1].start_offset}, '
        f'end_offset={hits[-1].end_offset}, direction="{further}") to keep walking'
    )
    return "\n".join(lines).rstrip()


async def read(
    source_id: str, start_offset: int | None = None, end_offset: int | None = None, top_k: int = 20
) -> str:
    """Fetch the chunks of one page between two offsets, verbatim.
    Omit both offsets for the whole page in reading order.

    USE WHEN: you know the page and range, such as when following an outline or
    re-reading a section without re-ranking anything.

    DO NOT USE: to expand around one search hit (open is cheaper; pass just the
    id); to find where something is (search).

    START WITH no offsets, top_k=20.

    Args:
        source_id: Page source_id exactly as a hit printed it.
        start_offset: Inclusive lower bound on chunk start (None = start of page).
        end_offset: Upper bound; a chunk is kept when it ends by this offset (None = end of page).
        top_k: Maximum chunks to return, 1-100 (clamped, announced).
    """
    applied, note = _clamp("read.top_k", top_k)
    async with _admission_or_busy():
        try:
            navigation = _engine.navigation_at(source_id)
            hits = await navigation.read(start_offset, end_offset, top_k=applied)
        except SourceNotFoundError as exc:
            raise _unknown_page(source_id) from exc
        except IndexException as exc:
            raise _upstream(f"read({source_id!r})", exc) from exc
    if not hits:
        if start_offset is None and end_offset is None:
            return "\n".join(
                [
                    f"Results: 0 content chunks on indexed page {source_id}",
                    _next(("search", "search(query=…) to find another page with content")),
                ]
            )
        raise _error(
            "E_BAD_PARAM",
            f"no chunk of {source_id} lies inside offsets "
            f"{start_offset}..{end_offset if end_offset is not None else 'end'}.",
            "this is an offset problem, not a missing page. read() with no offsets "
            "returns the whole page; or open(chunk_id=…) around a hit you hold.",
        )
    lines = [f'page: {source_id} | "{hits[0].page_title}"']
    if note:
        lines.append(note)
    if start_offset is not None or end_offset is not None:
        lines.append(
            f"range: {start_offset if start_offset is not None else 0}"
            f"..{end_offset if end_offset is not None else 'end'}"
        )
    lines.append("")
    for i, hit in enumerate(hits, 1):
        lines.append(_hit_block(hit, i, None))
        lines.append("")
    if len(hits) == applied:
        lines.append(f"Results: {len(hits)} chunks (top_k={applied}; the page may have more)")
        if hits[-1].end_offset is not None:
            lines.append(
                f'next: read(source_id="{source_id}", start_offset={hits[-1].end_offset}, '
                f"top_k={applied}) to continue after this page of chunks"
            )
        else:
            lines.append(_page_next(source_id))
    else:
        lines.append(f"Results: {len(hits)} chunks (the whole requested range; none dropped)")
        lines.append(_page_next(source_id))
    return "\n".join(lines).rstrip()


async def grep(source_id: str, pattern: str, mode: str = "phrase", top_k: int = 5) -> str:
    """Find an exact phrase or set of terms inside one indexed page.
    It matches words, not meaning.

    USE WHEN: you have a page and need an exact error string, parameter name, or
    heading.

    DO NOT USE: corpus-wide search (search); semantic matching (search).

    START WITH mode="phrase".

    Args:
        source_id: Page source_id exactly as a hit printed it.
        pattern: The words to find, in order for mode="phrase".
        mode: "phrase" (exact order, default) or "term" (all words, any order).
        top_k: Maximum matching chunks, 1-25 (clamped, announced).
    """
    if mode not in {"phrase", "term"}:
        raise _bad_param(
            f'mode={mode!r} is not one of "phrase", "term".',
            'mode="phrase" matches the words in order; "term" matches all words in any order.',
        )
    if not pattern.strip():
        raise _empty_query("pattern", pattern)
    applied, note = _clamp("grep.top_k", top_k)
    async with _admission_or_busy():
        try:
            navigation = _engine.navigation_at(source_id)
            hits = await navigation.grep(pattern, mode=GrepMode(mode), top_k=applied)
        except SourceNotFoundError as exc:
            raise _unknown_page(source_id) from exc
        except IndexException as exc:
            raise _upstream(f"grep({source_id!r}, {pattern!r})", exc) from exc
    lines = [f"matches for {json.dumps(pattern)} (mode={mode}) on {source_id}"]
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
                    "search",
                    f'search(query="{pattern}") corpus-wide, or grep with mode="term" '
                    "to relax the order",
                ),
                ("grep", 'grep with mode="term" to relax the order'),
            )
        )
        return "\n".join(lines).rstrip()
    for i, hit in enumerate(hits, 1):
        lines.append(_hit_block(hit, i, OPEN_PREVIEW_CHARS))
        lines.append("")
    count = f"Results: {len(hits)} chunks matched"
    if len(hits) == applied:
        count += f" (top_k={applied} was full; more matches may exist)"
    else:
        count += " (every match on this page)"
    lines.append(count)
    lines.append(_page_next(source_id, hits[0].chunk_id))
    return "\n".join(lines).rstrip()


async def ask(question: str, strategy: str = "single_pass") -> str:
    """Answer a question from the documentation with verified citations.
    Returns the answer with [n] markers, a numbered source list, and how many
    citations' quotes verified against their chunks.

    USE WHEN: the user wants an answer rather than a document list. The server
    retrieves, generates, and checks every quote itself.

    DO NOT USE: to browse or explore (search and the navigation tools); when
    you must quote the docs yourself (open the cited chunks and read them).

    START WITH strategy="single_pass" (one reranked retrieval, about 7 s);
    "search_loop" reads around its hits over up to four rounds for a few points
    more accuracy at three times the latency and five times the cost.

    Args:
        question: The question, in any phrasing; it is embedded, not matched verbatim.
        strategy: How evidence is gathered: "single_pass" (default), "search_loop"
            (thorough), or "outline" (experimental: picks pages from the site outline).
    """
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
            raise _upstream(f"ask({question!r})", exc) from exc
    return _answer_text(question, answer)


async def cite(draft: str, quotes: list[CiteQuote]) -> str:
    """Verify your own quotes against the chunks they claim to come from.
    Returns per-quote verdicts, fragment links for quotes that hold, and the
    markers no verified quote covers.

    USE WHEN: you wrote an answer from search, open or read hits and need to
    check each quote before showing it, with a paste-ready source list.

    DO NOT USE: to get an answer written for you (ask does that, with its own
    verified citations); to find sources (search).

    START WITH the draft and every quote you relied on, each naming a chunk_id
    exactly as a result printed it, or a page url with an optional #anchor.

    Args:
        draft: Your answer text with [n] markers, up to 20,000 characters (clamped, announced).
        quotes: The quotes behind the markers: each has n, quote, and either chunk_id
            or url. At most 20 are checked (clamped, announced).
    """
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
            raise _upstream("cite()", exc) from exc
    return _cite_text(result)


def _cite_next_hint() -> str:
    return (
        "each quote needs n, quote, and either chunk_id (exactly as a result "
        "printed it) or a page url with an optional #anchor."
    )


def _cite_text(result: cite_engine.CiteResult) -> str:
    """One cite result as text: verdicts, uncovered markers, the source list."""
    lines = []
    for line in result.notes:
        lines.append(line)
    if result.notes:
        lines.append("")
    for item in result.quotes:
        if item.verified:
            detail = item.fragment_url or item.citation_url or ""
            if item.emphasis_normalized:
                detail += " (verified after emphasis normalization)"
            lines.append(f"[{item.n}] verified: {detail}")
        else:
            lines.append(f"[{item.n}] NOT verified: {item.reason or 'unverified'}")
    lines.append("")
    if result.unverified_markers:
        named = ", ".join(f"[{n}]" for n in result.unverified_markers)
        lines.append(
            f"markers with no verified quote: {named}; remove them or fix them "
            "against a quoted source."
        )
        lines.append("")
    lines.append(result.source_list_markdown)
    lines.append("")
    lines.append(f"next: {result.next}")
    return "\n".join(lines).rstrip()


_TOOL_IMPLS: dict[str, Any] = {
    "search": search,
    "open": open,
    "navigate": navigate,
    "read": read,
    "grep": grep,
    "ask": ask,
    "cite": cite,
}
"""Every tool this server can register. Only the allowlisted ones are
registered below, so a disabled tool is absent from discovery, not an error."""


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
        _next(("open", f'open(chunk_id="{first_id}") to read source 1 in context'))
        if first_id
        else _next(("search", f'search(query="{question}") to look for sources yourself'))
    )
    if answer.insufficient_evidence:
        nxt += ', or ask with strategy="search_loop" to search in several rounds before answering'
    lines.append(nxt)
    return "\n".join(lines)


async def history(
    text: str | None = None,
    section: str | None = None,
    question: str | None = None,
) -> str:
    """Inspect stored documentation snapshots without answer generation.

    USE WHEN: you need a phrase's first and last appearance, a section's dated
    diffs, or the top retrieved section for one question at every date.

    DO NOT USE: to search only the current documentation (search); to generate
    an answer (ask).

    START WITH exactly one of text, section, or question.

    Args:
        text: Exact phrase to track with whitespace-normalized matching.
        section: docs.mistral.ai URL with optional anchor, or a page path.
        question: Question retrieved once per snapshot with the shipped reranker.
    """
    forms = [("text", text), ("section", section), ("question", question)]
    selected = [(name, value) for name, value in forms if value is not None]
    if len(selected) != 1:
        raise _bad_param(
            "history requires exactly one of text, section, or question.",
            'use history(text="phrase"), history(section="/page#anchor"), '
            'or history(question="question").',
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
        for state in states:
            target = state.get("page") or "(absent)"
            if state.get("anchor"):
                target += f"#{state['anchor']}"
            lines.append(f"{state['snapshot']}: {state['state']} | {target}")
            if state.get("diff"):
                lines.extend(["```diff", state["diff"], "```"])
                if state.get("diff_truncated"):
                    lines.append(
                        f"note: diff clamped server-side to {history_service.DIFF_MAX_CHARS} chars"
                    )
            if state.get("text"):
                lines.append(state["text"])
                if state.get("text_truncated"):
                    lines.append(
                        "note: section text clamped server-side to "
                        f"{history_service.QUESTION_TEXT_MAX_CHARS} chars"
                    )
        lines.append(f"Results: {len(states)} stored snapshot(s)")
    lines.append(
        _hint(
            (
                "search",
                "next: use history with another form, or search(query=...) to inspect the "
                "current index",
            ),
            ("history", "next: use history with another form"),
        )
    )
    return "\n".join(lines)


_TOOL_IMPLS["history"] = history

for _tool_name in _TOOL_ORDER:
    if _tool_name in _ENABLED_TOOLS:
        mcp.tool()(_TOOL_IMPLS[_tool_name])


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


@mcp.resource(
    "glossator://guide",
    name="How to use glossator",
    description="The tool flow and the shared rules every tool assumes.",
    mime_type="text/markdown",
)
def guide_resource() -> str:
    return _guide_text()


def _guide_steps_rows() -> str:
    """The tool-flow table over the registered tools only."""
    rows = []
    step = 0
    if "search" in _ENABLED_TOOLS:
        step += 1
        rows.append(
            f"| {step} | search | you need where the docs say something. START WITH top_k=5 |"
        )
    if "open" in _ENABLED_TOOLS:
        step += 1
        rows.append(f"| {step} | open | a hit looks promising; read it and its neighbours |")
    nav = [name for name in ("grep", "read", "navigate") if name in _ENABLED_TOOLS]
    if nav:
        step += 1
        rows.append(
            f"| {step} | {' · '.join(nav)} | follow an exact phrase, a range, or walk the page |"
        )
    if "cite" in _ENABLED_TOOLS:
        step += 1
        rows.append(
            f"| {step} | cite | you wrote the answer yourself; verify each quote, "
            "keep only verified quotes, paste the source list |"
        )
    if "ask" in _ENABLED_TOOLS:
        step += 1
        rows.append(f"| {step} | ask | you owe the user an answer, with verified citations |")
    if "history" in _ENABLED_TOOLS:
        rows.append("| any | history | track a phrase, section, or question across stored dates |")
    return "\n".join(rows)


def _guide_limits_rows() -> str:
    """The limits table over the registered tools only."""
    owners = {
        "search.top_k": "search",
        "open.window": "open",
        "navigate.top_k": "navigate",
        "read.top_k": "read",
        "grep.top_k": "grep",
        "cite.quotes": "cite",
    }
    return "\n".join(
        f"| `{name}` | {low}-{high} | {default} |"
        for name, (low, high, default) in LIMITS.items()
        if owners.get(name, name) in _ENABLED_TOOLS
    )


def _guide_preference_line() -> str:
    if "ask" in _ENABLED_TOOLS and "cite" in _ENABLED_TOOLS:
        return (
            "Prefer `ask` for questions and the navigation tools for exploration. "
            "When you write the answer yourself, verify it with `cite`."
        )
    if "ask" in _ENABLED_TOOLS:
        return "Prefer `ask` for questions and the navigation tools for exploration."
    if "cite" in _ENABLED_TOOLS:
        return (
            "Search, open or read the sections you rely on, write the answer with "
            "`[n]` markers and verbatim quotes, then call `cite`."
        )
    return "Search the index, then read the sections you rely on before answering."


def _guide_text() -> str:
    limits_rows = _guide_limits_rows()
    steps_rows = _guide_steps_rows()
    preference = _guide_preference_line()
    cite_rules = (
        "- Write the answer with `[n]` markers and verbatim quotes, then call "
        "`cite` with the draft and the quotes. Keep only quotes `cite` verified, "
        "drop every marker it names as uncovered, and paste its source list.\n"
        if "cite" in _ENABLED_TOOLS
        else ""
    )
    return f"""# Using glossator

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

The expensive paths use independent caps. `ask` runs at most 4 retrieval rounds
with a retrieval depth of 8. Tool parameters cannot raise these caps.

## Rules

- Never fabricate documentation URLs or anchors. Cite only a `url#anchor`
  exactly as a tool printed it; quote only text that appears in a hit's
  content.
{cite_rules}- Pass ids exactly as printed: chunk ids to `open`, `source_id` and offsets to
  `read`, `navigate` and `grep`. Do not construct or recall ids.
- Read the last line of every response: `next:` names the call that fits what
  you just got. A full `search` page also prints a copy-pasteable call that
  excludes what you have seen.
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
- `history` reads stored corpora for text and section forms. Its question form
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
    lines.append("# the url column is the source_id the tools take")
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
            "chunk_id": "opaque id printed by every hit; pass to open()",
            "source_id": "the page url, as hits print it; pass to read/navigate/grep",
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
