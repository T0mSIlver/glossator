"""Failure counts and shares per run, strategy and question type."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from glossator.eval.failures import corpus
from glossator.eval.failures.models import (
    CLASS_ORDER,
    FAILURES_KIND,
    SUB_LABELS,
    AnalysedRun,
    DefectSignal,
    FailureRecord,
    SkippedRun,
)
from glossator.index.variants import VARIANTS


def _class_counts(failures: Sequence[FailureRecord]) -> dict[str, int]:
    counts = Counter(failure.failure_class.value for failure in failures)
    return {
        failure_class.value: counts.get(failure_class.value, 0) for failure_class in CLASS_ORDER
    }


def _shares(counts: Mapping[str, int], total: int) -> dict[str, float]:
    return {name: round(count / total, 4) if total else 0.0 for name, count in counts.items()}


def _sub_label_counts(failures: Sequence[FailureRecord]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for failure_class in CLASS_ORDER:
        counts = Counter(
            failure.sub_label.value
            for failure in failures
            if failure.failure_class is failure_class
        )
        out[failure_class.value] = {
            sub.value: counts.get(sub.value, 0) for sub in SUB_LABELS[failure_class]
        }
    return out


def breakdown(failures: Sequence[FailureRecord], answers: int) -> dict[str, Any]:
    counts = _class_counts(failures)
    return {
        "answers": answers,
        "failures": len(failures),
        "failure_share": round(len(failures) / answers, 4) if answers else 0.0,
        "by_class": counts,
        "by_class_share": _shares(counts, answers),
        "sub_labels": _sub_label_counts(failures),
        "reference_defect_flagged": sum(failure.reference_defect_suspected for failure in failures),
        "defect_signals": {
            signal.value: sum(signal in failure.defect_signals for failure in failures)
            for signal in DefectSignal
        },
    }


def grouped(
    failures: Sequence[FailureRecord], answers: Mapping[str, int], key: str
) -> dict[str, dict[str, Any]]:
    """Failures broken down by one field of the row, over that group's answer count."""
    groups = sorted({str(getattr(failure, key)) for failure in failures} | set(answers))
    return {
        group: breakdown(
            [failure for failure in failures if str(getattr(failure, key)) == group],
            answers.get(group, 0),
        )
        for group in groups
    }


def aggregate(
    runs: Sequence[AnalysedRun],
    skipped: Sequence[SkippedRun],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    """Every number the README and the figure are built from."""
    by_run: dict[str, Any] = {}
    for run in runs:
        by_run[run.name] = {
            "run_dir": str(run.path),
            "dataset": run.config.get("dataset"),
            "model": run.config.get("model"),
            "variant": run.variant,
            "rerank": run.config.get("rerank"),
            "strategies": list(run.strategies),
            "judged": run.judged,
            "unjudged": run.answers - run.judged,
            "errors": run.errors,
            "chunk_ids_recorded": run.recorded_chunks,
            "chunk_ids_resolved": run.resolved_chunks,
            "passed_judged": run.passed_judged,
            "passed_naming_the_reference": run.passed_naming_the_reference,
            **breakdown(run.failures, run.answers),
            "by_strategy": grouped(run.failures, run.answers_by_strategy, "strategy"),
            "by_question_type": grouped(
                run.failures, run.answers_by_question_type, "question_type"
            ),
        }

    every = [failure for run in runs for failure in run.failures]
    answers = sum(run.answers for run in runs)
    return {
        "kind": FAILURES_KIND,
        "generated_at": datetime.now(UTC).isoformat(),
        "corpus": str(config.get("corpus")),
        "runs": [run.name for run in runs],
        "skipped_runs": [row.model_dump(mode="json") for row in skipped],
        "chunk_index": {
            variant: len(
                corpus.chunk_index(Path(str(config["corpus"])), VARIANTS[variant].chunking).facts
            )
            for variant in sorted({run.variant for run in runs})
        },
        "judge_model": config.get("judge_model"),
        "totals": {
            **breakdown(every, answers),
            "runs": len(runs),
            "chunk_ids_recorded": sum(run.recorded_chunks for run in runs),
            "chunk_ids_resolved": sum(run.resolved_chunks for run in runs),
            "passed_judged": sum(run.passed_judged for run in runs),
            "passed_naming_the_reference": sum(run.passed_naming_the_reference for run in runs),
            "defect_judgements": sum(failure.defect_judgement is not None for failure in every),
        },
        "by_run": by_run,
    }


def ordered_runs(metrics: Mapping[str, Any]) -> list[tuple[str, Mapping[str, Any]]]:
    """The runs in the order they were named on the command line.

    `metrics.json` is written with sorted keys, so `by_run` comes back off disk
    alphabetically; reading the order from the `runs` list keeps a regenerated
    README identical to the one the analysis wrote.
    """
    return [(name, metrics["by_run"][name]) for name in metrics["runs"]]
