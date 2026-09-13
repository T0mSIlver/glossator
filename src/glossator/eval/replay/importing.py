"""One run directory per source run, holding the replayed answers unjudged."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import structlog

from glossator.answer.config import ModelPrice
from glossator.eval.answer_eval.run_dir import RunDirectory
from glossator.eval.replay.records import call_row, replay_record, single_pass_records
from glossator.eval.run_records import create_run_directory
from glossator.index.variants import VARIANTS

logger = structlog.get_logger(__name__)


def import_results(
    results_path: Path,
    prompts_path: Path,
    *,
    name: str,
    model: str,
    corpus_dir: Path,
    runs_root: Path,
    notes: Sequence[str] = (),
) -> list[Path]:
    """One run directory per source run, holding the replayed answers unjudged."""
    prompts = {row["id"]: row for row in _jsonl(prompts_path)}
    results = _jsonl(results_path)
    by_run: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        by_run.setdefault(result["run"], []).append(result)
    results_sha = hashlib.sha256(results_path.read_bytes()).hexdigest()
    written: list[Path] = []
    for source_name, rows in by_run.items():
        source_dir = runs_root / source_name
        source_config = json.loads((source_dir / "config.json").read_text())
        variant = str(source_config.get("variant", "sec1024"))
        chunking = VARIANTS[variant].chunking
        min_quote_chars = int(source_config.get("answer_config", {}).get("min_quote_chars", 8))
        records = single_pass_records(source_dir)
        config = {
            **{k: v for k, v in source_config.items() if k not in ("resumed_records", "notes")},
            "kind": "answer_eval",
            "name": f"{name}-{_short_name(source_name)}",
            "model": model,
            "replay": {
                "source_run": source_name,
                "source_model": source_config.get("model"),
                "results": str(results_path),
                "results_sha256": results_sha,
                "prompts": str(prompts_path),
                "response_format": sorted({str(r.get("response_format")) for r in rows}),
                "endpoint_model": sorted({str(r.get("model")) for r in rows}),
            },
            "strategies": ["single_pass"],
            "judge_models": [],
            "judge_model": None,
            "notes": [
                f"Generation replayed on {model} from the recorded prompts of "
                f"`{source_name}`; retrieval, reranking and context are that run's, unchanged.",
                *notes,
            ],
        }
        config["answer_config"] = {**source_config.get("answer_config", {}), "model": model}
        run_path = create_run_directory(config["name"], root=runs_root)
        run_dir = RunDirectory.open(run_path, config)
        rebuild_notes: list[str] = []
        skipped: list[str] = []
        for result in sorted(rows, key=lambda r: r["question_id"]):
            source = records.get(result["question_id"])
            if source is None or source.trace is None:
                # The prompt was exported from the call ledger, but the source
                # run's record for it ended in an error and holds no trace, so
                # there is nothing to verify the replayed quotes against.
                logger.warning(
                    "No source record with a trace", run=source_name, question=result["question_id"]
                )
                skipped.append(result["question_id"])
                continue
            record, notes_for = replay_record(
                source,
                result,
                model=model,
                corpus_dir=corpus_dir,
                chunking=chunking,
                min_quote_chars=min_quote_chars,
                prices=_price_table(source_config),
            )
            rebuild_notes.extend(f"{result['question_id']}: {note}" for note in notes_for)
            run_dir.append_call("replay", call_row(result, prompts[result["id"]], record))
            run_dir.record(record)
        if skipped:
            run_dir.config["notes"].append(
                f"{len(skipped)} replayed answer(s) not scored because the source record "
                f"ended in an error and has no trace: {', '.join(skipped)}."
            )
            run_dir.config["replay"]["skipped_no_trace"] = skipped
            (run_path / "config.json").write_text(
                json.dumps(run_dir.config, indent=2, sort_keys=True) + "\n"
            )
        (run_path / "rebuild-notes.txt").write_text(
            "\n".join(rebuild_notes) + ("\n" if rebuild_notes else "")
        )
        run_dir.finalize(status="unjudged", error=None)
        logger.info(
            "Imported replay",
            run=str(run_path),
            answers=len(run_dir.records),
            rebuild_notes=len(rebuild_notes),
        )
        written.append(run_path)
    return written


def _price_table(config: Mapping[str, Any]) -> dict[str, ModelPrice] | None:
    prices = config.get("answer_config", {}).get("prices")
    if not prices:
        return None
    return {model: ModelPrice.model_validate(price) for model, price in prices.items()}


def _short_name(run_name: str) -> str:
    # `2026-09-09-0312-dev60-rerank` -> `dev60-rerank`
    return re.sub(r"^\d{4}-\d{2}-\d{2}-\d{4}-", "", run_name)


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
