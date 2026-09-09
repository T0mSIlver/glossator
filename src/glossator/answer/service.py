"""The one call the API, the MCP server and the eval grid all make.

Everything above this line is a question, a strategy name and a variant;
everything below is retrieval, generation and verification. Keeping the seam here
means a caller never has to build an engine, a client or a config to ask a
question, and an evaluation varies exactly the arguments a user could vary.
"""

import structlog

from glossator.answer.citations import Answer
from glossator.answer.config import DEFAULT_VARIANT, AnswerConfig
from glossator.answer.docs_index import DocsIndex
from glossator.answer.generation import Strategy
from glossator.answer.llm import LLM, CallRecorder, MistralLLM
from glossator.answer.outline import answer as outline_answer
from glossator.answer.search_loop import answer as search_loop_answer
from glossator.answer.single_pass import answer as single_pass_answer
from glossator.clients import chat_client
from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.engine import SearchEngine

logger = structlog.get_logger(__name__)

STRATEGIES: dict[str, Strategy] = {
    "single_pass": single_pass_answer,
    "search_loop": search_loop_answer,
    "outline": outline_answer,
}


async def ask(
    question: str,
    *,
    strategy: str = "single_pass",
    variant: str = DEFAULT_VARIANT,
    model: str | None = None,
    recorder: CallRecorder | None = None,
    config: AnswerConfig | None = None,
    engine: DocsIndex | None = None,
    llm: LLM | None = None,
) -> Answer:
    """Answer one question. ``engine`` and ``llm`` are injectable so a batch run
    builds the index client once instead of once per question.

    ``model`` names the generation model, which an evaluation varies per run and
    reports as a column of every table (D-017a). A model with no price in the
    table costs zero and says so once per process (D-035c): a local server
    reports ids the price list has never seen, and refusing them would make
    every local-server run impossible.
    """
    if strategy not in STRATEGIES:
        raise ValueError(f"unknown strategy {strategy!r}; available: {sorted(STRATEGIES)}")
    if llm is not None and recorder is not None:
        # Silently dropping the recorder here would leave an eval run -- the one
        # caller that injects a shared client -- with no record at all (D-023).
        raise ValueError(
            "pass either llm or recorder, not both: an injected llm already owns "
            "its recorder, so this one would be ignored"
        )
    settings = config or AnswerConfig()
    if model is not None and model != settings.model:
        settings = AnswerConfig.model_validate({**settings.model_dump(), "model": model})
    index = engine or SearchEngine(RetrievalConfig.shipped(variant=variant, top_k=settings.top_k))
    generator = llm or MistralLLM(settings, client=chat_client(), recorder=recorder)

    logger.info("Ask", strategy=strategy, variant=variant, question=question)
    return await STRATEGIES[strategy](question, engine=index, llm=generator, config=settings)


__all__ = ["STRATEGIES", "ask"]
