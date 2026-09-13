"""The search loop's caps as evaluation axes: one knob at a time (D-035c).

The loop stops after ``round_cap`` rounds, answers at most ``searches_per_round``
searches per round, and shows the model ``tool_result_chars``-character previews
of what its tools found; none of the three was ever varied. This grid varies
each in turn against the shipped point (round_cap 4, searches_per_round 4,
tool_result_chars 600), so every row isolates one knob rather than mixing three.
It runs on a local server: ``GLOSSATOR_CHAT_SERVER_URL`` points the answer layer
at it while embeddings stay on the Mistral API, and the numbers are relative
comparisons between configurations on that server -- never absolute quality
figures, which keep coming from the API.

Each configuration is a normal ``answer_eval`` run directory named
``<name>-<axis>-<value>`` (resumable like any answer run), and the grid writes a
summary directory ``<stamp>-<name>`` with the comparison table and one pair of
figures per axis.
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import structlog
from dotenv import load_dotenv

from glossator.answer.config import PRICES, AnswerConfig, ModelPrice, aliased_price
from glossator.clients import chat_reasoning_effort, chat_server_url
from glossator.eval.answer_eval.judge import JUDGE_MAX_TOKENS, JUDGE_TEMPERATURE
from glossator.eval.answer_eval.metrics import REFERENCE_PRICING_MODEL, UNPRICED_MODELS
from glossator.eval.answer_eval.models import (
    DEFAULT_GENERATION_MODEL,
    DEFAULT_JUDGE_MODEL,
    JudgeModel,
    parse_judge_models,
)
from glossator.eval.answer_eval.overrides import apply_answer_config
from glossator.eval.answer_eval.prompts import JUDGE_PROMPT_HASHES, JUDGE_VERSION
from glossator.eval.answer_eval.run import run as run_answer_eval
from glossator.eval.answer_eval.run_dir import RunDirectory, resolve_run_directory
from glossator.eval.charts import bar_chart
from glossator.eval.datasets import EvalQuestion, dataset_hash, read_jsonl, stratified_subset
from glossator.retrieval.config import RERANK_MODEL

logger = structlog.get_logger(__name__)

RUNS_ROOT = Path("eval/runs")

FULL_PREVIEWS = "full"
"""The preview axis's third value: no cut at all, spelled ``tool_result_chars=null``
in the run's configuration rather than a number that must track the longest
chunk (D-035c)."""

SHIPPED_POINT: dict[str, int | None] = {
    "round_cap": 4,
    "searches_per_round": 4,
    "tool_result_chars": 600,
}

AXIS_VALUES: tuple[tuple[str, tuple[tuple[str, int | None], ...]], ...] = (
    ("round_cap", (("4", 4), ("6", 6), ("8", 8))),
    ("searches_per_round", (("4", 4), ("6", 6))),
    ("tool_result_chars", (("600", 600), ("1500", 1500), (FULL_PREVIEWS, None))),
)


@dataclass(frozen=True)
class GridConfiguration:
    """One row of the grid: an axis value, or the shipped point itself."""

    axis: str | None
    """``None`` for the shipped point, which is the row every axis is compared to."""

    label: str
    overrides: dict[str, Any]

    @property
    def name(self) -> str:
        """The run-name suffix, in the dashed form run directories use."""
        return "shipped" if self.axis is None else f"{self.axis.replace('_', '-')}-{self.label}"


def configurations() -> list[GridConfiguration]:
    """Every listed axis value, with repeats of the shipped point collapsed.

    Each axis's shipped value appears in ``AXIS_VALUES`` so the axis stays
    readable; here those rows fold into the one shipped-point run, because a
    round_cap=4 row and the shipped point are the same experiment.
    """
    rows = [GridConfiguration(axis=None, label="shipped", overrides=dict(SHIPPED_POINT))]
    seen = {tuple(sorted(SHIPPED_POINT.items()))}
    for axis, values in AXIS_VALUES:
        for label, value in values:
            overrides = dict(SHIPPED_POINT)
            overrides[axis] = value
            key = tuple(sorted(overrides.items()))
            if key in seen:
                continue
            seen.add(key)
            rows.append(GridConfiguration(axis=axis, label=label, overrides=overrides))
    return rows


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


# --------------------------------------------------------------------------- #
# The summary directory
# --------------------------------------------------------------------------- #

TABLE_COLUMNS: tuple[tuple[str, str, str], ...] = (
    ("correctness", "correctness (judge)", "pct"),
    ("groundedness", "groundedness (judge)", "pct"),
    ("cited_url_match", "cited URL matches gold", "pct"),
    ("citation_verification_rate", "quotes verified", "pct"),
    ("rounds", "rounds used", "num"),
    ("round_cap_hit", "round cap hit", "pct"),
    ("tool_calls", "tool calls", "num"),
    ("tokens_in", "prompt tokens per answer", "num"),
    ("latency_p50_s", "median seconds per answer", "sec"),
)


def grid_config(
    args: argparse.Namespace,
    rows: list[dict[str, Any]],
    *,
    questions: Sequence[EvalQuestion],
    judges: Sequence[JudgeModel],
) -> dict[str, Any]:
    return {
        "kind": "loop_grid",
        "name": args.name,
        "dataset": str(args.dataset),
        "dataset_sha256": dataset_hash(args.dataset),
        "questions": [question.id for question in questions],
        "model": args.model,
        "generation_server": chat_server_url(),
        "reasoning_effort": chat_reasoning_effort(),
        "judge_model": judges[0].identifier if judges else None,
        "judge_models": [judge.identifier for judge in judges],
        "variant": args.variant,
        "response_format": args.response_format,
        "shipped_point": dict(SHIPPED_POINT),
        "axes": {axis: [label for label, _value in values] for axis, values in AXIS_VALUES},
        "runs": rows,
        "notes": list(args.note or []),
    }


def summarize(
    run_dir: Path,
    config: dict[str, Any],
    *,
    failed_rows: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Read every row's run back and write the summary's four artefacts."""
    rows = [configuration_row(entry) for entry in config["runs"]]
    metrics: dict[str, Any] = {
        "kind": "loop_grid",
        "run_dir": str(run_dir),
        "name": config["name"],
        "dataset": config["dataset"],
        "dataset_sha256": config["dataset_sha256"],
        "questions": len(config.get("questions") or []),
        "model": config["model"],
        "generation_server": config.get("generation_server"),
        "reasoning_effort": config.get("reasoning_effort"),
        "judge_model": config.get("judge_model"),
        "judge_models": config.get("judge_models") or [],
        "variant": config["variant"],
        "response_format": config.get("response_format"),
        "shipped_point": config.get("shipped_point"),
        "configurations": rows,
        "failed_rows": list(failed_rows or []),
        "notes": config.get("notes") or [],
    }
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "figures").mkdir(exist_ok=True)
    (run_dir / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    (run_dir / "README.md").write_text(render_readme(config, metrics))
    render_figures(metrics, run_dir / "figures")
    return metrics


def configuration_row(entry: dict[str, Any]) -> dict[str, Any]:
    """One row of the comparison, read out of the row's own metrics.json."""
    run_path = Path(str(entry["run_dir"]))
    row: dict[str, Any] = {
        "name": entry["name"],
        "axis": entry.get("axis"),
        "value": entry.get("value"),
        "overrides": entry.get("overrides") or {},
        "run_dir": str(run_path),
        "status": "missing",
        "questions": None,
        "records": None,
        "errors": None,
        # Every column exists even when the row has no metrics to fill it, so a
        # reader of metrics.json never has to guard for a missing key.
        **{key: None for key, _caption, _kind in TABLE_COLUMNS},
    }
    with contextlib.suppress(FileNotFoundError, ValueError, KeyError):
        metrics = json.loads((run_path / "metrics.json").read_text())
        cell = metrics["by_strategy"]["search_loop"]["all"]
        row.update(
            {
                "status": metrics.get("status"),
                "questions": metrics.get("questions"),
                "records": metrics.get("records"),
                "errors": cell.get("errors"),
                **{key: cell.get(key) for key, _caption, _kind in TABLE_COLUMNS},
            }
        )
    return row


def _cell_value(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    if value is None:
        return "--"
    for name, _caption, kind in TABLE_COLUMNS:
        if name == key:
            return {"pct": f"{value:.2f}", "num": f"{value:.1f}", "sec": f"{value:.1f}"}[kind]
    return str(value)


def render_readme(config: dict[str, Any], metrics: dict[str, Any]) -> str:
    """The grid's README (D-023): what was compared, on what, with what result."""
    server = metrics.get("generation_server")
    server_sentence = (
        f"Every configuration ran its chat calls on the local server `{server}` -- "
        "a quantized Ministral 3 served by llama.cpp -- with embeddings on the "
        "Mistral API."
        if server
        else "No generation server was configured for this grid, so its rows would "
        "run against the Mistral API, which the plan reserves for shipped figures."
    )
    header = "| configuration | " + " | ".join(caption for _k, caption, _f in TABLE_COLUMNS) + " |"
    divider = "|---" * (len(TABLE_COLUMNS) + 1) + "|"
    lines = [header, divider]
    for row in metrics["configurations"]:
        label = row["name"].removeprefix(f"{metrics['name']}-")
        status = "" if row.get("status") == "complete" else f" ({row.get('status') or '?'})"
        lines.append(
            f"| `{label}`{status} | "
            + " | ".join(_cell_value(row, key) for key, _caption, _kind in TABLE_COLUMNS)
            + " |"
        )
    notes = "\n".join(f"- {note}" for note in metrics.get("notes") or [])
    notes_section = f"\n\n## Notes on this run\n\n{notes}" if notes else ""
    judge_sentence = (
        "The judge was skipped for this grid (`--skip-judge`), so the judged "
        "columns (correctness, groundedness) are empty; every row holds its "
        "answers, traces, tokens and latencies, and a later `rejudge` fills the "
        "judged columns without re-running generation."
        if not metrics.get("judge_model")
        else f"Judge: `{metrics['judge_model']}`."
    )
    figures = "\n".join(
        f"- `figures/{figure_name(axis, what)}`"
        for axis, _values in AXIS_VALUES
        for what in ("correctness", "tokens")
    )
    return f"""# Search-loop cap grid: {metrics["name"]}

**What this measures.** The search loop stops after `round_cap` rounds, answers
at most `searches_per_round` searches per round, and shows the model
`tool_result_chars`-character previews of what its tools found (D-035c). None of
the three values had ever been varied; this grid moves one at a time away from
the shipped point (round_cap {metrics["shipped_point"]["round_cap"]}, searches_per_round
{metrics["shipped_point"]["searches_per_round"]}, tool_result_chars
{metrics["shipped_point"]["tool_result_chars"]}), so each row isolates one knob.

**Read the numbers as relative.** {server_sentence} They are comparisons between
configurations of the same server, not absolute quality figures; every shipped
figure keeps coming from the Mistral API (D-035c). A difference of a few points
on {metrics.get("questions", "--")} questions is a signal to follow up, not a
conclusion.

## Configuration

- Dataset: `{metrics["dataset"]}`, sha256 `{metrics["dataset_sha256"]}`
- Generation model: `{metrics["model"]}`; judge: `{metrics["judge_model"]}`; \
index variant: `{metrics["variant"]}`
- Structured output sent as `{metrics["response_format"]}`
- Each row is a normal answer-eval run of `search_loop` only, in the directory \
named in `config.json`.

## Results

{chr(10).join(lines)}

{judge_sentence}

## Figures

{figures}

Each figure shows one axis; the shipped point is the bar every other bar on that
axis is compared against.
{notes_section}

## Files

- `config.json` -- the grid definition: every row's axis, value, overrides and run directory.
- `metrics.json` -- the table above, as numbers.
- Each row's evidence (answers, citations, calls, per-question records) is in its
  own run directory, named in `config.json`.

## What it feeds

D-035c: whether the loop's caps should move, and in which direction, decided on
relative numbers from a local server before any API credits are spent.
"""


def figure_name(axis: str, what: str) -> str:
    return f"{what}-by-{axis}.svg"


def render_figures(metrics: dict[str, Any], figures_dir: Path) -> list[Path]:
    """One correctness figure and one token figure per axis, in the house style."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    by_name = {row["name"]: row for row in metrics["configurations"]}
    for axis, values in AXIS_VALUES:
        rows = _unique(
            [by_name.get(f"{metrics['name']}-shipped")]
            + [by_name.get(f"{metrics['name']}-{axis}-{label}") for label, _value in values]
        )
        for what, key, title in (
            ("correctness", "correctness", "Judged correctness"),
            ("tokens", "tokens_in", "Prompt tokens per answer"),
        ):
            # A row with no number is left out rather than drawn at zero: a
            # missing judged column and a genuine 0.0 must not look the same.
            measured = [row for row in rows if row.get(key) is not None]
            chart = bar_chart(
                f"{title} by {axis}",
                [(str(row.get("value") or "shipped"), (float(row[key]),)) for row in measured],
                (title,),
            )
            path = figures_dir / figure_name(axis, what)
            path.write_text(chart)
            written.append(path)
    return written


def _unique(rows: Sequence[dict[str, Any] | None]) -> list[dict[str, Any]]:
    """The rows in order, without the shipped point repeated under an axis label."""
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for row in rows:
        if row is None or row["name"] in seen:
            continue
        seen.add(row["name"])
        unique.append(row)
    return unique


def regenerate(run_dir: Path) -> dict[str, Any]:
    """Rebuild the summary from its rows' own metrics (D-023: figures regenerable)."""
    config = json.loads((run_dir / "config.json").read_text())
    previous: dict[str, Any] = {}
    with contextlib.suppress(FileNotFoundError, ValueError):
        previous = json.loads((run_dir / "metrics.json").read_text())
    return summarize(run_dir, config, failed_rows=previous.get("failed_rows"))


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Vary the search loop's caps one axis at a time (D-035c)"
    )
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument(
        "--name", default="loop-grid", help="Grid name; rows are <name>-<axis>-<value>"
    )
    parser.add_argument("--model", default=DEFAULT_GENERATION_MODEL)
    parser.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    parser.add_argument("--skip-judge", action="store_true")
    parser.add_argument("--variant", default="sec1024")
    parser.add_argument(
        "--response-format",
        choices=("json_schema", "json_object"),
        default=AnswerConfig().response_format,
        help=(
            "How structured requests are sent; json_object is the fallback for a "
            "server that does not honour a JSON schema"
        ),
    )
    parser.add_argument("--limit", type=int, help="Stratified subset of this many questions")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--quota-ceiling", type=int, default=80)
    parser.add_argument("--runs-root", type=Path, default=RUNS_ROOT)
    parser.add_argument(
        "--retry-errors",
        action="store_true",
        help="On resume, regenerate the rows whose record carries an error",
    )
    parser.add_argument(
        "--note",
        action="append",
        default=[],
        dest="note",
        help="A sentence of context rendered into the summary README; repeatable",
    )
    return parser.parse_args(argv)


def main() -> None:
    load_dotenv()
    metrics = asyncio.run(run_grid(_parse_args()))
    print(
        json.dumps(
            {
                "summary_dir": metrics["run_dir"],
                "configurations": len(metrics["configurations"]),
                "failed_rows": metrics["failed_rows"],
                "model": metrics["model"],
                "generation_server": metrics["generation_server"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
