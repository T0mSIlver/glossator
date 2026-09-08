"""What a run cost, in USD.

The budget is 20 USD of Mistral credit (D-017). Dataset generation and judging
run on GLM through the z.ai coding plan, which charges nothing against that
budget (D-020) -- its tokens are still counted, because "free" is a statement
about this month's plan, not about the work.
"""

from __future__ import annotations

from dataclasses import dataclass

from glossator.eval.providers import TokenUsage


@dataclass(frozen=True, slots=True)
class Price:
    """USD per million tokens, as published on the provider's pricing page."""

    input_usd_per_m: float
    output_usd_per_m: float
    note: str = ""


# Mistral prices read from the pricing page on 2026-09-08 (D-017). The z.ai
# coding plan is a flat subscription, so its per-token price against the Mistral
# budget is zero.
PRICES: dict[str, Price] = {
    "mistral-medium-3-5": Price(1.50, 7.50),
    "mistral-medium-latest": Price(1.50, 7.50),
    "mistral-large-3": Price(0.50, 1.50),
    "mistral-small-4": Price(0.15, 0.60),
    "ministral-3-8b": Price(0.15, 0.15),
    "mistral-embed": Price(0.10, 0.0),
    "glm-5.3": Price(0.0, 0.0, note="z.ai coding plan, not billed to the Mistral budget"),
    "glm-5.3-flash": Price(0.0, 0.0, note="z.ai coding plan, not billed to the Mistral budget"),
}


def price_for(model: str) -> Price | None:
    """The price entry for a model, or None when the model is not in the table."""
    return PRICES.get(model)


def estimate_usd(model: str, usage: TokenUsage) -> float | None:
    """Cost of ``usage`` on ``model``, or None when the model has no price entry.

    Reasoning tokens are billed as output tokens by both providers, and the
    OpenAI-compatible ``completion_tokens`` already includes them.
    """
    price = price_for(model)
    if price is None:
        return None
    return round(
        usage.prompt_tokens / 1_000_000 * price.input_usd_per_m
        + usage.completion_tokens / 1_000_000 * price.output_usd_per_m,
        6,
    )
