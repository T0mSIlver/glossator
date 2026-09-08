"""The model does its own retrieval, then answers from everything it gathered.

Four tools over the same index the MCP server exposes: `search` across pages,
`open`/`read` to pull more of a page it already landed in, `grep` to find an exact
phrase in one. Two things keep the loop from running away: chunks it has already
seen are excluded at query time, so a repeated search returns nothing and wastes
only a round, and tool results are previews -- the loop decides where to look, the
final generation reads the full chunks through context assembly.
"""

import json
from typing import Any

import structlog
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

MAX_TOOL_TOP_K = 10
"""Ceiling on what one tool call may return, whatever the model asks for."""

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
                        "description": "Results to return; 4 by default, 10 at most.",
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
                    "chunk_id": {"type": "string"},
                    "window": {"type": "integer", "description": "Neighbours on each side."},
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
                    "source_id": {"type": "string"},
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
                    "source_id": {"type": "string"},
                    "start": {"type": "integer"},
                    "end": {"type": "integer"},
                },
                "required": ["source_id"],
            },
        },
    },
]


async def answer(
    question: str,
    *,
    engine: DocsIndex,
    llm: LLM,
    config: AnswerConfig,
) -> Answer:
    run = AnswerRun(strategy=NAME, variant=engine.config.variant)
    collected: dict[str, Hit] = {}

    seed = await engine.search(question, top_k=config.top_k)
    _collect(collected, seed)
    run.event(
        "retrieval",
        "search",
        arguments={"query": question, "top_k": config.top_k},
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
            "content": SEARCH_LOOP_SEED_USER.format(
                question=question,
                seed=_render(seed, config.tool_result_chars),
            ),
        },
    ]

    for round_number in range(1, config.round_cap + 1):
        run.rounds = round_number
        completion = await llm.complete(
            messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=800,
            purpose=f"{NAME}:round_{round_number}",
        )
        run.spent(completion)
        if not completion.tool_calls:
            run.event("loop", "stop", note=completion.text[:400] or completion.finish_reason)
            break

        # Every tool call in the assistant message has to be answered, so the
        # round cap on searches is applied before the message is appended.
        invocations = completion.tool_calls[: config.searches_per_round]
        messages.append(_assistant_message(completion.text, invocations))
        for invocation in invocations:
            hits, note = await _invoke(invocation, engine=engine, config=config, seen=collected)
            fresh = _collect(collected, hits)
            run.event(
                "tool",
                invocation.name,
                arguments=dict(invocation.arguments),
                result_ids=[hit.chunk_id for hit in fresh],
                note=note,
            )
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": invocation.id,
                    "name": invocation.name,
                    "content": note or _render(fresh, _result_chars(invocation.name, config)),
                }
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
) -> tuple[list[Hit], str | None]:
    """Run one tool call. A bad call comes back as a message, not an exception."""
    arguments = invocation.arguments
    try:
        if invocation.name == "search":
            query = _string(arguments, "query")
            # A round trip costs the same whether it returns one chunk or eight, so
            # the model's own top_k only ever widens the result, never narrows it.
            top_k = min(
                max(_integer(arguments, "top_k", config.tool_top_k), config.tool_top_k),
                MAX_TOOL_TOP_K,
            )
            return await engine.search(query, exclude_ids=set(seen), top_k=top_k), None
        if invocation.name == "open":
            chunk_id = _string(arguments, "chunk_id")
            hit = seen.get(chunk_id) or await engine.get_chunk(chunk_id)
            if hit is None or hit.start_offset is None or hit.end_offset is None:
                return [], f"no chunk with id {chunk_id!r}"
            reader = engine.navigation_at(hit.source_id, hit.start_offset, hit.end_offset)
            window = _integer(arguments, "window", 2)
            return await reader.around(window=window), None
        if invocation.name == "grep":
            reader = engine.navigation_at(_string(arguments, "source_id"))
            hits = await reader.grep(
                _string(arguments, "pattern"), mode=GrepMode.PHRASE, top_k=config.tool_top_k
            )
            return hits, None if hits else "no match on that page"
        if invocation.name == "read":
            reader = engine.navigation_at(_string(arguments, "source_id"))
            hits = await reader.read(
                _optional_integer(arguments, "start"),
                _optional_integer(arguments, "end"),
                top_k=config.page_read_top_k,
            )
            return hits, None if hits else "no chunks in that range"
    except (KeyError, ValueError, TypeError) as error:
        return [], f"{invocation.name} failed: {error}"
    return [], f"no tool named {invocation.name!r}"


def _result_chars(tool: str, config: AnswerConfig) -> int:
    return config.tool_result_chars if tool == "search" else config.open_result_chars


def _collect(collected: dict[str, Hit], hits: list[Hit]) -> list[Hit]:
    """Keep the chunks that are new, and return only those."""
    fresh = [hit for hit in hits if hit.chunk_id not in collected]
    for hit in fresh:
        collected[hit.chunk_id] = hit
    return fresh


def _render(hits: list[Hit], limit: int) -> str:
    """A tool result: enough to judge relevance, not the whole chunk."""
    if not hits:
        return "No new chunks."
    blocks = []
    for hit in hits:
        body = " ".join(hit.content.split())
        if len(body) > limit:
            body = f"{body[:limit]}..."
        blocks.append(
            f"chunk_id={hit.chunk_id} source_id={hit.source_id} "
            f"offsets={hit.start_offset}-{hit.end_offset}\n"
            f"{hit.heading_line}\n{body}"
        )
    return "\n\n".join(blocks)


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


def _integer(arguments: dict[str, Any], key: str, fallback: int) -> int:
    value = arguments.get(key)
    return value if isinstance(value, int) and value > 0 else fallback


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


__all__ = ["MAX_TOOL_TOP_K", "NAME", "TOOLS", "answer"]
