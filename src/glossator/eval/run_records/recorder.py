"""Writing a run directory as the run happens."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Self

from pydantic import BaseModel

from glossator.eval.providers.models import Message, ProviderName, ThinkingMode, TokenUsage
from glossator.eval.run_records.models import (
    RUN_NAME_RE,
    STATUS_COMPLETE,
    STATUS_FAILED,
    STATUS_IN_PROGRESS,
)
from glossator.eval.run_records.summary import summarize, write_summary


class RunRecorder:
    """Writes the run directory as the run happens.

    Rows are appended as they are produced so that a run killed halfway still
    leaves everything it paid for.
    """

    def __init__(self, run_dir: Path, config: Mapping[str, Any]) -> None:
        self.run_dir = run_dir
        self.config = dict(config)
        self.calls_path = run_dir / "calls.jsonl"
        self.records_path = run_dir / "records.jsonl"
        self.metrics_path = run_dir / "metrics.json"
        self.readme_path = run_dir / "README.md"
        self.call_rows: list[dict[str, Any]] = []
        self.record_rows: list[dict[str, Any]] = []

    @classmethod
    def start(cls, run_dir: Path, config: Mapping[str, Any]) -> Self:
        """Create the run directory and write the configuration into it."""
        recorder = cls(run_dir, config)
        run_dir.mkdir(parents=True, exist_ok=False)
        (run_dir / "figures").mkdir()
        (run_dir / "config.json").write_text(
            json.dumps(recorder.config, indent=2, sort_keys=True) + "\n"
        )
        recorder.calls_path.touch()
        recorder.records_path.touch()
        # An interrupted run must not claim completion.
        recorder._write_summary(status=STATUS_IN_PROGRESS, dataset=None, error=None)
        return recorder

    def record_call(
        self,
        *,
        provider: ProviderName,
        model: str,
        endpoint: str,
        messages: Sequence[Message],
        response_text: str | None,
        parsed: BaseModel | None,
        usage: TokenUsage,
        cached: bool,
        latency_ms: float,
        error: str | None,
        thinking: ThinkingMode | None,
        temperature: float,
        max_tokens: int,
        response_format: dict[str, Any] | None,
        schema_name: str | None,
        schema_hash: str | None,
        seed: int | None,
        finish_reason: str | None,
        candidate_id: str | None,
        call_kind: str | None,
    ) -> None:
        row = {
            "timestamp": datetime.now(UTC).isoformat(),
            "candidate_id": candidate_id,
            "call_kind": call_kind or "other",
            "provider": provider,
            "endpoint": endpoint,
            "model": model,
            "thinking": thinking,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "seed": seed,
            "response_format": response_format,
            "schema_name": schema_name,
            "schema_hash": schema_hash,
            "request_messages": [dict(message) for message in messages],
            "raw_response_text": response_text,
            "parsed_result": parsed.model_dump(mode="json") if parsed else None,
            "usage": usage.model_dump(mode="json"),
            "cached": cached,
            "finish_reason": finish_reason,
            "call_ms": round(latency_ms, 3),
            "error": error,
        }
        self.call_rows.append(row)
        self._append(self.calls_path, row)

    def record_candidate(self, candidate: BaseModel) -> None:
        row = candidate.model_dump(mode="json")
        self.record_rows.append(row)
        self._append(self.records_path, row)

    def usage_line(self) -> dict[str, Any]:
        """The one-line usage summary the CLI prints."""
        metrics = summarize(self.call_rows, self.record_rows, self.config)
        return {
            "calls": metrics["calls"],
            "cached_calls": metrics["cached_calls"],
            "usage": metrics["usage"],
            "uncached_usage": metrics["uncached_usage"],
            "estimated_usd": metrics["estimated_usd"],
        }

    def finalize(
        self,
        *,
        dataset_path: Path | None,
        error: str | None,
        shortfalls: Mapping[str, int] | None = None,
        requested_by_type: Mapping[str, int] | None = None,
    ) -> None:
        if shortfalls is not None:
            self.config["shortfalls"] = dict(shortfalls)
        if requested_by_type is not None:
            self.config["requested_by_type"] = dict(requested_by_type)
        if shortfalls is not None or requested_by_type is not None:
            (self.run_dir / "config.json").write_text(
                json.dumps(self.config, indent=2, sort_keys=True) + "\n"
            )
        status = STATUS_FAILED if error else STATUS_COMPLETE
        self._write_summary(status=status, dataset=dataset_path, error=error)

    def _write_summary(self, *, status: str, dataset: Path | str | None, error: str | None) -> None:
        write_summary(
            self.run_dir,
            self.config,
            self.call_rows,
            self.record_rows,
            status=status,
            dataset=dataset,
            error=error,
        )

    @staticmethod
    def _append(path: Path, row: Mapping[str, Any]) -> None:
        with path.open("a") as file:
            file.write(json.dumps(row, sort_keys=True) + "\n")


def create_run_directory(name: str, *, root: Path = Path("eval/runs")) -> Path:
    """A fresh directory named for the moment the run started, in UTC.

    UTC because every timestamp inside the directory is UTC; a local-time name
    over a directory of UTC rows reads as a different run.
    """
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
