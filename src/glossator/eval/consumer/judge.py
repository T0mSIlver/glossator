"""Blind judging of the collected answers, resumable across quota windows."""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from glossator.eval.answer_eval.judge import JUDGE_MAX_TOKENS, JUDGE_TEMPERATURE
from glossator.eval.answer_eval.models import (
    JudgedCitation,
    JudgeInput,
    JudgeModel,
    JudgeRecord,
    JudgeVerdict,
)
from glossator.eval.answer_eval.prompts import JUDGE_SYSTEM, JUDGE_VERSION
from glossator.eval.answer_eval.quota import wait_for_quota
from glossator.eval.consumer.models import ConsumerRecord, load_records
from glossator.eval.consumer.tools import is_verify_tool
from glossator.eval.providers import (
    OpenAICompatibleProvider,
    ProviderCallError,
    call_scope,
    candidate_scope,
)


class _CallsRecorder:
    """The provider's CallRecorder, writing judge calls into the run.

    The provider hands over pydantic models (`usage`, `parsed`) and message
    sequences. Falling back to ``str`` for those wrote their Python repr into
    the ledger, so the token counts D-023b exists to make countable were not
    machine-readable; they are dumped as JSON instead.
    """

    def __init__(self, run_dir: Path) -> None:
        self.path = run_dir / "calls.jsonl"

    def record_call(self, **row: Any) -> None:
        serializable: dict[str, Any] = {"timestamp": datetime.now(UTC).isoformat()}
        for key, value in row.items():
            if isinstance(value, BaseModel):
                serializable[key] = value.model_dump(mode="json")
            elif key == "messages":
                serializable[key] = [dict(message) for message in value]
            else:
                serializable[key] = json.loads(json.dumps(value, sort_keys=True, default=str))
        with self.path.open("a") as handle:
            handle.write(json.dumps(serializable, sort_keys=True) + "\n")


def judged_citations(record: ConsumerRecord) -> list[JudgedCitation]:
    """Citations as the blind judge sees them: the verified quote and the
    passage behind it.

    A consumer answer has no served context the harness kept, so the only
    evidence the judge can check a claim against is the quote the server
    verified. The passage is that quote verbatim: groundedness then measures
    whether each claim follows from the sentences the answer cites, which is
    the honest reading for an answer whose evidence is quotes, not pages.
    """
    citations: list[JudgedCitation] = []
    for call in record.tool_calls:
        if not is_verify_tool(call.name):
            continue
        raw_quotes = call.arguments.get("quotes", "")
        try:
            quotes = json.loads(raw_quotes) if raw_quotes.startswith("[") else []
        except ValueError:
            quotes = []
        try:
            verdicts = json.loads(call.arguments.get("__verdicts", "{}"))
        except ValueError:
            verdicts = {}
        if not isinstance(verdicts, dict):
            verdicts = {}
        for quote in quotes:
            if not isinstance(quote, dict):
                continue
            try:
                number = int(quote.get("n", -1))
            except (TypeError, ValueError):
                continue
            text = quote.get("quote", "")
            if verdicts.get(str(number)) is True and isinstance(text, str) and text.strip():
                citations.append(JudgedCitation(n=number, quote=text, source_text=text))
    return citations


def judge_payload(record: ConsumerRecord) -> JudgeInput:
    return JudgeInput(
        question=record.question,
        reference_answer=record.reference_answer,
        answer_markdown=record.answer_text,
        citations=judged_citations(record),
    )


async def judge_record(
    record: ConsumerRecord,
    *,
    provider: OpenAICompatibleProvider,
    model: str,
) -> JudgeRecord:
    payload = judge_payload(record)
    rendered = payload.render()
    started = time.perf_counter()
    with (
        candidate_scope(f"{record.consumer}:{record.arm}:{record.question_id}"),
        call_scope("judge"),
    ):
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
        except ProviderCallError as error:
            return JudgeRecord(
                model=model,
                provider=provider.name,
                prompt_version=JUDGE_VERSION,
                input_text=rendered,
                error=str(error),
                latency_ms=(time.perf_counter() - started) * 1000,
            )
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


async def run_judge(
    run_dir: Path,
    judge_models: Sequence[JudgeModel],
    *,
    rejudge: bool = False,
    quota_ceiling: int = 80,
) -> dict[str, int]:
    """Grade every unjudged row with the first judge model. Resumes: rows the
    model already graded at this prompt version are skipped."""
    records = load_records(run_dir / "records.jsonl")
    if not judge_models:
        raise SystemExit("no judge models requested")
    primary = judge_models[0]
    pending_ids = {
        id(record)
        for record in records
        if rejudge
        or record.judge is None
        or record.judge.model != primary.model
        or record.judge.prompt_version != JUDGE_VERSION
    }
    counts = {"judged": 0, "skipped": len(records) - len(pending_ids), "errors": 0}
    if not pending_ids:
        return counts
    await wait_for_quota(quota_ceiling)
    recorder = _CallsRecorder(run_dir)
    async with OpenAICompatibleProvider(
        primary.provider,
        asyncio.Semaphore(4 if primary.provider == "zai" else 1),
        caller_tag="eval.consumer",
        recorder=recorder,
        seed=0,
    ) as provider:
        judged: list[ConsumerRecord] = []
        for record in records:
            if id(record) not in pending_ids:
                judged.append(record)
                continue
            result = await judge_record(record, provider=provider, model=primary.model)
            counts["judged"] += 1
            if result.error is not None:
                counts["errors"] += 1
            judged.append(record.model_copy(update={"judge": result}))
    temporary = run_dir / "records.jsonl.tmp"
    temporary.write_text("".join(r.model_dump_json() + "\n" for r in judged))
    temporary.replace(run_dir / "records.jsonl")
    return counts
