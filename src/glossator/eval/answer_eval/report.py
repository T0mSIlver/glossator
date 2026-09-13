"""The run README (D-023)."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from glossator.answer.config import PRICES, aliased_price
from glossator.eval.answer_eval.metrics import REFERENCE_PRICING_MODEL
from glossator.eval.answer_eval.prompts import JUDGE_PROMPT_HASHES, JUDGE_VERSION
from glossator.eval.answer_eval.tables import _agreement_section, format_value, metric_table

FAMILIES: tuple[tuple[str, str, tuple[tuple[str, str], ...]], ...] = (
    (
        "Citations against the gold sources",
        "Whether the answer's verified citations point at the pages the dataset "
        "says hold the answer. Unanswerable questions have no gold source, so they "
        "are left out of these tables rather than counted as failures. Capability "
        "questions also accept a named model's own card, and the last table counts "
        "matches that passed only because of that documented relaxation.",
        (
            ("cited_url_match", "a verified citation names a gold page"),
            ("cited_anchor_match", "a verified citation names the gold section"),
            ("gold_relaxed_matches", "matches accepted through the model-card relaxation"),
        ),
    ),
    (
        "Citation verification",
        "Whether the quotes the model wrote are in the sources it named. A "
        "fabricated rejection is a sentence that is not in the source at all; a "
        "cosmetic one is a quote too short to be evidence. The two are reported "
        "apart because averaging them hides both (D-027a). Distinct sources are "
        "counted beside the citations because an answer that cites `[1]` five "
        "times looks well cited and is not.",
        (
            ("citation_verification_rate", "verified citations over emitted citations"),
            ("unverified_citations_per_answer", "rejected citations per answer"),
            ("fabricated_per_answer", "fabricated rejections per answer"),
            ("cosmetic_per_answer", "cosmetic rejections per answer"),
            ("distinct_sources_cited", "different sources cited per answer"),
            ("unmatched_markers_per_answer", "`[n]` markers with no citation behind them"),
        ),
    ),
    (
        "Refusal",
        "`insufficient_evidence` should be set on exactly the questions the "
        "documentation cannot answer. This table scores both directions: a refused "
        "answerable question is as wrong as an answered unanswerable one.",
        (("refusal_correct", "the refusal flag matches the question"),),
    ),
    (
        "Judged quality",
        "The primary judge's verdicts (D-021), reported beside the deterministic numbers and "
        "never merged into them. Correctness scores correct as 1, partial as 0.5, "
        "wrong as 0. Groundedness is the fraction of the answer's factual claims "
        "the cited passages support. Citation relevance is the fraction of "
        "citations that support the sentence they are attached to.",
        (
            ("correctness", "correctness against the reference answer"),
            ("groundedness", "claims supported by the cited passages"),
            ("citation_relevance", "citations that support their sentence"),
        ),
    ),
    (
        "Effort",
        "What each strategy spent to get there.",
        (
            ("latency_p50_s", "median seconds per answer"),
            ("latency_p95_s", "95th percentile seconds per answer"),
            ("tokens_in", "prompt tokens per answer"),
            ("tokens_out", "completion tokens per answer"),
            ("usd", "USD per question, at this run's price table"),
            ("reference_usd", f"USD per question at {REFERENCE_PRICING_MODEL} prices"),
            ("tool_calls", "tool calls per answer"),
            ("rounds", "rounds per answer"),
            ("round_cap_hit", "share of answers that ran out of rounds"),
        ),
    ),
)


def _trade_off(metrics: Mapping[str, Any]) -> str:
    """One sentence naming the winners and what the best answer costs."""
    winner = metrics["winners"]
    quality = winner.get("correctness") or winner.get("cited_url_match")
    cheap = winner.get("usd") or winner.get("latency_p50_s")
    if not quality:
        return "No strategy produced a comparable number in this run."
    if quality == cheap:
        return (
            f"`{quality}` wins on quality and on cost, so there is no trade-off to "
            "make in this run."
        )
    strategies = metrics["by_strategy"]
    quality_cell = strategies[quality]["all"]
    cheap_cell = strategies[cheap]["all"] if cheap in strategies else quality_cell
    ratio = (
        quality_cell["tokens_in_total"] / cheap_cell["tokens_in_total"]
        if cheap_cell["tokens_in_total"]
        else 1.0
    )
    return (
        f"`{quality}` answers best and `{cheap}` is cheapest: the better answers "
        f"cost {ratio:.1f}x the prompt tokens of the cheaper strategy."
    )


def _server_line(config: Mapping[str, Any]) -> str:
    """The generation server, stated so a local-server run cannot pose as an API run."""
    server = config.get("generation_server")
    if not server:
        return "- Generation server: the Mistral API (`https://api.mistral.ai`)"
    effort = config.get("reasoning_effort")
    effort_note = f" Chat calls were sent with `reasoning_effort={effort}`." if effort else ""
    return (
        f"- Generation server: `{server}` -- a local server, not the Mistral API. "
        "Every judged number, latency and token count in this run describes that "
        "server; none of it is comparable with an API run of the same configuration." + effort_note
    )


def _overrides_line(config: Mapping[str, Any]) -> str:
    overrides = dict(config.get("answer_config_overrides") or {})
    if not overrides:
        return "- Answer-config overrides: none (the shipped configuration)"
    rendered = ", ".join(f"{key}={value!r}" for key, value in sorted(overrides.items()))
    return f"- Answer-config overrides: {rendered}"


def render_readme(config: Mapping[str, Any], metrics: Mapping[str, Any]) -> str:
    """The run README (D-023). Every sentence in it is computed from the records."""
    totals = metrics["totals"]
    model = str(metrics["model"])
    alias = aliased_price(model) if model not in PRICES else None
    unpriced = model not in PRICES and alias is None
    if unpriced:
        price_note = (
            f"\n\n`{model}` has no published price, so the USD column of this "
            f"run is zero by construction. The row beside it prices the same recorded "
            f"tokens at {REFERENCE_PRICING_MODEL} rates (D-017), which is what the "
            "shipped configuration would have cost."
        )
    elif alias is not None:
        price_note = (
            f"\n\n`{model}` is a local-server alias for Ministral 3 14B: costs use "
            "the published Ministral 3 API rate applied to a local run, not API tokens."
        )
    else:
        price_note = ""
    judged = (
        f"{totals['judged']} of {metrics['records']} answers were judged by "
        f"the primary judge `{metrics['judge_model']}`."
        if metrics.get("judge_model")
        else "The judge was skipped in this run, so only the deterministic tables below are filled."
    )
    winner_lines = [
        f"- `{metric}`: **{strategy}**"
        for metric, strategy in metrics["winners"].items()
        if strategy is not None
    ]
    judge_models = (
        ", ".join(f"`{model}`" for model in metrics.get("judge_models") or [])
        or "none (--skip-judge)"
    )
    judge_cost = (
        f"Judging spent {totals['judge_tokens_in']} prompt and "
        f"{totals['judge_tokens_out']} completion tokens over {totals['judge_calls']} "
        f"call(s) ({totals['judge_reasoning_tokens']} of them reasoning tokens, with "
        "thinking disabled), at a mean of "
        f"{totals['judge_latency_s_mean']:.1f} s per judgement and "
        f"{totals['judge_failures']} verdict(s) that did not validate. The z.ai coding "
        "plan bills nothing against the Mistral budget (D-020); the same judging on "
        f"{REFERENCE_PRICING_MODEL} would have cost "
        f"{totals['judge_reference_usd_total']:.4f} USD."
        if totals["judge_calls"]
        else "Nothing was judged in this run."
    )
    # Notes are the one part of the README an operator writes, and they are
    # written on the command line so that the README stays fully generated: a
    # sentence typed into a rendered file is lost the next time it is rendered.
    notes = "\n".join(f"- {note}" for note in config.get("notes") or [])
    notes_section = f"\n\n## Notes on this run\n\n{notes}" if notes else ""
    family_sections = []
    for title, blurb, metric_list in FAMILIES:
        tables = [
            f"**{metric}** -- {caption}\n\n{metric_table(metrics, metric)}"
            for metric, caption in metric_list
        ]
        family_sections.append(f"### {title}\n\n{blurb}\n\n" + "\n\n".join(tables))

    return f"""# Answer evaluation: {", ".join(metrics["strategies"])} on `{metrics["variant"]}`

