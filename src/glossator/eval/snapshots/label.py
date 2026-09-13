"""One availability cell per question and snapshot."""

from __future__ import annotations

import asyncio
import hashlib
import json
import random
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from glossator.corpus.snapshots import DEFAULT_MANIFEST, snapshot_corpus_dir
from glossator.eval.corpus import load_documents
from glossator.eval.datasets import dataset_hash
from glossator.eval.lexical import LexicalIndex
from glossator.eval.providers.client import OpenAICompatibleProvider
from glossator.eval.snapshots.evidence import (
    best_matching_pages,
    exact_cell,
    fallback_spans,
    load_questions,
    verified_quotes,
)
from glossator.eval.snapshots.label_judge import LabelCallRecorder, judge_cell
from glossator.eval.snapshots.label_report import label_figure, label_metrics, label_readme
from glossator.eval.snapshots.models import LABEL_SEED, PRIMARY_JUDGE, SECONDARY_JUDGE
from glossator.eval.snapshots.prompts import JUDGE_SYSTEM
from glossator.eval.snapshots.run_files import RUNS_ROOT, append_row, built_snapshots, run_path_for


async def label(
    datasets: Sequence[Path],
    *,
    name: str,
    manifest_path: Path = DEFAULT_MANIFEST,
    runs_root: Path = RUNS_ROOT,
    seed: int = LABEL_SEED,
    deterministic_only: bool = False,
) -> tuple[Path, dict[str, Any]]:
    """Decide one availability cell per question and snapshot.

    With ``deterministic_only`` the exact-span step runs and every other cell is
    recorded as ``pending_judges`` (label ``unknown``) with its lexical top pages,
    so the judged step can fill it in later without re-deciding anything. A later
    run without the flag drops the pending rows and judges them; finished cells
    are never re-decided.
    """
    questions = load_questions(datasets)
    snapshots = built_snapshots(manifest_path)
    run_path = run_path_for(name, runs_root)
    (run_path / "figures").mkdir(parents=True, exist_ok=True)
    labels_path = run_path / "labels.jsonl"
    calls_path = run_path / "calls.jsonl"
    records_path = run_path / "records.jsonl"
    calls_path.touch()
    labels_path.touch()
    records_path.touch()
    stored = [json.loads(line) for line in labels_path.read_text().splitlines() if line]
    existing = [row for row in stored if row.get("decided_by") != "pending_judges"]
    if len(existing) != len(stored):
        # Pending rows are placeholders for a later judged pass: drop them here so
        # the resume below re-examines exactly those cells instead of duplicating
        # them, and keep both files in sync with what the metrics are computed from.
        labels_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in existing))
        records_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in existing))
    done = {(row["question_id"], row["snapshot"]) for row in existing}
    quotes = verified_quotes(runs_root)
    fallbacks = fallback_spans(questions)
    recorder = LabelCallRecorder(calls_path)
    providers: Mapping[str, OpenAICompatibleProvider] = {}
    if not deterministic_only:
        providers = {
            model: OpenAICompatibleProvider(
                "zai",
                asyncio.Semaphore(1),
                caller_tag="eval.snapshots",
                recorder=recorder,
                seed=seed,
            )
            for model in (PRIMARY_JUDGE, SECONDARY_JUDGE)
        }
    try:
        for snapshot in snapshots:
            documents = load_documents(snapshot_corpus_dir(snapshot))
            lexical = LexicalIndex(documents)
            for dataset, question in questions:
                key = (question.id, snapshot.date)
                if key in done:
                    continue
                spans = quotes.get(question.id) or fallbacks.get(question.id, [])
                cell = exact_cell(question, spans, documents)
                top_pages: list[dict[str, str]] = []
                if cell is None and deterministic_only:
                    top_pages = best_matching_pages(lexical, question.reference_answer)
                    cell = {
                        "label": "unknown",
                        "moved": False,
                        "decided_by": "pending_judges",
                        "page": None,
                        "judges": {},
                    }
                if cell is None:
                    top_pages = best_matching_pages(lexical, question.reference_answer)
                    cell_label, judges = await judge_cell(question, top_pages, providers)
                    cell = {
                        "label": cell_label,
                        "moved": False,
                        "decided_by": "judges",
                        "page": judges[PRIMARY_JUDGE].get("page"),
                        "judges": judges,
                    }
                row = {
                    "question_id": question.id,
                    "dataset": dataset,
                    "snapshot": snapshot.date,
                    **cell,
                    "question": question.question,
                    "reference_answer": question.reference_answer,
                    "gold": [source.model_dump(mode="json") for source in question.gold],
                    "supporting_spans": [{"page": span.page, "text": span.text} for span in spans],
                    "top_pages": top_pages,
                }
                append_row(labels_path, row)
                append_row(records_path, row)
                existing.append(row)
    finally:
        await asyncio.gather(*(provider.aclose() for provider in providers.values()))

    metrics = label_metrics(existing, snapshots)
    config = {
        "kind": "snapshot_labels",
        "name": name,
        "datasets": [{"path": str(path), "sha256": dataset_hash(path)} for path in datasets],
        "snapshot_manifest": str(manifest_path),
        "snapshot_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "judges": [PRIMARY_JUDGE, SECONDARY_JUDGE],
        "seed": seed,
        "deterministic_only": deterministic_only,
        "prompt_sha256": hashlib.sha256(JUDGE_SYSTEM.encode()).hexdigest(),
    }
    (run_path / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    (run_path / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    (run_path / "README.md").write_text(label_readme(metrics, datasets))
    (run_path / "figures" / "availability.svg").write_text(label_figure(metrics))
    judged = [row for row in existing if row["decided_by"] == "judges"]
    sample = random.Random(seed).sample(judged, min(20, len(judged)))
    (run_path / "human-sample.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in sample)
    )
    return run_path, metrics
