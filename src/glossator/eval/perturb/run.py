"""The whole perturbation run, its dataset, and its figures."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any, cast

from glossator.eval.charts import bar_chart
from glossator.eval.datasets import EvalQuestion, read_jsonl, stratified_subset, write_jsonl
from glossator.eval.perturb.models import FIGURES, KINDS
from glossator.eval.perturb.prompts import PROMPT_VERSION
from glossator.eval.perturb.variants import assign_kinds, perturb_all
from glossator.eval.providers.client import OpenAICompatibleProvider
from glossator.eval.providers.models import ChatProvider, ProviderName, ThinkingMode
from glossator.eval.run_records import RunRecorder, create_run_directory


def render_figures(metrics: dict[str, Any], figures_dir: Path) -> None:
    """The two charts the README names, from the run's own metrics."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    candidates = metrics["candidates_by_type"]
    kept = metrics["kept_by_type"]
    (figures_dir / "kept-by-kind.svg").write_text(
        bar_chart(
            "Variants kept and dropped, per noise kind",
            [
                (kind, [float(kept.get(kind, 0)), float(count - kept.get(kind, 0))])
                for kind, count in sorted(candidates.items())
            ],
            ["kept", "dropped"],
        )
    )
    (figures_dir / "drop-reasons.svg").write_text(
        bar_chart(
            "Why variants were dropped",
            [
                (reason[:60], [float(count)])
                for reason, count in sorted(metrics["dropped_by_reason"].items())
            ],
            ["variants"],
        )
    )


async def run(
    args: argparse.Namespace,
    *,
    provider: ChatProvider | None = None,
    run_dir: Path | None = None,
) -> dict[str, Any]:
    """The whole run. ``provider`` and ``run_dir`` are injectable so a test can
    exercise the batching, the records and the README without a network."""
    questions = read_jsonl(Path(args.dataset))
    subset = stratified_subset(questions, args.n, args.seed)
    pairs = assign_kinds(subset)
    run_dir = run_dir or create_run_directory(args.name)
    config = {
        "kind": "perturb",
        "dataset": args.dataset,
        "n": args.n,
        "seed": args.seed,
        "provider": args.provider,
        "model": args.model,
        "prompt_version": PROMPT_VERSION,
        "noise_kinds": list(KINDS),
        "source_questions": [question.id for question in subset],
        "figures": list(FIGURES),
    }
    provider_name: ProviderName = args.provider
    # Reasoning has to be set and checked per call on z.ai, and recorded (D-020).
    thinking: ThinkingMode | None = "disabled" if provider_name == "zai" else None
    config["thinking"] = thinking
    recorder = RunRecorder.start(run_dir, config)

    async def perturb_with(client: ChatProvider) -> list[EvalQuestion]:
        return await perturb_all(
            client,
            pairs,
            recorder=recorder,
            model=args.model,
            seed=args.seed,
            thinking=thinking,
            concurrency=args.concurrency,
        )

    if provider is not None:
        kept = await perturb_with(provider)
    else:
        async with OpenAICompatibleProvider(
            provider_name,
            asyncio.Semaphore(args.concurrency),
            caller_tag="eval.perturb",
            recorder=recorder,
            seed=args.seed,
        ) as client:
            kept = await perturb_with(client)

    out = Path(args.out)
    write_jsonl(out, kept)
    recorder.finalize(dataset_path=out, error=None)
    render_figures(
        cast(dict[str, Any], json.loads(recorder.metrics_path.read_text())), run_dir / "figures"
    )
    return {
        "written": len(kept),
        "dropped": len(pairs) - len(kept),
        "out": str(out),
        "run_dir": str(run_dir),
        **recorder.usage_line(),
    }
