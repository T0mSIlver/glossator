"""The Mistral Work stand-in: the Conversations API's Connector tool loop.

Work has no API, but a Work session is a Connector-attached agent, and the
Conversations API runs the same server-side tool loop with the same model and
``reasoning_effort``. This module sends a question set through that loop --
one agent per run, one unstored conversation per question -- and writes a run
directory the consumer ``judge`` and ``score`` subcommands read unchanged.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import structlog
from dotenv import load_dotenv
from mistralai.client import Mistral
from mistralai.client.errors import MistralError
from mistralai.client.models.agent import Agent
from mistralai.client.models.completionargs import CompletionArgs
from mistralai.client.models.conversationresponse import ConversationResponse
from mistralai.client.models.customconnector import CustomConnector
from mistralai.client.models.messageinputentry import MessageInputEntry

from glossator.eval.consumer import (
    NAMESPACED_TOOLS,
    RUNS_ROOT,
    ConsumerRecord,
    HarnessTokens,
    ToolCallRecord,
    _fmt,
    _text_blocks,
    _tool_call_record,
    aggregate,
    append_record,
    corpus_page_urls,
    extract_links,
    is_server_tool,
    is_verify_tool,
    load_records,
)
from glossator.eval.datasets import EvalQuestion, dataset_hash, read_jsonl
from glossator.eval.pricing import estimate_usd
from glossator.eval.providers import TokenUsage

logger = structlog.get_logger(__name__)

SKILL_PATH = Path("skills/mistral-docs/SKILL.md")
CUSTOM_INSTRUCTIONS_PATH = Path("skills/mistral-docs/custom-instructions.md")

DEFAULT_MODEL = "mistral-medium-3-5"
DEFAULT_REASONING_EFFORT = "high"
DEFAULT_CONNECTOR = "mistral_docs_ca30"
"""The workspace's Connector for the deployed server, the one Work sessions use.
The platform suffixes a Connector's requested name with four hex characters, so
the name to pass is the suffixed one, or the UUID (D-049)."""
DEFAULT_CONCURRENCY = 2
QUESTION_TIMEOUT_S = 300.0
HTTP_ATTEMPTS = 5
"""429 and 5xx wait 2 * 2**attempt seconds. The platform rate-limits custom
Connector calls per minute, which the providers' sub-second backoff never
outwaits; four retries reach half a minute."""

ReasoningEffortChoice = Literal["high", "none"]
"""What the Work demo runs: reasoning on (high) or off (none). The Conversations
API accepts the same values its ``CompletionArgs`` lists."""


# --------------------------------------------------------------------------- #
# Instructions
# --------------------------------------------------------------------------- #


def skill_body(skill_path: Path = SKILL_PATH) -> str:
    """The skill file after its frontmatter: the instructions the agent runs."""
    text = skill_path.read_text()
    if text.startswith("---"):
        _, _, body = text.split("---", 2)
        return body.strip()
    return text.strip()


def custom_instructions_block(custom_path: Path = CUSTOM_INSTRUCTIONS_PATH) -> str:
    """The quoted block of the custom-instructions file, unquoted and joined.

    The block is line-wrapped markdown; a Work session carries it as one
    paragraph of context, so the lines are joined with spaces, not newlines.
    """
    lines = [
        line.removeprefix(">").strip()
        for line in custom_path.read_text().splitlines()
        if line.startswith(">")
    ]
    return " ".join(part for part in lines if part)


def agent_instructions(
    skill_path: Path = SKILL_PATH, custom_path: Path = CUSTOM_INSTRUCTIONS_PATH
) -> str:
    """What the proxy agent is told: the skill body, then the Work context."""
    return f"{skill_body(skill_path)}\n\n{custom_instructions_block(custom_path)}"


# --------------------------------------------------------------------------- #
# Response parsing
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class ParsedToolExecution:
    """One ``tool.execution`` output entry, kept verbatim enough for a transcript."""

    name: str
    arguments: str
    result: str
    failed: bool


@dataclass(slots=True)
class ParsedConversation:
    """One conversation response, reduced to what a record and a transcript hold."""

    answer_text: str = ""
    thinking: list[str] = field(default_factory=list)
    calls: list[ParsedToolExecution] = field(default_factory=list)
    usage: HarnessTokens = HarnessTokens()
    raw_usage: dict[str, Any] = field(default_factory=dict)


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
        return _text_blocks(result)
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
        _tool_call_record(call.name, arguments_of(call), call.result, call.failed) for call in calls
    ]


# --------------------------------------------------------------------------- #
# The Conversations-API loop
# --------------------------------------------------------------------------- #


def _status_of(error: BaseException) -> int | None:
    raw = getattr(error, "raw_response", None)
    return getattr(raw, "status_code", None)


async def start_conversation(
    client: Mistral,
    *,
    agent_id: str,
    question: str,
    timeout_s: float,
) -> ConversationResponse:
    """One conversation through the server-side tool loop, retried like the
    providers' calls: 429 and 5xx back off, anything else fails the question."""
    last_error: BaseException | None = None
    for attempt in range(HTTP_ATTEMPTS):
        try:
            return await asyncio.wait_for(
                client.beta.conversations.start_async(
                    agent_id=agent_id,
                    inputs=[MessageInputEntry(role="user", content=question)],  # type: ignore[arg-type]
                    store=False,
                    timeout_ms=int(timeout_s * 1000),
                ),
                timeout=timeout_s + 5.0,
            )
        except (TimeoutError, MistralError, OSError) as error:
            last_error = error
            status = _status_of(error)
            retryable = status == 429 or (status is not None and status >= 500)
            if retryable and attempt < HTTP_ATTEMPTS - 1:
                await asyncio.sleep(2.0 * (2**attempt))
                continue
            raise
    raise RuntimeError("conversation retry loop ended unexpectedly") from last_error


