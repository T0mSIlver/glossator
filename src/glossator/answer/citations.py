"""The answer contract (D-027) and the check that makes it worth something.

A citation that only names a source cannot be verified without another model. A
citation that carries a quote can be checked in code: normalize the whitespace,
look for the span in the chunk it claims to come from, and drop it when it is not
there. That check is the project's citation-correctness number, so it lives next
to the types rather than in a strategy.
"""

import re

import structlog
from pydantic import BaseModel, ConfigDict

from glossator.answer.context import AssembledContext, Source
from glossator.answer.llm import TokenUsage

logger = structlog.get_logger(__name__)

MARKER = re.compile(r"\[([1-9]\d{0,2})\]")
"""Sources are numbered from 1, so `[0]` is never a marker -- and answers about an
API are full of `choices[0]`."""

_CODE = re.compile(r"```.*?```|~~~.*?~~~|`[^`\n]*`", re.DOTALL)
_WHITESPACE = re.compile(r"\s+")
MIN_QUOTE_CHARS = 8
"""A quote shorter than this verifies against almost any chunk, so it is not
evidence that the model read the source."""


class Citation(BaseModel):
    """One `[n]` marker, resolved to a source and a span that was checked."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    n: int
    url: str
    anchor: str | None = None
    chunk_id: str | None = None
    quote: str
    verified: bool
    reason: str | None = None
    """Why an unverified citation failed, for the trace."""

    @property
    def citation_url(self) -> str:
        return f"{self.url}#{self.anchor}" if self.anchor else self.url


class TraceEvent(BaseModel):
    """One retrieval or tool step, with what it was asked and what it returned."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    step: int
    kind: str
    name: str
    round: int = 0
    arguments: dict[str, object] = {}
    result_ids: list[str] = []
    note: str | None = None


class TracedSource(BaseModel):
    """A numbered source as the model saw it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    n: int
    citation_url: str
    heading_path: list[str]
    chunk_ids: list[str]
    tokens: int


class Trace(BaseModel):
    """Everything the run did, in the order it did it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    strategy: str
    variant: str
    prompt_version: str
    rounds: int = 0
    events: list[TraceEvent] = []
    sources: list[TracedSource] = []
    context_tokens: int = 0
    dropped_chunk_ids: list[str] = []
    unverified_citations: list[Citation] = []
    unmatched_markers: list[int] = []
    """Markers in the answer text with no citation entry behind them."""

    def summary(self) -> str:
        parts = [
            f"{self.strategy} on {self.variant} ({self.prompt_version})",
            f"{len(self.events)} steps in {self.rounds} round(s)",
            f"{len(self.sources)} sources, {self.context_tokens} context tokens",
        ]
        if self.dropped_chunk_ids:
            parts.append(f"{len(self.dropped_chunk_ids)} chunks over budget")
        if self.unverified_citations:
            parts.append(f"{len(self.unverified_citations)} citations rejected")
        if self.unmatched_markers:
            parts.append(f"markers without citations: {self.unmatched_markers}")
        return "; ".join(parts)


class Answer(BaseModel):
    """What every strategy returns (D-027)."""

    model_config = ConfigDict(frozen=True, extra="forbid", protected_namespaces=())

    question: str
    strategy: str
    model: str
    answer_markdown: str
    citations: list[Citation] = []
    insufficient_evidence: bool = False
    trace: Trace
    usage: TokenUsage = TokenUsage()
    latency_ms: float = 0.0
    cost_usd: float = 0.0


def markers(text: str) -> list[int]:
    """The `[n]` markers in the prose, in order, without duplicates.

    Code is excluded: an answer that shows `messages[1]` is not citing source 1.
    """
    seen: list[int] = []
    for match in MARKER.finditer(_CODE.sub(" ", text)):
        n = int(match.group(1))
        if n not in seen:
            seen.append(n)
    return seen


def normalize(text: str) -> str:
    """Collapse whitespace, so a re-wrapped quote still matches its source."""
    return _WHITESPACE.sub(" ", text).strip()


def _normalized_with_map(text: str) -> tuple[str, list[int]]:
    """The normalized text plus, per normalized character, its original index."""
    out: list[str] = []
    positions: list[int] = []
    pending_space = False
    for index, char in enumerate(text):
        if char.isspace():
            pending_space = bool(out)
            continue
        if pending_space:
            out.append(" ")
            positions.append(index)
            pending_space = False
        out.append(char)
        positions.append(index)
    return "".join(out), positions


def verify(quote: str, source: Source) -> tuple[bool, str | None, str | None]:
    """Check a quote against a source. Returns (verified, chunk_id, reason).

    The source content is the merged passage, so a quote that runs across the
    boundary between two chunks of the same page verifies here even though it is
    in neither chunk on its own.
    """
    needle = normalize(quote)
    if len(needle) < MIN_QUOTE_CHARS:
        return False, None, f"quote shorter than {MIN_QUOTE_CHARS} characters"
    haystack, positions = _normalized_with_map(source.content)
    found = haystack.find(needle)
    if found < 0:
        return False, None, "quote is not in the cited source"
    return True, source.chunk_id_at(positions[found]), None


def resolve(
    raw_citations: list[tuple[int, str]],
    context: AssembledContext,
) -> tuple[list[Citation], list[Citation]]:
    """Map the model's `(n, quote)` pairs onto sources and verify each one.

    Returns the verified citations and the rejected ones. Markers stay in the
    answer text either way: renumbering would invalidate the quotes the model
    wrote them for, and a marker whose citation was dropped is visible in the
    trace as a rejection.
    """
    verified: list[Citation] = []
    rejected: list[Citation] = []
    for n, quote in raw_citations:
        source = context.by_number(n)
        if source is None:
            rejected.append(
                Citation(
                    n=n,
                    url="",
                    quote=quote,
                    verified=False,
                    reason=f"no source numbered {n}",
                )
            )
            continue
        ok, chunk_id, reason = verify(quote, source)
        citation = Citation(
            n=n,
            url=source.url,
            anchor=source.anchor,
            chunk_id=chunk_id or source.chunk_ids[0],
            quote=quote,
            verified=ok,
            reason=reason,
        )
        (verified if ok else rejected).append(citation)
    if rejected:
        logger.info("Citations rejected", count=len(rejected), verified=len(verified))
    return verified, rejected


def unmatched(text: str, citations: list[Citation]) -> list[int]:
    """Markers in the text that no citation, verified or not, accounts for."""
    cited = {citation.n for citation in citations}
    return [n for n in markers(text) if n not in cited]


__all__ = [
    "MARKER",
    "MIN_QUOTE_CHARS",
    "Answer",
    "Citation",
    "Trace",
    "TraceEvent",
    "TracedSource",
    "markers",
    "normalize",
    "resolve",
    "unmatched",
    "verify",
]