**What this measures.** Which way of gathering evidence produces the best cited
answer, and what each one costs. Every question of the dataset is run through
each strategy against the same index, and every answer is scored twice: once by
code that can be re-run without a model, and once by a judge.

The deterministic checks are the primary numbers (D-016). They ask whether a
verified citation landed on a page the dataset names as gold, whether the quotes
the model wrote survive the verifier, whether the answer refused exactly the
questions the documentation cannot answer, and what the run spent. None of them
depends on a model's opinion, so none of them moves when a judge is swapped.

The judge answers what code cannot: whether the answer is *right*, whether its
claims are actually in the passages it cites, and whether each citation supports
the sentence it hangs on. It is shown the question, the reference answer, the
answer and the cited passages verbatim. It sees no URL, page identifier, or strategy.

## Configuration

- Generation model: `{metrics["model"]}`
{_server_line(config)}
{_overrides_line(config)}
- Judge models: {judge_models}; primary first ({JUDGE_VERSION})
- Index variant: `{metrics["variant"]}`, top_k {config.get("top_k")}, \
rerank {config.get("rerank", "unknown")} ({config.get("rerank_model") or "off"}), context budget \
{config.get("context_token_budget")} tokens
- Search loop caps: round_cap {config.get("answer_config", {}).get("round_cap", "unknown")}, \
searches_per_round {config.get("answer_config", {}).get("searches_per_round", "unknown")}, \
tool_result_chars {config.get("answer_config", {}).get("tool_result_chars", "unknown")}, \
response_format {config.get("answer_config", {}).get("response_format", "unknown")}
- Non-English questions rendered in English for retrieval: \
{config.get("translate_for_retrieval", "unknown")}
- Question reworded into the documentation's vocabulary for retrieval: \
{config.get("rewrite_for_retrieval", "unknown")}
- Dataset: `{metrics["dataset"]}`, sha256 `{metrics["dataset_sha256"]}`
- Questions: {metrics["questions"]}; strategies: {len(metrics["strategies"])}; \
records: {metrics["records"]}
- Judge prompt hashes: {json.dumps(JUDGE_PROMPT_HASHES, sort_keys=True)}

