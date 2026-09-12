# mined-059 (single_page, 4 connector calls)

## Question

When is `RRFRanker` the right way to do hybrid search, and what does it need in front of it?

## Thinking

The user is asking about RRFRanker for hybrid search. They want to know:
1. When it's the right choice
2. What it needs in front of it (pre-requisites)

I need to search Mistral's documentation for information about RRFRanker, hybrid search, and its usage patterns. Let me start by searching for RRFRanker specifically.

I got some search results. Let me read the retrievers page to understand the hybrid search section and how RRFRanker fits in.

Good, I have the hybrid search section. Now let me read the RRFRanker documentation to understand its configuration and when it's appropriate.

Perfect. Now I have the RRFRanker documentation. Let me also check the agentic search page to see if there are additional context about when to use RRFRanker.

Now I have enough information to answer the user's question. Let me synthesize:

From the documentation:
1. **When to use RRFRanker**: It's the right choice when you need to combine results from multiple retrievers with different strategies (dense vectors, hybrid search, keyword search) or from separate stores. It's particularly useful when:
   - You have separate vector and keyword stores
   - You want to fuse results from multiple retrieval strategies on the same index
   - The results come from sources with incomparable scores
   - You want fusion without score normalization
   - There are no additional model or cost constraints

2. **What it needs in front of it**: RRFRanker needs:
   - Multiple retrievers (at least two) that have already executed their searches
   - These retrievers can be: VectorRetriever, KeywordRetriever, or VectorRetrievers with different query profiles
   - The retrievers are passed to a QueryEngine
   - RRFRanker is then used as a reranker to fuse the results from these multiple retrievers

The key insight is that RRFRanker is a **fusion reranker** that combines already-retrieved results, not a standalone retriever. It needs multiple retrieval pipelines in front of it.

Let me structure this answer clearly with the key points and examples from the docs.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "RRFRanker hybrid search when to use", "max_hits": 5}
```

Result:

```
q: "RRFRanker hybrid search when to use"

