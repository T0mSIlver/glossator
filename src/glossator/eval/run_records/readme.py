"""The run README, every sentence computed from the run's own numbers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from glossator.eval.pricing import price_for
from glossator.eval.run_records.models import STATUS_FAILED, STATUS_IN_PROGRESS


def _conclusion(config: Mapping[str, Any], metrics: Mapping[str, Any]) -> str:
    """The run's conclusion, computed from its own numbers."""
    if metrics["status"] == STATUS_IN_PROGRESS:
        return "The run had not finished when this summary was last written."
    if metrics["status"] == STATUS_FAILED:
        return f"{_as_sentence(metrics['error'])} No dataset was written."

    parts: list[str] = []
    requested = metrics["requested"] or metrics["kept"]
    parts.append(
        f"The run asked for {requested} questions and accepted {metrics['kept']} of "
        f"{metrics['candidates']} candidates."
    )
    shortfalls = metrics["shortfall_by_type"]
    if shortfalls:
        listed = ", ".join(f"{name} short by {count}" for name, count in sorted(shortfalls.items()))
        parts.append(
            f"{metrics['shortfall']} question(s) could not be filled from the corpus: {listed}. "
            "The dataset holds what was accepted."
        )
    else:
        parts.append("Every question type was filled.")
    reasons = sorted(metrics["dropped_by_reason"].items(), key=lambda item: (-item[1], item[0]))
    if reasons:
        top = ", ".join(f"{reason} ({count})" for reason, count in reasons[:3])
        parts.append(f"The largest drop reasons were {top}.")
    uncached = metrics["uncached_usage"]
    cost = metrics["estimated_usd"]
    price = price_for(metrics["model"])
    if cost is None:
        cost_sentence = f"No price is recorded for {metrics['model']}, so the cost is unknown."
    elif cost == 0.0 and price is not None and price.note:
        cost_sentence = (
            f"{uncached['prompt_tokens']} prompt and {uncached['completion_tokens']} completion "
            f"tokens were paid for at 0.00 USD against the Mistral budget ({price.note})."
        )
    else:
        cost_sentence = (
            f"{uncached['prompt_tokens']} prompt and {uncached['completion_tokens']} completion "
            f"tokens cost an estimated {cost:.4f} USD."
        )
    parts.append(cost_sentence)
    parts.append("The dataset feeds the retrieval and answer evaluations in D-016.")
    return " ".join(parts)


def render_readme(config: Mapping[str, Any], metrics: Mapping[str, Any]) -> str:
    if config.get("kind", "generate") != "generate":
        return _render_generic_readme(config, metrics)
    reason_lines = [
        f"- {reason}: {count}" for reason, count in metrics["dropped_by_reason"].items()
    ] or ["- None"]
    type_lines = []
    for question_type, candidates in metrics["candidates_by_type"].items():
        kept = metrics["kept_by_type"].get(question_type, 0)
        asked = metrics["requested_by_type"].get(question_type)
        asked_label = f"{asked} asked, " if asked is not None else ""
        type_lines.append(
            f"- {question_type}: {asked_label}{candidates} candidates, {kept} kept, "
            f"{candidates - kept} dropped"
        )
    if not type_lines:
        type_lines = ["- No candidates were generated"]
    kind_lines = [
        f"- {kind}: {count} calls, {metrics['usage_by_kind'][kind]['prompt_tokens']} prompt "
        f"+ {metrics['usage_by_kind'][kind]['completion_tokens']} completion tokens"
        for kind, count in metrics["calls_by_kind"].items()
    ] or ["- No calls were made"]
    usage = metrics["usage"]
    uncached = metrics["uncached_usage"]
    dataset = metrics["dataset"] or "No dataset was written"
    return (
        "# Dataset generation run\n\n"
        f"This run asked {config['model']} to generate documentation questions from "
        f"{config['corpus']}. It measures how many valid questions of each type the "
        f"generators produce, and what they cost.\n\n"
        "## Question\n\n"
        "Does this generator configuration produce standalone questions whose assigned "
        "sources are all necessary for the answer, in the numbers the development set needs?\n\n"
        "## Configuration\n\n"
        "`config.json` records every parameter and prompt hash.\n\n"
        f"- Provider: {config['provider']}\n"
        f"- Model: {config['model']}\n"
        f"- Thinking: {config['thinking']}\n"
        f"- Seed: {config['seed']}\n"
        f"- Prompt version: {config['prompt_version']}\n"
        f"- Corpus commit: {config['corpus_commit']}\n"
        f"- Requested questions: {config['n']}\n"
        f"- Dataset: {dataset}\n\n"
        "## Results\n\n"
        f"The run processed {metrics['candidates']} candidates, kept {metrics['kept']}, "
        f"and dropped {metrics['dropped']}.\n\n"
        + "\n".join(type_lines)
        + "\n\nDropped candidates by reason:\n\n"
        + "\n".join(reason_lines)
        + "\n\n## Calls and usage\n\n"
        f"The provider handled {metrics['calls']} calls, of which {metrics['cached_calls']} "
        f"were cache hits and {metrics['failed_calls']} returned an error that was retried "
        "or recorded.\n\n" + "\n".join(kind_lines) + "\n\n"
        f"Total tokens: {usage['prompt_tokens']} prompt, {usage['completion_tokens']} completion, "
        f"{usage['reasoning_tokens']} reasoning. Paid for in this run (uncached): "
        f"{uncached['prompt_tokens']} prompt, {uncached['completion_tokens']} completion, "
        f"{uncached['reasoning_tokens']} reasoning.\n\n"
        "## Figures\n\n"
        "`figures/` holds the charts, regenerated from `metrics.json` by "
        "`make eval-report run=<dir>`.\n\n"
        "- `figures/accepted-by-type.svg`: accepted against dropped, per question type\n"
        "- `figures/drop-reasons.svg`: how many candidates each drop reason accounts for\n"
        "- `figures/tokens-by-call-kind.svg`: tokens spent on generating against checking\n\n"
        "## Conclusion\n\n"
        f"{_conclusion(config, metrics)}\n"
    )


