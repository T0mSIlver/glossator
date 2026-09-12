"""Contain what a page read prints: one language tab per sample group, no
duplicate sample, no pasted output beyond its head.

Tool results are most of a session's tokens, and much of what ``read_page``
prints is fenced: the same sample repeated in Python, TypeScript and cURL tabs,
byte-identical V1/V2 migration samples, and pasted outputs and float vectors
tens of thousands of characters long. ``contain`` is a pure transform over the
chunk bodies of one section: state (inside a fence, inside a tab group, which
tab) carries from one chunk to the next, because a label can end one chunk with
its fence opening the next, and a fence above the chunker's atomic ceiling is
split across chunks and is treated as one fence here.
"""

import re
from dataclasses import dataclass

LANGS = ("python", "typescript", "curl")
"""The ``lang`` values read_page accepts; each names the tab of a sample group to print."""

_TAB_OF_LABEL = {"Python": "python", "TypeScript": "typescript", "cURL": "curl", "Bash": "curl"}
"""The docs render a tab as a bold label line; ``Bash`` carries the cURL sample."""
_DISPLAY_OF_TAB = {"python": "Python", "typescript": "TypeScript", "curl": "cURL"}
_VERSION_LABELS = frozenset({"V1", "V2"})
_LABEL = re.compile(r"\*\*(Python|TypeScript|cURL|Bash|V1|V2)\*\*")
_FENCE = re.compile(r" {0,3}(`{3,}|~{3,})(.*)")
_OUTPUT_TAGS = frozenset({"", "json", "jsonl", "text", "txt", "output", "console"})
_FLOATS = re.compile(r"\d+\.\d{3,}")

OUTPUT_MAX_CHARS = 1_500
_OUTPUT_MIN_FLOATS = 20


