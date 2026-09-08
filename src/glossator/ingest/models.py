"""Metadata the pipeline attaches to documents and chunks.

Declared as toolkit metadata subclasses rather than loose dict keys so the field
names are typed once. Every chunk key here has a same-named root field in the
Vespa schema, which is what makes the store promote it out of the opaque
metadata blob into an indexed, filterable field.
"""

from mistralai.search.toolkit.document import (
    DocumentChunkMetadata,
    DocumentMetadata,
    ExtractorType,
)


class CorpusPageMetadata(DocumentMetadata):
    """Page-level provenance, carried on the ``Document``.

    Reaches Vespa in the metadata blob under a ``document_`` prefix; it is not
    promoted to root fields because nothing filters or ranks on it. It is there
    so a stored chunk can be traced back to the corpus file and commit it came
    from without consulting the manifest.
    """

    extractor_type: ExtractorType = "corpus_page"
    url: str
    title: str
    kind: str
    locale: str
    source_path: str
    source_commit: str


class ChunkMetadata(DocumentChunkMetadata):
    """What a chunk needs to be cited and filtered.

    ``anchor`` is absent (not empty) when the chunk's heading has no deep link:
    the toolkit's metadata models treat ``None`` as absent and drop the key, so
    nothing is written for it.
    """

    url: str
    page_title: str
    kind: str
    locale: str
    heading_path: list[str]
    section_index: int
    anchor: str | None = None
