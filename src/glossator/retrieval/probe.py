"""Check embedding semantics and compatibility with vectors stored in Vespa.

Shape checks cannot detect random weights or a model swapped after indexing, so
the probe tests known semantic pairs and re-embeds one stored chunk (D-031).
"""

import math
from dataclasses import dataclass
from typing import Any

import structlog
from mistralai.client import Mistral
from mistralai.search.toolkit.embedding import Embedder, MistralEmbedder
from mistralai.search.toolkit.plugins.vespa.search.query import VespaSearchQuery
from mistralai.search.toolkit.search import SearchResultChunk

from glossator.clients import embedding_client
from glossator.index import get_index, get_variant
from glossator.index.variants import IndexVariant
from glossator.retrieval.context import restrict_to
from glossator.retrieval.engine import as_navigable

logger = structlog.get_logger(__name__)

# Measured 2026-09-09 on the pairs below against mistral-embed (1024 dimensions)
# and mistral-embed-dim128-2510 (128). Each threshold sits under the worst number
# either model produced, with enough room that noise does not fail an honest model
# and not so much that a model with random weights would pass.
MIN_RELATED_SIMILARITY = 0.55
"""Lowest cosine a question may have with the passage that answers it.
Measured worst case: 0.7549 at 1024 dimensions, 0.6662 at 128."""

MIN_SEPARATION = 0.05
"""How far the right passage must beat every other passage in the set. This is the
check that catches random weights: untrained embeddings put every text at roughly
the same distance from every other, so the separation collapses to zero while the
raw similarity stays high. Measured worst case: 0.0951 at 1024 dimensions, 0.1324
at 128."""

MIN_ROUND_TRIP_SIMILARITY = 0.999
"""How close a re-embedded chunk must be to its stored vector. Measured: 0.99997
at 1024 dimensions, 0.99999 at 128 -- not exactly 1.0 because Vespa stores the
tensor as float32 while the API returns full precision."""

PROBE_PAIRS: tuple[tuple[str, str], ...] = (
    (
        "how do I stream a chat completion",
        "Streaming returns server-sent events as the model produces them. Call "
        "client.chat.stream instead of client.chat.complete; every streamed chunk has "
        "the same shape as a non-streamed choice, except that the content arrives on "
        "delta instead of message.",
    ),
    (
        "what does tool_choice control",
        "The tool_choice field controls how freely the model may call tools: auto lets "
        "the model decide, any forces it to call one of the supplied tools, none "
        "forbids tool calls, and a named tool forces that specific one.",
    ),
    (
        "how many dimensions does mistral-embed return",
        "mistral-embed returns 1024-dimensional vectors and accepts up to 8192 input "
        "tokens. Reduced-dimension variants return 256 or 128 dimensions for a smaller "
        "index at some cost in quality.",
    ),
    (
        "which status codes are worth retrying",
        "Only 429 and 5xx responses are worth retrying. A 429 means the request was "
        "rate limited, so back off exponentially; a 422 means the values were invalid "
        "and retrying produces the same 422.",
    ),
    (
        "what flags does vLLM need to serve a Mistral model correctly",
        "Start vLLM with --tokenizer-mode mistral, --config-format mistral and "
        "--load-format mistral. Without them vLLM applies a HuggingFace chat template "
        "that does not match the model's own tokenizer and the answers get worse.",
    ),
)

UNRELATED_PASSAGES: tuple[str, ...] = (
    "Braise the shin in red wine with a bouquet garni for three hours, then reduce the "
    "cooking liquid until it coats the back of a spoon.",
    "Feline hyperthyroidism is usually caused by a benign adenoma of the thyroid gland; "
    "treatment options are radioiodine, thyroidectomy or lifelong methimazole.",
)


class EmbeddingProbeError(RuntimeError):
    """The embedding model or the stored vectors cannot be trusted to serve."""


@dataclass(frozen=True, slots=True)
class ProbeResult:
    """What the probe measured, whether or not it passed."""

    variant: str
    model: str
    dimensions: int
    lowest_related: float
    lowest_separation: float
    round_trip: float | None
    """``None`` when the index held no chunk to compare against, which is the
    normal state of an empty index before its first ingest."""

    failures: tuple[str, ...] = ()

    @property
    def passed(self) -> bool:
        return not self.failures

    def as_dict(self) -> dict[str, Any]:
        return {
            "variant": self.variant,
            "model": self.model,
            "dimensions": self.dimensions,
            "lowest_related": round(self.lowest_related, 4),
            "lowest_separation": round(self.lowest_separation, 4),
            "round_trip": None if self.round_trip is None else round(self.round_trip, 6),
            "failures": list(self.failures),
        }

    def summary(self) -> str:
        round_trip = (
            "not checked (index empty)" if self.round_trip is None else f"{self.round_trip:.6f}"
        )
        return (
            f"{self.variant} on {self.model} ({self.dimensions}d): "
            f"lowest related similarity {self.lowest_related:.4f} "
            f"(floor {MIN_RELATED_SIMILARITY}), smallest separation "
            f"{self.lowest_separation:.4f} (floor {MIN_SEPARATION}), "
            f"stored-vector round trip {round_trip}"
        )


