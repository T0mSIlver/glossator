"""Grading one recorded answer with every configured judge model."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Mapping, Sequence

import structlog

from glossator.answer.citations import Trace
from glossator.eval.answer_eval.models import (
    JudgedCitation,
    JudgeInput,
    JudgeModel,
    JudgeRecord,
    JudgeVerdict,
    QuestionRecord,
)
from glossator.eval.answer_eval.prompts import JUDGE_SYSTEM, JUDGE_VERSION
from glossator.eval.answer_eval.run_dir import JudgeCallRecorder, RunDirectory
from glossator.eval.datasets import EvalQuestion
from glossator.eval.providers import (
    OpenAICompatibleProvider,
    ProviderCallError,
    ProviderName,
    call_scope,
    candidate_scope,
)

logger = structlog.get_logger(__name__)


JUDGE_TEMPERATURE = 0.0
JUDGE_MAX_TOKENS = 1200
JUDGE_PROVIDER_ATTEMPTS = 3


def source_texts(trace: Trace | None) -> dict[int, str]:
    """The text of each numbered source, cut out of the context the model saw.

    `Trace.context_text` is the assembled context verbatim, and every source in
    it opens with the line `[n] <citation url>`. Locating those lines in order
    recovers each source's passage without re-running retrieval, which is what
    lets the judge be shown the cited text rather than asked to trust a quote.

    The heading path line stays on the passage: it is what the model saw, and it
    is what tells a judge reading a chunk from the middle of a page what section
    the chunk is from.
    """
    if trace is None or not trace.context_text:
        return {}
    text = trace.context_text
    marks: list[tuple[int, int, int]] = []
    cursor = 0
    for source in trace.sources:
        marker = f"[{source.n}] {source.citation_url}\n"
        start = text.find(marker, cursor)
        if start < 0:
            continue
        marks.append((source.n, start, start + len(marker)))
        cursor = start + len(marker)
    passages: dict[int, str] = {}
    for index, (n, _start, body) in enumerate(marks):
        end = marks[index + 1][1] if index + 1 < len(marks) else len(text)
        passages[n] = text[body:end].strip()
    return passages


def judge_input(question: EvalQuestion, record: QuestionRecord) -> JudgeInput:
    """What the judge is shown for one answer."""
    return _judge_input(
        question=question.question,
        reference_answer=question.reference_answer,
        record=record,
    )


def judge_input_from_record(record: QuestionRecord) -> JudgeInput:
    """Reconstruct judge input without reading or changing the answer dataset."""
    return _judge_input(
        question=record.question,
        reference_answer=record.reference_answer,
        record=record,
    )


def _judge_input(*, question: str, reference_answer: str, record: QuestionRecord) -> JudgeInput:
    passages = source_texts(record.trace)
    return JudgeInput(
        question=question,
        reference_answer=reference_answer,
        answer_markdown=record.answer_markdown,
        citations=[
            JudgedCitation(
                n=citation.n,
                quote=citation.quote,
                source_text=passages.get(citation.n, "(the passage was not recorded)"),
            )
            for citation in record.citations
        ],
    )


async def judge_one(
    record: QuestionRecord,
    *,
    provider: OpenAICompatibleProvider,
    model: str,
) -> JudgeRecord:
    """Grade one answer. The judge never learns which strategy wrote it."""
    payload = judge_input_from_record(record)
    rendered = payload.render()
    started = time.perf_counter()
    with candidate_scope(f"{record.question_id}:{record.strategy}"), call_scope("judge"):
        for attempt in range(JUDGE_PROVIDER_ATTEMPTS):
            try:
                completion = await provider.complete(
                    [
                        {"role": "system", "content": JUDGE_SYSTEM},
                        {"role": "user", "content": rendered},
                    ],
                    model=model,
                    temperature=JUDGE_TEMPERATURE,
                    max_tokens=JUDGE_MAX_TOKENS,
                    response_schema=JudgeVerdict,
                    thinking="disabled" if provider.name == "zai" else None,
                )
                break
            except ProviderCallError as error:
                last = attempt == JUDGE_PROVIDER_ATTEMPTS - 1
                if last or "HTTP 429" not in str(error):
                    return JudgeRecord(
                        model=model,
                        provider=provider.name,
                        prompt_version=JUDGE_VERSION,
                        input_text=rendered,
                        error=str(error),
                        latency_ms=(time.perf_counter() - started) * 1000,
                    )
                delay = (5.0 if provider.name == "zai" else 20.0) * (attempt + 1)
                logger.warning(
                    "Judge rate limited, backing off",
                    provider=provider.name,
                    model=model,
                    delay=delay,
                )
                await asyncio.sleep(delay)
    verdict = completion.parsed if isinstance(completion.parsed, JudgeVerdict) else None
    return JudgeRecord(
        model=model,
        provider=provider.name,
        prompt_version=JUDGE_VERSION,
        input_text=rendered,
        raw_output=completion.text,
        verdict=verdict,
        error=None if verdict else "the judge's output did not validate",
        latency_ms=(time.perf_counter() - started) * 1000,
        usage=completion.usage,
    )


def make_judge_providers(
    judges: Sequence[JudgeModel], run_dir: RunDirectory
) -> dict[ProviderName, OpenAICompatibleProvider]:
    """One shared, provider-throttled client for all configured judges."""
    providers: dict[ProviderName, OpenAICompatibleProvider] = {}
    for name in {judge.provider for judge in judges}:
        providers[name] = OpenAICompatibleProvider(
            name,
            asyncio.Semaphore({"zai": 4, "local": 2}.get(name, 1)),
            caller_tag="eval.answer_eval",
            recorder=JudgeCallRecorder(run_dir),
            seed=0,
            minimum_interval=1.05 if name == "mistral" else 0.0,
        )
    return providers


async def judge_with_models(
    record: QuestionRecord,
    judges: Sequence[JudgeModel],
    providers: Mapping[ProviderName, OpenAICompatibleProvider],
) -> dict[str, JudgeRecord]:
    """Judge one recorded answer with every requested model."""
    results = await asyncio.gather(
        *(
            judge_one(record, provider=providers[judge.provider], model=judge.model)
            for judge in judges
        )
    )
    return {judge.identifier: result for judge, result in zip(judges, results, strict=True)}
