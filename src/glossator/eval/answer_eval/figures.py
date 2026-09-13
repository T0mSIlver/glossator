"""The charts the run README links, rendered from `metrics.json`."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from glossator.eval.answer_eval.metrics import REFERENCE_PRICING_MODEL
from glossator.eval.charts import bar_chart, scatter


def render_figures(metrics: Mapping[str, Any], figures_dir: Path) -> list[Path]:
    """The six charts the README links. Returns the files written."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    strategies = list(metrics["by_strategy"])

    def values(metric: str) -> list[tuple[str, tuple[float, ...]]]:
        return [
            (strategy, (float(metrics["by_strategy"][strategy]["all"].get(metric) or 0.0),))
            for strategy in strategies
        ]

    def pairs(*names: str) -> list[tuple[str, tuple[float, ...]]]:
        return [
            (
                strategy,
                tuple(
                    float(metrics["by_strategy"][strategy]["all"].get(name) or 0.0)
                    for name in names
                ),
            )
            for strategy in strategies
        ]

    written: list[Path] = []
    charts: tuple[tuple[str, str], ...] = (
        ("citation-match.svg", "citation"),
        ("verification-rate.svg", "verification"),
        ("correctness.svg", "correctness"),
        ("groundedness.svg", "groundedness"),
        ("cost-per-question.svg", "cost"),
    )
    bodies = {
        "citation": bar_chart(
            "Citations landing on a gold source",
            pairs("cited_url_match", "cited_anchor_match"),
            ("gold URL", "gold anchor"),
        ),
        "verification": bar_chart(
            "Citation verification",
            pairs("citation_verification_rate", "fabricated_per_answer", "cosmetic_per_answer"),
            ("verified rate", "fabricated/answer", "cosmetic/answer"),
        ),
        "correctness": bar_chart(
            "Judged correctness",
            pairs("correct", "partial", "wrong"),
            ("correct", "partial", "wrong"),
        ),
        "groundedness": bar_chart(
            "Groundedness and citation relevance",
            pairs("groundedness", "citation_relevance"),
            ("groundedness", "citation relevance"),
        ),
        "cost": bar_chart(
            f"USD per question at {REFERENCE_PRICING_MODEL} prices",
            values("reference_usd"),
            ("USD",),
        ),
    }
    for name, key in charts:
        path = figures_dir / name
        path.write_text(bodies[key])
        written.append(path)

    points = [
        (
            strategy,
            float(metrics["by_strategy"][strategy]["all"].get("latency_p50_s") or 0.0),
            float(metrics["by_strategy"][strategy]["all"].get("correctness") or 0.0),
        )
        for strategy in strategies
    ]
    scatter_path = figures_dir / "latency-vs-correctness.svg"
    scatter_path.write_text(
        scatter(
            "What the better answers cost in seconds",
            points,
            x_label="median seconds per answer",
            y_label="judged correctness",
        )
    )
    written.append(scatter_path)
    return written
