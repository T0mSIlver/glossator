"""Judging a stored run again without touching any answer."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import structlog

from glossator.eval.answer_eval.judge import (
    JUDGE_MAX_TOKENS,
    JUDGE_TEMPERATURE,
    judge_with_models,
    make_judge_providers,
)
from glossator.eval.answer_eval.models import JudgeModel, QuestionRecord
from glossator.eval.answer_eval.prompts import JUDGE_PROMPT_HASHES, JUDGE_VERSION
from glossator.eval.answer_eval.quota import QUOTA_CEILING_PERCENT, wait_for_quota
from glossator.eval.answer_eval.run_dir import RunDirectory
from glossator.eval.providers.client import OpenAICompatibleProvider
from glossator.eval.providers.models import ProviderName

logger = structlog.get_logger(__name__)


def _archive_old_judges(record: QuestionRecord, config: Mapping[str, Any]) -> QuestionRecord:
    archived = dict(record.judges_v1)
    for identifier, judgement in record.judges.items():
        if judgement.prompt_version != JUDGE_VERSION:
            archived.setdefault(identifier, judgement)
    if record.judge is not None and record.judge.prompt_version != JUDGE_VERSION:
        provider = record.judge.provider or config.get("judge_provider") or "zai"
        archived.setdefault(f"{provider}:{record.judge.model}", record.judge)
    current = {
        identifier: judgement
        for identifier, judgement in record.judges.items()
        if judgement.prompt_version == JUDGE_VERSION
    }
    primary = (
        record.judge if record.judge and record.judge.prompt_version == JUDGE_VERSION else None
    )
    return record.model_copy(update={"judge": primary, "judges": current, "judges_v1": archived})


async def _rejudge_record(
    record: QuestionRecord,
    judges: Sequence[JudgeModel],
    providers: Mapping[ProviderName, OpenAICompatibleProvider],
) -> QuestionRecord:
    judgements = dict(record.judges)
    missing = [
        judge
        for judge in judges
        if judge.identifier not in judgements or judgements[judge.identifier].verdict is None
    ]
    if missing:
        judgements.update(await judge_with_models(record, missing, providers))
    return record.model_copy(
        update={"judge": judgements[judges[0].identifier], "judges": judgements}
    )


async def rejudge(
    run_path: Path,
    *,
    judge_models: Sequence[JudgeModel],
    labels: Path | None = None,
    quota_ceiling: int = QUOTA_CEILING_PERCENT,
) -> dict[str, Any]:
    """Replace a run's current judgements without changing any answer."""
    if not (run_path / "records.jsonl").is_file():
        raise ValueError(f"run has no records.jsonl: {run_path}")
    config = json.loads((run_path / "config.json").read_text())
    archive_config = dict(config)
    config.update(
        {
            "judge_model": judge_models[0].identifier,
            "judge_models": [judge.identifier for judge in judge_models],
            "judge_prompt_version": JUDGE_VERSION,
            "judge_prompt_hashes": JUDGE_PROMPT_HASHES,
            "judge_temperature": JUDGE_TEMPERATURE,
            "judge_max_tokens": JUDGE_MAX_TOKENS,
            "judge_thinking": {
                judge.identifier: "disabled" if judge.provider == "zai" else None
                for judge in judge_models
            },
            "judge_provider": None,
            "labels": str(labels) if labels is not None else config.get("labels"),
        }
    )
    run_dir = RunDirectory.open(run_path, config)
    records = [_archive_old_judges(record, archive_config) for record in run_dir.records]
    if any(judge.provider == "zai" for judge in judge_models):
        await wait_for_quota(quota_ceiling)
    providers = make_judge_providers(judge_models, run_dir)
    try:
        for start in range(0, len(records), 4):
            stop = min(start + 4, len(records))
            records[start:stop] = await asyncio.gather(
                *(
                    _rejudge_record(record, judge_models, providers)
                    for record in records[start:stop]
                )
            )
            run_dir.replace_records(records)
            logger.info("Re-judge checkpoint", run=str(run_path), judged=stop, total=len(records))
    finally:
        await asyncio.gather(*(provider.aclose() for provider in providers.values()))
    return run_dir.finalize(status="complete", error=None)
