"""Markdown tables for the run README."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from glossator.eval.answer_eval.metrics import MEAN_METRICS

_DECIMALS: dict[str, int] = {
    **MEAN_METRICS,
    "citation_verification_rate": 2,
    "fabricated_per_answer": 2,
    "cosmetic_per_answer": 2,
    "latency_p50_s": 1,
    "latency_p95_s": 1,
}


def format_value(value: Any, metric: str) -> str:
    if value is None:
        return "--"
    if isinstance(value, float):
        return f"{value:.{_DECIMALS.get(metric, 2)}f}"
    return str(value)


def metric_table(metrics: Mapping[str, Any], metric: str) -> str:
    """One metric, strategies as rows and question types as columns.

    The generation model is a column of every table: this run and a re-run on
    Mistral Medium 3.5 will sit side by side in the same README one day, and a
    number without its model is not a number (D-017a).
    """
    types = list(metrics["question_types"])
    header = "| strategy | model | " + " | ".join(types) + " | all |"
    divider = "|---" * (len(types) + 3) + "|"
    lines = [header, divider]
    for strategy, cells in metrics["by_strategy"].items():
        values = [
            format_value(cells["by_type"][question_type].get(metric), metric)
            for question_type in types
        ]
        lines.append(
            f"| `{strategy}` | `{metrics['model']}` | "
            + " | ".join(values)
            + f" | **{format_value(cells['all'].get(metric), metric)}** |"
        )
    return "\n".join(lines)


def _agreement_section(metrics: Mapping[str, Any]) -> str:
    agreement = metrics.get("agreement") or {}
    pairwise = agreement.get("pairwise") or []
    kappa_rows = [
        "| first judge | second judge | answers | quadratic-weighted kappa | exact agreement |",
        "|---|---|---:|---:|---:|",
    ]
    for row in pairwise:
        kappa_rows.append(
            f"| `{row['first']}` | `{row['second']}` | {row['items']} | "
            f"{format_value(row['quadratic_weighted_kappa'], 'agreement')} | "
            f"{format_value(row['percentage_agreement'], 'agreement')} |"
        )
    if not pairwise:
        kappa_rows.append("| -- | -- | 0 | -- | -- |")

    alpha_rows = [
        "| raters | ordinal alpha | pairwise exact agreement |",
        "|---|---:|---:|",
        "| configured judges | "
        f"{format_value(agreement.get('krippendorff_alpha_ordinal'), 'agreement')} | "
        f"{format_value(agreement.get('percentage_agreement'), 'agreement')} |",
    ]
    human = agreement.get("human")
    if human:
        alpha_rows.append(
            f"| configured judges and human | "
            f"{format_value(human.get('krippendorff_alpha_ordinal'), 'agreement')} | "
            f"{format_value(human.get('percentage_agreement'), 'agreement')} |"
        )

    means = [
        "| judge | answers | mean correctness | human-labeled answers |",
        "|---|---:|---:|---:|",
    ]
    for name, row in (agreement.get("per_judge") or {}).items():
        means.append(
            f"| `{name}` | {row['items']} | {format_value(row['mean_correctness'], 'agreement')} | "
            f"{row.get('human_items', '--')} |"
        )

    human_section = ""
    if human:
        rows = [
            "| judge | answers | quadratic-weighted kappa | exact agreement |",
            "|---|---:|---:|---:|",
        ]
        for row in human.get("pairwise") or []:
            rows.append(
                f"| `{row['judge']}` | {row['items']} | "
                f"{format_value(row['quadratic_weighted_kappa'], 'agreement')} | "
                f"{format_value(row['percentage_agreement'], 'agreement')} |"
            )
        matrices = []
        for name, judge_row in (agreement.get("per_judge") or {}).items():
            matrix = judge_row.get("confusion_matrix_human_rows")
            if not matrix:
                continue
            matrix_rows = [
                "| human \\ judge | wrong | partial | correct |",
                "|---|---:|---:|---:|",
            ]
            for label in ("wrong", "partial", "correct"):
                matrix_rows.append(
                    f"| {label} | {matrix[label]['wrong']} | {matrix[label]['partial']} | "
                    f"{matrix[label]['correct']} |"
                )
            matrices.append(f"#### `{name}` confusion matrix\n\n" + "\n".join(matrix_rows))
        human_section = (
            "\n\n### Against human labels\n\n"
            + "\n".join(rows)
            + ("\n\n" + "\n\n".join(matrices) if matrices else "")
        )

    return (
        "## Agreement\n\n"
        "Correctness is ordinal: wrong is 0, partial is 0.5, and correct is 1. "
        "Kappa uses quadratic weights. Exact agreement requires the same label.\n\n"
        "### Judge pairs\n\n"
        + "\n".join(kappa_rows)
        + "\n\n### Krippendorff's alpha\n\n"
        + "\n".join(alpha_rows)
        + "\n\n### Judge means\n\n"
        + "\n".join(means)
        + human_section
    )
