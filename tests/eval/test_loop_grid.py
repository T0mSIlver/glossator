"""The loop-cap grid: which configurations it runs, and what its summary says.

The grid rows themselves are normal answer-eval runs, so their arithmetic is
already covered by `test_answer_eval`; what needs its own tests is the grid's
shape (one axis at a time, shipped point collapsed) and the summary that reads
the rows back.
"""

import json
from pathlib import Path
from typing import Any

from glossator.eval.loop_grid import (
    AXIS_VALUES,
    FULL_PREVIEWS,
    SHIPPED_POINT,
    configurations,
    eval_prices,
    figure_name,
    regenerate,
    summarize,
)


def test_the_grid_is_one_axis_at_a_time_with_the_shipped_point_once() -> None:
    rows = configurations()
    assert [row.name for row in rows] == [
        "shipped",
        "round-cap-6",
        "round-cap-8",
        "searches-per-round-6",
        "tool-result-chars-1500",
        "tool-result-chars-full",
    ]
    shipped = rows[0]
    assert shipped.overrides == SHIPPED_POINT
    for row in rows[1:]:
        moved = [key for key in SHIPPED_POINT if row.overrides[key] != SHIPPED_POINT[key]]
        assert moved == [row.axis or ""], f"{row.name} moves more than its own axis"


def test_full_previews_is_null_rather_than_a_magic_number() -> None:
    full = next(row for row in configurations() if row.label == FULL_PREVIEWS)
    assert full.overrides["tool_result_chars"] is None
    # And the axis's other values stay concrete sizes.
    labels = dict((label, value) for label, value in AXIS_VALUES[2][1])
    assert labels["600"] == 600 and labels["1500"] == 1500


def test_a_local_model_id_gets_a_zero_price_entry_not_a_refusal() -> None:
    prices = eval_prices("ministral-3b-local")
    assert prices["ministral-3b-local"].input_usd_per_mtok == 0.0
    # A model the eval table already prices keeps its price.
    assert eval_prices("ministral-14b-2512") is not eval_prices("ministral-3b-local")


def _row_metrics(
    path: Path,
    *,
    correctness: float,
    tokens_in: float,
    status: str = "complete",
) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "metrics.json").write_text(
        json.dumps(
            {
                "kind": "answer_eval",
                "status": status,
                "questions": 2,
                "records": 2,
                "by_strategy": {
                    "search_loop": {
                        "all": {
                            "errors": 0,
                            "correctness": correctness,
                            "groundedness": correctness - 0.1,
                            "cited_url_match": correctness - 0.2,
                            "citation_verification_rate": 0.9,
                            "rounds": 3.0,
                            "round_cap_hit": 0.5,
                            "tool_calls": 6.0,
                            "tokens_in": tokens_in,
                            "latency_p50_s": 20.0,
                        }
                    }
                },
            }
        )
    )


def _grid(tmp_path: Path, *, server: str | None = "http://gpu.example:8081/v1") -> Path:
    runs: list[dict[str, Any]] = []
    for row in configurations():
        run_path = tmp_path / f"2026-09-09-1200-{row.name}"
        _row_metrics(run_path, correctness=0.8, tokens_in=12000.0)
        runs.append(
            {
                "name": f"loop-grid-{row.name}",
                "axis": row.axis,
                "value": row.label,
                "overrides": row.overrides,
                "run_dir": str(run_path),
            }
        )
    config = {
        "kind": "loop_grid",
        "name": "loop-grid",
        "dataset": "eval/dev-fresh60.jsonl",
        "dataset_sha256": "0" * 64,
        "questions": ["q1", "q2"],
        "model": "ministral-3b-local",
        "generation_server": server,
        "judge_model": "zai:glm-5.3",
        "judge_models": ["zai:glm-5.3"],
        "variant": "sec1024",
        "response_format": "json_object",
        "shipped_point": dict(SHIPPED_POINT),
        "axes": {axis: [label for label, _value in values] for axis, values in AXIS_VALUES},
        "runs": runs,
        "notes": [],
    }
    summary = tmp_path / "2026-09-09-1200-loop-grid"
    summarize(summary, config)
    return summary


def test_the_summary_names_every_configuration_and_its_numbers(tmp_path: Path) -> None:
    summary = _grid(tmp_path)
    metrics = json.loads((summary / "metrics.json").read_text())
    assert [row["name"] for row in metrics["configurations"]] == [
        f"loop-grid-{row.name}" for row in configurations()
    ]
    row = metrics["configurations"][1]
    assert row["status"] == "complete"
    assert row["correctness"] == 0.8
    assert row["round_cap_hit"] == 0.5

    readme = (summary / "README.md").read_text()
    for caption in (
        "correctness (judge)",
        "groundedness (judge)",
        "cited URL matches gold",
        "quotes verified",
        "rounds used",
        "round cap hit",
        "tool calls",
        "prompt tokens per answer",
        "median seconds per answer",
    ):
        assert caption in readme
    assert "`round-cap-6`" in readme and "`tool-result-chars-full`" in readme


def test_the_summary_says_in_plain_words_what_the_numbers_are(tmp_path: Path) -> None:
    readme = (_grid(tmp_path) / "README.md").read_text()
    assert "http://gpu.example:8081/v1" in readme
    assert "relative" in readme
    assert "quantized Ministral 3" in readme
    assert "Mistral API" in readme


def test_the_summary_carries_one_correctness_and_one_token_figure_per_axis(
    tmp_path: Path,
) -> None:
    figures_dir = _grid(tmp_path) / "figures"
    written = sorted(path.name for path in figures_dir.glob("*.svg"))
    assert written == sorted(
        figure_name(axis, what)
        for axis, _values in AXIS_VALUES
        for what in ("correctness", "tokens")
    )
    for name in written:
        body = (figures_dir / name).read_text()
        assert body.startswith("<svg") and body.rstrip().endswith("</svg>")


def test_a_row_without_metrics_is_reported_missing_rather_than_guessed(tmp_path: Path) -> None:
    summary = _grid(tmp_path)
    missing = tmp_path / "2026-09-09-1200-round-cap-8"
    # A row that never finished has no metrics.json at all.
    (missing / "metrics.json").unlink()

    regenerated = regenerate(summary)
    row = next(row for row in regenerated["configurations"] if row["name"].endswith("round-cap-8"))
    assert row["status"] == "missing"
    assert row["correctness"] is None
    assert "(missing)" in (summary / "README.md").read_text()


def test_the_summary_regenerates_from_its_rows(tmp_path: Path) -> None:
    summary = _grid(tmp_path)
    (summary / "README.md").write_text("stale")

    metrics = regenerate(summary)

    assert metrics["kind"] == "loop_grid"
    assert "Search-loop cap grid" in (summary / "README.md").read_text()
    assert len(metrics["configurations"]) == len(configurations())
