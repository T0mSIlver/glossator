"""Where does a real question's similarity stop and a junk question's begin?

D-030 wants two numbers on the retriever: an absolute cosine floor and a relative
margin below the query's own best hit. Both are only defensible if the corridor
between real questions and junk ones was measured rather than guessed, so this
runs both populations through the live index, records the similarity at four
depths per query, and proposes the numbers only when the two distributions
actually separate. When they overlap it says so and proposes nothing: a floor
picked from overlapping distributions refuses real questions.

Junk questions are written here rather than generated, from domains the corpus
has no reason to contain -- cooking, veterinary medicine, astronomy, sport. They
are ordinary, well-formed questions, because a malformed one would be refused for
the wrong reason.

Usage:
    python -m glossator.eval.calibrate_floors --dataset eval/dev.jsonl --name dev
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import structlog
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

from glossator.eval.datasets import QuestionType, read_jsonl
from glossator.eval.report import line_chart
from glossator.eval.run_records import create_run_directory
from glossator.retrieval.config import DEFAULT_CORPUS_DIR, RetrievalConfig
from glossator.retrieval.engine import SearchEngine

logger = structlog.get_logger(__name__)

RUN_KIND = "floor-calibration"

POPULATIONS = ("real", "junk", "unanswerable")
"""``real`` is an answerable dataset question, ``junk`` a question about another
subject entirely. ``unanswerable`` is the dataset's own unanswerable type: written
in the corpus's vocabulary, not answered by it. It is reported separately and
never used to set the floor -- a floor low enough to accept a question the corpus
cannot answer accepts everything, which is exactly the failure D-030 is about."""

DEPTHS = (1, 5, 20, 50)
"""Where the similarity is read. 1 is the number a floor is compared against, 5
is roughly what an answer reads, 20 is the reranker's window, and 50 is deep
enough to show where the tail flattens."""

TOP_K = 50

JUNK_QUESTIONS: tuple[str, ...] = (
    # Cooking
    "how long should I proof a sourdough starter before the first bake",
    "what temperature should a rib of beef reach for medium rare",
    "why does my hollandaise split when I add the butter too quickly",
    "which flour makes the chewiest neapolitan pizza base",
    # Veterinary
    "what causes feline hyperthyroidism and how is it treated",
    "how often should a border collie puppy be wormed",
    "is xylitol dangerous for dogs in small quantities",
    "what are the early signs of laminitis in a horse",
    # Astronomy
    "why does the moon appear larger near the horizon",
    "how do astronomers measure the distance to a cepheid variable",
    "what is the difference between a meteor and a meteorite",
    "when is the next total solar eclipse visible from northern europe",
    # Sport
    "what is the offside rule in rugby union",
    "how many sets does a player need to win a grand slam final",
    "what gear ratio suits a steep alpine climb on a road bike",
)


class QuerySimilarities(BaseModel):
    """One query's similarity profile through the index."""

    model_config = ConfigDict(frozen=True)

    query: str
    population: str
    """``real`` or ``junk``."""

    question_id: str | None = None
    question_type: str | None = None
    lexical_footing: bool | None = None
    hits: int = 0
    at_depth: dict[str, float | None] = Field(default_factory=dict)
    """Similarity at each depth in ``DEPTHS``, keyed by the depth as a string."""

    error: str | None = None

    @property
    def best(self) -> float | None:
        return self.at_depth.get("1")


async def measure(
    engine: SearchEngine,
    query: str,
    population: str,
    *,
    question_id: str | None = None,
    question_type: str | None = None,
) -> QuerySimilarities:
    """One query's cosine similarities at the recorded depths.

    Searches the way serving searches -- hybrid, ranked by the schema's weights --
    and then reads the cosine of exactly those hits, so the numbers describe the
    result set a floor would be filtering rather than a different one.
    """
    try:
        hits = await engine.search(query, top_k=TOP_K)
        similarities = await engine.retriever.cosine_similarities(
            await engine.retriever.embed_query(query, context=engine.context),
            [hit.chunk_id for hit in hits],
            context=engine.context,
        )
    except Exception as error:  # noqa: BLE001 - one query's failure is recorded, not fatal
        logger.warning("Similarity read-out failed", query=query, error=str(error))
        return QuerySimilarities(
            query=query,
            population=population,
            question_id=question_id,
            question_type=question_type,
            error=str(error),
        )

    ranked = sorted(
        (similarities[hit.chunk_id] for hit in hits if hit.chunk_id in similarities), reverse=True
    )
    vocabulary = engine.vocabulary
    return QuerySimilarities(
        query=query,
        population=population,
        question_id=question_id,
        question_type=question_type,
        lexical_footing=vocabulary.has_footing(query) if vocabulary else None,
        hits=len(ranked),
        at_depth={
            str(depth): (ranked[depth - 1] if len(ranked) >= depth else None) for depth in DEPTHS
        },
    )


