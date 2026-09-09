"""Read-only MCP tools for search, page navigation, and cited answers."""

import argparse
import asyncio
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

from entrypoints.param_suggestions import suggest_fields
from glossator.answer import service as answer_service
from glossator.answer.citations import Answer
from glossator.answer.config import (
    DEFAULT_VARIANT,
    MISTRAL_MEDIUM_3_5,
    PRICES,
    AnswerConfig,
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

# Generation model for the ask tool. The default is the shipped configuration
# (D-017); a deployment on the free tier points this at a reachable model
# (D-017a) without widening the tool's parameter surface.
_model_env = os.environ.get("GLOSSATOR_MODEL", "")


def _answer_config() -> AnswerConfig:
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
            continuation = (
                f'read(source_id="{hit.source_id}", start_offset={hit.start_offset}, '
                f"end_offset={hit.end_offset}, top_k=1)"
            )
        else:
            continuation = f'read(source_id="{hit.source_id}", top_k=1)'
        preview = preview[:chars] + f" …[truncated; use {continuation}]"
    lines.append(f"    {preview}")
    return "\n".join(lines)


def _source_id_of(hit: Hit) -> str:
    return hit.source_id


def _deeper_search_line(query: str, ids: list[str], **fixed: Any) -> str:
    """A copy-pasteable call that excludes exactly what this page returned."""
    id_list = ", ".join(json.dumps(i) for i in ids)
    parts = [f"query={json.dumps(query)}", f"exclude_ids=[{id_list}]"]
    parts += [f"{k}={json.dumps(v)}" for k, v in fixed.items()]
    return f"search({', '.join(parts)})"


mcp: FastMCP = FastMCP(
    "glossator",
    instructions=(
        "Start with search, then open the hit to read the section in context "
        "before answering; prefer `ask` for questions and the navigation tools "
        "for exploration. Read `glossator://guide` for the shared rules; never "
        "fabricate documentation URLs or anchors: cite only a URL and anchor "
        "exactly as a tool printed them."
    ),
)


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


@mcp.tool()
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
        lines.append(
            f'next: open(chunk_id="{hits[0].chunk_id}") to read hit 1 in context, '
            f'or ask(question="{query}") for a grounded answer'
        )
    else:
        lines.append(
            f"Results: {trace.kept}/{trace.considered} kept/considered "
            f"(all that matched within top_k={applied})"
        )
        lines.append(
            f'next: open(chunk_id="{hits[0].chunk_id}") to read hit 1 in context, '
            f'or ask(question="{query}") for a grounded answer'
        )
    return "\n".join(lines).rstrip()


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


class _admission_or_busy:
    """Acquire an admission slot or fail immediately with the typed retry hint."""

    async def __aenter__(self) -> None:
        if _admission.locked():
            raise _busy()
        await _admission.acquire()

    async def __aexit__(self, *exc: object) -> None:
        _admission.release()


@mcp.tool()
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
    lines.append(
        f'next: read(source_id="{anchor.source_id}") for the whole page, '
        f'or grep(source_id="{anchor.source_id}", pattern="…") for an exact phrase on it'
    )
    return "\n".join(lines).rstrip()


@mcp.tool()
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
            "next: open(chunk_id=…) around a hit you hold, or search(query=…) to change page",
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


@mcp.tool()
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
                    "next: search(query=…) to find another page with content",
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
            lines.append(
                f'next: grep(source_id="{source_id}", pattern="…") to jump to an exact phrase'
            )
    else:
        lines.append(f"Results: {len(hits)} chunks (the whole requested range; none dropped)")
        lines.append(
            f'next: grep(source_id="{source_id}", pattern="…") for an exact '
            "phrase on this page, or search(query=…) to change page"
        )
    return "\n".join(lines).rstrip()


@mcp.tool()
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
            f'next: search(query="{pattern}") corpus-wide, or grep with mode="term" '
            "to relax the order"
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
    lines.append(f'next: open(chunk_id="{hits[0].chunk_id}") for context around match 1')
    return "\n".join(lines).rstrip()


@mcp.tool()
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
    except ValidationError as exc:
        # A bad GLOSSATOR_MODEL is deterministic misconfiguration: retrying the
        # identical call, as E_UPSTREAM tells a client to, can never fix it.
        raise _bad_param(
            f"the GLOSSATOR_MODEL setting is invalid: {exc}",
            f"GLOSSATOR_MODEL must be one of {sorted(PRICES)}",
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
    lines.append(f"Sources ({len(verified)} verified):")
    for citation in verified:
        heading = headings.get(citation.n, "")
        # The fragment link scrolls a supporting browser to the quoted span and
        # still carries the anchor inside it, so it is the link worth printing;
        # the citation_url remains the canonical form in the API's JSON.
        link = citation.fragment_url or citation.citation_url
        lines.append(f"[{citation.n}] {link}" + (f" | {heading}" if heading else ""))
    if not verified:
        lines.append("(none)")
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
        f'next: open(chunk_id="{first_id}") to read source 1 in context'
        if first_id
        else f'next: search(query="{question}") to look for sources yourself'
    )
    if answer.insufficient_evidence:
        nxt += ', or ask with strategy="search_loop" to search in several rounds before answering'
    lines.append(nxt)
    return "\n".join(lines)


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


def _guide_text() -> str:
    limits_rows = "\n".join(
        f"| `{name}` | {low}-{high} | {default} |" for name, (low, high, default) in LIMITS.items()
    )
    return f"""# Using glossator

Mistral's documentation, indexed as citable sections. Every hit prints its
citation target as `url#anchor`. Cite that exact string, never a URL or anchor
from memory. Many sections have no anchor, and a made-up one points a reader
nowhere.

| Step | Tool | When |
|---|---|---|
| 1 | search | you need where the docs say something. START WITH top_k=5 |
| 2 | open | a hit looks promising; read it and its neighbours |
| 3 | grep · read · navigate | follow an exact phrase, a range, or walk the page |
| 4 | ask | you owe the user an answer, with verified citations |

Prefer `ask` for questions and the navigation tools for exploration.

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
- Pass ids exactly as printed: chunk ids to `open`, `source_id` and offsets to
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
        mcp.run(transport="http", host=args.host, port=args.port)
    else:
        mcp.run()
