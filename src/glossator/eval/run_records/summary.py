"""The run's metrics, computed from its rows, and the files rebuilt from them."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from glossator.eval.pricing import estimate_usd
from glossator.eval.providers.models import TokenUsage
from glossator.eval.run_records.models import STATUS_IN_PROGRESS
from glossator.eval.run_records.readme import render_readme


def summarize(
    call_rows: Sequence[Mapping[str, Any]],
    record_rows: Sequence[Mapping[str, Any]],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    """Every number the README and the figures are built from."""
    candidate_types = Counter(row.get("generator_type", "row") for row in record_rows)
    kept_types = Counter(row.get("generator_type", "row") for row in record_rows if row["kept"])
    dropped_reasons: Counter[str] = Counter()
    for row in record_rows:
        if not row["kept"]:
            dropped_reasons.update(row["drop_reasons"])

    usage = TokenUsage()
    uncached_usage = TokenUsage()
    by_kind: dict[str, TokenUsage] = defaultdict(TokenUsage)
    calls_by_kind: Counter[str] = Counter()
    finish_reasons: Counter[str] = Counter()
    failed_calls = 0
    for row in call_rows:
        call_usage = TokenUsage.model_validate(row["usage"])
        usage = usage.plus(call_usage)
        kind = str(row.get("call_kind") or "other")
        calls_by_kind[kind] += 1
        by_kind[kind] = by_kind[kind].plus(call_usage)
        if not row["cached"]:
            uncached_usage = uncached_usage.plus(call_usage)
        if row.get("finish_reason"):
            finish_reasons[str(row["finish_reason"])] += 1
        if row.get("error"):
            failed_calls += 1

    model = str(config.get("model", ""))
    requested = dict(config.get("requested_by_type") or {})
    shortfalls = dict(config.get("shortfalls") or {})
    return {
        "requested": int(config.get("n", 0)),
        "requested_by_type": requested,
        "shortfall_by_type": shortfalls,
        "shortfall": sum(shortfalls.values()),
        "candidates": len(record_rows),
        "kept": sum(bool(row["kept"]) for row in record_rows),
        "dropped": sum(not row["kept"] for row in record_rows),
        "candidates_by_type": dict(sorted(candidate_types.items())),
        "kept_by_type": dict(sorted(kept_types.items())),
        "dropped_by_reason": dict(sorted(dropped_reasons.items())),
        "calls": len(call_rows),
        "cached_calls": sum(bool(row["cached"]) for row in call_rows),
        "failed_calls": failed_calls,
        "calls_by_kind": dict(sorted(calls_by_kind.items())),
        "usage": usage.model_dump(mode="json"),
        "uncached_usage": uncached_usage.model_dump(mode="json"),
        "usage_by_kind": {kind: by_kind[kind].model_dump(mode="json") for kind in sorted(by_kind)},
        "finish_reasons": dict(sorted(finish_reasons.items())),
        "model": model,
        "estimated_usd": estimate_usd(model, uncached_usage),
        # Sum of per-call durations, not elapsed time: the calls run concurrently.
        "call_ms_total": round(sum(float(row.get("call_ms", 0.0)) for row in call_rows), 3),
    }


def write_summary(
    run_dir: Path,
    config: Mapping[str, Any],
    call_rows: Sequence[Mapping[str, Any]],
    record_rows: Sequence[Mapping[str, Any]],
    *,
    status: str,
    dataset: Path | str | None,
    error: str | None,
) -> dict[str, Any]:
    metrics = {
        "status": status,
        "error": error,
        "dataset": str(dataset) if dataset else None,
        **summarize(call_rows, record_rows, config),
    }
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    (run_dir / "README.md").write_text(render_readme(config, metrics))
    return metrics


def regenerate(run_dir: Path) -> dict[str, Any]:
    """Rebuild metrics.json and README.md from the recorded rows.

    Only the terminal status and the failure message cannot be derived from the
    rows; everything the README says about the run comes from the rows and the
    configuration, so a README can never drift from the records under it.
    """
    config = json.loads((run_dir / "config.json").read_text())
    previous = json.loads((run_dir / "metrics.json").read_text())
    call_rows = _read_jsonl(run_dir / "calls.jsonl")
    record_rows = _read_jsonl(run_dir / "records.jsonl")
    dataset = previous.get("dataset")
    (run_dir / "figures").mkdir(exist_ok=True)
    return write_summary(
        run_dir,
        config,
        call_rows,
        record_rows,
        status=previous.get("status", STATUS_IN_PROGRESS),
        dataset=dataset,
        error=previous.get("error"),
    )


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
