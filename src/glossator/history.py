"""Deterministic history operations over stored documentation snapshots."""

from __future__ import annotations

import difflib
import hashlib
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any

from glossator.answer.citations import find_span, fragment_link
from glossator.changelog import comparable_body, read_changelog, shared_path_tail
from glossator.citing import section_keys
from glossator.corpus.snapshots import (
    DEFAULT_MANIFEST,
    SnapshotRecord,
    read_snapshot_manifest,
    snapshot_corpus_dir,
)
from glossator.corpus.snapshots import (
    SnapshotUnavailableError as SnapshotUnavailableError,
)
from glossator.doc_paths import SITE, split_docs_location, under_prefix
from glossator.ingest.pages import CorpusPage, iter_page_paths, load_page
from glossator.ingest.sections import parse_sections

DIFF_MAX_CHARS = 6000


class UnknownPageError(ValueError):
    """No stored snapshot contains the requested page."""


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


def available_snapshots(manifest_path: Path = DEFAULT_MANIFEST) -> list[SnapshotRecord]:
    """The built snapshots, oldest date first.

    Every form here reads its answer out of the order: "first appearance" is the
    head of the list, "last" is the tail, and a section's diff is against the
    date before it. The manifest happens to be written chronologically, but a
    manifest that is not would silently invert all three.
    """
    built = [row for row in read_snapshot_manifest(manifest_path) if row.status == "built"]
    return sorted(built, key=lambda row: row.date)


def snapshot_availability(manifest_path: Path = DEFAULT_MANIFEST) -> dict[str, int]:
    """Count snapshot corpora that the history service can read."""
    try:
        snapshots = read_snapshot_manifest(manifest_path)
    except (OSError, ValueError):
        return {"readable": 0, "total": 0}
    readable = 0
    for snapshot in snapshots:
        if snapshot.status != "built":
            continue
        try:
            snapshot_corpus_dir(snapshot)
        except SnapshotUnavailableError:
            continue
        readable += 1
    return {"readable": readable, "total": len(snapshots)}


def _pages(snapshot: SnapshotRecord) -> list[CorpusPage]:
    corpus_dir = snapshot_corpus_dir(snapshot)
    try:
        return [load_page(path) for path in iter_page_paths(corpus_dir)]
    except OSError as exc:
        raise SnapshotUnavailableError(
            f"snapshot {snapshot.date} is unreadable at {corpus_dir}: {exc}"
        ) from exc


def phrase_history(
    text: str,
    manifest_path: Path = DEFAULT_MANIFEST,
    *,
    page_url: str | None = None,
    under: str | None = None,
) -> dict[str, Any]:
    """Where a phrase first and last appears, site-wide or on one page or path.

    The scope is what a model reaches for when it asks "this phrase, on this
    page" (D-051); a page that no snapshot holds is refused, as the page form
    refuses it.
    """
    if not text.strip():
        raise ValueError("text must contain a non-whitespace phrase")
    if page_url is not None and under is not None:
        raise ValueError("text takes page_url or under, not both")
    scope_url = _target(page_url, None)[0] if page_url is not None else None
    prefix = under_prefix(under) if under is not None else None
    occurrences: list[PhraseOccurrence] = []
    snapshots = available_snapshots(manifest_path)
    scoped_pages = 0
    for snapshot in snapshots:
        for page in _pages(snapshot):
            here = page.url.rstrip("/")
            if scope_url is not None and here != scope_url.rstrip("/"):
                continue
            if prefix is not None and not is_under(here, prefix):
                continue
            scoped_pages += 1
            match = find_span(page.body, text)
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
    if scope_url is not None and scoped_pages == 0:
        raise UnknownPageError(scope_url)
    if prefix is not None and scoped_pages == 0:
        raise ValueError(f'no stored page exists under "{prefix}"')
    # The stored date before the first appearance, so the render can say the
    # phrase was absent then: an appearance is a bound, not a day (D-048).
    dates = [snapshot.date for snapshot in snapshots]
    absent_before = None
    if occurrences and dates.index(occurrences[0].snapshot) > 0:
        absent_before = dates[dates.index(occurrences[0].snapshot) - 1]
    return {
        "form": "text",
        "text": text,
        "page_url": scope_url,
        "under": prefix,
        "absent_before": absent_before,
        "first": asdict(occurrences[0]) if occurrences else None,
        "last": asdict(occurrences[-1]) if occurrences else None,
        "snapshots_found": len(occurrences),
        "snapshots_total": len(snapshots),
    }


def _target(page_url: str, section: str | None) -> tuple[str, str | None]:
    raw = page_url.strip()
    if not raw:
        raise ValueError("page_url must contain a documentation URL or page path")
    path, fragment = split_docs_location(raw, "page_url")
    key = section.strip() if section is not None else fragment
    if section is not None and not key:
        raise ValueError("section must contain a key")
    return f"{SITE}{path or '/'}", key or None


