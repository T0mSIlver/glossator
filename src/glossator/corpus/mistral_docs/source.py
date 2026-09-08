"""Fetch the docs repository at a pinned ref into a local cache directory."""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import structlog

from . import DOCS_REPO_URL

log = structlog.get_logger(__name__)

DEFAULT_CACHE_DIR = Path.home() / ".cache" / "glossator" / "platform-docs-public"

# Deepening steps used when a ref is not reachable from a shallow clone. Tags and
# branch heads are reachable at depth 1; an older commit needs history.
_DEEPEN_STEPS = (50, 500, 0)

_FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


class SourceError(RuntimeError):
    """The docs repository could not be fetched or checked out."""


@dataclass(frozen=True)
class DocsCheckout:
    """A working tree of the docs repository at a resolved commit."""

    path: Path
    ref: str
    commit: str

    @property
    def content_root(self) -> Path:
        return self.path / "src" / "content"


def _git(args: list[str], cwd: Path | None = None) -> str:
    proc = subprocess.run(  # noqa: S603 - fixed argv, no shell
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise SourceError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def _try_git(args: list[str], cwd: Path | None = None) -> bool:
    proc = subprocess.run(  # noqa: S603 - fixed argv, no shell
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode == 0


def _has_commit(repo: Path, ref: str) -> bool:
    # `--verify <ref>^{commit}` succeeds only when the object is present locally.
    return _try_git(["rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"], cwd=repo)


def _is_immutable(ref: str) -> bool:
    """A full commit sha always names the same commit; every other ref can move."""
    return _FULL_SHA.match(ref) is not None


def fetch_docs_repo(
    ref: str,
    cache_dir: Path = DEFAULT_CACHE_DIR,
    repo_url: str = DOCS_REPO_URL,
) -> DocsCheckout:
    """Clone (or reuse) the docs repository and check out `ref`.

    Starts from a `--depth 1` clone and deepens only when the ref is not reachable,
    so the common case of a recent commit stays a small download.
    """
    cache_dir = cache_dir.expanduser()
    git_dir = cache_dir / ".git"

    if git_dir.is_dir():
        log.debug("docs repo cache hit", path=str(cache_dir))
    else:
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
        cache_dir.parent.mkdir(parents=True, exist_ok=True)
        log.info("cloning docs repo", url=repo_url, path=str(cache_dir))
        _git(["clone", "--depth", "1", repo_url, str(cache_dir)])

    target = _resolve_ref(cache_dir, ref, repo_url)
    _git(["checkout", "--force", "--detach", target], cwd=cache_dir)
    _git(["clean", "-fdx", "--quiet"], cwd=cache_dir)
    commit = _git(["rev-parse", "HEAD"], cwd=cache_dir)
    log.info("docs repo ready", ref=ref, commit=commit, path=str(cache_dir))
    return DocsCheckout(path=cache_dir, ref=ref, commit=commit)


def _resolve_ref(cache_dir: Path, ref: str, repo_url: str) -> str:
    """The commit `ref` names now, fetching whenever the ref can have moved.

    A cached branch or tag is stale the moment upstream advances, so only a full
    commit sha already in the cache skips the network.
    """
    if _is_immutable(ref) and _has_commit(cache_dir, ref):
        return ref

    if _try_git(["fetch", "--depth", "1", "origin", ref], cwd=cache_dir):
        return _git(["rev-parse", "FETCH_HEAD^{commit}"], cwd=cache_dir)

    for depth in _DEEPEN_STEPS:
        if _has_commit(cache_dir, ref):
            return ref
        if depth == 0:
            log.info("deepening docs repo to full history", ref=ref)
            # Best effort: `--unshallow` errors on a clone that is already complete,
            # which is exactly the case where there is nothing left to deepen.
            if not _try_git(["fetch", "--unshallow", "--tags", "origin"], cwd=cache_dir):
                _try_git(["fetch", "--tags", "origin"], cwd=cache_dir)
        else:
            log.info("deepening docs repo", ref=ref, depth=depth)
            _try_git(["fetch", f"--depth={depth}", "origin"], cwd=cache_dir)

    if _has_commit(cache_dir, ref):
        return ref
    raise SourceError(f"ref {ref!r} is not reachable in {repo_url}")


def use_existing_checkout(path: Path, ref: str | None = None) -> DocsCheckout:
    """Wrap an already-present working tree, for offline builds and tests.

    The tree need not be a git checkout: an exported copy still builds, and then the
    ref is the only provenance there is to record on the pages.
    """
    path = path.expanduser().resolve()
    if not (path / "src" / "content").is_dir():
        raise SourceError(f"{path} does not look like the docs repository")
    try:
        commit = _git(["rev-parse", "HEAD"], cwd=path)
    except SourceError:
        if ref is None:
            raise SourceError(f"{path} has no commit to read, so a ref is required") from None
        log.info("checkout has no commit, recording the ref", path=str(path), ref=ref)
        commit = ref
    return DocsCheckout(path=path, ref=ref or commit, commit=commit)