def propose(rows: Sequence[QuerySimilarities]) -> dict[str, Any]:
    """The floor and margin the two distributions support, or the reason they do not.

    The floor is the midpoint of the corridor between the worst real query's best
    hit and the best junk query's best hit -- if there is a corridor at all. The
    margin is the largest gap a real query shows between its own best hit and its
    fifth, so that applying it never cuts a real query below five results.

    Only the ``real`` population sets the floor. The dataset's own unanswerable
    questions are in the corpus's vocabulary but have no answer in it, so a floor
    fitted to accept them would accept everything; they are measured against the
    proposal instead (see ``_against_floor``).
    """
    real = [row for row in rows if row.population == "real" and row.best is not None]
    junk = [row for row in rows if row.population == "junk" and row.best is not None]
    if not real or not junk:
        return {"corridor": False, "reason": "one of the two populations produced no similarity"}

    worst_real = min(row.best or 0.0 for row in real)
    best_junk = max(row.best or 0.0 for row in junk)
    if worst_real <= best_junk:
        overlapping = sum(1 for row in real if (row.best or 0.0) <= best_junk)
        return {
            "corridor": False,
            "worst_real_best_hit": round(worst_real, 4),
            "best_junk_best_hit": round(best_junk, 4),
            "overlapping_real_questions": overlapping,
            "reason": (
                f"the worst real question's best hit ({worst_real:.4f}) does not clear the best "
                f"junk question's ({best_junk:.4f}), so no absolute floor separates them; "
                f"{overlapping} real question(s) sit at or below the junk ceiling"
            ),
        }

    spreads = [
        (row.at_depth["1"] or 0.0) - (row.at_depth["5"] or 0.0)
        for row in real
        if row.at_depth.get("5") is not None
    ]
    return {
        "corridor": True,
        "width": round(worst_real - best_junk, 4),
        "worst_real_best_hit": round(worst_real, 4),
        "best_junk_best_hit": round(best_junk, 4),
        "similarity_floor": round((worst_real + best_junk) / 2, 3),
        "similarity_margin": round(max(spreads), 3) if spreads else None,
        "margin_basis": (
            f"the largest best-to-fifth spread over {len(spreads)} real questions, so the "
            "margin never cuts a real question below five hits"
        ),
    }


def summarize(rows: Sequence[QuerySimilarities], config: Mapping[str, Any]) -> dict[str, Any]:
    """Every distribution, the proposal, and the counts behind them."""
    proposal = propose(rows)
    return {
        "kind": RUN_KIND,
        "status": "complete",
        "variant": config["variant"],
        "top_k": TOP_K,
        "depths": list(DEPTHS),
        "queries": len(rows),
        "errors": [row.query for row in rows if row.error],
        "distributions": {
            population: _distribution([row for row in rows if row.population == population])
            for population in POPULATIONS
        },
        "no_lexical_footing": {
            population: sum(
                1 for row in rows if row.population == population and row.lexical_footing is False
            )
            for population in POPULATIONS
        },
        "proposal": proposal,
        "unanswerable_against_the_floor": _against_floor(rows, proposal),
    }


def _against_floor(
    rows: Sequence[QuerySimilarities], proposal: Mapping[str, Any]
) -> dict[str, Any]:
    """How the dataset's unanswerable questions fare against the proposed floor.

    They are the population the floor is really for: questions written in the
    corpus's own vocabulary that the corpus does not answer. They cannot help set
    the floor -- a floor fitted to accept them accepts everything -- so they are
    measured against it instead, and a floor that lets most of them through has not
    bought what D-030 wanted.
    """
    unanswerable = [
        row for row in rows if row.population == "unanswerable" and row.best is not None
    ]
    floor = proposal.get("similarity_floor")
    if not unanswerable or floor is None:
        return {"questions": len(unanswerable), "clearing_the_floor": None}
    return {
        "questions": len(unanswerable),
        "clearing_the_floor": sum(1 for row in unanswerable if (row.best or 0.0) >= floor),
        "floor": floor,
    }