async def create_agent(
    client: Mistral,
    *,
    name: str,
    model: str,
    instructions: str,
    connector: str,
    reasoning_effort: ReasoningEffortChoice,
) -> Agent:
    # The SDK's per-endpoint unions are invariant over list, so the one-tool and
    # one-entry lists meet their parameter as Any rather than as cast union members.
    tools: Any = [CustomConnector(connector_id=connector)]
    return await client.beta.agents.create_async(
        name=name,
        model=model,
        instructions=instructions,
        tools=tools,
        completion_args=CompletionArgs(reasoning_effort=reasoning_effort),
    )


# --------------------------------------------------------------------------- #
# Records and transcripts
# --------------------------------------------------------------------------- #


def consumer_name(model: str, reasoning_effort: str) -> str:
    return f"work-proxy-{model}-{reasoning_effort}"


def record_for(
    question: EvalQuestion,
    parsed: ParsedConversation,
    *,
    consumer: str,
    model: str,
    wall_seconds: float,
    transcript: str,
    error: str | None,
) -> ConsumerRecord:
    """One consumer record for one question, priced with the eval price table."""
    calls = tool_call_records(parsed.calls)
    cost = estimate_usd(
        model,
        TokenUsage(
            prompt_tokens=parsed.usage.input_tokens,
            completion_tokens=parsed.usage.output_tokens,
        ),
    )
    return ConsumerRecord(
        consumer=consumer,
        arm="A1",
        question_id=question.id,
        question_type=question.type.value,
        question=question.question,
        reference_answer=question.reference_answer,
        gold_urls=[gold.url for gold in question.gold],
        answer_text=parsed.answer_text,
        wall_seconds=wall_seconds,
        tokens=parsed.usage,
        harness_cost_usd=cost or 0.0,
        tool_calls=calls,
        mcp_called=any(is_server_tool(call.name) for call in calls),
        cite_called=any(is_verify_tool(call.name) for call in calls),
        links=extract_links(parsed.answer_text),
        transcript=transcript,
        error=error,
    )


