"""Quote verification for answers the consumer wrote itself (D-040).

A consumer model that can call tools gathers context through ``search``,
``open``, ``read`` and ``grep``; what it cannot do is verify its own quotes,
because checking a quoted span needs the chunk text only the server has. This
module does that check and nothing else: it never rewrites the answer and never
calls a model.

The consumer sends its draft (with ``[n]`` markers) and the quotes it relied
on, each naming either a chunk id from an earlier tool result or a page URL
with an optional ``#anchor``. A URL reference resolves to the page's chunks,
merged the way the answer layer merges them, so a quote spanning two adjacent
chunks still verifies. Each quote is checked with the same verifier the
answer layer uses, and the draft's markers are reconciled against the verified
quotes.
"""

import structlog
from pydantic import BaseModel, ConfigDict, Field

from glossator.answer.citations import (
    VERIFIED_AFTER_EMPHASIS,
    Citation,
    RejectionReason,
    fragment_link,
    markers,
    matched_source_quote,
    verify,
)
from glossator.answer.context import Source, SourcePiece, assemble
from glossator.answer.docs_index import DocsIndex

logger = structlog.get_logger(__name__)

MAX_QUOTES = 20
"""How many quotes one call verifies. More would let a caller turn the server
into a batch oracle one sentence at a time."""

MAX_DRAFT_CHARS = 20_000
"""The draft is only scanned for ``[n]`` markers, so beyond this it is cut."""

PAGE_READ_TOP_K = 200
"""Chunks read for one URL reference. Pages are small (about 11 chunks on
average); the cap is generous rather than load-bearing."""


class CiteQuote(BaseModel):
    """One quote the consumer relied on, and where it claims to come from."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    n: int = Field(ge=1, le=999)
    quote: str = Field(min_length=1)
    chunk_id: str | None = None
    url: str | None = None
    """A page URL with an optional ``#anchor``, in place of ``chunk_id``."""


class VerifiedQuote(BaseModel):
    """What the check found for one submitted quote."""

    model_config = ConfigDict(frozen=True)

    n: int
    verified: bool
    reason: str | None = None
    """Why a failed quote was rejected: too short, fabricated, no such source."""

    fragment_url: str | None = None
    """A text-fragment deep link to the quoted span, on verified quotes only."""

    url: str | None = None
    anchor: str | None = None
    chunk_id: str | None = None
    quote: str = ""
    """The submitted quote, so the source list can show what was checked."""

    heading: str = ""
    """The section path of the chunk the quote was checked against."""

    emphasis_normalized: bool = False
    """True when the quote verified only after emphasis normalization."""

    @property
    def citation_url(self) -> str | None:
        if not self.url:
            return None
        return f"{self.url}#{self.anchor}" if self.anchor else self.url


class SourceQuote(BaseModel):
    """One verified quote behind a deduplicated source entry."""

    model_config = ConfigDict(frozen=True)

    n: int
    fragment_url: str | None = None
    text: str = ""
    """The quoted sentence, printed under its source in the rendered block."""


class SourceEntry(BaseModel):
    """One entry of the deduplicated source list (D-027b)."""

    model_config = ConfigDict(frozen=True)

    url: str
    anchor: str | None = None
    citation_url: str
    numbers: list[int] = Field(default_factory=list)
    """Every ``[n]`` marker that points at this source; markers keep their numbers."""
    quotes: list[SourceQuote] = Field(default_factory=list)
    heading: str = ""
    """The section path of the source, when the caller knows it."""


class CiteResult(BaseModel):
    """Everything one ``cite`` call verified, ready for either surface."""

    model_config = ConfigDict(frozen=True)

    quotes: list[VerifiedQuote] = Field(default_factory=list)
    unverified_markers: list[int] = Field(default_factory=list)
    """Draft ``[n]`` markers that name no verified quote: remove or fix them."""
    sources: list[SourceEntry] = Field(default_factory=list)
    sources_markdown: str = ""
    """The rendered Markdown block, ready to paste under an answer."""

    notes: list[str] = Field(default_factory=list)
    """Announced clamps: quotes cut to 20, the draft cut to 20,000 characters."""
    next: str = ""


class CiteInputError(ValueError):
    """A malformed ``cite`` call. Both surfaces answer it with ``E_BAD_PARAM``."""


def split_url_anchor(url: str) -> tuple[str, str | None]:
    """Split a ``page#anchor`` reference into the page URL and the anchor."""
    page, separator, anchor = url.partition("#")
    return page, anchor if separator else None


