"""The first grounded-answer request of every single-pass question, as it was sent."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from glossator.answer.generation import GeneratedAnswer

PURPOSE = "single_pass:grounded_answer"


def read_calls(run_dir: Path) -> Iterator[dict[str, Any]]:
    with (run_dir / "calls.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def _records(run_dir: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    with (run_dir / "records.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("strategy") == "single_pass":
                out[row["question_id"]] = row
    return out


def export_prompts(
    run_dirs: list[Path],
    output: Path,
    *,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> dict[str, Any]:
    """Write the first grounded-answer request of every single-pass question.

    `temperature` and `max_tokens` override the recorded sampling on every row,
    for runs that were generated under a local model's own settings (D-038b):
    the shipped sampling is what a comparison with the API runs needs, and the
    row keeps the recorded values under `source_temperature` and
    `source_max_tokens`.
    """
    schema = GeneratedAnswer.model_json_schema()
    rows: list[dict[str, Any]] = []
    per_run: dict[str, int] = {}
    for run_dir in run_dirs:
        records = _records(run_dir)
        seen: set[str] = set()
        for call in read_calls(run_dir):
            if call.get("purpose") != PURPOSE or call["question_id"] in seen:
                continue
            seen.add(call["question_id"])
            record = records.get(call["question_id"], {})
            rows.append(
                {
                    "id": f"{run_dir.name}/{call['question_id']}",
                    "run": run_dir.name,
                    "question_id": call["question_id"],
                    "question_type": record.get("question_type"),
                    "source_call_id": call["call_id"],
                    "source_model": call["model"],
                    "messages": call["messages"],
                    "temperature": call["temperature"] if temperature is None else temperature,
                    "max_tokens": call["max_tokens"] if max_tokens is None else max_tokens,
                    "source_temperature": call["temperature"],
                    "source_max_tokens": call["max_tokens"],
                    "response_schema": "GeneratedAnswer",
                    "json_schema": schema,
                }
            )
        per_run[run_dir.name] = len(seen)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    return {"prompts": len(rows), "per_run": per_run, "sha256": digest, "path": str(output)}
