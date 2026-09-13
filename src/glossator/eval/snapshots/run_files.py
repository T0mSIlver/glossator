"""Run directories and the built snapshots both the labeller and the evaluation read."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from glossator.corpus.snapshots import SnapshotRecord, read_snapshot_manifest
from glossator.eval.answer_eval.run_dir import resolve_run_directory

RUNS_ROOT = Path("eval/runs")


def built_snapshots(path: Path) -> list[SnapshotRecord]:
    return [row for row in read_snapshot_manifest(path) if row.status == "built"]


def run_path_for(name: str, root: Path = RUNS_ROOT) -> Path:
    return resolve_run_directory(name, root=root)


def append_row(path: Path, row: Mapping[str, Any]) -> None:
    with path.open("a") as handle:
        handle.write(json.dumps(dict(row), sort_keys=True) + "\n")
