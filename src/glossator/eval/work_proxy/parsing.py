"""A dumped conversation response into answer text, thinking, tool calls and usage."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from glossator.eval.consumer.models import HarnessTokens, ToolCallRecord
from glossator.eval.consumer.tools import NAMESPACED_TOOLS
from glossator.eval.consumer.transcript import text_blocks, tool_call_record
from glossator.eval.work_proxy.models import ParsedConversation, ParsedToolExecution


def strip_connector_prefix(name: str) -> str:
    """The tool name as this server spells it, without the Connector's token.

    The Conversations API prefixes a Connector's tools with the Connector's
    live name -- ``mistral_docs_ca30_mistral_docs_search`` -- and that name is
    not the id we address the Connector by, so the strip recognises the server
    tool suffix instead of any one prefix.
    """
    for tool in NAMESPACED_TOOLS:
        for separator in ("__", "_", "-"):
            if name == tool or name.endswith(separator + tool):
                return tool
    return name


def tool_execution_result(entry: Mapping[str, Any]) -> str:
    """What the tool printed, out of the ``info.result`` the API returns.

    The result is MCP content: a list of ``{"type": "text", "text": ...}``
    blocks, read off a live response. Anything else under ``info`` stays
    uninterpreted; the raw entry is kept in ``calls.jsonl`` either way.
    """
    info = entry.get("info")
    if not isinstance(info, Mapping):
        return ""
    result = info.get("result")
    if isinstance(result, str):
        return result
    if isinstance(result, list):
        return text_blocks(result)
    return ""


def _tool_failed(info: Mapping[str, Any]) -> bool:
    status = info.get("status")
    return bool(info.get("error")) or status in ("failed", "error")


def _parse_tool_execution(entry: Mapping[str, Any]) -> ParsedToolExecution:
    arguments = entry.get("arguments")
    raw_info: Any = entry.get("info")
    info: Mapping[str, Any] = raw_info if isinstance(raw_info, dict) else {}
    return ParsedToolExecution(
        name=strip_connector_prefix(str(entry.get("name", "unknown"))),
        arguments=arguments if isinstance(arguments, str) else json.dumps(arguments),
        result=tool_execution_result(entry),
        failed=_tool_failed(info),
    )


def _thinking_text(chunk: Mapping[str, Any]) -> list[str]:
    """A thinking chunk holds a list of text chunks: the reasoning is nested."""
    pieces = chunk.get("thinking")
    if not isinstance(pieces, list):
        return []
    return [piece["text"] for piece in pieces if isinstance(piece, Mapping) and "text" in piece]


def _parse_message_output(entry: Mapping[str, Any], parsed: ParsedConversation) -> None:
    content = entry.get("content")
    if isinstance(content, str):
        if content.strip():
            parsed.answer_text = (parsed.answer_text + "\n" + content).strip()
        return
    if not isinstance(content, list):
        return
    for chunk in content:
        if not isinstance(chunk, Mapping):
            continue
        kind = chunk.get("type")
        if kind == "thinking":
            parsed.thinking.extend(_thinking_text(chunk))
        elif kind == "text" and isinstance(chunk.get("text"), str) and chunk["text"].strip():
            parsed.answer_text = (parsed.answer_text + "\n" + chunk["text"]).strip()


def parse_conversation_response(response: Mapping[str, Any]) -> ParsedConversation:
    """A dumped ``ConversationResponse`` into answer, thinking, calls and usage."""
    parsed = ParsedConversation()
    outputs = response.get("outputs")
    for entry in outputs if isinstance(outputs, list) else []:
        if not isinstance(entry, Mapping):
            continue
        if entry.get("type") == "tool.execution":
            parsed.calls.append(_parse_tool_execution(entry))
        elif entry.get("type") == "message.output":
            _parse_message_output(entry, parsed)
    raw_usage: Any = response.get("usage")
    usage: Mapping[str, Any] = raw_usage if isinstance(raw_usage, dict) else {}
    # Connector tokens are billed like input tokens: the Conversations API
    # counts them beside prompt_tokens, and a record's input is what the run
    # pays for, so they join the input side rather than hiding in raw_usage.
    parsed.usage = HarnessTokens(
        input_tokens=int(usage.get("prompt_tokens", 0) or 0)
        + int(usage.get("connector_tokens", 0) or 0),
        output_tokens=int(usage.get("completion_tokens", 0) or 0),
    )
    parsed.raw_usage = dict(usage)
    return parsed


def connector_call_count(parsed: ParsedConversation) -> int:
    """How many times the conversation called its Connector, from the usage's
    per-connector call-count map."""
    connectors = parsed.raw_usage.get("connectors")
    if not isinstance(connectors, Mapping):
        return 0
    return sum(int(count) for count in connectors.values() if isinstance(count, int))


def tool_call_records(calls: Sequence[ParsedToolExecution]) -> list[ToolCallRecord]:
    """Tool executions as consumer records, with the consumer's own shaping of
    arguments, errors and notes."""

    def arguments_of(call: ParsedToolExecution) -> dict[str, Any] | str:
        try:
            loaded = json.loads(call.arguments) if call.arguments.strip() else {}
        except ValueError:
            return call.arguments
        return loaded if isinstance(loaded, dict) else call.arguments

    return [
        tool_call_record(call.name, arguments_of(call), call.result, call.failed) for call in calls
    ]
