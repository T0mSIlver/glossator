"""Answer settings and model prices, with dated model IDs for reproducible runs."""

from collections.abc import Mapping
from typing import Annotated, Literal

import structlog
from pydantic import BaseModel, ConfigDict, Field

from glossator.clients import chat_server_url

logger = structlog.get_logger(__name__)

# Fixed ids read from `client.models.list()` on 2026-09-08. Every Mistral Medium
# 3.5 alias on the account (mistral-medium, mistral-medium-3, mistral-medium-3.5,
# mistral-medium-latest, magistral-medium-latest) resolves to this one.
MISTRAL_MEDIUM_3_5 = "mistral-medium-2604"
MISTRAL_SMALL_4 = "mistral-small-2603"
MINISTRAL_3_8B = "ministral-8b-2512"
MINISTRAL_3_14B = "ministral-14b-2512"
LOCAL_MINISTRAL_3_14B = "llamacpp/ministral3-14b"
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
    # The pricing page publishes one Ministral 3 line and does not break the 14B
    # out separately (checked 2026-09-09), so it is recorded at the same rate. The
    # token counts are recorded whatever the price, so a published number can be
    # applied to a run that already happened.
    MINISTRAL_3_14B: ModelPrice(input_usd_per_mtok=0.15, output_usd_per_mtok=0.15),
    # Embeddings are billed on input only; the output price is zero rather than
    # absent so one arithmetic path covers every model.
    MISTRAL_EMBED: ModelPrice(input_usd_per_mtok=0.10, output_usd_per_mtok=0.0),
}

DEFAULT_VARIANT = "sec1024"

LOCAL_MINISTRAL_3_14B_MARKER = "ministral3-14b"
"""Substring the local llama.cpp server uses in the ids it reports.

The request names ``llamacpp/ministral3-14b`` while the response reports
``ministral3-14b`` (no prefix, no date); neither matches the published id
``ministral-14b-2512``. Any id containing this marker prices as Ministral 3 14B
at the published API rate, with the run recording that the rate was applied to
a local run rather than to API tokens.
"""


def aliased_price(model: str, prices: Mapping[str, ModelPrice] | None = None) -> ModelPrice | None:
    """The published price for a model id, following the local-server alias.

    Exact ids come straight from the price table; an id containing the local
    Ministral 3 14B marker prices as ``MINISTRAL_3_14B``. Anything else has no
    published price. ``prices`` lets a run apply its own table -- the one it
    recorded -- through the same alias rule, so a price is never resolved two
    ways in two places.
    """
    table = PRICES if prices is None else prices
    price = table.get(model)
    if price is not None:
        return price
    if LOCAL_MINISTRAL_3_14B_MARKER in model.casefold():
        return table.get(MINISTRAL_3_14B) or PRICES[MINISTRAL_3_14B]
    return None


def price_of(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    prices: Mapping[str, ModelPrice] | None = None,
) -> float | None:
    """USD for one call, or ``None`` when the model has no published price.

    The one place the arithmetic lives: the serving path, the eval's repricing
    pass and the grid all resolve a price the same way and multiply it the same
    way, so a rate applied in one of them is applied in all of them.
    """
    price = aliased_price(model, prices)
    if price is None:
        return None
    return (
        prompt_tokens * price.input_usd_per_mtok + completion_tokens * price.output_usd_per_mtok
    ) / 1_000_000


