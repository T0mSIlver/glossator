"""The reference-defect judge: optional, one call per flagged failure."""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Sequence
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from glossator.eval.failures.corpus import gold_section_text
from glossator.eval.failures.evidence import page_url
from glossator.eval.failures.models import (
    AnalysedRun,
    DefectJudgement,
    DefectVerdict,
    FailureRecord,
)
from glossator.eval.failures.prompts import DEFECT_SYSTEM, DEFECT_USER, DEFECT_VERSION
from glossator.eval.providers.client import OpenAICompatibleProvider
from glossator.eval.providers.models import ProviderCallError, ProviderName
from glossator.eval.providers.scopes import call_scope, candidate_scope
from glossator.index.variants import VARIANTS

DEFECT_MAX_TOKENS = 500
DEFECT_ATTEMPTS = 3
DEFECT_SECTION_CHARS = 12000
"""How much gold section text one judgement carries. A whole unanchored page can
run past a judge's context, and the reference answers this checks are two lines."""


def parse_judge_model(value: str) -> tuple[ProviderName, str]:
    """`provider:model` from the command line, with the same providers as the answer judge."""
    provider, separator, model = value.partition(":")
    if separator != ":" or provider not in ("zai", "mistral", "local") or not model.strip():
        raise ValueError(
            f"invalid judge model {value!r}; expected provider:model with provider "
            "zai, mistral or local"
        )
    return provider, model.strip()  # type: ignore[return-value]


def defect_input(failure: FailureRecord, reference_answer: str, section_text: str) -> str:
    return DEFECT_USER.format(
        question=failure.question,
        reference_answer=reference_answer,
        section_text=section_text[:DEFECT_SECTION_CHARS] or "(no gold section text was found)",
    )


async def judge_defect(
    failure: FailureRecord,
    *,
    reference_answer: str,
    section_text: str,
    provider: OpenAICompatibleProvider,
    model: str,
) -> DefectJudgement:
    """Ask one judge whether the dataset's reference answer is in the gold section."""
    rendered = defect_input(failure, reference_answer, section_text)
    started = time.perf_counter()
    scope = f"{failure.question_id}:{failure.strategy}"
    with candidate_scope(scope), call_scope("reference_defect"):
        for attempt in range(DEFECT_ATTEMPTS):
            try:
                completion = await provider.complete(
                    [
                        {"role": "system", "content": DEFECT_SYSTEM},
                        {"role": "user", "content": rendered},
                    ],
                    model=model,
                    temperature=0.0,
                    max_tokens=DEFECT_MAX_TOKENS,
                    response_schema=DefectVerdict,
                    thinking="disabled" if provider.name == "zai" else None,
                )
                break
            except ProviderCallError as error:
                if attempt == DEFECT_ATTEMPTS - 1 or "HTTP 429" not in str(error):
                    return DefectJudgement(
                        model=model,
                        provider=provider.name,
                        prompt_version=DEFECT_VERSION,
                        input_text=rendered,
                        error=str(error),
                        latency_ms=(time.perf_counter() - started) * 1000,
                    )
                await asyncio.sleep((5.0 if provider.name == "zai" else 20.0) * (attempt + 1))
    verdict = completion.parsed if isinstance(completion.parsed, DefectVerdict) else None
    return DefectJudgement(
        model=model,
        provider=provider.name,
        prompt_version=DEFECT_VERSION,
        input_text=rendered,
        raw_output=completion.text,
        verdict=verdict,
        error=None if verdict else "the judge's output did not validate",
        latency_ms=(time.perf_counter() - started) * 1000,
        usage=completion.usage,
    )


class DefectCallRecorder:
    """The provider's `CallRecorder`, writing into this run's `calls.jsonl` (D-023)."""

    def __init__(self, calls_path: Path) -> None:
        self.calls_path = calls_path

    def record_call(self, **row: Any) -> None:
        payload: dict[str, Any] = {"source": "judge", "timestamp": datetime.now(UTC).isoformat()}
        for key, value in row.items():
            if isinstance(value, BaseModel):
                payload[key] = value.model_dump(mode="json")
            elif key == "messages":
                payload[key] = [dict(message) for message in value]
            else:
                payload[key] = value
        with self.calls_path.open("a") as handle:
            handle.write(json.dumps(payload, sort_keys=True, default=str) + "\n")


async def judge_flagged(
    runs: Sequence[AnalysedRun],
    *,
    judge: tuple[ProviderName, str],
    calls_path: Path,
    corpus_dir: Path,
) -> list[AnalysedRun]:
    """Ask the judge about every flagged failure, one call each, all recorded."""
    provider_name, model = judge
    provider = OpenAICompatibleProvider(
        provider_name,
        asyncio.Semaphore({"zai": 4, "local": 2}.get(provider_name, 1)),
        caller_tag="eval.failures",
        recorder=DefectCallRecorder(calls_path),
        seed=0,
        minimum_interval=1.05 if provider_name == "mistral" else 0.0,
    )
    judged: list[AnalysedRun] = []
    try:
        for run in runs:
            chunking = VARIANTS[run.variant].chunking
            rows: list[FailureRecord] = []
            for failure in run.failures:
                if not failure.reference_defect_suspected or not failure.gold_urls:
                    rows.append(failure)
                    continue
                anchor = failure.gold_anchors[0] if failure.gold_anchors else None
                judgement = await judge_defect(
                    failure,
                    reference_answer=run.reference_answers.get(
                        (failure.question_id, failure.strategy), ""
                    ),
                    section_text=gold_section_text(
                        corpus_dir, chunking, page_url(failure.gold_urls[0]), anchor
                    ),
                    provider=provider,
                    model=model,
                )
                rows.append(failure.model_copy(update={"defect_judgement": judgement}))
            judged.append(replace(run, failures=tuple(rows)))
    finally:
        await provider.aclose()
    return judged
