import json
from pathlib import Path

from glossator.eval.providers import TokenUsage
from glossator.eval.run_records import (
    STATUS_IN_PROGRESS,
    RunRecorder,
    regenerate,
)


def make_recorder(tmp_path: Path) -> RunRecorder:
    return RunRecorder(
        tmp_path / "run",
        {
            "model": "stub",
            "corpus": "fixture",
            "prompt_version": "test",
            "provider": "zai",
            "thinking": "disabled",
            "seed": 0,
            "corpus_commit": "fixture",
            "n": 6,
        },
    )


def record_one(recorder: RunRecorder) -> None:
    recorder.record_call(
        provider="zai",
        model="stub",
        messages=[{"role": "user", "content": "question"}],
        response_text='{"question": "q"}',
        parsed=None,
        usage=TokenUsage(prompt_tokens=3, completion_tokens=2, reasoning_tokens=1),
        cached=False,
        latency_ms=12.5,
        error=None,
        thinking="disabled",
    )
    recorder.record_candidate(
        {
            "generator_type": "cross_page",
            "kept": True,
            "drop_reasons": [],
        }
    )


def test_interrupted_run_keeps_in_progress_summary(tmp_path: Path) -> None:
    recorder = make_recorder(tmp_path)
    run_dir = recorder.run_dir

    metrics = json.loads((run_dir / "metrics.json").read_text())
    readme = (run_dir / "README.md").read_text()

    assert metrics["status"] == STATUS_IN_PROGRESS
    assert metrics["dataset"] is None
    assert "in progress" in readme
    assert (run_dir / "calls.jsonl").read_text() == ""
    assert (run_dir / "records.jsonl").read_text() == ""
    assert json.loads((run_dir / "config.json").read_text())["model"] == "stub"


def test_finalize_records_dataset_and_regenerate_is_stable(tmp_path: Path) -> None:
    recorder = make_recorder(tmp_path)
    run_dir = recorder.run_dir
    record_one(recorder)
    dataset = run_dir / "questions.jsonl"
    dataset.write_text("{}\n")

    recorder.finalize(dataset_path=dataset, error=None)
    metrics = json.loads((run_dir / "metrics.json").read_text())
    readme = (run_dir / "README.md").read_text()

    assert metrics["status"] == "complete"
    assert metrics["dataset"] == str(dataset)
    assert metrics["kept"] == 1
    assert metrics["usage"]["reasoning_tokens"] == 1
    assert str(dataset) in readme

    metrics_before = (run_dir / "metrics.json").read_text()
    readme_before = (run_dir / "README.md").read_text()
    regenerate(run_dir)
    assert (run_dir / "metrics.json").read_text() == metrics_before
    assert (run_dir / "README.md").read_text() == readme_before


def test_finalize_failed_renders_error_as_sentence(tmp_path: Path) -> None:
    recorder = make_recorder(tmp_path)
    run_dir = recorder.run_dir
    record_one(recorder)

    recorder.finalize(
        dataset_path=None,
        error="accepted 7 of 10 required cross-page candidates after 60 attempts",
    )
    readme = (run_dir / "README.md").read_text()
    metrics = json.loads((run_dir / "metrics.json").read_text())

    assert metrics["status"] == "failed"
    assert metrics["dataset"] is None
    assert (
        "Status: failed. Accepted 7 of 10 required cross-page candidates after "
        "60 attempts. No dataset was written." in readme
    )

    regenerate(run_dir)
    assert json.loads((run_dir / "metrics.json").read_text())["error"] == (
        "accepted 7 of 10 required cross-page candidates after 60 attempts"
    )


def test_regenerate_restores_dataset_for_legacy_summary(tmp_path: Path) -> None:
    recorder = make_recorder(tmp_path)
    run_dir = recorder.run_dir
    record_one(recorder)
    dataset = run_dir / "questions.jsonl"
    dataset.write_text("{}\n")
    recorder.finalize(dataset_path=dataset, error=None)
    metrics = json.loads((run_dir / "metrics.json").read_text())
    del metrics["dataset"]
    (run_dir / "metrics.json").write_text(json.dumps(metrics))
    config = json.loads((run_dir / "config.json").read_text())
    config["out"] = str(dataset)
    (run_dir / "config.json").write_text(json.dumps(config))

    regenerated = regenerate(run_dir)

    assert regenerated["dataset"] == str(dataset)
