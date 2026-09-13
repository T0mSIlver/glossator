"""One answer-evaluation run directory in, its classified failures out."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from glossator.eval.agreement import CorrectnessLabel, labels_for_run, read_human_labels
from glossator.eval.answer_eval.run_dir import read_records
from glossator.eval.failures import corpus
from glossator.eval.failures.classify import REFERENCE_MENTION, classify
from glossator.eval.failures.evidence import rerank_candidates, retrieved_chunk_ids, verdict_of
from glossator.eval.failures.models import ANSWER_EVAL_KIND, AnalysedRun, FailureRecord, SkippedRun
from glossator.index.variants import VARIANTS


def analyse_run(
    run_dir: Path,
    *,
    corpus_dir: Path,
    labels_path: Path | None,
) -> AnalysedRun | SkippedRun:
    """Classify every failed answer of one run directory."""
    config = json.loads((run_dir / "config.json").read_text())
    kind = str(config.get("kind", "generate"))
    if kind != ANSWER_EVAL_KIND:
        return SkippedRun(
            run_dir=str(run_dir),
            kind=kind,
            reason=(
                f"a `{kind}` run holds no answers to classify; it is the run that "
                "produced a dataset, not one that answered its questions"
            ),
        )
    records = read_records(run_dir / "records.jsonl")
    variant = str(config.get("variant", "sec1024"))
    index = corpus.chunk_index(corpus_dir, VARIANTS[variant].chunking)
    reranked = rerank_candidates(run_dir)
    human = _human_labels(labels_path, run_dir, config)

    failures: list[FailureRecord] = []
    resolved = recorded = 0
    passed_judged = passed_naming = 0
    for record in records:
        ids = retrieved_chunk_ids(record.trace)
        recorded += len(ids)
        resolved += index.resolves(ids)
        classified = classify(
            record,
            index=index,
            run_name=run_dir.name,
            run_dir=run_dir,
            reranked=reranked,
            human=human.get((record.question_id, record.strategy)),
        )
        if classified is not None:
            failures.append(classified)
            continue
        verdict = record.judge.verdict if record.judge else None
        if verdict is not None:
            passed_judged += 1
            passed_naming += bool(REFERENCE_MENTION.search(verdict.correctness_reason))
    return AnalysedRun(
        path=run_dir,
        name=run_dir.name,
        config=config,
        answers=len(records),
        judged=sum(verdict_of(record) is not None for record in records),
        errors=sum(record.error is not None for record in records),
        failures=tuple(failures),
        resolved_chunks=resolved,
        recorded_chunks=recorded,
        answers_by_strategy=Counter(record.strategy for record in records),
        answers_by_question_type=Counter(record.question_type for record in records),
        reference_answers={record.key: record.reference_answer for record in records},
        passed_judged=passed_judged,
        passed_naming_the_reference=passed_naming,
    )


def _human_labels(
    labels_path: Path | None, run_dir: Path, config: Mapping[str, Any]
) -> dict[tuple[str, str], CorrectnessLabel]:
    """The hand labels that belong to this run, if any were exported for it."""
    if labels_path is None or not labels_path.exists():
        return {}
    names = [str(run_dir), run_dir.name, str(config.get("name") or "")]
    return labels_for_run(read_human_labels(labels_path), [name for name in names if name])