def dedupe_sources(
    items: list[Citation] | list[VerifiedQuote],
) -> list[SourceEntry]:
    """Collapse verified quotes to one entry per distinct (url, anchor).

    Markers keep their numbers: the entry lists every ``[n]`` that points at
    it. Two sections of one page with different anchors stay separate entries,
    since they are two deep links.
    """
    grouped: dict[tuple[str, str | None], SourceEntry] = {}
    order: list[tuple[str, str | None]] = []
    for item in items:
        if not item.verified or not item.url:
            continue
        key = (item.url, item.anchor)
        entry = grouped.get(key)
        if entry is None:
            entry = SourceEntry(
                url=item.url,
                anchor=item.anchor,
                citation_url=(f"{item.url}#{item.anchor}" if item.anchor else item.url),
            )
            grouped[key] = entry
            order.append(key)
        # The heading is the entry's description in the rendered block. The
        # answer path passes it separately through entries_with_headings; a
        # verified quote carries its own, so cite entries have one too.
        heading = grouped[key].heading or getattr(item, "heading", "")
        entry = grouped[key].model_copy(
            update={
                "numbers": [*grouped[key].numbers, item.n],
                "heading": heading,
                "quotes": [
                    *grouped[key].quotes,
                    SourceQuote(
                        n=item.n,
                        fragment_url=item.fragment_url,
                        text=getattr(item, "quote", ""),
                    ),
                ],
            }
        )
        grouped[key] = entry
    return [grouped[key] for key in order]


def entries_with_headings(
    items: list[Citation] | list[VerifiedQuote],
    headings: dict[int, str],
) -> list[SourceEntry]:
    """Deduplicated source entries with the section path each marker came from."""
    entries = dedupe_sources(items)
    out: list[SourceEntry] = []
    for entry in entries:
        # One entry, one section path: several markers on one source are the
        # same section, so the paths are deduplicated rather than concatenated.
        paths = list(dict.fromkeys(headings[n] for n in entry.numbers if headings.get(n)))
        heading = " > ".join(paths)
        out.append(entry.model_copy(update={"heading": heading}) if heading else entry)
    return out


def sources_markdown(entries: list[SourceEntry]) -> str:
    """A ready-to-paste Markdown source list over deduplicated entries.

    One line per distinct (url, anchor): the markers that point at it, a link
    whose text is the section path and whose href is the text fragment that
    scrolls to the quoted sentence, and the sentence itself. A bare URL is at
    the mercy of a renderer's autolinking, and an `[n]` alone is inert text.
    """
    if not entries:
        return "Sources (0 verified):\n(none)"
    lines = [f"Sources ({sum(len(entry.numbers) for entry in entries)} verified):"]
    for entry in entries:
        numbers = "".join(f"[{n}]" for n in entry.numbers)
        first = entry.quotes[0] if entry.quotes else None
        href = (first.fragment_url if first else None) or entry.citation_url
        label = _link_label(entry.heading or entry.citation_url)
        line = f"{numbers} [{label}]({href})"
        if first and first.text.strip():
            line += f' — "{" ".join(first.text.split())}"'
        lines.append(line)
    return "\n".join(lines)


def _link_label(text: str) -> str:
    """Link text that cannot close its own bracket."""
    return text.replace("[", "(").replace("]", ")")


def _single_chunk_source(n: int, content: str, url: str, anchor: str | None) -> Source:
    return Source(
        n=n,
        url=url,
        anchor=anchor,
        page_title="",
        heading_path=(),
        source_id=url,
        content=content,
        pieces=(
            SourcePiece(
                chunk_id="",
                score=0.0,
                start_offset=None,
                end_offset=None,
                text_start=0,
                text_end=len(content),
            ),
        ),
        score=0.0,
        tokens=0,
    )


async def cite_draft(
    draft: str,
    quotes: list[CiteQuote],
    *,
    engine: DocsIndex,
    min_quote_chars: int = 8,
) -> CiteResult:
    """Verify a consumer's quotes against the chunks they name.

    Raises :class:`CiteInputError` on malformed input; clamps the quote list
    and the draft with an announcement instead of failing.
    """
    if not draft.strip():
        raise CiteInputError("the draft is empty or only whitespace.")
    for quote in quotes:
        if not quote.quote.strip():
            raise CiteInputError(f"quote [{quote.n}] is empty or only whitespace.")
        if quote.chunk_id and quote.url:
            raise CiteInputError(
                f"quote [{quote.n}] names both chunk_id and url; send exactly one."
            )
        if not quote.chunk_id and not quote.url:
            raise CiteInputError(
                f"quote [{quote.n}] names neither chunk_id nor url; send one of them."
            )

    notes: list[str] = []
    if len(quotes) > MAX_QUOTES:
        notes.append(f"note: clamped server-side: quotes={len(quotes)} → {MAX_QUOTES}")
        quotes = quotes[:MAX_QUOTES]
    if len(draft) > MAX_DRAFT_CHARS:
        notes.append(f"note: clamped server-side: draft={len(draft)} → {MAX_DRAFT_CHARS} chars")
        draft = draft[:MAX_DRAFT_CHARS]

    checked: list[VerifiedQuote] = []
    for quote in quotes:
        if quote.chunk_id is not None:
            checked.append(await _cite_chunk(quote, engine=engine, min_quote_chars=min_quote_chars))
        else:
            assert quote.url is not None
            checked.append(await _cite_url(quote, engine=engine, min_quote_chars=min_quote_chars))

    verified_numbers = {item.n for item in checked if item.verified}
    unverified = [n for n in markers(draft) if n not in verified_numbers]
    entries = dedupe_sources(checked)
    verified_count = len(verified_numbers)
    if verified_count:
        next_hint = (
            "keep only the verified quotes; drop every [n] in "
            f"{unverified} or fix it against a quoted source, then paste the Sources block"
            if unverified
            else "every [n] in the draft verified; paste the Sources block as-is"
        )
    else:
        next_hint = (
            "nothing verified: re-read the cited chunks with open() and quote them "
            "verbatim, or search(query=…) for sources that state the claim"
        )
    return CiteResult(
        quotes=checked,
        unverified_markers=unverified,
        sources=entries,
        sources_markdown=sources_markdown(entries),
        notes=notes,
        next=next_hint,
    )


