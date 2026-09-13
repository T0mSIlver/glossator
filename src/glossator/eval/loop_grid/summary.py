"""The summary directory: the grid's config, its comparison rows, and regeneration."""

from __future__ import annotations

import argparse
import contextlib
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from glossator.clients import chat_reasoning_effort, chat_server_url
from glossator.eval.answer_eval.models import JudgeModel
from glossator.eval.datasets import EvalQuestion, dataset_hash
from glossator.eval.loop_grid.models import AXIS_VALUES, SHIPPED_POINT, TABLE_COLUMNS
from glossator.eval.loop_grid.report import render_figures, render_readme


def grid_config(
    args: argparse.Namespace,
    rows: list[dict[str, Any]],
    *,
    questions: Sequence[EvalQuestion],
    judges: Sequence[JudgeModel],
) -> dict[str, Any]:
    return {
        "kind": "loop_grid",
        "name": args.name,
        "dataset": str(args.dataset),
        "dataset_sha256": dataset_hash(args.dataset),
        "questions": [question.id for question in questions],
        "model": args.model,
        "generation_server": chat_server_url(),
        "reasoning_effort": chat_reasoning_effort(),
        "judge_model": judges[0].identifier if judges else None,
        "judge_models": [judge.identifier for judge in judges],
        "variant": args.variant,
        "response_format": args.response_format,
        "shipped_point": dict(SHIPPED_POINT),
        "axes": {axis: [label for label, _value in values] for axis, values in AXIS_VALUES},
        "runs": rows,
        "notes": list(args.note or []),
    }


def summarize(
    run_dir: Path,
    config: dict[str, Any],
    *,
    failed_rows: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Read every row's run back and write the summary's four artefacts."""
    rows = [configuration_row(entry) for entry in config["runs"]]
    metrics: dict[str, Any] = {
        "kind": "loop_grid",
        "run_dir": str(run_dir),
        "name": config["name"],
        "dataset": config["dataset"],
        "dataset_sha256": config["dataset_sha256"],
        "questions": len(config.get("questions") or []),
        "model": config["model"],
        "generation_server": config.get("generation_server"),
        "reasoning_effort": config.get("reasoning_effort"),
        "judge_model": config.get("judge_model"),
        "judge_models": config.get("judge_models") or [],
        "variant": config["variant"],
        "response_format": config.get("response_format"),
        "shipped_point": config.get("shipped_point"),
        "configurations": rows,
        "failed_rows": list(failed_rows or []),
        "notes": config.get("notes") or [],
    }
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "figures").mkdir(exist_ok=True)
    (run_dir / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    (run_dir / "README.md").write_text(render_readme(config, metrics))
    render_figures(metrics, run_dir / "figures")
    return metrics


def configuration_row(entry: dict[str, Any]) -> dict[str, Any]:
    """One row of the comparison, read out of the row's own metrics.json."""
    run_path = Path(str(entry["run_dir"]))
    row: dict[str, Any] = {
        "name": entry["name"],
        "axis": entry.get("axis"),
        "value": entry.get("value"),
        "overrides": entry.get("overrides") or {},
        "run_dir": str(run_path),
        "status": "missing",
        "questions": None,
        "records": None,
        "errors": None,
        # Every column exists even when the row has no metrics to fill it, so a
        # reader of metrics.json never has to guard for a missing key.
        **{key: None for key, _caption, _kind in TABLE_COLUMNS},
    }
    with contextlib.suppress(FileNotFoundError, ValueError, KeyError):
        metrics = json.loads((run_path / "metrics.json").read_text())
        cell = metrics["by_strategy"]["search_loop"]["all"]
        row.update(
            {
                "status": metrics.get("status"),
                "questions": metrics.get("questions"),
                "records": metrics.get("records"),
                "errors": cell.get("errors"),
                **{key: cell.get(key) for key, _caption, _kind in TABLE_COLUMNS},
            }
        )
    return row


def regenerate(run_dir: Path) -> dict[str, Any]:
    """Rebuild the summary from its rows' own metrics (D-023: figures regenerable)."""
    config = json.loads((run_dir / "config.json").read_text())
    previous: dict[str, Any] = {}
    with contextlib.suppress(FileNotFoundError, ValueError):
        previous = json.loads((run_dir / "metrics.json").read_text())
    return summarize(run_dir, config, failed_rows=previous.get("failed_rows"))
