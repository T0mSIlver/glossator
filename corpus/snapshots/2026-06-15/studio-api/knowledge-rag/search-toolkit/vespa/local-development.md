---
url: https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/vespa/local-development
title: Local development
breadcrumbs: [Studio, Knowledge & RAG, Search Toolkit, Manage and deploy Vespa applications]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/knowledge-rag/search-toolkit/vespa/local-development/page.mdx
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
---

# Local development

This guide covers the full local development loop: create a schema, deploy locally, feed and query documents, then iterate with new migrations. See [Manage Schema](https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/vespa/migrations) to learn how to manage schemas and the [CLI reference](https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/vespa/cli) for the full set of flags.

## Prerequisites {#prerequisites}

- Search Toolkit Vespa Plugin installed ([Installation](https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/#installation))
- Docker installed and running

## Step 1: Create Your First Migration {#step-1-create-your-first-migration}

```bash
uv run mistral-vespa generate-migration --app-dir ./vespa_app initial_schema
```

Fill in the generated file:

```python
from mistralai.search.toolkit.plugins.vespa.app.schemas.app import (
    FieldDefinition,
    SearchMode,
)
from mistralai.search.toolkit.plugins.vespa.migration import VespaMigration, create_default_schema, set_app_name


class InitialSchema(VespaMigration):
    def migrate(self) -> None:
        set_app_name("mynewproject")

        create_default_schema(
            name="articles",
            mode=SearchMode.INDEX,
            embedding_dimensions=1024,
            schema_version=1,
            default_query_profile_name="hybrid-profile",
            additional_fields=[
                FieldDefinition.TextField(name="title"),
            ],
        )
```

`create_default_schema()` includes all required fields for VespaSearchIndex by default. Use `additional_fields` to add custom fields for your use case. For full control over the field set, use `create_schema()` with explicit fields.

> **Info**
>
> **Application name restrictions:** The name passed to `set_app_name()` must contain only lowercase letters (`a-z`). Numbers, underscores, hyphens, and other special characters are not allowed.

> **Info**
>
> **Chunk functions are generated automatically when chunk fields are present.** If a schema includes both a multi-dimensional embedding field and a multi-dimensional text field, the plugin generates `best_chunks`, `chunk_scores`, and related helpers automatically.

## Step 2: Start a Local Vespa Instance {#step-2-start-a-local-vespa-instance}

```bash
uv run mistral-vespa local up --query-port 18080 --config-port 19171 --name vespa-dev
```

| Port  | Service        | Use                     |
|-------|----------------|-------------------------|
| 18080 | Container HTTP | Query and document feed |
| 19171 | Config server  | Application deploys     |

## Step 3: Deploy From Migrations {#step-3-deploy-from-migrations}

```bash
uv run mistral-vespa migrate \
  --app-dir ./vespa_app \
  --config-server http://localhost:19171 \
  --query-port 18080
```

`mistral-vespa migrate` builds the application package from migrations in memory, deploys it, and polls the query endpoint until the app is up.

## Step 4: Feed and Query Documents {#step-4-feed-and-query-documents}

Feed a document:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  --data '{
    "fields": {
      "title": "Document 1"
    }
  }' \
  "http://localhost:18080/document/v1/articles/articles/docid/doc1"
```

Run a search:

```bash
curl -H "Content-Type: application/json" \
  --data '{"yql": "select * from sources * where true"}' \
  "http://localhost:18080/search/"
```

## Step 5: Modify the Schema {#step-5-modify-the-schema}

Create a new migration to evolve the schema:

```bash
uv run mistral-vespa generate-migration \
  --app-dir ./vespa_app \
  add_view_count
```

Update the generated file:

```python
from mistralai.search.toolkit.plugins.vespa.app.schemas.app import FieldDefinition
from mistralai.search.toolkit.plugins.vespa.migration import VespaMigration, add_field


class AddViewCount(VespaMigration):
    def migrate(self) -> None:
        add_field("articles", FieldDefinition.CountField(name="view_count"))
```

Preview the change:

```bash
uv run mistral-vespa migrate \
  --app-dir ./vespa_app \
  --config-server http://localhost:19171 \
  --query-port 18080 \
  --dry-run
```

Apply it (remove `--dry-run`):

```bash
uv run mistral-vespa migrate \
  --app-dir ./vespa_app \
  --config-server http://localhost:19171 \
  --query-port 18080
```

## Understanding Schema Changes {#understanding-schema-changes}

What happens when you change the schema of a running application:

| Change | Behavior |
|---|---|
| **Adding new fields** | No problem. The new field has no value until documents write to it. |
| **Changing how a field is indexed** | Vespa triggers background reindexing. Temporary inconsistency possible. |
| **Removing a field** | All data and indexes for that field are removed. |
| **Changing the type of a field** | Data loss. Prefer adding a new field, migrating data, then removing the old one. |

For more details, see [Vespa's documentation on modifying schemas](https://docs.vespa.ai/en/reference/schemas/schemas.html#modifying-schemas).

## Custom Ranking Profiles and Extra Assets {#custom-ranking-profiles-and-extra-assets}

Add custom rank profiles or model files from a migration:

```python
from pathlib import Path

from mistralai.search.toolkit.plugins.vespa.migration import VespaMigration, add_schema_rank_profiles


class AddCustomRankingProfile(VespaMigration):
    def migrate(self) -> None:
        add_schema_rank_profiles(
            "articles",
            [Path(__file__).parent.parent / "vespa-extra" / "custom.profile"],
        )
```

You can use the same pattern for `add_schema_model_files`, `add_schema_custom_document_summary`, and `add_query_profiles`.

## Optional: Generate a `vespa.lock` Snapshot {#optional-generate-a-vespalock-snapshot}

If your repo keeps a generated reference package for CI or review:

```bash
uv run mistral-vespa generate \
  --app-dir ./vespa_app \
  --path ./vespa.lock
```

Regenerate after every schema change. Deployment should still happen from migrations via `mistral-vespa migrate`.

## IDE Support {#ide-support}

Use an IDE with the Vespa plugin for syntax highlighting, code completion, navigation between functions and profiles, and error detection. See [Vespa IDE support documentation](https://docs.vespa.ai/en/applications/ide-support.html).

## See Also {#see-also}

- **[Deploy and Operate](https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/vespa/operations)** — Production deployment and health checks
