"""The durable record of one run: config, every call, every candidate, metrics.

D-023: a number that cannot be traced back to raw model output cannot be
defended. The run directory holds that trace, and the README is rendered from
it -- no sentence in the README is written by hand or preserved across a
regeneration.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Self

from pydantic import BaseModel

from glossator.eval.pricing import estimate_usd, price_for
from glossator.eval.providers import Message, ProviderName, ThinkingMode, TokenUsage

RUN_NAME_RE = re.compile(r"[^a-z0-9-]+")
STATUS_IN_PROGRESS = "in progress"
STATUS_COMPLETE = "complete"
STATUS_FAILED = "failed"


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


def _conclusion(config: Mapping[str, Any], metrics: Mapping[str, Any]) -> str:
    """The run's conclusion, computed from its own numbers."""
    if metrics["status"] == STATUS_IN_PROGRESS:
        return "The run had not finished when this summary was last written."
    if metrics["status"] == STATUS_FAILED:
        return f"{_as_sentence(metrics['error'])} No dataset was written."

    parts: list[str] = []
    requested = metrics["requested"] or metrics["kept"]
    parts.append(
        f"The run asked for {requested} questions and accepted {metrics['kept']} of "
        f"{metrics['candidates']} candidates."
    )
    shortfalls = metrics["shortfall_by_type"]
    if shortfalls:
        listed = ", ".join(f"{name} short by {count}" for name, count in sorted(shortfalls.items()))
        parts.append(
            f"{metrics['shortfall']} question(s) could not be filled from the corpus: {listed}. "
            "The dataset holds what was accepted."
        )
    else:
        parts.append("Every question type was filled.")
    reasons = sorted(metrics["dropped_by_reason"].items(), key=lambda item: (-item[1], item[0]))
    if reasons:
        top = ", ".join(f"{reason} ({count})" for reason, count in reasons[:3])
        parts.append(f"The largest drop reasons were {top}.")
    uncached = metrics["uncached_usage"]
    cost = metrics["estimated_usd"]
    price = price_for(metrics["model"])
    if cost is None:
        cost_sentence = f"No price is recorded for {metrics['model']}, so the cost is unknown."
    elif cost == 0.0 and price is not None and price.note:
        cost_sentence = (
            f"{uncached['prompt_tokens']} prompt and {uncached['completion_tokens']} completion "
            f"tokens were paid for at 0.00 USD against the Mistral budget ({price.note})."
        )
    else:
        cost_sentence = (
            f"{uncached['prompt_tokens']} prompt and {uncached['completion_tokens']} completion "
            f"tokens cost an estimated {cost:.4f} USD."
        )
    parts.append(cost_sentence)
    parts.append("The dataset feeds the retrieval and answer evaluations in D-016.")
    return " ".join(parts)


