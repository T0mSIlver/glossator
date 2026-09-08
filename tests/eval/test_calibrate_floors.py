"""The corridor proposal, on distributions built by hand.

The point of the tool is to refuse to propose a number when the two populations
overlap, so the overlapping case is the one worth the most care.
"""

import json
from pathlib import Path
from typing import Any

from glossator.eval.calibrate_floors import (
    DEPTHS,
    JUNK_QUESTIONS,
    RUN_KIND,
    QuerySimilarities,
    propose,
    recompute,
    render_readme,
    summarize,
    write_report,
)


def row(
    population: str, best: float, fifth: float | None = None, **extra: Any
) -> QuerySimilarities:
    at_depth: dict[str, float | None] = {str(depth): None for depth in DEPTHS}
    at_depth["1"] = best
    at_depth["5"] = best - 0.05 if fifth is None else fifth
    at_depth["20"] = best - 0.10
    at_depth["50"] = best - 0.15
    return QuerySimilarities(
        query=f"{population} {best}", population=population, hits=50, at_depth=at_depth, **extra
    )


SEPARATED = [row("real", best) for best in (0.80, 0.84, 0.86)] + [
    row("junk", best) for best in (0.55, 0.60, 0.67)
]
OVERLAPPING = [row("real", best) for best in (0.62, 0.84, 0.86)] + [
    row("junk", best) for best in (0.55, 0.60, 0.67)
]


def test_junk_questions_come_from_four_unrelated_domains() -> None:
    assert len(JUNK_QUESTIONS) == 15
    assert len(set(JUNK_QUESTIONS)) == 15


def test_separated_populations_produce_a_floor_and_a_margin() -> None:
    proposal = propose(SEPARATED)
    assert proposal["corridor"] is True
    assert proposal["worst_real_best_hit"] == 0.8
    assert proposal["best_junk_best_hit"] == 0.67
    assert proposal["similarity_floor"] == 0.735
    assert proposal["width"] == 0.13
    # The margin keeps the worst real query's own top five.
    assert proposal["similarity_margin"] == 0.05


def test_overlapping_populations_propose_nothing_and_say_why() -> None:
    proposal = propose(OVERLAPPING)
    assert proposal["corridor"] is False
    assert proposal["overlapping_real_questions"] == 1
    assert "does not clear" in proposal["reason"]
    assert "similarity_floor" not in proposal


def test_an_unanswerable_question_never_lowers_the_floor() -> None:
    """It is in the corpus's vocabulary and has no answer in it, so a floor fitted
    to accept it would accept everything."""
    rows = [*SEPARATED, row("unanswerable", 0.61)]
    proposal = propose(rows)
    assert proposal["corridor"] is True
    assert proposal["worst_real_best_hit"] == 0.8
    assert proposal["similarity_floor"] == 0.735


def test_the_unanswerable_questions_are_measured_against_the_proposed_floor() -> None:
    rows = [*SEPARATED, row("unanswerable", 0.90), row("unanswerable", 0.61)]
    metrics = summarize(rows, _config())
    against = metrics["unanswerable_against_the_floor"]
    assert against == {"questions": 2, "clearing_the_floor": 1, "floor": 0.735}
    assert metrics["distributions"]["unanswerable"]["queries"] == 2
    readme = render_readme(_config(), metrics)
    assert "1 of 2 unanswerable questions still clear the proposed floor of 0.735" in readme


def test_nothing_is_measured_against_a_floor_that_was_not_proposed() -> None:
    metrics = summarize([*OVERLAPPING, row("unanswerable", 0.61)], _config())
    assert metrics["unanswerable_against_the_floor"]["clearing_the_floor"] is None
    assert "nothing to measure them against" in render_readme(_config(), metrics)


def test_a_population_with_no_similarity_at_all_proposes_nothing() -> None:
    assert propose([r for r in SEPARATED if r.population == "real"])["corridor"] is False
    assert propose([])["corridor"] is False


def test_a_query_that_failed_is_recorded_without_numbers() -> None:
    failed = QuerySimilarities(query="broken", population="real", error="Vespa said no")
    metrics = summarize([*SEPARATED, failed], _config())
    assert metrics["errors"] == ["broken"]
    assert metrics["distributions"]["real"]["queries"] == 4
    assert metrics["distributions"]["real"]["scored"] == 3


def test_the_summary_reports_both_distributions_at_every_depth() -> None:
    metrics = summarize(SEPARATED, _config())
    real = metrics["distributions"]["real"]["at_depth"]
    assert sorted(real) == sorted(str(depth) for depth in DEPTHS)
    assert real["1"]["min"] == 0.8
    assert real["1"]["max"] == 0.86
    assert metrics["distributions"]["junk"]["at_depth"]["1"]["median"] == 0.6
    assert metrics["kind"] == RUN_KIND


def test_the_footing_gate_is_counted_per_population() -> None:
    rows = [
        row("junk", 0.55, lexical_footing=False),
        row("junk", 0.60, lexical_footing=True),
        row("real", 0.80, lexical_footing=True),
    ]
    metrics = summarize(rows, _config())
    assert metrics["no_lexical_footing"] == {"real": 0, "junk": 1, "unanswerable": 0}


def test_the_readme_prints_the_proposal_and_regenerates_from_the_rows(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    (run_dir / "figures").mkdir(parents=True)
    config = _config()
    (run_dir / "config.json").write_text(json.dumps(config))
    (run_dir / "records.jsonl").write_text(
        "".join(item.model_dump_json() + "\n" for item in SEPARATED)
    )
    metrics = recompute(run_dir)
    write_report(run_dir, config, metrics)

    readme = (run_dir / "README.md").read_text()
    assert "# Score floor calibration" in readme
    assert "A corridor of 0.1300 exists" in readme
    assert "`similarity_floor`: **0.735**" in readme
    assert (run_dir / "figures" / "similarity-by-depth.svg").exists()
    assert json.loads((run_dir / "metrics.json").read_text())["proposal"]["corridor"] is True


def test_the_readme_says_plainly_when_there_is_no_corridor(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    (run_dir / "figures").mkdir(parents=True)
    config = _config()
    (run_dir / "config.json").write_text(json.dumps(config))
    (run_dir / "records.jsonl").write_text(
        "".join(item.model_dump_json() + "\n" for item in OVERLAPPING)
    )
    write_report(run_dir, config, recompute(run_dir))
    readme = (run_dir / "README.md").read_text()
    assert "**No corridor.**" in readme
    assert "No floor is proposed" in readme


def _config() -> dict[str, Any]:
    return {
        "kind": RUN_KIND,
        "variant": "sec1024",
        "top_k": 50,
        "depths": list(DEPTHS),
        "dataset": "eval/dev.jsonl",
        "dataset_sha256": "abc",
        "real_questions": 3,
        "junk_questions": len(JUNK_QUESTIONS),
        "corpus_dir": "corpus/mistral-docs",
    }
