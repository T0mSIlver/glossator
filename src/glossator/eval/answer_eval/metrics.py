"""Per-question numbers and their aggregates, as `metrics.json` holds them."""

from __future__ import annotations

import statistics
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from glossator.answer.citations import VERIFIED_AFTER_EMPHASIS, RejectionReason
from glossator.answer.config import MISTRAL_MEDIUM_3_5, PRICES
from glossator.answer.llm import TokenUsage as AnswerTokenUsage
from glossator.eval.agreement import (
    CorrectnessLabel,
    agreement_report,
    labels_for_run,
    read_human_labels,
)
from glossator.eval.answer_eval.matching import (
    exact_gold_anchor_match,
    exact_gold_url_match,
    gold_anchor_match,
    gold_relaxed_match,
    gold_url_match,
)
from glossator.eval.answer_eval.models import (
    CORRECTNESS_SCORE,
    QUESTION_TYPES,
    JudgeRecord,
    QuestionRecord,
)
from glossator.eval.datasets import QuestionType
from glossator.eval.percentiles import nearest_rank_percentile

REFERENCE_PRICING_MODEL = MISTRAL_MEDIUM_3_5
"""Prices the recorded tokens a second time, at the shipped model's rates (D-017),
so the day the account is provisioned the budget question is already answered."""

UNPRICED_MODELS: frozenset[str] = frozenset()
"""Generation models known to lack a published price in the current price table."""


def tool_calls(record: QuestionRecord) -> int:
    if record.trace is None:
        return 0
    return sum(event.kind == "tool" for event in record.trace.events)


def rounds(record: QuestionRecord) -> int:
    return record.trace.rounds if record.trace is not None else 0


def hit_round_cap(record: QuestionRecord) -> bool:
    """Whether the loop ran out of rounds before it stopped itself.

    A configuration whose answers keep hitting the cap is one where the model
    wanted to keep looking; read beside `rounds`, it says whether the mean is
    the model's choice or the configuration's (D-035c).
    """
    if record.trace is None:
        return False
    return any(event.kind == "loop" and event.name == "round_cap" for event in record.trace.events)


def rejection_counts(record: QuestionRecord) -> tuple[int, int]:
    """Rejected citations split into fabricated and cosmetic.

    A model that invented a sentence and a model that dropped a pair of asterisks
    are different failures (D-027a); averaging them into one rate hides both. A
    citation naming a source number that does not exist counts as fabricated: the
    quote was never checkable against anything.
    """
    fabricated = 0
    cosmetic = 0
    for citation in record.unverified_citations:
        if citation.reason in RejectionReason.COSMETIC:
            cosmetic += 1
        else:
            fabricated += 1
    return fabricated, cosmetic


def question_metrics(record: QuestionRecord) -> dict[str, float | None]:
    """Every per-question number, or None where the question does not have one."""
    answerable = record.question_type != QuestionType.UNANSWERABLE.value
    emitted = len(record.citations) + len(record.unverified_citations)
    fabricated, cosmetic = rejection_counts(record)
    normalized = sum(citation.reason == VERIFIED_AFTER_EMPHASIS for citation in record.citations)
    relaxed = gold_relaxed_match(record) and not (
        exact_gold_url_match(record) and exact_gold_anchor_match(record)
    )
    verdict = record.judge.verdict if record.judge else None
    return {
        "cited_url_match": float(gold_url_match(record)) if answerable else None,
        "cited_anchor_match": float(gold_anchor_match(record)) if answerable else None,
        "gold_relaxed_matches": float(relaxed) if answerable else None,
        "citations_emitted": float(emitted),
        "citations_verified": float(len(record.citations)),
        "citations_fabricated": float(fabricated),
        "citations_cosmetic": float(cosmetic),
        "citations_normalized": float(normalized),
        "distinct_sources_cited": float(len({citation.n for citation in record.citations})),
        "unmatched_markers_per_answer": float(
            len(record.trace.unmatched_markers) if record.trace else 0
        ),
        "unverified_citations_per_answer": float(len(record.unverified_citations)),
        "refusal_correct": float(record.insufficient_evidence == (not answerable)),
        "insufficient_evidence": float(record.insufficient_evidence),
        "latency_ms": record.latency_ms,
        "tokens_in": float(record.usage.prompt_tokens),
        "tokens_out": float(record.usage.completion_tokens),
        "usd": record.cost_usd,
        "reference_usd": reference_cost_usd(record.usage),
        "tool_calls": float(tool_calls(record)),
        "rounds": float(rounds(record)),
        "round_cap_hit": float(hit_round_cap(record)),
        "errors": float(record.error is not None),
        "correctness": CORRECTNESS_SCORE[verdict.correctness] if verdict else None,
        "correct": float(verdict.correctness == "correct") if verdict else None,
        "partial": float(verdict.correctness == "partial") if verdict else None,
        "wrong": float(verdict.correctness == "wrong") if verdict else None,
        "groundedness": verdict.groundedness if verdict else None,
        "citation_relevance": verdict.citation_relevance if verdict else None,
    }


