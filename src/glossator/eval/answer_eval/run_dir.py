"""One run's directory on disk: config, records, the call ledger and the rendered report."""

from __future__ import annotations

import contextlib
import json
import os
from collections.abc import Iterator, Mapping, Sequence
from contextvars import ContextVar
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from glossator.answer.llm import LLMCall
from glossator.eval.answer_eval.figures import render_figures
from glossator.eval.answer_eval.metrics import aggregate
from glossator.eval.answer_eval.models import QuestionRecord
from glossator.eval.answer_eval.report import render_readme
from glossator.eval.run_records import RUN_NAME_RE

RUNS_ROOT = Path("eval/runs")

_scope: ContextVar[tuple[str, str] | None] = ContextVar("answer_eval_scope", default=None)


@contextlib.contextmanager
def answer_scope(question_id: str, strategy: str) -> Iterator[None]:
    """Tag the answer layer's calls with the pair they were made for."""
    token = _scope.set((question_id, strategy))
    try:
        yield
    finally:
        _scope.reset(token)


class RunDirectory:
    """One run's files. Rows are appended as they are produced, so a run that is
    killed halfway still holds everything it paid for -- and is resumable."""

    def __init__(self, path: Path, config: dict[str, Any]) -> None:
        self.path = path
        self.config = config
        self.calls_path = path / "calls.jsonl"
        self.records_path = path / "records.jsonl"
        self.records: list[QuestionRecord] = []

    @classmethod
    def open(cls, path: Path, config: dict[str, Any]) -> RunDirectory:
        """Create the directory, or reopen one and read its records back.

        Resuming rewrites `config.json` from the command that resumed, except for
        the notes: those describe the run, and a resume typed without `--note`
        would otherwise silently delete the caveats the run was published with.
        """
        resumed = path.exists()
        (path / "figures").mkdir(parents=True, exist_ok=True)
        run = cls(path, config)
        if resumed and run.records_path.exists():
            run.records = read_records(run.records_path)
        if resumed and not run.config.get("notes"):
            with contextlib.suppress(FileNotFoundError, ValueError):
                stored = json.loads((path / "config.json").read_text())
                run.config["notes"] = stored.get("notes") or []
        run.calls_path.touch()
        run.records_path.touch()
        run.config["resumed_records"] = len(run.records)
        (path / "config.json").write_text(json.dumps(run.config, indent=2, sort_keys=True) + "\n")
        return run

    @property
    def done(self) -> set[tuple[str, str]]:
        return {record.key for record in self.records}

    def record(self, record: QuestionRecord) -> None:
        self.records.append(record)
        self._append(self.records_path, json.loads(record.model_dump_json()))

    def drop_error_records(self) -> int:
        """Remove the rows that ended in an error, so a resume regenerates them.

        Rows with an answer are the run's paid-for output and stay; the calls
        that failed stay in `calls.jsonl`, which is an append-only ledger.
        Rewritten from the stored lines rather than re-serialized models, so
        fields this model does not know about survive the rewrite.
        """
        lines = [line for line in self.records_path.read_text().splitlines() if line.strip()]
        kept_lines: list[str] = []
        kept: list[QuestionRecord] = []
        for line in lines:
            record = QuestionRecord.model_validate_json(line)
            if record.error is None:
                kept_lines.append(line)
                kept.append(record)
        dropped = len(lines) - len(kept_lines)
        if dropped:
            temporary = self.records_path.with_suffix(f".{os.getpid()}.tmp")
            with temporary.open("w") as handle:
                for line in kept_lines:
                    handle.write(line + "\n")
            temporary.replace(self.records_path)
            self.records = kept
        return dropped

    def replace_records(self, records: Sequence[QuestionRecord]) -> None:
        """Checkpoint judge fields without normalizing the stored answer or trace."""
        stored = [json.loads(line) for line in self.records_path.read_text().splitlines()]
        if len(stored) != len(records):
            raise ValueError("re-judge checkpoint changed the number of answer records")
        temporary = self.records_path.with_suffix(f".{os.getpid()}.tmp")
        with temporary.open("w") as handle:
            for row, record in zip(stored, records, strict=True):
                updated = record.model_dump(mode="json")
                for field in ("judge", "judges", "judges_v1"):
                    row[field] = updated[field]
                handle.write(json.dumps(row, sort_keys=True) + "\n")
        temporary.replace(self.records_path)
        self.records = list(records)

    def append_call(self, source: str, row: Mapping[str, Any]) -> None:
        """One line in `calls.jsonl`, tagged with which client made the call."""
        self._append(self.calls_path, {"source": source, **row})

    def finalize(self, *, status: str, error: str | None) -> dict[str, Any]:
        metrics = aggregate(self.records, self.config)
        metrics["status"] = status
        metrics["error"] = error
        (self.path / "metrics.json").write_text(
            json.dumps(metrics, indent=2, sort_keys=True) + "\n"
        )
        (self.path / "README.md").write_text(render_readme(self.config, metrics))
        render_figures(metrics, self.path / "figures")
        return metrics

    @staticmethod
    def _append(path: Path, row: Mapping[str, Any]) -> None:
        with path.open("a") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


class AnswerCallRecorder:
    """The answer layer's `CallRecorder`, writing into the run's `calls.jsonl`.

    The two client libraries record different shapes, and flattening one into the
    other would lose fields that only one of them has (tool calls on one side,
    thinking mode and cache hits on the other). Both go into the same file with a
    `source` tag instead, so the file stays the run's whole call ledger (D-023).
    """

    def __init__(self, run_dir: RunDirectory) -> None:
        self.run_dir = run_dir

    def record(self, call: LLMCall) -> None:
        scope = _scope.get()
        self.run_dir.append_call(
            "answer",
            {
                "question_id": scope[0] if scope else None,
                "strategy": scope[1] if scope else None,
                **json.loads(call.model_dump_json()),
            },
        )


class JudgeCallRecorder:
    """The provider's `CallRecorder`, writing into the same `calls.jsonl`."""

    def __init__(self, run_dir: RunDirectory) -> None:
        self.run_dir = run_dir

    def record_call(self, **row: Any) -> None:
        self.run_dir.append_call(
            "judge", {"timestamp": datetime.now(UTC).isoformat(), **_jsonable(row)}
        )


def _jsonable(row: Mapping[str, Any]) -> dict[str, Any]:
    """The provider hands over pydantic models and sequences; JSON wants neither."""
    out: dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, BaseModel):
            out[key] = value.model_dump(mode="json")
        elif key == "messages":
            out[key] = [dict(message) for message in value]
        else:
            out[key] = value
    return out


def read_records(path: Path) -> list[QuestionRecord]:
    return [
        QuestionRecord.model_validate_json(line)
        for line in path.read_text().splitlines()
        if line.strip()
    ]


def resolve_run_directory(name: str, *, root: Path = RUNS_ROOT) -> Path:
    """The directory for a run of this name: an existing one, or a fresh one.

    Resumption is by name rather than by path so that the command a run was
    started with is also the command that finishes it. The newest matching
    directory wins, because that is the run the operator just interrupted.
    """
    safe = RUN_NAME_RE.sub("-", name.casefold()).strip("-")
    if not safe:
        raise ValueError("run name must contain a letter or digit")
    existing = sorted(path for path in root.glob(f"*-{safe}") if path.is_dir())
    if existing:
        return existing[-1]
    return root / f"{datetime.now(UTC).strftime('%Y-%m-%d-%H%M')}-{safe}"
