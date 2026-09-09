"""Hits in, one numbered context block out.

Retrieval returns overlapping slices of pages in relevance order, which is the
wrong shape to read: the same chunk can arrive twice, two hits can be halves of
one paragraph, and the section that explains a snippet can rank below it. This
module puts a page back together -- de-duplicated, merged where the offsets touch,
in reading order -- and cuts it to a token budget, so what the model sees is a
short document rather than a pile of search results.

Every source keeps the pieces it was merged from, with the character range each
one occupies in the merged text. That is what lets citation verification say
*which* chunk a quote came from even when the quote straddles a merge.
"""

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Protocol

import structlog
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer

from glossator.retrieval.engine import Hit

logger = structlog.get_logger(__name__)

_HEADING_SEPARATOR = " > "
"""What the chunker prefixes chunk content with; stripped when a chunk is merged
into one that already carries it."""


class TokenCounter(Protocol):
    def __call__(self, text: str) -> int: ...


@dataclass(frozen=True, slots=True)
class SourcePiece:
    """One original chunk inside a merged source."""

    chunk_id: str
    score: float
    start_offset: int | None
    end_offset: int | None
    text_start: int
    """Where this chunk's text begins in the merged source content."""

    text_end: int


@dataclass(frozen=True, slots=True)
class Source:
    """One numbered source in the assembled context."""

    n: int
    url: str
    anchor: str | None
    page_title: str
    heading_path: tuple[str, ...]
    source_id: str
    content: str
    pieces: tuple[SourcePiece, ...]
    score: float
    tokens: int

    @property
    def citation_url(self) -> str:
        return f"{self.url}#{self.anchor}" if self.anchor else self.url

    @property
    def chunk_ids(self) -> tuple[str, ...]:
        return tuple(piece.chunk_id for piece in self.pieces)

    def chunk_id_at(self, position: int) -> str:
        """The chunk that owns a character position in the merged content."""
        for piece in self.pieces:
            if piece.text_start <= position < piece.text_end:
                return piece.chunk_id
        return self.pieces[0].chunk_id

    def render(self) -> str:
        heading = _HEADING_SEPARATOR.join(self.heading_path) or self.page_title
        return f"[{self.n}] {self.citation_url}\n{heading}\n{self.content}"


@dataclass(frozen=True, slots=True)
class AssembledContext:
    """The rendered context and the source table citations are mapped through."""

    text: str
    sources: tuple[Source, ...]
    tokens: int
    dropped_chunk_ids: tuple[str, ...]
    """Chunks that did not fit the budget, kept for the trace."""

    def by_number(self, n: int) -> Source | None:
        for source in self.sources:
            if source.n == n:
                return source
        return None


def assemble(
    hits: list[Hit],
    *,
    token_budget: int,
    count_tokens: TokenCounter | None = None,
) -> AssembledContext:
    """De-duplicate, merge, order and number hits into one context block.

    ``hits`` are taken in the order given: for a search that is relevance order,
    and it decides both what survives the budget and how pages are ordered
    against each other. Within a page, reading order always wins.
    """
    counter = count_tokens or count_mistral_tokens
    groups = _merge(_deduplicate(hits))
    kept, dropped = _fit(groups, token_budget=token_budget, count_tokens=counter)
    ordered = sorted(kept, key=lambda group: (group.page_rank, group.start_offset))

    sources = tuple(
        _source(group, n=n, count_tokens=counter) for n, group in enumerate(ordered, start=1)
    )
    text = "\n\n".join(source.render() for source in sources)
    logger.debug(
        "Assembled context",
        hits=len(hits),
        sources=len(sources),
        dropped=len(dropped),
        tokens=counter(text) if sources else 0,
    )
    return AssembledContext(
        text=text,
        sources=sources,
        tokens=counter(text) if sources else 0,
        dropped_chunk_ids=tuple(dropped),
    )


@lru_cache(maxsize=1)
def _tokenizer() -> MistralTokenizer[Any, Any, Any, Any, Any]:
    # v1 regardless of model, matching the chunker: the budget and the chunk sizes
    # it was built from have to be counted the same way to mean anything.
    return MistralTokenizer.v1()


def count_mistral_tokens(text: str) -> int:
    return len(_tokenizer().instruct_tokenizer.tokenizer.encode(text, bos=False, eos=False))


@dataclass(slots=True)
class _Group:
    """Chunks of one page being merged together, in reading order."""

    rank: int
    """Position of the group's best hit in the input, used to break score ties."""

    page_rank: int
    """Position of the whole page's best hit in the input. Pages are ordered
    against each other by relevance; passages within a page by offset."""

    hits: list[Hit]

    @property
    def start_offset(self) -> int:
        return self.hits[0].start_offset or 0

    @property
    def end_offset(self) -> int:
        return self.hits[-1].end_offset or 0

    @property
    def score(self) -> float:
        return max(hit.score for hit in self.hits)


def _deduplicate(hits: list[Hit]) -> list[Hit]:
    seen: set[str] = set()
    unique: list[Hit] = []
    for hit in hits:
        if hit.chunk_id in seen:
            continue
        seen.add(hit.chunk_id)
        unique.append(hit)
    return unique


