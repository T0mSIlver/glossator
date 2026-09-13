"""The run directory: what it claims, and whether it can be rebuilt from its rows."""

import json
from pathlib import Path

import pytest

from glossator.eval.generate.models import GenerationAttempt
from glossator.eval.providers import TokenUsage
from glossator.eval.report import rebuild, render_figures
from glossator.eval.run_records import (
    STATUS_IN_PROGRESS,
    RunRecorder,
    create_run_directory,
    regenerate,
)

CONFIG = {
    "model": "glm-5.3-flash",
    "corpus": "corpus/mistral-docs",
    "prompt_version": "v1",
    "provider": "zai",
    "thinking": "disabled",
    "seed": 0,
    "corpus_commit": "2e094f7",
    "n": 6,
}


def make_recorder(tmp_path: Path) -> RunRecorder:
    return RunRecorder.start(tmp_path / "run", CONFIG)


def attempt(*, kept: bool, drop_reasons: list[str], error: str | None = None) -> GenerationAttempt:
    return GenerationAttempt(
        candidate_id="cand-1",
        generator_type="cross_page",
        seed=["https://docs.mistral.ai/agents/conversations"],
        kept=kept,
        drop_reasons=drop_reasons,
        sampled_sources=[],
        error=error,
    )


def record_one(recorder: RunRecorder, *, kept: bool = True, kind: str = "generation") -> None:
    recorder.record_call(
        provider="zai",
        model="glm-5.3-flash",
        endpoint="https://api.z.ai/api/coding/paas/v4/",
        messages=[{"role": "user", "content": "question"}],
        response_text='{"question": "q"}',
        parsed=None,
        usage=TokenUsage(prompt_tokens=3, completion_tokens=2, reasoning_tokens=1),
        cached=False,
        latency_ms=12.5,
        error=None,
        thinking="disabled",
        temperature=0.7,
        max_tokens=700,
        response_format={"type": "json_object"},
        schema_name="CandidateOutput",
        schema_hash="abc123",
        seed=0,
        finish_reason="stop",
        candidate_id="cand-1",
        call_kind=kind,
    )
    recorder.record_candidate(attempt(kept=kept, drop_reasons=[] if kept else ["not standalone"]))


def test_an_interrupted_run_keeps_an_in_progress_summary(tmp_path: Path) -> None:
    recorder = make_recorder(tmp_path)
    run_dir = recorder.run_dir

    metrics = json.loads((run_dir / "metrics.json").read_text())

    assert metrics["status"] == STATUS_IN_PROGRESS
    assert metrics["dataset"] is None
    assert "had not finished" in (run_dir / "README.md").read_text()
    assert (run_dir / "calls.jsonl").read_text() == ""
    assert json.loads((run_dir / "config.json").read_text())["model"] == "glm-5.3-flash"


def test_the_conclusion_is_computed_from_the_numbers(tmp_path: Path) -> None:
    recorder = make_recorder(tmp_path)
    record_one(recorder, kept=True)
    record_one(recorder, kept=False)
    dataset = recorder.run_dir / "questions.jsonl"
    dataset.write_text("{}\n")

    recorder.finalize(
        dataset_path=dataset,
        error=None,
        shortfalls={"post_cutoff": 2},
        requested_by_type={"cross_page": 1, "post_cutoff": 2},
    )
    readme = (recorder.run_dir / "README.md").read_text()
    metrics = json.loads((recorder.run_dir / "metrics.json").read_text())

    assert "accepted 1 of 2 candidates" in readme
    assert "post_cutoff short by 2" in readme
    assert "The largest drop reasons were not standalone (1)" in readme
    assert "0.00 USD against the Mistral budget" in readme
    assert metrics["shortfall"] == 2
    assert metrics["estimated_usd"] == 0.0
    assert metrics["usage_by_kind"]["generation"]["prompt_tokens"] == 6


def test_a_priced_model_reports_a_cost(tmp_path: Path) -> None:
    recorder = RunRecorder.start(tmp_path / "run", {**CONFIG, "model": "mistral-medium-3-5"})
    record_one(recorder)

    recorder.finalize(dataset_path=None, error=None)
    metrics = json.loads((recorder.run_dir / "metrics.json").read_text())

    assert metrics["estimated_usd"] == pytest.approx(3 / 1e6 * 1.50 + 2 / 1e6 * 7.50, abs=5e-7)
    assert "USD" in (recorder.run_dir / "README.md").read_text()


def test_a_failed_run_says_why(tmp_path: Path) -> None:
    recorder = make_recorder(tmp_path)
    record_one(recorder)

    recorder.finalize(dataset_path=None, error="the corpus directory does not exist")
    readme = (recorder.run_dir / "README.md").read_text()

    assert "Status" not in readme.split("## Conclusion")[1]
    assert "The corpus directory does not exist. No dataset was written." in readme
    assert json.loads((recorder.run_dir / "metrics.json").read_text())["status"] == "failed"


def test_regenerate_rebuilds_the_readme_from_the_rows_alone(tmp_path: Path) -> None:
    recorder = make_recorder(tmp_path)
    record_one(recorder)
    recorder.finalize(dataset_path=None, error=None, requested_by_type={"cross_page": 1})
    metrics_before = (recorder.run_dir / "metrics.json").read_text()
    readme_before = (recorder.run_dir / "README.md").read_text()

    (recorder.run_dir / "README.md").write_text("hand-written nonsense\n")
    regenerate(recorder.run_dir)

    assert (recorder.run_dir / "metrics.json").read_text() == metrics_before
    assert (recorder.run_dir / "README.md").read_text() == readme_before


def test_summarize_handles_a_candidate_that_failed_before_the_filter(tmp_path: Path) -> None:
    recorder = make_recorder(tmp_path)
    recorder.record_candidate(
        attempt(kept=False, drop_reasons=["provider_error"], error="HTTP 500")
    )

    recorder.finalize(dataset_path=None, error=None)
    metrics = json.loads((recorder.run_dir / "metrics.json").read_text())

    assert metrics["dropped_by_reason"] == {"provider_error": 1}
    assert metrics["kept"] == 0


def test_rebuild_writes_the_three_figures(tmp_path: Path) -> None:
    recorder = make_recorder(tmp_path)
    record_one(recorder, kept=True)
    record_one(recorder, kept=False, kind="filter")
    recorder.finalize(dataset_path=None, error=None)

    rebuild(recorder.run_dir)
    figures = sorted(path.name for path in (recorder.run_dir / "figures").glob("*.svg"))

    assert figures == ["accepted-by-type.svg", "drop-reasons.svg", "tokens-by-call-kind.svg"]
    chart = (recorder.run_dir / "figures" / "accepted-by-type.svg").read_text()
    assert chart.startswith("<svg")
    assert "cross_page" in chart


def test_a_figure_escapes_its_labels(tmp_path: Path) -> None:
    written = render_figures(
        {
            "candidates_by_type": {"a & b": 2},
            "kept_by_type": {"a & b": 1},
            "dropped_by_reason": {},
            "usage_by_kind": {},
        },
        tmp_path / "figures",
    )

    chart = written[0].read_text()
    assert "a &amp; b" in chart
    assert "a & b" not in chart


def test_run_directories_are_named_in_utc(tmp_path: Path) -> None:
    first = create_run_directory("Dev Smoke!", root=tmp_path)
    first.mkdir(parents=True)
    second = create_run_directory("Dev Smoke!", root=tmp_path)

    assert first.name.endswith("-dev-smoke")
    assert second.name == f"{first.name}-2"