def _selected(page: CorpusPage, key: str | None) -> tuple[str, str | None] | None:
    if key is None:
        return page.body, None
    sections = parse_sections(page.body, page_title=page.title)
    keys = section_keys(sections)
    for parsed, named in zip(sections, keys, strict=True):
        if named.key == key:
            return parsed.body, named.key
    return None


def _locate(
    pages: list[CorpusPage], url: str, key: str | None, previous_text: str | None
) -> tuple[CorpusPage, str, str | None] | None:
    page = next((item for item in pages if item.url.rstrip("/") == url.rstrip("/")), None)
    if page is not None:
        selected = _selected(page, key)
        if selected is not None:
            return page, selected[0], selected[1]
    if previous_text:
        # Bodies compare with internal links reduced to their last path segment,
        # as the changelog builder compares them: a folder rename rewrites the
        # links inside a page, and the page is still the same page (D-048a).
        wanted = comparable_body(previous_text)
        matches: list[tuple[CorpusPage, str, str | None]] = []
        structural: list[tuple[CorpusPage, str, str | None]] = []
        wanted_shape = _shape(previous_text)
        for candidate in pages:
            if key is None:
                if comparable_body(candidate.body) == wanted:
                    matches.append((candidate, candidate.body, None))
                elif (
                    shared_path_tail(url, candidate.url) >= 1
                    and _shape(candidate.body) == wanted_shape
                ):
                    # The same page under another folder with its prose edited:
                    # same last path segment, same headings in the same order.
                    structural.append((candidate, candidate.body, None))
                continue
            sections = parse_sections(candidate.body, page_title=candidate.title)
            keys = section_keys(sections)
            for parsed, named in zip(sections, keys, strict=True):
                if find_span(comparable_body(parsed.body), wanted) is not None:
                    matches.append((candidate, parsed.body, named.key))
        matches = matches or structural
        if matches:
            return max(matches, key=lambda match: shared_path_tail(url, match[0].url))
    return None


def _shape(body: str) -> tuple[str, ...]:
    """A page's headings in order, the identity a rename keeps when the prose moves on."""
    sections = parse_sections(body, page_title="")
    return tuple(section.heading_path[-1] if section.heading_path else "" for section in sections)


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
    page_url: str,
    section: str | None = None,
    manifest_path: Path = DEFAULT_MANIFEST,
    *,
    diff_max_chars: int = DIFF_MAX_CHARS,
) -> dict[str, Any]:
    url, key = _target(page_url, section)
    snapshots = available_snapshots(manifest_path)
    snapshot_pages = [(snapshot, _pages(snapshot)) for snapshot in snapshots]
    pages_at_url = [
        page
        for _snapshot, pages in snapshot_pages
        for page in pages
        if page.url.rstrip("/") == url.rstrip("/")
    ]
    if not pages_at_url:
        raise UnknownPageError(url)
    if key is not None and not any(_selected(page, key) is not None for page in pages_at_url):
        raise ValueError(
            f'page {url} has no section "{key}" in any stored snapshot; '
            f"read_page({url}) prints the keys"
        )

    located_states: list[tuple[CorpusPage, str, str | None] | None] = []
    previous_text: str | None = None
    for _snapshot, pages in snapshot_pages:
        located = _locate(pages, url, key, previous_text)
        located_states.append(located)
        if located is not None:
            previous_text = located[1]

    first_present = next((i for i, item in enumerate(located_states) if item is not None), None)
    if first_present is not None and first_present > 0:
        first_text = located_states[first_present][1]  # type: ignore[index]
        for index in range(first_present - 1, -1, -1):
            located_states[index] = _locate(snapshot_pages[index][1], url, key, first_text)

    states: list[SectionState] = []
    previous: tuple[CorpusPage, str, str | None] | None = None
    for (snapshot, _pages_for_date), located in zip(snapshot_pages, located_states, strict=True):
        if located is None:
            states.append(SectionState(snapshot.date, "absent", None, None, None))
            previous = None
            continue
        page, text, found_key = located
        digest = _digest(text)
        here = page.url.rstrip("/")
        if previous is None:
            state = "moved" if here != url.rstrip("/") else "same"
        else:
            previous_location = (previous[0].url.rstrip("/"), previous[2])
            if (here, found_key) != previous_location:
                state = "moved"
            elif digest != _digest(previous[1]):
                state = "changed"
            else:
                state = "same"
        rendered_diff = None
        truncated = False
        if state == "changed" and previous is not None:
            rendered_diff, truncated = _diff(previous[1], text, diff_max_chars)
        states.append(
            SectionState(
                snapshot=snapshot.date,
                state=state,
                page=page.url,
                anchor=found_key,
                content_sha256=digest,
                diff=rendered_diff,
                diff_truncated=truncated,
            )
        )
        previous = located
    return {
        "form": "section",
        "page_url": url,
        "section": key,
        "states": [asdict(row) for row in states],
    }


