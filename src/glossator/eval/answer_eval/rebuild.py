"""Rebuilding a stored run's report, and repricing it at the current price table."""

from __future__ import annotations

import contextlib
import json
import os
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from glossator.answer.config import PRICES, aliased_price, price_of
from glossator.eval.answer_eval.run_dir import RunDirectory, read_records


def regenerate(run_dir: Path) -> dict[str, Any]:
    """Rebuild metrics.json, README.md and figures/ from the run's own rows."""
    config = json.loads((run_dir / "config.json").read_text())
    previous: dict[str, Any] = {}
    with contextlib.suppress(FileNotFoundError, ValueError):
        previous = json.loads((run_dir / "metrics.json").read_text())
    directory = RunDirectory(run_dir, config)
    directory.records = read_records(run_dir / "records.jsonl")
    return directory.finalize(
        status=previous.get("status", "complete"), error=previous.get("error")
    )


def _cost_from_row(row: Mapping[str, Any]) -> float:
    """The current price of one recorded call or record; 0 for an unpriced model.

    Unpriced models are not silently absorbed: ``recost`` lists every one it met
    in the run's ``config.json`` under ``unpriced_models``.
    """
    usage = row.get("usage")
    if not isinstance(usage, Mapping):
        return 0.0
    return (
        price_of(
            str(row.get("model") or ""),
            int(usage.get("prompt_tokens") or 0),
            int(usage.get("completion_tokens") or 0),
        )
        or 0.0
    )


def _write_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    temporary = path.with_suffix(f".{os.getpid()}.tmp")
    temporary.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))
    temporary.replace(path)


def recost(run_dir: Path) -> dict[str, Any]:
    """Apply current prices to every call and answer record in an existing run."""
    records_path = run_dir / "records.jsonl"
    calls_path = run_dir / "calls.jsonl"
    config_path = run_dir / "config.json"
    if not records_path.is_file() or not calls_path.is_file() or not config_path.is_file():
        raise ValueError(f"run lacks answer-evaluation files: {run_dir}")

    call_rows = [json.loads(line) for line in calls_path.read_text().splitlines() if line.strip()]
    scoped_costs: dict[tuple[str, str], float] = {}
    for row in call_rows:
        if "cost_usd" in row and row.get("cost_usd_v1") is None:
            row["cost_usd_v1"] = row["cost_usd"]
        row["cost_usd"] = _cost_from_row(row)
        question_id = row.get("question_id")
        strategy = row.get("strategy")
        if row.get("source") == "answer" and question_id and strategy:
            key = (str(question_id), str(strategy))
            scoped_costs[key] = scoped_costs.get(key, 0.0) + float(row["cost_usd"])

    record_rows = [
        json.loads(line) for line in records_path.read_text().splitlines() if line.strip()
    ]
    for row in record_rows:
        if row.get("cost_usd_v1") is None:
            row["cost_usd_v1"] = row.get("cost_usd", 0.0)
        key = (str(row.get("question_id") or ""), str(row.get("strategy") or ""))
        row["cost_usd"] = scoped_costs.get(key, _cost_from_row(row))

    config = json.loads(config_path.read_text())
    answer_config = dict(config.get("answer_config") or {})
    answer_config["prices"] = {
        model: price.model_dump(mode="json") for model, price in PRICES.items()
    }
    config["answer_config"] = answer_config
    config["unpriced_models"] = sorted(
        {
            str(row.get("model"))
            for row in [*call_rows, *record_rows]
            if row.get("model")
            and str(row.get("model")) not in PRICES
            and aliased_price(str(row.get("model"))) is None
        }
    )

    _write_jsonl(calls_path, call_rows)
    _write_jsonl(records_path, record_rows)
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    metrics = regenerate(run_dir)
    return {
        "run_dir": str(run_dir),
        "calls": len(call_rows),
        "records": len(record_rows),
        "usd_total": metrics["totals"]["usd_total"],
    }
