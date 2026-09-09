"""Blind consumer evaluation: weak models answer documentation questions over MCP.

An ordinary agent, on a weak model at low reasoning, that is not told it is
being evaluated, answers Mistral documentation questions while connected to
glossator's MCP server over the same HTTP transport the Work Connector uses.
Three tool surfaces (arms) are compared:

- **A0, no tools**: the consumer answers from memory. The floor.
- **A1, retrieval tools plus ``cite``**: search, open, navigate, read, grep, cite.
- **A2, ``ask`` only**: the server writes the answer.

Every consumer runs from a scratch directory outside the repository with no
repository files visible, so it cannot read the corpus from disk. Shell tools
stay available in every arm: the comparison is between whole agents.

Subcommands (``run`` collects answers, ``judge`` grades them, ``score``
reports) are resumable independently: ``run`` skips (consumer, arm, question)
cells that already have a record, and ``judge`` skips rows the requested judge
already graded. The judge step is a separate subcommand on purpose: when the
judge provider's quota window is exhausted, collection still proceeds.
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import json
import math
import os
import random
import re
import shutil
import statistics
import subprocess
import time
import urllib.parse
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlsplit

import httpx
import structlog
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict

from glossator.eval.answer_eval import (
    CORRECTNESS_SCORE,
    JUDGE_MAX_TOKENS,
    JUDGE_PROMPT_HASHES,
    JUDGE_SYSTEM,
    JUDGE_TEMPERATURE,
    JUDGE_VERSION,
    JudgedCitation,
    JudgeInput,
    JudgeModel,
    JudgeRecord,
    JudgeVerdict,
    parse_judge_models,
    wait_for_quota,
)
from glossator.eval.charts import bar_chart
from glossator.eval.datasets import EvalQuestion, read_jsonl, stratified_subset
from glossator.eval.fragments import PageCache, visible_text
from glossator.eval.providers import (
    OpenAICompatibleProvider,
    ProviderCallError,
    call_scope,
    candidate_scope,
)

logger = structlog.get_logger(__name__)

RUNS_ROOT = Path("eval/runs")
MINED_DATASET = Path("eval/mined.jsonl")
FRESH_DATASET = Path("eval/dev-fresh60.jsonl")
DEFAULT_CORPUS = Path("corpus/mistral-docs")

PROMPT_LEAD = (
    "You are helping a developer with Mistral's platform. "
    "Answer precisely and cite the documentation pages you used with links."
)
"""The one fixed sentence before every question. Nothing says evaluation,
nothing names the tools; the MCP server's own instructions are the only
guidance in A1 and A2."""

ARMS = ("A0", "A1", "A2")

ARM_TOOLS: dict[str, str | None] = {
    "A0": None,
    "A1": (
        "mistral_docs_search,mistral_docs_open_section,mistral_docs_step,"
        "mistral_docs_read_page,mistral_docs_find_on_page,mistral_docs_verify_quotes"
    ),
    "A2": "mistral_docs_answer",
}
"""The GLOSSATOR_MCP_TOOLS allowlist each arm's server runs. A0 never sees an
MCP server at all; A1 and A2 talk to servers started with these allowlists."""

TOOL_SUFFIXES = (
    "mistral_docs_search",
    "mistral_docs_open_section",
    "mistral_docs_step",
    "mistral_docs_read_page",
    "mistral_docs_find_on_page",
    "mistral_docs_answer",
    "mistral_docs_verify_quotes",
    "mistral_docs_history",
    # The names the tools had before they were namespaced, so recorded runs
    # keep reading the way they did when they were collected.
    "search",
    "open",
    "navigate",
    "read",
    "grep",
    "ask",
    "cite",
    "history",
)
"""Every tool name this server has ever served. A harness prefixes them its own
way -- `glossator_search`, `mcp__mistral-docs__mistral_docs_search` -- so the
match is on the suffix, longest first."""

VERIFY_SUFFIXES = ("mistral_docs_verify_quotes", "cite")
"""The quote checker, under either name."""


def is_server_tool(name: str) -> bool:
    """Whether one harness tool name is one of this server's tools."""
    return any(name.endswith(suffix) for suffix in TOOL_SUFFIXES)


def is_verify_tool(name: str) -> bool:
    """Whether one harness tool name is the quote checker."""
    return any(name.endswith(suffix) for suffix in VERIFY_SUFFIXES)


MAX_PARALLEL = 2
"""At most two headless harness processes at once: opencode hangs at a third."""

QUESTION_TIMEOUT_S = 600.0

QUOTA_HINTS = ("quota", "rate limit", "rate_limit", "usage limit", "429", "limit reached")
"""Substrings marking a harness failure as an exhausted provider window rather
than a broken question. Quota errors become error rows, not a crashed run."""

REFUSAL_PATTERNS = (
    r"documentation (does not|doesn't|do not|don't) (say|state|mention|cover|document|specify)",
    r"no(t| (such| record of| information| mention of)) .* in the documentation",
    r"(could|cannot|can't|could not) find .* in the documentation",
    r"not (covered|documented|stated|mentioned|specified) (in|by) the",
    r"(i |we |this server |the index )?(do not|don't|does not|doesn't) have .*documentation",
    r"unable to (find|locate|answer)",
    r"(decline|refuse) to answer",
    r"no evidence",
)
_REFUSAL = re.compile("|".join(REFUSAL_PATTERNS), re.IGNORECASE)

_URL = re.compile(r"https?://[^\s)>\]\"']+")
_CITE_VERIFIED = re.compile(r"^\[(\d+)\] verified:", re.MULTILINE)
"""The per-quote verdict line recorded runs carry; it is one count line now."""

_CITE_COUNT = re.compile(r"^verified: \d+ of \d+ quotes?(?: \(([^)]*)\))?", re.MULTILINE)
_CITE_REJECTED = re.compile(r"^\[(\d+)\] NOT verified:", re.MULTILINE)
_MARKER = re.compile(r"\[(\d+)\]")
_BAD_PARAM = "error: E_BAD_PARAM"
_CLAMP = "clamped server-side"


# --------------------------------------------------------------------------- #
# Consumers
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class ConsumerSpec:
    """One weak consumer: harness, model, and low-reasoning setting."""

    name: str
    harness: Literal["opencode", "codex", "claude"]
    model: str
    variant: str | None = None
    """The reasoning effort, named the way the harness names it: opencode's
    ``--variant``, claude's ``--effort``, codex's ``model_reasoning_effort``.
    None means the harness default; weak consumers always name the lowest."""


CONSUMERS: tuple[ConsumerSpec, ...] = (
    ConsumerSpec(
        name="opencode-muse-minimal",
        harness="opencode",
        model="opencode/muse-spark-1.3-contributor-free",
        variant="minimal",
    ),
    ConsumerSpec(
        name="opencode-glm-flash-low",
        harness="opencode",
        model="zai-coding-plan/glm-5.3-flash",
        variant="low",
    ),
    ConsumerSpec(
        name="codex-gpt-luna-low",
        harness="codex",
        model="gpt-5.6-luna",
        variant="low",
    ),
    ConsumerSpec(
        name="claude-sonnet-low",
        harness="claude",
        model="sonnet",
        variant="low",
    ),
)
"""Every weak consumer. The muse consumer is first: it is the contributor-free
model with quota while the z.ai window and the codex quota are exhausted."""

