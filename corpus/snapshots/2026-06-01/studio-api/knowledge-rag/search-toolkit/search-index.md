---
url: https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/search-index
title: Search index
breadcrumbs: [Studio, Knowledge & RAG, Search Toolkit]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/knowledge-rag/search-toolkit/search-index/page.mdx
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
---

# Search index

Storage backends persist processed chunks and enable efficient search across your document collection. Vector stores enable semantic search by storing chunk embeddings and finding similar vectors.

## Available vector stores {#available-vector-stores}

| Vector Store | Purpose |
|--------------|---------|
| **[Vespa Search Index](https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/search-index#vespa-search-index)** | Scalable vector database with schema management and deployment |
| **[Custom Vector Stores](https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/search-index#custom-vector-stores)** | Custom storage backend |

## Vespa Search Index {#vespa-search-index}

Use Vespa as a vector store in Search Toolkit ingestion and retrieval pipelines. Vespa provides scalable vector search with schema management, ranking, and production-ready clustering.

> **Info**
>
> **Requirement**: You must have a **running Vespa application** before connecting with this search index. See **[Manage and deploy Vespa](https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/vespa)** to define schemas and deploy your application first.

**Features**:
- Scalable vector search natively optimized with HNSW indexing
- BM25 text search for hybrid ranking
- Multi-phase ranking with custom scoring functions
- Production-ready with clustering and replication support

**Installation**:

```bash
uv add "mistralai-search-toolkit[vespa]"
```

### Prerequisites

Before using Vespa as a search index:

1. **Define your application** — Create schemas with fields and ranking profiles using Python migrations
2. **Deploy Vespa** — Run `mistral-vespa migrate` to deploy your application
3. **Get the endpoint** — Note the Vespa query endpoint (e.g., `http://localhost:8080`)

See **[Manage and deploy Vespa](https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/vespa)** for complete setup instructions.

### Quick start

Configure Vespa as a vector store:

```python
from mistralai.search.toolkit.plugins.vespa import VespaClientConfig
from vespa_app import app

collection_name = "my_collection"
config = VespaClientConfig(
    endpoint="http://localhost:8080",
)

vector_store = app.get_search_index(config, collection_name=collection_name)
```

Use in an ingestion pipeline:

```python
from mistralai.search.toolkit.ingestion.pipelines import Pipeline

pipeline = Pipeline(
    loader=loader,
    extractor=extractor,
    text_splitter=splitter,
    embedder=embedder,
    stores=vector_store,
)

num_chunks = await pipeline.run(documents=["doc1.pdf", "doc2.pdf"])
```

Use in a retrieval pipeline:

```python
from mistralai.search.toolkit.retrieval import QueryEngine
from mistralai.search.toolkit.retrieval.retrievers import VectorRetriever

embedder = MistralEmbedder(client=mistral_client)
query_engine = QueryEngine(
    retriever=VectorRetriever(client=vector_store, embedder=embedder),
)

result = await query_engine.search(query="What is RAG?", top_k=5)
```

For comprehensive setup, schema design, and operations, see **[Manage and deploy Vespa](https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/vespa)**.

## Custom vector stores {#custom-vector-stores}

Implement custom storage backends by implementing the `VectorStoreClient` protocol:

```python
from mistralai.search.toolkit.indices import VectorStoreClient
from mistralai.search.toolkit.document import Document
from mistralai.search.toolkit.indices import VectorSearchQuery, SearchResult

class MyVectorStore(VectorStoreClient):
    async def create_index(self) -> bool:
        pass

    async def upsert(self, document: Document) -> bool:
        pass

    async def search(self, query: VectorSearchQuery) -> list[SearchResult]:
        pass

    async def delete_document(self, doc_id: str) -> None:
        pass
```