def _render_generic_readme(config: Mapping[str, Any], metrics: Mapping[str, Any]) -> str:
    """A run of another kind (a translation, a perturbation, a probe): plainer prose."""
    usage = metrics["usage"]
    uncached = metrics["uncached_usage"]
    kind_lines = [
        f"- {kind}: {count} calls, {metrics['usage_by_kind'][kind]['prompt_tokens']} prompt "
        f"+ {metrics['usage_by_kind'][kind]['completion_tokens']} completion tokens"
        for kind, count in metrics["calls_by_kind"].items()
    ] or ["- No calls were made"]
    config_lines = [f"- {key}: {_short(value)}" for key, value in sorted(config.items())]
    dataset = metrics["dataset"] or "No dataset was written"
    return (
        f"# {config.get('kind', 'run').capitalize()} run\n\n"
        f"Status: {metrics['status']}."
        + (f" {_as_sentence(metrics['error'])}" if metrics.get("error") else "")
        + "\n\n"
        "## Configuration\n\n" + "\n".join(config_lines) + "\n\n"
        "## Records\n\n"
        f"- rows: {metrics['candidates']}, kept: {metrics['kept']}\n"
        f"- dataset: {dataset}\n"
        + _breakdown_lines(metrics)
        + "\n## Calls\n\n"
        + "\n".join(kind_lines)
        + "\n\n"
        f"- total: {metrics['calls']} calls ({metrics['cached_calls']} cached), "
        f"{usage['prompt_tokens']} prompt + {usage['completion_tokens']} completion tokens "
        f"({usage['reasoning_tokens']} reasoning); uncached {uncached['prompt_tokens']} + "
        f"{uncached['completion_tokens']}; {_estimated(metrics)}\n\n"
        + _figure_lines(config)
        + "Every call is in `calls.jsonl` and every row in `records.jsonl`.\n"
    )


CONFIG_LIST_PREVIEW = 6
"""How many entries of a long list a README shows before it says how many more.

The whole list stays in `config.json`, which is the record; a README that opens
with a hundred and twenty ids is not readable, and that is the README's only job.
"""


def _short(value: Any) -> str:
    if isinstance(value, list) and len(value) > CONFIG_LIST_PREVIEW:
        shown = ", ".join(str(item) for item in value[:CONFIG_LIST_PREVIEW])
        return f"[{shown}, ... {len(value) - CONFIG_LIST_PREVIEW} more, see config.json]"
    return str(value)


def _breakdown_lines(metrics: Mapping[str, Any]) -> str:
    """Kept and dropped per row type, and why, when the rows carry a type.

    A run whose rows are all the same thing has nothing to break down, and
    `summarize` labels those rows `row`; that case renders nothing.
    """
    candidates = metrics["candidates_by_type"]
    if not candidates or set(candidates) == {"row"}:
        return ""
    kept = metrics["kept_by_type"]
    lines = [
        f"- {name}: {count} candidates, {kept.get(name, 0)} kept, "
        f"{count - kept.get(name, 0)} dropped"
        for name, count in candidates.items()
    ]
    reasons = [f"- {reason}: {count}" for reason, count in metrics["dropped_by_reason"].items()]
    if reasons:
        lines.append("")
        lines.append("Dropped by reason:")
        lines.append("")
        lines.extend(reasons)
    return "\n" + "\n".join(lines) + "\n"


def _estimated(metrics: Mapping[str, Any]) -> str:
    """What the run cost, or that its model has no published price."""
    cost = metrics["estimated_usd"]
    if cost is None:
        return f"no price is recorded for {metrics['model']}, so the cost is unknown"
    return f"estimated {cost:.4f} USD against the Mistral budget"


def _figure_lines(config: Mapping[str, Any]) -> str:
    """The charts the run rendered, named by the run itself (D-023)."""
    figures = list(config.get("figures") or [])
    if not figures:
        return ""
    listed = "\n".join(f"- `figures/{name}`" for name in figures)
    return f"## Figures\n\n{listed}\n\n"


def _as_sentence(text: str | None) -> str:
    if not text:
        return "The run failed."
    sentence = text.strip()
    sentence = sentence[0].upper() + sentence[1:]
    if sentence[-1] not in ".!?":
        sentence += "."
    return sentence
