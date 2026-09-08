from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from glossator.eval.providers import (
    Message,
    ProviderName,
    ThinkingMode,
    TokenUsage,
)

RUN_NAME_RE = re.compile(r"[^a-z0-9-]+")
STATUS_IN_PROGRESS = "in progress"
STATUS_COMPLETE = "complete"
STATUS_FAILED = "failed"


class RunRecorder:
    def __init__(self, run_dir: Path, config: Mapping[str, Any]) -> None:
        self.run_dir = run_dir
        self.config = dict(config)
        self.calls_path = run_dir / "calls.jsonl"
        self.records_path = run_dir / "records.jsonl"
        self.metrics_path = run_dir / "metrics.json"
        self.readme_path = run_dir / "README.md"
        self.call_rows: list[dict[str, Any]] = []
        self.record_rows: list[dict[str, Any]] = []
        run_dir.mkdir(parents=True, exist_ok=False)
        (run_dir / "figures").mkdir()
        (run_dir / "config.json").write_text(
            json.dumps(self.config, indent=2, sort_keys=True) + "\n"
        )
        self.calls_path.touch()
        self.records_path.touch()
        # An interrupted run must not claim completion; regenerate() rebuilds
        # this summary from the row files once the outcome is known.
        self._write_summary(status=STATUS_IN_PROGRESS, dataset=None, error=None)

    def record_call(
        self,
        *,
        provider: ProviderName,
        model: str,
        messages: Sequence[Message],
        response_text: str | None,
        parsed: BaseModel | None,
        usage: TokenUsage,
        cached: bool,
        latency_ms: float,
        error: str | None,
        thinking: ThinkingMode | None,
    ) -> None:
        row = {
            "timestamp": datetime.now(UTC).isoformat(),
            "provider": provider,
            "model": model,
            "thinking": thinking,
            "request_messages": [dict(message) for message in messages],
            "raw_response_text": response_text,
            "parsed_result": parsed.model_dump(mode="json") if parsed else None,
            "usage": usage.model_dump(mode="json"),
            "cached": cached,
            "latency_ms": round(latency_ms, 3),
            "error": error,
        }
        self.call_rows.append(row)
        self._append(self.calls_path, row)

    def record_candidate(self, candidate: BaseModel | Mapping[str, Any]) -> None:
        row = (
            candidate.model_dump(mode="json")
            if isinstance(candidate, BaseModel)
            else dict(candidate)
        )
        self.record_rows.append(row)
        self._append(self.records_path, row)

    def finalize(
        self,
        *,
        dataset_path: Path | None,
        error: str | None,
        status: str | None = None,
    ) -> None:
        if status is None:
            status = STATUS_FAILED if error else STATUS_COMPLETE
        self._write_summary(status=status, dataset=dataset_path, error=error)

    def _write_summary(
        self, *, status: str, dataset: Path | str | None, error: str | None
    ) -> None:
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


