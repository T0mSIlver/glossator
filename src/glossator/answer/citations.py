"""The answer contract (D-027) and the check that makes it worth something.

A citation that only names a source cannot be verified without another model. A
citation that carries a quote can be checked in code: normalize the whitespace,
look for the span in the chunk it claims to come from, and drop it when it is not
there. That check is the project's citation-correctness number, so it lives next
to the types rather than in a strategy.
"""

import re
from collections.abc import Collection

import structlog
from pydantic import BaseModel, ConfigDict

from glossator.answer.context import AssembledContext, Source
from glossator.answer.llm import TokenUsage

logger = structlog.get_logger(__name__)

MARKER = re.compile(r"\[([1-9]\d{0,2})\]")
"""Sources are numbered from 1, so `[0]` is never a marker -- and answers about an
API are full of `choices[0]`."""

_CODE = re.compile(r"```.*?```|~~~.*?~~~|`[^`\n]*`", re.DOTALL)
_FENCES = (re.compile(r"(?m)^[ \t]*```"), re.compile(r"(?m)^[ \t]*~~~"))
_EMPHASIS = frozenset("*_`")
_WHITESPACE = re.compile(r"\s+")
_MARKER_WITH_SPACE = re.compile(r" ?\[([1-9]\d{0,2})\]")

DEFAULT_MIN_QUOTE_CHARS = 8
"""Fallback for callers with no `AnswerConfig` to hand; the live value is
`AnswerConfig.min_quote_chars`."""


class RejectionReason:
    """Why a citation was dropped, as a closed vocabulary.

    The eval reports fabrication separately from cosmetics: a model that invented
    a sentence and a model that dropped a pair of asterisks are different
    failures, and averaging them into one "quote rate" hides both.
    """

    FABRICATED = "quote is not in the cited source"
    TOO_SHORT = "quote is shorter than the minimum"
    NO_SUCH_SOURCE = "no source with that number"

    COSMETIC = frozenset({TOO_SHORT})
    """Reasons that mean the model looked at the source but wrote the quote
    badly, as opposed to not having the sentence at all."""


VERIFIED_AFTER_EMPHASIS = "verified after emphasis normalization"
"""Set on a citation that only matched once `*`, `_` and backticks were stripped
from both sides: the sentence is real, the markdown around it was not copied."""


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
    score: float = 0.0
    """Best retrieval score among the chunks merged into this source. D-023 wants
    the hit scores in the record; joining `calls.jsonl` back to recover them is
    work a reader of `records.jsonl` should not have to do."""


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
    context_text: str = ""
    """The assembled context exactly as the model saw it (D-023)."""

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


def mask_code(text: str) -> str:
    """Blank out code so it cannot be read as prose.

    An odd number of fence markers means the last one was never closed, and
    everything after it is code the model forgot to end. That tail is cut before
    anything else, because treating it as prose is how `choices[0]` becomes a
    citation to source 0 and a weak model forgets a closing fence constantly.
    """
    cut = len(text)
    for fence in _FENCES:
        markers_found = list(fence.finditer(text))
        if len(markers_found) % 2:
            cut = min(cut, markers_found[-1].start())
    return _CODE.sub(" ", text[:cut])


def markers(text: str) -> list[int]:
    """The `[n]` markers in the prose, in order, without duplicates.

    Code is excluded: an answer that shows `messages[1]` is not citing source 1.
    """
    seen: list[int] = []
    for match in MARKER.finditer(mask_code(text)):
        n = int(match.group(1))
        if n not in seen:
            seen.append(n)
    return seen


def strip_markers(text: str, numbers: Collection[int]) -> str:
    """Remove selected prose markers while leaving code spans unchanged."""
    if not numbers:
        return text
    cut = len(text)
    for fence in _FENCES:
        markers_found = list(fence.finditer(text))
        if len(markers_found) % 2:
            cut = min(cut, markers_found[-1].start())
    code_ranges = [(match.start(), match.end()) for match in _CODE.finditer(text[:cut])]
    if cut < len(text):
        code_ranges.append((cut, len(text)))

    def replace(match: re.Match[str]) -> str:
        in_code = any(start <= match.start() < end for start, end in code_ranges)
        return match.group(0) if in_code or int(match.group(1)) not in numbers else ""

    return _MARKER_WITH_SPACE.sub(replace, text)


