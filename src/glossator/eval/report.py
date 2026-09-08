"""Rebuild a run's README and figures from its records.

D-023 asks for charts rendered by a script so they can be regenerated. Two kinds
of run write directories now -- dataset generation and answer evaluation -- and
`make eval-report run=<dir>` has to work on either without being told which, so
the run's own `config.json` names its kind and this module dispatches on it.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from glossator.eval import answer_eval
from glossator.eval.charts import bar_chart
from glossator.eval.run_records import regenerate

ANSWER_EVAL_KIND = "answer_eval"


def render_figures(metrics: Mapping[str, Any], figures_dir: Path) -> list[Path]:
    """Write a generation run's three charts. Returns the files written."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    candidates_by_type = dict(metrics.get("candidates_by_type") or {})
    kept_by_type = dict(metrics.get("kept_by_type") or {})
    accepted_rows: list[tuple[str, Sequence[float]]] = [
        (name, (float(kept_by_type.get(name, 0)), float(count - kept_by_type.get(name, 0))))
        for name, count in sorted(candidates_by_type.items())
    ]
    reasons = dict(metrics.get("dropped_by_reason") or {})
    reason_rows: list[tuple[str, Sequence[float]]] = [
        (name, (float(count),))
        for name, count in sorted(reasons.items(), key=lambda item: (-item[1], item[0]))
    ]
    usage_by_kind = dict(metrics.get("usage_by_kind") or {})
    token_rows: list[tuple[str, Sequence[float]]] = [
        (name, (float(usage["prompt_tokens"]), float(usage["completion_tokens"])))
        for name, usage in sorted(usage_by_kind.items())
    ]

    written = []
    for name, title, rows, series in (
        (
            "accepted-by-type.svg",
            "Candidates accepted and dropped, by question type",
            accepted_rows,
            ("accepted", "dropped"),
        ),
        ("drop-reasons.svg", "Dropped candidates by reason", reason_rows, ("candidates",)),
        ("tokens-by-call-kind.svg", "Tokens by call kind", token_rows, ("prompt", "completion")),
    ):
        path = figures_dir / name
        path.write_text(bar_chart(title, rows, series))
        written.append(path)
    return written


def run_kind(run_dir: Path) -> str:
    """What kind of run wrote this directory, from its own configuration."""
    config = json.loads((run_dir / "config.json").read_text())
    return str(config.get("kind", "generate"))


def rebuild(run_dir: Path) -> dict[str, Any]:
    """Regenerate metrics.json, README.md and figures/ for one run directory."""
    if run_kind(run_dir) == ANSWER_EVAL_KIND:
        return answer_eval.regenerate(run_dir)
    metrics = regenerate(run_dir)
    render_figures(metrics, run_dir / "figures")
    return metrics


def _summary(run_dir: Path, metrics: Mapping[str, Any]) -> dict[str, Any]:
    figures = sorted(path.name for path in (run_dir / "figures").glob("*.svg"))
    if metrics.get("kind") == ANSWER_EVAL_KIND:
        return {
            "run_dir": str(run_dir),
            "records": metrics["records"],
            "questions": metrics["questions"],
            "figures": figures,
        }
    return {
        "run_dir": str(run_dir),
        "kept": metrics["kept"],
        "candidates": metrics["candidates"],
        "figures": figures,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Regenerate a run's README and figures from its records"
    )
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(_summary(args.run_dir, rebuild(args.run_dir))))


if __name__ == "__main__":
    main()
