"""The analysis README and its figure."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from glossator.eval.charts import stacked_bar_chart
from glossator.eval.failures.aggregate import ordered_runs
from glossator.eval.failures.classify import shorten
from glossator.eval.failures.models import CLASS_ORDER, CLASS_TITLES, DefectSignal, FailureRecord
from glossator.eval.failures.prompts import DEFECT_PROMPT_HASHES, DEFECT_VERSION
from glossator.eval.failures.rules import BLIND_SPOTS, RULES

EXAMPLES_PER_CLASS = 3
"""How many worked examples the README shows per class, per run."""


def render_figures(metrics: Mapping[str, Any], figures_dir: Path) -> list[Path]:
    """The one figure the README carries: what each run's failures are made of."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    rows: list[tuple[str, Sequence[float]]] = [
        (
            name,
            tuple(float(run["by_class"][failure_class.value]) for failure_class in CLASS_ORDER),
        )
        for name, run in ordered_runs(metrics)
    ]
    path = figures_dir / "failure-classes.svg"
    path.write_text(
        stacked_bar_chart(
            "Failures by class, per run",
            rows,
            [CLASS_TITLES[failure_class] for failure_class in CLASS_ORDER],
        )
    )
    return [path]


def _class_table(breakdowns: Mapping[str, Mapping[str, Any]], first_column: str) -> str:
    """A table of failure counts by class, with the share of all answers beside each."""
    header = (
        f"| {first_column} | answers | failures | "
        + " | ".join(CLASS_TITLES[failure_class] for failure_class in CLASS_ORDER)
        + " |"
    )
    divider = "|---" * (3 + len(CLASS_ORDER)) + "|"
    lines = [header, divider]
    for name, breakdown in breakdowns.items():
        answers = int(breakdown["answers"])
        cells = [
            f"{breakdown['by_class'][failure_class.value]} "
            f"({breakdown['by_class_share'][failure_class.value]:.0%})"
            for failure_class in CLASS_ORDER
        ]
        share = f"{breakdown['failure_share']:.0%}" if answers else "n/a"
        lines.append(
            f"| {name} | {answers} | {breakdown['failures']} ({share}) | "
            + " | ".join(cells)
            + " |"
        )
    return "\n".join(lines)


def _sub_label_table(breakdown: Mapping[str, Any]) -> str:
    lines = ["| class | sub-label | failures |", "|---|---|---|"]
    for failure_class in CLASS_ORDER:
        for sub, count in breakdown["sub_labels"][failure_class.value].items():
            if count:
                lines.append(f"| {CLASS_TITLES[failure_class]} | `{sub}` | {count} |")
    if len(lines) == 2:
        lines.append("| (none) | | 0 |")
    return "\n".join(lines)