CONSUMER_NAMES = tuple(spec.name for spec in CONSUMERS)


def consumer_spec(name: str) -> ConsumerSpec:
    for spec in CONSUMERS:
        if spec.name == name:
            return spec
    raise SystemExit(f"unknown consumer {name!r}; available: {list(CONSUMER_NAMES)}")


# --------------------------------------------------------------------------- #
# Records
# --------------------------------------------------------------------------- #


class HarnessTokens(BaseModel):
    model_config = ConfigDict(frozen=True)

    input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0

    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens


class ToolCallRecord(BaseModel):
    """One harness tool call, extracted from the event stream."""

    model_config = ConfigDict(frozen=True)

    name: str
    arguments: dict[str, str] = {}
    output_chars: int = 0
    error: str | None = None
    notes: list[str] = []
    """The `note:` lines the tool printed. A clamp is announced there and never
    as an error (D-029), so counting clamps out of `error` counted none."""


class ConsumerRecord(BaseModel):
    """One (consumer, arm, question) cell: the answer and everything behind it."""

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    consumer: str
    arm: str
    question_id: str
    question_type: str
    question: str
    reference_answer: str
    gold_urls: list[str] = []
    answer_text: str = ""
    wall_seconds: float = 0.0
    tokens: HarnessTokens = HarnessTokens()
    harness_cost_usd: float = 0.0
    tool_calls: list[ToolCallRecord] = []
    mcp_called: bool = False
    cite_called: bool = False
    links: list[str] = []
    transcript: str = ""
    error: str | None = None
    judge: JudgeRecord | None = None

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.consumer, self.arm, self.question_id)


class _CallsRecorder:
    """The provider's CallRecorder, writing judge calls into the run.

    The provider hands over pydantic models (`usage`, `parsed`) and message
    sequences. Falling back to ``str`` for those wrote their Python repr into
    the ledger, so the token counts D-023b exists to make countable were not
    machine-readable; they are dumped as JSON instead.
    """

    def __init__(self, run_dir: Path) -> None:
        self.path = run_dir / "calls.jsonl"

    def record_call(self, **row: Any) -> None:
        serializable: dict[str, Any] = {"timestamp": datetime.now(UTC).isoformat()}
        for key, value in row.items():
            if isinstance(value, BaseModel):
                serializable[key] = value.model_dump(mode="json")
            elif key == "messages":
                serializable[key] = [dict(message) for message in value]
            else:
                serializable[key] = json.loads(json.dumps(value, sort_keys=True, default=str))
        with self.path.open("a") as handle:
            handle.write(json.dumps(serializable, sort_keys=True) + "\n")


# --------------------------------------------------------------------------- #
# Question set
# --------------------------------------------------------------------------- #


MINED_COUNT = 40
FRESH_COUNT = 20


def build_question_set(
    mined_count: int = MINED_COUNT,
    fresh_count: int = FRESH_COUNT,
    mined_path: Path = MINED_DATASET,
    fresh_path: Path = FRESH_DATASET,
) -> list[EvalQuestion]:
    """The fixed question set: ``mined_count`` stratified from mined (seed 0)
    and ``fresh_count`` from the fresh slice (seed 0). Same rows every run, and
    a smaller count is a prefix of a larger one, so a consumer run on thirty
    questions is comparable with one on sixty.

    The full forty keeps all nine mined unanswerables; a smaller draw keeps as
    many as round-robin stratification gives it, and the run's config records
    how many it got."""
    mined = stratified_subset(read_jsonl(mined_path), mined_count, seed=0)
    fresh = stratified_subset(read_jsonl(fresh_path), fresh_count, seed=0)
    unanswerable = [q for q in mined if q.type.value == "unanswerable"]
    if mined_count >= MINED_COUNT and len(unanswerable) != 9:
        raise ValueError(f"expected all 9 mined unanswerables in the 40, found {len(unanswerable)}")
    return mined + fresh


def prompt_for(question: EvalQuestion) -> str:
    return f"{PROMPT_LEAD}\n\n{question.question}"


# --------------------------------------------------------------------------- #
# Harness event parsing
# --------------------------------------------------------------------------- #


def _json_events(lines: Sequence[str]) -> list[dict[str, Any]]:
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
    record = _tool_call_record(
        name, state.get("input"), output if isinstance(output, str) else "", failed=False
    )
    status = state.get("status")
    if not isinstance(output, str) and status not in (None, "completed"):
        # A call the harness abandoned prints nothing, so its failure is only
        # readable in the status.
        return record.model_copy(update={"error": f"tool status: {status}"})
    return record


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


def _content_blocks(event: Mapping[str, Any]) -> list[dict[str, Any]]:
    """The content blocks of one claude ``assistant`` or ``user`` event."""
    message = event.get("message")
    if not isinstance(message, dict):
        return []
    content = message.get("content")
    if not isinstance(content, list):
        return []
    return [block for block in content if isinstance(block, dict)]


def _tool_output_text(content: Any) -> str:
    """What the tool printed, out of a harness's wrapping of the result.

    An MCP result arrives as the JSON object ``{"result": "<printed output>"}``;
    a built-in tool's result arrives as plain text or as a list of blocks. The
    printed output is what carries this server's ``error:`` and ``note:`` lines,
    so it is unwrapped before either is looked for.
    """
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        parts = [
            str(block.get("text"))
            if isinstance(block, dict) and isinstance(block.get("text"), str)
            else json.dumps(block, sort_keys=True)
            for block in content
        ]
        text = "\n".join(parts)
    else:
        text = json.dumps(content, sort_keys=True)
    try:
        payload = json.loads(text)
    except ValueError:
        return text
    if isinstance(payload, dict) and isinstance(payload.get("result"), str):
        return str(payload["result"])
    return text


