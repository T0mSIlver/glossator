"""The calibration README and its figure."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from glossator.eval.calibrate_floors.models import DEPTHS, POPULATIONS, TOP_K
from glossator.eval.charts import line_chart


def write_report(run_dir: Path, config: Mapping[str, Any], metrics: Mapping[str, Any]) -> None:
    (run_dir / "README.md").write_text(render_readme(config, metrics))
    render_figures(metrics, run_dir / "figures")


def render_readme(config: Mapping[str, Any], metrics: Mapping[str, Any]) -> str:
    proposal = metrics["proposal"]
    parts = [
        "# Score floor calibration\n",
        "## What this measures\n",
        f"Every query -- {config['real_questions']} questions from `{config['dataset']}` "
        f"and {config['junk_questions']} hand-written junk questions from cooking, "
        "veterinary medicine, astronomy and sport -- was searched against "
        f"`{config['variant']}` at top-{TOP_K}, and the cosine similarity of each returned "
        "hit was read back. The question is whether an absolute similarity floor exists "
        "that a real question always clears and a junk question never does (D-030). "
        "Without one, a k-nearest-neighbour index has no way to return nothing, and an "
        "unanswerable question gets a confident wrong answer.\n",
        "Three populations, not two. **real** is an answerable dataset question. **junk** "
        "is a question about another subject entirely. **unanswerable** is the dataset's "
        "own unanswerable type: written in this corpus's vocabulary, and not answered by "
        "it. Only `real` sets the floor -- a floor fitted to accept a question the corpus "
        "cannot answer would accept everything -- and `unanswerable` is measured against "
        "the proposal instead.\n",
        "The numbers describe the documents that variant's schema actually held when the "
        f"run happened. The lexical-footing column below was computed against "
        f"`{config['corpus_dir']}`, which is the corpus the vocabulary was read from and "
        "need not be the whole of what is indexed.\n",
        "## Distributions\n",
        _distribution_table(metrics),
        "## Lexical footing\n",
        f"{metrics['no_lexical_footing']['junk']} of {config['junk_questions']} junk queries "
        f"and {metrics['no_lexical_footing']['real']} of "
        f"{metrics['distributions']['real']['queries']} real queries have no content word "
        "anywhere in the corpus. That gate is independent of the similarity floor and is "
        "what makes a genuinely empty result reachable.\n",
        "## Proposal\n",
        _proposal(proposal),
        _unanswerable(metrics),
        "## Figures\n",
        "- `figures/similarity-by-depth.svg`: median similarity at each depth, one line "
        "per population\n",
        "## Decision\n",
        "These numbers are what D-030's `similarity_floor` and `similarity_margin` are set "
        "from. They are not set from a fixture corpus: eight pages produce a similarity "
        "distribution that says nothing about four hundred.\n",
    ]
    if metrics["errors"]:
        parts.append(
            f"{len(metrics['errors'])} queries failed and were recorded without numbers.\n"
        )
    return "\n".join(part.rstrip() + "\n" for part in parts)


def _distribution_table(metrics: Mapping[str, Any]) -> str:
    lines = [
        "| population | depth | n | min | p10 | median | p90 | max |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for population in POPULATIONS:
        for depth in DEPTHS:
            row = metrics["distributions"][population]["at_depth"][str(depth)]
            cells = " | ".join(
                "--" if row[key] is None else f"{row[key]:.4f}"
                for key in ("min", "p10", "median", "p90", "max")
            )
            lines.append(f"| {population} | {depth} | {row['n']} | {cells} |")
    return "\n".join(lines)


def _unanswerable(metrics: Mapping[str, Any]) -> str:
    """What the proposed floor would do to the questions it exists for."""
    against = metrics.get("unanswerable_against_the_floor") or {}
    questions = against.get("questions", 0)
    if not questions:
        return (
            "## Unanswerable questions\n\n"
            "The dataset holds none, so nothing here says what the floor would do to the "
            "case it exists for."
        )
    clearing = against.get("clearing_the_floor")
    if clearing is None:
        return (
            "## Unanswerable questions\n\n"
            f"{questions} of the dataset's questions are unanswerable. No floor was "
            "proposed, so there is nothing to measure them against."
        )
    return (
        "## Unanswerable questions\n\n"
        f"{clearing} of {questions} unanswerable questions still clear the proposed floor "
        f"of {against['floor']}. They are the case the floor exists for, so this is the "
        "number to watch: a floor most of them clear separates junk from documentation "
        "and not answerable from unanswerable, and the lexical-footing gate cannot help "
        "here either, because these questions are written in the corpus's own words."
    )


def _proposal(proposal: Mapping[str, Any]) -> str:
    if not proposal["corridor"]:
        return (
            "**No corridor.** " + str(proposal["reason"]) + "\n\n"
            "No floor is proposed. Setting one from these numbers would refuse real "
            "questions to reject junk ones, which is the wrong trade for a documentation "
            "engine: the lexical-footing gate handles the junk that has no words in "
            "common with the corpus, and the rest is the reranker's problem."
        )
    return (
        f"**A corridor of {proposal['width']:.4f} exists** between the worst real question's "
        f"best hit ({proposal['worst_real_best_hit']:.4f}) and the best junk question's "
        f"({proposal['best_junk_best_hit']:.4f}).\n\n"
        f"- `similarity_floor`: **{proposal['similarity_floor']}**, the midpoint of the corridor\n"
        f"- `similarity_margin`: **{proposal['similarity_margin']}**, {proposal['margin_basis']}\n"
    )


def render_figures(metrics: Mapping[str, Any], figures_dir: Path) -> list[Path]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    series = [
        (
            population,
            [
                float(metrics["distributions"][population]["at_depth"][str(depth)]["median"] or 0.0)
                for depth in DEPTHS
            ],
        )
        for population in ("real", "junk")
    ]
    path = figures_dir / "similarity-by-depth.svg"
    path.write_text(
        line_chart(
            "Median cosine similarity by result depth",
            [str(depth) for depth in DEPTHS],
            series,
        )
    )
    return [path]
