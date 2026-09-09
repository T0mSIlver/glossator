"""Keep each chunk heading's own anchor beside its citation fallback."""

from mistralai.search.toolkit.plugins.vespa.app.schemas.app import FieldDefinition
from mistralai.search.toolkit.plugins.vespa.migration import VespaMigration, add_field

from glossator.index.variants import VARIANTS


class AddOwnAnchorMigration(VespaMigration):
    """Add the original heading anchor to every variant."""

    def migrate(self) -> None:
        for variant in VARIANTS.values():
            add_field(variant.schema_name, FieldDefinition.StringField(name="own_anchor"))
