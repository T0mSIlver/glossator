"""Headless codex: its command and its event stream."""

from __future__ import annotations

import contextlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from glossator.eval.consumer.consumers import ConsumerSpec
from glossator.eval.consumer.models import HarnessTokens, ToolCallRecord
from glossator.eval.consumer.tools import MCP_SERVER_NAME, TOKEN_ENV_VAR
from glossator.eval.consumer.transcript import json_events, tool_call_record, tool_output_text


def _codex_item(event: Mapping[str, Any]) -> tuple[str, dict[str, Any]] | None:
    """One codex thread item and its kind, out of an ``item.*`` event."""
    item = event.get("item")
    if not isinstance(item, dict):
        return None
    kind = item.get("item_type") or item.get("type") or ""
    return str(kind), item


def parse_codex_events(lines: Sequence[str]) -> tuple[str, list[ToolCallRecord]]:
    """Answer text and tool calls from a ``codex exec --json`` stream.

    The stream is a sequence of thread items: ``mcp_tool_call`` items carry the
    server, the tool, its arguments and its result; the last ``agent_message``
    item is the answer. Items are announced when they start and again when they
    complete, so each is kept once, under its id, and overwritten by its
    completion. The consumer's own shell and web items are kept too, so a tool
    call counts the same here as it does under the other harnesses.
    """
    texts: list[str] = []
    calls: dict[str, ToolCallRecord] = {}
    for event in json_events(lines):
        if not str(event.get("type", "")).startswith("item."):
            continue
        parsed = _codex_item(event)
        if parsed is None:
            continue
        kind, item = parsed
        item_id = str(item.get("id", len(calls)))
        if kind == "agent_message":
            text = item.get("text")
            if isinstance(text, str) and text.strip():
                texts = [text.strip()]
        elif kind == "mcp_tool_call":
            calls[item_id] = _codex_tool_call(item)
        elif kind in CODEX_TOOL_ITEMS:
            calls[item_id] = _codex_own_tool(kind, item)
    return "\n".join(texts).strip(), list(calls.values())


CODEX_TOOL_ITEMS = ("command_execution", "web_search", "file_change")
"""Codex items that are the consumer's own tools rather than this server's."""

_CODEX_OUTPUT_KEYS = ("aggregated_output", "output", "result", "text")
_CODEX_META_KEYS = ("id", "item_type", "type", "status", "error", *_CODEX_OUTPUT_KEYS)


def _codex_own_tool(kind: str, item: Mapping[str, Any]) -> ToolCallRecord:
    """One of the consumer's own tools: a shell command, a web search, an edit."""
    output = next(
        (str(item[key]) for key in _CODEX_OUTPUT_KEYS if isinstance(item.get(key), str)), ""
    )
    arguments = {key: value for key, value in item.items() if key not in _CODEX_META_KEYS}
    failed = str(item.get("status", "")) in ("failed", "errored") or bool(item.get("error"))
    return tool_call_record(kind, arguments, output, failed)


def _codex_tool_call(item: Mapping[str, Any]) -> ToolCallRecord:
    """One ``mcp_tool_call`` item. The name a consumer sees is the server's own
    name and the tool's, which is how codex prefixes them."""
    tool = str(item.get("tool") or item.get("name") or "unknown")
    server = str(item.get("server") or "")
    name = f"{server}__{tool}" if server and not tool.startswith(server) else tool
    arguments = item.get("arguments")
    if isinstance(arguments, str):
        with contextlib.suppress(ValueError):
            arguments = json.loads(arguments)
    status = str(item.get("status", ""))
    failed = status in ("failed", "errored", "error") or bool(item.get("error"))
    result = item.get("result")
    # A call codex refused has no result at all, and the reason it gives is the
    # only thing the row can carry.
    output = tool_output_text(result) if result is not None else _codex_error_text(item)
    return tool_call_record(name, arguments, output, failed)


def _codex_error_text(item: Mapping[str, Any]) -> str:
    error = item.get("error")
    if isinstance(error, Mapping):
        return str(error.get("message", ""))
    return str(error or "")


def parse_codex_tokens(lines: Sequence[str]) -> tuple[HarnessTokens, float]:
    """Billed tokens from the ``turn.completed`` usage. Codex reports no price,
    so the cost stays zero and the token counts carry the comparison."""
    tokens = HarnessTokens()
    for event in json_events(lines):
        usage = event.get("usage")
        if not isinstance(usage, dict):
            continue
        tokens = HarnessTokens(
            input_tokens=int(usage.get("input_tokens", 0) or 0)
            + int(usage.get("cached_input_tokens", 0) or 0)
            + int(usage.get("cache_write_input_tokens", 0) or 0),
            output_tokens=int(usage.get("output_tokens", 0) or 0),
            reasoning_tokens=int(usage.get("reasoning_output_tokens", 0) or 0),
        )
    return tokens, 0.0


def codex_failure(lines: Sequence[str]) -> str | None:
    """The failure a codex stream reports, or None when the turn completed."""
    failure: str | None = None
    for event in json_events(lines):
        kind = event.get("type")
        if kind == "turn.completed":
            return None
        if kind in ("error", "turn.failed"):
            error = event.get("error")
            message = error.get("message") if isinstance(error, dict) else event.get("message")
            failure = str(message or kind)[:400]
    return failure


def codex_command(
    spec: ConsumerSpec, answer_path: Path, mcp_url: str | None, *, token_env: str = TOKEN_ENV_VAR
) -> list[str]:
    """Headless codex, prompt on stdin.

    The MCP keys are the ones ``codex mcp add --url ... --bearer-token-env-var
    ...`` writes into ``config.toml``: ``mcp_servers.<name>.url`` and
    ``mcp_servers.<name>.bearer_token_env_var``. The token itself never reaches
    the command line; codex reads it from the environment.
    ``--ignore-user-config`` keeps the machine's own servers, plugins and hooks
    out of the consumer, so the arm decides the tool surface and nothing else.
    """
    command = ["codex", "exec", "--skip-git-repo-check", "--ignore-user-config", "-m", spec.model]
    if spec.variant is not None:
        # The value is TOML, and there is no shell here to strip the quotes a
        # shell command line would carry: the effort has to arrive as the TOML
        # string "low", not as the six characters '"low"'.
        command += ["-c", f'model_reasoning_effort="{spec.variant}"']
    if mcp_url is not None:
        command += [
            "-c",
            f"mcp_servers.{MCP_SERVER_NAME}.url={mcp_url}",
            "-c",
            f"mcp_servers.{MCP_SERVER_NAME}.bearer_token_env_var={token_env}",
        ]
    return command + ["--json", "-o", str(answer_path), "-"]
