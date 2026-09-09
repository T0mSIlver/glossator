"""Store dated documentation snapshots in one filterable schema."""

from mistralai.search.toolkit.plugins.vespa.app.schemas.app import (
    FieldDefinition,
    IndexingMode,
    SearchMode,
    VespaFieldDefinition,
)
from mistralai.search.toolkit.plugins.vespa.migration import (
    VespaMigration,
    create_schema,
    set_default_ranking_weights,
)

from glossator.index.variants import SNAPSHOT_VARIANT


def _fields() -> list[VespaFieldDefinition]:
    return [
        FieldDefinition.StringField(name="url", fast_search=True),
        FieldDefinition.StringField(name="anchor"),
        FieldDefinition.TextField(name="page_title"),
        FieldDefinition.TextField(name="heading_path", multi_dimensional=True),
        FieldDefinition.StringField(name="kind", fast_search=True),
        FieldDefinition.StringField(name="locale", fast_search=True),
        FieldDefinition.IntField(name="section_index"),
        FieldDefinition.StringField(name="snapshot", fast_search=True),
        FieldDefinition.StringField(name="content_sha256", fast_search=True),
    ]


_RANKING_WEIGHTS = {
    "bm25_content": 0.5,
    "content_embedding_closeness": 5.0,
    "bm25_page_title": 0.3,
    "bm25_heading_path_max": 0.3,
    "match_content": 0.5,
    "content_embedding_cosine_similarity_score": 5.0,
}


class AddSnapshotSchemaMigration(VespaMigration):
    """Add the full-dimension section index shared by all dates."""

    def migrate(self) -> None:
        create_schema(
            name=SNAPSHOT_VARIANT.schema_name,
            mode=SearchMode.INDEX,
            indexing_mode=IndexingMode.DOCUMENT_PER_CHUNK,
            embedding_model=SNAPSHOT_VARIANT.embedding,
            fields=_fields(),
        )
        set_default_ranking_weights(SNAPSHOT_VARIANT.schema_name, _RANKING_WEIGHTS)
