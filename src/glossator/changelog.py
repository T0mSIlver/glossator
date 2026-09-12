"""Build and read section changes between stored documentation snapshots."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from glossator.answer.citations import find_span, normalize
from glossator.citing import citation_link, page_search_text, section_keys
from glossator.corpus.snapshots import DEFAULT_MANIFEST, SnapshotRecord, read_snapshot_manifest
from glossator.ingest.pages import CorpusPage, iter_page_paths, load_page
from glossator.ingest.sections import parse_sections

DEFAULT_CHANGELOG_DIR = Path("eval/snapshots/changelog")
_HEADING_ANCHOR = re.compile(r"(?m)(^#{1,6} .+?)\s+\{#[^}]+\}(\s*$)")
_STUDIO_API_PATH = re.compile(r"/studio-api(?=/|\b)")


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


def _comparable_body(body: str) -> str:
    without_anchor_markup = _HEADING_ANCHOR.sub(r"\1\2", body)
    return normalize(_STUDIO_API_PATH.sub("/studio", without_anchor_markup))


def _contains_body(haystack: str, needle: str) -> bool:
    return find_span(_comparable_body(haystack), _comparable_body(needle)) is not None


def _canonical_page(url: str) -> str:
    return _STUDIO_API_PATH.sub("/studio", url.rstrip("/"))


def _site_rename(old: _SectionRecord, new: _SectionRecord) -> bool:
    return old.page.rstrip("/") != new.page.rstrip("/") and _canonical_page(
        old.page
    ) == _canonical_page(new.page)


def _built(path: Path) -> list[SnapshotRecord]:
    return sorted(
        (row for row in read_snapshot_manifest(path) if row.status == "built"),
        key=lambda row: row.date,
    )


def _records(snapshot: SnapshotRecord) -> tuple[list[_SectionRecord], list[CorpusPage]]:
    pages = [load_page(path) for path in iter_page_paths(Path(snapshot.corpus_dir).expanduser())]
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
                    normalized=_comparable_body(section.body),
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

    by_renamed_location: dict[tuple[str, str], list[int]] = defaultdict(list)
    by_renamed_heading: dict[tuple[str, tuple[str, ...]], list[int]] = defaultdict(list)
    for new_index in sorted(available):
        new = after[new_index]
        by_renamed_location[(_canonical_page(new.page), new.key)].append(new_index)
        by_renamed_heading[(_canonical_page(new.page), new.heading_path)].append(new_index)
    for old_index, old in enumerate(before):
        if old_index in matched:
            continue
        candidates = by_renamed_location.get((_canonical_page(old.page), old.key), [])
        if not candidates:
            candidates = by_renamed_heading.get((_canonical_page(old.page), old.heading_path), [])
        candidates = [index for index in candidates if index in available]
        if candidates and _site_rename(old, after[candidates[0]]):
            new_index = candidates[0]
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
            same_heading = next(
                (index for index in candidates if after[index].heading_path == old.heading_path),
                candidates[0],
            )
            candidates.remove(same_heading)
            matched[old_index] = same_heading
            available.remove(same_heading)

    page_text = [(page, _comparable_body(page.body)) for page in after_pages]
    for old_index, old in enumerate(before):
        if old_index in matched or not old.normalized:
            continue
        destination_page = next(
            (page for page, body in page_text if old.normalized in body),
            None,
        )
        if destination_page is None:
            continue
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
        source_page = next(
            (
                page
                for page, body in before_page_text.items()
                if new.normalized in _comparable_body(body)
            ),
            None,
        )
        if source_page is None:
            continue
        for old_index in unmatched_old:
            old = before[old_index]
            if old.page == source_page and _contains_body(old.body, new.body):
                matched[old_index] = new_index
                unmatched_old.remove(old_index)
                break

    remaining_by_page: dict[str, list[int]] = defaultdict(list)
    for new_index in sorted(available):
        remaining_by_page[_canonical_page(after[new_index].page)].append(new_index)
    old_by_page: dict[str, list[int]] = defaultdict(list)
    for old_index in range(len(before)):
        if old_index not in matched:
            old_by_page[_canonical_page(before[old_index].page)].append(old_index)
    for page, old_indexes in old_by_page.items():
        new_indexes = remaining_by_page.get(page, [])
        if len(old_indexes) != len(new_indexes):
            continue
        if not old_indexes or not _site_rename(before[old_indexes[0]], after[new_indexes[0]]):
            continue
        for old_index, new_index in zip(old_indexes, new_indexes, strict=True):
            matched[old_index] = new_index
            available.remove(new_index)
    return matched


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
        state = "moved" if same_body or _site_rename(old, new) else "changed"
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
