"""The run README, in the shape of a consumer run's."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from glossator.eval.consumer.links import corpus_page_urls
from glossator.eval.consumer.metrics import aggregate
from glossator.eval.consumer.models import ConsumerRecord, load_records
from glossator.eval.consumer.report import cells_table
from glossator.eval.work_proxy.models import QUESTION_TIMEOUT_S


def agent_deletion_line(config: Mapping[str, Any]) -> str:
    deletion = str(config.get("agent_deletion") or "")
    if deletion in ("", "deleted"):
        return "- deleted after the run."
    return f"- agent deletion: {deletion}"


def size_metrics(records: Sequence[ConsumerRecord]) -> dict[str, float]:
    """What a question costs in context: tokens per question and characters per
    tool result, the two numbers D-050 contains."""
    answered = [record for record in records if not record.error]
    calls = [call for record in answered for call in record.tool_calls]
    input_tokens = sorted(record.tokens.input_tokens for record in answered)
    result_chars = [call.output_chars for call in calls]
    if not answered:
        return {}
    return {
        "questions": len(answered),
        "input_tokens_mean": sum(input_tokens) / len(input_tokens),
        "input_tokens_p50": input_tokens[len(input_tokens) // 2],
        "output_tokens_mean": sum(record.tokens.output_tokens for record in answered)
        / len(answered),
        "tool_results": len(calls),
        "result_chars_mean": (sum(result_chars) / len(result_chars)) if result_chars else 0.0,
        "result_chars_per_question": sum(result_chars) / len(answered),
    }


def render_readme(
    config: Mapping[str, Any],
    metrics: Mapping[str, Any],
    size: Mapping[str, float] | None = None,
) -> str:
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
        *cells_table(metrics),
    ]
    if size:
        lines += [
            "",
            "## Size",
            "",
            "| questions | input tokens / question (mean) | (p50) | output tokens / question "
            "| tool results | chars / tool result | chars / question |",
            "|---:|---:|---:|---:|---:|---:|---:|",
            f"| {size['questions']:.0f} | {size['input_tokens_mean']:,.0f} | "
            f"{size['input_tokens_p50']:,.0f} | {size['output_tokens_mean']:,.0f} | "
            f"{size['tool_results']:.0f} | {size['result_chars_mean']:,.0f} | "
            f"{size['result_chars_per_question']:,.0f} |",
            "",
            "Input tokens include the Connector's tool results as the API counts them;",
            "characters are what the tools printed, before tokenization.",
        ]
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
    (run_dir / "README.md").write_text(render_readme(config, metrics, size_metrics(records)))