def render_transcript(question: EvalQuestion, parsed: ParsedConversation, error: str | None) -> str:
    calls_note = (
        f"{question.type.value}, {connector_call_count(parsed)} connector calls"
        if parsed.raw_usage
        else question.type.value
    )
    lines = [
        f"# {question.id} ({calls_note})",
        "",
        "## Question",
        "",
        question.question,
        "",
    ]
    if parsed.thinking:
        lines += ["## Thinking", "", "\n\n".join(parsed.thinking), ""]
    if parsed.calls:
        lines += ["## Tool calls", ""]
        for index, call in enumerate(parsed.calls, 1):
            lines += [f"### {index}. {call.name}", "", "```json", call.arguments, "```", ""]
            if call.result:
                lines += ["Result:", "", "```", call.result, "```", ""]
            if call.failed:
                lines += ["> the tool reported an error", ""]
    lines += ["## Answer", "", parsed.answer_text or "(no answer text)", ""]
    if error:
        lines += [f"> conversation error: {error}", ""]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- #
# Run directory
# --------------------------------------------------------------------------- #


def resolve_run_directory(name: str, *, root: Path = RUNS_ROOT) -> Path:
    """The run directory, timestamp-prefixed, resumed by stem.

    Re-running the same ``--name`` continues the newest directory the stem
    already has, so a partial run keeps its records without the caller having
    to know the timestamp.
    """
    existing = sorted(root.glob(f"*-{name}"))
    if existing:
        return existing[-1]
    path = root / f"{datetime.now(UTC).strftime('%Y-%m-%d-%H%M')}-{name}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_config(run_dir: Path, config: Mapping[str, Any]) -> None:
    (run_dir / "config.json").write_text(json.dumps(dict(config), indent=2, sort_keys=True) + "\n")


def append_call(run_dir: Path, row: Mapping[str, Any]) -> None:
    """The conversation verbatim: one JSON object per question."""
    with (run_dir / "calls.jsonl").open("a") as handle:
        handle.write(json.dumps(dict(row), sort_keys=True, default=str) + "\n")


def write_transcript(run_dir: Path, question: EvalQuestion, body: str) -> str:
    target = run_dir / "transcripts" / f"{question.id}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body)
    return str(target.relative_to(run_dir))


def answered_ids(records: Sequence[ConsumerRecord]) -> set[str]:
    """The questions a run need not ask again. An error row is not an answer:
    a resumed run asks that question again and the fresh record replaces it."""
    return {record.question_id for record in records if not record.error}


def select_pending(questions: Sequence[EvalQuestion], done_ids: set[str]) -> list[EvalQuestion]:
    """The questions a resumed run still owes, in dataset order."""
    return [question for question in questions if question.id not in done_ids]


@dataclass(slots=True)
class WorkProxyConfig:
    name: str
    model: str
    reasoning_effort: ReasoningEffortChoice
    connector: str
    dataset: Path
    run_dir: Path
    timeout_s: float

    def as_dict(
        self,
        *,
        agent_id: str | None,
        question_count: int,
        connector_tools: list[str] | None = None,
        instructions: str | None = None,
    ) -> dict[str, Any]:
        consumer = consumer_name(self.model, self.reasoning_effort)
        return {
            "kind": "work_proxy_eval",
            "instructions": instructions,
            "name": self.name,
            "run_dir": str(self.run_dir),
            "consumer": consumer,
            "model": self.model,
            "reasoning_effort": self.reasoning_effort,
            "connector": self.connector,
            "connector_tools": connector_tools,
            "agent_id": agent_id,
            "dataset": str(self.dataset),
            "dataset_hash": dataset_hash(self.dataset),
            "question_count": question_count,
            # The consumer `score` README renderer reads these; on a single
            # arbitrary dataset every question counts as mined.
            "mined_count": question_count,
            "fresh_count": 0,
            "consumers": [consumer],
            "timeout_s": self.timeout_s,
            "judge_model": None,
        }


# --------------------------------------------------------------------------- #
# Collection
# --------------------------------------------------------------------------- #