def reference_cost_usd(usage: AnswerTokenUsage) -> float:
    """What the same tokens would cost on the shipped model (D-017, D-017a)."""
    price = PRICES[REFERENCE_PRICING_MODEL]
    return (
        usage.prompt_tokens * price.input_usd_per_mtok
        + usage.completion_tokens * price.output_usd_per_mtok
    ) / 1_000_000


# Metrics whose cell value is a mean of the per-question values, and the number of
# decimals the tables print them with.
MEAN_METRICS: dict[str, int] = {
    "cited_url_match": 2,
    "cited_anchor_match": 2,
    "distinct_sources_cited": 2,
    "unmatched_markers_per_answer": 2,
    "unverified_citations_per_answer": 2,
    "refusal_correct": 2,
    "correctness": 2,
    "correct": 2,
    "partial": 2,
    "wrong": 2,
    "groundedness": 2,
    "citation_relevance": 2,
    "tokens_in": 0,
    "tokens_out": 0,
    "usd": 5,
    "reference_usd": 4,
    "tool_calls": 2,
    "rounds": 2,
    "round_cap_hit": 2,
}


def _mean(values: Sequence[float]) -> float | None:
    return statistics.fmean(values) if values else None


def cell(records: Sequence[QuestionRecord]) -> dict[str, Any]:
    """Every aggregate number for one group of records."""
    per_question = [question_metrics(record) for record in records]

    def column(name: str) -> list[float]:
        return [row[name] for row in per_question if row[name] is not None]  # type: ignore[misc]

    emitted = sum(column("citations_emitted"))
    verified = sum(column("citations_verified"))
    latencies = column("latency_ms")
    aggregate: dict[str, Any] = {
        "questions": len(records),
        "errors": int(sum(column("errors"))),
        "citations_emitted": int(emitted),
        "citations_verified": int(verified),
        "citation_verification_rate": (verified / emitted) if emitted else None,
        "fabricated_per_answer": _mean(column("citations_fabricated")),
        "cosmetic_per_answer": _mean(column("citations_cosmetic")),
        "verified_after_normalization": int(sum(column("citations_normalized"))),
        "gold_relaxed_matches": int(sum(column("gold_relaxed_matches"))),
        "latency_p50_s": (
            None if not latencies else (nearest_rank_percentile(latencies, 0.5) or 0.0) / 1000
        ),
        "latency_p95_s": (
            None if not latencies else (nearest_rank_percentile(latencies, 0.95) or 0.0) / 1000
        ),
        "judged": sum(1 for row in per_question if row["correctness"] is not None),
    }
    for name in MEAN_METRICS:
        aggregate[name] = _mean(column(name))
    aggregate["tokens_in_total"] = int(sum(column("tokens_in")))
    aggregate["tokens_out_total"] = int(sum(column("tokens_out")))
    aggregate["usd_total"] = sum(column("usd"))
    aggregate["reference_usd_total"] = sum(column("reference_usd"))
    aggregate.update(judge_spend(records))
    return aggregate


def judge_spend(records: Sequence[QuestionRecord]) -> dict[str, Any]:
    """What judging cost, counted apart from what answering cost.

    The judge runs on the z.ai coding plan, which bills nothing against the
    Mistral budget (D-020), so its tokens would vanish if they were added to the
    answer totals. They are counted anyway: "free" is a statement about this
    month's plan, not about the work, and a Mistral judge would be priced from
    exactly these numbers.
    """
    judged = [judgement for record in records for judgement in _current_judgements(record)]
    prompt = sum(judgement.usage.prompt_tokens for judgement in judged)
    completion = sum(judgement.usage.completion_tokens for judgement in judged)
    reasoning = sum(judgement.usage.reasoning_tokens for judgement in judged)
    price = PRICES[REFERENCE_PRICING_MODEL]
    return {
        "judge_calls": len(judged),
        "judge_failures": sum(1 for judgement in judged if judgement.verdict is None),
        "judge_tokens_in": prompt,
        "judge_tokens_out": completion,
        "judge_reasoning_tokens": reasoning,
        "judge_latency_s_mean": (_mean([judgement.latency_ms for judgement in judged]) or 0.0)
        / 1000,
        "judge_reference_usd_total": (
            prompt * price.input_usd_per_mtok + completion * price.output_usd_per_mtok
        )
        / 1_000_000,
    }


