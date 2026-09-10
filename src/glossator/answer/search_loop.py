"""Run answer generation with an internal search, open, grep and read tool loop.

The loop sees previews and excludes chunks already collected; final generation
reads the full collected chunks through context assembly. These are model tools
inside the HTTP answer path, not MCP tools (D-044).
"""

import json
from dataclasses import dataclass, field
from typing import Any

import structlog
from mistralai.search.toolkit.errors import SearchToolkitException
from mistralai.search.toolkit.search import GrepMode

from glossator.answer.citations import Answer
from glossator.answer.config import AnswerConfig
from glossator.answer.docs_index import DocsIndex
from glossator.answer.generation import AnswerRun
from glossator.answer.llm import LLM, Message, ToolInvocation, ToolSpec
from glossator.answer.prompts import SEARCH_LOOP_SEED_USER, SEARCH_LOOP_SYSTEM
from glossator.retrieval.engine import Hit

logger = structlog.get_logger(__name__)

NAME = "search_loop"

CAPPED_TOOL = "search"
"""Only searches are capped per round. `open`, `grep` and `read` are each bounded
by their own arguments, and dropping one costs the model a page it had already
found."""

TOOLS: list[ToolSpec] = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": (
                "Search the documentation. The query is one sentence describing what "
                "you want to find. Chunks already returned in this session are excluded."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "top_k": {
                        "type": "integer",
                        "description": (
                            "Results to return; 4 by default, 4 at the least and 10 at "
                            "most. A smaller number is raised to 4 and the result says so."
                        ),
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open",
            "description": "Show a chunk from a search result together with its neighbours.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chunk_id": {
                        "type": "string",
                        "description": "A chunk_id exactly as an earlier result printed it.",
                    },
                    "window": {
                        "type": "integer",
                        "description": "Neighbours on each side; 2 by default, 5 at most.",
                    },
                },
                "required": ["chunk_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep",
            "description": "Find an exact phrase inside one page, given its source_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_id": {
                        "type": "string",
                        "description": "A source_id exactly as an earlier result printed it.",
                    },
                    "pattern": {"type": "string"},
                },
                "required": ["source_id", "pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read",
            "description": "Read a page, or a known offset range of it, given its source_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_id": {
                        "type": "string",
                        "description": "A source_id exactly as an earlier result printed it.",
                    },
                    "start": {"type": "integer"},
                    "end": {"type": "integer"},
                },
                "required": ["source_id"],
            },
        },
    },
]


@dataclass(frozen=True, slots=True)
class ToolResult:
    """What one tool call produced, plus everything the model has to be told.

    ``message`` replaces the rendered hits (an error, or an empty result that
    explains which kind of empty). ``notes`` are appended either way, because a
    clamp still applies to a call that succeeded.
    """

    hits: list[Hit] = field(default_factory=list)
    message: str | None = None
    notes: tuple[str, ...] = ()

    def content(self, fresh: list[Hit], returned: int, limit: int | None) -> str:
        body = self.message or _render(fresh, returned, limit)
        return "\n".join([body, *self.notes])