async def ask_and_record(
    client: Mistral,
    agent_id: str,
    question: EvalQuestion,
    *,
    config: WorkProxyConfig,
    append_lock: asyncio.Lock,
) -> ConsumerRecord:
    """One question: conversation, ledger row, transcript, record."""
    consumer = consumer_name(config.model, config.reasoning_effort)
    started = time.perf_counter()
    response: ConversationResponse | None = None
    error: str | None = None
    try:
        response = await start_conversation(
            client, agent_id=agent_id, question=question.question, timeout_s=config.timeout_s
        )
    except Exception as caught:
        # One failed question is an error row; the run keeps its questions.
        error = f"{type(caught).__name__}: {caught}"[:400]
    wall_seconds = time.perf_counter() - started
    parsed = ParsedConversation()
    if response is not None:
        parsed = parse_conversation_response(response.model_dump(mode="json"))
    async with append_lock:
        row: dict[str, Any] = {"question_id": question.id, "wall_seconds": wall_seconds}
        if response is not None:
            row["response"] = response.model_dump(mode="json")
        else:
            row["error"] = error
        append_call(config.run_dir, row)
        transcript = write_transcript(
            config.run_dir, question, render_transcript(question, parsed, error)
        )
        record = record_for(
            question,
            parsed,
            consumer=consumer,
            model=config.model,
            wall_seconds=wall_seconds,
            transcript=transcript,
            error=error,
        )
        append_record(config.run_dir / "records.jsonl", record)
    logger.info(
        "Work proxy question done",
        question_id=question.id,
        error=error,
        run=str(config.run_dir),
    )
    return record


def _mark_agent_deletion(run_dir: Path, deletion: str) -> None:
    path = run_dir / "config.json"
    if not path.is_file():
        return
    config = json.loads(path.read_text())
    config["agent_deletion"] = deletion
    write_config(run_dir, config)


async def run_work_proxy(
    questions: Sequence[EvalQuestion],
    *,
    config: WorkProxyConfig,
    concurrency: int = DEFAULT_CONCURRENCY,
    client: Mistral | None = None,
) -> list[ConsumerRecord]:
    """Every pending question through one proxy agent, resumable by question id."""
    api_client = client or Mistral(api_key=_api_key())
    records = load_records(config.run_dir / "records.jsonl")
    done_ids = answered_ids(records)
    pending = select_pending(questions, done_ids)
    logger.info(
        "Work proxy collection",
        pending=len(pending),
        recorded=len(done_ids),
        run=str(config.run_dir),
    )
    if not pending:
        return []
    agent_id: str | None = None
    semaphore = asyncio.Semaphore(concurrency)
    append_lock = asyncio.Lock()
    try:
        # A wrong connector id does not fail the conversations: they come back
        # toolless and plausible, so the id is proven before anything runs.
        connector_tools = await api_client.beta.connectors.list_tools_async(
            connector_id_or_name=config.connector
        )
        if not connector_tools:
            raise SystemExit(f"connector {config.connector!r} exposes no tools")
        instructions = agent_instructions()
        agent = await create_agent(
            api_client,
            name=f"glossator-work-proxy-{config.name}",
            model=config.model,
            instructions=instructions,
            connector=config.connector,
            reasoning_effort=config.reasoning_effort,
        )
        agent_id = agent.id
        write_config(
            config.run_dir,
            config.as_dict(
                agent_id=agent_id,
                question_count=len(questions),
                connector_tools=[
                    tool.name if not isinstance(tool, dict) else str(tool.get("name", ""))
                    for tool in connector_tools
                ],
                instructions=instructions,
            ),
        )
        (config.run_dir / "questions.jsonl").write_text(
            "".join(question.model_dump_json() + "\n" for question in questions)
        )

        async def one(question: EvalQuestion) -> ConsumerRecord:
            async with semaphore:
                return await ask_and_record(
                    api_client, agent_id or "", question, config=config, append_lock=append_lock
                )

        return list(await asyncio.gather(*(one(question) for question in pending)))
    finally:
        if agent_id is not None:
            deletion = "deleted"
            try:
                await api_client.beta.agents.delete_async(agent_id=agent_id)
            except MistralError as caught:
                # The records are already on disk; a failed deletion leaves the
                # id in config.json so it can be removed by hand.
                deletion = f"delete failed: {caught}"[:400]
            _mark_agent_deletion(config.run_dir, deletion)


def _api_key() -> str:
    key = os.environ.get("MISTRAL_API_KEY")
    if not key:
        raise SystemExit("MISTRAL_API_KEY is not set; the Conversations API needs it")
    return key


