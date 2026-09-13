"""The analysis run directory: written once, and rebuilt from its own rows."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from glossator.eval.failures.aggregate import aggregate, breakdown, grouped
from glossator.eval.failures.models import AnalysedRun, FailureRecord, SkippedRun
from glossator.eval.failures.report import render_figures, render_readme
from glossator.eval.run_records.models import RUN_NAME_RE

RUNS_ROOT = Path("eval/runs")


def resolve_run_directory(name: str, *, root: Path = RUNS_ROOT) -> Path:
    """A fresh directory named for the moment the analysis ran, in UTC."""
    safe_name = RUN_NAME_RE.sub("-", name.casefold()).strip("-")
    if not safe_name:
        raise ValueError("run name must contain a letter or digit")
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d-%H%M")
    candidate = root / f"{timestamp}-{safe_name}"
    suffix = 2
    while candidate.exists():
        candidate = root / f"{timestamp}-{safe_name}-{suffix}"
        suffix += 1
    return candidate


def write_run(
    run_dir: Path,
    runs: Sequence[AnalysedRun],
    skipped: Sequence[SkippedRun],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    """Write config, records, metrics, README and figures (D-023)."""
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "figures").mkdir(exist_ok=True)
    (run_dir / "config.json").write_text(json.dumps(dict(config), indent=2, sort_keys=True) + "\n")
    rows = [failure for run in runs for failure in run.failures]
    (run_dir / "records.jsonl").write_text(
        "".join(
            json.dumps(failure.model_dump(mode="json"), sort_keys=True) + "\n" for failure in rows
        )
    )
    metrics = aggregate(runs, skipped, config)
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    (run_dir / "README.md").write_text(render_readme(config, metrics, rows))
    render_figures(metrics, run_dir / "figures")
    return metrics


def regenerate(run_dir: Path) -> dict[str, Any]:
    """Rebuild metrics, README and figures from this run's own records.

    The rows are the record, so the analysis is not re-run: a README regenerated
    a month later says exactly what the rows say, which is the point of D-023.
    """
    config = json.loads((run_dir / "config.json").read_text())
    previous = json.loads((run_dir / "metrics.json").read_text())
    rows = [
        FailureRecord.model_validate_json(line)
        for line in (run_dir / "records.jsonl").read_text().splitlines()
        if line.strip()
    ]
    metrics = dict(previous)
    metrics["by_run"] = _rebuild_by_run(previous, rows)
    metrics["totals"] = {
        **previous["totals"],
        **breakdown(rows, int(previous["totals"]["answers"])),
    }
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    (run_dir / "README.md").write_text(render_readme(config, metrics, rows))
    render_figures(metrics, run_dir / "figures")
    return metrics


def _rebuild_by_run(previous: Mapping[str, Any], rows: Sequence[FailureRecord]) -> dict[str, Any]:
    """Recount every class from the rows, keeping the per-run facts that are not counts.

    The answer counts are the only thing the rows cannot supply, so they are read
    back out of the stored metrics and everything else is recomputed.
    """
    by_run: dict[str, Any] = {}
    for name, run in previous["by_run"].items():
        failures = [row for row in rows if row.run == name]
        by_run[name] = {
            **run,
            **breakdown(failures, int(run["answers"])),
            "by_strategy": grouped(failures, _answers_of(run["by_strategy"]), "strategy"),
            "by_question_type": grouped(
                failures, _answers_of(run["by_question_type"]), "question_type"
            ),
        }
    return by_run


def _answers_of(groups: Mapping[str, Mapping[str, Any]]) -> dict[str, int]:
    return {name: int(group["answers"]) for name, group in groups.items()}