async def _cite_chunk(
    quote: CiteQuote, *, engine: DocsIndex, min_quote_chars: int
) -> VerifiedQuote:
    """Verify a quote against the single chunk it names."""
    assert quote.chunk_id is not None
    try:
        hit = await engine.get_chunk(quote.chunk_id)
    except Exception as exc:
        raise CiteInputError(f"could not read chunk {quote.chunk_id!r}: {exc}") from exc
    if hit is None:
        return VerifiedQuote(
            n=quote.n,
            verified=False,
            reason=f"{RejectionReason.NO_SUCH_SOURCE}: {quote.chunk_id}",
        )
    source = _single_chunk_source(quote.n, hit.content, hit.url, hit.anchor)
    ok, _chunk_id, reason = verify(quote.quote, source, min_quote_chars=min_quote_chars)
    if not ok:
        return VerifiedQuote(
            n=quote.n,
            verified=False,
            reason=reason,
            url=hit.url,
            anchor=hit.anchor,
            chunk_id=hit.chunk_id,
            quote=quote.quote,
        )
    span = matched_source_quote(quote.quote, hit.content, min_quote_chars=min_quote_chars)
    return VerifiedQuote(
        n=quote.n,
        verified=True,
        reason=reason,
        fragment_url=(fragment_link(hit.url, hit.anchor, span) if span is not None else None),
        url=hit.url,
        anchor=hit.anchor,
        chunk_id=hit.chunk_id,
        quote=quote.quote,
        heading=hit.heading_line or hit.page_title,
        emphasis_normalized=reason == VERIFIED_AFTER_EMPHASIS,
    )


async def _cite_url(quote: CiteQuote, *, engine: DocsIndex, min_quote_chars: int) -> VerifiedQuote:
    """Verify a quote against a page's chunks, merged as the answer layer merges them.

    Adjacent chunks of the page are stitched back into one passage before the
    check, so a quote running across a chunk boundary still verifies even
    though it sits in neither chunk on its own.
    """
    assert quote.url is not None
    page_url, _anchor_hint = split_url_anchor(quote.url)
    try:
        navigation = engine.navigation_at(page_url)
        hits = await navigation.read(None, None, top_k=PAGE_READ_TOP_K)
    except Exception as exc:
        raise CiteInputError(f"could not read page {page_url!r}: {exc}") from exc
    if not hits:
        return VerifiedQuote(
            n=quote.n,
            verified=False,
            reason=f"{RejectionReason.NO_SUCH_SOURCE}: {page_url}",
            url=page_url,
        )
    context = assemble(hits, token_budget=_PAGE_BUDGET)
    for source in context.sources:
        ok, chunk_id, reason = verify(quote.quote, source, min_quote_chars=min_quote_chars)
        if not ok:
            continue
        span = matched_source_quote(quote.quote, source.content, min_quote_chars=min_quote_chars)
        return VerifiedQuote(
            n=quote.n,
            verified=True,
            reason=reason,
            fragment_url=(
                fragment_link(source.url, source.anchor, span) if span is not None else None
            ),
            url=source.url,
            anchor=source.anchor,
            chunk_id=chunk_id,
            quote=quote.quote,
            heading=" > ".join(source.heading_path) or source.page_title,
            emphasis_normalized=reason == VERIFIED_AFTER_EMPHASIS,
        )
    first = context.sources[0]
    return VerifiedQuote(
        n=quote.n,
        verified=False,
        reason=RejectionReason.FABRICATED,
        url=first.url,
        anchor=first.anchor,
    )


_PAGE_BUDGET = 1_000_000
"""A budget no single page can exceed: merging must never drop a chunk."""


__all__ = [
    "MAX_DRAFT_CHARS",
    "MAX_QUOTES",
    "PAGE_READ_TOP_K",
    "CiteInputError",
    "CiteQuote",
    "CiteResult",
    "SourceEntry",
    "SourceQuote",
    "VerifiedQuote",
    "cite_draft",
    "dedupe_sources",
    "entries_with_headings",
    "sources_markdown",
    "split_url_anchor",
]
