"""Answering and judging every pending (question, strategy) pair of a run."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Sequence
from typing import Any

import structlog

from glossator.answer.citations import Answer
from glossator.answer.config import AnswerConfig
from glossator.answer.llm import MistralLLM
from glossator.answer.service import ask
from glossator.clients import chat_client
from glossator.eval.answer_eval.judge import judge_with_models, make_judge_providers
from glossator.eval.answer_eval.models import JudgeModel, QuestionRecord
from glossator.eval.answer_eval.quota import QUOTA_CEILING_PERCENT, wait_for_quota
from glossator.eval.answer_eval.run_dir import AnswerCallRecorder, RunDirectory, answer_scope
from glossator.eval.datasets import EvalQuestion
from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.engine import SearchEngine

logger = structlog.get_logger(__name__)


async def answer_one(
    question: EvalQuestion,
    strategy: str,
    *,
    variant: str,
    model: str,
    settings: AnswerConfig,
    engine: SearchEngine,
    llm: MistralLLM,
) -> QuestionRecord:
    """One (question, strategy) pair, whatever happens to it.

    A strategy that raises is recorded with its error rather than killing the
    run: a run of thirty-six answers must not be lost to one timeout, and an
    error that is not in the records is an error nobody can count.
    """
    base = QuestionRecord(
        question_id=question.id,
        question=question.question,
        question_type=question.type.value,
        language=question.language,
        gold_urls=[gold.url for gold in question.gold],
        gold_anchors=[gold.anchor for gold in question.gold],
        reference_answer=question.reference_answer,
        strategy=strategy,
        variant=variant,
        model=model,
    )
    started = time.perf_counter()
    with answer_scope(question.id, strategy):
        try:
            answer: Answer = await ask(
                question.question,
                strategy=strategy,
                variant=variant,
                model=model,
                config=settings,
                engine=engine,
                llm=llm,
            )
        except Exception as error:  # noqa: BLE001 - recorded, then the run goes on
            logger.warning(
                "Answer failed", question=question.id, strategy=strategy, error=str(error)
            )
            return base.model_copy(
                update={
                    "error": f"{type(error).__name__}: {error}",
                    "latency_ms": (time.perf_counter() - started) * 1000,
                }
            )
    return base.model_copy(
        update={
            "answer_markdown": answer.answer_markdown,
            "citations": answer.citations,
            "unverified_citations": answer.trace.unverified_citations,
            "insufficient_evidence": answer.insufficient_evidence,
            "trace": answer.trace,
            "usage": answer.usage,
            "latency_ms": answer.latency_ms,
            "cost_usd": answer.cost_usd,
        }
    )


async def run(
    questions: Sequence[EvalQuestion],
    *,
    strategies: Sequence[str],
    variant: str,
    model: str,
    judge_models: Sequence[JudgeModel],
    run_dir: RunDirectory,
    settings: AnswerConfig,
    quota_ceiling: int = QUOTA_CEILING_PERCENT,
    rerank: bool = True,
    retry_errors: bool = False,
) -> dict[str, Any]:
    """Every question through every strategy, judged, recorded, summarized.

    Questions run one at a time: the Mistral account is on the free tier, where
    concurrency buys 429s rather than throughput (D-028).

    ``retry_errors`` regenerates the rows whose record carries an error -- the
    429s and timeouts a resumed run would otherwise keep forever -- and leaves
    every answered row alone.
    """
    if retry_errors:
        dropped = run_dir.drop_error_records()
        if dropped:
            logger.info("Dropping error rows for regeneration", records=dropped)
    done = run_dir.done
    pending = [
        (question, strategy)
        for question in questions
        for strategy in strategies
        if (question.id, strategy) not in done
    ]
    logger.info("Answer eval", pending=len(pending), recorded=len(done), run_dir=str(run_dir.path))
    if any(judge.provider == "zai" for judge in judge_models):
        await wait_for_quota(quota_ceiling)

    # One recorder for both layers: the reranker's calls belong in the run's
    # calls.jsonl beside the generation calls (D-023). Before this the engine had
    # no recorder, so every reranker call made during an answer run went
    # unrecorded and the run's cost understated the Mistral spend.
    recorder = AnswerCallRecorder(run_dir)
    engine = SearchEngine(
        RetrievalConfig.shipped(variant=variant, top_k=settings.top_k, rerank=rerank),
        recorder=recorder,
    )
    llm = MistralLLM(settings, client=chat_client(), recorder=recorder)
    providers = make_judge_providers(judge_models, run_dir)
    try:
        for question, strategy in pending:
            record = await answer_one(
                question,
                strategy,
                variant=variant,
                model=model,
                settings=settings,
                engine=engine,
                llm=llm,
            )
            if judge_models and record.error is None:
                judgements = await judge_with_models(record, judge_models, providers)
                record = record.model_copy(
                    update={"judge": judgements[judge_models[0].identifier], "judges": judgements}
                )
            run_dir.record(record)
    finally:
        await asyncio.gather(*(provider.aclose() for provider in providers.values()))
    return run_dir.finalize(status="complete", error=None)
