"""The step every strategy ends with: hits in, a verified answer out.

The three strategies differ only in how they find chunks. Once they have them,
assembly, the grounded prompt, the structured call and the citation check are the
same code, so a difference in an evaluation is a difference in retrieval and not
in how the answer was written.
"""

import time
from dataclasses import dataclass, field
from typing import Protocol

import structlog
from pydantic import BaseModel, ConfigDict, Field

from glossator.answer.citations import (
    Answer,
    Citation,
    Trace,
    TracedSource,
    TraceEvent,
    resolve,
    unmatched,
)
from glossator.answer.config import AnswerConfig
from glossator.answer.context import AssembledContext, assemble
from glossator.answer.docs_index import DocsIndex
from glossator.answer.llm import LLM, Completion, TokenUsage
from glossator.answer.prompts import (
    GROUNDED_ANSWER_SYSTEM,
    GROUNDED_ANSWER_USER,
    GROUNDED_ANSWER_VERSION,
)
from glossator.retrieval.engine import Hit

logger = structlog.get_logger(__name__)


class GeneratedCitation(BaseModel):
    """A citation as the model writes it, before anything is checked."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    n: int
    quote: str


class GeneratedAnswer(BaseModel):
    """The structured output the grounded prompt asks for (D-027)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    answer_markdown: str
    citations: list[GeneratedCitation] = Field(default_factory=list)
    insufficient_evidence: bool = False


class Strategy(Protocol):
    """One way of getting from a question to a verified answer."""

    async def __call__(
        self,
        question: str,
        *,
        engine: DocsIndex,
        llm: LLM,
        config: AnswerConfig,
    ) -> Answer: ...


@dataclass(slots=True)
class AnswerRun:
    """A strategy in progress: its clock, its trace and its spend so far."""

    strategy: str
    variant: str
    started: float = field(default_factory=time.perf_counter)
    events: list[TraceEvent] = field(default_factory=list)
    completions: list[Completion] = field(default_factory=list)
    rounds: int = 0

    def event(
        self,
        kind: str,
        name: str,
        *,
        arguments: dict[str, object] | None = None,
        result_ids: list[str] | None = None,
        note: str | None = None,
    ) -> None:
        self.events.append(
            TraceEvent(
                step=len(self.events) + 1,
                kind=kind,
                name=name,
                round=self.rounds,
                arguments=arguments or {},
                result_ids=result_ids or [],
                note=note,
            )
        )

    def spent(self, completion: Completion) -> None:
        self.completions.append(completion)

    @property
    def usage(self) -> TokenUsage:
        return sum((completion.usage for completion in self.completions), TokenUsage())

    @property
    def cost_usd(self) -> float:
        return sum(completion.cost_usd for completion in self.completions)

    @property
    def latency_ms(self) -> float:
        return (time.perf_counter() - self.started) * 1000

    async def finish(
        self,
        question: str,
        hits: list[Hit],
        *,
        llm: LLM,
        config: AnswerConfig,
        no_sources_message: str | None = None,
    ) -> Answer:
        """Assemble, generate, verify: the common tail of every strategy.

        ``no_sources_message`` is what to say when nothing was gathered. A
        strategy that failed before it reached the index passes its own reason:
        "the documentation does not cover this" and "the step that picks pages
        broke" are different answers, and reporting the second as the first
        turns a bug into a refusal in the eval's refusal rate (D-016).
        """
        context = assemble(hits, token_budget=config.context_token_budget)
        self.event(
            "assembly",
            "context",
            arguments={"tokens": context.tokens, "sources": len(context.sources)},
            result_ids=[chunk_id for source in context.sources for chunk_id in source.chunk_ids],
        )
        if not context.sources:
            return self._answer(
                question,
                config,
                context,
                markdown=no_sources_message
                or "The documentation index returned nothing for this question.",
                verified=[],
                rejected=[],
                insufficient=True,
            )

        completion = await llm.complete(
            [
                {"role": "system", "content": GROUNDED_ANSWER_SYSTEM},
                {
                    "role": "user",
                    "content": GROUNDED_ANSWER_USER.format(question=question, context=context.text),
                },
            ],
            response_schema=GeneratedAnswer,
            purpose=f"{self.strategy}:grounded_answer",
        )
        self.spent(completion)

        generated = completion.parsed
        if not isinstance(generated, GeneratedAnswer):
            # Both the first call and its repair failed the schema. The raw text
            # is still the model's answer, so it is returned uncited rather than
            # thrown away, and the run records why nothing verified.
            logger.warning("Grounded answer did not parse", strategy=self.strategy)
            self.event("generation", "unparsed", note=completion.finish_reason)
            return self._answer(
                question,
                config,
                context,
                markdown=completion.text,
                verified=[],
                rejected=[],
                insufficient=True,
            )

        verified, rejected = resolve(
            [(citation.n, citation.quote) for citation in generated.citations],
            context,
            min_quote_chars=config.min_quote_chars,
        )
        return self._answer(
            question,
            config,
            context,
            markdown=generated.answer_markdown,
            verified=verified,
            rejected=rejected,
            insufficient=generated.insufficient_evidence or not verified,
        )

    def _answer(
        self,
        question: str,
        config: AnswerConfig,
        context: AssembledContext,
        *,
        markdown: str,
        verified: list[Citation],
        rejected: list[Citation],
        insufficient: bool,
    ) -> Answer:
        trace = Trace(
            strategy=self.strategy,
            variant=self.variant,
            prompt_version=GROUNDED_ANSWER_VERSION,
            rounds=self.rounds,
            events=self.events,
            sources=[
                TracedSource(
                    n=source.n,
                    citation_url=source.citation_url,
                    heading_path=list(source.heading_path),
                    chunk_ids=list(source.chunk_ids),
                    tokens=source.tokens,
                    score=source.score,
                )
                for source in context.sources
            ],
            context_tokens=context.tokens,
            context_text=context.text,
            dropped_chunk_ids=list(context.dropped_chunk_ids),
            unverified_citations=rejected,
            unmatched_markers=unmatched(markdown, verified + rejected),
        )
        return Answer(
            question=question,
            strategy=self.strategy,
            model=config.model,
            answer_markdown=markdown,
            citations=verified,
            insufficient_evidence=insufficient,
            trace=trace,
            usage=self.usage,
            latency_ms=self.latency_ms,
            cost_usd=self.cost_usd,
        )


__all__ = ["AnswerRun", "GeneratedAnswer", "GeneratedCitation", "Strategy"]