def _examples(rows: Sequence[FailureRecord], run_name: str) -> str:
    """Up to three worked examples per class, one paragraph each."""
    blocks: list[str] = []
    for failure_class in CLASS_ORDER:
        chosen = _pick_examples(
            [row for row in rows if row.run == run_name and row.failure_class is failure_class]
        )
        if not chosen:
            blocks.append(f"**{CLASS_TITLES[failure_class]}** -- none in this run.")
            continue
        lines = [f"**{CLASS_TITLES[failure_class]}**", ""]
        for row in chosen:
            lines.append(
                f"- `{row.question_id}` ({row.question_type}, {row.strategy}, judged "
                f"{row.verdict or 'not judged'}, `{row.sub_label.value}`) --- "
                f'"{shorten(row.question, 160)}"'
            )
            lines.append(f"  - what happened: {row.evidence}")
            if row.judge_reason:
                lines.append(f"  - the judge: {row.judge_reason}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def _pick_examples(rows: Sequence[FailureRecord]) -> list[FailureRecord]:
    """One example of each sub-label first, then the rest, deterministically.

    Showing three failures that all say the same thing wastes the section; a
    reader wants the range the class covers.
    """
    ordered = sorted(rows, key=lambda row: (row.sub_label.value, row.question_id, row.strategy))
    chosen: list[FailureRecord] = []
    seen: set[str] = set()
    for row in ordered:
        if row.sub_label.value not in seen:
            chosen.append(row)
            seen.add(row.sub_label.value)
    for row in ordered:
        if len(chosen) >= EXAMPLES_PER_CLASS:
            break
        if row not in chosen:
            chosen.append(row)
    return chosen[:EXAMPLES_PER_CLASS]


def _run_section(name: str, run: Mapping[str, Any], rows: Sequence[FailureRecord]) -> str:
    resolved = run["chunk_ids_resolved"]
    recorded = run["chunk_ids_recorded"]
    coverage = (
        f"{resolved} of {recorded} recorded chunk ids resolved to a page through the corpus"
        if recorded
        else "the run recorded no chunk ids"
    )
    return f"""### `{name}`

Dataset `{run["dataset"]}`, generator `{run["model"]}`, index `{run["variant"]}`,
reranker {run["rerank"]}. {run["judged"]} of {run["answers"]} answers carry a primary
verdict ({run["unjudged"]} do not), {run["errors"]} ended in an error. {coverage}.

**By strategy**

{_class_table(run["by_strategy"], "strategy")}

**By question type**

{_class_table(run["by_question_type"], "question type")}

**Sub-labels**

{_sub_label_table(run)}

{_defect_line(run)}

**Examples**

{_examples(rows, name)}"""


def _defect_line(breakdown: Mapping[str, Any]) -> str:
    """The defect flag with the base rate that says what it is worth.

    The first signal fires on a judge reason that names the reference, and the
    judge prompt asks the judge to grade against the reference, so the same words
    appear in the reasons of answers that passed. Printing the flag without that
    comparison would read as a defect rate.
    """
    signals = breakdown["defect_signals"]
    passed = int(breakdown.get("passed_judged", 0))
    naming = int(breakdown.get("passed_naming_the_reference", 0))
    base = (
        f" For comparison, {naming} of the {passed} answers that passed carry the same "
        f"`{DefectSignal.JUDGE_NAMES_THE_REFERENCE.value}` wording "
        f"({naming / passed:.0%}), so that signal on its own separates nothing; "
        f"`{DefectSignal.HUMAN_IS_MORE_LENIENT.value}` is the discriminating one."
        if passed
        else ""
    )
    return (
        f"{breakdown['reference_defect_flagged']} of {breakdown['failures']} failures carry "
        f"the reference-defect flag: "
        + ", ".join(f"`{name}` {count}" for name, count in signals.items())
        + f" (a row can carry both).{base}"
    )


def render_readme(
    config: Mapping[str, Any], metrics: Mapping[str, Any], rows: Sequence[FailureRecord]
) -> str:
    """The run README (D-023). Every number in it comes from `records.jsonl`."""
    totals = metrics["totals"]
    skipped = metrics["skipped_runs"]
    skipped_lines = (
        "\n".join(f"- `{row['run_dir']}`: {row['reason']}" for row in skipped)
        if skipped
        else "- None: every directory named on the command line held answers."
    )
    judge_line = (
        f"The reference-defect judge ran on `{metrics['judge_model']}` and produced "
        f"{totals['defect_judgements']} judgement(s), one per flagged failure, "
        "all in `calls.jsonl`."
        if metrics.get("judge_model")
        else (
            "The reference-defect judge did not run: no `--judge-model` was given, so "
            "every reference-defect entry below is a flag raised by a deterministic "
            "signal and nothing more. Running it is one call per flagged failure and "
            "decides those flags."
        )
    )
    index_line = ", ".join(
        f"`{variant}` {count} chunks" for variant, count in metrics["chunk_index"].items()
    )
    run_sections = "\n\n".join(_run_section(name, run, rows) for name, run in ordered_runs(metrics))
    return f"""# Failure analysis: which part of the pipeline was wrong

**What this measures.** Not how often the pipeline fails --- the answer evaluations
already say that --- but *which part* failed each time. Every answer these runs
recorded that the judge scored `partial` or `wrong`, or that refused in the wrong
direction, is assigned one class: the retrieval never found the page, the context
never carried it, the model had it and still answered wrong, or the refusal went the
wrong way. A wrong answer with the right passage in front of the model and a wrong
answer whose page was never retrieved call for opposite work, and the generator here
is a small model (Ministral 3 14B, D-017a), which makes the split worth having before
anything is blamed on it.

No model was called to produce this run's classes. Every class is decided from the
records the answer evaluations already wrote, so it can be recomputed from
`records.jsonl` at any time.

## Configuration

- Runs analysed: {len(metrics["runs"])} --- {", ".join(f"`{name}`" for name in metrics["runs"])}
- Corpus: `{metrics["corpus"]}`; chunk map rebuilt offline: {index_line}
- Human labels: `{config.get("labels") or "none"}`
- Reference-defect judge: `{metrics.get("judge_model") or "not run"}` ({DEFECT_VERSION}, \
hashes {json.dumps(DEFECT_PROMPT_HASHES, sort_keys=True)})

Directories named but not analysed:

{skipped_lines}

## How each class is decided

{RULES}

## Known blind spots

{BLIND_SPOTS}

## Results

Across {len(metrics["runs"])} runs, {totals["failures"]} of {totals["answers"]} answers
failed ({totals["failure_share"]:.0%}). {totals["chunk_ids_resolved"]} of
{totals["chunk_ids_recorded"]} recorded chunk ids resolved to a page through the corpus;
an unresolved id is a chunk the current corpus no longer produces, and is counted on the
row it came from as `unresolved_chunks`.

{_class_table(dict(ordered_runs(metrics)), "run")}

{_defect_line(totals)} {judge_line}

{run_sections}

## Figures

`figures/` is regenerated from `metrics.json` by `make eval-report run={config.get("run_dir")}`.

- `failure-classes.svg`: what each run's failures are made of, one stacked bar per run

## Files

- `config.json` --- the runs analysed, the corpus, the labels, and the judge setting.
- `records.jsonl` --- one row per failed answer: its class, its sub-label, the evidence
  that decided the class, and every intermediate fact the decision used
  (`gold_retrieved`, `gold_in_context`, `gold_section_in_context`, `gold_chunk_dropped`,
  the retrieved pages, the defect signals). Every number in this README is a count over
  these rows.
- `metrics.json` --- every number in the tables above.

## What it feeds

D-016 (which checks the answer evaluation reports), D-034 and D-035 (whether the next
effort belongs in retrieval or in the answer layer) and D-021b (the reference-defect rate
the judge study reports beside its own numbers).
"""