def contain(blocks: list[str], lang: str, report: dict[str, int] | None = None) -> list[str]:
    """Contain the chunk bodies of one section, in reading order.

    Returns one output string per input chunk. ``report``, when given,
    accumulates the characters each rule saved under ``tabs``, ``v1v2``,
    ``duplicates`` and ``outputs``.
    """
    if lang not in LANGS:
        raise ValueError(f"lang must be one of {', '.join(LANGS)}, not {lang!r}")
    chunks = [block.split("\n") for block in blocks]
    table = [(index, text) for index, lines in enumerate(chunks) for text in lines]
    texts = [text for _, text in table]
    fences = _scan_fences(texts)
    groups = _scan_groups(texts, fences)
    out: list[list[str]] = [[] for _ in chunks]
    seen: set[str] = set()

    def emit(line: int, text: str | None = None) -> None:
        out[table[line][0]].append(texts[line] if text is None else text)

    def charge(rule: str, saved: int) -> None:
        if report is not None and saved > 0:
            report[rule] = report.get(rule, 0) + saved

    def emit_fence(fence: _Fence) -> None:
        body = _normalized(fence.body)
        duplicate = bool(body) and body in seen
        if body:
            seen.add(body)
        if duplicate:
            note = "(same sample as above)"
            emit(fence.start, note)
            charge("duplicates", fence.chars(texts) - (len(note) + 1))
            return
        if _is_output(fence) and len(fence.body) > OUTPUT_MAX_CHARS:
            kept, more = _head_lines(fence.body_lines)
            note = _cut_note(more)
            head = texts[fence.start]
            spent = len(head) + 1 + sum(len(line) + 1 for line in kept) + len(fence.marker) + 1
            # The head, the closing fence and the cut line all print in the chunk
            # where the fence opened; a fence the chunker split across chunks is
            # one fence, and its continuation chunks print nothing for it.
            out[table[fence.start][0]].extend([head, *kept, fence.marker, note])
            charge("outputs", fence.chars(texts) - (spent + len(note) + 1))
            return
        for line in range(fence.start, fence.end + 1):
            emit(line)

    def emit_group(group: _Group) -> None:
        tabs: list[str] = []
        for item in group.items:
            if item.tab not in tabs:
                tabs.append(item.tab)
        kept_tab = lang if lang in tabs else tabs[0]
        kept = [item for item in group.items if item.tab == kept_tab]
        v1 = next((i for i in kept if i.version == "V1" and i.fence is not None), None)
        v2 = next((i for i in kept if i.version == "V2" and i.fence is not None), None)
        v1_fence = v1.fence if v1 is not None else None
        v2_fence = v2.fence if v2 is not None else None
        identical = (
            kept_tab == "python"
            and v1_fence is not None
            and v2_fence is not None
            and _normalized(v1_fence.body) == _normalized(v2_fence.body)
        )
        printed: list[_Item] = []
        bodies: set[str] = set()
        for item in kept:
            if identical and item is v1:
                continue
            if item.fence is not None:
                # The chunker's overlap can repeat a tab whole at the head of the
                # next chunk; a repeat within one tab prints once.
                body = _normalized(item.fence.body)
                if body and body in bodies:
                    continue
                if body:
                    bodies.add(body)
            printed.append(item)
        for item in group.items:
            if item.fence is not None and _normalized(item.fence.body):
                seen.add(_normalized(item.fence.body))
        dropped = [tab for tab in tabs if tab != kept_tab]
        keep: set[int] = set()
        for item in printed:
            if item.label_line is not None:
                keep.add(item.label_line)
            if item.fence is not None:
                keep.update(range(item.fence.start, item.fence.end + 1))
        solid = sorted(line for line in keep if texts[line].strip())
        # Blanks that separate kept lines stay verbatim; a run of blanks around
        # dropped lines collapses to the one separator the kept lines need.
        spacer_after: set[int] = set()
        for left, right in zip(solid, solid[1:], strict=False):
            gap = range(left + 1, right)
            has_dropped = any(texts[line].strip() and line not in keep for line in gap)
            if not has_dropped:
                keep.update(line for line in gap if not texts[line].strip())
                continue
            first_blank = next((line for line in gap if not texts[line].strip()), None)
            if first_blank is not None:
                keep.add(first_blank)
            else:
                spacer_after.add(left)
        last = solid[-1]
        before = sum(len(texts[line]) + 1 for line in range(group.start, group.end + 1))
        after = 0
        for line in range(group.start, group.end + 1):
            if line not in keep:
                continue
            emit(line)
            after += len(texts[line]) + 1
            if line in spacer_after:
                emit(line, "")
                after += 1
            if identical and v2_fence is not None and line == v2_fence.end:
                note = "(V1 identical)"
                emit(line, "")
                emit(line, note)
                after += len(note) + 2
            if dropped and line == last:
                note = _omission_line(dropped)
                emit(line, "")
                emit(line, note)
                after += len(note) + 2
        saved_v1v2 = 0
        if identical and v1_fence is not None and v1 is not None and v1.label_line is not None:
            saved_v1v2 = sum(
                len(texts[line]) + 1 for line in range(v1.label_line, v1_fence.end + 1)
            )
        charge("tabs", before - after - saved_v1v2)
        charge("v1v2", saved_v1v2)

    line = 0
    while line < len(texts):
        if line in groups:
            emit_group(groups[line])
            line = groups[line].end + 1
        elif line in fences:
            emit_fence(fences[line])
            line = fences[line].end + 1
        else:
            emit(line)
            line += 1
    return ["\n".join(lines) for lines in out]


@dataclass(frozen=True, slots=True)
class _Fence:
    """A fenced block over the flattened lines of a section's chunks."""

    start: int
    end: int
    """The closing fence line, or the last line of the section when never closed."""
    marker: str
    tag: str
    body_lines: tuple[str, ...]

    @property
    def body(self) -> str:
        return "\n".join(self.body_lines)

    def chars(self, texts: list[str]) -> int:
        return sum(len(texts[line]) + 1 for line in range(self.start, self.end + 1))


@dataclass(frozen=True, slots=True)
class _Item:
    """One label with its fence inside a tab group."""

    label_line: int | None
    tab: str
    version: str | None
    fence: _Fence | None


@dataclass(frozen=True, slots=True)
class _Group:
    """A run of tab labels and fences, from the opening label to the last line
    that is a blank, a label of the vocabulary or a fence."""

    start: int
    end: int
    items: tuple[_Item, ...]


def _scan_fences(texts: list[str]) -> dict[int, _Fence]:
    """Fences by the line they open at, spanning chunk boundaries whole."""
    fences: dict[int, _Fence] = {}
    line = 0
    while line < len(texts):
        opening = _FENCE.fullmatch(texts[line])
        if opening is None:
            line += 1
            continue
        marker = opening.group(1)
        body: list[str] = []
        close = line + 1
        while close < len(texts):
            candidate = _FENCE.fullmatch(texts[close])
            if (
                candidate is not None
                and candidate.group(1)[0] == marker[0]
                and len(candidate.group(1)) >= len(marker)
                and not candidate.group(2).strip()
            ):
                break
            body.append(texts[close])
            close += 1
        end = min(close, len(texts) - 1)
        fences[line] = _Fence(
            start=line,
            end=end,
            marker=marker,
            tag=opening.group(2).strip().lower(),
            body_lines=tuple(body),
        )
        line = close + 1
    return fences