# --------------------------------------------------------------------------- #
# README
# --------------------------------------------------------------------------- #


def agent_deletion_line(config: Mapping[str, Any]) -> str:
    deletion = str(config.get("agent_deletion") or "")
    if deletion in ("", "deleted"):
        return "- deleted after the run."
    return f"- agent deletion: {deletion}"


def render_readme(config: Mapping[str, Any], metrics: Mapping[str, Any]) -> str:
    """The run README in the shape of a consumer run's: protocol, cells, files."""
    lines = [
        "# Work proxy evaluation",
        "",
        "A Conversations-API agent stood in for a Mistral Work session: model",
        f"`{config['model']}` at `reasoning_effort: {config['reasoning_effort']}`, the",
        "mistral-docs Skill body plus the Work custom instructions as its",
        "instructions, and the `mistral_docs` Connector as its only tool. One",
        "unstored conversation per question; the consumer `judge` and `score`",
        "subcommands read this directory unchanged.",
        "",
        "## Protocol",
        "",
        f"- Questions: {config['question_count']} rows from `{config['dataset']}`"
        f" (sha256 {config['dataset_hash'][:12]}).",
        f"- Consumer: `{config['consumer']}` (arm A1), the same record shape as",
        "  the blind consumer runs, so the metrics are comparable.",
        f"- Agent: `{config.get('agent_id')}` on Connector `{config['connector']}`,",
        agent_deletion_line(config),
        f"- Timeout {float(config.get('timeout_s', QUESTION_TIMEOUT_S)):.0f} s per question;",
        "429 and 5xx retried with backoff; other failures are error rows.",
        "",
        "## Cells",
        "",
        "| cell | n | correctness | refusal | links resolve | on gold | mcp called "
        "| rerank asked | cite verified | tool calls | bad params | p50 s |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in sorted(metrics["cells"]):
        cell = metrics["cells"][name]
        lines.append(
            f"| {name} | {cell['n']} | {_fmt(cell.get('correctness'))} | "
            f"{_fmt(cell.get('refusal_correct'))} | {_fmt(cell.get('links_resolve'))} | "
            f"{_fmt(cell.get('links_on_gold'))} | {_fmt(cell.get('mcp_called'))} | "
            f"{_fmt(cell.get('rerank_asked'))} | {_fmt(cell.get('cite_verified'))} | "
            f"{_fmt(cell.get('tool_calls'))} | {_fmt(cell.get('bad_param_errors'))} | "
            f"{_fmt(cell.get('latency_p50'))} |"
        )
    lines += [
        "",
        "Correctness is the blind judge's 1 / 0.5 / 0 mean where judged, else `--`.",
        "Run `python -m glossator.eval.consumer judge --run <dir>` and then `score`",
        "to fill it in; `score` also writes `metrics.json`, `figures/`, `defects.md`",
        "and `samples.md` from the same records.",
        "",
        "## Files",
        "",
        "- `config.json`: the agent, model, effort, Connector and dataset behind",
        "  the run, with the agent id and its deletion outcome.",
        "- `questions.jsonl`: the question rows the run read.",
        "- `records.jsonl`: one consumer record per question, the same shape as",
        "  the blind consumer runs.",
        "- `calls.jsonl`: every conversation response verbatim, one JSON object",
        "  per question.",
        "- `transcripts/<question_id>.md`: question, thinking, tool calls with",
        "  arguments and results, and the answer.",
        "- `README.md`: this file.",
    ]
    return "\n".join(lines) + "\n"


def write_readme(run_dir: Path) -> None:
    config = json.loads((run_dir / "config.json").read_text())
    records = load_records(run_dir / "records.jsonl")
    metrics = aggregate(records, corpus_page_urls())
    (run_dir / "README.md").write_text(render_readme(config, metrics))


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Conversations-API work proxy over a question set"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run", help="Collect answers through the proxy agent")
    run_parser.add_argument("--dataset", type=Path, required=True)
    run_parser.add_argument("--name", required=True, help="Run stem; re-running it resumes")
    run_parser.add_argument("--model", default=DEFAULT_MODEL)
    run_parser.add_argument(
        "--reasoning-effort", choices=["high", "none"], default=DEFAULT_REASONING_EFFORT
    )
    run_parser.add_argument("--connector", default=DEFAULT_CONNECTOR, help="Connector name or UUID")
    run_parser.add_argument("--limit", type=int, help="How many questions to run")
    run_parser.add_argument("--ids", help="Comma-separated question ids to run")
    run_parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    run_parser.add_argument("--timeout", type=float, default=QUESTION_TIMEOUT_S)
    run_parser.add_argument("--runs-root", type=Path, default=RUNS_ROOT)

    readme_parser = sub.add_parser("readme", help="Re-render a run's README from its records")
    readme_parser.add_argument("--run", type=Path, required=True)
    return parser.parse_args(argv)


