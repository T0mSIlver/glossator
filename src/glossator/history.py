"""Deterministic history operations over stored documentation snapshots."""

from __future__ import annotations

import difflib
import hashlib
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from glossator.answer.citations import _searchable, fragment_link
from glossator.corpus.snapshots import (
    DEFAULT_MANIFEST,
    SnapshotRecord,
    read_snapshot_manifest,
)
from glossator.ingest.pages import CorpusPage, iter_page_paths, load_page
from glossator.ingest.sections import parse_sections
from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.engine import Hit, SearchEngine

DIFF_MAX_CHARS = 6000
QUESTION_TEXT_MAX_CHARS = 2400
SITE_ORIGIN = "https://docs.mistral.ai"


@dataclass(frozen=True, slots=True)
class PhraseOccurrence:
    snapshot: str
    page: str
    fragment_url: str


@dataclass(frozen=True, slots=True)
class SectionState:
    snapshot: str
    state: str
    page: str | None
    anchor: str | None
    content_sha256: str | None
    diff: str | None = None
    diff_truncated: bool = False


@dataclass(frozen=True, slots=True)
class QuestionState:
    snapshot: str
    state: str
    page: str | None
    anchor: str | None
    content_sha256: str | None
    text: str | None
    text_truncated: bool = False


def available_snapshots(manifest_path: Path = DEFAULT_MANIFEST) -> list[SnapshotRecord]:
    return [row for row in read_snapshot_manifest(manifest_path) if row.status == "built"]


def _pages(snapshot: SnapshotRecord) -> list[CorpusPage]:
    corpus_dir = Path(snapshot.corpus_dir).expanduser()
    return [load_page(path) for path in iter_page_paths(corpus_dir)]


def _find(text: str, phrase: str) -> tuple[int, int] | None:
    haystack, positions = _searchable(text)
    needle, _ = _searchable(phrase)
    if not needle:
        return None
    found = haystack.find(needle)
    if found < 0:
        return None
    return positions[found], positions[found + len(needle) - 1] + 1


def phrase_history(text: str, manifest_path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    if not text.strip():
        raise ValueError("text must contain a non-whitespace phrase")
    occurrences: list[PhraseOccurrence] = []
    for snapshot in available_snapshots(manifest_path):
        for page in _pages(snapshot):
            match = _find(page.body, text)
            if match is None:
                continue
            quote = page.body[match[0] : match[1]]
            occurrences.append(
                PhraseOccurrence(
                    snapshot=snapshot.date,
                    page=page.url,
                    fragment_url=fragment_link(page.url, None, quote),
                )
            )
            break
    return {
        "form": "text",
        "text": text,
        "first": asdict(occurrences[0]) if occurrences else None,
        "last": asdict(occurrences[-1]) if occurrences else None,
        "snapshots_found": len(occurrences),
    }


def _target(value: str) -> tuple[str, str | None]:
    raw = value.strip()
    if not raw:
        raise ValueError("section must contain a documentation URL or page path")
    parsed = urlsplit(raw if "://" in raw else f"{SITE_ORIGIN}/{raw.lstrip('/')}")
    if parsed.netloc and parsed.netloc != "docs.mistral.ai":
        raise ValueError("section must be on docs.mistral.ai")
    return f"{SITE_ORIGIN}{parsed.path.rstrip('/') or '/'}", parsed.fragment or None


def _selected(page: CorpusPage, anchor: str | None) -> tuple[str, str | None] | None:
    if anchor is None:
        return page.body, None
    sections = parse_sections(page.body, page_title=page.title)
    section = next((item for item in sections if item.own_anchor == anchor), None)
    return (section.body, section.own_anchor) if section is not None else None


def _locate(
    pages: list[CorpusPage], url: str, anchor: str | None, previous_text: str | None
) -> tuple[CorpusPage, str, str | None] | None:
    page = next((item for item in pages if item.url.rstrip("/") == url.rstrip("/")), None)
    if page is not None:
        selected = _selected(page, anchor)
        if selected is not None:
            return page, selected[0], selected[1]
    if previous_text:
        for candidate in pages:
            match = _find(candidate.body, previous_text)
            if match is not None:
                return candidate, candidate.body[match[0] : match[1]], None
    return None


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _diff(before: str, after: str, limit: int) -> tuple[str, bool]:
    rendered = "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile="previous",
            tofile="current",
        )
    )
    if len(rendered) <= limit:
        return rendered, False
    return rendered[:limit] + "\n...[diff truncated]", True


def section_history(
    section: str,
    manifest_path: Path = DEFAULT_MANIFEST,
    *,
    diff_max_chars: int = DIFF_MAX_CHARS,
) -> dict[str, Any]:
    url, anchor = _target(section)
    states: list[SectionState] = []
    previous_text: str | None = None
    previous_digest: str | None = None
    previous_page: str | None = None
    for snapshot in available_snapshots(manifest_path):
        located = _locate(_pages(snapshot), url, anchor, previous_text)
        if located is None:
            states.append(SectionState(snapshot.date, "absent", None, None, None))
            continue
        page, text, found_anchor = located
        digest = _digest(text)
        moved = page.url.rstrip("/") != url.rstrip("/")
        if previous_digest is None:
            state = "moved" if moved else "same"
        elif digest == previous_digest:
            state = "moved" if page.url != previous_page else "same"
        else:
            state = "changed"
        rendered_diff = None
        truncated = False
        if state == "changed" and previous_text is not None:
            rendered_diff, truncated = _diff(previous_text, text, diff_max_chars)
        states.append(
            SectionState(
                snapshot=snapshot.date,
                state=state,
                page=page.url,
                anchor=found_anchor,
                content_sha256=digest,
                diff=rendered_diff,
                diff_truncated=truncated,
            )
        )
        previous_text = text
        previous_digest = digest
        previous_page = page.url
    return {"form": "section", "section": section, "states": [asdict(row) for row in states]}


def _question_state(hit: Hit | None, previous: Hit | None, snapshot: str) -> QuestionState:
    if hit is None:
        return QuestionState(snapshot, "absent", None, None, None, None)
    digest = hit.content_sha256 or _digest(hit.content)
    previous_digest = (
        previous.content_sha256 or _digest(previous.content) if previous is not None else None
    )
    if previous is None:
        state = "same"
    elif digest == previous_digest:
        state = "moved" if hit.citation_url != previous.citation_url else "same"
    else:
        state = "changed"
    truncated = len(hit.content) > QUESTION_TEXT_MAX_CHARS
    text = hit.content[:QUESTION_TEXT_MAX_CHARS] + ("...[text truncated]" if truncated else "")
    return QuestionState(
        snapshot,
        state,
        hit.url,
        hit.anchor,
        digest,
        text,
        truncated,
    )


async def question_history(
    question: str,
    manifest_path: Path = DEFAULT_MANIFEST,
    *,
    engine_factory: Callable[[RetrievalConfig], Any] = SearchEngine,
) -> dict[str, Any]:
    if not question.strip():
        raise ValueError("question must contain non-whitespace text")
    states: list[QuestionState] = []
    previous: Hit | None = None
    for snapshot in available_snapshots(manifest_path):
        config = RetrievalConfig.shipped(variant="snap1024", snapshot=snapshot.date, top_k=1)
        hits = await engine_factory(config).search(question, top_k=1)
        hit = hits[0] if hits else None
        states.append(_question_state(hit, previous, snapshot.date))
        previous = hit
    return {
        "form": "question",
        "question": question,
        "states": [asdict(row) for row in states],
    }
