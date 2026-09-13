"""Command line: run a dataset, re-judge a run, or reprice one."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from glossator.answer.config import PRICES, AnswerConfig
from glossator.answer.service import STRATEGIES
from glossator.clients import chat_reasoning_effort, chat_sampling, chat_server_url
from glossator.eval.answer_eval.judge import JUDGE_MAX_TOKENS, JUDGE_TEMPERATURE
from glossator.eval.answer_eval.metrics import REFERENCE_PRICING_MODEL, UNPRICED_MODELS
from glossator.eval.answer_eval.models import (
    DEFAULT_GENERATION_MODEL,
    DEFAULT_JUDGE_MODELS,
    parse_judge_models,
)
from glossator.eval.answer_eval.overrides import apply_answer_config, parse_answer_config
from glossator.eval.answer_eval.prompts import JUDGE_PROMPT_HASHES, JUDGE_VERSION
from glossator.eval.answer_eval.quota import QUOTA_CEILING_PERCENT
from glossator.eval.answer_eval.rebuild import recost
from glossator.eval.answer_eval.rejudge import rejudge
from glossator.eval.answer_eval.run import run
from glossator.eval.answer_eval.run_dir import RUNS_ROOT, RunDirectory, resolve_run_directory
from glossator.eval.datasets import dataset_hash, read_jsonl, stratified_subset
from glossator.retrieval.config import RERANK_MODEL


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a question dataset through the answer strategies and score it"
    )
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument(
        "--strategies",
        default="single_pass,search_loop,outline",
        help="Comma-separated strategy names",
    )
    parser.add_argument("--variant", default="sec1024")
    parser.add_argument("--name", required=True, help="Run name; re-running it resumes the run")
    parser.add_argument(
        "--limit",
        type=int,
        help="Run a stratified subset of this many questions instead of the whole dataset",
    )
    parser.add_argument("--seed", type=int, default=0, help="Seed for --limit's sampler")
    parser.add_argument("--model", default=DEFAULT_GENERATION_MODEL)
    parser.add_argument(
        "--judge-models",
        default=DEFAULT_JUDGE_MODELS,
        help="Comma-separated provider-qualified judge models; the first is primary",
    )
    parser.add_argument("--judge-model", help=argparse.SUPPRESS)
    parser.add_argument("--skip-judge", action="store_true")
    parser.add_argument("--labels", type=Path, help="Human correctness labels as JSONL")
    parser.add_argument("--top-k", type=int, default=AnswerConfig().top_k)
    parser.add_argument(
        "--no-translate",
        dest="translate_for_retrieval",
        action="store_false",
        help=(
            "Retrieve a non-English question exactly as it was asked, instead of "
            "rendering it in English first (the shipped default renders it)"
        ),
    )
    parser.add_argument(
        "--rewrite",
        dest="rewrite_for_retrieval",
        action="store_true",
        help=(
            "Reword the question into the documentation's vocabulary before "
            "retrieval (off by default, as it is in the answer layer)"
        ),
    )
    parser.add_argument(
        "--no-rerank",
        dest="rerank",
        action="store_false",
        help="Retrieve without the listwise reranker (the shipped default reranks)",
    )
    parser.add_argument(
        "--answer-config",
        action="append",
        default=[],
        dest="answer_config",
        metavar="KEY=VALUE",
        help=(
            "Override one AnswerConfig field by name (round_cap=6, "
            "searches_per_round=4, tool_result_chars=1500, tool_result_chars=null "
            "for full previews, response_format=json_object); repeatable"
        ),
    )
    parser.add_argument(
        "--retry-errors",
        action="store_true",
        help=(
            "On resume, regenerate the rows whose record carries an error "
            "(429s, timeouts); rows with an answer are kept"
        ),
    )
    parser.add_argument("--runs-root", type=Path, default=RUNS_ROOT)
    parser.add_argument(
        "--note",
        action="append",
        default=[],
        dest="notes",
        help="A sentence of context to render in the run README; repeatable",
    )
    parser.add_argument(
        "--quota-ceiling",
        type=int,
        default=QUOTA_CEILING_PERCENT,
        help="Pause before judging while the z.ai token window is this full",
    )
    return parser.parse_args(argv)


def _parse_rejudge_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Judge the stored answers in an existing run")
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--judge-models", required=True)
    parser.add_argument("--labels", type=Path)
    parser.add_argument(
        "--quota-ceiling",
        type=int,
        default=QUOTA_CEILING_PERCENT,
        help="Pause before judging while the z.ai token window is this full",
    )
    return parser.parse_args(argv)


async def _run(args: argparse.Namespace) -> None:
    strategies = [name.strip() for name in args.strategies.split(",") if name.strip()]
    unknown = sorted(set(strategies) - set(STRATEGIES))
    if unknown:
        raise SystemExit(f"unknown strategy {unknown}; available: {sorted(STRATEGIES)}")

    questions = read_jsonl(args.dataset)
    if args.limit is not None:
        questions = stratified_subset(questions, args.limit, args.seed)
    try:
        overrides = parse_answer_config(args.answer_config)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    if "model" in overrides and overrides["model"] != args.model:
        # The model is a column of every table; letting --answer-config model=...
        # disagree with --model would record two different truths. Refused before
        # the model validates the overrides, so the answer is this sentence and
        # not a validation error about a field the operator may set legitimately.
        raise SystemExit("set the model with --model, not --answer-config")
    settings = apply_answer_config(
        AnswerConfig(
            model=args.model,
            top_k=args.top_k,
            translate_for_retrieval=args.translate_for_retrieval,
            rewrite_for_retrieval=args.rewrite_for_retrieval,
            prices=PRICES,
        ),
        overrides,
    )
    try:
        judge_models = (
            []
            if args.skip_judge
            else parse_judge_models(
                f"zai:{args.judge_model}" if args.judge_model else args.judge_models
            )
        )
    except ValueError as error:
        raise SystemExit(str(error)) from error
    primary_judge = judge_models[0].identifier if judge_models else None

    run_path = resolve_run_directory(args.name, root=args.runs_root)
    config: dict[str, Any] = {
        "kind": "answer_eval",
        "name": args.name,
        "run_dir": str(run_path),
        "dataset": str(args.dataset),
        "dataset_sha256": dataset_hash(args.dataset),
        "questions": [question.id for question in questions],
        "limit": args.limit,
        "seed": args.seed,
        "variant": args.variant,
        "strategies": strategies,
        "model": args.model,
        "judge_model": primary_judge,
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
        "labels": str(args.labels) if args.labels else None,
        "top_k": settings.top_k,
        "rerank": args.rerank,
        "translate_for_retrieval": settings.translate_for_retrieval,
        "rewrite_for_retrieval": settings.rewrite_for_retrieval,
        "rerank_model": RERANK_MODEL if args.rerank else None,
        "context_token_budget": settings.context_token_budget,
        "answer_config": settings.model_dump(mode="json"),
        "answer_config_overrides": overrides,
        "generation_server": chat_server_url(),
        "reasoning_effort": chat_reasoning_effort(),
        "chat_sampling": chat_sampling(),
        "unpriced_models": sorted(UNPRICED_MODELS),
        "reference_pricing_model": REFERENCE_PRICING_MODEL,
        "notes": list(args.notes),
    }
    run_dir = RunDirectory.open(run_path, config)
    try:
        metrics = await run(
            questions,
            strategies=strategies,
            variant=args.variant,
            model=args.model,
            judge_models=judge_models,
            run_dir=run_dir,
            settings=settings,
            quota_ceiling=args.quota_ceiling,
            rerank=args.rerank,
            retry_errors=args.retry_errors,
        )
    except Exception as error:
        run_dir.finalize(status="failed", error=f"{type(error).__name__}: {error}")
        raise
    print(
        json.dumps(
            {
                "run_dir": str(run_path),
                "records": metrics["records"],
                "questions": metrics["questions"],
                "errors": metrics["totals"]["errors"],
                "tokens_in": metrics["totals"]["tokens_in_total"],
                "tokens_out": metrics["totals"]["tokens_out_total"],
                "usd": round(metrics["totals"]["usd_total"], 6),
                "reference_usd": round(metrics["totals"]["reference_usd_total"], 6),
                "winners": metrics["winners"],
            },
            indent=2,
        )
    )


def main() -> None:
    load_dotenv()
    if len(sys.argv) > 1 and sys.argv[1] == "recost":
        parser = argparse.ArgumentParser(description="Reprice a stored answer evaluation")
        parser.add_argument("--run", type=Path, required=True)
        args = parser.parse_args(sys.argv[2:])
        print(json.dumps(recost(args.run), indent=2))
        return
    if len(sys.argv) > 1 and sys.argv[1] == "rejudge":
        args = _parse_rejudge_args(sys.argv[2:])
        try:
            judges = parse_judge_models(args.judge_models)
        except ValueError as error:
            raise SystemExit(str(error)) from error
        metrics = asyncio.run(
            rejudge(
                args.run,
                judge_models=judges,
                labels=args.labels,
                quota_ceiling=args.quota_ceiling,
            )
        )
        print(
            json.dumps(
                {
                    "run_dir": str(args.run),
                    "records": metrics["records"],
                    "judge_models": metrics["judge_models"],
                    "judge_calls": metrics["totals"]["judge_calls"],
                },
                indent=2,
            )
        )
        return
    asyncio.run(_run(_parse_args()))