async def answer(
    question: str,
    *,
    engine: DocsIndex,
    llm: LLM,
    config: AnswerConfig,
) -> Answer:
    run = AnswerRun(strategy=NAME, variant=engine.config.variant)
    collected: dict[str, Hit] = {}

    query = await run.prepare(question, llm=llm, config=config)
    seed = await engine.search(query.text, top_k=config.top_k)
    _collect(collected, seed)
    run.event(
        "retrieval",
        "search",
        arguments={"query": query.text, "top_k": config.top_k},
        result_ids=[hit.chunk_id for hit in seed],
        note="seed search on the question",
    )

    messages: list[Message] = [
        {
            "role": "system",
            "content": SEARCH_LOOP_SYSTEM.format(
                searches_per_round=config.searches_per_round, round_cap=config.round_cap
            ),
        },
        {
            "role": "user",
            # The loop searches the English index, so it is shown the English
            # rendering of the question and writes its queries from that; the
            # answer is generated from the original (D-008a).
            "content": SEARCH_LOOP_SEED_USER.format(
                question=query.text,
                seed=_render(seed, len(seed), config.tool_result_chars),
            ),
        },
    ]

    for round_number in range(1, config.round_cap + 1):
        run.rounds = round_number
        completion = await llm.complete(
            messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=config.loop_max_tokens,
            purpose=f"{NAME}:round_{round_number}",
        )
        run.spent(completion)
        if not completion.tool_calls:
            run.event("loop", "stop", note=completion.text[:400] or completion.finish_reason)
            break

        # Every tool call in the assistant message has to be answered, so calls
        # over the per-round search cap are answered with a refusal rather than
        # left hanging.
        dropped = _over_round_cap(completion.tool_calls, config.searches_per_round)
        messages.append(_assistant_message(completion.text, completion.tool_calls))

        for invocation in completion.tool_calls:
            if invocation.id in dropped:
                note = (
                    f"note: not run: this round already used its "
                    f"{config.searches_per_round} searches. next: ask for it in the next round."
                )
                run.event("tool", invocation.name, arguments=dict(invocation.arguments), note=note)
                messages.append(_tool_message(invocation, note))
                continue

            result = await _invoke(invocation, engine=engine, config=config, seen=collected)
            fresh = _collect(collected, result.hits)
            run.event(
                "tool",
                invocation.name,
                arguments=dict(invocation.arguments),
                result_ids=[hit.chunk_id for hit in fresh],
                note="; ".join(filter(None, (result.message, *result.notes))) or None,
            )
            messages.append(
                _tool_message(
                    invocation,
                    result.content(fresh, len(result.hits), _result_chars(invocation.name, config)),
                )
            )
    else:
        run.event("loop", "round_cap", note=f"stopped after {config.round_cap} rounds")

    logger.info("Search loop finished", rounds=run.rounds, chunks=len(collected))
    return await run.finish(question, list(collected.values()), llm=llm, config=config)


async def _invoke(
    invocation: ToolInvocation,
    *,
    engine: DocsIndex,
    config: AnswerConfig,
    seen: dict[str, Hit],
) -> ToolResult:
    """Run one tool call. A bad call comes back as a message, not an exception."""
    arguments = invocation.arguments
    try:
        if invocation.name == "search":
            query = _string(arguments, "query")
            # A round trip costs the same whether it returns one chunk or eight,
            # so the model's own top_k only ever widens the result.
            top_k, notes = _clamp(arguments, "top_k", config.tool_top_k, config.max_tool_top_k)
            hits = await engine.search(query, exclude_ids=set(seen), top_k=top_k)
            return ToolResult(
                hits=hits,
                message=None if hits else f"No results for that query: {query!r}.",
                notes=notes,
            )

        if invocation.name == "open":
            chunk_id = _string(arguments, "chunk_id")
            hit = seen.get(chunk_id) or await engine.get_chunk(chunk_id)
            if hit is None or hit.start_offset is None or hit.end_offset is None:
                return ToolResult(message=_unknown_id("chunk_id", chunk_id))
            window, notes = _clamp(arguments, "window", 2, config.max_open_window, floor=1)
            reader = engine.navigation_at(hit.source_id, hit.start_offset, hit.end_offset)
            return ToolResult(hits=await reader.around(window=window), notes=notes)

        if invocation.name == "grep":
            source_id = _string(arguments, "source_id")
            pattern = _string(arguments, "pattern")
            hits = await engine.navigation_at(source_id).grep(
                pattern, mode=GrepMode.PHRASE, top_k=config.tool_top_k
            )
            return ToolResult(
                hits=hits,
                message=None
                if hits
                else f"No line on that page contains {pattern!r}. next: read the page, "
                "or search for the idea in one sentence instead of an exact phrase.",
            )

        if invocation.name == "read":
            source_id = _string(arguments, "source_id")
            start = _optional_integer(arguments, "start")
            end = _optional_integer(arguments, "end")
            hits = await engine.navigation_at(source_id).read(
                start, end, top_k=config.page_read_top_k
            )
            return ToolResult(
                hits=hits,
                message=None
                if hits
                else f"No chunks between offsets {start} and {end} on that page. "
                "next: call read with no start or end to get the whole page.",
            )
    except SearchToolkitException as error:
        # The index raises this for a source_id it does not hold, which is the
        # loop's most likely failure: a url the model half-remembered. It ends
        # the tool call, not the answer.
        return ToolResult(message=f"{invocation.name} failed: {error}. {_COPY_IDS}")
    except (KeyError, ValueError, TypeError) as error:
        return ToolResult(message=f"{invocation.name} failed: {error}. {_COPY_IDS}")
    return ToolResult(
        message=f"No tool named {invocation.name!r}. next: use search, open, grep or read."
    )