def _tool_call_record(name: str, arguments: Any, output: str, failed: bool) -> ToolCallRecord:
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
    for event in _json_events(lines):
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
                calls[index]["output"] = _tool_output_text(block.get("content"))
                calls[index]["failed"] = bool(block.get("is_error"))
        elif kind == "result" and isinstance(event.get("result"), str):
            answer = event["result"].strip()
    records = [
        _tool_call_record(
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
    for event in _json_events(lines):
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
    for event in _json_events(lines):
        if event.get("type") != "result":
            continue
        if event.get("subtype") == "success" and not event.get("is_error"):
            return None
        detail = event.get("result") if isinstance(event.get("result"), str) else ""
        return f"{event.get('subtype', 'error')}: {detail}"[:400]
    return "the harness wrote no result event"


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
    for event in _json_events(lines):
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
    return _tool_call_record(kind, arguments, output, failed)


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
    output = _tool_output_text(item.get("result") if item.get("result") is not None else "")
    status = str(item.get("status", ""))
    failed = status in ("failed", "errored", "error") or bool(item.get("error"))
    return _tool_call_record(name, arguments, output, failed)


def parse_codex_tokens(lines: Sequence[str]) -> tuple[HarnessTokens, float]:
    """Billed tokens from the ``turn.completed`` usage. Codex reports no price,
    so the cost stays zero and the token counts carry the comparison."""
    tokens = HarnessTokens()
    for event in _json_events(lines):
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
    for event in _json_events(lines):
        kind = event.get("type")
        if kind == "turn.completed":
            return None
        if kind in ("error", "turn.failed"):
            error = event.get("error")
            message = error.get("message") if isinstance(error, dict) else event.get("message")
            failure = str(message or kind)[:400]
    return failure


def extract_links(answer: str) -> list[str]:
    """Documentation URLs in the answer, in order, deduplicated."""
    seen: list[str] = []
    for match in _URL.finditer(answer):
        url = match.group(0).rstrip(".,;:")
        if url not in seen:
            seen.append(url)
    return seen


def refused(answer: str) -> bool:
    """Whether the answer declines for lack of documentation (heuristic)."""
    return _REFUSAL.search(answer) is not None


def cite_verdicts(calls: Sequence[ToolCallRecord]) -> tuple[int, int]:
    """(verified, rejected) cite quotes, counted from the verdict lines the
    consumer itself saw in each cite output."""
    verified = rejected = 0
    for call in calls:
        if not is_verify_tool(call.name):
            continue
        try:
            verdicts = json.loads(call.arguments.get("__verdicts", "{}"))
        except ValueError:
            continue
        if isinstance(verdicts, dict):
            verified += sum(1 for held in verdicts.values() if held)
            rejected += sum(1 for held in verdicts.values() if not held)
    return verified, rejected


# --------------------------------------------------------------------------- #
# Harness commands
# --------------------------------------------------------------------------- #


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


MCP_SERVER_NAME = "mistral-docs"
"""What the consumer's client calls this server. Harnesses prefix tool names
with it, and the name a consumer reads is the server's own."""

TOKEN_ENV_VAR = "GLOSSATOR_MCP_TOKEN"


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
        command += ["-c", f"model_reasoning_effort='\"{spec.variant}\"'"]
    if mcp_url is not None:
        command += [
            "-c",
            f"mcp_servers.{MCP_SERVER_NAME}.url={mcp_url}",
            "-c",
            f"mcp_servers.{MCP_SERVER_NAME}.bearer_token_env_var={token_env}",
        ]
    return command + ["--json", "-o", str(answer_path), "-"]


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


# --------------------------------------------------------------------------- #
# Collection
# --------------------------------------------------------------------------- #


@dataclass(slots=True)
class CollectedAnswer:
    answer_text: str
    tool_calls: list[ToolCallRecord]
    tokens: HarnessTokens
    cost_usd: float
    wall_seconds: float
    transcript: str
    error: str | None


@dataclass(slots=True)
class _HarnessRun:
    """What one headless harness process left behind."""

    lines: list[str]
    stderr: str
    wall_seconds: float
    timed_out: bool
    events_path: Path


def _run_harness(
    command: Sequence[str],
    cell_dir: Path,
    *,
    timeout_s: float,
    cwd: Path | None = None,
    stdin_path: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> _HarnessRun:
    """One harness process, its event stream and stderr kept in the cell.

    Nothing is ever read from the terminal: stdin is either the prompt file or
    ``/dev/null``, so a harness that would otherwise wait for input exits.
    """
    cell_dir.mkdir(parents=True, exist_ok=True)
    events_path = cell_dir / "events.jsonl"
    stderr_path = cell_dir / "stderr.txt"
    started = time.perf_counter()
    timed_out = False
    with contextlib.ExitStack() as stack:
        events_file = stack.enter_context(events_path.open("w"))
        stderr_file = stack.enter_context(stderr_path.open("w"))
        stdin: Any = subprocess.DEVNULL
        if stdin_path is not None:
            stdin = stack.enter_context(stdin_path.open("rb"))
        try:
            subprocess.run(
                list(command),
                cwd=str(cwd) if cwd is not None else None,
                stdin=stdin,
                stdout=events_file,
                stderr=stderr_file,
                timeout=timeout_s,
                check=False,
                env=dict(env) if env is not None else None,
            )
        except subprocess.TimeoutExpired:
            timed_out = True
    return _HarnessRun(
        lines=events_path.read_text().splitlines() if events_path.is_file() else [],
        stderr=stderr_path.read_text() if stderr_path.is_file() else "",
        wall_seconds=time.perf_counter() - started,
        timed_out=timed_out,
        events_path=events_path,
    )


def _harness_environment(token: str, token_env: str = TOKEN_ENV_VAR) -> dict[str, str]:
    """The consumer's environment: this process's, plus the server token for a
    harness that reads it from a named variable."""
    environment = dict(os.environ)
    if token:
        environment[token_env] = token
    return environment


def _collected(
    run: _HarnessRun,
    answer: str,
    calls: Sequence[ToolCallRecord],
    tokens: HarnessTokens,
    cost: float,
    *,
    timeout_s: float,
    failure: str | None = None,
) -> CollectedAnswer:
    """One cell's answer, with the failure a silent harness leaves in stderr."""
    error = failure
    if run.timed_out:
        error = f"harness timeout after {timeout_s:.0f}s"
    elif not answer and not calls:
        if is_quota_error(run.stderr) or (failure and is_quota_error(failure)):
            detail = (run.stderr.strip() or (failure or ""))[-300:]
            error = f"provider quota exhausted: {detail}"
        elif error is None:
            error = "harness produced no answer text and no tool calls"
    return CollectedAnswer(
        answer_text=answer,
        tool_calls=list(calls),
        tokens=tokens,
        cost_usd=cost,
        wall_seconds=run.wall_seconds,
        transcript=str(run.events_path),
        error=error,
    )


def collect_opencode(
    spec: ConsumerSpec,
    prompt: str,
    cell_dir: Path,
    *,
    mcp_url: str | None,
    token: str,
    timeout_s: float,
) -> CollectedAnswer:
    """One question through headless opencode. Prompt travels as an argv item
    read from the prompt file (no shell), stdin stays /dev/null."""
    cell_dir.mkdir(parents=True, exist_ok=True)
    (cell_dir / "prompt.txt").write_text(prompt + "\n")
    if mcp_url is not None:
        write_opencode_config(cell_dir, mcp_url, token)
    run = _run_harness(opencode_command(spec, prompt, cell_dir), cell_dir, timeout_s=timeout_s)
    answer, calls = parse_opencode_events(run.lines)
    tokens, cost = parse_opencode_tokens(run.lines)
    return _collected(run, answer, calls, tokens, cost, timeout_s=timeout_s)


def collect_claude(
    spec: ConsumerSpec,
    prompt: str,
    cell_dir: Path,
    *,
    mcp_url: str | None,
    token: str,
    timeout_s: float,
) -> CollectedAnswer:
    """One question through headless claude, from the cell's own directory.

    The MCP server is declared in the cell's ``mcp.json`` and nowhere else, so
    the arm decides what the consumer can call.
    """
    cell_dir.mkdir(parents=True, exist_ok=True)
    (cell_dir / "prompt.txt").write_text(prompt + "\n")
    config_path = write_claude_mcp_config(cell_dir, mcp_url, token)
    run = _run_harness(
        claude_command(spec, prompt, config_path),
        cell_dir,
        timeout_s=timeout_s,
        cwd=cell_dir,
        env=_harness_environment(token),
    )
    answer, calls = parse_claude_events(run.lines)
    tokens, cost = parse_claude_tokens(run.lines)
    return _collected(
        run, answer, calls, tokens, cost, timeout_s=timeout_s, failure=claude_failure(run.lines)
    )


def collect_codex(
    spec: ConsumerSpec,
    prompt: str,
    cell_dir: Path,
    *,
    mcp_url: str | None,
    token: str,
    timeout_s: float,
) -> CollectedAnswer:
    """One question through headless codex, prompt piped in on stdin."""
    cell_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = cell_dir / "prompt.md"
    prompt_path.write_text(prompt + "\n")
    answer_path = cell_dir / "answer.md"
    run = _run_harness(
        codex_command(spec, answer_path, mcp_url),
        cell_dir,
        timeout_s=timeout_s,
        cwd=cell_dir,
        stdin_path=prompt_path,
        env=_harness_environment(token),
    )
    answer, calls = parse_codex_events(run.lines)
    tokens, cost = parse_codex_tokens(run.lines)
    if not answer and answer_path.is_file():
        answer = answer_path.read_text().strip()
    return _collected(
        run, answer, calls, tokens, cost, timeout_s=timeout_s, failure=codex_failure(run.lines)
    )


COLLECTORS = {
    "opencode": collect_opencode,
    "claude": collect_claude,
    "codex": collect_codex,
}


def is_quota_error(text: str) -> bool:
    lowered = text.casefold()
    return any(hint in lowered for hint in QUOTA_HINTS)


def load_records(path: Path) -> list[ConsumerRecord]:
    if not path.is_file():
        return []
    records: list[ConsumerRecord] = []
    for line in path.read_text().splitlines():
        if line.strip():
            records.append(ConsumerRecord.model_validate_json(line))
    return records


def append_record(path: Path, record: ConsumerRecord) -> None:
    with path.open("a") as handle:
        handle.write(record.model_dump_json() + "\n")


def cell_dir_for(scratch_root: Path, run_name: str, record: ConsumerRecord) -> Path:
    return scratch_root / run_name / record.consumer / record.arm / record.question_id


def copy_transcript(
    run_dir: Path, source: Path, *, consumer: str, arm: str, question_id: str
) -> str:
    """The cell's event stream, copied into the run directory (D-023c).

    The scratch directory is the consumer's working directory and nothing else,
    so the conversation behind a row travels with the run and a reviewer can
    open it from the record's ``transcript`` path.
    """
    target = run_dir / "transcripts" / consumer / arm / f"{question_id}.jsonl"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not source.is_file():
        return ""
    shutil.copyfile(source, target)
    return str(target.relative_to(run_dir))


async def _collect_cell(
    spec: ConsumerSpec,
    question: EvalQuestion,
    arm: str,
    *,
    run_dir: Path,
    run_name: str,
    scratch_root: Path,
    mcp_urls: Mapping[str, str],
    token: str,
    timeout_s: float,
    semaphore: asyncio.Semaphore,
    append_lock: asyncio.Lock,
) -> ConsumerRecord:
    key = (spec.name, arm, question.id)
    cell_dir = scratch_root / run_name / spec.name / arm / question.id
    prompt = prompt_for(question)
    mcp_url = mcp_urls.get(arm)
    collect = COLLECTORS[spec.harness]
    async with semaphore:
        collected = await asyncio.to_thread(
            collect,
            spec,
            prompt,
            cell_dir,
            mcp_url=mcp_url,
            token=token,
            timeout_s=timeout_s,
        )
    transcript = copy_transcript(
        run_dir,
        Path(collected.transcript),
        consumer=spec.name,
        arm=arm,
        question_id=question.id,
    )
    links = extract_links(collected.answer_text)
    calls = collected.tool_calls
    record = ConsumerRecord(
        consumer=spec.name,
        arm=arm,
        question_id=question.id,
        question_type=question.type.value,
        question=question.question,
        reference_answer=question.reference_answer,
        gold_urls=[gold.url for gold in question.gold],
        answer_text=collected.answer_text,
        wall_seconds=collected.wall_seconds,
        tokens=collected.tokens,
        harness_cost_usd=collected.cost_usd,
        tool_calls=calls,
        mcp_called=any(is_server_tool(call.name) for call in calls),
        cite_called=any(is_verify_tool(call.name) for call in calls),
        links=links,
        transcript=transcript or collected.transcript,
        error=collected.error,
    )
    async with append_lock:
        append_record(run_dir / "records.jsonl", record)
    logger.info("Consumer cell done", key=key, error=record.error)
    return record


async def run_collection(
    questions: Sequence[EvalQuestion],
    specs: Sequence[ConsumerSpec],
    arms: Sequence[str],
    *,
    run_dir: Path,
    run_name: str,
    scratch_root: Path,
    mcp_urls: Mapping[str, str],
    token: str,
    timeout_s: float,
) -> list[ConsumerRecord]:
    """Every cell through its harness, skipping cells already recorded."""
    done = {(r.consumer, r.arm, r.question_id) for r in load_records(run_dir / "records.jsonl")}
    pending = [
        (spec, question, arm)
        for spec in specs
        for arm in arms
        for question in questions
        if (spec.name, arm, question.id) not in done
    ]
    logger.info("Consumer collection", pending=len(pending), recorded=len(done), run=str(run_dir))
    semaphore = asyncio.Semaphore(MAX_PARALLEL)
    append_lock = asyncio.Lock()

    # One coroutine per cell would open every question at once; bound the
    # concurrency with the semaphore inside _collect_cell instead.
    async def one(spec: ConsumerSpec, question: EvalQuestion, arm: str) -> ConsumerRecord:
        return await _collect_cell(
            spec,
            question,
            arm,
            run_dir=run_dir,
            run_name=run_name,
            scratch_root=scratch_root,
            mcp_urls=mcp_urls,
            token=token,
            timeout_s=timeout_s,
            semaphore=semaphore,
            append_lock=append_lock,
        )

    return list(
        await asyncio.gather(*(one(spec, question, arm) for spec, question, arm in pending))
    )


# --------------------------------------------------------------------------- #
# Judging (resumable; runs after the judge quota window reopens)
# --------------------------------------------------------------------------- #


def judged_citations(record: ConsumerRecord) -> list[JudgedCitation]:
    """Citations as the blind judge sees them: the verified quote and the
    passage behind it.

    A consumer answer has no served context the harness kept, so the only
    evidence the judge can check a claim against is the quote the server
    verified. The passage is that quote verbatim: groundedness then measures
    whether each claim follows from the sentences the answer cites, which is
    the honest reading for an answer whose evidence is quotes, not pages.
    """
    citations: list[JudgedCitation] = []
    for call in record.tool_calls:
        if not is_verify_tool(call.name):
            continue
        raw_quotes = call.arguments.get("quotes", "")
        try:
            quotes = json.loads(raw_quotes) if raw_quotes.startswith("[") else []
        except ValueError:
            quotes = []
        try:
            verdicts = json.loads(call.arguments.get("__verdicts", "{}"))
        except ValueError:
            verdicts = {}
        if not isinstance(verdicts, dict):
            verdicts = {}
        for quote in quotes:
            if not isinstance(quote, dict):
                continue
            try:
                number = int(quote.get("n", -1))
            except (TypeError, ValueError):
                continue
            text = quote.get("quote", "")
            if verdicts.get(str(number)) is True and isinstance(text, str) and text.strip():
                citations.append(JudgedCitation(n=number, quote=text, source_text=text))
    return citations


def judge_payload(record: ConsumerRecord) -> JudgeInput:
    return JudgeInput(
        question=record.question,
        reference_answer=record.reference_answer,
        answer_markdown=record.answer_text,
        citations=judged_citations(record),
    )


async def judge_record(
    record: ConsumerRecord,
    *,
    provider: OpenAICompatibleProvider,
    model: str,
) -> JudgeRecord:
    payload = judge_payload(record)
    rendered = payload.render()
    started = time.perf_counter()
    with (
        candidate_scope(f"{record.consumer}:{record.arm}:{record.question_id}"),
        call_scope("judge"),
    ):
        try:
            completion = await provider.complete(
                [
                    {"role": "system", "content": JUDGE_SYSTEM},
                    {"role": "user", "content": rendered},
                ],
                model=model,
                temperature=JUDGE_TEMPERATURE,
                max_tokens=JUDGE_MAX_TOKENS,
                response_schema=JudgeVerdict,
                thinking="disabled" if provider.name == "zai" else None,
            )
        except ProviderCallError as error:
            return JudgeRecord(
                model=model,
                provider=provider.name,
                prompt_version=JUDGE_VERSION,
                input_text=rendered,
                error=str(error),
                latency_ms=(time.perf_counter() - started) * 1000,
            )
    verdict = completion.parsed if isinstance(completion.parsed, JudgeVerdict) else None
    return JudgeRecord(
        model=model,
        provider=provider.name,
        prompt_version=JUDGE_VERSION,
        input_text=rendered,
        raw_output=completion.text,
        verdict=verdict,
        error=None if verdict else "the judge's output did not validate",
        latency_ms=(time.perf_counter() - started) * 1000,
        usage=completion.usage,
    )


async def run_judge(
    run_dir: Path,
    judge_models: Sequence[JudgeModel],
    *,
    rejudge: bool = False,
    quota_ceiling: int = 80,
) -> dict[str, int]:
    """Grade every unjudged row with the first judge model. Resumes: rows the
    model already graded at this prompt version are skipped."""
    records = load_records(run_dir / "records.jsonl")
    if not judge_models:
        raise SystemExit("no judge models requested")
    primary = judge_models[0]
    pending_ids = {
        id(record)
        for record in records
        if rejudge
        or record.judge is None
        or record.judge.model != primary.model
        or record.judge.prompt_version != JUDGE_VERSION
    }
    counts = {"judged": 0, "skipped": len(records) - len(pending_ids), "errors": 0}
    if not pending_ids:
        return counts
    await wait_for_quota(quota_ceiling)
    recorder = _CallsRecorder(run_dir)
    async with OpenAICompatibleProvider(
        primary.provider,
        asyncio.Semaphore(4 if primary.provider == "zai" else 1),
        caller_tag="eval.consumer",
        recorder=recorder,
        seed=0,
    ) as provider:
        judged: list[ConsumerRecord] = []
        for record in records:
            if id(record) not in pending_ids:
                judged.append(record)
                continue
            result = await judge_record(record, provider=provider, model=primary.model)
            counts["judged"] += 1
            if result.error is not None:
                counts["errors"] += 1
            judged.append(record.model_copy(update={"judge": result}))
    temporary = run_dir / "records.jsonl.tmp"
    temporary.write_text("".join(r.model_dump_json() + "\n" for r in judged))
    temporary.replace(run_dir / "records.jsonl")
    return counts


# --------------------------------------------------------------------------- #
# Deterministic scoring
# --------------------------------------------------------------------------- #


def corpus_page_urls(corpus_dir: Path = DEFAULT_CORPUS) -> set[str]:
    manifest = corpus_dir / "manifest.json"
    if not manifest.is_file():
        return set()
    pages = json.loads(manifest.read_text())
    return {str(page.get("url", "")) for page in pages if page.get("url")}


def page_of(url: str) -> str:
    """A cited URL reduced to its corpus page: host plus path, no fragment."""
    parts = urlsplit(url)
    if parts.netloc != "docs.mistral.ai":
        return url
    return f"https://{parts.netloc}{parts.path}"


def record_metrics(record: ConsumerRecord, corpus_urls: set[str]) -> dict[str, float | None]:
    answerable = record.question_type != "unanswerable"
    page_links = [page_of(url) for url in record.links]
    resolved = [url for url in page_links if url in corpus_urls]
    gold = [url for url in page_links if url in set(record.gold_urls)]
    bad_param = sum(1 for call in record.tool_calls if _BAD_PARAM in (call.error or ""))
    clamps = sum(1 for call in record.tool_calls for note in call.notes if _CLAMP in note)
    verified, rejected = cite_verdicts(record.tool_calls)
    verdict = record.judge.verdict if record.judge else None
    return {
        "correctness": CORRECTNESS_SCORE[verdict.correctness] if verdict else None,
        "correct": float(verdict.correctness == "correct") if verdict else None,
        "refusal_correct": float(refused(record.answer_text) == (not answerable)),
        "refused": float(refused(record.answer_text)),
        "links": float(len(record.links)),
        "links_resolve": float(len(resolved) / len(page_links)) if page_links else None,
        "links_on_gold": float(bool(gold)) if answerable else None,
        "mcp_called": float(record.mcp_called),
        "cite_called": float(record.cite_called),
        "cite_verified": float(verified),
        "cite_rejected": float(rejected),
        "tool_calls": float(len(record.tool_calls)),
        "bad_param_errors": float(bad_param),
        "clamps": float(clamps),
        "tokens_total": float(record.tokens.total),
        "wall_seconds": record.wall_seconds,
        "errors": float(record.error is not None),
    }


def _mean(values: Sequence[float | None]) -> float | None:
    kept = [v for v in values if v is not None]
    return statistics.fmean(kept) if kept else None


def _percentile(values: Sequence[float], fraction: float) -> float | None:
    """Nearest-rank percentile, like the answer eval: a dozen questions per
    cell is too few for an interpolated percentile to mean anything."""
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(fraction * len(ordered)) - 1))
    return ordered[index]


CELL_METRICS = (
    "correctness",
    "refusal_correct",
    "links_resolve",
    "links_on_gold",
    "mcp_called",
    "cite_called",
    "cite_verified",
    "cite_rejected",
    "tool_calls",
    "bad_param_errors",
    "clamps",
    "tokens_total",
)


def aggregate(records: Sequence[ConsumerRecord], corpus_urls: set[str]) -> dict[str, Any]:
    """One metrics object for the run: per (consumer, arm) cells plus totals."""
    per_row = [record_metrics(record, corpus_urls) for record in records]
    grouped: dict[str, list[dict[str, float | None]]] = {}
    for record, metrics in zip(records, per_row, strict=True):
        grouped.setdefault(f"{record.consumer} / {record.arm}", []).append(metrics)
    by_cell: dict[str, dict[str, Any]] = {}
    for name, rows in grouped.items():
        by_cell[name] = {
            "n": len(rows),
            "errors": int(sum(r["errors"] or 0 for r in rows)),
            **{metric: _mean([r[metric] for r in rows]) for metric in CELL_METRICS},
            "latency_p50": _percentile(
                [float(r["wall_seconds"] or 0) for r in rows],
                0.5,
            ),
        }
    return {"cells": by_cell, "records": len(records)}


def check_fragments(
    run_dir: Path, records: Sequence[ConsumerRecord], *, sample: int = 60, seed: int = 0
) -> dict[str, Any]:
    """Do the answer links resolve: page in the corpus, fragment text on it.

    Page resolution is offline against the manifest. Fragment text is checked
    against the live page with cached fetches under the run directory, reusing
    the fragment check's visible-text reduction;     tab-panel misses are reported
    apart for the same reason as in the answer eval.
    """
    candidates = sorted({url for record in records for url in record.links})
    chosen = (
        random.Random(seed).sample(candidates, sample) if len(candidates) > sample else candidates
    )
    cache = PageCache(run_dir / "fragments" / "pages")
    rows: list[dict[str, Any]] = []
    for url in chosen:
        base, _, directive = url.partition(":~:text=")
        row: dict[str, Any] = {
            "url": url,
            "page": base,
            "has_fragment": bool(directive),
            "found": None,
            "failure": None,
        }
        if not directive:
            rows.append(row)
            continue
        try:
            response = cache.get(base)
        except httpx.HTTPError:
            row["failure"] = "page fetch"
            rows.append(row)
            continue
        if response.status_code != 200:
            row["failure"] = "page fetch"
            rows.append(row)
            continue
        text = visible_text(response.content.decode("utf-8", errors="replace")).casefold()
        start, _, end = directive.partition(",")
        start_text = urllib.parse.unquote(start).replace("\n", " ").casefold()
        found = start_text in text
        failure = None if found else "text absent"
        if found and end:
            end_text = urllib.parse.unquote(end).replace("\n", " ").casefold()
            found = end_text in text[text.find(start_text) + len(start_text) :]
            failure = None if found else "range order"
        row["found"] = found
        row["failure"] = failure
        rows.append(row)
    fragment_rows = [row for row in rows if row["has_fragment"]]
    found_count = sum(1 for row in fragment_rows if row["found"])
    metrics = {
        "links_checked": len(rows),
        "fragment_links": len(fragment_rows),
        "fragments_found": found_count,
        "share_found": found_count / len(fragment_rows) if fragment_rows else None,
        "seed": seed,
    }
    (run_dir / "fragments" / "results.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    )
    (run_dir / "fragments" / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n"
    )
    return metrics


def collect_defects(records: Sequence[ConsumerRecord]) -> list[dict[str, str]]:
    """Every wrong turn the transcripts show, as a surface defect until proven
    otherwise. Severities: a turn that cost the answer is ``severe``; one that
    cost extra calls is ``extra-calls``; anything else is ``friction``."""
    defects: list[dict[str, str]] = []
    for record in records:
        for call in record.tool_calls:
            error = call.error or ""
            if _BAD_PARAM in error:
                defects.append(
                    {
                        "question_id": record.question_id,
                        "consumer": record.consumer,
                        "arm": record.arm,
                        "transcript": record.transcript,
                        "observation": f"{call.name} rejected with E_BAD_PARAM: {error}",
                        "severity": "extra-calls",
                        "proposal": (
                            "Read the transcript turn: if the parameter name came "
                            "from the tool description, rename the description's "
                            "wording; if it came from the guide, fix the guide."
                        ),
                    }
                )
            # Any refusal by one of this server's tools is friction, typed or
            # not: the error row names the tool before the line the tool
            # printed, so matching the line's start missed both the typed
            # errors and the schema rejections. A consumer's own shell or fetch
            # failing is not a defect of the surface under test.
            elif is_server_tool(call.name) and error:
                defects.append(
                    {
                        "question_id": record.question_id,
                        "consumer": record.consumer,
                        "arm": record.arm,
                        "transcript": record.transcript,
                        "observation": f"{call.name} returned {error}",
                        "severity": "friction",
                        "proposal": (
                            "Check whether the typed error and its next hint led "
                            "the consumer to a working call within two turns; if "
                            "not, sharpen the hint."
                        ),
                    }
                )
        if record.error and not is_quota_error(record.error):
            defects.append(
                {
                    "question_id": record.question_id,
                    "consumer": record.consumer,
                    "arm": record.arm,
                    "transcript": record.transcript,
                    "observation": f"harness failed: {record.error}",
                    "severity": "severe",
                    "proposal": (
                        "Re-run the cell by hand; if the failure repeats, the "
                        "harness or the prompt needs a fix before the numbers "
                        "are quoted."
                    ),
                }
            )
    return defects


def render_figures(metrics: Mapping[str, Any], figures_dir: Path) -> list[str]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    cells = metrics["cells"]
    names = sorted(cells)
    consumers = sorted({name.split(" / ")[0] for name in names})
    single_consumer = len(consumers) == 1

    def label(name: str) -> str:
        return name.split(" / ")[1] if single_consumer else name

    written: list[str] = []
    svg = bar_chart(
        "Correctness by arm and consumer (blind judge v2)",
        [(label(name), [cells[name].get("correctness") or 0.0]) for name in names],
        ["correctness"],
    )
    (figures_dir / "correctness-by-arm.svg").write_text(svg)
    written.append("figures/correctness-by-arm.svg")
    svg = bar_chart(
        "Citation resolvability by arm (links on a corpus page)",
        [(label(name), [cells[name].get("links_resolve") or 0.0]) for name in names],
        ["share"],
    )
    (figures_dir / "citation-resolvability-by-arm.svg").write_text(svg)
    written.append("figures/citation-resolvability-by-arm.svg")
    return written


def render_readme(
    config: Mapping[str, Any], metrics: Mapping[str, Any], fragments: Mapping[str, Any]
) -> str:
    lines = [
        "# Blind consumer evaluation",
        "",
        "Weak models at low reasoning answer Mistral documentation questions over",
        "glossator's MCP server, without being told they are evaluated. Three arms",
        "per consumer: A0 answers from memory, A1 uses retrieval tools plus `cite`,",
        "A2 asks the server for the answer. Shell tools stay available in every",
        "arm, so the comparison is between whole agents.",
        "",
        "## Protocol",
        "",
        f"- Questions: {config['question_count']} fixed rows "
        f"({config['mined_count']} stratified from eval/mined.jsonl and "
        f"{config['fresh_count']} from eval/dev-fresh60.jsonl, seed 0), identical "
        "in every arm and for every consumer.",
        "- The prompt is one fixed sentence plus the question; nothing says",
        "  evaluation and nothing names the tools.",
        f"- Consumers: {', '.join(config['consumers'])}.",
        f"- Judge: {config.get('judge_model') or 'not yet run'} "
        f"({JUDGE_VERSION}); citation passages shown to the judge are the verified",
        "  quotes themselves, since a consumer answer keeps no served context.",
        "",
        "## Cells",
        "",
        "| cell | n | correctness | refusal | links resolve | on gold | mcp called "
        "| cite verified | tool calls | bad params | p50 s |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in sorted(metrics["cells"]):
        cell = metrics["cells"][name]
        lines.append(
            f"| {name} | {cell['n']} | {_fmt(cell.get('correctness'))} | "
            f"{_fmt(cell.get('refusal_correct'))} | {_fmt(cell.get('links_resolve'))} | "
            f"{_fmt(cell.get('links_on_gold'))} | {_fmt(cell.get('mcp_called'))} | "
            f"{_fmt(cell.get('cite_verified'))} | "
            f"{_fmt(cell.get('tool_calls'))} | {_fmt(cell.get('bad_param_errors'))} | "
            f"{_fmt(cell.get('latency_p50'))} |"
        )
    lines += [
        "",
        "Correctness is the blind judge's 1 / 0.5 / 0 mean where judged, else `--`.",
        "`links resolve` is the share of answer URLs landing on a corpus page;",
        "`on gold` the share of answerable answers naming a gold page. Refusal is a",
        "heuristic over the answer text (declines for lack of documentation).",
        "",
        "## Fragments",
        "",
        f"{fragments.get('fragments_found')} of {fragments.get('fragment_links')} "
        "sampled fragment links found their text on the live page "
        f"(seed {fragments.get('seed')}).",
        "",
        "## Files",
        "",
        "- `records.jsonl`: one row per consumer, arm, question, with the answer",
        "  text and the extracted links.",
        "- `metrics.json`: the cells above in machine form.",
        "- `defects.md`: every wrong turn with transcript path and severity.",
        "- `samples.md`: ten questions with the three arms side by side.",
        "- `figures/`: regenerated SVG charts.",
        "- `transcripts/<consumer>/<arm>/<question>.jsonl`: the harness event",
        "  stream behind every row, copied out of the consumer's scratch",
        "  directory at collection time; each record names its own under",
        "  `transcript`.",
        "- `calls.jsonl`: the judge's calls, verbatim. The consumers' own model",
        "  calls are their harnesses', not this server's.",
    ]
    return "\n".join(lines) + "\n"


def _fmt(value: Any) -> str:
    if value is None:
        return "--"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def render_defects(defects: Sequence[Mapping[str, str]]) -> str:
    lines = [
        "# Surface defects",
        "",
        "Every wrong turn a consumer took, with the transcript path, a severity,",
        "and a proposed fix in prose. Fixes to the server belong in their own change.",
        "",
    ]
    if not defects:
        lines.append("No defects observed: no typed errors and no harness failures.")
        return "\n".join(lines) + "\n"
    for index, defect in enumerate(defects, 1):
        lines += [
            f"## {index}. {defect['question_id']} ({defect['consumer']} / {defect['arm']})",
            "",
            f"- Observation: {defect['observation']}",
            f"- Transcript: `{defect['transcript']}`",
            f"- Severity: {defect['severity']}",
            f"- Proposed fix: {defect['proposal']}",
            "",
        ]
    return "\n".join(lines)


def render_samples(records: Sequence[ConsumerRecord], *, consumer: str, seed: int = 0) -> str:
    """Ten seeded questions, the arms' answers side by side for one consumer.

    A run collected by one consumer is scored with the default name of
    another often enough that an empty samples file is the likelier mistake
    than a deliberately empty one, so a name no record carries falls back to
    the first consumer in the run.
    """
    present = [record.consumer for record in records]
    if consumer not in present and present:
        consumer = present[0]
    question_ids = sorted({r.question_id for r in records if r.consumer == consumer})
    chosen = random.Random(seed).sample(question_ids, min(10, len(question_ids)))
    by_key = {(r.question_id, r.arm): r for r in records if r.consumer == consumer}
    lines = [
        "# Answer samples",
        "",
        f"Ten seeded questions (seed {seed}) for consumer `{consumer}`, the arms'",
        "answers side by side with the judge's verdicts.",
        "",
    ]
    for question_id in chosen:
        first = next(r for r in records if r.question_id == question_id)
        lines += [f"## {question_id} ({first.question_type})", "", first.question, ""]
        for arm in ARMS:
            record = by_key.get((question_id, arm))
            if record is None:
                lines += [f"### {arm}: not run", ""]
                continue
            verdict = (
                record.judge.verdict.correctness
                if record.judge and record.judge.verdict
                else "not judged"
            )
            lines += [
                f"### {arm} (judge: {verdict})",
                "",
                record.answer_text or f"(no answer: {record.error})",
                "",
            ]
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def resolve_run_directory(name: str, *, root: Path = RUNS_ROOT) -> Path:
    path = root / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def _read_config(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "config.json"
    if not path.is_file():
        return {}
    loaded = json.loads(path.read_text())
    return loaded if isinstance(loaded, dict) else {}


MERGED_KEYS = (
    "consumers",
    "consumer_models",
    "consumer_harnesses",
    "consumer_variants",
    "arms",
    "arm_tools",
    "mcp_urls",
)


def merge_config(existing: Mapping[str, Any], fresh: Mapping[str, Any]) -> dict[str, Any]:
    """The config of a run a second consumer is being added to.

    Consumers run one command each, often days apart and on different quota
    windows, into the same run directory. Writing the newest command's config
    over the old one left the run describing one consumer while its records
    held several, so the consumer and arm keys are unions and everything else
    is the newest command's.
    """
    if not existing:
        return dict(fresh)
    if existing.get("questions") != fresh.get("questions"):
        raise SystemExit(
            "the run directory holds a different question set; use a new --name "
            "or the same --mined/--fresh counts"
        )
    merged = dict(fresh)
    for key in MERGED_KEYS:
        before, after = existing.get(key), fresh.get(key)
        if isinstance(before, list) and isinstance(after, list):
            merged[key] = before + [item for item in after if item not in before]
        elif isinstance(before, dict) and isinstance(after, dict):
            merged[key] = {**before, **after}
    for key in ("judge_model", "judge_models"):
        if existing.get(key) and not fresh.get(key):
            merged[key] = existing[key]
    return merged


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Blind consumer evaluation over the MCP server")
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run", help="Collect consumer answers")
    run_parser.add_argument("--name", help="Run name; re-running it resumes the run")
    run_parser.add_argument(
        "--consumers",
        default="opencode-muse-minimal",
        help="Comma-separated consumer names",
    )
    run_parser.add_argument("--arms", default="A0,A1", help="Comma-separated arms")
    run_parser.add_argument("--scratch-root", type=Path, required=True)
    run_parser.add_argument("--mcp-url-a1", default="http://127.0.0.1:8000/mcp")
    run_parser.add_argument("--mcp-url-a2", default="http://127.0.0.1:8001/mcp")
    run_parser.add_argument("--token-env", default="GLOSSATOR_MCP_TOKEN")
    run_parser.add_argument("--timeout-s", type=float, default=QUESTION_TIMEOUT_S)
    run_parser.add_argument("--runs-root", type=Path, default=RUNS_ROOT)
    run_parser.add_argument(
        "--mined", type=int, default=MINED_COUNT, help="How many mined questions (seed 0)"
    )
    run_parser.add_argument(
        "--fresh", type=int, default=FRESH_COUNT, help="How many fresh questions (seed 0)"
    )
    run_parser.add_argument("--mined-path", type=Path, default=MINED_DATASET)
    run_parser.add_argument("--fresh-path", type=Path, default=FRESH_DATASET)

    judge_parser = sub.add_parser("judge", help="Grade stored answers (resumable)")
    judge_parser.add_argument("--run", type=Path, required=True)
    judge_parser.add_argument("--judge-models", default="zai:glm-5.3")
    judge_parser.add_argument("--rejudge", action="store_true")
    judge_parser.add_argument("--quota-ceiling", type=int, default=80)

    score_parser = sub.add_parser("score", help="Score a run deterministically")
    score_parser.add_argument("--run", type=Path, required=True)
    score_parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    score_parser.add_argument("--sample-consumer", default="opencode-muse-minimal")
    return parser.parse_args(argv)


async def _run(args: argparse.Namespace) -> None:
    specs = [consumer_spec(name.strip()) for name in args.consumers.split(",")]
    arms = [arm.strip() for arm in args.arms.split(",")]
    unknown_arms = sorted(set(arms) - set(ARMS))
    if unknown_arms:
        raise SystemExit(f"unknown arms {unknown_arms}; available: {list(ARMS)}")
    name = args.name or (datetime.now(UTC).strftime("%Y-%m-%d-%H%M") + "-consumer-eval")
    run_dir = resolve_run_directory(name, root=args.runs_root)
    questions = build_question_set(args.mined, args.fresh, args.mined_path, args.fresh_path)
    token = os.environ.get(args.token_env, "")
    if any(arm in ("A1", "A2") for arm in arms) and not token:
        raise SystemExit(f"{args.token_env} is not set; the MCP arms need it")
    mcp_urls = {"A1": args.mcp_url_a1, "A2": args.mcp_url_a2}
    config = {
        "kind": "consumer_eval",
        "name": name,
        "run_dir": str(run_dir),
        "consumers": [spec.name for spec in specs],
        "consumer_models": {spec.name: spec.model for spec in specs},
        "consumer_harnesses": {spec.name: spec.harness for spec in specs},
        "consumer_variants": {spec.name: spec.variant for spec in specs},
        "arms": arms,
        "arm_tools": {arm: ARM_TOOLS[arm] for arm in arms},
        "mcp_urls": {arm: mcp_urls[arm] for arm in arms if arm in mcp_urls},
        "mcp_server_name": MCP_SERVER_NAME,
        "scratch_root": str(args.scratch_root),
        "question_count": len(questions),
        "mined_count": args.mined,
        "fresh_count": args.fresh,
        "unanswerable_count": sum(1 for q in questions if q.type.value == "unanswerable"),
        "questions": [question.id for question in questions],
        "prompt_lead": PROMPT_LEAD,
        "judge_model": None,
        "judge_prompt_version": JUDGE_VERSION,
        "judge_prompt_hashes": JUDGE_PROMPT_HASHES,
    }
    config = merge_config(_read_config(run_dir), config)
    (run_dir / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    (run_dir / "questions.jsonl").write_text("".join(q.model_dump_json() + "\n" for q in questions))
    _start_run_directory(run_dir)
    await run_collection(
        questions,
        specs,
        arms,
        run_dir=run_dir,
        run_name=name,
        scratch_root=args.scratch_root,
        mcp_urls=mcp_urls,
        token=token,
        timeout_s=args.timeout_s,
    )


async def _judge(args: argparse.Namespace) -> None:
    try:
        judge_models = parse_judge_models(args.judge_models)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    counts = await run_judge(
        args.run, judge_models, rejudge=args.rejudge, quota_ceiling=args.quota_ceiling
    )
    config_path = args.run / "config.json"
    if config_path.is_file():
        config = json.loads(config_path.read_text())
        config["judge_model"] = judge_models[0].identifier
        config["judge_models"] = [judge.identifier for judge in judge_models]
        config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    print(json.dumps(counts, indent=2, sort_keys=True))


def _score(args: argparse.Namespace) -> None:
    run_dir: Path = args.run
    records = load_records(run_dir / "records.jsonl")
    corpus_urls = corpus_page_urls(args.corpus)
    metrics = aggregate(records, corpus_urls)
    fragments = check_fragments(run_dir, records)
    metrics["fragments"] = fragments
    judged = sum(1 for r in records if r.judge and r.judge.verdict)
    metrics["judged"] = judged
    config = json.loads((run_dir / "config.json").read_text())
    metrics["correctness_cost"] = _cost_per_correct(records)
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    (run_dir / "README.md").write_text(render_readme(config, metrics, fragments))
    (run_dir / "defects.md").write_text(render_defects(collect_defects(records)))
    (run_dir / "samples.md").write_text(render_samples(records, consumer=args.sample_consumer))
    figures = render_figures(metrics, run_dir / "figures")
    print(json.dumps({"records": len(records), "figures": figures}, indent=2))


def _start_run_directory(run_dir: Path) -> None:
    """Give a collection run the shape D-023 asks for before it collects anything.

    Collection, judging and scoring are three commands, and a run interrupted
    between them used to sit in the repository as a bare `records.jsonl`: no
    ledger, no figures directory, and no README saying what it was or which of
    the three steps still owed it numbers. The placeholder is overwritten by
    `score`.
    """
    (run_dir / "figures").mkdir(parents=True, exist_ok=True)
    (run_dir / "calls.jsonl").touch()
    (run_dir / "records.jsonl").touch()
    readme = run_dir / "README.md"
    if not readme.is_file():
        readme.write_text(
            "# Blind consumer evaluation (collecting)\n\n"
            "Answers are being collected; no judge has run and no metrics exist yet.\n"
            "`config.json` holds the consumers, arms and question set. Run\n"
            "`python -m glossator.eval.consumer judge --run <dir>` and then `score`\n"
            "to fill in `metrics.json`, `figures/` and this file.\n"
        )


def _cost_per_correct(records: Sequence[ConsumerRecord]) -> dict[str, float | None]:
    """Harness tokens per correct answer, per cell (judge-dependent)."""
    out: dict[str, float | None] = {}
    cells: dict[str, list[ConsumerRecord]] = {}
    for record in records:
        cells.setdefault(f"{record.consumer} / {record.arm}", []).append(record)
    for name, rows in cells.items():
        correct = sum(
            1
            for row in rows
            if row.judge and row.judge.verdict and row.judge.verdict.correctness == "correct"
        )
        tokens = sum(row.tokens.total for row in rows)
        out[name] = tokens / correct if correct else None
    return out


def main() -> None:
    load_dotenv(override=True)
    args = _parse_args()
    if args.command == "run":
        asyncio.run(_run(args))
    elif args.command == "judge":
        asyncio.run(_judge(args))
    elif args.command == "score":
        _score(args)
    else:
        raise SystemExit(f"unknown command {args.command!r}")


if __name__ == "__main__":
    main()


__all__ = [
    "ARMS",
    "ARM_TOOLS",
    "COLLECTORS",
    "TOOL_SUFFIXES",
    "CONSUMERS",
    "CONSUMER_NAMES",
    "MAX_PARALLEL",
    "MCP_SERVER_NAME",
    "PROMPT_LEAD",
    "ConsumerRecord",
    "ConsumerSpec",
    "HarnessTokens",
    "ToolCallRecord",
    "aggregate",
    "build_question_set",
    "check_fragments",
    "cite_verdicts",
    "claude_command",
    "claude_failure",
    "codex_command",
    "codex_failure",
    "collect_claude",
    "collect_codex",
    "collect_defects",
    "collect_opencode",
    "consumer_spec",
    "copy_transcript",
    "corpus_page_urls",
    "extract_links",
    "is_quota_error",
    "is_server_tool",
    "is_verify_tool",
    "judge_payload",
    "judge_record",
    "load_records",
    "merge_config",
    "opencode_command",
    "parse_claude_events",
    "parse_claude_tokens",
    "parse_codex_events",
    "parse_codex_tokens",
    "parse_opencode_events",
    "parse_opencode_tokens",
    "prompt_for",
    "write_claude_mcp_config",
    "record_metrics",
    "refused",
    "render_defects",
    "render_figures",
    "render_readme",
    "render_samples",
    "resolve_run_directory",
    "run_collection",
    "run_judge",
]