async def probe_embedding(
    variant: IndexVariant | str,
    embedder: Embedder | None = None,
    client: Mistral | None = None,
) -> ProbeResult:
    """Run the probe and raise ``EmbeddingProbeError`` if the model fails it."""
    resolved = get_variant(variant) if isinstance(variant, str) else variant
    model = resolved.embedding_model_name
    embedder = embedder or MistralEmbedder(client=client or embedding_client(), model_name=model)

    questions = [question for question, _passage in PROBE_PAIRS]
    passages = [passage for _question, passage in PROBE_PAIRS] + list(UNRELATED_PASSAGES)
    # One request for everything: the probe runs before every ingest and once per
    # search process, and the free tier is rate limited by request, not by token.
    vectors = (await embedder.embed(questions + passages)).embeddings
    question_vectors = vectors[: len(questions)]
    passage_vectors = vectors[len(questions) :]

    failures: list[str] = []
    lowest_related = 1.0
    lowest_separation = 2.0
    for index, (question, question_vector) in enumerate(
        zip(questions, question_vectors, strict=True)
    ):
        scores = [cosine(question_vector, passage) for passage in passage_vectors]
        related = scores[index]
        best_other = max(score for position, score in enumerate(scores) if position != index)
        separation = related - best_other
        lowest_related = min(lowest_related, related)
        lowest_separation = min(lowest_separation, separation)
        if scores.index(max(scores)) != index:
            failures.append(
                f"{question!r} is closer to another probe passage "
                f"({max(scores):.4f}) than to its own ({related:.4f})"
            )
        elif related < MIN_RELATED_SIMILARITY:
            failures.append(
                f"{question!r} matches its own passage at only {related:.4f} "
                f"(floor {MIN_RELATED_SIMILARITY})"
            )
        elif separation < MIN_SEPARATION:
            failures.append(
                f"{question!r} beats the next passage by only {separation:.4f} "
                f"(floor {MIN_SEPARATION})"
            )

    round_trip = await _round_trip(resolved, embedder)
    if round_trip is not None and round_trip < MIN_ROUND_TRIP_SIMILARITY:
        failures.append(
            f"a stored chunk re-embeds to {round_trip:.6f} of its indexed vector "
            f"(floor {MIN_ROUND_TRIP_SIMILARITY}); the index was built by a different model"
        )

    result = ProbeResult(
        variant=resolved.name,
        model=model,
        dimensions=resolved.embedding_dimensions,
        lowest_related=lowest_related,
        lowest_separation=lowest_separation,
        round_trip=round_trip,
        failures=tuple(failures),
    )
    if not result.passed:
        raise EmbeddingProbeError(
            f"embedding probe failed for variant {resolved.name!r} on model {model!r}: "
            + "; ".join(result.failures)
        )
    logger.info("Embedding probe passed", **result.as_dict())
    return result


async def _round_trip(variant: IndexVariant, embedder: Embedder) -> float | None:
    """Cosine between one stored chunk's vector and a fresh embedding of its text."""
    context = restrict_to(variant.schema_name)
    index = get_index(variant)
    # Any indexed chunk will do, so the cheapest way to name one is to ask for a
    # single hit; an empty index returns none and the check is skipped. The query
    # vector is a unit basis vector rather than zeros: cosine against an all-zero
    # query is NaN, which Vespa returns as a null relevance the parser rejects.
    probe = VespaSearchQuery(
        query="the",
        embedding=[0.0] * (variant.embedding_dimensions - 1) + [1.0],
        top_k=1,
    )
    hits = await index.search(query=probe, context=context)
    if not hits:
        return None
    stored = await as_navigable(index).get_chunk(hits[0].chunk.id, context=context)
    if stored is None:
        return None
    vector = _stored_vector(stored.chunk)
    if vector is None:
        logger.warning(
            "Stored chunk carries no embedding; skipping the round trip",
            variant=variant.name,
            chunk_id=stored.chunk.id,
        )
        return None
    fresh = await embedder.embed_query(stored.chunk.content)
    return cosine(vector, fresh)


def _stored_vector(chunk: SearchResultChunk) -> list[float] | None:
    """The chunk's indexed embedding, as Vespa's document API returns it.

    ``SearchResultChunk`` allows extra fields, and ``get_chunk`` promotes every
    schema field onto it, so the tensor arrives as ``{"type": ..., "values": [...]}``.
    """
    raw = (chunk.model_extra or {}).get("content_embedding")
    if isinstance(raw, dict):
        raw = raw.get("values")
    if isinstance(raw, list) and raw and all(isinstance(value, int | float) for value in raw):
        return [float(value) for value in raw]
    return None


async def check_embedding_once(variant: str) -> ProbeResult:
    """Probe this variant once per process, and reuse the answer after that.

    A command that searches several times, or a server that answers many
    requests, should pay for the probe on the way up and not on every query. The
    result is cached rather than the coroutine, so a failure raises every time it
    is asked rather than being swallowed by an already-awaited future.
    """
    cached = _PROBED.get(variant)
    if cached is None:
        cached = await probe_embedding(variant)
        _PROBED[variant] = cached
    return cached


_PROBED: dict[str, ProbeResult] = {}


def cosine(left: list[float], right: list[float]) -> float:
    """Cosine similarity. Written out because Mistral's embeddings are not unit
    length, so a dot product is not the same number (the embeddings page says so)."""
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    norm = math.sqrt(sum(a * a for a in left)) * math.sqrt(sum(b * b for b in right))
    return dot / norm if norm else 0.0


__all__ = [
    "MIN_RELATED_SIMILARITY",
    "MIN_ROUND_TRIP_SIMILARITY",
    "MIN_SEPARATION",
    "PROBE_PAIRS",
    "UNRELATED_PASSAGES",
    "EmbeddingProbeError",
    "ProbeResult",
    "check_embedding_once",
    "cosine",
    "probe_embedding",
]
