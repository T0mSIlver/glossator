"""The judge a cell falls back to when no span decides it deterministically."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from glossator.eval.datasets import EvalQuestion
from glossator.eval.providers import OpenAICompatibleProvider
from glossator.eval.snapshots.models import PRIMARY_JUDGE, SECONDARY_JUDGE, FactVerdict
from glossator.eval.snapshots.prompts import JUDGE_SYSTEM


class LabelCallRecorder:
    def __init__(self, path: Path) -> None:
        self.path = path

    def record_call(self, **row: Any) -> None:
        encoded: dict[str, Any] = {}
        for key, value in row.items():
            if isinstance(value, BaseModel):
                encoded[key] = value.model_dump(mode="json")
            elif key == "messages":
                encoded[key] = [dict(message) for message in value]
            else:
                encoded[key] = value
        with self.path.open("a") as handle:
            handle.write(json.dumps(encoded, sort_keys=True) + "\n")


def _judge_prompt(question: EvalQuestion, pages: Sequence[Mapping[str, str]]) -> str:
    rendered = "\n\n".join(
        f"PAGE {index}: {page['url']}\n{page['text']}" for index, page in enumerate(pages, 1)
    )
    return (
        f"QUESTION\n{question.question}\n\nREFERENCE ANSWER\n{question.reference_answer}"
        f"\n\nOLDER DOCUMENTATION\n{rendered or '(no lexical match)'}"
    )


async def judge_cell(
    question: EvalQuestion,
    pages: list[dict[str, str]],
    providers: Mapping[str, OpenAICompatibleProvider],
) -> tuple[str, dict[str, Any]]:
    prompt = _judge_prompt(question, pages)

    async def call(model: str) -> tuple[str, dict[str, Any]]:
        completion = await providers[model].complete(
            [{"role": "system", "content": JUDGE_SYSTEM}, {"role": "user", "content": prompt}],
            model=model,
            temperature=0.0,
            max_tokens=800,
            response_schema=FactVerdict,
            thinking="disabled",
        )
        verdict = completion.parsed
        if not isinstance(verdict, FactVerdict):
            raise ValueError(f"{model} returned no valid fact verdict")
        return model, {
            "classification": verdict.classification,
            "reason": verdict.reason,
            "page": verdict.page,
            "evidence": verdict.evidence,
            "raw": completion.text,
            "usage": completion.usage.model_dump(mode="json"),
            "cached": completion.cached,
        }

    judged = dict(await asyncio.gather(call(PRIMARY_JUDGE), call(SECONDARY_JUDGE)))
    primary = judged[PRIMARY_JUDGE]["classification"]
    label = {
        "stated": "present_rephrased",
        "different_value": "changed",
        "not_stated": "absent",
    }[primary]
    return label, judged
