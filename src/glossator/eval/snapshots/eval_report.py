"""The snapshot evaluation's scores, figure and README, computed from its rows."""

from __future__ import annotations

import json
import statistics
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from glossator.corpus.snapshots import SnapshotRecord
from glossator.eval.datasets import dataset_hash


def score_snapshot_records(
    records: Sequence[Mapping[str, Any]], snapshots: Sequence[SnapshotRecord]
) -> dict[str, Any]:
    """Correctness on present cells and refusal on absent cells, per snapshot.

    Rows without a judge verdict (a run with ``--skip-judge``) contribute their
    cell counts but no score: correctness and refusal stay ``None`` until judges
    fill them in.
    """
    per_snapshot: dict[str, Any] = {}
    for snapshot in snapshots:
        cells = [row for row in records if row["snapshot"] == snapshot.date]
        present = [
            row for row in cells if row["availability_label"] in {"present", "present_rephrased"}
        ]
        absent = [row for row in cells if row["availability_label"] == "absent"]
        correctness = []
        for row in present:
            verdict = (row.get("judge") or {}).get("verdict") or {}
            score = {"wrong": 0.0, "partial": 0.5, "correct": 1.0}.get(
                verdict.get("correctness", "")
            )
            if score is not None:
                correctness.append(score)
        refusal = [bool(row["insufficient_evidence"]) for row in absent]
        per_snapshot[snapshot.date] = {
            "present_cells": len(present),
            "absent_cells": len(absent),
            # Cells whose availability label is missing or still `unknown` score
            # in neither column. Counted rather than dropped: a table whose rows
            # do not add up to the cells that ran hides how much is unread.
            "unscored_cells": len(cells) - len(present) - len(absent),
            "correctness_present": statistics.fmean(correctness) if correctness else None,
            "refusal_rate_absent": statistics.fmean(refusal) if refusal else None,
        }
    return per_snapshot


def _eval_svg(metrics: Mapping[str, Any]) -> str:
    cells = list(metrics["per_snapshot"].items())
    points = []
    for index, (_date, cell) in enumerate(cells):
        value = cell["correctness_present"]
        if value is None:
            continue
        x = 65 + index * 105
        y = 340 - float(value) * 280
        points.append((x, y))
    polyline = " ".join(f"{x},{y:.1f}" for x, y in points)
    labels = "".join(
        f'<text x="{65 + index * 105}" y="370" text-anchor="middle" '
        f'font-family="sans-serif" font-size="11">{date[5:]}</text>'
        for index, (date, _cell) in enumerate(cells)
    )
    dots = "".join(f'<circle cx="{x}" cy="{y:.1f}" r="4" fill="#2b6cb0"/>' for x, y in points)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="400" '
        'viewBox="0 0 900 400"><rect width="100%" height="100%" fill="white"/>'
        '<text x="20" y="28" font-family="sans-serif" font-size="18">'
        "Correctness on present cells</text>"
        '<line x1="50" y1="340" x2="850" y2="340" stroke="#777"/>'
        '<line x1="50" y1="60" x2="50" y2="340" stroke="#777"/>'
        f'<polyline points="{polyline}" fill="none" stroke="#2b6cb0" stroke-width="2"/>'
        f"{dots}{labels}</svg>\n"
    )


def _eval_readme(metrics: Mapping[str, Any], dataset: Path, labels_path: Path) -> str:
    rows = []
    for date, cell in metrics["per_snapshot"].items():
        correctness = cell["correctness_present"]
        refusal = cell["refusal_rate_absent"]
        correctness_text = f"{correctness:.3f}" if correctness is not None else "--"
        refusal_text = f"{refusal:.3f}" if refusal is not None else "--"
        rows.append(
            f"| {date} | {cell['present_cells']} | {correctness_text} | "
            f"{cell['absent_cells']} | {refusal_text} | {cell.get('unscored_cells', 0)} |"
        )
    skipped = (
        "\nJudges were skipped for this run (`--skip-judge`): correctness and refusal "
        "are empty until a judged pass fills them in.\n"
        if metrics.get("judge_skipped")
        else ""
    )
    return f"""# Answer evaluation across snapshots

Each question ran once against each dated `snap1024` partition with the shipped
reranker. Generation used the recorded local server, never the Mistral API.
Correctness includes only cells labeled present or present with different
wording. Refusal includes only cells labeled absent. The `unscored` column counts
the cells whose availability label is missing or still pending the judged step;
they score in neither column.

- Dataset: `{dataset}`, sha256 `{dataset_hash(dataset)}`
- Availability labels: `{labels_path}`
{skipped}
| snapshot | present cells | correctness | absent cells | refusal rate | unscored |
|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

`changelog.jsonl` lists questions whose answer text changed between consecutive
snapshots. `figures/correctness.svg` is generated from `metrics.json`.
"""


def write_snapshot_outputs(
    run_path: Path,
    records: Sequence[Mapping[str, Any]],
    snapshots: Sequence[SnapshotRecord],
    dataset: Path,
    labels_path: Path,
    *,
    judge_skipped: bool,
) -> dict[str, Any]:
    """Metrics, README, figure and changelog, computed from the rows alone so a
    later judging pass rewrites them without touching the answers."""
    per_snapshot = score_snapshot_records(list(records), snapshots)
    metrics: dict[str, Any] = {
        "records": len(records),
        "per_snapshot": per_snapshot,
        "judge_skipped": judge_skipped,
    }
    by_question: dict[str, list[Mapping[str, Any]]] = {}
    for row in records:
        by_question.setdefault(str(row["question_id"]), []).append(row)
    changelog: list[dict[str, Any]] = []
    for question_id, question_rows in by_question.items():
        for before, after in zip(question_rows, question_rows[1:], strict=False):
            if before["answer_markdown"] == after["answer_markdown"]:
                continue
            changelog.append(
                {
                    "question_id": question_id,
                    "question": after["question"],
                    "from_snapshot": before["snapshot"],
                    "to_snapshot": after["snapshot"],
                    "before": before["answer_markdown"],
                    "after": after["answer_markdown"],
                }
            )
    metrics["changed_answers"] = len(changelog)
    (run_path / "figures").mkdir(parents=True, exist_ok=True)
    (run_path / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    (run_path / "changelog.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in changelog)
    )
    (run_path / "README.md").write_text(_eval_readme(metrics, dataset, labels_path))
    (run_path / "figures" / "correctness.svg").write_text(_eval_svg(metrics))
    return metrics
