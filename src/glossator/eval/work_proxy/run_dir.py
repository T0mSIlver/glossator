"""The run directory: config, call ledger, transcripts, and what a resume still owes."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from glossator.eval.consumer.models import ConsumerRecord
from glossator.eval.consumer.run_dir import RUNS_ROOT
from glossator.eval.datasets import EvalQuestion


def resolve_run_directory(name: str, *, root: Path = RUNS_ROOT) -> Path:
    """The run directory, timestamp-prefixed, resumed by stem.

    Re-running the same ``--name`` continues the newest directory the stem
    already has, so a partial run keeps its records without the caller having
    to know the timestamp.
    """
    existing = sorted(root.glob(f"*-{name}"))
    if existing:
        return existing[-1]
    path = root / f"{datetime.now(UTC).strftime('%Y-%m-%d-%H%M')}-{name}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_config(run_dir: Path, config: Mapping[str, Any]) -> None:
    (run_dir / "config.json").write_text(json.dumps(dict(config), indent=2, sort_keys=True) + "\n")


def append_call(run_dir: Path, row: Mapping[str, Any]) -> None:
    """The conversation verbatim: one JSON object per question."""
    with (run_dir / "calls.jsonl").open("a") as handle:
        handle.write(json.dumps(dict(row), sort_keys=True, default=str) + "\n")


def write_transcript(run_dir: Path, question: EvalQuestion, body: str) -> str:
    target = run_dir / "transcripts" / f"{question.id}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body)
    return str(target.relative_to(run_dir))


def answered_ids(records: Sequence[ConsumerRecord]) -> set[str]:
    """The questions a run need not ask again. An error row is not an answer:
    a resumed run asks that question again and the fresh record replaces it."""
    return {record.question_id for record in records if not record.error}


def select_pending(questions: Sequence[EvalQuestion], done_ids: set[str]) -> list[EvalQuestion]:
    """The questions a resumed run still owes, in dataset order."""
    return [question for question in questions if question.id not in done_ids]


def merge_existing_config(run_dir: Path, fresh: dict[str, Any]) -> dict[str, Any]:
    """A re-run's config over the one already in the directory.

    A resume with nothing pending never reaches the agent, so the agent id and
    its deletion outcome of the run that collected the records would be
    overwritten with nulls; they are carried over instead. A different dataset
    in the same directory is refused, as the consumer runs refuse it.
    """
    path = run_dir / "config.json"
    if not path.is_file():
        return fresh
    existing = json.loads(path.read_text())
    if existing.get("dataset_hash") not in (None, fresh["dataset_hash"]):
        raise SystemExit("the run directory holds a different dataset; use a new --name")
    for key in ("agent_id", "agent_deletion", "judge_model", "judge_models"):
        if fresh.get(key) is None and existing.get(key) is not None:
            fresh[key] = existing[key]
    return fresh
