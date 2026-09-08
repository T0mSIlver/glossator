"""Fetching the docs repository at a ref, against a local origin (no network)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from glossator.corpus.mistral_docs import source as source_module
from glossator.corpus.mistral_docs.source import (
    SourceError,
    fetch_docs_repo,
    use_existing_checkout,
)


def _git(args: list[str], cwd: Path) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True
    ).stdout.strip()


Origin = tuple[Path, str, str]


@pytest.fixture
def origin(tmp_path: Path) -> Origin:
    """A tiny repository with two commits, standing in for the docs repo."""
    repo = tmp_path / "origin"
    (repo / "src" / "content").mkdir(parents=True)
    _git(["init", "--initial-branch=main", "--quiet", "."], repo)
    _git(["config", "user.email", "test@example.invalid"], repo)
    _git(["config", "user.name", "Test"], repo)
    (repo / "src" / "content" / "first.txt").write_text("one", encoding="utf-8")
    _git(["add", "-A"], repo)
    _git(["commit", "--quiet", "-m", "first"], repo)
    first = _git(["rev-parse", "HEAD"], repo)
    (repo / "src" / "content" / "second.txt").write_text("two", encoding="utf-8")
    _git(["add", "-A"], repo)
    _git(["commit", "--quiet", "-m", "second"], repo)
    head = _git(["rev-parse", "HEAD"], repo)
    return repo, first, head


def test_head_is_reachable_from_a_shallow_clone(tmp_path: Path, origin: Origin) -> None:
    repo, _, head = origin
    checkout = fetch_docs_repo(head, cache_dir=tmp_path / "cache", repo_url=str(repo))
    assert checkout.commit == head
    assert (checkout.content_root / "second.txt").is_file()


def test_an_older_ref_deepens_the_clone(tmp_path: Path, origin: Origin) -> None:
    repo, first, _ = origin
    checkout = fetch_docs_repo(first, cache_dir=tmp_path / "cache", repo_url=str(repo))
    assert checkout.commit == first
    assert not (checkout.content_root / "second.txt").exists()


def test_the_cache_is_reused_for_a_second_ref(tmp_path: Path, origin: Origin) -> None:
    repo, first, head = origin
    cache = tmp_path / "cache"
    fetch_docs_repo(head, cache_dir=cache, repo_url=str(repo))
    checkout = fetch_docs_repo(first, cache_dir=cache, repo_url=str(repo))
    assert checkout.commit == first


def test_a_branch_is_refetched_after_it_advances(tmp_path: Path, origin: Origin) -> None:
    repo, _, head = origin
    cache = tmp_path / "cache"
    first = fetch_docs_repo("main", cache_dir=cache, repo_url=str(repo))
    assert first.commit == head

    (repo / "src" / "content" / "third.txt").write_text("three", encoding="utf-8")
    _git(["add", "-A"], repo)
    _git(["commit", "--quiet", "-m", "third"], repo)
    advanced = _git(["rev-parse", "HEAD"], repo)

    # A cached branch is stale the moment upstream moves, so it must be refetched.
    second = fetch_docs_repo("main", cache_dir=cache, repo_url=str(repo))
    assert second.commit == advanced
    assert (second.content_root / "third.txt").is_file()


def test_a_cached_full_sha_is_not_refetched(
    tmp_path: Path, origin: Origin, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _, head = origin
    cache = tmp_path / "cache"
    fetch_docs_repo(head, cache_dir=cache, repo_url=str(repo))

    real_try_git = source_module._try_git

    def refuse_fetch(args: list[str], **kwargs: object) -> bool:
        if args and args[0] == "fetch":
            raise AssertionError("a full commit sha already in the cache needs no network")
        return bool(real_try_git(args, **kwargs))  # type: ignore[arg-type]

    monkeypatch.setattr(source_module, "_try_git", refuse_fetch)
    assert fetch_docs_repo(head, cache_dir=cache, repo_url=str(repo)).commit == head


def test_an_unknown_ref_fails(tmp_path: Path, origin: Origin) -> None:
    repo, _, _ = origin
    with pytest.raises(SourceError, match="not reachable"):
        fetch_docs_repo("0" * 40, cache_dir=tmp_path / "cache", repo_url=str(repo))


def test_an_existing_checkout_is_accepted(origin: Origin) -> None:
    repo, _, head = origin
    checkout = use_existing_checkout(repo)
    assert checkout.commit == head


def test_a_directory_that_is_not_the_docs_repo_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(SourceError, match="docs repository"):
        use_existing_checkout(tmp_path)
