"""Reading the vendored corpus: one markdown page with YAML frontmatter per route.

The corpus adapter (``glossator.corpus``) writes these files; ingestion only
reads them, so the format is validated here rather than trusted.
"""

import hashlib
import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import structlog
import yaml

logger = structlog.get_logger(__name__)

_FRONTMATTER_FENCE = "---"

MANIFEST_NAME = "manifest.json"

# Frontmatter keys every page carries. A missing one is a corpus bug, not a page
# variation, so it fails the ingest rather than defaulting.
_REQUIRED_KEYS = ("url", "title", "kind", "locale", "source_path", "source_commit")

_KINDS = frozenset({"doc", "api", "model"})


class CorpusError(ValueError):
    """A corpus file does not match the format ingestion expects."""


@dataclass(frozen=True, slots=True)
class CorpusPage:
    """One normalized documentation page.

    ``body`` is the markdown after the frontmatter. Every offset in the ingestion
    pipeline -- section spans, chunk ``start_offset``/``end_offset`` -- indexes
    into this string, so that a chunk can always be located in the file on disk
    by skipping the frontmatter.
    """

    path: Path
    url: str
    title: str
    kind: str
    locale: str
    source_path: str
    source_commit: str
    breadcrumbs: tuple[str, ...]
    body: str


def _split_frontmatter(text: str, *, path: Path) -> tuple[dict[str, Any], str]:
    """Return the parsed frontmatter mapping and the body that follows it."""
    if not text.startswith(_FRONTMATTER_FENCE):
        raise CorpusError(f"{path}: page does not start with a YAML frontmatter fence")
    end = text.find(f"\n{_FRONTMATTER_FENCE}", len(_FRONTMATTER_FENCE))
    if end == -1:
        raise CorpusError(f"{path}: unterminated YAML frontmatter")
    raw = text[len(_FRONTMATTER_FENCE) : end]
    # Skip the closing fence line and the newline that ends it.
    body_start = text.find("\n", end + 1)
    body = "" if body_start == -1 else text[body_start + 1 :]
    try:
        parsed = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise CorpusError(f"{path}: frontmatter is not valid YAML") from exc
    if not isinstance(parsed, dict):
        raise CorpusError(f"{path}: frontmatter is not a mapping")
    return parsed, body


def parse_page(text: str, *, path: Path) -> CorpusPage:
    """Parse one corpus file into a page. Raises ``CorpusError`` on a bad file."""
    front, body = _split_frontmatter(text, path=path)

    missing = [key for key in _REQUIRED_KEYS if not front.get(key)]
    if missing:
        raise CorpusError(f"{path}: frontmatter is missing {missing}")
    kind = str(front["kind"])
    if kind not in _KINDS:
        raise CorpusError(f"{path}: kind {kind!r} is not one of {sorted(_KINDS)}")

    breadcrumbs = front.get("breadcrumbs") or []
    if not isinstance(breadcrumbs, list):
        raise CorpusError(f"{path}: breadcrumbs is not a list")

    return CorpusPage(
        path=path,
        url=str(front["url"]),
        title=str(front["title"]),
        kind=kind,
        locale=str(front["locale"]),
        source_path=str(front["source_path"]),
        source_commit=str(front["source_commit"]),
        breadcrumbs=tuple(str(crumb) for crumb in breadcrumbs),
        body=body,
    )


def load_page(path: Path) -> CorpusPage:
    return parse_page(path.read_text(encoding="utf-8"), path=path)


def iter_page_paths(corpus_dir: Path) -> Iterator[Path]:
    """Markdown files of a corpus directory, in a stable order.

    Ordering is by path so that two ingest runs over the same corpus process
    pages in the same sequence, which makes a partial run's progress readable.
    """
    if not corpus_dir.is_dir():
        raise CorpusError(f"{corpus_dir}: corpus directory not found")
    yield from sorted(corpus_dir.rglob("*.md"))


def read_manifest(corpus_dir: Path) -> list[dict[str, Any]]:
    """Manifest entries, or an empty list when the corpus ships without one.

    The manifest is a cross-check (it names the source commit and content hash
    of each page), not the index of what to ingest: the pages on disk are.
    """
    manifest = corpus_dir / MANIFEST_NAME
    if not manifest.is_file():
        return []
    loaded = json.loads(manifest.read_text(encoding="utf-8"))
    pages = loaded.get("pages", []) if isinstance(loaded, dict) else loaded
    if not isinstance(pages, list):
        raise CorpusError(f"{manifest}: expected a list of page entries")
    return [entry for entry in pages if isinstance(entry, dict)]


def verify_manifest(corpus_dir: Path) -> int:
    """Check every manifest entry against the file on disk. Returns pages checked.

    The corpus is vendored (D-009), so the manifest is how a reader knows which
    upstream commit the committed markdown came from. A page edited after the
    manifest was written breaks that link silently: the index would hold text no
    recorded commit produced, and a citation would point at a page that never said
    it. Ingestion refuses rather than indexing content it cannot account for.

    A corpus that ships no manifest is checked as far as it can be -- not at all --
    and ingested; the fixture corpora used in tests are the reason that is allowed.
    """
    entries = read_manifest(corpus_dir)
    if not entries:
        logger.warning(
            "Corpus has no manifest; skipping the content check",
            corpus_dir=str(corpus_dir),
        )
        return 0

    missing: list[str] = []
    changed: list[str] = []
    for entry in entries:
        relative = str(entry.get("path", ""))
        expected = str(entry.get("sha256", ""))
        if not relative or not expected:
            raise CorpusError(
                f"{corpus_dir / MANIFEST_NAME}: an entry has no path or sha256"
            )
        path = corpus_dir / relative
        if not path.is_file():
            missing.append(relative)
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            changed.append(relative)

    if missing or changed:
        raise CorpusError(
            f"{corpus_dir}: corpus does not match its manifest "
            f"(missing: {sorted(missing)}; content changed: {sorted(changed)}). "
            "Regenerate the manifest if the change is intended."
        )
    return len(entries)
