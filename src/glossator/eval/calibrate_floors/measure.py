"""One query's cosine similarities at the recorded depths, through the live index."""

from __future__ import annotations

import structlog

from glossator.eval.calibrate_floors.models import DEPTHS, TOP_K, QuerySimilarities
from glossator.retrieval.engine import SearchEngine

logger = structlog.get_logger(__name__)


async def measure(
    engine: SearchEngine,
    query: str,
    population: str,
    *,
    question_id: str | None = None,
    question_type: str | None = None,
) -> QuerySimilarities:
    """One query's cosine similarities at the recorded depths.

    Searches the way serving searches -- hybrid, ranked by the schema's weights --
    and then reads the cosine of exactly those hits, so the numbers describe the
    result set a floor would be filtering rather than a different one.
    """
    try:
        hits = await engine.search(query, top_k=TOP_K)
        similarities = await engine.retriever.cosine_similarities(
            await engine.retriever.embed_query(query, context=engine.context),
            [hit.chunk_id for hit in hits],
            context=engine.context,
        )
    except Exception as error:  # noqa: BLE001 - one query's failure is recorded, not fatal
        logger.warning("Similarity read-out failed", query=query, error=str(error))
        return QuerySimilarities(
            query=query,
            population=population,
            question_id=question_id,
            question_type=question_type,
            error=str(error),
        )

    ranked = sorted(
        (similarities[hit.chunk_id] for hit in hits if hit.chunk_id in similarities), reverse=True
    )
    vocabulary = engine.vocabulary
    return QuerySimilarities(
        query=query,
        population=population,
        question_id=question_id,
        question_type=question_type,
        lexical_footing=vocabulary.has_footing(query) if vocabulary else None,
        hits=len(ranked),
        at_depth={
            str(depth): (ranked[depth - 1] if len(ranked) >= depth else None) for depth in DEPTHS
        },
    )
