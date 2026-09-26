---
url: https://docs.mistral.ai/studio/search/search-toolkit/search-index
title: Search index
breadcrumbs: [Studio, Search, Search Toolkit]
kind: doc
locale: en
source_path: src/content/en/docs/studio/search/search-toolkit/search-index/page.mdx
source_commit: bee3023d26c331c00fa6c24bc746ef4cf5e97031
---

# Search index

Storage backends persist processed chunks and enable efficient search across your document collection. Vector stores enable semantic search by storing chunk embeddings and finding similar vectors.

## Available backends {#available-vector-stores}

### Officially supported

| Backend | Purpose |
|---------|---------|
| **[Vespa](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa)** | Vector database with schema management, ranking, clustering, and replication |
| **[Postgres](https://docs.mistral.ai/studio/search/search-toolkit/search-index/postgres)** | PostgreSQL with `pgvector` and `pg_textsearch` for dense and hybrid search |

Both built-in backends implement the `VectorStoreIndex` protocol, so they use the same ingestion and retrieval pipeline interfaces. Their provisioning, schema management, and query-scoping behavior differ. See each backend's page for details.

### Community

| Backend | Purpose |
|---------|---------|
| **[Qdrant](https://docs.mistral.ai/studio/search/search-toolkit/search-index/qdrant)** | [Qdrant](https://qdrant.tech/) vector search engine, maintained as a third-party plugin |

Community backends are not part of the `mistralai-search-toolkit` package. Refer to each plugin's repository for installation and support.

### Custom backends

| Backend | Purpose |
|---------|---------|
| **[Custom vector stores](https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores)** | Implement your own storage backend |
