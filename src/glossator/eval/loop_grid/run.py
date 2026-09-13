"""Every grid row as a normal answer-evaluation run over `search_loop` only."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import structlog

from glossator.answer.config import PRICES, AnswerConfig, ModelPrice, aliased_price
from glossator.clients import chat_reasoning_effort, chat_server_url
from glossator.eval.answer_eval.judge import JUDGE_MAX_TOKENS, JUDGE_TEMPERATURE
from glossator.eval.answer_eval.metrics import REFERENCE_PRICING_MODEL, UNPRICED_MODELS
from glossator.eval.answer_eval.models import JudgeModel, parse_judge_models
from glossator.eval.answer_eval.overrides import apply_answer_config
from glossator.eval.answer_eval.prompts import JUDGE_PROMPT_HASHES, JUDGE_VERSION
from glossator.eval.answer_eval.run import run as run_answer_eval
from glossator.eval.answer_eval.run_dir import RunDirectory, resolve_run_directory
from glossator.eval.datasets import EvalQuestion, dataset_hash, read_jsonl, stratified_subset
from glossator.eval.loop_grid.models import SHIPPED_POINT, GridConfiguration, configurations
from glossator.eval.loop_grid.summary import grid_config, summarize
from glossator.retrieval.config import RERANK_MODEL

logger = structlog.get_logger(__name__)


def resolve_judge_models(value: str) -> list[JudgeModel]:
    """A bare model name means the z.ai provider; ``provider:model`` passes through."""
    return parse_judge_models(value if ":" in value else f"zai:{value}")


def eval_prices(model: str) -> dict[str, ModelPrice]:
    """The eval price table, with the local-server alias spelled out.

    The request names ``llamacpp/ministral3-14b`` while the response reports
    ``ministral3-14b``; both price as Ministral 3 14B at the published API rate
    applied to a local run (D-035c). A model with no published price and no
    alias is left out of the table on purpose: it then costs 0 with the one
    warning per model that says so, rather than carrying a fabricated zero rate
    that reads like a measured price.
    """
    prices = dict(PRICES)
    alias = aliased_price(model)
    if model not in prices and alias is not None:
        prices[model] = alias
    return prices


async def run_grid(args: argparse.Namespace) -> dict[str, Any]:
    questions = read_jsonl(args.dataset)
    if args.limit is not None:
        questions = stratified_subset(questions, args.limit, args.seed)
    judges = [] if args.skip_judge else resolve_judge_models(args.judge_model)

    failures: list[str] = []
    rows: list[dict[str, Any]] = []
    for configuration in configurations():
        run_name = f"{args.name}-{configuration.name}"
        run_path = resolve_run_directory(run_name, root=args.runs_root)
        try:
            await run_one(
                configuration,
                questions=questions,
                run_name=run_name,
                run_path=run_path,
                args=args,
                judges=judges,
            )
        except Exception as error:  # noqa: BLE001 - one failed row must not lose the others
            logger.error("Grid row failed", run=run_name, error=str(error))
            failures.append(run_name)
        rows.append(
            {
                "name": run_name,
                "axis": configuration.axis,
                "value": configuration.label,
                "overrides": dict(configuration.overrides),
                "run_dir": str(run_path),
            }
        )

    summary_path = resolve_run_directory(args.name, root=args.runs_root)
    return summarize(
        summary_path,
        grid_config(args, rows, questions=questions, judges=judges),
        failed_rows=failures,
    )


async def run_one(
    configuration: GridConfiguration,
    *,
    questions: Sequence[EvalQuestion],
    run_name: str,
    run_path: Path,
    args: argparse.Namespace,
    judges: Sequence[JudgeModel],
) -> dict[str, Any]:
    """One grid row: a normal answer_eval run over `search_loop` only."""
    settings = apply_answer_config(
        AnswerConfig(
            model=args.model,
            response_format=args.response_format,
            prices=eval_prices(args.model),
        ),
        configuration.overrides,
    )
    server = chat_server_url()
    pricing_note = (
        "Costs use the published Ministral 3 API rate applied to a local run."
        if server and aliased_price(args.model) is not None
        else None
    )
    run_config: dict[str, Any] = {
        "kind": "answer_eval",
        "name": run_name,
        "grid": {
            "grid_name": args.name,
            "axis": configuration.axis,
            "value": configuration.label,
            "overrides": dict(configuration.overrides),
        },
        "run_dir": str(run_path),
        "dataset": str(args.dataset),
        "dataset_sha256": dataset_hash(args.dataset),
        "questions": [question.id for question in questions],
        "limit": args.limit,
        "seed": args.seed,
        "variant": args.variant,
        "strategies": ["search_loop"],
        "model": args.model,
        "generation_server": server,
        "reasoning_effort": chat_reasoning_effort(),
        "judge_model": judges[0].identifier if judges else None,
        "judge_models": [judge.identifier for judge in judges],
        "judge_prompt_version": JUDGE_VERSION,
        "judge_prompt_hashes": JUDGE_PROMPT_HASHES,
        "judge_temperature": JUDGE_TEMPERATURE,
        "judge_max_tokens": JUDGE_MAX_TOKENS,
        "judge_thinking": {
            judge.identifier: "disabled" if judge.provider == "zai" else None for judge in judges
        },
        "judge_provider": None,
        "labels": None,
        "top_k": settings.top_k,
        "rerank": True,
        "translate_for_retrieval": settings.translate_for_retrieval,
        "rewrite_for_retrieval": settings.rewrite_for_retrieval,
        "rerank_model": RERANK_MODEL,
        "context_token_budget": settings.context_token_budget,
        "answer_config": settings.model_dump(mode="json"),
        "answer_config_overrides": dict(configuration.overrides),
        "unpriced_models": sorted(UNPRICED_MODELS),
        "reference_pricing_model": REFERENCE_PRICING_MODEL,
        "notes": [
            f"grid row {configuration.name}: one axis moved off the shipped point "
            f"(round_cap {SHIPPED_POINT['round_cap']}, searches_per_round "
            f"{SHIPPED_POINT['searches_per_round']}, tool_result_chars "
            f"{SHIPPED_POINT['tool_result_chars']})"
        ]
        + ([pricing_note] if pricing_note else [])
        + list(args.note or []),
    }
    run_dir = RunDirectory.open(run_path, run_config)
    return await run_answer_eval(
        questions,
        strategies=["search_loop"],
        variant=args.variant,
        model=args.model,
        judge_models=judges,
        run_dir=run_dir,
        settings=settings,
        quota_ceiling=args.quota_ceiling,
        rerank=True,
        retry_errors=args.retry_errors,
    )
