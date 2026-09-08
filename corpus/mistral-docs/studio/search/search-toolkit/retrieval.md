---
url: https://docs.mistral.ai/studio/search/search-toolkit/retrieval
title: Retrieval
breadcrumbs: [Studio, Search, Search Toolkit]
kind: doc
locale: en
source_path: src/content/en/docs/studio/search/search-toolkit/retrieval/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# Retrieval

Retrieval finds relevant chunks for a given user query. Search Toolkit supports vector (semantic), keyword (BM25), and hybrid search strategies that can be combined for optimal results.

An optional **query preprocessor** transforms the raw query before search — rewriting it for clarity or expanding it into multiple variants.

One or more **Retrievers** execute the search against the index. They can run in parallel and their results are merged.

An optional **Reranker** re-scores the merged results using a more precise scoring strategy — an LLM, a cross-encoder, or rank fusion across multiple result sets.

## Query engine {#query-engine}

`QueryEngine` orchestrates the retrieval pipeline. It accepts one or more retrievers, optional query preprocessing, and optional rerankers:

```python
from mistralai.search.toolkit.retrieval import QueryEngine
from mistralai.search.toolkit.retrieval.retrievers import VectorRetriever
from mistralai.search.toolkit.retrieval.rerankers import LLMReRanker
from mistralai.search.toolkit.retrieval.pre_processors import LLMQueryRewriter

query_engine = QueryEngine(
    retriever=vector_retriever,       # Also accepts a list of retrievers
    query_rewriter=query_rewriter,    # Optional
    rerankers=[llm_reranker],         # Optional, supports ReRanker and GroupedRanker
)

result = await query_engine.search(
    query="What is RAG?",
    top_k=10,
    include_metadata=True,
    include_content=True,
)

print(f"Original query: {result.original_query}")
print(f"Results: {len(result.results)}")
```

## Components {#components}

Each retrieval component is documented in detail with examples and best practices:

- **[Retrievers](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers)**: VectorRetriever, KeywordRetriever, and hybrid search patterns
- **[Rerankers](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers)**: LLMReRanker, CrossEncoderReRanker, RRF fusion, and custom rerankers
- **[Query preprocessing](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/preprocessing)**: Query rewriting and expansion for better retrieval quality
- **[Semantic cache](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache)**: Cache results by query similarity to reduce latency