_COPY_IDS = (
    "next: use a chunk_id or source_id exactly as an earlier result printed it, "
    "never one written from memory."
)


def _unknown_id(field_name: str, value: str) -> str:
    return f"No chunk with {field_name}={value!r}. {_COPY_IDS}"


def _over_round_cap(invocations: tuple[ToolInvocation, ...], searches_per_round: int) -> set[str]:
    """Ids of the calls this round will not run.

    Only searches count against the cap: they are the expensive, unbounded ones,
    and dropping a follow-up `open` throws away work the model already did.
    """
    dropped: set[str] = set()
    searches = 0
    for invocation in invocations:
        if invocation.name != CAPPED_TOOL:
            continue
        searches += 1
        if searches > searches_per_round:
            dropped.add(invocation.id)
    return dropped


def _result_chars(tool: str, config: AnswerConfig) -> int | None:
    return config.tool_result_chars if tool == CAPPED_TOOL else config.open_result_chars


def _collect(collected: dict[str, Hit], hits: list[Hit]) -> list[Hit]:
    """Keep the chunks that are new, and return only those."""
    fresh = [hit for hit in hits if hit.chunk_id not in collected]
    for hit in fresh:
        collected[hit.chunk_id] = hit
    return fresh


def _render(hits: list[Hit], returned: int, limit: int | None) -> str:
    """A tool result: enough to judge relevance, not the whole chunk.

    ``limit`` is ``None`` in the grid's "full" configuration (D-035c): the whole
    collapsed chunk is shown, and only the no-new-chunks message stays short.
    """
    if not hits:
        return (
            f"No new chunks: all {returned} results were already collected. "
            "next: search for something the collected chunks do not cover."
        )
    return "\n\n".join(
        f"chunk_id={hit.chunk_id} source_id={hit.source_id} "
        f"offsets={hit.start_offset}-{hit.end_offset}\n"
        f"{hit.heading_line}\n{hit.preview(limit)}"
        for hit in hits
    )


def _tool_message(invocation: ToolInvocation, content: str) -> Message:
    return {
        "role": "tool",
        "tool_call_id": invocation.id,
        "name": invocation.name,
        "content": content,
    }


def _assistant_message(text: str, invocations: tuple[ToolInvocation, ...]) -> Message:
    return {
        "role": "assistant",
        "content": text,
        "tool_calls": [
            {
                "id": invocation.id,
                "type": "function",
                "function": {
                    "name": invocation.name,
                    "arguments": json.dumps(invocation.arguments),
                },
            }
            for invocation in invocations
        ],
    }


def _string(arguments: dict[str, Any], key: str) -> str:
    value = arguments.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"missing or empty {key!r}")
    return value


def _clamp(
    arguments: dict[str, Any], key: str, default: int, ceiling: int, floor: int | None = None
) -> tuple[int, tuple[str, ...]]:
    """The value to use, and the note that says it was changed (D-029).

    A clamp the model cannot see is a clamp it will keep hitting, so every one
    of them comes back in the tool result.
    """
    lower = default if floor is None else floor
    value = arguments.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        return default, ()
    clamped = min(max(value, lower), ceiling)
    if clamped == value:
        return clamped, ()
    return clamped, (f"note: clamped server-side: {key}={value} → {clamped}",)


def _optional_integer(arguments: dict[str, Any], key: str) -> int | None:
    """An offset bound the model may leave out, or send as a string."""
    value = arguments.get(key)
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value)
    return None


__all__ = ["CAPPED_TOOL", "NAME", "TOOLS", "ToolResult", "answer"]
