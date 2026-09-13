"""The run directory: where it lives and how a second consumer's config joins it."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

RUNS_ROOT = Path("eval/runs")

QUARANTINE_FILE = "records-a2-set-aside.jsonl"
"""Answer-arm rows the run does not report: collected while the server could
not reach its model, or against a model the run has since replaced. They stay
on disk, out of the metrics, so the arm can be collected again without
pretending either happened."""


def resolve_run_directory(name: str, *, root: Path = RUNS_ROOT) -> Path:
    path = root / name
    path.mkdir(parents=True, exist_ok=True)
    return path


MERGED_KEYS = (
    "notes",
    "consumers",
    "consumer_models",
    "consumer_harnesses",
    "consumer_variants",
    "arms",
    "arm_tools",
    "mcp_urls",
)


def merge_config(existing: Mapping[str, Any], fresh: Mapping[str, Any]) -> dict[str, Any]:
    """The config of a run a second consumer is being added to.

    Consumers run one command each, often days apart and on different quota
    windows, into the same run directory. Writing the newest command's config
    over the old one left the run describing one consumer while its records
    held several, so the consumer and arm keys are unions and everything else
    is the newest command's.
    """
    if not existing:
        return dict(fresh)
    if existing.get("questions") != fresh.get("questions"):
        raise SystemExit(
            "the run directory holds a different question set; use a new --name "
            "or the same --mined/--fresh counts"
        )
    merged = dict(fresh)
    for key in MERGED_KEYS:
        before, after = existing.get(key), fresh.get(key)
        if isinstance(before, list) and isinstance(after, list):
            merged[key] = before + [item for item in after if item not in before]
        elif isinstance(before, dict) and isinstance(after, dict):
            merged[key] = {**before, **after}
    for key in ("judge_model", "judge_models"):
        if existing.get(key) and not fresh.get(key):
            merged[key] = existing[key]
    return merged
