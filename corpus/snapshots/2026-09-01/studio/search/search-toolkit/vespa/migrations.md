---
url: https://docs.mistral.ai/studio/search/search-toolkit/vespa/migrations
title: Manage schema
breadcrumbs: [Studio, Search, Search Toolkit, Manage and deploy Vespa applications]
kind: doc
locale: en
source_path: src/content/en/docs/studio/search/search-toolkit/vespa/migrations/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Manage schema

Manage your Vespa application schemas through Python migrations. For the concepts behind schemas, fields, and ranking, see [Anatomy of a Vespa application](https://docs.mistral.ai/studio/search/search-toolkit/vespa/anatomy).

## Create and evolve schemas {#creating-and-evolving-schemas}

Use migrations to define and modify your schemas. Migrations are Python files under `vespa_app/migrations/` that are append-only, ordered by timestamp, and re-run on every deploy.

Generate a new migration:

```bash
uv run mistral-vespa generate-migration --app-dir ./vespa_app <name>
```

This creates a timestamped file with a class stub:

```python
from mistralai.search.toolkit.plugins.vespa.migration import VespaMigration


class MyMigration(VespaMigration):
    def migrate(self) -> None:
        pass  # Define your changes here
```

## Define a schema {#defining-a-schema}

Use `create_schema` with an explicit `indexing_mode`. `DOCUMENT_PER_CHUNK` is the recommended mode. It indexes one Vespa document per chunk and injects the standard chunk fields (content, embedding, identity, metadata) automatically:

```python
from mistralai.search.toolkit.plugins.vespa.app.schemas.app import FieldDefinition, IndexingMode, SearchMode
from mistralai.search.toolkit.plugins.vespa.migration import VespaMigration, create_schema, set_app_name


class InitialSchema(VespaMigration):
    def migrate(self) -> None:
        set_app_name("myapp")
        create_schema(
            name="articles",
            mode=SearchMode.INDEX,
            embedding_dimensions=1024,
            indexing_mode=IndexingMode.DOCUMENT_PER_CHUNK,
            # The standard chunk fields (content, embedding, identity, metadata) are
            # added automatically. `fields` only declares your extra fields.
            fields=[
                FieldDefinition.TextField(name="title"),
                FieldDefinition.TimestampField(name="created_at"),
            ],
        )
```

> **Info**
>
> **Application name restrictions:** The name passed to `set_app_name()` must contain only lowercase letters (`a-z`). Numbers, underscores, hyphens, and other special characters are not allowed.

This injects the fields the pipeline needs (chunk content, embedding, identity, metadata) and adds your project-specific fields via `fields`.

> **Warning**
>
> `create_default_schema(...)` is deprecated. It only produces the legacy `IndexingMode.SINGLE_DOCUMENT` field set and will be removed before 1.0.0. Use `create_schema(..., indexing_mode=...)` instead.

### Add fields to an existing schema

Use `add_field` in a new migration to add fields after the initial schema is created:

```python
from mistralai.search.toolkit.plugins.vespa.app.schemas.app import FieldDefinition
from mistralai.search.toolkit.plugins.vespa.migration import VespaMigration, add_field


class AddViewCount(VespaMigration):
    def migrate(self) -> None:
        add_field("articles", FieldDefinition.CountField(name="view_count"))
```

Set `multi_dimensional=True` for array fields (e.g., per-chunk embeddings or text chunks). Embedding dimensions are set once in `create_schema(embedding_dimensions=...)`.

### Multiple schemas

Call `create_schema()` multiple times to register multiple document types under one application. Each schema produces its own `.sd` file and query profile. Names must be unique.

## Migration helpers {#migration-helpers}

| Helper | Description |
|---|---|
| `set_app_name(name)` | Set the application name (required in the first migration) |
| `create_schema(...)` | Create a schema with an explicit `indexing_mode` and fields (recommended) |
| `create_default_schema(...)` | Legacy single-document schema. **Deprecated** and removed before 1.0.0. |
| `add_field(schema, field)` | Add a field to an existing schema |
| `add_custom_functions(schema, functions)` | Add custom ranking functions to an existing schema |
| `add_query_profiles(...)` | Add or update query profiles |
| `add_schema_rank_profiles(schema, paths)` | Add custom rank profile files |
| `add_schema_model_files(schema, paths)` | Add ML model files |
| `add_schema_custom_document_summary(...)` | Add custom document summaries |
| `set_content_id(id)` | Override the content cluster id (avoids destructive cluster renames) |
| `allow_schema_removal(until)` | Permit schema removal until a given date |

For full signatures and parameters, see the [Migration helpers reference](https://docs.mistral.ai/studio/search/search-toolkit/vespa/migration-helpers).

## Deploying {#deploying}

`mistral-vespa migrate` discovers migrations, runs them in order, builds the app package, and uploads it. See the [Local Development](https://docs.mistral.ai/studio/search/search-toolkit/vespa/local-development) and [Deploy and Operate](https://docs.mistral.ai/studio/search/search-toolkit/vespa/operations) guides for details.

## Optional snapshot {#optional-snapshot}

```bash
uv run mistral-vespa generate \
  --app-dir ./vespa_app \
  --path ./vespa.lock
```

Writes the app package to disk for inspection or CI validation. It is not used for deployment.

## See also {#see-also}

- **[Anatomy of a Vespa application](https://docs.mistral.ai/studio/search/search-toolkit/vespa/anatomy)**: concepts: schemas, fields, ranking profiles, migrations
- **[Local development](https://docs.mistral.ai/studio/search/search-toolkit/vespa/local-development)**: full local development loop
- **[CLI reference](https://docs.mistral.ai/studio/search/search-toolkit/vespa/cli)**: full set of CLI flags