def _label_of(text: str) -> str | None:
    matched = _LABEL.fullmatch(text.strip())
    return matched.group(1) if matched else None


def _next_solid(texts: list[str], after: int) -> int | None:
    line = after + 1
    while line < len(texts):
        if texts[line].strip():
            return line
        line += 1
    return None


def _opens_group(texts: list[str], fences: dict[int, _Fence], at: int) -> bool:
    """A tab label starts a group when a fence follows it across blank lines,
    directly or under a nested V1/V2 label."""
    following = _next_solid(texts, at)
    if following is None:
        return False
    if following in fences:
        return True
    if _label_of(texts[following]) in _VERSION_LABELS:
        nested = _next_solid(texts, following)
        return nested is not None and nested in fences
    return False


def _take_group(texts: list[str], fences: dict[int, _Fence], start: int) -> _Group:
    items: list[_Item] = []
    tab = _TAB_OF_LABEL[_label_of(texts[start]) or "Python"]
    version: str | None = None
    label_line: int | None = start
    pending: _Item | None = _Item(label_line=start, tab=tab, version=None, fence=None)
    last = start
    line = start + 1
    while line < len(texts):
        if not texts[line].strip():
            line += 1
            continue
        if line in fences:
            items.append(_Item(label_line=label_line, tab=tab, version=version, fence=fences[line]))
            pending = None
            label_line = None
            version = None
            last = fences[line].end
            line = last + 1
            continue
        name = _label_of(texts[line])
        if name is None:
            break
        if pending is not None:
            items.append(pending)
        if name in _TAB_OF_LABEL:
            tab = _TAB_OF_LABEL[name]
            version = None
        else:
            version = name
        label_line = line
        pending = _Item(label_line=line, tab=tab, version=version, fence=None)
        last = line
        line += 1
    if pending is not None:
        items.append(pending)
    return _Group(start=start, end=last, items=tuple(items))


def _scan_groups(texts: list[str], fences: dict[int, _Fence]) -> dict[int, _Group]:
    groups: dict[int, _Group] = {}
    line = 0
    while line < len(texts):
        if line in fences:
            line = fences[line].end + 1
            continue
        if _label_of(texts[line]) in _TAB_OF_LABEL and _opens_group(texts, fences, line):
            group = _take_group(texts, fences, line)
            groups[line] = group
            line = group.end + 1
            continue
        line += 1
    return groups


def _normalized(body: str) -> str:
    return " ".join(body.split())


def _is_output(fence: _Fence) -> bool:
    if fence.tag in _OUTPUT_TAGS:
        return True
    if len(_FLOATS.findall(fence.body)) >= _OUTPUT_MIN_FLOATS:
        return True
    return any(len(line) > OUTPUT_MAX_CHARS for line in fence.body_lines)


def _head_lines(body_lines: tuple[str, ...]) -> tuple[list[str], int]:
    """The first lines of an output up to the ceiling, and how many body lines
    that leaves unprinted. At least one line stays; a single line longer than
    the ceiling is cut at the character count and counts as unprinted."""
    kept: list[str] = []
    used = 0
    printed_whole = 0
    for line in body_lines:
        if kept and used + len(line) + 1 > OUTPUT_MAX_CHARS:
            break
        if not kept and len(line) > OUTPUT_MAX_CHARS:
            kept.append(line[:OUTPUT_MAX_CHARS])
            used = OUTPUT_MAX_CHARS + 1
            continue
        kept.append(line)
        used += len(line) + 1
        printed_whole += 1
    return kept, len(body_lines) - printed_whole


def _cut_note(more: int) -> str:
    lines = "line" if more == 1 else "lines"
    return f"(output cut after {OUTPUT_MAX_CHARS:,} characters; {more} more {lines})"


def _omission_line(dropped: list[str]) -> str:
    names = " and ".join(_DISPLAY_OF_TAB[tab] for tab in dropped)
    langs = " or ".join(f'lang="{tab}"' for tab in dropped)
    noun = "samples" if len(dropped) > 1 else "sample"
    return f"({noun} in {names} omitted: pass {langs})"


__all__ = ["LANGS", "OUTPUT_MAX_CHARS", "contain"]
