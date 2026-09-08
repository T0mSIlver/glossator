"""The README and the figures a retrieval run is read through.

Nothing here is written by hand and preserved across a regeneration: every
sentence and every table cell is computed from ``metrics.json``, which is itself
computed from ``records.jsonl``. That is what makes `make eval-report` safe to run
on an old directory, and what stops a README from outliving the numbers under it.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from glossator.eval.report import bar_chart, line_chart
from glossator.eval.retrieval_metrics import METRIC_NAMES, Matching

RECALL_KS = ("recall@1", "recall@3", "recall@5", "recall@10")


def write_report(run_dir: Path, config: Mapping[str, Any], metrics: Mapping[str, Any]) -> None:
    """Write ``README.md`` and ``figures/`` for a finished grid run."""
    (run_dir / "README.md").write_text(render_readme(config, metrics))
    render_figures(metrics, run_dir / "figures")


def rebuild_by_kind(kind: str, run_dir: Path) -> dict[str, Any]:
    """Regenerate a run of a known kind from the rows it recorded."""
    from glossator.eval.calibrate_floors import RUN_KIND as FLOOR_KIND
    from glossator.eval.calibrate_floors import recompute as recompute_floors
    from glossator.eval.calibrate_floors import write_report as write_floor_report
    from glossator.eval.retrieval_grid import RUN_KIND as GRID_KIND
    from glossator.eval.retrieval_grid import recompute as recompute_grid

    config = json.loads((run_dir / "config.json").read_text())
    if kind == GRID_KIND:
        metrics = asyncio.run(recompute_grid(run_dir))
        write_report(run_dir, config, metrics)
    elif kind == FLOOR_KIND:
        metrics = recompute_floors(run_dir)
        write_floor_report(run_dir, config, metrics)
    else:
        raise ValueError(f"unknown run kind {kind!r} in {run_dir / 'config.json'}")
    return dict(metrics)


def render_readme(config: Mapping[str, Any], metrics: Mapping[str, Any]) -> str:
    order = list(metrics["configuration_order"])
    configs = metrics["configurations"]
    types = ["overall", *metrics["question_types"]]
    scored_types = [name for name in types if name != "unanswerable"]

    sections = [
        "# Retrieval grid",
        _what(config, metrics),
        _configurations(config, order, configs),
        _tables(order, configs, types=scored_types),
        _operations(order, configs),
        _unanswerable(metrics),
        _figures(),
        _conclusion(metrics, configs),
    ]
    return "\n".join(part.rstrip() + "\n" for part in sections if part)


def _what(config: Mapping[str, Any], metrics: Mapping[str, Any]) -> str:
    rerank = config.get("rerank", {})
    return (
        "## What this measures\n\n"
        f"Every one of {metrics['questions']} questions was run through "
        f"{_plural(len(metrics['configuration_order']), 'retrieval configuration')}, and "
        "the ranked hits of each run were kept. The question each row answers is: which "
        "index variant, which ranking weights, and reranking or not, put the "
        "documentation section that answers a question inside the top few results.\n\n"
        "A hit counts as correct in two ways, reported separately:\n\n"
        "- **page**: the hit's URL is one of the question's gold URLs. This is what a "
        "reader needs to reach the answer at all.\n"
        "- **section**: the hit's URL *and* anchor match a gold URL and anchor. This is "
        "what a citation needs in order to deep-link.\n\n"
        "Most markdown headings in this corpus carry no anchor (D-003a), so a question "
        "whose gold has no anchor cannot be scored at the section level. "
        f"{metrics['section_scoreable']} of {metrics['page_scoreable']} answerable questions "
        "carry an anchor on every gold source and are the only ones in the section "
        "tables; the rest are page level only, and are not counted as section misses.\n\n"
        "Unanswerable questions have no gold, so they are excluded from every recall "
        "number and reported on their own below.\n\n"
        "Several chunks of one page are one result: the ranked list is collapsed to "
        "distinct pages (or sections) at their best rank before it is scored, so "
        'recall@k reads as "the answer was among the first k pages" rather than '
        '"among the first k chunks".\n\n'
        "## Datasets\n\n"
        f"- Questions: `{config['dataset']}`, sha256 `{config['dataset_sha256'][:16]}`\n"
        f"- {metrics['questions']} questions: "
        + ", ".join(
            f"{count} {name}" for name, count in sorted(config["questions_by_type"].items())
        )
        + "\n"
        f"- Reranker prompt: `{rerank.get('prompt_version')}`, "
        f"sha256 `{rerank.get('prompt_sha256')}`\n"
        f"- Reranker model: `{rerank.get('model')}`\n"
    )


def _configurations(
    config: Mapping[str, Any], order: Sequence[str], configs: Mapping[str, Any]
) -> str:
    lines = [
        "## Configurations\n",
        "| configuration | variant | weight set | rerank | ranking weights |",
        "|---|---|---|---|---|",
    ]
    for name in order:
        row = configs[name]
        weights = row["config"]["ranking_weights"]
        rendered = (
            ", ".join(f"`{key}` {value:g}" for key, value in sorted(weights.items()))
            or "schema defaults"
        )
        lines.append(
            f"| `{name}` | {row['variant']} | {row['weights']} | "
            f"{'yes' if row['rerank'] else 'no'} | {rendered} |"
        )
    lines.append("")
    lines.append(f"Every row retrieves {config['top_k']} hits.")
    return "\n".join(lines)


def _tables(order: Sequence[str], configs: Mapping[str, Any], *, types: Sequence[str]) -> str:
    parts = ["## Results\n"]
    for matching in Matching:
        parts.append(f"### {matching.value.capitalize()}-level matching\n")
        for metric in METRIC_NAMES:
            parts.append(f"**{metric}**\n")
            parts.append("| configuration | " + " | ".join(types) + " |")
            parts.append("|---" * (len(types) + 1) + "|")
            for name in order:
                cells = []
                for question_type in types:
                    row = configs[name]["metrics"][str(matching)]["common"].get(question_type) or {}
                    value = row.get(metric)
                    cells.append("--" if value is None else f"{value:.3f}")
                parts.append(f"| `{name}` | " + " | ".join(cells) + " |")
            parts.append("")
        counts = configs[order[0]]["metrics"][str(matching)]["common"]
        parts.append(
            "Question counts per column: "
            + ", ".join(f"{name} {(counts.get(name) or {}).get('questions', 0)}" for name in types)
            + ".\n"
        )
    return "\n".join(parts)


def _operations(order: Sequence[str], configs: Mapping[str, Any]) -> str:
    lines = [
        "## Latency, cost and failures\n",
        "| configuration | median ms | p90 ms | rerank calls applied | rerank fallbacks | "
        "rerank USD | errors |",
        "|---|---|---|---|---|---|---|",
    ]
    for name in order:
        row = configs[name]
        median = row.get("median_latency_ms")
        p90 = row.get("p90_latency_ms")
        lines.append(
            f"| `{name}` | {'--' if median is None else f'{median:.0f}'} | "
            f"{'--' if p90 is None else f'{p90:.0f}'} | {row['rerank_applied']} | "
            f"{row['rerank_fallbacks']} | {row['rerank_cost_usd']:.5f} | {row['errors']} |"
        )
    lines.append("")
    lines.append(
        "Latency is wall-clock for one question through one configuration: the Vespa "
        "round trip and, where it ran, the reranker's model call. The query's embedding "
        "is not in it -- a question is embedded once per embedding model and the vector "
        "is reused across every configuration that shares it, so charging that call to "
        "one configuration and not the others would be arbitrary."
    )
    return "\n".join(lines)


def _unanswerable(metrics: Mapping[str, Any]) -> str:
    unanswerable = metrics["unanswerable"]
    if not unanswerable["questions"]:
        return "## Unanswerable questions\n\nThe dataset holds none.\n"
    lines = [
        "## Unanswerable questions\n",
        f"The dataset holds {_plural(unanswerable['questions'], 'question')} with no gold "
        "source, so they carry no recall. What they measure is whether the engine returns "
        "something confident anyway. Across every configuration, "
        f"{unanswerable['with_a_top_hit']} of {len(unanswerable['rows'])} runs returned a "
        f"top hit, and {unanswerable['no_lexical_footing']} were reported as having no "
        "lexical footing.\n",
        "| question | configuration | top hit | footing |",
        "|---|---|---|---|",
    ]
    for row in unanswerable["rows"]:
        top = row["top_hit"]
        target = "none" if top is None else _citation(top)
        footing = {True: "yes", False: "no", None: "not checked"}[row["lexical_footing"]]
        lines.append(f"| {row['question']} | `{row['configuration']}` | {target} | {footing} |")
    return "\n".join(lines)


def _figures() -> str:
    return (
        "## Figures\n\n"
        "Regenerated from `metrics.json` by `make eval-report run=<dir>`.\n\n"
        "- `figures/recall-at-k-page.svg`, `figures/recall-at-k-section.svg`: recall "
        "against k, one line per configuration\n"
        "- `figures/best-two-by-type-page.svg`, `figures/best-two-by-type-section.svg`: "
        "recall@5 per question type, for the two leading configurations\n"
    )


def _plural(count: int, noun: str) -> str:
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def _conclusion(metrics: Mapping[str, Any], configs: Mapping[str, Any]) -> str:
    parts = ["## Conclusion"]
    for matching in Matching:
        best = metrics["best"].get(str(matching))
        if not best:
            parts.append(f"No configuration could be scored at the {matching} level.")
            continue
        winner = best["configuration"]
        sentence = (
            f"At the {matching} level, `{winner}` leads on recall@5 with {best['recall@5']:.3f}"
        )
        runner_up = best["runner_up"]
        if runner_up:
            second = configs[runner_up]["metrics"][str(matching)]["common"]["overall"]["recall@5"]
            sentence += f", {best['margin']:+.3f} over `{runner_up}` ({second:.3f})"
        tied = sum(1 for row in best["ranking"] if row["recall@5"] == best["recall@5"])
        if tied > 1:
            sentence += (
                f"; {tied} configurations are tied at that number, so the lead is the "
                "alphabetical tie-break and not a difference the dataset can see"
            )
        parts.append(sentence + ".")
    calls = metrics["rerank_calls"]
    fallbacks = metrics.get("rerank_fallbacks", 0)
    if calls:
        sentence = (
            f"The reranker's ranking was applied {calls} times for "
            f"${metrics['rerank_cost_usd']:.4f}, about "
            f"${metrics['rerank_cost_usd'] / calls:.6f} a call"
        )
        if fallbacks:
            sentence += (
                f"; {_plural(fallbacks, 'further call')} returned a ranking the reordering "
                "could not use and fell back to retrieval order, which the per-question "
                "records name"
            )
        parts.append(sentence + ".")
    else:
        parts.append("No reranker call was applied in this run.")
    parts.append(
        "This feeds D-012a: the shipped ranking weights are a starting point and the "
        "winning row above is what replaces them, and D-015: whether one listwise call "
        "buys enough ordering to be worth its latency in the serving path."
    )
    if metrics["errors"]:
        parts.append(f"{len(metrics['errors'])} question runs failed; see `metrics.json`.")
    return "\n\n".join(parts)


def render_figures(metrics: Mapping[str, Any], figures_dir: Path) -> list[Path]:
    """Recall curves per configuration, and per-type bars for the leading two rows."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    order = list(metrics["configuration_order"])
    configs = metrics["configurations"]
    types = [name for name in metrics["question_types"] if name != "unanswerable"]
    written: list[Path] = []

    for matching in Matching:
        curves = [
            (
                name,
                [
                    float(
                        (
                            configs[name]["metrics"][str(matching)]["common"].get("overall") or {}
                        ).get(k)
                        or 0.0
                    )
                    for k in RECALL_KS
                ],
            )
            for name in order
        ]
        path = figures_dir / f"recall-at-k-{matching}.svg"
        path.write_text(
            line_chart(
                f"Recall at k, {matching}-level matching",
                ["1", "3", "5", "10"],
                curves,
            )
        )
        written.append(path)

        leaders = [
            row["configuration"]
            for row in (metrics["best"].get(str(matching), {}).get("ranking") or [])[:2]
        ]
        rows = [
            (
                question_type,
                tuple(
                    float(
                        (
                            configs[name]["metrics"][str(matching)]["common"].get(question_type)
                            or {}
                        ).get("recall@5")
                        or 0.0
                    )
                    for name in leaders
                ),
            )
            for question_type in types
        ]
        path = figures_dir / f"best-two-by-type-{matching}.svg"
        path.write_text(
            bar_chart(f"recall@5 by question type, {matching}-level matching", rows, leaders)
        )
        written.append(path)
    return written


def _citation(hit: Mapping[str, Any]) -> str:
    url = hit["url"]
    return f"{url}#{hit['anchor']}" if hit.get("anchor") else str(url)


__all__ = ["rebuild_by_kind", "render_figures", "render_readme", "write_report"]
