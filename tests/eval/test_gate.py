"""The refresh gate: paired net loss beyond the repeat-run noise (D-045)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from glossator.eval.gate import (
    Cell,
    compare,
    main,
    page,
    read_cells,
    render,
    threshold_for,
)


def cell(
    question_id: str,
    *,
    label: str | None = "present",
    question_type: str = "single_page",
    retrieved: bool = True,
    cited: bool = True,
    refused: bool = False,
    verdict: str | None = "correct",
    error: str | None = None,
) -> Cell:
    return Cell(
        question_id=question_id,
        dataset="fixture",
        question_type=question_type,
        label=label,
        accepted_pages=frozenset({"https://docs.example/page"}),
        retrieved=retrieved,
        cited=cited,
        refused=refused,
        verdict=verdict,
        error=error,
    )


def population(n: int, **overrides: object) -> dict[str, Cell]:
    return {f"q{i}": cell(f"q{i}", **overrides) for i in range(n)}  # type: ignore[arg-type]


def test_threshold_is_the_larger_of_floor_and_share() -> None:
    assert threshold_for(20, share=0.05, floor=3) == 3
    assert threshold_for(145, share=0.05, floor=3) == 8
    assert threshold_for(0, share=0.05, floor=3) == 3


def test_page_drops_the_fragment_only() -> None:
    assert page("https://docs.example/a/b#anchor") == "https://docs.example/a/b"
    assert page("https://docs.example/a/b?x=1") == "https://docs.example/a/b?x=1"


def test_symmetric_churn_passes() -> None:
    baseline = population(60)
    candidate = population(60)
    # Six verdict flips, three each way: the repeat-run noise floor.
    for q in ("q0", "q1", "q2"):
        candidate[q] = cell(q, verdict="partial")
    for q in ("q3", "q4", "q5"):
        baseline[q] = cell(q, verdict="partial")
    result = compare(baseline, candidate)
    assert result["verdict"] == "pass"
    correct = next(s for s in result["signals"] if s["signal"] == "correct")
    assert len(correct["worse"]) == 3 and len(correct["better"]) == 3
    assert correct["net_loss"] == 0


def test_net_loss_beyond_threshold_is_a_regression() -> None:
    baseline = population(60)
    candidate = population(60)
    for q in ("q0", "q1", "q2", "q3"):
        candidate[q] = cell(q, cited=False)
    result = compare(baseline, candidate)
    assert result["verdict"] == "regression"
    assert result["regressed_signals"] == ["cited"]
    cited = next(s for s in result["signals"] if s["signal"] == "cited")
    assert cited["net_loss"] == 4 and cited["threshold"] == 3


def test_net_loss_at_threshold_passes() -> None:
    baseline = population(60)
    candidate = population(60)
    for q in ("q0", "q1", "q2"):
        candidate[q] = cell(q, retrieved=False)
    assert compare(baseline, candidate)["verdict"] == "pass"


def test_only_questions_present_in_both_snapshots_are_paired() -> None:
    baseline = population(10)
    candidate = population(10)
    candidate["q0"] = cell("q0", label="absent", cited=False, verdict="wrong")
    candidate["q1"] = cell("q1", label=None, cited=False)
    result = compare(baseline, candidate)
    assert result["paired_answerable"] == 8
    assert "q0" in result["dropped_from_population"]
    assert "q1" in result["dropped_from_population"]
    assert result["verdict"] == "pass"


def test_refusal_is_scored_on_absent_cells_and_unanswerable_questions() -> None:
    baseline = {
        "u0": cell("u0", question_type="unanswerable", label="absent", refused=True, verdict=None),
        "u1": cell("u1", question_type="unanswerable", label="absent", refused=True, verdict=None),
        "a0": cell("a0", label="absent", refused=True, verdict=None),
    }
    candidate = {
        "u0": cell("u0", question_type="unanswerable", label="absent", refused=False, verdict=None),
        "u1": cell("u1", question_type="unanswerable", label="absent", refused=True, verdict=None),
        "a0": cell("a0", label="absent", refused=True, verdict=None),
    }
    result = compare(baseline, candidate)
    refused = next(s for s in result["signals"] if s["signal"] == "refused")
    assert refused["population"] == 3
    assert refused["worse"] == [{"question_id": "u0", "before": True, "after": False}]
    assert result["verdict"] == "pass"


def test_too_many_unscored_cells_is_inconclusive_not_a_pass() -> None:
    baseline = population(20)
    candidate = population(20)
    for q in ("q0", "q1", "q2"):
        candidate[q] = cell(q, error="HTTP 429")
    result = compare(baseline, candidate)
    assert result["verdict"] == "inconclusive"
    assert result["candidate_unscored"] == 3


def test_unjudged_runs_gate_on_the_deterministic_signals() -> None:
    baseline = population(10, verdict=None)
    candidate = population(10, verdict=None)
    result = compare(baseline, candidate)
    correct = next(s for s in result["signals"] if s["signal"] == "correct")
    assert correct["population"] == 0 and correct["baseline_mean"] is None
    assert result["verdict"] == "pass"


def _write_run(tmp_path: Path, name: str, rows: list[dict]) -> Path:
    run = tmp_path / name
    run.mkdir()
    (run / "records.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    return run


def _record(
    question_id: str,
    snapshot: str,
    *,
    gold: str = "https://docs.example/page",
    source: str = "https://docs.example/page#s",
    cited_url: str | None = "https://docs.example/page",
    refused: bool = False,
    verdict: str | None = "correct",
    label: str = "present",
) -> dict:
    return {
        "question_id": question_id,
        "snapshot": snapshot,
        "question_type": "single_page",
        "availability_label": label,
        "gold_urls": [gold],
        "trace": {"sources": [{"citation_url": source}]},
        "citations": [{"url": cited_url}] if cited_url else [],
        "insufficient_evidence": refused,
        "judge": {"verdict": {"correctness": verdict}} if verdict else None,
        "error": None,
    }


def test_read_cells_uses_the_label_file_page_for_moved_facts(tmp_path: Path) -> None:
    run = _write_run(
        tmp_path,
        "run",
        [
            _record(
                "q0",
                "2026-09-07",
                gold="https://docs.example/old",
                source="https://docs.example/new#s",
                cited_url="https://docs.example/new",
            )
        ],
    )
    labels = tmp_path / "labels.jsonl"
    labels.write_text(
        json.dumps(
            {
                "question_id": "q0",
                "snapshot": "2026-09-07",
                "label": "present",
                "moved": True,
                "page": "https://docs.example/new",
            }
        )
        + "\n"
    )
    without = read_cells(run / "records.jsonl", snapshot="2026-09-07")
    assert not without["q0"].retrieved and not without["q0"].cited
    with_labels = read_cells(run / "records.jsonl", snapshot="2026-09-07", labels_path=labels)
    assert with_labels["q0"].retrieved and with_labels["q0"].cited


def test_cli_writes_gate_files_and_exit_code_names_the_verdict(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rows_old = [_record(f"q{i}", "2026-09-01") for i in range(10)]
    rows_new = [_record(f"q{i}", "2026-09-07") for i in range(10)]
    for i in range(4):
        rows_new[i] = _record(f"q{i}", "2026-09-07", cited_url=None, verdict="wrong")
    baseline = _write_run(tmp_path, "baseline", rows_old)
    candidate = _write_run(tmp_path, "candidate", rows_new)
    out = tmp_path / "gate"
    code = main(
        [
            "--baseline",
            str(baseline),
            "--baseline-snapshot",
            "2026-09-01",
            "--candidate",
            str(candidate),
            "--candidate-snapshot",
            "2026-09-07",
            "--output",
            str(out),
        ]
    )
    assert code == 1
    result = json.loads((out / "gate.json").read_text())
    assert result["verdict"] == "regression"
    assert set(result["regressed_signals"]) == {"cited", "correct"}
    text = (out / "gate.md").read_text()
    assert text.startswith("# Refresh gate: regression")
    assert "`q0`: correct → wrong" in text
    assert capsys.readouterr().out.startswith("# Refresh gate: regression")


def test_render_reports_inconclusive_counts() -> None:
    result = compare(population(10), population(10, error="down"))
    text = render(result, baseline_name="b", candidate_name="c")
    assert "# Refresh gate: inconclusive" in text
    assert "10 of 10 candidate cells" in text