def summarize(
    call_rows: Sequence[Mapping[str, Any]],
    record_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    candidate_types = Counter(row["generator_type"] for row in record_rows)
    kept_types = Counter(row["generator_type"] for row in record_rows if row["kept"])
    dropped_reasons: Counter[str] = Counter()
    for row in record_rows:
        if not row["kept"]:
            dropped_reasons.update(row["drop_reasons"])
    usage = TokenUsage()
    uncached_usage = TokenUsage()
    for row in call_rows:
        call_usage = TokenUsage.model_validate(row["usage"])
        usage = usage.plus(call_usage)
        if not row["cached"]:
            uncached_usage = uncached_usage.plus(call_usage)
    return {
        "candidates": len(record_rows),
        "kept": sum(bool(row["kept"]) for row in record_rows),
        "dropped": sum(not row["kept"] for row in record_rows),
        "candidates_by_type": dict(sorted(candidate_types.items())),
        "kept_by_type": dict(sorted(kept_types.items())),
        "dropped_by_reason": dict(sorted(dropped_reasons.items())),
        "calls": len(call_rows),
        "cached_calls": sum(bool(row["cached"]) for row in call_rows),
        "usage": usage.model_dump(mode="json"),
        "uncached_usage": uncached_usage.model_dump(mode="json"),
        "latency_ms": round(sum(float(row["latency_ms"]) for row in call_rows), 3),
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
        **summarize(call_rows, record_rows),
    }
    (run_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n"
    )
    (run_dir / "README.md").write_text(render_readme(config, metrics))
    return metrics


def render_readme(config: Mapping[str, Any], metrics: Mapping[str, Any]) -> str:
    reason_lines = [
        f"- {reason}: {count}" for reason, count in metrics["dropped_by_reason"].items()
    ] or ["- None"]
    type_lines = []
    for question_type, candidates in metrics["candidates_by_type"].items():
        kept = metrics["kept_by_type"].get(question_type, 0)
        candidate_label = "candidate" if candidates == 1 else "candidates"
        type_lines.append(
            f"- {question_type}: {candidates} {candidate_label}, {kept} kept, "
            f"{candidates - kept} dropped"
        )
    if not type_lines:
        type_lines = ["- No candidates were generated"]
    usage = metrics["usage"]
    dataset = metrics["dataset"] or "No dataset was written"
    if metrics["status"] == STATUS_COMPLETE:
        conclusion = (
            "Status: complete. The records support the dataset-generation choice "
            "in D-020 and the record requirements in D-023."
        )
    elif metrics["status"] == STATUS_FAILED:
        conclusion = (
            f"Status: failed. {_as_sentence(metrics['error'])} No dataset was written."
        )
    else:
        conclusion = (
            "Status: in progress. The run had not finished when this summary was "
            "last written."
        )
    return (
        "# Dataset generation run\n\n"
        f"This run asked {config['model']} to generate documentation questions from "
        f"{config['corpus']}. It tested whether prompt {config['prompt_version']} "
        "produces standalone questions supported by their assigned sources.\n\n"
        "## Question\n\n"
        "Does this generator configuration produce valid questions whose assigned sources "
        "are all necessary for the answer?\n\n"
        "## Configuration\n\n"
        "The run used one provider and prompt configuration. `config.json` records every "
        "parameter and prompt hash.\n\n"
        f"- Provider: {config['provider']}\n"
        f"- Model: {config['model']}\n"
        f"- Thinking: {config['thinking']}\n"
        f"- Seed: {config['seed']}\n"
        f"- Corpus commit: {config['corpus_commit']}\n"
        f"- Requested questions: {config['n']}\n"
        f"- Dataset: {dataset}\n\n"
        "## Results\n\n"
        f"The run processed {metrics['candidates']} candidates, kept {metrics['kept']}, "
        f"and dropped {metrics['dropped']}.\n\n"
        + "\n".join(type_lines)
        + "\n\nDropped candidates by reason:\n\n"
        + "\n".join(reason_lines)
        + "\n\n"
        f"The provider handled {metrics['calls']} calls, including "
        f"{metrics['cached_calls']} cache hits. Recorded usage was "
        f"{usage['prompt_tokens']} prompt tokens, {usage['completion_tokens']} completion "
        f"tokens, and {usage['reasoning_tokens']} reasoning tokens.\n\n"
        "## Conclusion\n\n"
        f"{conclusion}\n"
    )


def _as_sentence(text: str | None) -> str:
    if not text:
        return "The run failed."
    sentence = text.strip()
    sentence = sentence[0].upper() + sentence[1:]
    if sentence[-1] not in ".!?":
        sentence += "."
    return sentence


def regenerate(run_dir: Path) -> dict[str, Any]:
    """Rebuild metrics.json and README.md from the committed row files.

    The terminal status, error, and dataset path are preserved from the
    existing metrics.json because they cannot be derived from the rows.
    """
    config = json.loads((run_dir / "config.json").read_text())
    previous = json.loads((run_dir / "metrics.json").read_text())
    call_rows = _read_jsonl(run_dir / "calls.jsonl")
    record_rows = _read_jsonl(run_dir / "records.jsonl")
    dataset = previous.get("dataset")
    if dataset is None and previous.get("status") == STATUS_COMPLETE:
        out = config.get("out")
        # Summaries written before the dataset field existed; a completed run
        # wrote exactly the configured output path.
        if isinstance(out, str) and Path(out).exists():
            dataset = out
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
    return [json.loads(line) for line in path.read_text().splitlines()]


def create_run_directory(name: str, *, root: Path = Path("eval/runs")) -> Path:
    safe_name = RUN_NAME_RE.sub("-", name.casefold()).strip("-")
    if not safe_name:
        raise ValueError("run name must contain a letter or digit")
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d-%H%M")
    candidate = root / f"{timestamp}-{safe_name}"
    suffix = 2
    while candidate.exists():
        candidate = root / f"{timestamp}-{safe_name}-{suffix}"
        suffix += 1
    return candidate
