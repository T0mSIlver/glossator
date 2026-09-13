"""The consumer run README, figures and side-by-side samples."""

from __future__ import annotations

import random
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from glossator.eval.answer_eval.prompts import JUDGE_VERSION
from glossator.eval.charts import bar_chart
from glossator.eval.consumer.consumers import ARMS
from glossator.eval.consumer.models import ConsumerRecord

# The per-cell metrics the README's table prints, in column order after `n`.
CELL_COLUMNS = (
    "correctness",
    "refusal_correct",
    "links_resolve",
    "links_on_gold",
    "mcp_called",
    "rerank_asked",
    "cite_verified",
    "tool_calls",
    "bad_param_errors",
    "latency_p50",
)


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


def cells_table(metrics: Mapping[str, Any]) -> list[str]:
    """One row per (consumer, arm) cell, shared by every run shaped like a consumer run."""
    lines = [
        "| cell | n | correctness | refusal | links resolve | on gold | mcp called "
        "| rerank asked | cite verified | tool calls | bad params | p50 s |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in sorted(metrics["cells"]):
        cell = metrics["cells"][name]
        values = " | ".join(format_number(cell.get(column)) for column in CELL_COLUMNS)
        lines.append(f"| {name} | {cell['n']} | {values} |")
    return lines


def render_readme(
    config: Mapping[str, Any],
    metrics: Mapping[str, Any],
    fragments: Mapping[str, Any],
    extra_files: Sequence[str] = (),
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
        *_notes_section(config),
        "## Cells",
        "",
        *cells_table(metrics),
        "",
        "Correctness is the blind judge's 1 / 0.5 / 0 mean where judged, else `--`.",
        "`rerank asked` is the share of cells where the consumer asked search to",
        "rerank: search ranks with the index alone otherwise, so the retrieval arm",
        "spends no generation except on those cells.",
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
        *extra_files,
    ]
    return "\n".join(lines) + "\n"


def _notes_section(config: Mapping[str, Any]) -> list[str]:
    """What a reader has to know about the machine the run reached.

    A run's cells are collected over hours, and the model behind the answer
    arm and the reranker can be swapped between them; the numbers only mean
    something next to the record of what was running when.
    """
    notes = [str(note) for note in config.get("notes") or []]
    if not notes:
        return []
    return ["## Notes", "", *[f"- {note}" for note in notes], ""]


def format_number(value: Any) -> str:
    if value is None:
        return "--"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


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
