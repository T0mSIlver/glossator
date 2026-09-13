---
url: https://docs.mistral.ai/studio/search-toolkit/vespa/query-profiles
title: Manage ranking
breadcrumbs: [Studio, Search Toolkit, Manage and deploy Vespa applications]
kind: doc
locale: en
source_path: src/content/en/docs/studio/search-toolkit/vespa/query-profiles/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
---

# Manage ranking

Query profiles let you **control ranking at query time** without modifying your schema. Each profile bundles a ranking profile, function weights, and query parameters into a named configuration that you can switch between requests.

For the concepts behind query profiles, see [Anatomy of a Vespa application](https://docs.mistral.ai/studio/search-toolkit/vespa/anatomy).

## Default query profile {#default-query-profile}

When you create a schema with `create_schema()`, the plugin generates a default query profile automatically. It includes:

- A YQL query for hybrid search (keyword + vector) or keyword-only search
- The `weighted-rank2` ranking profile
- Query type fields for all function weights

The default profile name matches the schema name, unless you override it with `default_query_profile_name`:

```python
create_schema(
    name="articles",
    mode=SearchMode.INDEX,
    embedding_dimensions=1024,
    indexing_mode=IndexingMode.DOCUMENT_PER_CHUNK,
    default_query_profile_name="articles-default",
)
```

With the default profile, all ranking weights start at `0`. Set one or more to a non-zero value when querying to activate ranking.

## Create custom query profiles {#creating-custom-query-profiles}

First, generate a new migration file:

```bash
uv run mistral-vespa generate-migration --app-dir ./vespa_app add_custom_query_profiles
```

Then edit the generated file to define your profiles using `add_query_profiles`:

```python
from vespa.package import QueryField

from mistralai.search.toolkit.plugins.vespa.app.schemas.query_profile import QueryProfile
from mistralai.search.toolkit.plugins.vespa.migration import VespaMigration, add_query_profiles


class AddCustomQueryProfiles(VespaMigration):
    def migrate(self) -> None:
        add_query_profiles(
            [
                QueryProfile(
                    name="keyword-search",
                    fields=[
                        QueryField(name="ranking.features.query(bm25_title_weight)", value=100),
                        QueryField(name="ranking.features.query(bm25_content_weight)", value=50),
                        QueryField(name="hits", value=10),
                        QueryField(name="ranking.profile", value="weighted-rank1"),
                    ],
                ),
                QueryProfile(
                    name="hybrid-search",
                    fields=[
                        QueryField(name="ranking.features.query(bm25_title_weight)", value=100),
                        QueryField(
                            name="ranking.features.query(content_embedding_cosine_similarity_score_weight)",
                            value=80,
                        ),
                        QueryField(
                            name="ranking.features.query(freshness_created_at_weight)",
                            value=20,
                        ),
                        QueryField(name="hits", value=10),
                        QueryField(name="ranking.profile", value="weighted-rank2"),
                    ],
                ),
            ]
        )
```

Each `QueryProfile` has:

| Parameter | Type | Description |
|---|---|---|
| `name` | `str` | Profile name, used to select it at query time |
| `fields` | `list[QueryField]` | List of query fields with preset values |

Each `QueryField` has:

| Parameter | Type | Description |
|---|---|---|
| `name` | `str` | Vespa query parameter name |
| `value` | `str \| int \| float` | Default value for the parameter |

## Common query fields {#common-query-fields}

| Field | Description |
|---|---|
| `ranking.profile` | Ranking profile to use (`weighted-rank1`, `weighted-rank2`, `match-only`) |
| `ranking.features.query(<weight_name>)` | Weight for a ranking function (see [Ranking reference](https://docs.mistral.ai/studio/search-toolkit/vespa/anatomy)) |
| `hits` | Number of results to return |

Weight names follow the pattern `<function_name>_weight`. For example, `bm25_title` has weight `bm25_title_weight`.

## Versioned query profiles {#versioned-query-profiles}

Use a colon-separated version string to maintain multiple versions of a profile:

```python
add_query_profiles(
    [
        QueryProfile(
            name="search:1.0.0",
            fields=[
                QueryField(name="ranking.features.query(bm25_title_weight)", value=50),
                QueryField(name="hits", value=3),
                QueryField(name="ranking.profile", value="weighted-rank2"),
            ],
        ),
        QueryProfile(
            name="search:2.0.0",
            fields=[
                QueryField(name="ranking.features.query(bm25_title_weight)", value=100),
                QueryField(
                    name="ranking.features.query(freshness_created_at_weight)",
                    value=20,
                ),
                QueryField(name="hits", value=5),
                QueryField(name="ranking.profile", value="weighted-rank2"),
            ],
        ),
    ]
)
```

Select the version when creating a `QueryProfile` at query time:

```python
from mistralai.search.toolkit.plugins.vespa.search import QueryProfile

query_profile = QueryProfile(name="search", version="2.0.0")
```

## Use query profiles at query time {#using-query-profiles-at-query-time}

Pass a `QueryProfile` to `app.get_search_index()` to select which profile to use for retrieval:

```python
import os

from mistralai.search.toolkit.plugins.vespa import VespaClientConfig
from mistralai.search.toolkit.plugins.vespa.search import QueryProfile
from vespa_app import app

collection_name = "articles"
vespa_config = VespaClientConfig(
    endpoint=os.environ.get("VESPA_ENDPOINT", "http://localhost:18080"),
)
vector_store = app.get_search_index(
    vespa_config,
    collection_name=collection_name,
    query_profile=QueryProfile(name="hybrid-search"),
)
```

When `query_profile` is omitted, the schema's default query profile is used automatically.

## See also {#see-also}

- **[Anatomy of a Vespa application](https://docs.mistral.ai/studio/search-toolkit/vespa/anatomy)**: query profiles concept
- **[Manage schema](https://docs.mistral.ai/studio/search-toolkit/vespa/migrations)**: migration system and helpers
- **[Vespa query profiles documentation](https://docs.vespa.ai/en/querying/query-profiles.html)**: official Vespa guide
