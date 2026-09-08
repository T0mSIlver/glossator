"""What one answer run is configured with, and what a token of it costs.

Model identifiers are pinned to the dated ids rather than the ``-latest`` aliases:
a run recorded under ``mistral-medium-latest`` stops being reproducible the day
the alias moves, and D-023 wants every number traceable to the model that
produced it.
"""

from typing import Annotated, Self

import structlog
from pydantic import BaseModel, ConfigDict, Field, model_validator

logger = structlog.get_logger(__name__)

# Fixed ids read from `client.models.list()` on 2026-09-08. Every Mistral Medium
# 3.5 alias on the account (mistral-medium, mistral-medium-3, mistral-medium-3.5,
# mistral-medium-latest, magistral-medium-latest) resolves to this one.
MISTRAL_MEDIUM_3_5 = "mistral-medium-2604"
MISTRAL_SMALL_4 = "mistral-small-2603"
MINISTRAL_3_8B = "ministral-8b-2512"
MISTRAL_EMBED = "mistral-embed-2312"


class ModelPrice(BaseModel):
    """USD per million tokens, as published on the pricing page (D-017)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    input_usd_per_mtok: float
    output_usd_per_mtok: float


PRICES: dict[str, ModelPrice] = {
    MISTRAL_MEDIUM_3_5: ModelPrice(input_usd_per_mtok=1.50, output_usd_per_mtok=7.50),
    MISTRAL_SMALL_4: ModelPrice(input_usd_per_mtok=0.15, output_usd_per_mtok=0.60),
    MINISTRAL_3_8B: ModelPrice(input_usd_per_mtok=0.15, output_usd_per_mtok=0.15),
    # Embeddings are billed on input only; the output price is zero rather than
    # absent so one arithmetic path covers every model.
    MISTRAL_EMBED: ModelPrice(input_usd_per_mtok=0.10, output_usd_per_mtok=0.0),
}

DEFAULT_VARIANT = "sec1024"


class AnswerConfig(BaseModel):
    """One answering configuration: which model, how much context, how hard to look."""

    model_config = ConfigDict(frozen=True, extra="forbid", protected_namespaces=())

    model: str = MISTRAL_MEDIUM_3_5
    temperature: float = 0.2
    max_tokens: int = 1600

    top_k: Annotated[int, Field(ge=1, le=50)] = 8

    context_token_budget: int = 6000
    """Ceiling on the assembled context. Roughly a third of a 20k-token page set,
    which keeps a single_pass question near 8k prompt tokens."""

    round_cap: int = 4
    searches_per_round: int = 4
    tool_top_k: int = 4
    tool_result_chars: int = 600
    """Tool results are previews. The loop only has to decide what to look at
    next; the final generation re-reads the full chunks through context
    assembly, so paying for whole chunks twice buys nothing."""

    open_result_chars: int = 1600
    """`open` and `read` are deliberate drill-downs, so they show more."""

    page_cap: int = 4
    page_read_top_k: int = 40

    max_attempts: int = 4
    retry_base_seconds: float = 1.0
    request_timeout_ms: int = 180_000

    prices: dict[str, ModelPrice] = Field(default_factory=lambda: dict(PRICES))

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.model not in self.prices:
            raise ValueError(
                f"no price for model {self.model!r}; "
                f"priced models: {sorted(self.prices)} (add it to PRICES, D-017)"
            )
        return self

    def cost_usd(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """USD for one call. An unpriced model costs 0 and says so, loudly.

        Token counts are recorded either way, so a price added later can be
        applied to a run that already happened.
        """
        price = self.prices.get(model)
        if price is None:
            logger.warning("No price for model, cost recorded as zero", model=model)
            return 0.0
        return (
            prompt_tokens * price.input_usd_per_mtok + completion_tokens * price.output_usd_per_mtok
        ) / 1_000_000


__all__ = [
    "DEFAULT_VARIANT",
    "MINISTRAL_3_8B",
    "MISTRAL_EMBED",
    "MISTRAL_MEDIUM_3_5",
    "MISTRAL_SMALL_4",
    "PRICES",
    "AnswerConfig",
    "ModelPrice",
]