def _current_judgements(record: QuestionRecord) -> list[JudgeRecord]:
    """Current prompt-version judgements, without counting the primary twice."""
    if record.judges:
        return list(record.judges.values())
    return [record.judge] if record.judge is not None else []


def _agreement_metrics(
    records: Sequence[QuestionRecord], config: Mapping[str, Any]
) -> dict[str, object]:
    configured = config.get("judge_models") or []
    judges: dict[str, dict[tuple[str, str], CorrectnessLabel]] = {
        str(name): {} for name in configured if name
    }
    for record in records:
        item = record.key
        current: list[tuple[str, JudgeRecord]]
        if record.judges:
            current = list(record.judges.items())
        elif record.judge is not None:
            provider = record.judge.provider or config.get("judge_provider") or "zai"
            current = [(f"{provider}:{record.judge.model}", record.judge)]
        else:
            current = []
        for name, judgement in current:
            if judgement.verdict is not None:
                judges.setdefault(name, {})[item] = judgement.verdict.correctness

    human: dict[tuple[str, str], CorrectnessLabel] | None = None
    labels_path = config.get("labels")
    if labels_path:
        labels = read_human_labels(Path(str(labels_path)))
        run_path = Path(str(config.get("run_dir", "")))
        run_names = [str(run_path), run_path.name, str(config.get("name", ""))]
        human = labels_for_run(labels, run_names)
    return agreement_report(judges, human)


def aggregate(records: Sequence[QuestionRecord], config: Mapping[str, Any]) -> dict[str, Any]:
    """The metrics file: one cell per strategy and question type, plus totals."""
    strategies = [
        strategy
        for strategy in config.get("strategies", [])
        if any(record.strategy == strategy for record in records)
    ] or sorted({record.strategy for record in records})
    types = [
        question_type
        for question_type in QUESTION_TYPES
        if any(record.question_type == question_type for record in records)
    ]
    by_strategy: dict[str, Any] = {}
    for strategy in strategies:
        rows = [record for record in records if record.strategy == strategy]
        by_strategy[strategy] = {
            "all": cell(rows),
            "by_type": {
                question_type: cell([row for row in rows if row.question_type == question_type])
                for question_type in types
            },
        }
    return {
        "kind": "answer_eval",
        "model": config.get("model"),
        "generation_server": config.get("generation_server"),
        "reasoning_effort": config.get("reasoning_effort"),
        "answer_config_overrides": dict(config.get("answer_config_overrides") or {}),
        "judge_model": config.get("judge_model"),
        "judge_models": config.get("judge_models")
        or ([config.get("judge_model")] if config.get("judge_model") else []),
        "variant": config.get("variant"),
        "dataset": config.get("dataset"),
        "dataset_sha256": config.get("dataset_sha256"),
        "strategies": strategies,
        "question_types": types,
        "questions": len({record.question_id for record in records}),
        "records": len(records),
        "by_strategy": by_strategy,
        "totals": cell(list(records)),
        "winners": winners(by_strategy),
        "agreement": _agreement_metrics(records, config),
    }


# Metrics the README names a winner for, and whether more is better.
WINNER_METRICS: tuple[tuple[str, bool], ...] = (
    ("cited_url_match", True),
    ("cited_anchor_match", True),
    ("citation_verification_rate", True),
    ("unverified_citations_per_answer", False),
    ("refusal_correct", True),
    ("correctness", True),
    ("groundedness", True),
    ("citation_relevance", True),
    ("latency_p50_s", False),
    ("usd", False),
    ("reference_usd", False),
)


def winners(by_strategy: Mapping[str, Any]) -> dict[str, str | None]:
    """The best strategy on each metric, over all question types."""
    result: dict[str, str | None] = {}
    for metric, higher_is_better in WINNER_METRICS:
        scored = [
            (strategy, cells["all"][metric])
            for strategy, cells in by_strategy.items()
            if cells["all"].get(metric) is not None
        ]
        if not scored:
            result[metric] = None
            continue
        best = (
            max(scored, key=lambda pair: pair[1])
            if higher_is_better
            else min(scored, key=lambda pair: pair[1])
        )
        result[metric] = best[0]
    return result
