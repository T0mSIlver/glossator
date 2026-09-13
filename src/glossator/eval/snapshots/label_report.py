"""The labelling run's metrics, figure and README."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from glossator.corpus.snapshots import SnapshotRecord
from glossator.eval.agreement import agreement_report
from glossator.eval.datasets import dataset_hash
from glossator.eval.snapshots.models import PRIMARY_JUDGE, SECONDARY_JUDGE


def label_metrics(
    rows: Sequence[Mapping[str, Any]], snapshots: Sequence[SnapshotRecord]
) -> dict[str, Any]:
    per_snapshot: dict[str, Any] = {}
    for snapshot in snapshots:
        cells = [row for row in rows if row["snapshot"] == snapshot.date]
        counts = Counter(str(row["label"]) for row in cells)
        deterministic = sum(row["decided_by"] == "exact_span" for row in cells)
        per_snapshot[snapshot.date] = {
            "counts": dict(sorted(counts.items())),
            "cells": len(cells),
            "deterministic": deterministic,
            "deterministic_share": deterministic / len(cells) if cells else None,
        }
    judge_maps: dict[str, dict[tuple[str, str], Any]] = {PRIMARY_JUDGE: {}, SECONDARY_JUDGE: {}}
    mapped = {"stated": "correct", "different_value": "partial", "not_stated": "wrong"}
    for row in rows:
        for model, verdict in row.get("judges", {}).items():
            judge_maps[model][(str(row["question_id"]), str(row["snapshot"]))] = mapped[
                verdict["classification"]
            ]
    return {
        "cells": len(rows),
        "per_snapshot": per_snapshot,
        "deterministic_share": (
            sum(row["decided_by"] == "exact_span" for row in rows) / len(rows) if rows else None
        ),
        "agreement": agreement_report(judge_maps),
    }


def label_figure(metrics: Mapping[str, Any]) -> str:
    snapshots = list(metrics["per_snapshot"])
    width, height = 900, 420
    chart_height = 300
    bar_width = 70
    gap = 35
    maximum = max((cell["cells"] for cell in metrics["per_snapshot"].values()), default=1)
    colors = {"present": "#2f855a", "changed": "#d69e2e", "absent": "#c53030"}
    pending_color = "#a0aec0"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="20" y="28" font-family="sans-serif" font-size="18">'
        "Question availability by snapshot</text>",
    ]
    for index, date in enumerate(snapshots):
        x = 45 + index * (bar_width + gap)
        y = 345
        counts = metrics["per_snapshot"][date]["counts"]
        groups = {
            "present": counts.get("present", 0) + counts.get("present_rephrased", 0),
            "changed": counts.get("changed", 0),
            "absent": counts.get("absent", 0),
        }
        for label in ("present", "changed", "absent"):
            segment = chart_height * groups[label] / maximum
            y -= segment
            parts.append(
                f'<rect x="{x}" y="{y:.1f}" width="{bar_width}" '
                f'height="{segment:.1f}" fill="{colors[label]}"/>'
            )
        pending = counts.get("unknown", 0)
        if pending:
            segment = chart_height * pending / maximum
            y -= segment
            parts.append(
                f'<rect x="{x}" y="{y:.1f}" width="{bar_width}" '
                f'height="{segment:.1f}" fill="{pending_color}"/>'
            )
        parts.append(
            f'<text x="{x + bar_width / 2}" y="370" text-anchor="middle" '
            f'font-family="sans-serif" font-size="11">{date[5:]}</text>'
        )
    parts.extend(
        [
            '<rect x="620" y="20" width="12" height="12" fill="#2f855a"/>'
            '<text x="638" y="31" font-family="sans-serif" font-size="12">present</text>',
            '<rect x="700" y="20" width="12" height="12" fill="#d69e2e"/>'
            '<text x="718" y="31" font-family="sans-serif" font-size="12">changed</text>',
            '<rect x="790" y="20" width="12" height="12" fill="#c53030"/>'
            '<text x="808" y="31" font-family="sans-serif" font-size="12">absent</text>',
            "</svg>\n",
        ]
    )
    return "".join(parts)


def label_readme(metrics: Mapping[str, Any], datasets: Sequence[Path]) -> str:
    rows = []
    for date, cell in metrics["per_snapshot"].items():
        counts = cell["counts"]
        rows.append(
            f"| {date} | {counts.get('present', 0)} | {counts.get('present_rephrased', 0)} | "
            f"{counts.get('changed', 0)} | {counts.get('absent', 0)} | "
            f"{cell['deterministic_share']:.3f} |"
        )
    pair = (metrics.get("agreement", {}).get("pairwise") or [{}])[0]
    agreement = pair.get("percentage_agreement")
    kappa = pair.get("quadratic_weighted_kappa")
    dataset_lines = "\n".join(f"- `{path}`: `{dataset_hash(path)}`" for path in datasets)
    return f"""# Snapshot availability labels

A cell is `present` when a verified supporting quote occurs in that snapshot. A
match on another page is marked as moved. If no quote matches, GLM 5.3 and GLM
5.3 Flash compare the reference answer with the five highest-scoring lexical
pages. The primary judge assigns `present_rephrased`, `changed`, or `absent`.
Cells still waiting for that judged step are `unknown` (shown grey): a later run
without `--deterministic-only` judges exactly those cells and never re-decides
the rest.

Correctness can only be scored on present cells because an answer cannot be
correct when its fact is missing or has a different dated value. Absent cells
instead measure whether the answer refuses to invent a current-looking answer.

## Datasets

{dataset_lines}

## Counts

| snapshot | present | rephrased | changed | absent | deterministic share |
|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

The two judges agreed exactly on {agreement if agreement is not None else "no judged cells"};
quadratic-weighted kappa was {kappa if kappa is not None else "not defined"}.
The figure at `figures/availability.svg` combines exact and rephrased cells as present.
"""
