"""Corpus page -> toolkit ``Document``.

There is nothing to extract in the usual sense: the corpus adapter already
produced clean markdown. This step exists to strip the frontmatter, make the
page body the document content (so every downstream offset means the same thing),
and carry the page's provenance onto the document.
"""

from pathlib import Path
from typing import override

from mistralai.search.toolkit.common.text import sanitize_text
from mistralai.search.toolkit.context import IngestContext
from mistralai.search.toolkit.document import Document
from mistralai.search.toolkit.ingestion import File
from mistralai.search.toolkit.ingestion.extractors import DocumentExtractor

from glossator.ingest.models import CorpusPageMetadata
from glossator.ingest.pages import CorpusPage, load_page, parse_page


# The page URL is the stable identity of a document across re-ingests and across
# index variants, so it is what ``source_id`` carries. Chunk ids derive from it,
# which is what makes a re-ingest replace a page's chunks rather than duplicate them.
def page_file(page: CorpusPage) -> File:
    """The pipeline ``File`` for a corpus page, keyed on its URL."""
    return File(
        path=str(page.path),
        name=page.path.name,
        raw=page.path.read_bytes(),
        source_id=page.url,
    )


class CorpusPageExtractor(DocumentExtractor):
    """Turn a corpus page file into a document whose content is the page body."""

    @override
    async def extract(
        self, file: File, context: IngestContext = IngestContext()
    ) -> Document:
        path = Path(file.path)
        page = (
            parse_page(file.raw.decode("utf-8"), path=path)
            if file.raw
            else load_page(path)
        )
        return Document(
            source_id=file.source_id or page.url,
            # Vespa rejects a string field containing a code point that is illegal
            # in XML text, and the docs corpus contains a few (a stray 0x08 in one
            # security advisory). The toolkit's sanitizer substitutes U+FFFD one
            # code point at a time, so offsets into the body still line up.
            content=sanitize_text(page.body),
            # No chunks: the chunker builds them from the body, because per-chunk
            # metadata differs within a page and the toolkit's sub-chunk path can
            # only copy one metadata object onto all of them.
            chunks=[],
            metadata=CorpusPageMetadata(
                url=page.url,
                title=page.title,
                kind=page.kind,
                locale=page.locale,
                source_path=page.source_path,
                source_commit=page.source_commit,
            ),
        )
