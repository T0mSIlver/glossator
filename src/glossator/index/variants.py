"""The index variants v1 ships, and the facts that distinguish them.

One Vespa schema per (chunking strategy, embedding model) pair, so the eval grid
can compare them on the same corpus without re-indexing between rows: ingest
writes every variant, retrieval reads one.

Schema names are owned here rather than by an environment variable (D-022): a
name is part of the deployed schema, not of a deployment's configuration.
"""

from dataclasses import dataclass
from enum import StrEnum

from mistralai.search.toolkit.embedding import MistralEmbeddingPreset


class ChunkStrategy(StrEnum):
    """How a corpus page becomes chunks. Implementations live in ``glossator.ingest.chunker``."""

    PAGE = "page"
    SECTION = "section"


@dataclass(frozen=True, slots=True)
class IndexVariant:
    """One indexed view of the corpus: a chunker, an embedding model, a schema."""

    name: str
    """Variant key used on the command line and in eval reports."""

    schema_name: str
    """Vespa document type. The toolkit constrains it to ``^[a-z_]+$``, so the
    embedding size is spelled out in words rather than written as digits."""

    chunking: ChunkStrategy
    embedding: MistralEmbeddingPreset

    @property
    def embedding_model_name(self) -> str:
        """Model id to pass to ``MistralEmbedder``."""
        return self.embedding.full_model_name

    @property
    def embedding_dimensions(self) -> int:
        return self.embedding.dimensions


_VARIANTS: tuple[IndexVariant, ...] = (
    # Baseline: what the starter app does (whole-page markdown chunks, 128-dim
    # embeddings). Kept so the eval has a row that is not our own work.
    IndexVariant(
        name="page128",
        schema_name="docs_page_lowdim",
        chunking=ChunkStrategy.PAGE,
        embedding=MistralEmbeddingPreset.MISTRAL_EMBED_DIM_128,
    ),
    # Section chunks at the starter's embedding size: isolates the chunker's effect.
    IndexVariant(
        name="sec128",
        schema_name="docs_section_lowdim",
        chunking=ChunkStrategy.SECTION,
        embedding=MistralEmbeddingPreset.MISTRAL_EMBED_DIM_128,
    ),
    # Section chunks at full embedding size: isolates the embedding size's effect (D-011).
    IndexVariant(
        name="sec1024",
        schema_name="docs_section_fulldim",
        chunking=ChunkStrategy.SECTION,
        embedding=MistralEmbeddingPreset.MISTRAL_EMBED_DIM_1024,
    ),
)

VARIANTS: dict[str, IndexVariant] = {variant.name: variant for variant in _VARIANTS}
"""Variants created by the immutable initial migration."""

SNAPSHOT_VARIANT = IndexVariant(
    name="snap1024",
    schema_name="docs_snapshot_fulldim",
    chunking=ChunkStrategy.SECTION,
    embedding=MistralEmbeddingPreset.MISTRAL_EMBED_DIM_1024,
)

ALL_VARIANTS: dict[str, IndexVariant] = {**VARIANTS, SNAPSHOT_VARIANT.name: SNAPSHOT_VARIANT}
"""Every queryable variant, including schemas added after migration 001."""


def get_variant(name: str) -> IndexVariant:
    """Resolve a variant by name, naming the alternatives when it is unknown."""
    try:
        return ALL_VARIANTS[name]
    except KeyError:
        raise ValueError(
            f"unknown index variant {name!r}; known variants: {sorted(ALL_VARIANTS)}"
        ) from None
