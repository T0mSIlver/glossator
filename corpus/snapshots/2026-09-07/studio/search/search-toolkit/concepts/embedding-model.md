---
url: https://docs.mistral.ai/studio/search/search-toolkit/concepts/embedding-model
title: Embedding model
breadcrumbs: [Studio, Search, Search Toolkit, Concepts]
kind: doc
locale: en
source_path: src/content/en/docs/studio/search/search-toolkit/concepts/embedding-model/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# Embedding model

An `EmbeddingModel` describes the dimensions, data type, and distance metric of vectors stored in an index. The schema layer uses it as the source of truth to size embedding tensors and select the ranking metric, independently of the embedder that produces vectors at runtime.

The embedder you pass to the `Pipeline` (see [Embedders](https://docs.mistral.ai/studio/search/search-toolkit/ingestion/embedders)) produces the vectors; the `EmbeddingModel` on the schema describes the index. The two must agree on dimensions.

## Choose a Mistral or custom embedding model {#flavors}

There are two flavors, discriminated by `type`:

- **`MistralEmbeddingModel`**: a model served by the **Mistral Embedding API**. Use this type to instantiate a `MistralEmbedder`. Search Toolkit validates dimensions against known presets. A dimension that doesn't match the model name raises `DimensionMismatchError`. Pass a `MistralEmbeddingPreset` to `create_schema` to use its defaults, or build it explicitly to override the data type or distance metric:

  ```python
  from mistralai.search.toolkit.embedding import (
      DistanceMetric,
      MistralEmbeddingModel,
      MistralEmbeddingPreset,
      VectorDType,
  )

  # Pass a preset directly to create_schema (dimensions and metric filled in)
  from mistralai.search.toolkit.plugins.vespa.migration import create_schema

  create_schema(
      ...,
      embedding_model=MistralEmbeddingPreset.MISTRAL_EMBED_DIM_1024,
  )

  # Build explicitly to override the dtype or distance metric
  model = MistralEmbeddingPreset.MISTRAL_EMBED_DIM_1024.build_embedding_model(
      dtype=VectorDType.FLOAT16,
      distance_metric=DistanceMetric.INNER_PRODUCT,
  )

  # Construct directly (dimensions must match the known preset for that name)
  model = MistralEmbeddingModel(name="mistral-embed", dimensions=1024)
  ```

- **`CustomEmbeddingModel`**: any embedding model **not** served by the Mistral Embedding API, such as a third-party or self-hosted model. Use this type with your own `Embedder` implementation. You set the dimensions, data type, and distance metric. Search Toolkit doesn't apply preset validation:

  ```python
  from mistralai.search.toolkit.embedding import CustomEmbeddingModel, DistanceMetric, VectorDType

  model = CustomEmbeddingModel(
      name="my-provider/text-embedding-3-small",
      dimensions=1536,
      dtype=VectorDType.FLOAT32,
      distance_metric=DistanceMetric.COSINE,
  )
  ```

The discriminated union is exposed as `EmbeddingModel`, which accepts either flavor.

## Use Mistral embedding presets {#presets}

`MistralEmbeddingPreset` enumerates the supported Mistral embedding models and carries each one's full name, dimensions, and default distance metric:

| Preset | Full model name | Dimensions | Distance metric |
|--------|-----------------|------------|-----------------|
| `MISTRAL_EMBED_DIM_1024` | `"mistral-embed"` | 1024 | `COSINE` |
| `MISTRAL_EMBED_DIM_256` | `"mistral-embed-dim256-2510"` | 256 | `COSINE` |
| `MISTRAL_EMBED_DIM_128` | `"mistral-embed-dim128-2510"` | 128 | `COSINE` |

Resolve a preset from a model name with `MistralEmbeddingPreset.from_name("mistral-embed")`.

Pair each preset with the matching `MistralEmbedder` constant on the pipeline:

| Schema preset | Embedder constant |
|---------------|-------------------|
| `MISTRAL_EMBED_DIM_1024` | `MODEL_1024_EMBEDDING` |
| `MISTRAL_EMBED_DIM_256` | `MODEL_256_EMBEDDING` |
| `MISTRAL_EMBED_DIM_128` | `MODEL_128_EMBEDDING` |

## Configure stored vectors {#vector-config}

Every `EmbeddingModel` carries three vector-config fields, also available as the `VectorConfig` protocol:

| Field | Type | Default | Purpose |
|--------|------|---------|---------|
| `dimensions` | `int` | *(required)* | Vector dimensionality; must be `>= 1` |
| `dtype` | `VectorDType` | `FLOAT32` | `FLOAT32` or `FLOAT16` |
| `distance_metric` | `DistanceMetric` | `COSINE` | `COSINE`, `INNER_PRODUCT`, or `L2` |

The schema layer uses these to size the embedding tensor and select the ranking metric (for example, cosine similarity vs. inner product).

## Keep the schema and embedder aligned {#schema-vs-embedder}

The `EmbeddingModel` on the schema describes the index; the embedder you pass to the `Pipeline` produces the vectors at query and ingestion time. They are separate concerns that must agree on dimensions:

- A `MistralEmbeddingModel` on the schema pairs with a `MistralEmbedder` using the matching `MODEL_*_EMBEDDING` constant.
- A `CustomEmbeddingModel` on the schema pairs with a custom `Embedder`.

Keep the dimensions in sync. The schema rejects vectors of the wrong size.

## See also {#see-also}

- **[Embedders](https://docs.mistral.ai/studio/search/search-toolkit/ingestion/embedders)**: the runtime side that produces vectors.
- **[Search index](https://docs.mistral.ai/studio/search/search-toolkit/search-index)**: where the schema and the embedding model live.
- **[Migration helpers](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/migration-helpers)**: `create_schema(embedding_model=...)` reference.