def _distribution(rows: Sequence[QuerySimilarities]) -> dict[str, Any]:
    scored = [row for row in rows if row.error is None]
    per_depth: dict[str, Any] = {}
    for depth in DEPTHS:
        values = sorted(
            value for row in scored if (value := row.at_depth.get(str(depth))) is not None
        )
        per_depth[str(depth)] = {
            "n": len(values),
            "min": round(values[0], 4) if values else None,
            "p10": round(_percentile(values, 0.10), 4) if values else None,
            "median": round(_percentile(values, 0.50), 4) if values else None,
            "p90": round(_percentile(values, 0.90), 4) if values else None,
            "max": round(values[-1], 4) if values else None,
        }
    return {"queries": len(rows), "scored": len(scored), "at_depth": per_depth}


def _percentile(values: Sequence[float], fraction: float) -> float:
    if not values:
        return 0.0
    index = min(len(values) - 1, max(0, round(fraction * (len(values) - 1))))
    return values[index]


def recompute(run_dir: Path) -> dict[str, Any]:
    """Rebuild ``metrics.json`` from the per-query rows the run recorded (D-023)."""
    config = json.loads((run_dir / "config.json").read_text())
    rows = [
        QuerySimilarities.model_validate_json(line)
        for line in (run_dir / "records.jsonl").read_text().splitlines()
        if line.strip()
    ]
    metrics = summarize(rows, config)
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    return metrics


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


async def run(
    dataset: Path,
    run_dir: Path,
    *,
    variant: str,
    corpus_dir: Path,
    limit: int | None = None,
) -> dict[str, Any]:
    questions = read_jsonl(dataset)[:limit]
    config = {
        "kind": RUN_KIND,
        "variant": variant,
        "top_k": TOP_K,
        "depths": list(DEPTHS),
        "dataset": str(dataset),
        "dataset_sha256": hashlib.sha256(dataset.read_bytes()).hexdigest(),
        "real_questions": len(questions),
        "junk_questions": len(JUNK_QUESTIONS),
        "corpus_dir": str(corpus_dir),
    }
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "figures").mkdir()
    (run_dir / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    # No model calls are made here, so calls.jsonl exists and stays empty rather
    # than being absent: a run directory has the same shape whatever produced it.
    (run_dir / "calls.jsonl").touch()
    records_path = run_dir / "records.jsonl"
    records_path.touch()

    engine = SearchEngine(
        RetrievalConfig(
            variant=variant, top_k=TOP_K, check_lexical_footing=True, corpus_dir=corpus_dir
        )
    )
    if engine.vocabulary is None:
        logger.warning(
            "No corpus vocabulary; lexical footing will be unknown", corpus_dir=str(corpus_dir)
        )

    rows: list[QuerySimilarities] = []
    for question in questions:
        rows.append(
            await measure(
                engine,
                question.question,
                "unanswerable" if question.type is QuestionType.UNANSWERABLE else "real",
                question_id=question.id,
                question_type=str(question.type),
            )
        )
    for junk in JUNK_QUESTIONS:
        rows.append(await measure(engine, junk, "junk"))

    with records_path.open("a") as handle:
        for row in rows:
            handle.write(row.model_dump_json() + "\n")

    metrics = summarize(rows, config)
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    write_report(run_dir, config, metrics)
    return metrics


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure the similarity corridor between real and junk questions."
    )
    parser.add_argument("--dataset", type=Path, required=True, help="Question set, one per line")
    parser.add_argument("--name", required=True, help="Name for the run directory")
    parser.add_argument("--variant", default="sec1024", help="Index variant to measure")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS_DIR)
    parser.add_argument("--limit", type=int, help="Use only the first N real questions")
    parser.add_argument("--runs-root", type=Path, default=Path("eval/runs"))
    return parser.parse_args()


async def main() -> None:
    load_dotenv(override=True)
    args = _parse_args()
    run_dir = create_run_directory(args.name, root=args.runs_root)
    metrics = await run(
        args.dataset, run_dir, variant=args.variant, corpus_dir=args.corpus, limit=args.limit
    )
    print(
        json.dumps(
            {
                "run_dir": str(run_dir),
                "queries": metrics["queries"],
                "proposal": metrics["proposal"],
            },
            indent=2,
        )
    )


__all__ = [
    "DEPTHS",
    "JUNK_QUESTIONS",
    "RUN_KIND",
    "TOP_K",
    "QuerySimilarities",
    "measure",
    "propose",
    "recompute",
    "render_readme",
    "run",
    "summarize",
    "write_report",
]

if __name__ == "__main__":
    asyncio.run(main())
