"""One model call that reads every candidate at once and puts them in order.

Hybrid retrieval decides relevance from a lexical overlap and a vector distance,
neither of which can tell that a section titled "Streaming" is about server-sent
events for the chat API and not about streaming a file upload. A model reading
twenty candidates side by side can, and it costs one round trip: the toolkit's own
``LLMReRanker`` scores each candidate in its own sequential call and never writes
the score back onto the result (D-015).

Listwise, not pointwise, for the same reason a person ranks a shortlist rather
than grading each entry blind: the comparison is the judgement. The model returns
positions, not scores, because a model's absolute score is not comparable across
queries while its ordering is.
"""

import time
from dataclasses import dataclass, replace
from functools import lru_cache
from typing import Any

import structlog
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
from pydantic import BaseModel, ConfigDict, Field

from glossator.answer.config import PRICES, AnswerConfig
from glossator.answer.llm import LLM, Completion, TokenUsage
from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.engine import Hit

logger = structlog.get_logger(__name__)

RERANK_PROMPT_VERSION = "listwise-rerank/v1"

CANDIDATE_TOKEN_BUDGET = 300
"""How much of a candidate the model reads. Long enough for a section's opening
claim, short enough that twenty candidates fit in a prompt a small model handles:
twenty times this plus headings lands near 7k prompt tokens."""

REASONED_POSITIONS = 5
"""How many of the ranked positions carry a reason. A reason per candidate would
double the completion for positions nobody reads."""

RERANK_MAX_TOKENS = 900
"""Enough for twenty positions and five short reasons. A ranking cut off by the
token limit is a malformed response, which falls back rather than raising."""

SYSTEM_PROMPT = """\
You put search results in order of how well they answer a question.

You are given a question and numbered candidate passages from Mistral's \
documentation. Return every candidate number exactly once, best first.

Judge each candidate on whether its own text answers the question asked. A \
passage that names the topic but answers a different question about it ranks \
below one that answers this question. A passage that is only a heading, a link \
list or a table of contents ranks last. Ignore the order the candidates arrive \
in; it is the order you are being asked to correct.

Return JSON with ranking: a list of objects, each with index (a candidate \
number) and reason. Give a reason of at most fifteen words for the first {reasoned} \
entries and an empty reason for the rest. Include every candidate number once and \
invent none.
"""

USER_PROMPT = """\
Question: {question}

Candidates:
{candidates}
"""


class RankedCandidate(BaseModel):
    """One position in the model's ranking."""

    model_config = ConfigDict(extra="forbid")

    index: int
    reason: str = ""


class Ranking(BaseModel):
    """The reranker's structured response."""

    model_config = ConfigDict(extra="forbid")

    ranking: list[RankedCandidate] = Field(default_factory=list)


@dataclass(frozen=True, slots=True)
class RerankTrace:
    """What the reranker did to one result set, whether or not it worked."""

    model: str
    candidates: int
    applied: bool
    reasons: tuple[tuple[str, str], ...] = ()
    """``(chunk_id, reason)`` for the positions the model explained."""

    usage: TokenUsage = TokenUsage()
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    error: str | None = None
    """Why the retrieval order was kept. ``None`` when the ranking was applied."""

    def as_dict(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "candidates": self.candidates,
            "applied": self.applied,
            "reasons": [
                {"chunk_id": chunk_id, "reason": reason} for chunk_id, reason in self.reasons
            ],
            "usage": self.usage.model_dump(mode="json"),
            "cost_usd": round(self.cost_usd, 8),
            "latency_ms": round(self.latency_ms, 3),
            "error": self.error,
        }


@dataclass(frozen=True, slots=True)
class RerankResult:
    """The reordered hits and the record of how they got that way."""

    hits: list[Hit]
    trace: RerankTrace


class ListwiseReranker:
    """Reorders one result set per model call."""

    def __init__(self, config: RetrievalConfig, llm: LLM) -> None:
        if config.rerank_model not in PRICES:
            raise ValueError(
                f"no price for rerank model {config.rerank_model!r}; "
                f"priced models: {sorted(PRICES)} (add it to glossator.answer.config, D-017)"
            )
        self.config = config
        self.llm = llm

    async def rerank(self, query: str, hits: list[Hit]) -> RerankResult:
        """Order ``hits`` by relevance to ``query``.

        Never raises on the model's behalf: a refusal, a truncated response, a
        ranking that names a candidate twice or invents one leaves the retrieval
        order in place and says why in the trace. Retrieval order is a usable
        answer; an exception on the serving path is not.
        """
        candidates = hits[: self.config.rerank_candidates]
        trace = RerankTrace(
            model=self.config.rerank_model, candidates=len(candidates), applied=False
        )
        if len(candidates) < 2:
            return RerankResult(hits=_unranked(candidates), trace=trace)

        started = time.perf_counter()
        try:
            completion = await self.llm.complete(
                [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT.format(reasoned=REASONED_POSITIONS),
                    },
                    {
                        "role": "user",
                        "content": USER_PROMPT.format(
                            question=query, candidates=render_candidates(candidates)
                        ),
                    },
                ],
                model=self.config.rerank_model,
                temperature=self.config.rerank_temperature,
                max_tokens=RERANK_MAX_TOKENS,
                response_schema=Ranking,
                purpose="rerank",
            )
        except Exception as error:  # noqa: BLE001 - a failed rerank is a kept order
            latency_ms = (time.perf_counter() - started) * 1000
            logger.warning("Rerank call failed; keeping retrieval order", error=str(error))
            return RerankResult(
                hits=_unranked(candidates),
                trace=replace(trace, latency_ms=latency_ms, error=str(error)),
            )

        trace = replace(
            trace,
            usage=completion.usage,
            cost_usd=completion.cost_usd,
            latency_ms=(time.perf_counter() - started) * 1000,
        )
        order, reason = _order_from(completion, len(candidates))
        if order is None:
            logger.warning("Malformed rerank response; keeping retrieval order", reason=reason)
            return RerankResult(
                hits=_unranked(candidates),
                trace=replace(trace, error=reason),
            )

        ranked = _scored(candidates, order)
        reasons = _reasons(completion, candidates, order)
        logger.info(
            "Reranked",
            candidates=len(candidates),
            moved=sum(1 for position, index in enumerate(order) if position != index),
            cost_usd=round(completion.cost_usd, 6),
        )
        return RerankResult(hits=ranked, trace=replace(trace, applied=True, reasons=reasons))


