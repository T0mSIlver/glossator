"""Two ways to turn a corpus page into chunks, behind one interface.

Both produce toolkit ``DocumentChunk``s whose ``start_offset``/``end_offset``
index into the *page body* (the markdown after the frontmatter), so a hit can
always be mapped back to a span of the file on disk.

``page`` reproduces the starter app's splitter: whole-page markdown chunks,
page-level metadata only. ``section`` chunks along the page's own heading
structure, budgeted in Mistral tokens, and prefixes each chunk's embedded text
with its heading path.

The prefix is deliberately not part of the located span. It exists so that a
chunk taken out of the middle of a page still says what it is about ("Agents API
> Function calling > Streaming"), which is what the embedder and the reader both
need; but a citation must quote text that is actually in the document, so the
offsets keep pointing at the original body and the prefix is dropped when the
span is resolved back to the source.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import Any, ClassVar, override

import structlog
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
from mistralai.search.toolkit.context import IngestContext
from mistralai.search.toolkit.document import (
    Document,
    DocumentChunk,
    compute_char_locator,
    compute_id,
)
from mistralai.search.toolkit.ingestion.text_splitters import (
    MarkdownTextSplitter,
    MarkdownTextSplitterConfig,
    TextSplitter,
    TokenTextSplitter,
)
from mistralai.search.toolkit.ingestion.text_splitters.models import TextFragment

from glossator.index.variants import ChunkStrategy
from glossator.ingest.markdown import Line, is_table_row, parse_heading, scan_lines
from glossator.ingest.models import ChunkMetadata, CorpusPageMetadata
from glossator.ingest.sections import Section, parse_sections, title_from_body

logger = structlog.get_logger(__name__)

# The starter app's settings, kept verbatim so the baseline variant measures the
# starter and not a paraphrase of it.
PAGE_CHUNK_SIZE = 4096
PAGE_CHUNK_OVERLAP = 50

SECTION_TARGET_TOKENS = 600
SECTION_MAX_TOKENS = 1024
SECTION_OVERLAP_TOKENS = 60

# Hard limit on one embedding input, from the Mistral embedding models.
EMBEDDER_TOKEN_LIMIT = 8192

# How far a table or a code fence may exceed the chunk cap before it has to be
# split anyway. Below this it is emitted whole: half a table has no header row and
# half a code block does not run, and an over-long chunk is a smaller problem than
# an unquotable one. Above it there is no choice -- the embedder rejects an input
# over its limit, and a chunk that cannot be embedded cannot be retrieved at all.
# The margin under the limit covers the heading-path prefix and the model's own
# special tokens. The real corpus has four such blocks (the largest 39k tokens).
ATOMIC_TOKEN_CEILING = 7000

_CONTEXT_SEPARATOR = " > "


class ChunkerError(ValueError):
    """A page cannot be chunked."""


@dataclass(frozen=True, slots=True)
class PageFacts:
    """What a chunker needs to know about the page it is chunking."""

    url: str
    title: str
    kind: str
    locale: str

    @classmethod
    def from_metadata(cls, metadata: CorpusPageMetadata) -> "PageFacts":
        return cls(
            url=metadata.url,
            title=metadata.title,
            kind=metadata.kind,
            locale=metadata.locale,
        )


@dataclass(frozen=True, slots=True)
class ChunkSpec:
    """One planned chunk: a span of the page body plus the text to embed for it."""

    start: int
    end: int
    content: str
    """Embedded text. Equals ``body[start:end]`` unless a context prefix was added."""

    metadata: ChunkMetadata


@dataclass(frozen=True, slots=True)
class _Block:
    """A run of lines that must not be split: a paragraph, a table, a fenced block."""

    start: int
    end: int
    atomic: bool
    """True for a table or a fenced code block: splitting inside one destroys it."""

    is_heading: bool


class CorpusChunker(TextSplitter, ABC):
    """Chunking strategy for corpus pages.

    Subclasses of the toolkit's ``TextSplitter`` because that is what ``Pipeline``
    takes, but the working entry point is ``plan``: per-chunk metadata varies
    within a page, and the base class's fragment interface can only copy one
    metadata object onto every sub-chunk.
    """

    strategy: ClassVar[ChunkStrategy]

    @abstractmethod
    def plan(self, body: str, page: PageFacts) -> list[ChunkSpec]:
        """Chunks for one page body, in reading order."""

    @override
    def split_text(self, text: str, context: IngestContext = IngestContext()) -> list[TextFragment]:
        """The planned spans as bare fragments, without context prefixes.

        Present because ``TextSplitter`` requires it, and useful for inspecting a
        strategy's boundaries; ingestion goes through ``process``, which has the
        page's frontmatter. Here there is only markdown, so the title is taken from
        the body's own first heading -- otherwise every heading path would start
        with an empty segment.
        """
        page = PageFacts(url="", title=title_from_body(text), kind="doc", locale="en")
        return [
            TextFragment(
                content=text[spec.start : spec.end],
                start_offset=spec.start,
                end_offset=spec.end,
            )
            for spec in self.plan(text, page)
        ]

    @override
    def _split_document(
        self, document: Document, context: IngestContext = IngestContext()
    ) -> list[DocumentChunk]:
        metadata = document.metadata
        if not isinstance(metadata, CorpusPageMetadata):
            raise ChunkerError(
                f"{type(self).__name__} needs a corpus page document; "
                f"got metadata {type(metadata).__name__}"
            )
        specs = self.plan(document.content, PageFacts.from_metadata(metadata))
        parent_ref = compute_id(document.source_id)
        chunks: list[DocumentChunk] = []
        for spec in specs:
            locator = compute_char_locator(spec.start, spec.end)
            chunks.append(
                DocumentChunk(
                    id=compute_id(document.source_id, locator),
                    source_id=document.source_id,
                    locator=locator,
                    start_offset=spec.start,
                    end_offset=spec.end,
                    parent_ref=parent_ref,
                    content=spec.content,
                    metadata=spec.metadata,
                )
            )
        logger.debug(
            "Chunked page",
            url=metadata.url,
            strategy=str(self.strategy),
            chunks=len(chunks),
            body_chars=len(document.content),
        )
        return chunks


class PageChunker(CorpusChunker):
    """The starter app's splitter, with page-level metadata attached.

    Kept as a baseline: at 4096 characters most documentation pages become a
    single chunk, so a citation can only name a page, never a section.
    """

    strategy: ClassVar[ChunkStrategy] = ChunkStrategy.PAGE

    def __init__(
        self, chunk_size: int = PAGE_CHUNK_SIZE, chunk_overlap: int = PAGE_CHUNK_OVERLAP
    ) -> None:
        self._splitter = MarkdownTextSplitter(
            MarkdownTextSplitterConfig(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        )

    @override
    def plan(self, body: str, page: PageFacts) -> list[ChunkSpec]:
        specs: list[ChunkSpec] = []
        for index, fragment in enumerate(self._splitter.split_text(body)):
            specs.append(
                ChunkSpec(
                    start=fragment.start_offset,
                    end=fragment.end_offset,
                    content=fragment.content,
                    # No anchor: this strategy knows nothing about headings, so a
                    # citation from it can only point at the page. section_index is
                    # the chunk's position in the page, which is still reading order.
                    metadata=ChunkMetadata(
                        url=page.url,
                        page_title=page.title,
                        kind=page.kind,
                        locale=page.locale,
                        heading_path=[page.title],
                        section_index=index,
                    ),
                )
            )
        return specs


class SectionChunker(CorpusChunker):
    """Heading-aligned chunks under a Mistral-token budget.

    One chunk per section where the section fits; otherwise the section is packed
    into several chunks at paragraph boundaries with a small overlap. A chunk
    never spans two headings, and never cuts into a table or a fenced code block
    while that block stays under ``ATOMIC_TOKEN_CEILING`` -- half a table is worse
    than a long chunk. Past the ceiling the block is cut anyway, because the
    embedder refuses an input over 8192 tokens and an unembeddable chunk is not in
    the index at all.
    """

    strategy: ClassVar[ChunkStrategy] = ChunkStrategy.SECTION

    def __init__(
        self,
        target_tokens: int = SECTION_TARGET_TOKENS,
        max_tokens: int = SECTION_MAX_TOKENS,
        overlap_tokens: int = SECTION_OVERLAP_TOKENS,
        atomic_ceiling: int = ATOMIC_TOKEN_CEILING,
        tokenizer: MistralTokenizer[Any, Any, Any, Any, Any] | None = None,
    ) -> None:
        if not 0 < target_tokens <= max_tokens:
            raise ValueError(
                f"target_tokens ({target_tokens}) must be positive "
                f"and at most max_tokens ({max_tokens})"
            )
        if not 0 <= overlap_tokens < target_tokens:
            raise ValueError(
                f"overlap_tokens ({overlap_tokens}) must be under target_tokens ({target_tokens})"
            )
        if atomic_ceiling < max_tokens or atomic_ceiling > EMBEDDER_TOKEN_LIMIT:
            raise ValueError(
                f"atomic_ceiling ({atomic_ceiling}) must sit between max_tokens ({max_tokens}) "
                f"and the embedder limit ({EMBEDDER_TOKEN_LIMIT})"
            )
        self.target_tokens = target_tokens
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.atomic_ceiling = atomic_ceiling
        # v1 regardless of model: MistralEmbedder tokenizes every embedding model
        # with it, and "mistral-embed" is not a name MistralTokenizer resolves.
        self._tokenizer = tokenizer or MistralTokenizer.v1()

    def count_tokens(self, text: str) -> int:
        return len(self._tokenizer.instruct_tokenizer.tokenizer.encode(text, bos=False, eos=False))

    @override
    def plan(self, body: str, page: PageFacts) -> list[ChunkSpec]:
        specs: list[ChunkSpec] = []
        for section in parse_sections(body, page_title=page.title):
            if section.is_empty:
                # A heading that only introduces subsections carries no text of its
                # own; its children are chunked in their own right.
                continue
            specs.extend(self._plan_section(body, section, page))
        if not specs and body.strip():
            # A page with no chunkable section (no headings, no prose under any)
            # still has to be retrievable.
            specs.append(self._spec(body, 0, len(body), _page_section(page), page))
        return specs

    def _plan_section(self, body: str, section: Section, page: PageFacts) -> list[ChunkSpec]:
        prefix_tokens = self.count_tokens(_context_line(section.heading_path))
        budget = max(1, self.target_tokens - prefix_tokens)
        cap = max(budget, self.max_tokens - prefix_tokens)

        blocks = _split_blocks(body, section.start_offset, section.end_offset)
        specs: list[ChunkSpec] = []
        current: list[_Block] = []
        current_tokens = 0

        def flush() -> list[_Block]:
            """Emit the packed blocks and return the ones to carry into the next chunk."""
            if not current:
                return []
            specs.append(self._spec(body, current[0].start, current[-1].end, section, page))
            return self._overlap_seed(body, current)

        for block in blocks:
            tokens = self.count_tokens(body[block.start : block.end])
            heading_only = bool(current) and all(item.is_heading for item in current)
            if tokens > cap:
                # Nothing this block is packed with can help it fit, so close the
                # current chunk first -- unless all it holds is the section's own
                # heading, which belongs with the block rather than alone.
                if current and not heading_only:
                    flush()
                oversized = replace(block, start=current[0].start if heading_only else block.start)
                specs.extend(self._plan_oversized(body, oversized, section, page, cap))
                current, current_tokens = [], 0
                continue
            # A heading on its own is not a chunk; keep packing until it has content.
            if current and current_tokens + tokens > budget and not heading_only:
                seed = flush()
                current = seed
                current_tokens = sum(
                    self.count_tokens(body[item.start : item.end]) for item in seed
                )
                if current and current_tokens + tokens > budget:
                    current, current_tokens = [], 0
            current.append(block)
            current_tokens += tokens

        flush()
        return specs

    def _plan_oversized(
        self, body: str, block: _Block, section: Section, page: PageFacts, cap: int
    ) -> list[ChunkSpec]:
        """One block that does not fit on its own.

        A table or a fenced code block is emitted whole while it stays under
        ``ATOMIC_TOKEN_CEILING``: cutting it would produce a chunk that is not
        valid markdown and cannot be quoted, and being over the chunk cap is the
        lesser harm. Past that ceiling it must be cut anyway -- the embedder
        rejects an input over its own limit, so the alternative is a chunk that
        never reaches the index.

        Everything else is one paragraph over the cap; it is cut at line
        boundaries, which is as close to a sentence boundary as this gets.
        """
        tokens = self.count_tokens(body[block.start : block.end])
        if block.atomic and tokens <= self.atomic_ceiling:
            logger.info(
                "Emitting an oversized atomic block whole",
                url=page.url,
                heading=section.heading,
                tokens=tokens,
                cap=cap,
            )
            return [self._spec(body, block.start, block.end, section, page)]
        if block.atomic:
            logger.warning(
                "Splitting a table or code block above the embedder's input limit",
                url=page.url,
                heading=section.heading,
                tokens=tokens,
                ceiling=self.atomic_ceiling,
            )
        return self._split_at_lines(body, block, section, page, min(cap, self.atomic_ceiling))

    def _split_at_lines(
        self, body: str, block: _Block, section: Section, page: PageFacts, cap: int
    ) -> list[ChunkSpec]:
        """Cut one block into line-aligned windows of at most ``cap`` tokens."""
        specs: list[ChunkSpec] = []
        start = block.start
        tokens = 0
        for line in scan_lines(body[block.start : block.end]):
            line_start = block.start + line.start
            line_end = block.start + line.end
            line_tokens = self.count_tokens(line.text)
            if line_start > start and tokens + line_tokens > cap:
                specs.append(self._spec(body, start, line_start, section, page))
                start, tokens = line_start, 0
            if line_tokens > cap:
                # One line over the cap on its own: a minified payload or a long
                # generated blob, where there is no textual boundary left to
                # respect. Windowing on tokens is the last resort that keeps every
                # chunk embeddable.
                specs.extend(self._split_by_tokens(body, start, line_end, section, page, cap))
                start, tokens = line_end, 0
                continue
            tokens += line_tokens
            if line_end == block.end and start < block.end:
                specs.append(self._spec(body, start, block.end, section, page))
        return specs

    def _split_by_tokens(
        self,
        body: str,
        start: int,
        end: int,
        section: Section,
        page: PageFacts,
        cap: int,
    ) -> list[ChunkSpec]:
        """Cut a span into token windows, ignoring text structure entirely."""
        splitter = TokenTextSplitter(chunk_size=cap, chunk_overlap=0, tokenizer=self._tokenizer)
        return [
            self._spec(
                body,
                start + fragment.start_offset,
                start + fragment.end_offset,
                section,
                page,
            )
            for fragment in splitter.split_text(body[start:end])
        ]

    def _overlap_seed(self, body: str, packed: list[_Block]) -> list[_Block]:
        """Trailing blocks of a flushed chunk to repeat at the head of the next one.

        Overlap is taken as whole trailing blocks so the next chunk stays a
        contiguous slice of the page body and its offsets remain exact.
        """
        if self.overlap_tokens == 0:
            return []
        seed: list[_Block] = []
        tokens = 0
        # Never the first block: the next chunk has to start later than this one did.
        for block in reversed(packed[1:]):
            block_tokens = self.count_tokens(body[block.start : block.end])
            if tokens + block_tokens > self.overlap_tokens:
                break
            seed.insert(0, block)
            tokens += block_tokens
        return seed

    def _spec(
        self, body: str, start: int, end: int, section: Section, page: PageFacts
    ) -> ChunkSpec:
        prefix = _context_line(section.heading_path)
        return ChunkSpec(
            start=start,
            end=end,
            content=f"{prefix}\n\n{body[start:end]}",
            metadata=ChunkMetadata(
                url=page.url,
                page_title=page.title,
                kind=page.kind,
                locale=page.locale,
                heading_path=list(section.heading_path),
                section_index=section.index,
                anchor=section.anchor,
                own_anchor=section.own_anchor,
            ),
        )


def _context_line(heading_path: tuple[str, ...]) -> str:
    return _CONTEXT_SEPARATOR.join(heading_path)


def _page_section(page: PageFacts) -> Section:
    """A stand-in section for a page with no headings at all."""
    return Section(
        index=0,
        level=0,
        heading=page.title,
        anchor=None,
        own_anchor=None,
        heading_path=(page.title,),
        body="",
        start_offset=0,
        end_offset=0,
    )


def _split_blocks(body: str, start: int, end: int) -> list[_Block]:
    """Tile ``body[start:end]`` with blocks that must not be split internally.

    Blocks are contiguous and cover the whole span, blank separator lines
    included, so any run of consecutive blocks is a verbatim slice of the body.
    """
    lines = [
        Line(
            text=line.text,
            start=start + line.start,
            end=start + line.end,
            in_fence=line.in_fence,
        )
        for line in scan_lines(body[start:end])
    ]
    marks: list[tuple[int, bool, bool]] = []  # start offset, atomic, is_heading
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.is_blank:
            index += 1
            continue
        if line.in_fence:
            marks.append((line.start, True, False))
            index += 1
            while index < len(lines) and lines[index].in_fence:
                index += 1
            continue
        if is_table_row(line):
            marks.append((line.start, True, False))
            while index < len(lines) and is_table_row(lines[index]):
                index += 1
            continue
        if parse_heading(line) is not None:
            marks.append((line.start, False, True))
            index += 1
            continue
        marks.append((line.start, False, False))
        index += 1
        while index < len(lines):
            following = lines[index]
            if following.is_blank or following.in_fence or is_table_row(following):
                break
            if parse_heading(following) is not None:
                break
            index += 1

    if not marks:
        return []
    blocks: list[_Block] = []
    for position, (block_start, atomic, is_heading) in enumerate(marks):
        block_end = marks[position + 1][0] if position + 1 < len(marks) else end
        blocks.append(
            _Block(start=block_start, end=block_end, atomic=atomic, is_heading=is_heading)
        )
    # The first block absorbs any leading blank lines so the tiling starts at ``start``.
    first = blocks[0]
    blocks[0] = _Block(start=start, end=first.end, atomic=first.atomic, is_heading=first.is_heading)
    return blocks


def build_chunker(strategy: ChunkStrategy) -> CorpusChunker:
    """The chunker a variant's strategy names."""
    match strategy:
        case ChunkStrategy.PAGE:
            return PageChunker()
        case ChunkStrategy.SECTION:
            return SectionChunker()
