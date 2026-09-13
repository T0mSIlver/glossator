"""Tool calls out of a harness event stream, shared by the three harness parsers."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from typing import Any

from glossator.eval.consumer.models import ToolCallRecord
from glossator.eval.consumer.tools import is_verify_tool

_CITE_VERIFIED = re.compile(r"^\[(\d+)\] verified:", re.MULTILINE)
"""The per-quote verdict line recorded runs carry; it is one count line now."""

_CITE_COUNT = re.compile(r"^verified: \d+ of \d+ quotes?(?: \(([^)]*)\))?", re.MULTILINE)
_CITE_REJECTED = re.compile(r"^\[(\d+)\] NOT verified:", re.MULTILINE)
_MARKER = re.compile(r"\[(\d+)\]")


def json_events(lines: Sequence[str]) -> list[dict[str, Any]]:
    """The JSON objects of an event stream, skipping anything unparsable.

    Every harness writes one JSON object per line and every harness also writes
    the occasional banner or warning to the same stream, so a line that does
    not parse is dropped rather than failing the cell.
    """
    events: list[dict[str, Any]] = []
    for line in lines:
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict):
            events.append(event)
    return events


def _short(value: Any) -> str:
    text = value if isinstance(value, str) else json.dumps(value, sort_keys=True)
    return text if len(text) <= 500 else text[:500] + "…[truncated]"


def _tool_error(name: str, output: str) -> str | None:
    for line in output.splitlines():
        if line.startswith("error:"):
            return f"{name}: {line.strip()}"
    return None


def _verdicts(output: str) -> dict[str, bool]:
    """Which markers the quote checker held, over either output format.

    Today's check prints one count line naming the markers that verified;
    recorded runs print one verdict line per quote. Both are read, so a run
    collected before the change still counts.
    """
    verdicts = {match.group(1): True for match in _CITE_VERIFIED.finditer(output)}
    for match in _CITE_COUNT.finditer(output):
        verdicts.update({n: True for n in _MARKER.findall(match.group(1) or "")})
    verdicts.update({match.group(1): False for match in _CITE_REJECTED.finditer(output)})
    return verdicts


def _tool_notes(output: str) -> list[str]:
    """The `note:` lines a tool printed, clamps among them (D-029)."""
    return [line.strip() for line in output.splitlines() if line.startswith("note:")]


def tool_output_text(content: Any) -> str:
    """What the tool printed, out of a harness's wrapping of the result.

    Each harness wraps a tool result its own way: claude passes the JSON object
    ``{"result": "<printed output>"}`` as a string, codex passes the MCP result
    with its ``content`` blocks and its ``structured_content``, and a built-in
    tool passes plain text or a list of blocks. The printed output is what
    carries this server's ``error:`` and ``note:`` lines, so it is unwrapped
    before either is looked for.
    """
    payload: Any = content
    if isinstance(content, str):
        try:
            payload = json.loads(content)
        except ValueError:
            return content
    if isinstance(payload, dict):
        blocks = payload.get("content")
        if isinstance(blocks, list):
            return text_blocks(blocks)
        structured = payload.get("structured_content")
        if isinstance(structured, dict) and isinstance(structured.get("result"), str):
            return str(structured["result"])
        if isinstance(payload.get("result"), str):
            return str(payload["result"])
    if isinstance(payload, list):
        return text_blocks(payload)
    if isinstance(payload, str):
        return payload
    return json.dumps(payload, sort_keys=True)


def text_blocks(blocks: Sequence[Any]) -> str:
    return "\n".join(
        str(block.get("text"))
        if isinstance(block, dict) and isinstance(block.get("text"), str)
        else json.dumps(block, sort_keys=True)
        for block in blocks
    )


def tool_call_record(name: str, arguments: Any, output: str, failed: bool) -> ToolCallRecord:
    """One tool call, however the harness spelled the call and its result."""
    recorded: dict[str, str] = {}
    if isinstance(arguments, Mapping):
        for key, value in arguments.items():
            # The cite quotes are the judge's evidence; truncating them would
            # corrupt the JSON the judge reads back.
            if is_verify_tool(name) and key == "quotes":
                recorded[key] = (
                    value if isinstance(value, str) else json.dumps(value, sort_keys=True)
                )
            else:
                recorded[key] = _short(value)
    elif arguments not in (None, ""):
        recorded["input"] = _short(arguments)
    error = _tool_error(name, output)
    if error is None and failed:
        error = f"{name}: {output.strip().splitlines()[0] if output.strip() else 'failed'}"
    if is_verify_tool(name) and output:
        # Which quotes the server verified, so the judge and the metrics can
        # count them without re-reading the transcript.
        recorded["__verdicts"] = json.dumps(_verdicts(output), sort_keys=True)
    return ToolCallRecord(
        name=name,
        arguments=recorded,
        output_chars=len(output),
        error=error,
        notes=_tool_notes(output),
    )
