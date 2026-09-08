---
url: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers
title: Retrievers
breadcrumbs: [Studio, Search, Search Toolkit, Retrieval]
kind: doc
locale: en
source_path: src/content/en/docs/studio/search/search-toolkit/retrieval/retrievers/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# Retrievers

Retrievers execute the search against your index. Search Toolkit provides vector (semantic) and keyword (BM25) retrievers, which you can combine for hybrid search.

## Available retrievers {#available-retrievers}

| Retriever | Purpose |
|-----------|---------|
| **[Vector Retriever](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers#vector-retriever)** | Semantic search using embeddings |
| **[Keyword Retriever](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers#keyword-retriever)** | BM25 / keyword search |
| **[Hybrid search](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers#hybrid-search)** | Combine vector and keyword retrievers |
| **[Custom Retrievers](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers#custom-retrievers)** | Custom search logic |

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
| `client` | VectorStoreIndex | Required | Vector store to search |
| `embedder` | Embedder | Required | Embedder for query vectorization |

**When to use**:
- General semantic search across your documents
- Finding conceptually similar content
- Handling synonyms and paraphrasing naturally

## Keyword Retriever {#keyword-retriever}

Performs keyword search against a `KeywordStoreIndex`. It finds chunks that share terms with the query and ranks them by lexical relevance.

> **Info**
>
> The built-in Vespa and Postgres backends don't implement `KeywordStoreIndex`. Use `KeywordRetriever` with a custom keyword store. For hybrid search with a built-in backend, use `VectorRetriever`; it sends both the query text and embedding to the backend.

**Installation**: Core library (no extra required)

**Example**:

```python
from mistralai.search.toolkit.retrieval.retrievers import KeywordRetriever

retriever = KeywordRetriever(
    client=keyword_store,  # Custom KeywordStoreIndex implementation
)

results = await retriever.retrieve(
    query="quarterly revenue report",
    top_k=10,
)
```

**Configuration options**:

| Option | Type | Default | Purpose |
|--------|------|---------|---------|
| `client` | KeywordStoreIndex | Required | Keyword store to search |

**When to use**:
- Exact-term matching (names, identifiers, error codes)
- Queries where lexical relevance matters more than semantics
- As one arm of a hybrid search (see below)

## Hybrid search {#hybrid-search}

If you have separate vector and custom keyword stores, run both retrievers and fuse their results. Pass the retrievers to `QueryEngine` and combine them with a fusion reranker such as `RRFRanker`:

```python
from mistralai.search.toolkit.retrieval import QueryEngine
from mistralai.search.toolkit.retrieval.retrievers import VectorRetriever, KeywordRetriever
from mistralai.search.toolkit.retrieval.rerankers import RRFRanker

query_engine = QueryEngine(
    retriever=[
        VectorRetriever(client=vector_store, embedder=embedder),
        KeywordRetriever(client=keyword_store),
    ],
    rerankers=[RRFRanker(rrf_k=60, top_k=10)],
)

result = await query_engine.search(query="What is RAG?", top_k=10)
```

See [Rerankers](rerankers) for RRF and other fusion strategies.

## Custom retrievers {#custom-retrievers}

Implement the `Retriever` protocol for custom search logic:

```python
from mistralai.search.toolkit.context import RetrievalContext
from mistralai.search.toolkit.retrieval.retrievers import Retriever
from mistralai.search.toolkit.search import SearchResult

class CustomRetriever(Retriever):
    """Custom retriever with domain-specific logic."""

    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        include_metadata: bool = True,
        include_content: bool = True,
        context: RetrievalContext = RetrievalContext(),
    ) -> list[SearchResult]:
        """Retrieve relevant chunks for the query."""
        # 1. Preprocess query
        processed_query = self._preprocess(query)

        # 2. Search with custom logic
        results = await self._search(processed_query, top_k)

        # 3. Post-process or augment results
        enhanced_results = self._enhance(results)

        return enhanced_results

    def _preprocess(self, query: str) -> str:
        # Custom preprocessing (stemming, lemmatization, etc.)
        return query.lower().strip()

    async def _search(self, query: str, top_k: int) -> list[SearchResult]:
        # Custom search implementation
        ...

    def _enhance(self, results: list[SearchResult]) -> list[SearchResult]:
        # Augment results with additional context
        ...

# Use in QueryEngine
query_engine = QueryEngine(retriever=CustomRetriever())
```

## See also {#see-also}

- [Retrieval overview](../retrieval): retrieval pipeline architecture
- [Rerankers](rerankers): re-score results for better ranking
- [Query preprocessing](preprocessing): improve queries before retrieval
