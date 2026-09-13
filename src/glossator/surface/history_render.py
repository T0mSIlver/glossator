"""History results as the MCP tool prints them: a phrase's first and last
stored date, a section's timeline, and the changes under a path."""

import json
from collections import Counter
from typing import Any

from glossator import history as history_service
from glossator.surface.history import HistoryForm
from glossator.surface.names import HISTORY

HISTORY_MAX_CHARS = 12_000
"""Per-call ceiling on a rendered timeline or change listing."""
DIFF_LIMIT_NOTE = f"note: diff cut at {history_service.DIFF_MAX_CHARS} characters"


def render_phrase(form: HistoryForm, result: dict[str, Any]) -> str:
    heading = f"history text: {json.dumps(form.value)}"
    if result.get("page_url"):
        heading += f" | page: {result['page_url']}"
    elif result.get("under"):
        heading += f" | under: {result['under']}"
    lines = [heading]
    first, last = result["first"], result["last"]
    if first is None:
        lines.append("Results: the phrase is absent from every stored snapshot.")
    else:
        first_line = f"first stored date with the phrase: {first['snapshot']} | {first['page']}"
        if result.get("absent_before"):
            first_line += f" (absent at {result['absent_before']})"
        lines.append(first_line)
        lines.append(f"last stored date with the phrase: {last['snapshot']} | {last['page']}")
        lines.append(
            f"Results: present in {result['snapshots_found']} of "
            f"{result['snapshots_total']} stored snapshots"
        )
    return "\n".join(lines)


def _state_target(state: dict[str, Any]) -> str:
    target = state.get("page") or "(absent)"
    if state.get("anchor"):
        target += f"#{state['anchor']}"
    return target


def _section_timeline(states: list[dict[str, Any]]) -> list[tuple[int, list[str]]]:
    """Timeline blocks, each with the index of the last state it covers: a run of
    unchanged or absent dates collapses into one line."""
    if not states:
        return []
    timeline: list[tuple[int, list[str]]] = []
    first = states[0]
    if first.get("page"):
        end = 0
        while (
            end + 1 < len(states)
            and states[end + 1].get("page") is not None
            and states[end + 1]["state"] == "same"
        ):
            end += 1
        if end:
            timeline.append(
                (
                    end,
                    [
                        f"present at {first['snapshot']}, same through "
                        f"{states[end]['snapshot']} | {_state_target(states[end])}"
                    ],
                )
            )
        else:
            timeline.append((0, [f"present at {first['snapshot']} | {_state_target(first)}"]))
    else:
        end = 0
        timeline.append((0, [f"absent at {first['snapshot']}"]))

    index = end + 1
    while index < len(states):
        state = states[index]
        previous = states[index - 1]
        date = state["snapshot"]
        before = previous["snapshot"]
        if state.get("page") is None:
            if previous.get("page") is not None:
                lines = [f"removed between {before} and {date} | {_state_target(previous)}"]
            else:
                end = index
                while end + 1 < len(states) and states[end + 1].get("page") is None:
                    end += 1
                lines = [f"absent through {states[end]['snapshot']}"]
                index = end
        elif previous.get("page") is None:
            lines = [f"added between {before} and {date} | {_state_target(state)}"]
        elif state["state"] == "changed":
            lines = [f"changed between {before} and {date} | {_state_target(state)}"]
            if state.get("diff"):
                lines.extend(["```diff", state["diff"], "```"])
                if state.get("diff_truncated"):
                    lines.append(DIFF_LIMIT_NOTE)
        elif state["state"] == "moved":
            lines = [
                f"moved between {before} and {date} | "
                f"{_state_target(previous)} -> {_state_target(state)}"
            ]
        else:
            end = index
            while (
                end + 1 < len(states)
                and states[end + 1].get("page") is not None
                and states[end + 1]["state"] == "same"
            ):
                end += 1
            lines = [f"same through {states[end]['snapshot']} | {_state_target(states[end])}"]
            index = end
        timeline.append((index, lines))
        index += 1
    return timeline


