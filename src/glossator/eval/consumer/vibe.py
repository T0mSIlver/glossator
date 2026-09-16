"""Headless Mistral Vibe: its per-cell home, its command and its event stream.

Each cell gets its own ``VIBE_HOME``, so the arm alone decides the tools, the
system prompt and the MCP server; nothing from the user's own Vibe setup
reaches the consumer. The shell tool runs through ``$SHELL``, which points at
the sandbox wrapper.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from glossator.eval.consumer.consumers import ConsumerSpec
from glossator.eval.consumer.models import HarnessTokens, ToolCallRecord
from glossator.eval.consumer.transcript import json_events, tool_call_record
from glossator.eval.consumer.vibe_arms import VibeArm

VIBE_MCP_NAME = "mistral_docs"
"""Vibe prefixes every MCP tool with the server's name: `mistral_docs_mistral_docs_search`."""

SYSTEM_PROMPT_ID = "glossator-arm"

MAX_TURNS = 40
MAX_PRICE_USD = 2.0


def _toml_string(value: str) -> str:
    return json.dumps(value)


def write_vibe_home(
    home: Path, spec: ConsumerSpec, arm: VibeArm, *, mcp_url: str | None, token_env: str
) -> None:
    """The cell's Vibe home: config, the arm's system prompt, nothing else."""
    (home / "prompts").mkdir(parents=True, exist_ok=True)
    (home / "prompts" / f"{SYSTEM_PROMPT_ID}.md").write_text(arm.system_prompt())
    tools: list[str] = []
    if arm.shell:
        tools.append("bash")
    if arm.mcp:
        tools.append(f"{VIBE_MCP_NAME}_*")
    lines = [
        f"active_model = {_toml_string(spec.model)}",
        f"enabled_tools = [{', '.join(_toml_string(tool) for tool in tools)}]",
        f"system_prompt_id = {_toml_string(SYSTEM_PROMPT_ID)}",
        "include_project_context = false",
        "include_prompt_detail = false",
        "include_model_info = false",
        "enable_telemetry = false",
        "enable_update_checks = false",
        "enable_auto_update = false",
        "enable_notifications = false",
        "enable_connectors = false",
        "vibe_code_enabled = false",
        "",
        "[experiments]",
        "enable = false",
    ]
    if arm.mcp:
        if mcp_url is None:
            raise ValueError(f"arm {arm.name} needs an MCP URL")
        lines += [
            "",
            "[[mcp_servers]]",
            f"name = {_toml_string(VIBE_MCP_NAME)}",
            'transport = "streamable-http"',
            f"url = {_toml_string(mcp_url)}",
            "tool_timeout_sec = 120",
            "sampling_enabled = false",
            "",
            "[mcp_servers.auth]",
            'type = "static"',
            f"api_key_env = {_toml_string(token_env)}",
        ]
    (home / "config.toml").write_text("\n".join(lines) + "\n")


def vibe_command(prompt: str, workdir: Path) -> list[str]:
    return [
        "vibe",
        "--legacy-harness",
        "-p",
        prompt,
        "--output",
        "streaming",
        "--auto-approve",
        "--trust",
        "--workdir",
        str(workdir),
        "--max-turns",
        str(MAX_TURNS),
        "--max-price",
        str(MAX_PRICE_USD),
    ]


def _text_of(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            str(block.get("text", ""))
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return ""


def parse_vibe_events(lines: Sequence[str]) -> tuple[str, list[ToolCallRecord]]:
    """The final assistant message and every tool call from a streaming run.

    Vibe emits one entry per message: ``message`` entries carry text by role,
    ``effect`` entries carry a tool call with its input and printed output. An
    assistant message written before more tool calls is narration, so the
    answer is the last assistant message.
    """
    answer = ""
    calls: list[ToolCallRecord] = []
    for event in json_events(lines):
        kind = event.get("type")
        if kind == "message" and event.get("role") == "assistant":
            text = _text_of(event.get("content")).strip()
            if text:
                answer = text
        elif kind == "effect":
            raw_detail = event.get("detail")
            raw_state = event.get("state")
            detail: dict[str, Any] = raw_detail if isinstance(raw_detail, dict) else {}
            state: dict[str, Any] = raw_state if isinstance(raw_state, dict) else {}
            name = str(detail.get("toolName") or event.get("title") or "unknown")
            output = state.get("outputText")
            status = state.get("status")
            calls.append(
                tool_call_record(
                    name,
                    detail.get("input"),
                    output if isinstance(output, str) else "",
                    failed=status not in (None, "completed"),
                )
            )
    return answer, calls


def parse_vibe_session(home: Path) -> tuple[HarnessTokens, float, str | None]:
    """Tokens and cost from the session log Vibe writes under its home."""
    metas = sorted((home / "logs" / "session").glob("*/meta.json"))
    if not metas:
        return HarnessTokens(), 0.0, "vibe wrote no session log"
    prompt = completion = 0
    cost = 0.0
    for meta_path in metas:
        stats = json.loads(meta_path.read_text()).get("stats") or {}
        prompt += int(stats.get("session_prompt_tokens", 0) or 0)
        completion += int(stats.get("session_completion_tokens", 0) or 0)
        cost += float(stats.get("session_cost", 0.0) or 0.0)
    return HarnessTokens(input_tokens=prompt, output_tokens=completion), cost, None
