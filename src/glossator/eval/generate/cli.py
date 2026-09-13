"""Command line: generate a dataset, or dry-run the sources it would ask about."""

from __future__ import annotations

import argparse
import asyncio
import json
import random
from collections.abc import Sequence
from pathlib import Path
from typing import cast

from dotenv import load_dotenv

from glossator.eval.corpus import CorpusDocument, load_documents
from glossator.eval.datasets import validate_against_corpus, write_jsonl
from glossator.eval.generate.models import (
    CHECK_MAX_TOKENS,
    CHECK_TEMPERATURE,
    GENERATED_TYPES,
    GENERATION_MAX_TOKENS,
    GENERATION_TEMPERATURE,
    MAX_SOURCE_CHARS,
    MIN_SECTION_TOKENS,
    UNANSWERABLE_CHECK_TOP_K,
)
from glossator.eval.generate.planning import plan_attempts
from glossator.eval.generate.prompts import PROMPT_HASHES, PROMPT_VERSION
from glossator.eval.generate.run import generate_questions, type_allocations
from glossator.eval.providers import OpenAICompatibleProvider, ProviderName, ThinkingMode
from glossator.eval.run_records import RunRecorder, create_run_directory
from glossator.ingest.pages import read_manifest


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a documentation evaluation set")
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--name")
    parser.add_argument("--n", type=int, default=300)
    parser.add_argument("--provider", choices=("zai", "mistral"), default="zai")
    parser.add_argument("--model", default="glm-5.3-flash")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--concurrency", type=int, default=8)
    parser.add_argument(
        "--attempts-per-question",
        type=int,
        default=4,
        help="candidates generated per requested question before a type is left short",
    )
    parser.add_argument("--thinking", choices=("enabled", "disabled"), default="disabled")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print what the run would sample, call nothing and write nothing",
    )
    return parser.parse_args()


def _dry_run(documents: Sequence[CorpusDocument], args: argparse.Namespace) -> None:
    """Show the sources a real run with these arguments would ask about."""
    rng = random.Random(args.seed)
    allocations = type_allocations(args.n)
    for question_type in GENERATED_TYPES:
        budget = allocations[question_type] * args.attempts_per_question
        for plan in plan_attempts(documents, question_type, budget, rng):
            print(
                json.dumps(
                    {
                        "type": question_type.value,
                        "candidate_id": plan.candidate_id,
                        "sources": [
                            {
                                "url": source.url,
                                "anchor": source.anchor,
                                "heading_path": source.heading_path,
                            }
                            for source in plan.sources
                        ],
                    }
                )
            )


async def _run(args: argparse.Namespace) -> None:
    documents = load_documents(args.corpus)
    if args.dry_run:
        _dry_run(documents, args)
        return

    run_name = args.name or (args.out.stem if args.out else "generate")
    run_dir = create_run_directory(run_name)
    dataset_path = args.out or run_dir / "questions.jsonl"
    corpus_commits = sorted({document.page.source_commit for document in documents})
    # z.ai is the only provider that takes a thinking setting; sending it to
    # Mistral is an error, and D-020 and D-021 both rest on this being swappable.
    thinking = cast(ThinkingMode, args.thinking) if args.provider == "zai" else None
    config = {
        "name": run_name,
        "run_dir": str(run_dir),
        "corpus": str(args.corpus),
        "corpus_commit": corpus_commits[0] if len(corpus_commits) == 1 else corpus_commits,
        "out": str(dataset_path),
        "n": args.n,
        "provider": args.provider,
        "model": args.model,
        "thinking": thinking,
        "seed": args.seed,
        "concurrency": args.concurrency,
        "attempts_per_question": args.attempts_per_question,
        "prompt_version": PROMPT_VERSION,
        "prompt_hashes": PROMPT_HASHES,
        "cache_dir": ".cache/llm",
        "minimum_section_tokens": MIN_SECTION_TOKENS,
        "max_source_chars": MAX_SOURCE_CHARS,
        "generation_temperature": GENERATION_TEMPERATURE,
        "generation_max_tokens": GENERATION_MAX_TOKENS,
        "check_temperature": CHECK_TEMPERATURE,
        "check_max_tokens": CHECK_MAX_TOKENS,
        "unanswerable_check_top_k": UNANSWERABLE_CHECK_TOP_K,
        "http_attempts": 3,
        "structured_output_repairs": 1,
    }
    recorder = RunRecorder.start(run_dir, config)
    try:
        async with OpenAICompatibleProvider(
            cast(ProviderName, args.provider),
            asyncio.Semaphore(args.concurrency),
            caller_tag="eval.generate",
            recorder=recorder,
            seed=args.seed,
        ) as provider:
            questions, _attempts, results = await generate_questions(
                provider,
                documents,
                n=args.n,
                model=args.model,
                seed=args.seed,
                thinking=thinking,
                attempts_per_question=args.attempts_per_question,
                recorder=recorder,
            )
        manifest_path = args.corpus / "manifest.json"
        if manifest_path.exists():
            issues = validate_against_corpus(
                questions,
                read_manifest(args.corpus),
                [document.page for document in documents],
            )
            if issues:
                raise RuntimeError(
                    "generated questions contain invalid gold sources: "
                    + "; ".join(issue.message for issue in issues)
                )
        write_jsonl(dataset_path, questions)
    except Exception as error:
        recorder.finalize(dataset_path=None, error=str(error))
        raise
    recorder.finalize(
        dataset_path=dataset_path,
        error=None,
        shortfalls={
            result.question_type.value: result.shortfall for result in results if result.shortfall
        },
        requested_by_type={result.question_type.value: result.requested for result in results},
    )
    print(
        json.dumps(
            {
                "written": len(questions),
                "out": str(dataset_path),
                "run_dir": str(run_dir),
                "requested": {result.question_type.value: result.requested for result in results},
                "accepted": {result.question_type.value: result.accepted for result in results},
                "shortfall": {
                    result.question_type.value: result.shortfall
                    for result in results
                    if result.shortfall
                },
                "usage": recorder.usage_line(),
            }
        )
    )


def main() -> None:
    # Not override=True: an operator who exports a key for one run should not
    # have it replaced by whatever .env holds.
    load_dotenv()
    asyncio.run(_run(_parse_args()))