def render_section(form: HistoryForm, result: dict[str, Any], max_chars: int) -> str:
    """The section's timeline, whole blocks while the budget lasts, then the call
    that names the same section again."""
    heading = f"history page: {result.get('page_url', form.value)}"
    result_section = result.get("section")
    if result_section:
        heading += f" | section: {result_section}"
    lines = [heading]
    states = result["states"]
    spent = 0
    rendered = -1
    for end_index, block in _section_timeline(states):
        size = sum(len(line) + 1 for line in block)
        if rendered >= 0 and spent + size > max_chars:
            break
        spent += size
        rendered = end_index
        lines.extend(block)
    shown = rendered + 1
    lines.append(f"Results: {shown} of {len(states)} stored snapshots")
    if shown < len(states):
        arguments = f'page_url="{form.value}"'
        if form.section is not None:
            arguments += f', section="{form.section}"'
        lines.append(
            f"next: {HISTORY}({arguments}) again names the same section; the dates "
            f"after {states[rendered]['snapshot']} were not rendered in this call."
        )
    return "\n".join(lines)


def _change_block(row: dict[str, Any]) -> list[str]:
    line = f"  {row['state']} | {row['page']}"
    if row.get("level") == "page":
        # One row per page beneath the prefix: the row is the URL, so no cite line.
        if row.get("sections") is not None:
            line += f" | {row['sections']} sections"
        elif row.get("counts"):
            line += " | " + ", ".join(f"{n} {state}" for state, n in row["counts"].items())
        block = [line]
        if row.get("old_page"):
            block.append(f"    from: {row['old_page']}")
        return block
    if row.get("key"):
        line += f" | section: {row['key']}"
    elif row.get("sections") is not None:
        line += f" | {row['sections']} sections"
    block = [line]
    if row.get("old_page"):
        old = row["old_page"]
        if row.get("old_key"):
            old += f"#{row['old_key']}"
        block.append(f"    from: {old}")
    block.append(f"    cite: {row['cite']}")
    return block


def render_under(result: dict[str, Any], max_chars: int) -> str:
    """Per interval a summary line, then the rows while the budget lasts; every
    summary is printed even when the rows are cut."""
    intervals = result["intervals"]
    summaries: list[str] = []
    for interval in intervals:
        sections = Counter(row["state"] for row in interval["rows"] if row.get("level") != "page")
        pages = Counter(row["state"] for row in interval["rows"] if row.get("level") == "page")
        parts = [
            f"{sections[state]} {state}"
            for state in ("added", "removed", "changed", "moved")
            if sections[state]
        ] + [
            f"{pages[state]} {'page' if pages[state] == 1 else 'pages'} {state}"
            for state in ("added", "removed", "changed", "moved")
            if pages[state]
        ]
        detail = ", ".join(parts) or "no change"
        summaries.append(f"between {interval['before']} and {interval['after']}: {detail}")
    heading = f"history under: {result['under']} | since: {result['since']}"
    result_line = f"Results: {result['changes']} changes over {len(intervals)} intervals"
    cut_line = "next: narrow under or raise since; the rest was not rendered"
    reserved = sum(len(line) + 1 for line in [heading, *summaries, result_line, cut_line])
    remaining = max(0, max_chars - reserved)
    rendered_rows = 0
    detail_lines: list[list[str]] = []
    for interval in intervals:
        lines: list[str] = []
        for row in interval["rows"]:
            block = _change_block(row)
            size = sum(len(line) + 1 for line in block)
            if size > remaining:
                break
            remaining -= size
            rendered_rows += 1
            lines.extend(block)
        detail_lines.append(lines)
    lines = [heading]
    for summary, details in zip(summaries, detail_lines, strict=True):
        lines.append(summary)
        lines.extend(details)
    lines.append(result_line)
    if rendered_rows < result["changes"]:
        lines.append(cut_line)
    else:
        page_row = next(
            (
                row
                for interval in intervals
                for row in interval["rows"]
                if row.get("level") == "page" and row["state"] != "removed"
            ),
            None,
        )
        first = next(
            (row for interval in intervals for row in interval["rows"] if row.get("key")),
            None,
        )
        if page_row is not None:
            lines.append(
                f'next: {HISTORY}(under="{page_row["page"]}") lists the sections of one page'
            )
        elif first is not None:
            lines.append(
                f'next: {HISTORY}(page_url="{first["page"]}", section="{first["key"]}") '
                "shows the diff of one section"
            )
    return "\n".join(lines)


def render_history(form: HistoryForm, result: dict[str, Any], max_chars: int) -> str:
    if form.kind == "text":
        return render_phrase(form, result)
    if form.kind == "page_url":
        return render_section(form, result, max_chars)
    return render_under(result, max_chars)


__all__ = ["HISTORY_MAX_CHARS", "render_history", "render_phrase", "render_section", "render_under"]
