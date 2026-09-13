"""Headless opencode: its command, its MCP config and its event stream."""

from __future__ import annotations

import contextlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from glossator.eval.consumer.consumers import ConsumerSpec
from glossator.eval.consumer.models import HarnessTokens, ToolCallRecord
from glossator.eval.consumer.tools import MCP_SERVER_NAME
from glossator.eval.consumer.transcript import tool_call_record


def parse_opencode_events(lines: Sequence[str]) -> tuple[str, list[ToolCallRecord]]:
    """Answer text, tool calls, and harness tokens from an opencode JSON stream.

    The stream is one JSON object per line: ``text`` parts carry the answer,
    ``tool_use`` parts carry each call's input and printed output, and
    ``step_finish`` parts carry the billed tokens.
    """
    texts: list[str] = []
    calls: list[ToolCallRecord] = []
    for line in lines:
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        part = event.get("part")
        if not isinstance(part, dict):
            continue
        kind = event.get("type")
        if kind == "text" and isinstance(part.get("text"), str) and part["text"].strip():
            texts.append(part["text"])
        elif kind == "tool_use" and part.get("type") == "tool":
            calls.append(_parse_tool_part(part))
    return "\n".join(texts).strip(), calls


def _parse_tool_part(part: Mapping[str, Any]) -> ToolCallRecord:
    """One opencode ``tool`` part: the call's input and what it printed."""
    name = str(part.get("tool", "unknown"))
    raw_state = part.get("state")
    state: dict[str, Any] = raw_state if isinstance(raw_state, dict) else {}
    output = state.get("output")
    record = tool_call_record(
        name, state.get("input"), output if isinstance(output, str) else "", failed=False
    )
    status = state.get("status")
    if not isinstance(output, str) and status not in (None, "completed"):
        # A call the harness abandoned prints nothing, so its failure is only
        # readable in the status.
        return record.model_copy(update={"error": f"tool status: {status}"})
    return record


def parse_opencode_tokens(lines: Sequence[str]) -> tuple[HarnessTokens, float]:
    """Summed step-finish tokens and cost across the whole stream."""
    prompt = completion = reasoning = 0
    cost = 0.0
    for line in lines:
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue
        part = event.get("part") if isinstance(event, dict) else None
        if not isinstance(part, dict) or event.get("type") != "step_finish":
            continue
        tokens = part.get("tokens")
        if isinstance(tokens, dict):
            prompt += int(tokens.get("input", 0) or 0)
            completion += int(tokens.get("output", 0) or 0)
            reasoning += int(tokens.get("reasoning", 0) or 0)
        with contextlib.suppress(TypeError, ValueError):
            cost += float(part.get("cost", 0.0) or 0.0)
    return HarnessTokens(
        input_tokens=prompt, output_tokens=completion, reasoning_tokens=reasoning
    ), cost


def opencode_command(spec: ConsumerSpec, prompt: str, workdir: Path) -> list[str]:
    """Headless opencode over the scratch directory's own opencode.json."""
    command = [
        "opencode",
        "run",
        "-m",
        spec.model,
        "--format",
        "json",
        "--dir",
        str(workdir),
        prompt,
    ]
    if spec.variant is not None:
        command.extend(["--variant", spec.variant])
    return command


def write_opencode_config(workdir: Path, mcp_url: str, token: str) -> None:
    """The scratch directory's own MCP declaration. ``oauth: false`` stops the
    client from starting an OAuth flow against a bearer-token server."""
    config = {
        "mcp": {
            MCP_SERVER_NAME: {
                "type": "remote",
                "url": mcp_url,
                "headers": {"Authorization": f"Bearer {token}"},
                "oauth": False,
            }
        }
    }
    (workdir / "opencode.json").write_text(json.dumps(config, indent=2) + "\n")
