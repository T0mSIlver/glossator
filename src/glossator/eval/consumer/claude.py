"""Headless claude: its command, its MCP config and its event stream."""

from __future__ import annotations

import contextlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from glossator.eval.consumer.consumers import ConsumerSpec
from glossator.eval.consumer.models import HarnessTokens, ToolCallRecord
from glossator.eval.consumer.tools import MCP_SERVER_NAME
from glossator.eval.consumer.transcript import json_events, tool_call_record, tool_output_text


def _content_blocks(event: Mapping[str, Any]) -> list[dict[str, Any]]:
    """The content blocks of one claude ``assistant`` or ``user`` event."""
    message = event.get("message")
    if not isinstance(message, dict):
        return []
    content = message.get("content")
    if not isinstance(content, list):
        return []
    return [block for block in content if isinstance(block, dict)]


def parse_claude_events(lines: Sequence[str]) -> tuple[str, list[ToolCallRecord]]:
    """Answer text and tool calls from a ``claude -p --output-format stream-json``
    stream.

    Assistant messages carry ``tool_use`` blocks; each tool's output comes back
    later as a ``tool_result`` block inside a user message, keyed by
    ``tool_use_id``, so the two halves are joined on that id. The answer is the
    ``result`` event's text, with the last assistant text as the fallback for a
    run that ended without one.
    """
    calls: list[dict[str, Any]] = []
    at_id: dict[str, int] = {}
    last_text = ""
    answer = ""
    for event in json_events(lines):
        kind = event.get("type")
        if kind == "assistant":
            texts = []
            for block in _content_blocks(event):
                if block.get("type") == "tool_use":
                    at_id[str(block.get("id", ""))] = len(calls)
                    calls.append(
                        {
                            "name": str(block.get("name", "unknown")),
                            "input": block.get("input"),
                            "output": "",
                            "failed": False,
                        }
                    )
                elif block.get("type") == "text" and str(block.get("text", "")).strip():
                    texts.append(str(block["text"]))
            if texts:
                last_text = "\n".join(texts).strip()
        elif kind == "user":
            for block in _content_blocks(event):
                if block.get("type") != "tool_result":
                    continue
                index = at_id.get(str(block.get("tool_use_id", "")))
                if index is None:
                    continue
                calls[index]["output"] = tool_output_text(block.get("content"))
                calls[index]["failed"] = bool(block.get("is_error"))
        elif kind == "result" and isinstance(event.get("result"), str):
            answer = event["result"].strip()
    records = [
        tool_call_record(
            str(call["name"]), call["input"], str(call["output"]), bool(call["failed"])
        )
        for call in calls
    ]
    return answer or last_text, records


def parse_claude_tokens(lines: Sequence[str]) -> tuple[HarnessTokens, float]:
    """Billed tokens and cost from the run's ``result`` event.

    Cached prompt tokens are prompt tokens: the input count is the sum of fresh,
    cache-write and cache-read input, so a cell's total is comparable with a
    harness that caches nothing.
    """
    tokens = HarnessTokens()
    cost = 0.0
    for event in json_events(lines):
        if event.get("type") != "result":
            continue
        usage = event.get("usage")
        if isinstance(usage, dict):
            details = usage.get("output_tokens_details")
            tokens = HarnessTokens(
                input_tokens=sum(
                    int(usage.get(field, 0) or 0)
                    for field in (
                        "input_tokens",
                        "cache_creation_input_tokens",
                        "cache_read_input_tokens",
                    )
                ),
                output_tokens=int(usage.get("output_tokens", 0) or 0),
                reasoning_tokens=int(
                    (details.get("thinking_tokens", 0) or 0) if isinstance(details, dict) else 0
                ),
            )
        with contextlib.suppress(TypeError, ValueError):
            cost = float(event.get("total_cost_usd", 0.0) or 0.0)
    return tokens, cost


def claude_failure(lines: Sequence[str]) -> str | None:
    """The failure a claude stream reports, or None when the turn succeeded."""
    for event in json_events(lines):
        if event.get("type") != "result":
            continue
        if event.get("subtype") == "success" and not event.get("is_error"):
            return None
        detail = event.get("result") if isinstance(event.get("result"), str) else ""
        return f"{event.get('subtype', 'error')}: {detail}"[:400]
    return "the harness wrote no result event"


def claude_command(spec: ConsumerSpec, prompt: str, mcp_config: Path) -> list[str]:
    """Headless claude, prompt as an argument and stdin closed.

    ``--setting-sources ""`` keeps the machine's own settings, hooks and skills
    out of the consumer, so the agent under test is the stock harness on the
    named model. ``--permission-mode bypassPermissions`` is what makes the run
    headless at all: with the default mode nobody answers a permission prompt
    in print mode and every call that would ask is denied.
    """
    command = [
        "claude",
        "-p",
        prompt,
        "--model",
        spec.model,
        "--output-format",
        "stream-json",
        "--verbose",
        "--setting-sources",
        "",
        "--permission-mode",
        "bypassPermissions",
        "--mcp-config",
        str(mcp_config),
        "--strict-mcp-config",
    ]
    if spec.variant is not None:
        command += ["--effort", spec.variant]
    return command


def write_claude_mcp_config(workdir: Path, mcp_url: str | None, token: str) -> Path:
    """The cell's MCP config file, empty in the arm that has no server.

    An empty ``mcpServers`` object with ``--strict-mcp-config`` is how A0 is
    guaranteed no MCP server at all: no file on the machine can add one back.
    """
    servers: dict[str, Any] = {}
    if mcp_url is not None:
        servers[MCP_SERVER_NAME] = {
            "type": "http",
            "url": mcp_url,
            "headers": {"Authorization": f"Bearer {token}"},
        }
    path = workdir / "mcp.json"
    path.write_text(json.dumps({"mcpServers": servers}, indent=2) + "\n")
    return path
