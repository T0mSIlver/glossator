---
url: https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/retrieval/retrievers
title: Retrievers
breadcrumbs: [Studio, Knowledge & RAG, Search Toolkit, Retrieval]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/knowledge-rag/search-toolkit/retrieval/retrievers/page.mdx
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
---

# Retrievers

Retrievers execute the search against your index. Search Toolkit provides vector (semantic) retrievers for semantic search over your documents.

## Available retrievers {#available-retrievers}

| Retriever | Purpose |
|-----------|---------|
| **[Vector Retriever](https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/retrieval/retrievers#vector-retriever)** | Semantic search using embeddings |
| **[Custom Retrievers](https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/retrieval/retrievers#custom-retrievers)** | Custom search logic |

## Vector Retriever {#vector-retriever}

Performs semantic search using embeddings. Finds chunks with similar meaning to the query, even if they use different words.

**Installation**: Core library (no extra required)

**Example**:

```python
from mistralai.search.toolkit.retrieval.retrievers import VectorRetriever

retriever = VectorRetriever(
    client=vector_store,  # Vector store client (Vespa or custom implementation)
    embedder=embedder,    # MistralEmbedder or custom Embedder
)

results = await retriever.retrieve(
    query="What is semantic search?",
    top_k=10,
)
```

**Configuration options**:

| Option | Type | Default | Purpose |
|--------|------|---------|---------|
| `client` | VectorStoreClient | Required | Vector store to search |
| `embedder` | Embedder | Required | Embedder for query vectorization |

**Filtering**:

Filter by metadata to narrow results:

```python
results = await retriever.retrieve(
    query="machine learning",
    top_k=10,
    filter={"category": "tutorials", "year": 2024},  # Depends on store support
)
```

> **Info**
>
> Filtering support depends on your vector store backend. Vespa supports metadata filtering natively.

**When to use**:
- General semantic search across your documents
- Finding conceptually similar content
- Handling synonyms and paraphrasing naturally

## Custom retrievers {#custom-retrievers}

Implement the `Retriever` protocol for custom search logic:

```python
from mistralai.search.toolkit.retrieval.retrievers import Retriever
from mistralai.search.toolkit.indices import SearchResult

class CustomRetriever(Retriever):
    """Custom retriever with domain-specific logic."""

    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filter: dict | None = None,
    ) -> list[SearchResult]:
        """Retrieve relevant chunks for the query."""
        # 1. Preprocess query
        processed_query = self._preprocess(query)

        # 2. Search with custom logic
        results = await self._search(processed_query, top_k, filter)

        # 3. Post-process or augment results
        enhanced_results = self._enhance(results)

        return enhanced_results

    def _preprocess(self, query: str) -> str:
        # Custom preprocessing (stemming, lemmatization, etc.)
        return query.lower().strip()

    async def _search(self, query: str, top_k: int, filter: dict) -> list[SearchResult]:
        # Custom search implementation
        ...

    def _enhance(self, results: list[SearchResult]) -> list[SearchResult]:
        # Augment results with additional context
        ...

# Use in QueryEngine
query_engine = QueryEngine(retriever=CustomRetriever())
```

## See also {#see-also}

- [Retrieval overview](https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/retrieval) — Retrieval pipeline architecture
- [Rerankers](https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/retrieval/rerankers) — Re-score results for better ranking
- [Query preprocessing](https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/retrieval/preprocessing) — Improve queries before retrieval