class AnswerConfig(BaseModel):
    """One answering configuration: which model, how much context, how hard to look."""

    model_config = ConfigDict(frozen=True, extra="forbid", protected_namespaces=())

    model: str = MISTRAL_MEDIUM_3_5
    temperature: float = 0.2
    max_tokens: int = 1600

    top_k: Annotated[int, Field(ge=1, le=50)] = 8

    context_token_budget: int = 6000
    """Ceiling on the assembled context. A `single_pass` question at ``top_k`` 8
    measured 1.9k-3.0k prompt tokens against this budget in the 2026-09-09 smoke,
    so the budget binds only for `outline`, which reads whole pages."""

    min_quote_chars: int = 8
    """A quote shorter than this verifies against almost any chunk, so it is not
    evidence that the model read the source."""

    translate_for_retrieval: bool = True
    """Whether a non-English question is rendered in English before retrieval and
    reranking (D-008a). Off, the question is retrieved exactly as it was asked,
    which is what the French baseline measured."""

    render_max_tokens: int = 200
    """The rendering is one restated question, not prose."""

    rewrite_for_retrieval: bool = False
    """Whether the question is reworded into the documentation's vocabulary before
    retrieval. Off until measured: every generated dev question was written from
    the section that answers it, so on that distribution there is nothing to
    reword, and the shipped single pass already matched the search loop there
    (D-035). It composes with the rendering, which runs first."""

    rewrite_max_tokens: int = 120
    """The rewrite is a search query, shorter than the question it came from."""

    round_cap: int = 4
    searches_per_round: int = 4
    tool_top_k: int = 4
    max_tool_top_k: int = 10
    """Ceiling on what one search call may return, whatever the model asks for."""

    max_open_window: int = 5
    """Ceiling on `open`'s window. Each step of it is another positional query."""

    loop_max_tokens: int = 800
    """The loop's turns are tool calls and a one-line stop, not prose."""

    picker_max_tokens: int = 300
    """The outline picker returns a handful of numbers and one sentence."""

    tool_result_chars: int | None = 600
    """Tool results are previews. The loop only has to decide what to look at
    next; the final generation re-reads the full chunks through context
    assembly, so paying for whole chunks twice buys nothing. ``None`` is the
    explicit "full" size (D-035c): no preview is cut at all, rather than a
    number that has to track the longest chunk."""

    open_result_chars: int = 1600
    """`open` and `read` are deliberate drill-downs, so they show more."""

    response_format: Literal["json_schema", "json_object"] = "json_schema"
    """What structured requests send as ``response_format``. The API honours a
    full JSON schema; a server that does not (llama.cpp behind some templates)
    gets ``json_object`` plus the schema described in the prompt, with the same
    validation and repair on the way back. Recorded with every run so a fallback
    is a stated configuration, never a silent degrade (D-035c)."""

    page_cap: int = 4
    page_read_top_k: int = 40

    max_attempts: int = 4
    retry_base_seconds: float = 1.0
    request_timeout_ms: int = 180_000

    prices: dict[str, ModelPrice] = Field(default_factory=lambda: dict(PRICES))

    def cost_usd(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """USD for one call. An unpriced model costs 0 and says so once (D-035c).

        A local-server id containing the Ministral 3 14B marker prices at the
        published Ministral 3 API rate applied to a local run; the token counts
        are recorded either way so a price added later can be applied to a run
        that already happened. A genuinely unpriced model logs once per model
        per process rather than per call.
        """
        cost = price_of(model, prompt_tokens, completion_tokens, self.prices)
        if cost is None:
            if model not in _WARNED_UNPRICED:
                _WARNED_UNPRICED.add(model)
                logger.warning("No price for model, cost recorded as zero", model=model)
            return 0.0
        return cost


_WARNED_UNPRICED: set[str] = set()


def known_serving_model(model: str) -> bool:
    """Whether a serving entrypoint should accept this model id.

    The Mistral API path serves priced models only (D-017); a local chat server
    (D-035c) reports aliased Ministral 3 14B ids, which are accepted and priced
    at the published API rate, and any other id when a server is configured,
    costing 0 with one warning per model per process. The check lives at the
    entrypoints rather than in ``AnswerConfig`` because it is a question about
    what this deployment serves, not about what a run may record.
    """
    return model in PRICES or aliased_price(model) is not None or chat_server_url() is not None


__all__ = [
    "DEFAULT_VARIANT",
    "LOCAL_MINISTRAL_3_14B_MARKER",
    "MINISTRAL_3_14B",
    "LOCAL_MINISTRAL_3_14B",
    "MINISTRAL_3_8B",
    "MISTRAL_EMBED",
    "MISTRAL_MEDIUM_3_5",
    "MISTRAL_SMALL_4",
    "PRICES",
    "AnswerConfig",
    "ModelPrice",
    "aliased_price",
    "known_serving_model",
    "price_of",
]