@lru_cache(maxsize=4)
def _stored_page_urls(corpora: tuple[tuple[str, str], ...]) -> frozenset[str]:
    """Every page URL any stored snapshot holds, read once per process.

    Keyed on the corpus directories and their manifest digests, so a refreshed
    snapshot set invalidates it and a call never re-reads eight corpora to
    validate one prefix.
    """
    urls: set[str] = set()
    for corpus_dir, _digest in corpora:
        for path in iter_page_paths(Path(corpus_dir)):
            urls.add(load_page(path).url.rstrip("/"))
    return frozenset(urls)


def is_under(page: str, prefix: str) -> bool:
    return prefix == SITE or page == prefix or page.startswith(prefix + "/")


def _nearest_ancestor(prefix: str, pages: frozenset[str]) -> str | None:
    parent = prefix
    while parent.startswith(SITE + "/"):
        parent = parent.rsplit("/", 1)[0]
        if parent == SITE:
            return None
        if any(is_under(page, parent) for page in pages):
            return parent
    return None


def history_under(
    under: str,
    since: str | None = None,
    manifest_path: Path = DEFAULT_MANIFEST,
    changelog_dir: Path | None = None,
) -> dict[str, Any]:
    prefix = under_prefix(under)
    snapshots = available_snapshots(manifest_path)
    if not snapshots:
        raise ValueError("the snapshot manifest has no built snapshots")
    pages = _stored_page_urls(
        tuple((str(snapshot_corpus_dir(row)), row.content_digest or "") for row in snapshots)
    )
    if not any(is_under(page, prefix) for page in pages):
        ancestor = _nearest_ancestor(prefix, pages)
        hint = f' nearest path with pages: "{ancestor}".' if ancestor else ""
        raise ValueError(f'no stored page exists under "{prefix}".{hint}')
    try:
        requested = date.fromisoformat(since) if since else date.fromisoformat(snapshots[0].date)
    except ValueError as exc:
        raise ValueError("since must be a date in YYYY-MM-DD form") from exc
    snapped = next(
        (row.date for row in snapshots if date.fromisoformat(row.date) >= requested), None
    )
    if snapped is None:
        raise ValueError(f"since is after the last stored date {snapshots[-1].date}")
    intervals = []
    for interval in read_changelog(manifest_path, changelog_dir):
        if interval["before"] < snapped:
            continue
        rows = [
            row
            for row in interval["rows"]
            if is_under(row["page"], prefix)
            or (row.get("old_page") and is_under(row["old_page"], prefix))
        ]
        intervals.append(
            {
                "before": interval["before"],
                "after": interval["after"],
                "rows": _two_levels(rows, prefix),
            }
        )
    return {
        "form": "under",
        "under": prefix,
        "since": snapped,
        "intervals": intervals,
        "changes": sum(len(interval["rows"]) for interval in intervals),
    }


_STATES = ("added", "removed", "changed", "moved")


def _two_levels(rows: list[dict[str, Any]], prefix: str) -> list[dict[str, Any]]:
    """Sections for the prefix page itself, one row per page for everything
    beneath it. A folder-wide call then reads as a list of pages, and the page
    form or ``under`` on one page gives the sections (D-051)."""
    own: list[dict[str, Any]] = []
    beneath: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        pages = {row["page"].rstrip("/"), (row.get("old_page") or "").rstrip("/")}
        if prefix in pages:
            own.append({**row, "level": "section"})
        else:
            beneath.setdefault(row["page"].rstrip("/"), []).append(row)
    collapsed: list[dict[str, Any]] = []
    for _page, page_rows in sorted(beneath.items()):
        whole = next((row for row in page_rows if row.get("sections") is not None), None)
        if whole is not None and len(page_rows) == 1:
            collapsed.append(
                {
                    "level": "page",
                    "state": whole["state"],
                    "page": whole["page"],
                    "sections": whole["sections"],
                    "old_page": whole.get("old_page"),
                    "cite": whole["page"],
                }
            )
            continue
        counts = Counter(row["state"] for row in page_rows)
        collapsed.append(
            {
                "level": "page",
                "state": "changed",
                "page": page_rows[0]["page"],
                "counts": {state: counts[state] for state in _STATES if counts[state]},
                "old_page": None,
                "cite": page_rows[0]["page"],
            }
        )
    return own + collapsed