def render_readme(config: Mapping[str, Any], metrics: Mapping[str, Any]) -> str:
    if config.get("kind", "generate") != "generate":
        return _render_generic_readme(config, metrics)
    reason_lines = [
        f"- {reason}: {count}" for reason, count in metrics["dropped_by_reason"].items()
    ] or ["- None"]
    type_lines = []
    for question_type, candidates in metrics["candidates_by_type"].items():
        kept = metrics["kept_by_type"].get(question_type, 0)
        asked = metrics["requested_by_type"].get(question_type)
        asked_label = f"{asked} asked, " if asked is not None else ""
        type_lines.append(
            f"- {question_type}: {asked_label}{candidates} candidates, {kept} kept, "
            f"{candidates - kept} dropped"
        )
    if not type_lines:
        type_lines = ["- No candidates were generated"]
    kind_lines = [
        f"- {kind}: {count} calls, {metrics['usage_by_kind'][kind]['prompt_tokens']} prompt "
        f"+ {metrics['usage_by_kind'][kind]['completion_tokens']} completion tokens"
        for kind, count in metrics["calls_by_kind"].items()
    ] or ["- No calls were made"]
    usage = metrics["usage"]
    uncached = metrics["uncached_usage"]
    dataset = metrics["dataset"] or "No dataset was written"
    return (
        "# Dataset generation run\n\n"
        f"This run asked {config['model']} to generate documentation questions from "
        f"{config['corpus']}. It measures how many valid questions of each type the "
        f"generators produce, and what they cost.\n\n"
        "## Question\n\n"
        "Does this generator configuration produce standalone questions whose assigned "
        "sources are all necessary for the answer, in the numbers the development set needs?\n\n"
        "## Configuration\n\n"
        "`config.json` records every parameter and prompt hash.\n\n"
        f"- Provider: {config['provider']}\n"
        f"- Model: {config['model']}\n"
        f"- Thinking: {config['thinking']}\n"
        f"- Seed: {config['seed']}\n"
        f"- Prompt version: {config['prompt_version']}\n"
        f"- Corpus commit: {config['corpus_commit']}\n"
        f"- Requested questions: {config['n']}\n"
        f"- Dataset: {dataset}\n\n"
        "## Results\n\n"
        f"The run processed {metrics['candidates']} candidates, kept {metrics['kept']}, "
        f"and dropped {metrics['dropped']}.\n\n"
        + "\n".join(type_lines)
        + "\n\nDropped candidates by reason:\n\n"
        + "\n".join(reason_lines)
        + "\n\n## Calls and usage\n\n"
        f"The provider handled {metrics['calls']} calls, of which {metrics['cached_calls']} "
        f"were cache hits and {metrics['failed_calls']} returned an error that was retried "
        "or recorded.\n\n" + "\n".join(kind_lines) + "\n\n"
        f"Total tokens: {usage['prompt_tokens']} prompt, {usage['completion_tokens']} completion, "
        f"{usage['reasoning_tokens']} reasoning. Paid for in this run (uncached): "
        f"{uncached['prompt_tokens']} prompt, {uncached['completion_tokens']} completion, "
        f"{uncached['reasoning_tokens']} reasoning.\n\n"
        "## Figures\n\n"
        "`figures/` holds the charts, regenerated from `metrics.json` by "
        "`make eval-report run=<dir>`.\n\n"
        "- `figures/accepted-by-type.svg`: accepted against dropped, per question type\n"
        "- `figures/drop-reasons.svg`: how many candidates each drop reason accounts for\n"
        "- `figures/tokens-by-call-kind.svg`: tokens spent on generating against checking\n\n"
        "## Conclusion\n\n"
        f"{_conclusion(config, metrics)}\n"
    )


def _render_generic_readme(config: Mapping[str, Any], metrics: Mapping[str, Any]) -> str:
    """A run of another kind (a translation, a probe): the same records, plainer prose."""
    usage = metrics["usage"]
    uncached = metrics["uncached_usage"]
    kind_lines = [
        f"- {kind}: {count} calls, {metrics['usage_by_kind'][kind]['prompt_tokens']} prompt "
        f"+ {metrics['usage_by_kind'][kind]['completion_tokens']} completion tokens"
        for kind, count in metrics["calls_by_kind"].items()
    ] or ["- No calls were made"]
    config_lines = [f"- {key}: {value}" for key, value in sorted(config.items())]
    dataset = metrics["dataset"] or "No dataset was written"
    return (
        f"# {config.get('kind', 'run').capitalize()} run\n\n"
        f"Status: {metrics['status']}."
        + (f" {_as_sentence(metrics['error'])}" if metrics.get("error") else "")
        + "\n\n"
        "## Configuration\n\n" + "\n".join(config_lines) + "\n\n"
        "## Records\n\n"
        f"- rows: {metrics['candidates']}, kept: {metrics['kept']}\n"
        f"- dataset: {dataset}\n\n"
        "## Calls\n\n" + "\n".join(kind_lines) + "\n\n"
        f"- total: {metrics['calls']} calls ({metrics['cached_calls']} cached), "
        f"{usage['prompt_tokens']} prompt + {usage['completion_tokens']} completion tokens "
        f"({usage['reasoning_tokens']} reasoning); uncached {uncached['prompt_tokens']} + "
        f"{uncached['completion_tokens']}; estimated {metrics['estimated_usd']:.4f} USD "
        "against the Mistral budget\n\n"
        "Every call is in `calls.jsonl` and every row in `records.jsonl`.\n"
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
