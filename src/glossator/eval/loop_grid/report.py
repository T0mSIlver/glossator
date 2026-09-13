"""The grid README and its per-axis figures."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from glossator.eval.charts import bar_chart
from glossator.eval.loop_grid.models import AXIS_VALUES, TABLE_COLUMNS


def _cell_value(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    if value is None:
        return "--"
    for name, _caption, kind in TABLE_COLUMNS:
        if name == key:
            return {"pct": f"{value:.2f}", "num": f"{value:.1f}", "sec": f"{value:.1f}"}[kind]
    return str(value)


def render_readme(config: dict[str, Any], metrics: dict[str, Any]) -> str:
    """The grid's README (D-023): what was compared, on what, with what result."""
    server = metrics.get("generation_server")
    server_sentence = (
        f"Every configuration ran its chat calls on the local server `{server}` -- "
        "a quantized Ministral 3 served by llama.cpp -- with embeddings on the "
        "Mistral API."
        if server
        else "No generation server was configured for this grid, so its rows would "
        "run against the Mistral API, which the plan reserves for shipped figures."
    )
    header = "| configuration | " + " | ".join(caption for _k, caption, _f in TABLE_COLUMNS) + " |"
    divider = "|---" * (len(TABLE_COLUMNS) + 1) + "|"
    lines = [header, divider]
    for row in metrics["configurations"]:
        label = row["name"].removeprefix(f"{metrics['name']}-")
        status = "" if row.get("status") == "complete" else f" ({row.get('status') or '?'})"
        lines.append(
            f"| `{label}`{status} | "
            + " | ".join(_cell_value(row, key) for key, _caption, _kind in TABLE_COLUMNS)
            + " |"
        )
    notes = "\n".join(f"- {note}" for note in metrics.get("notes") or [])
    notes_section = f"\n\n## Notes on this run\n\n{notes}" if notes else ""
    judge_sentence = (
        "The judge was skipped for this grid (`--skip-judge`), so the judged "
        "columns (correctness, groundedness) are empty; every row holds its "
        "answers, traces, tokens and latencies, and a later `rejudge` fills the "
        "judged columns without re-running generation."
        if not metrics.get("judge_model")
        else f"Judge: `{metrics['judge_model']}`."
    )
    figures = "\n".join(
        f"- `figures/{figure_name(axis, what)}`"
        for axis, _values in AXIS_VALUES
        for what in ("correctness", "tokens")
    )
    return f"""# Search-loop cap grid: {metrics["name"]}

**What this measures.** The search loop stops after `round_cap` rounds, answers
at most `searches_per_round` searches per round, and shows the model
`tool_result_chars`-character previews of what its tools found (D-035c). None of
the three values had ever been varied; this grid moves one at a time away from
the shipped point (round_cap {metrics["shipped_point"]["round_cap"]}, searches_per_round
{metrics["shipped_point"]["searches_per_round"]}, tool_result_chars
{metrics["shipped_point"]["tool_result_chars"]}), so each row isolates one knob.

**Read the numbers as relative.** {server_sentence} They are comparisons between
configurations of the same server, not absolute quality figures; every shipped
figure keeps coming from the Mistral API (D-035c). A difference of a few points
on {metrics.get("questions", "--")} questions is a signal to follow up, not a
conclusion.

## Configuration

- Dataset: `{metrics["dataset"]}`, sha256 `{metrics["dataset_sha256"]}`
- Generation model: `{metrics["model"]}`; judge: `{metrics["judge_model"]}`; \
index variant: `{metrics["variant"]}`
- Structured output sent as `{metrics["response_format"]}`
- Each row is a normal answer-eval run of `search_loop` only, in the directory \
named in `config.json`.

## Results

{chr(10).join(lines)}

{judge_sentence}

## Figures

{figures}

Each figure shows one axis; the shipped point is the bar every other bar on that
axis is compared against.
{notes_section}

## Files

- `config.json` -- the grid definition: every row's axis, value, overrides and run directory.
- `metrics.json` -- the table above, as numbers.
- Each row's evidence (answers, citations, calls, per-question records) is in its
  own run directory, named in `config.json`.

## What it feeds

D-035c: whether the loop's caps should move, and in which direction, decided on
relative numbers from a local server before any API credits are spent.
"""


def figure_name(axis: str, what: str) -> str:
    return f"{what}-by-{axis}.svg"


def render_figures(metrics: dict[str, Any], figures_dir: Path) -> list[Path]:
    """One correctness figure and one token figure per axis, in the house style."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    by_name = {row["name"]: row for row in metrics["configurations"]}
    for axis, values in AXIS_VALUES:
        rows = _unique(
            [by_name.get(f"{metrics['name']}-shipped")]
            + [by_name.get(f"{metrics['name']}-{axis}-{label}") for label, _value in values]
        )
        for what, key, title in (
            ("correctness", "correctness", "Judged correctness"),
            ("tokens", "tokens_in", "Prompt tokens per answer"),
        ):
            # A row with no number is left out rather than drawn at zero: a
            # missing judged column and a genuine 0.0 must not look the same.
            measured = [row for row in rows if row.get(key) is not None]
            chart = bar_chart(
                f"{title} by {axis}",
                [(str(row.get("value") or "shipped"), (float(row[key]),)) for row in measured],
                (title,),
            )
            path = figures_dir / figure_name(axis, what)
            path.write_text(chart)
            written.append(path)
    return written


def _unique(rows: Sequence[dict[str, Any] | None]) -> list[dict[str, Any]]:
    """The rows in order, without the shipped point repeated under an axis label."""
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for row in rows:
        if row is None or row["name"] in seen:
            continue
        seen.add(row["name"])
        unique.append(row)
    return unique
