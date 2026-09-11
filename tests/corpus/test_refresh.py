"""Candidate snapshots and the served pointer (D-045)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from glossator.corpus import refresh
from glossator.corpus.snapshots import SnapshotRecord, write_snapshot_manifest


def _served(tmp_path: Path, snapshot: str, commit: str) -> Path:
    path = tmp_path / "served.json"
    refresh.write_served(path, {"snapshot": snapshot, "commit": commit})
    return path


def _manifest(tmp_path: Path, *records: SnapshotRecord) -> Path:
    path = tmp_path / "manifest.json"
    write_snapshot_manifest(path, list(records))
    return path


def _record(date: str, commit: str) -> SnapshotRecord:
    return SnapshotRecord(
        date=date,
        commit=commit,
        pages=1,
        content_digest="d",
        corpus_dir=f"~/snapshots/{date}",
        status="built",
        error=None,
        openapi_source=None,
        openapi_snapshot_exact=False,
        models_snapshot_exact=True,
    )


def _gate(tmp_path: Path, verdict: str = "pass") -> str:
    gate = tmp_path / "gate"
    gate.mkdir(exist_ok=True)
    (gate / "gate.json").write_text(json.dumps({"verdict": verdict}))
    return str(gate)


@dataclass
class _Checkout:
    path: Path
    ref: str
    commit: str


@dataclass
class _Summary:
    total_pages: int = 3


def test_head_equal_to_served_is_not_a_candidate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        refresh, "fetch_docs_repo", lambda ref, cache_dir: _Checkout(tmp_path, ref, "abc")
    )
    served = _served(tmp_path, "2026-09-07", "abc")
    manifest = _manifest(tmp_path, _record("2026-09-07", "abc"))
    result = refresh.build_candidate(
        manifest_path=manifest,
        snapshot_root=tmp_path / "snapshots",
        repo=tmp_path / "repo",
        served_path=served,
        gate_manifest=tmp_path / "gate.json",
    )
    assert result == {
        "changed": False,
        "commit": "abc",
        "served_commit": "abc",
        "served_snapshot": "2026-09-07",
    }
    assert not (tmp_path / "gate.json").exists()


def test_new_head_becomes_a_candidate_beside_the_served_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    checkout = _Checkout(tmp_path / "checkout", "main", "def")
    checkout.path.mkdir()
    monkeypatch.setattr(refresh, "fetch_docs_repo", lambda ref, cache_dir: checkout)
    monkeypatch.setattr(refresh, "build_corpus", lambda *a, **k: _Summary())
    monkeypatch.setattr(refresh, "corpus_digest", lambda corpus_dir: "digest")
    served = _served(tmp_path, "2026-09-07", "abc")
    manifest = _manifest(tmp_path, _record("2026-09-01", "old"), _record("2026-09-07", "abc"))
    gate = tmp_path / "gate.json"
    result = refresh.build_candidate(
        manifest_path=manifest,
        snapshot_root=tmp_path / "snapshots",
        repo=tmp_path / "repo",
        served_path=served,
        gate_manifest=gate,
    )
    assert result["changed"] is True
    assert result["commit"] == "def"
    assert result["served_snapshot"] == "2026-09-07"
    dates = [r["date"] for r in json.loads(manifest.read_text())["snapshots"]]
    assert dates == ["2026-09-01", "2026-09-07", result["date"]]
    gate_rows = json.loads(gate.read_text())["snapshots"]
    assert [(r["date"], r["commit"]) for r in gate_rows] == [
        ("2026-09-07", "abc"),
        (result["date"], "def"),
    ]
    # The served snapshot's corpus is the vendored one on a runner, not a cache path.
    assert gate_rows[0]["corpus_dir"] == "corpus/mistral-docs"
    assert gate_rows[1]["status"] == "built"


def test_build_refuses_to_overwrite_a_fixed_snapshot_date(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from datetime import UTC, datetime

    today = datetime.now(UTC).strftime("%Y-%m-%d")
    checkout = _Checkout(tmp_path / "checkout", "main", "def")
    checkout.path.mkdir()
    monkeypatch.setattr(refresh, "fetch_docs_repo", lambda ref, cache_dir: checkout)
    monkeypatch.setattr(refresh, "build_corpus", lambda *a, **k: _Summary())
    served = _served(tmp_path, "2026-09-07", "abc")
    manifest = _manifest(tmp_path, _record("2026-09-07", "abc"), _record(today, "historical"))
    with pytest.raises(ValueError, match="already records commit historical"):
        refresh.build_candidate(
            manifest_path=manifest,
            snapshot_root=tmp_path / "snapshots",
            repo=tmp_path / "repo",
            served_path=served,
            gate_manifest=tmp_path / "gate.json",
        )


def test_cli_writes_the_json_to_the_output_file_and_stdout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        refresh, "fetch_docs_repo", lambda ref, cache_dir: _Checkout(tmp_path, ref, "abc")
    )
    served = _served(tmp_path, "2026-09-07", "abc")
    manifest = _manifest(tmp_path, _record("2026-09-07", "abc"))
    out = tmp_path / "candidate.json"
    code = refresh.main(
        [
            "build",
            "--manifest",
            str(manifest),
            "--out",
            str(tmp_path / "snapshots"),
            "--repo",
            str(tmp_path / "repo"),
            "--served",
            str(served),
            "--gate-manifest",
            str(tmp_path / "gate.json"),
            "--output",
            str(out),
        ]
    )
    assert code == 0
    assert json.loads(out.read_text())["changed"] is False
    assert json.loads(capsys.readouterr().out)["changed"] is False


def test_build_refuses_when_the_served_snapshot_is_missing_from_the_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    checkout = _Checkout(tmp_path / "checkout", "main", "def")
    checkout.path.mkdir()
    monkeypatch.setattr(refresh, "fetch_docs_repo", lambda ref, cache_dir: checkout)
    monkeypatch.setattr(refresh, "build_corpus", lambda *a, **k: _Summary())
    monkeypatch.setattr(refresh, "corpus_digest", lambda corpus_dir: "digest")
    served = _served(tmp_path, "2026-09-07", "abc")
    manifest = _manifest(tmp_path, _record("2026-09-01", "old"))
    with pytest.raises(ValueError, match="served snapshot 2026-09-07"):
        refresh.build_candidate(
            manifest_path=manifest,
            snapshot_root=tmp_path / "snapshots",
            repo=tmp_path / "repo",
            served_path=served,
            gate_manifest=tmp_path / "gate.json",
        )


def test_accept_moves_the_served_pointer_to_a_manifest_snapshot(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path, _record("2026-09-07", "abc"), _record("2026-09-14", "def"))
    served = _served(tmp_path, "2026-09-07", "abc")
    gate = _gate(tmp_path)
    payload = refresh.accept(
        date="2026-09-14",
        commit="def",
        run="eval/runs/x-refresh-eval",
        labels="eval/runs/x-refresh-labels/labels.jsonl",
        gate=gate,
        manifest_path=manifest,
        served_path=served,
    )
    stored = refresh.read_served(served)
    assert stored["snapshot"] == "2026-09-14" and stored["commit"] == "def"
    assert stored["run"] == payload["run"] and stored["accepted_at"]
    with pytest.raises(ValueError, match="no snapshot"):
        refresh.accept(
            date="2026-09-21",
            commit="ghi",
            run="r",
            labels="l",
            gate=gate,
            manifest_path=manifest,
            served_path=served,
        )


def test_accept_refuses_a_gate_that_did_not_pass(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path, _record("2026-09-07", "abc"), _record("2026-09-14", "def"))
    served = _served(tmp_path, "2026-09-07", "abc")
    with pytest.raises(ValueError, match="regression"):
        refresh.accept(
            date="2026-09-14",
            commit="def",
            run="eval/runs/x-refresh-eval",
            labels="eval/runs/x-refresh-labels/labels.jsonl",
            gate=_gate(tmp_path, verdict="regression"),
            manifest_path=manifest,
            served_path=served,
        )
    stored = refresh.read_served(served)
    assert stored["snapshot"] == "2026-09-07" and stored["commit"] == "abc"


def test_served_pointer_in_the_repository_names_a_manifest_snapshot() -> None:
    served = refresh.read_served(Path("eval/refresh/served.json"))
    manifest = json.loads(Path("eval/snapshots/manifest.json").read_text())
    assert any(
        s["date"] == served["snapshot"] and s["commit"] == served["commit"]
        for s in manifest["snapshots"]
    )
    assert Path(served["run"]).is_dir() and Path(served["labels"]).is_file()