`config.json` holds every other parameter, including the price table the USD
columns were computed with.{notes_section}

## Results

{judged} {totals["errors"]} answer(s) ended in an error and are recorded with it.

{(chr(10) * 2).join(family_sections)}

{_agreement_section(metrics)}

## Cost and latency

The run made {metrics["records"]} answers over {metrics["questions"]} questions:
{totals["tokens_in_total"]} prompt and {totals["tokens_out_total"]} completion tokens,
{totals["usd_total"]:.4f} USD at this run's price table and
{totals["reference_usd_total"]:.4f} USD at {REFERENCE_PRICING_MODEL} prices. Median
answer latency was {format_value(totals["latency_p50_s"], "latency_p50_s")} s, 95th
percentile {format_value(totals["latency_p95_s"], "latency_p95_s")} s.{price_note}

{judge_cost}

## Winner per metric

{chr(10).join(winner_lines) or "- No metric had a comparable value."}

{_trade_off(metrics)}

## Figures

`figures/` is regenerated from `metrics.json` by `make eval-report run={config.get("run_dir")}`.

- `citation-match.svg`: gold URL and gold anchor match, per strategy
- `verification-rate.svg`: verified, fabricated and cosmetic citations, per strategy
- `correctness.svg`: correct, partial and wrong, per strategy
- `groundedness.svg`: groundedness and citation relevance, per strategy
- `latency-vs-correctness.svg`: what the better answers cost in seconds
- `cost-per-question.svg`: USD per question at {REFERENCE_PRICING_MODEL} prices

## Files

- `config.json` -- every parameter, including the judge prompt hashes and the price table.
- `calls.jsonl` -- every model call, verbatim. `source` is `answer` for the serving
  path's calls and `judge` for the judge's.
- `records.jsonl` -- one line per (question, strategy): the answer, its verified and
  rejected citations, the whole trace including the context the model saw, the judge's
  input and raw output, usage, latency and cost. These rows are also the run's
  checkpoint: re-running with the same name skips the pairs already in them.
- `metrics.json` -- every number in the tables above.

## What it feeds

D-016 (which deterministic checks and which judged ones the answer eval reports),
D-027 (which strategy the shipped `ask` defaults to) and D-017a (the generation
model column, so this run and a Mistral Medium 3.5 re-run stay comparable).
"""
