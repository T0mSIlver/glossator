"""Metadata the pipeline attaches to documents and chunks.

Declared as toolkit metadata subclasses rather than loose dict keys so the field
names are typed once. Citation and retrieval fields have same-named root fields
in Vespa. Provenance fields that do not need filtering remain in the opaque
metadata blob.
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
    breadcrumbs: list[str]
    """The page's place in the documentation navigation, outermost first.

    Not a root field and not matched: it duplicates what the heading path already
    says about a chunk. It is carried so an answer can name where a page sits
    ("Studio > Agents > Conversations") without a second lookup."""


class ChunkMetadata(DocumentChunkMetadata):
    """What a chunk needs to be cited and filtered.

    ``anchor`` points to the closest linkable heading at or above the chunk's
    heading. ``own_anchor`` records whether the chunk's heading itself has a deep
    link. The toolkit drops either key when its value is ``None``.
    """

    url: str
    page_title: str
    kind: str
    locale: str
    heading_path: list[str]
    section_index: int
    anchor: str | None = None
    own_anchor: str | None = None
    snapshot: str | None = None
    content_sha256: str | None = None
