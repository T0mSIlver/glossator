"""The floor and margin the distributions support, and every number behind them."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from glossator.eval.calibrate_floors.models import (
    DEPTHS,
    POPULATIONS,
    RUN_KIND,
    TOP_K,
    QuerySimilarities,
)
from glossator.eval.percentiles import rounded_index_percentile


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
            "p10": round(rounded_index_percentile(values, 0.10), 4) if values else None,
            "median": round(rounded_index_percentile(values, 0.50), 4) if values else None,
            "p90": round(rounded_index_percentile(values, 0.90), 4) if values else None,
            "max": round(values[-1], 4) if values else None,
        }
    return {"queries": len(rows), "scored": len(scored), "at_depth": per_depth}


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