[1] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers | section: hybrid-search
    Retrievers > Hybrid search
    If you have separate vector and custom keyword stores, run both retrievers and fuse their results. Pass the retrievers to `QueryEngine` and combine them with a fusion reranker such as `RRFRanker`: ```python from mistralai.search.toolkit.retrieval import QueryEngine from mistralai.search.toolkit.retrieval.retrievers import VectorRetriever, KeywordRetriever from mistralai.search.toolkit.retrieval.re …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers#hybrid-search

[2] https://docs.mistral.ai/studio/search/agentic-search | section: sdk-patterns
    Agentic Search > Use Agentic Search with the SDK > Core SDK patterns
    **Hybrid retrieval** Run multiple retrievers with different query profiles, then fuse the results with `RRFRanker` (Reciprocal Rank Fusion). This combines dense and hybrid retrieval for better coverage. ```python from mistralai.search.toolkit.retrieval.rerankers import RRFRanker dense_store = get_index("exampledocs", query_profile="dense") hybrid_store = get_index("exampledocs", query_profile="hyb …
    cite: https://docs.mistral.ai/studio/search/agentic-search#sdk-patterns:~:text=Hybrid%20retrieval%20Run

[3] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers | section: rrf-ranker
    Rerankers > RRF Ranker
    **Configuration options**: | Option | Type | Default | Purpose | |--------|------|---------|---------| | `rrf_k` | int | 60 | Smoothing factor (try 30-100) | | `top_k` | int | 10 | Number of results to return | **Tuning RRF**: ```python # Lower rrf_k = more emphasis on exact rank positions RRFRanker(rrf_k=30, top_k=10) # Lower k, more differentiation # Higher rrf_k = less emphasis on rank position …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#rrf-ranker

[4] https://docs.mistral.ai/studio/search/search-toolkit/search-index/postgres | section: search/hybrid-search
    Postgres > Search > Hybrid search
    A `VectorSearchQuery` that contains both `query` and `embedding` runs both retrievers without extra configuration: ```python results = await store.search( VectorSearchQuery(query="quarterly revenue", embedding=vec, top_k=10) ) ``` Every collection's table carries a BM25 index over `content` (built by `pg_textsearch`). The two retrievers are combined by **weighted reciprocal rank fusion**: ```text …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/search-index/postgres#search

[5] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers | section: chaining-rerankers
    Rerankers > Chaining rerankers
    Multiple rerankers can be applied in sequence for progressive refinement: ```python from mistralai.search.toolkit.retrieval.rerankers import RRFRanker, LLMReRanker query_engine = QueryEngine( retriever=[dense_retriever, hybrid_retriever], rerankers=[ RRFRanker(rrf_k=60, top_k=50), # Step 1: Fuse results → top 50 MetadataReRanker(), # Step 2: Boost verified content LLMReRanker(llm_provider=llm, top …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#chaining-rerankers

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers") to read hit 1 on its page
```

### 2. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers", "section": "hybrid-search"}
```

Result:

```
page: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers | "Retrievers" | section: hybrid-search

## section: hybrid-search
    Retrievers > Hybrid search
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers#hybrid-search
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

See [Rerankers](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers) for RRF and other fusion strategies.

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers", section="custom-retrievers") for the section after it
```

### 3. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers", "section": "rrf-ranker"}
```

Result:

```
page: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers | "Rerankers" | section: rrf-ranker

## section: rrf-ranker
    Rerankers > RRF Ranker
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#rrf-ranker
## RRF Ranker {#rrf-ranker}

Reciprocal Rank Fusion (RRF) combines results from multiple retrievers using rank positions. Useful for fusing different retrieval strategies on the same index.

**Installation**: Core library (no extra required)

**Example**: multiple vector retrievers with different query profiles:

```python
from mistralai.client import Mistral
from mistralai.search.toolkit.embedding import MistralEmbedder, MODEL_1024_EMBEDDING
from mistralai.search.toolkit.retrieval.retrievers import VectorRetriever
from mistralai.search.toolkit.retrieval.rerankers import RRFRanker
from mistralai.search.toolkit.retrieval import QueryEngine
from mistralai.search.toolkit.plugins.vespa import VespaClientConfig
from vespa_app import app

# Initialize embedder for query vectorization
embedder = MistralEmbedder(
    client=Mistral(api_key="your-api-key"),
    model_name=MODEL_1024_EMBEDDING,
)

# Create Vespa search backends with different query profiles
config = VespaClientConfig(
    endpoint="http://localhost:8080",
)

# Use different query profiles for dense and hybrid search
dense_store = app.get_search_index(config, collection_name="my_collection", query_profile="dense")
hybrid_store = app.get_search_index(config, collection_name="my_collection", query_profile="hybrid")

# Create retrievers with different strategies
dense_retriever = VectorRetriever(client=dense_store, embedder=embedder)
hybrid_retriever = VectorRetriever(client=hybrid_store, embedder=embedder)

# Fuse results with RRF
query_engine = QueryEngine(
    retriever=[dense_retriever, hybrid_retriever],
    rerankers=[RRFRanker(rrf_k=60, top_k=10)],
)

result = await query_engine.search(query="How does RAG work?", top_k=10)
```

**Configuration options**:

**Configuration options**:

| Option | Type | Default | Purpose |
|--------|------|---------|---------|
| `rrf_k` | int | 60 | Smoothing factor (try 30-100) |
| `top_k` | int | 10 | Number of results to return |

**Tuning RRF**:

```python
# Lower rrf_k = more emphasis on exact rank positions
RRFRanker(rrf_k=30, top_k=10)  # Lower k, more differentiation

# Higher rrf_k = less emphasis on rank positions
RRFRanker(rrf_k=100, top_k=10)  # Higher k, flattens differences
```

**When to use**:
- Combining multiple retrieval strategies on the same index (dense vectors, hybrid search, etc.)
- Results from multiple sources with incomparable scores
- No additional model or cost constraints
- Fusion that doesn't require score normalization

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers", section="chaining-rerankers") for the section after it
```

### 4. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/search/agentic-search", "section": "sdk-patterns"}
```

Result:

```
page: https://docs.mistral.ai/studio/search/agentic-search | "Agentic Search" | section: sdk-patterns

## section: sdk-patterns
    Agentic Search > Use Agentic Search with the SDK > Core SDK patterns
    cite: https://docs.mistral.ai/studio/search/agentic-search#sdk-patterns
### Core SDK patterns {#sdk-patterns}

The SDK snippets build from the smallest setup to more advanced retrieval. Use the tabs to start with the client, run a query, then add preprocessing or hybrid retrieval.

**Client**

```python
from mistralai.client import Mistral
from mistralai.search.toolkit.embedders import MistralEmbedder

client = Mistral(api_key="your-api-key")
embedder = MistralEmbedder(client=client)
```

**Query engine**

Create a `QueryEngine` with a `VectorRetriever` backed by your search index:

```python
from mistralai.search.toolkit.retrieval import QueryEngine, VectorRetriever
from search_app import get_index

vector_store = get_index("exampledocs")
query_engine = QueryEngine(
    retriever=[VectorRetriever(client=vector_store, embedder=embedder)],
)

result = await query_engine.search(
    query="What is RAG?",
    top_k=5,
    include_metadata=True,
    include_content=True,
)

for hit in result.results:
    print(f"Score: {hit.score:.3f}")
    print(f"Content: {hit.chunk.content[:200]}")
```

**Preprocessing**

Two preprocessors are particularly relevant for agentic behavior:

- `LLMQueryExtension` breaks a query into sub-queries. Each runs an independent retrieval pass, and the results are combined. This improves recall for multi-faceted questions.
- `LLMQueryRewriter` rewrites informal queries into a more structured form before retrieval.

```python
from mistralai.search.toolkit.retrieval.pre_processors import LLMQueryExtension
from mistralai.search.toolkit.llm import MistralChat, LLMConfig

llm = MistralChat(
    client=client,
    config=LLMConfig(model="mistral-small-latest"),
)

query_engine = QueryEngine(
    retriever=[VectorRetriever(client=vector_store, embedder=embedder)],
    query_rewriter=LLMQueryExtension(llm_provider=llm, num_queries=3),
)
```

**Hybrid retrieval**

**Hybrid retrieval**

Run multiple retrievers with different query profiles, then fuse the results with `RRFRanker` (Reciprocal Rank Fusion). This combines dense and hybrid retrieval for better coverage.

```python
from mistralai.search.toolkit.retrieval.rerankers import RRFRanker

dense_store = get_index("exampledocs", query_profile="dense")
hybrid_store = get_index("exampledocs", query_profile="hybrid")

query_engine = QueryEngine(
    retriever=[
        VectorRetriever(client=dense_store, embedder=embedder),
        VectorRetriever(client=hybrid_store, embedder=embedder),
    ],
    rerankers=[RRFRanker(rrf_k=60, top_k=10)],
)
```

You can chain rerankers from cheap to expensive for progressive refinement. For example, fuse with `RRFRanker` first, then apply an `LLMReRanker` for a final quality pass.

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/agentic-search", section="ingest-documents") for the section after it
```

## Answer

`RRFRanker` is the right way to do hybrid search **when you need to combine results from multiple, independent retrievers**—for example, a dense vector store and a keyword/BM25 store, or multiple vector retrievers with different query profiles. It fuses their ranked lists without requiring score normalization, which is ideal when the scores from each source are incomparable (e.g., cosine similarity vs. BM25) or when you want to avoid extra model or cost overheads.
[When to use RRFRanker](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#rrf-ranker)

**What it needs in front of it:**
- **At least two retrievers** (e.g., `VectorRetriever` + `KeywordRetriever`, or two `VectorRetriever`s with different query profiles like `dense` and `hybrid`).
- These retrievers must be passed to a `QueryEngine`, and `RRFRanker` is added as a reranker to fuse their results.
[Hybrid search setup](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers#hybrid-search)
[SDK pattern for hybrid retrieval](https://docs.mistral.ai/studio/search/agentic-search#sdk-patterns:~:text=Hybrid%20retrieval%20Run)

