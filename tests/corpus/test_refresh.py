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
    gate_dates = [(r["date"], r["commit"]) for r in json.loads(gate.read_text())["snapshots"]]
    assert gate_dates == [("2026-09-07", "abc"), (result["date"], "def")]


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
    payload = refresh.accept(
        date="2026-09-14",
        commit="def",
        run="eval/runs/x-refresh-eval",
        labels="eval/runs/x-refresh-labels/labels.jsonl",
        gate="eval/runs/x-refresh-eval/gate",
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
            gate="g",
            manifest_path=manifest,
            served_path=served,
        )


def test_served_pointer_in_the_repository_names_a_manifest_snapshot() -> None:
    served = refresh.read_served(Path("eval/refresh/served.json"))
    manifest = json.loads(Path("eval/snapshots/manifest.json").read_text())
    assert any(
        s["date"] == served["snapshot"] and s["commit"] == served["commit"]
        for s in manifest["snapshots"]
    )
    assert Path(served["run"]).is_dir() and Path(served["labels"]).is_file()