def render_candidates(hits: list[Hit]) -> str:
    """The candidate block: one numbered line per hit, its citation and its opening."""
    return "\n\n".join(
        f"[{number}] {hit.citation_url} | {hit.heading_line or hit.page_title}\n"
        f"{truncate_tokens(hit.content, CANDIDATE_TOKEN_BUDGET)}"
        for number, hit in enumerate(hits, start=1)
    )


def truncate_tokens(text: str, budget: int) -> str:
    """The first ``budget`` tokens of ``text``, marked when anything was cut.

    Tokens rather than characters because the budget is a prompt cost, and the
    same tokenizer the chunker and the embedder use, so the number in the code is
    the number that is billed.
    """
    tokenizer = _tokenizer().instruct_tokenizer.tokenizer
    ids = tokenizer.encode(text, bos=False, eos=False)
    if len(ids) <= budget:
        return text
    return f"{tokenizer.decode(ids[:budget]).rstrip()} [...]"


@lru_cache(maxsize=1)
def _tokenizer() -> MistralTokenizer[Any, Any, Any, Any, Any]:
    return MistralTokenizer.v1()


def rerank_llm_config(config: RetrievalConfig) -> AnswerConfig:
    """The chat settings one rerank call runs under.

    The reranker borrows the answer layer's client so its calls are recorded and
    costed like any other (D-023); only the model and the temperature come from
    the retrieval configuration.
    """
    return AnswerConfig(
        model=config.rerank_model,
        temperature=config.rerank_temperature,
        max_tokens=RERANK_MAX_TOKENS,
    )


def _order_from(completion: Completion, count: int) -> tuple[list[int] | None, str | None]:
    """The response as a permutation of ``range(count)``, or why it is not one."""
    parsed = completion.parsed
    if not isinstance(parsed, Ranking):
        return None, f"response did not validate as a ranking (finish: {completion.finish_reason})"
    positions = [entry.index - 1 for entry in parsed.ranking]
    out_of_range = sorted({index + 1 for index in positions if not 0 <= index < count})
    if out_of_range:
        return None, f"ranking names candidate(s) that were not offered: {out_of_range}"
    if len(set(positions)) != len(positions):
        return None, "ranking repeats a candidate"
    if len(positions) != count:
        return None, f"ranking covers {len(positions)} of {count} candidates"
    return positions, None


def _unranked(candidates: list[Hit]) -> list[Hit]:
    """Retrieval order, kept. ``rerank_score`` stays unset, which is how a reader
    of the record tells a fallback from a ranking that happened to agree."""
    return [replace(hit, retrieval_score=hit.score) for hit in candidates]


def _scored(candidates: list[Hit], order: list[int]) -> list[Hit]:
    """``candidates`` in ``order``, each carrying both scores.

    ``rerank_score`` is the rank position read as a score -- first of twenty scores
    1.0, last scores 0.05 -- because that is what the ranking says and no more.
    Reading a model's ordinal as a similarity would invent precision it does not
    have. ``retrieval_score`` keeps the number Vespa produced, so a comparison
    between the two orders is still possible after the fact.
    """
    total = len(order)
    return [
        replace(
            candidates[index],
            score=(total - position) / total,
            rerank_score=(total - position) / total,
            retrieval_score=candidates[index].score,
        )
        for position, index in enumerate(order)
    ]


def _reasons(
    completion: Completion, candidates: list[Hit], order: list[int]
) -> tuple[tuple[str, str], ...]:
    parsed = completion.parsed
    if not isinstance(parsed, Ranking):
        return ()
    by_index = {entry.index - 1: entry.reason.strip() for entry in parsed.ranking}
    return tuple(
        (candidates[index].chunk_id, by_index[index])
        for index in order[:REASONED_POSITIONS]
        if by_index.get(index)
    )


__all__ = [
    "CANDIDATE_TOKEN_BUDGET",
    "RERANK_MAX_TOKENS",
    "RERANK_PROMPT_VERSION",
    "REASONED_POSITIONS",
    "SYSTEM_PROMPT",
    "USER_PROMPT",
    "ListwiseReranker",
    "RankedCandidate",
    "Ranking",
    "RerankResult",
    "RerankTrace",
    "render_candidates",
    "rerank_llm_config",
    "truncate_tokens",
]