def _merge(hits: list[Hit]) -> list[_Group]:
    """Group each page's hits and merge the ones whose offsets touch or overlap."""
    ranks = {hit.chunk_id: rank for rank, hit in enumerate(hits)}
    by_page: dict[str, list[Hit]] = {}
    for hit in hits:
        by_page.setdefault(hit.source_id, []).append(hit)

    groups: list[_Group] = []
    for page_hits in by_page.values():
        page_rank = min(ranks[hit.chunk_id] for hit in page_hits)
        ordered = sorted(page_hits, key=lambda hit: (hit.start_offset or 0, hit.end_offset or 0))
        current: list[Hit] = []
        for hit in ordered:
            if current and _adjacent(current[-1], hit):
                current.append(hit)
                continue
            if current:
                groups.append(_group(current, ranks, page_rank))
            current = [hit]
        if current:
            groups.append(_group(current, ranks, page_rank))
    return groups


def _group(hits: list[Hit], ranks: dict[str, int], page_rank: int) -> _Group:
    return _Group(
        rank=min(ranks[hit.chunk_id] for hit in hits),
        page_rank=page_rank,
        hits=hits,
    )


def _adjacent(left: Hit, right: Hit) -> bool:
    """True when the right chunk starts no later than the left one ends.

    Offsets are exact spans of the page body, so touching or overlapping chunks
    can be stitched back into one contiguous passage. A gap cannot: the text in
    between was never retrieved and is not available to fill it.
    """
    if left.end_offset is None or right.start_offset is None:
        return False
    return right.start_offset <= left.end_offset


def _fit(
    groups: list[_Group], *, token_budget: int, count_tokens: TokenCounter
) -> tuple[list[_Group], list[str]]:
    """Take groups by relevance until the budget is spent.

    Relevance decides what survives; reading order decides how it is presented.
    Deciding both by relevance would drop the section that explains a snippet in
    favour of a second copy of the snippet.
    """
    kept: list[_Group] = []
    dropped: list[str] = []
    spent = 0
    for group in sorted(groups, key=lambda group: (-group.score, group.rank)):
        cost = count_tokens(_merged_content(group.hits)) + _OVERHEAD_TOKENS
        if spent + cost > token_budget and kept:
            dropped.extend(hit.chunk_id for hit in group.hits)
            continue
        if spent + cost > token_budget and not kept:
            # The single best group is over budget on its own. An empty context is
            # worse than a truncated one, so it is kept whole and the caller sees
            # the overrun in the assembled token count.
            logger.warning("Best source exceeds the context budget", tokens=cost)
        kept.append(group)
        spent += cost
    return kept, dropped


_OVERHEAD_TOKENS = 24
"""Rough cost of a source's header lines, so the budget is not blown by them."""


def _source(group: _Group, *, n: int, count_tokens: TokenCounter) -> Source:
    content, pieces = _merged(group.hits)
    best = max(group.hits, key=lambda hit: hit.score)
    return Source(
        n=n,
        url=best.url,
        anchor=group.hits[0].anchor,
        page_title=best.page_title,
        heading_path=group.hits[0].heading_path,
        source_id=best.source_id,
        content=content,
        pieces=pieces,
        score=group.score,
        tokens=count_tokens(content),
    )


def _merged_content(hits: list[Hit]) -> str:
    return _merged(hits)[0]


def _merged(hits: list[Hit]) -> tuple[str, tuple[SourcePiece, ...]]:
    """Stitch chunks into one passage, dropping the text an overlap repeats."""
    parts: list[str] = []
    pieces: list[SourcePiece] = []
    position = 0
    previous_end: int | None = None

    for hit in hits:
        body = chunk_body(hit) if parts else hit.content
        if previous_end is not None and hit.start_offset is not None:
            overlap = previous_end - hit.start_offset
            if overlap > 0:
                # The chunker's overlap repeats whole blocks, so cutting the
                # repeated prefix leaves a clean block boundary.
                body = body[min(overlap, len(body)) :].lstrip()
        if not body:
            continue
        if parts:
            parts.append("\n\n")
            position += 2
        parts.append(body)
        pieces.append(
            SourcePiece(
                chunk_id=hit.chunk_id,
                score=hit.score,
                start_offset=hit.start_offset,
                end_offset=hit.end_offset,
                text_start=position,
                text_end=position + len(body),
            )
        )
        position += len(body)
        previous_end = hit.end_offset if hit.end_offset is not None else previous_end

    return "".join(parts), tuple(pieces)


def chunk_body(hit: Hit) -> str:
    """A chunk's content without the heading line the chunker prefixes it with."""
    prefix = _HEADING_SEPARATOR.join(hit.heading_path)
    if prefix and hit.content.startswith(f"{prefix}\n\n"):
        return hit.content[len(prefix) + 2 :]
    return hit.content


__all__ = [
    "AssembledContext",
    "Source",
    "SourcePiece",
    "TokenCounter",
    "assemble",
    "chunk_body",
    "count_mistral_tokens",
]
