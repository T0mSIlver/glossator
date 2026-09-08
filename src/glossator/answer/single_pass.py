"""One retrieval, one generation. The baseline every other strategy has to beat."""

import structlog

from glossator.answer.citations import Answer
from glossator.answer.config import AnswerConfig
from glossator.answer.docs_index import DocsIndex
from glossator.answer.generation import AnswerRun
from glossator.answer.llm import LLM

logger = structlog.get_logger(__name__)

NAME = "single_pass"


async def answer(
    question: str,
    *,
    engine: DocsIndex,
    llm: LLM,
    config: AnswerConfig,
) -> Answer:
    run = AnswerRun(strategy=NAME, variant=engine.config.variant)
    run.rounds = 1
    hits = await engine.search(question, top_k=config.top_k)
    run.event(
        "retrieval",
        "search",
        arguments={"query": question, "top_k": config.top_k},
        result_ids=[hit.chunk_id for hit in hits],
    )
    return await run.finish(question, hits, llm=llm, config=config)


__all__ = ["NAME", "answer"]
