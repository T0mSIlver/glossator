---
url: https://docs.mistral.ai/studio/search/search-toolkit/search-index
title: Search index
breadcrumbs: [Studio, Search, Search Toolkit]
kind: doc
locale: en
source_path: src/content/en/docs/studio/search/search-toolkit/search-index/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# Search index

Storage backends persist processed chunks and enable efficient search across your document collection. Vector stores enable semantic search by storing chunk embeddings and finding similar vectors.

## Available backends {#available-vector-stores}

| Backend | Purpose |
|---------|---------|
| **[Vespa](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa)** | Vector database with schema management, ranking, clustering, and replication |
| **[Postgres](https://docs.mistral.ai/studio/search/search-toolkit/search-index/postgres)** | PostgreSQL with `pgvector` and `pg_textsearch` for dense and hybrid search |
| **[Custom vector stores](https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores)** | Implement your own storage backend |

Both built-in backends implement the `VectorStoreIndex` protocol, so they use the same ingestion and retrieval pipeline interfaces. Their provisioning, schema management, and query-scoping behavior differ. See each backend's page for details.
