"""Build and read section changes between stored documentation snapshots."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from glossator.answer.citations import find_span, normalize
from glossator.citing import citation_link, page_search_text, section_keys
from glossator.corpus.snapshots import (
    DEFAULT_MANIFEST,
    SnapshotRecord,
    SnapshotUnavailableError,
    read_snapshot_manifest,
    snapshot_corpus_dir,
)
from glossator.ingest.pages import CorpusPage, iter_page_paths, load_page
from glossator.ingest.sections import parse_sections

DEFAULT_CHANGELOG_DIR = Path("eval/snapshots/changelog")
SITE_ORIGIN = "https://docs.mistral.ai"
_HEADING_ANCHOR = re.compile(r"(?m)(^#{1,6} .+?)\s+\{#[^}]+\}(\s*$)")
_INTERNAL_LINK = re.compile(
    r"https://docs\.mistral\.ai/(?P<path>[^#\s)>\]}'\"]+)"
    r"(?:#(?P<fragment>[^\s)>\]}'\"]+))?"
)


class StaleChangelogError(ValueError):
    """The changelog was built from different snapshot content."""


@dataclass(frozen=True, slots=True)
class Change:
    state: str
    page: str
    key: str | None
    heading_path: list[str]
    cite: str
    old_page: str | None = None
    old_key: str | None = None
    sections: int | None = None


@dataclass(frozen=True, slots=True)
class _SectionRecord:
    page: str
    key: str
    heading_path: tuple[str, ...]
    body: str
    normalized: str
    cite: str

    @property
    def location(self) -> tuple[str, str]:
        return self.page.rstrip("/"), self.key


def comparable_body(body: str) -> str:
    without_anchor_markup = _HEADING_ANCHOR.sub(r"\1\2", body)
    return normalize(_INTERNAL_LINK.sub(_link_tail, without_anchor_markup))


def _link_tail(match: re.Match[str]) -> str:
    path = match.group("path").rstrip("/")
    tail = path.rsplit("/", 1)[-1]
    fragment = match.group("fragment")
    return f"{tail}#{fragment}" if fragment else tail


def _contains_body(haystack: str, needle: str) -> bool:
    return find_span(comparable_body(haystack), comparable_body(needle)) is not None


def _shared_path_tail(left: str, right: str) -> int:
    left_parts = urlsplit(left).path.rstrip("/").split("/")
    right_parts = urlsplit(right).path.rstrip("/").split("/")
    shared = 0
    for left_part, right_part in zip(reversed(left_parts), reversed(right_parts), strict=False):
        if left_part != right_part:
            break
        shared += 1
    return shared


def _best_page_match(reference: str, candidates: list[int], records: list[_SectionRecord]) -> int:
    return max(
        candidates, key=lambda index: (_shared_path_tail(reference, records[index].page), -index)
    )


def _built(path: Path) -> list[SnapshotRecord]:
    return sorted(
        (row for row in read_snapshot_manifest(path) if row.status == "built"),
        key=lambda row: row.date,
    )


def _records(snapshot: SnapshotRecord) -> tuple[list[_SectionRecord], list[CorpusPage]]:
    corpus_dir = snapshot_corpus_dir(snapshot)
    try:
        pages = [load_page(path) for path in iter_page_paths(corpus_dir)]
    except OSError as exc:
        raise SnapshotUnavailableError(
            f"snapshot {snapshot.date} is unreadable at {corpus_dir}: {exc}"
        ) from exc
    records: list[_SectionRecord] = []
    for page in pages:
        sections = parse_sections(page.body, page_title=page.title)
        keys = section_keys(sections)
        haystack = page_search_text(page.body)
        for section, key in zip(sections, keys, strict=True):
            cite = citation_link(
                page.url,
                key.anchor,
                landing=key.anchor_start,
                text_start=section.start_offset,
                text=section.body,
                haystack=haystack,
            )
            records.append(
                _SectionRecord(
                    page=page.url,
                    key=key.key,
                    heading_path=section.heading_path,
                    body=section.body,
                    normalized=comparable_body(section.body),
                    cite=cite,
                )
            )
    return records, pages


def _match_pair(
    before: list[_SectionRecord], after: list[_SectionRecord], after_pages: list[CorpusPage]
) -> dict[int, int]:
    matched: dict[int, int] = {}
    available = set(range(len(after)))

    by_location: dict[tuple[str, str], int] = {
        record.location: index for index, record in enumerate(after)
    }
    for old_index, old in enumerate(before):
        new_index = by_location.get(old.location)
        if new_index in available:
            matched[old_index] = new_index
            available.remove(new_index)

    by_heading: dict[tuple[str, tuple[str, ...]], list[int]] = defaultdict(list)
    for new_index in sorted(available):
        new = after[new_index]
        by_heading[(new.page.rstrip("/"), new.heading_path)].append(new_index)
    for old_index, old in enumerate(before):
        if old_index in matched:
            continue
        candidates = by_heading.get((old.page.rstrip("/"), old.heading_path), [])
        if candidates:
            new_index = candidates.pop(0)
            matched[old_index] = new_index
            available.remove(new_index)

    by_body: dict[str, list[int]] = defaultdict(list)
    for new_index in sorted(available):
        by_body[after[new_index].normalized].append(new_index)
    for old_index, old in enumerate(before):
        if old_index in matched or not old.normalized:
            continue
        candidates = by_body.get(old.normalized, [])
        if candidates:
            new_index = _best_page_match(
                old.page,
                [index for index in candidates if index in available],
                after,
            )
            candidates.remove(new_index)
            matched[old_index] = new_index
            available.remove(new_index)

    page_text = [(page, comparable_body(page.body)) for page in after_pages]
    for old_index, old in enumerate(before):
        if old_index in matched or not old.normalized:
            continue
        destination_pages = [page for page, body in page_text if old.normalized in body]
        if not destination_pages:
            continue
        destination_page = max(
            destination_pages,
            key=lambda page: _shared_path_tail(old.page, page.url),
        )
        for new_index in sorted(available):
            new = after[new_index]
            if new.page == destination_page.url and _contains_body(new.body, old.body):
                matched[old_index] = new_index
                available.remove(new_index)
                break

    before_page_text: dict[str, str] = {}
    for old in before:
        before_page_text.setdefault(old.page, "")
        before_page_text[old.page] += old.body
    unmatched_old = [index for index in range(len(before)) if index not in matched]
    for new_index in sorted(available):
        new = after[new_index]
        if not new.normalized:
            continue
        source_pages = [
            page
            for page, body in before_page_text.items()
            if new.normalized in comparable_body(body)
        ]
        if not source_pages:
            continue
        source_page = max(source_pages, key=lambda page: _shared_path_tail(new.page, page))
        for old_index in unmatched_old:
            old = before[old_index]
            if old.page == source_page and _contains_body(old.body, new.body):
                matched[old_index] = new_index
                unmatched_old.remove(old_index)
                break

    _match_whole_pages(before, after, matched, available)
    return matched


def _match_whole_pages(
    before: list[_SectionRecord],
    after: list[_SectionRecord],
    matched: dict[int, int],
    available: set[int],
) -> None:
    old_pages: dict[str, list[int]] = defaultdict(list)
    new_pages: dict[str, list[int]] = defaultdict(list)
    before_urls = {record.page.rstrip("/") for record in before}
    after_urls = {record.page.rstrip("/") for record in after}
    for old_index, old in enumerate(before):
        if old_index not in matched and old.page.rstrip("/") not in after_urls:
            old_pages[old.page].append(old_index)
    for new_index in sorted(available):
        new = after[new_index]
        if new.page.rstrip("/") not in before_urls:
            new_pages[new.page].append(new_index)
    for old_indexes in old_pages.values():
        old_records = [before[index] for index in old_indexes]
        candidates = [
            indexes
            for indexes in new_pages.values()
            if len(indexes) == len(old_indexes)
            and after[indexes[0]].heading_path[0] == old_records[0].heading_path[0]
            and [after[index].heading_path for index in indexes]
            == [record.heading_path for record in old_records]
        ]
        if not candidates:
            continue
        new_indexes = max(
            candidates,
            key=lambda indexes: _shared_path_tail(old_records[0].page, after[indexes[0]].page),
        )
        new_pages.pop(after[new_indexes[0]].page)
        for old_index, new_index in zip(old_indexes, new_indexes, strict=True):
            matched[old_index] = new_index
            available.remove(new_index)


def build_pair(before_snapshot: SnapshotRecord, after_snapshot: SnapshotRecord) -> list[Change]:
    before, _before_pages = _records(before_snapshot)
    after, after_pages = _records(after_snapshot)
    matched = _match_pair(before, after, after_pages)
    used_after = set(matched.values())
    changes: list[Change] = []
    for old_index, new_index in sorted(matched.items()):
        old = before[old_index]
        new = after[new_index]
        same_body = old.normalized == new.normalized
        same_location = old.location == new.location
        if same_body and same_location:
            continue
        state = "moved" if same_body else "changed"
        changes.append(
            Change(
                state=state,
                page=new.page,
                key=new.key,
                heading_path=list(new.heading_path),
                cite=new.cite,
                old_page=old.page if not same_location else None,
                old_key=old.key if not same_location else None,
            )
        )
    for old_index, old in enumerate(before):
        if old_index not in matched:
            changes.append(Change("removed", old.page, old.key, list(old.heading_path), old.cite))
    for new_index, new in enumerate(after):
        if new_index not in used_after:
            changes.append(Change("added", new.page, new.key, list(new.heading_path), new.cite))
    return _collapse_pages(changes, before, after)


def _collapse_pages(
    changes: list[Change], before: list[_SectionRecord], after: list[_SectionRecord]
) -> list[Change]:
    counts_before = Counter(record.page for record in before)
    counts_after = Counter(record.page for record in after)
    groups: dict[tuple[str, str], list[Change]] = defaultdict(list)
    for change in changes:
        groups[(change.state, change.page)].append(change)
    collapsed: list[Change] = []
    consumed: set[int] = set()
    for (state, page), rows in groups.items():
        total = counts_after[page] if state == "added" else counts_before[page]
        if state not in {"added", "removed"} or len(rows) != total:
            continue
        collapsed.append(
            Change(
                state=state,
                page=page,
                key=None,
                heading_path=[],
                cite=page,
                sections=total,
            )
        )
        consumed.update(id(row) for row in rows)
    moved_groups: dict[tuple[str, str], list[Change]] = defaultdict(list)
    for change in changes:
        if change.state == "moved" and change.old_page is not None:
            moved_groups[(change.old_page, change.page)].append(change)
    for (old_page, page), rows in moved_groups.items():
        if (
            len(rows) != counts_before[old_page]
            or len(rows) != counts_after[page]
            or any(row.key != row.old_key for row in rows)
        ):
            continue
        collapsed.append(
            Change(
                state="moved",
                page=page,
                key=None,
                heading_path=[],
                cite=page,
                old_page=old_page,
                sections=len(rows),
            )
        )
        consumed.update(id(row) for row in rows)
    collapsed.extend(change for change in changes if id(change) not in consumed)
    return sorted(collapsed, key=lambda row: (row.page, row.key or "", row.state))


def build_changelog(
    manifest_path: Path = DEFAULT_MANIFEST, out_dir: Path = DEFAULT_CHANGELOG_DIR
) -> dict[str, Any]:
    snapshots = _built(manifest_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    pairs: list[dict[str, Any]] = []
    for before, after in zip(snapshots, snapshots[1:], strict=False):
        rows = build_pair(before, after)
        name = f"{before.date}..{after.date}.json"
        (out_dir / name).write_text(
            json.dumps([asdict(row) for row in rows], indent=2, sort_keys=True) + "\n"
        )
        pairs.append(
            {
                "before": before.date,
                "after": after.date,
                "file": name,
                "before_content_digest": before.content_digest,
                "after_content_digest": after.content_digest,
                "counts": dict(sorted(Counter(row.state for row in rows).items())),
            }
        )
    index = {"manifest": str(manifest_path), "pairs": pairs}
    (out_dir / "index.json").write_text(json.dumps(index, indent=2, sort_keys=True) + "\n")
    return index


def read_changelog(
    manifest_path: Path = DEFAULT_MANIFEST, changelog_dir: Path | None = None
) -> list[dict[str, Any]]:
    directory = changelog_dir or manifest_path.parent / "changelog"
    index = json.loads((directory / "index.json").read_text())
    snapshots = {row.date: row for row in _built(manifest_path)}
    intervals: list[dict[str, Any]] = []
    for pair in index.get("pairs", []):
        before = snapshots.get(pair["before"])
        after = snapshots.get(pair["after"])
        if (
            before is None
            or after is None
            or before.content_digest != pair.get("before_content_digest")
            or after.content_digest != pair.get("after_content_digest")
        ):
            raise StaleChangelogError(
                f"changelog interval {pair['before']}..{pair['after']} does not match the manifest"
            )
        rows = json.loads((directory / pair["file"]).read_text())
        intervals.append({**pair, "rows": rows})
    return intervals


def under_prefix(under: str) -> str:
    raw = under.strip()
    if not raw:
        raise ValueError("under must contain a documentation path")
    parsed = urlsplit(raw if "://" in raw else f"{SITE_ORIGIN}/{raw.lstrip('/')}")
    if parsed.netloc and parsed.netloc != "docs.mistral.ai":
        raise ValueError("under must be on docs.mistral.ai")
    return f"{SITE_ORIGIN}{parsed.path.rstrip('/') or ''}"


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
    return prefix == SITE_ORIGIN or page == prefix or page.startswith(prefix + "/")


def _nearest_ancestor(prefix: str, pages: frozenset[str]) -> str | None:
    parent = prefix
    while parent.startswith(SITE_ORIGIN + "/"):
        parent = parent.rsplit("/", 1)[0]
        if parent == SITE_ORIGIN:
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
    snapshots = _built(manifest_path)
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


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="glossator.changelog")
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    build.add_argument("--out", type=Path, default=DEFAULT_CHANGELOG_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    index = build_changelog(args.manifest, args.out)
    for pair in index["pairs"]:
        counts = ", ".join(f"{state}={count}" for state, count in pair["counts"].items())
        print(f"{pair['before']}..{pair['after']}: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