def _select_questions(
    dataset: Path, *, ids: Sequence[str], limit: int | None
) -> list[EvalQuestion]:
    questions = read_jsonl(dataset)
    if ids:
        wanted = set(ids)
        questions = [question for question in questions if question.id in wanted]
        missing = wanted - {question.id for question in questions}
        if missing:
            raise SystemExit(f"question ids not in {dataset}: {sorted(missing)}")
    if limit is not None:
        questions = questions[:limit]
    return questions


def merge_existing_config(run_dir: Path, fresh: dict[str, Any]) -> dict[str, Any]:
    """A re-run's config over the one already in the directory.

    A resume with nothing pending never reaches the agent, so the agent id and
    its deletion outcome of the run that collected the records would be
    overwritten with nulls; they are carried over instead. A different dataset
    in the same directory is refused, as the consumer runs refuse it.
    """
    path = run_dir / "config.json"
    if not path.is_file():
        return fresh
    existing = json.loads(path.read_text())
    if existing.get("dataset_hash") not in (None, fresh["dataset_hash"]):
        raise SystemExit("the run directory holds a different dataset; use a new --name")
    for key in ("agent_id", "agent_deletion", "judge_model", "judge_models"):
        if fresh.get(key) is None and existing.get(key) is not None:
            fresh[key] = existing[key]
    return fresh


async def _run(args: argparse.Namespace) -> None:
    questions = _select_questions(
        args.dataset,
        ids=[piece.strip() for piece in args.ids.split(",")] if args.ids else [],
        limit=args.limit,
    )
    if not questions:
        raise SystemExit("no questions selected")
    run_dir = resolve_run_directory(args.name, root=args.runs_root)
    config = WorkProxyConfig(
        name=args.name,
        model=args.model,
        reasoning_effort=args.reasoning_effort,
        connector=args.connector,
        dataset=args.dataset,
        run_dir=run_dir,
        timeout_s=args.timeout,
    )
    (run_dir / "records.jsonl").touch()
    (run_dir / "calls.jsonl").touch()
    write_config(
        run_dir,
        merge_existing_config(
            run_dir, config.as_dict(agent_id=None, question_count=len(questions))
        ),
    )
    try:
        await run_work_proxy(questions, config=config, concurrency=args.concurrency)
    finally:
        write_readme(run_dir)


def main() -> None:
    load_dotenv()
    args = _parse_args()
    if args.command == "run":
        asyncio.run(_run(args))
    elif args.command == "readme":
        write_readme(args.run)
    else:
        raise SystemExit(f"unknown command {args.command!r}")


if __name__ == "__main__":
    main()


__all__ = [
    "DEFAULT_CONNECTOR",
    "DEFAULT_MODEL",
    "DEFAULT_REASONING_EFFORT",
    "HTTP_ATTEMPTS",
    "ParsedConversation",
    "ParsedToolExecution",
    "WorkProxyConfig",
    "agent_instructions",
    "append_call",
    "connector_call_count",
    "consumer_name",
    "custom_instructions_block",
    "parse_conversation_response",
    "record_for",
    "render_readme",
    "render_transcript",
    "resolve_run_directory",
    "run_work_proxy",
    "select_pending",
    "skill_body",
    "strip_connector_prefix",
    "tool_call_records",
    "tool_execution_result",
    "write_readme",
]