def normalize(text: str) -> str:
    """Collapse whitespace, so a re-wrapped quote still matches its source."""
    return _WHITESPACE.sub(" ", text).strip()


def _searchable(text: str, *, drop_emphasis: bool = False) -> tuple[str, list[int]]:
    """The comparable form of a text, plus each character's index in the original.

    Keeping the position map is what lets a match be traced back to the chunk it
    landed in even after whitespace (and optionally emphasis) has been removed.
    """
    out: list[str] = []
    positions: list[int] = []
    pending_space = False
    for index, char in enumerate(text):
        if char.isspace():
            pending_space = bool(out)
            continue
        if drop_emphasis and char in _EMPHASIS:
            continue
        if pending_space:
            out.append(" ")
            positions.append(index)
            pending_space = False
        out.append(char)
        positions.append(index)
    return "".join(out), positions


def verify(
    quote: str, source: Source, *, min_quote_chars: int = DEFAULT_MIN_QUOTE_CHARS
) -> tuple[bool, str | None, str | None]:
    """Check a quote against a source. Returns (verified, chunk_id, reason).

    The source content is the merged passage, so a quote that runs across the
    boundary between two chunks of the same page verifies here even though it is
    in neither chunk on its own.

    A quote that fails the literal match gets a second chance with emphasis
    markers and backticks stripped from both sides. The smoke run showed why:
    the docs write "Maximum number of tools per request: **128**", and a model
    that quotes the sentence without the asterisks has read the source
    correctly. That match is still a pass, but it says so in the reason, so an
    eval can separate a clean quote from a re-typed one.
    """
    needle = normalize(quote)
    if len(needle) < min_quote_chars:
        return False, None, RejectionReason.TOO_SHORT
    haystack, positions = _searchable(source.content)
    found = haystack.find(needle)
    if found >= 0:
        return True, source.chunk_id_at(positions[found]), None

    bare_needle, _ = _searchable(quote, drop_emphasis=True)
    if len(bare_needle) >= min_quote_chars:
        bare_haystack, bare_positions = _searchable(source.content, drop_emphasis=True)
        found = bare_haystack.find(bare_needle)
        if found >= 0:
            return True, source.chunk_id_at(bare_positions[found]), VERIFIED_AFTER_EMPHASIS
    return False, None, RejectionReason.FABRICATED


def resolve(
    raw_citations: list[tuple[int, str]],
    context: AssembledContext,
    *,
    min_quote_chars: int = DEFAULT_MIN_QUOTE_CHARS,
) -> tuple[list[Citation], list[Citation]]:
    """Map the model's `(n, quote)` pairs onto sources and verify each one.

    Returns the verified citations and the rejected ones. The generation layer
    removes prose markers that have no verified citation behind them without
    renumbering the markers that remain.
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
                    reason=f"{RejectionReason.NO_SUCH_SOURCE}: {n}",
                )
            )
            continue
        ok, chunk_id, reason = verify(quote, source, min_quote_chars=min_quote_chars)
        citation = Citation(
            n=n,
            # A rejected quote was never located, so naming a chunk for it would
            # put a chunk id in the trace that the quote is not in.
            chunk_id=chunk_id,
            url=source.url,
            anchor=source.anchor,
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


def fabricated(citations: list[Citation]) -> list[Citation]:
    """Rejections where the sentence is not in the source at all."""
    return [c for c in citations if c.reason and c.reason not in RejectionReason.COSMETIC]


def cosmetic(citations: list[Citation]) -> list[Citation]:
    """Rejections where the model wrote the quote badly rather than invented it."""
    return [c for c in citations if c.reason in RejectionReason.COSMETIC]


__all__ = [
    "DEFAULT_MIN_QUOTE_CHARS",
    "MARKER",
    "VERIFIED_AFTER_EMPHASIS",
    "Answer",
    "Citation",
    "RejectionReason",
    "Trace",
    "TraceEvent",
    "TracedSource",
    "cosmetic",
    "fabricated",
    "markers",
    "mask_code",
    "normalize",
    "resolve",
    "strip_markers",
    "unmatched",
    "verify",
]
