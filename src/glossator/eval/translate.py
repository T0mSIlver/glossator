"""Translate a stratified subset of an evaluation set into French.

The corpus is English only, so the generators produce English questions. D-008
asks how the engine fares on French questions over English pages; this makes
that measurable without a French corpus: the gold sources and the reference
facts stay the same, only the wording changes language.

Usage:
    uv run python -m glossator.eval.translate --dataset eval/dev.jsonl --out eval/dev-fr.jsonl \
        --n 36 --provider zai --model glm-5.3 --seed 0 --name dev-fr
"""

from __future__ import annotations

import argparse
import asyncio
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict

from glossator.eval.datasets import EvalQuestion, read_jsonl, write_jsonl
from glossator.eval.providers.client import OpenAICompatibleProvider
from glossator.eval.providers.models import ProviderName
from glossator.eval.providers.scopes import call_scope, candidate_scope
from glossator.eval.run_records import RunRecorder, create_run_directory

PROMPT_VERSION = "translate-v1"
SYSTEM = (
    "You translate evaluation questions about Mistral AI's platform documentation from English "
    "into natural French, as a French-speaking developer would ask them. Keep every identifier, "
    "API name, parameter, model name, code, URL and number exactly as written. Do not add or "
    "remove information. Return JSON only."
)


class Translation(BaseModel):
    model_config = ConfigDict(frozen=True)

    question_fr: str
    reference_answer_fr: str


class TranslationRow(BaseModel):
    model_config = ConfigDict(frozen=True)

    candidate_id: str
    source_id: str
    kept: bool
    drop_reasons: list[str]
    question: EvalQuestion | None = None


def stratified(questions: list[EvalQuestion], n: int, seed: int) -> list[EvalQuestion]:
    """Round-robin over types after a seeded shuffle, so every type is represented."""
    rng = random.Random(seed)
    by_type: dict[str, list[EvalQuestion]] = defaultdict(list)
    for question in questions:
        by_type[question.type.value].append(question)
    for rows in by_type.values():
        rng.shuffle(rows)
    picked: list[EvalQuestion] = []
    while len(picked) < n and any(by_type.values()):
        for key in sorted(by_type):
            if by_type[key] and len(picked) < n:
                picked.append(by_type[key].pop())
    return picked


async def translate_one(
    provider: OpenAICompatibleProvider, question: EvalQuestion, *, model: str
) -> Translation:
    user = json.dumps(
        {"question": question.question, "reference_answer": question.reference_answer},
        ensure_ascii=False,
    )
    with candidate_scope(question.id), call_scope("translate"):
        completion = await provider.complete(
            [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
            model=model,
            temperature=0.2,
            max_tokens=600,
            response_schema=Translation,
            thinking="disabled" if provider.name == "zai" else None,
        )
    parsed = completion.parsed
    if not isinstance(parsed, Translation):
        raise RuntimeError("translation did not parse")
    return parsed


async def run(args: argparse.Namespace) -> dict[str, Any]:
    questions = read_jsonl(Path(args.dataset))
    subset = stratified(questions, args.n, args.seed)
    run_dir = create_run_directory(args.name)
    config = {
        "kind": "translate",
        "dataset": args.dataset,
        "n": args.n,
        "seed": args.seed,
        "provider": args.provider,
        "model": args.model,
        "prompt_version": PROMPT_VERSION,
        "target_language": "fr",
    }
    recorder = RunRecorder.start(run_dir, config)
    provider_name: ProviderName = args.provider
    translated: list[EvalQuestion] = []
    async with OpenAICompatibleProvider(
        provider_name,
        asyncio.Semaphore(args.concurrency),
        caller_tag="eval.translate",
        recorder=recorder,
        seed=args.seed,
    ) as provider:
        for question in subset:
            try:
                result = await translate_one(provider, question, model=args.model)
            except Exception as error:  # noqa: BLE001 - one failed row must not lose the run
                recorder.record_candidate(
                    TranslationRow(
                        candidate_id=question.id,
                        source_id=question.id,
                        kept=False,
                        drop_reasons=[f"provider_error: {type(error).__name__}: {error}"],
                    )
                )
                continue
            generator = dict(question.generator or {})
            generator.update({"translated_from": question.id, "translation_prompt": PROMPT_VERSION})
            new = question.model_copy(
                update={
                    "id": f"{question.id}-fr",
                    "question": result.question_fr,
                    "reference_answer": result.reference_answer_fr,
                    "language": "fr",
                    "generator": generator,
                }
            )
            translated.append(new)
            recorder.record_candidate(
                TranslationRow(
                    candidate_id=question.id,
                    source_id=question.id,
                    kept=True,
                    drop_reasons=[],
                    question=new,
                )
            )
    out = Path(args.out)
    write_jsonl(out, translated)
    recorder.finalize(dataset_path=out, error=None)
    return {
        "written": len(translated),
        "out": str(out),
        "run_dir": str(run_dir),
        **recorder.usage_line(),
    }


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Translate an evaluation subset into French")
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--n", type=int, default=36)
    parser.add_argument("--provider", choices=["zai", "mistral"], default="zai")
    parser.add_argument("--model", default="glm-5.3")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--concurrency", type=int, default=4)
    print(json.dumps(asyncio.run(run(parser.parse_args())), ensure_ascii=False))


if __name__ == "__main__":
    main()
