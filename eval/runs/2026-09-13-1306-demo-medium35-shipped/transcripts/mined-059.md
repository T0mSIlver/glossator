# mined-059 (single_page, 5 connector calls)

## Question

When is `RRFRanker` the right way to do hybrid search, and what does it need in front of it?

## Thinking

The user is asking about when to use RRFRanker for hybrid search and what prerequisites are needed. This is a specific technical question about Mistral's search capabilities. I need to search the Mistral documentation for information about RRFRanker, hybrid search, and its requirements. Let me start with a search query that combines these key terms.

I got a search result pointing to the retrievers documentation. This seems relevant. Let me read the full page to understand the context better and see if it contains the information about RRFRanker usage and requirements.

The first read gave me a section about hybrid search. I need more details about the RRFRanker itself. Let me search for more specific information about when to use RRFRanker and its requirements.

The previous search didn't give me the specific details I need. Let me read the RRFRanker documentation page directly to understand its purpose and requirements.

I have information from the RRFRanker page, but I need to understand the broader context of hybrid search. Let me read the agentic search documentation to see how RRFRanker fits into hybrid retrieval patterns.

Now I have enough information from the documentation. Let me synthesize what I've learned:

1. RRFRanker is used for hybrid search when you need to combine results from multiple retrievers
2. It uses Reciprocal Rank Fusion (RRF) which combines results based on rank positions without needing score normalization
3. It requires separate retrievers (vector and keyword) to be run first
4. The results from these retrievers are then fused using RRFRanker

I should structure my answer to directly address both parts of the user's question:
- When is RRFRanker the right way to do hybrid search?
- What does it need in front of it?

I'll organize this into clear sections with the key points, and include the citations from the documentation I found.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "RRFRanker hybrid search when to use and requirements"}
```

Result:

```
q: "RRFRanker hybrid search when to use and requirements"

[1] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers | section: hybrid-search
    Retrievers > Hybrid search
    If you have separate vector and custom keyword stores, run both retrievers and fuse their results. Pass the retrievers to `QueryEngine` and combine them with a fusion reranker such as `RRFRanker`: ```python from mistralai.search.toolkit.retrieval import QueryEngine from mistralai.search.toolkit.retrieval.retrievers import VectorRetriever, KeywordRetriever from mistralai.search.toolkit.retrieval.re …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers#hybrid-search

[2] https://docs.mistral.ai/studio/search/agentic-search | section: sdk-patterns
    Agentic Search > Use Agentic Search with the SDK > Core SDK patterns
    **Hybrid retrieval** Run multiple retrievers with different query profiles, then fuse the results with `RRFRanker` (Reciprocal Rank Fusion). This combines dense and hybrid retrieval for better coverage. ```python from mistralai.search.toolkit.retrieval.rerankers import RRFRanker dense_store = get_index("exampledocs", query_profile="dense") hybrid_store = get_index("exampledocs", query_profile="hyb …
    cite: https://docs.mistral.ai/studio/search/agentic-search#sdk-patterns:~:text=Hybrid%20retrieval%20Run

[3] https://docs.mistral.ai/studio/search/search-toolkit/search-index/postgres | section: requirements
    Postgres > Requirements
    The target database must have two extensions installed before you create a collection table: - [`vector`](https://github.com/pgvector/pgvector): provides HNSW indexing over embeddings. - [`pg_textsearch`](https://github.com/timescale/pg_textsearch): provides the BM25 access method for hybrid search. Add it to `shared_preload_libraries` before the server starts. `CREATE EXTENSION` fails until the s …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/search-index/postgres#requirements

[4] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers | section: rrf-ranker
    Rerankers > RRF Ranker
    **Configuration options**: | Option | Type | Default | Purpose | |--------|------|---------|---------| | `rrf_k` | int | 60 | Smoothing factor (try 30-100) | | `top_k` | int | 10 | Number of results to return | **Tuning RRF**: ```python # Lower rrf_k = more emphasis on exact rank positions RRFRanker(rrf_k=30, top_k=10) # Lower k, more differentiation # Higher rrf_k = less emphasis on rank position …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#rrf-ranker

[5] https://docs.mistral.ai/studio/search/search-toolkit/search-index/postgres | section: search/hybrid-search
    Postgres > Search > Hybrid search
    A `VectorSearchQuery` that contains both `query` and `embedding` runs both retrievers without extra configuration: ```python results = await store.search( VectorSearchQuery(query="quarterly revenue", embedding=vec, top_k=10) ) ``` Every collection's table carries a BM25 index over `content` (built by `pg_textsearch`). The two retrievers are combined by **weighted reciprocal rank fusion**: ```text …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/search-index/postgres#search

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

### 3. mistral_docs_search

```json
{"q": "when to use RRFRanker and what it requires"}
```

Result:

```
q: "when to use RRFRanker and what it requires"

[1] https://docs.mistral.ai/studio/workflows/building-workflows/payload_offloading | section: when-to-use-what
    Payload offloading > When to use what
    | Your problem | Use | |------|-----| | Activity I/O > 2MB, accessed only inside activities | **Activity field offloading** *(recommended)* | | Workflow input or activity I/O > 2MB, accessed in workflow code | **Payload offloading** | > **Tip** > > **Quick guide**: if you can keep your large data inside activities (most common case), use **activity field offloading**. It has none of the replay-tim …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/payload_offloading#when-to-use-what

[2] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers | section: rrf-ranker
    Rerankers > RRF Ranker
    **Configuration options**: | Option | Type | Default | Purpose | |--------|------|---------|---------| | `rrf_k` | int | 60 | Smoothing factor (try 30-100) | | `top_k` | int | 10 | Number of results to return | **Tuning RRF**: ```python # Lower rrf_k = more emphasis on exact rank positions RRFRanker(rrf_k=30, top_k=10) # Lower k, more differentiation # Higher rrf_k = less emphasis on rank position …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#rrf-ranker

[3] https://docs.mistral.ai/studio/workflows/getting-started/cookbook_examples | section: cargo-release/what-it-does
    Cookbook examples > Cargo release and dangerous goods compliance > What it does
    This cookbook automates cargo release for maritime logistics. It extracts the shipping document, classifies the cargo, runs dangerous goods checks when needed, validates customs compliance, and pauses for a reviewer if an anomaly is detected. Use this example when you want to understand `wait_for_input()`, child workflows, and typed LLM outputs in one end-to-end flow.
    cite: https://docs.mistral.ai/studio/workflows/getting-started/cookbook_examples#cargo-release

[4] https://docs.mistral.ai/studio/search/agentic-search | section: sdk-patterns
    Agentic Search > Use Agentic Search with the SDK > Core SDK patterns
    **Hybrid retrieval** Run multiple retrievers with different query profiles, then fuse the results with `RRFRanker` (Reciprocal Rank Fusion). This combines dense and hybrid retrieval for better coverage. ```python from mistralai.search.toolkit.retrieval.rerankers import RRFRanker dense_store = get_index("exampledocs", query_profile="dense") hybrid_store = get_index("exampledocs", query_profile="hyb …
    cite: https://docs.mistral.ai/studio/search/agentic-search#sdk-patterns:~:text=Hybrid%20retrieval%20Run

[5] https://docs.mistral.ai/studio/workflows/getting-started/cookbook_examples | section: insurance-claims/what-it-does
    Cookbook examples > Insurance claims triage with vision > What it does
    This cookbook triages an insurance claim from text and photo inputs. It analyzes claim photos in parallel, checks the written description for inconsistencies, assigns a deterministic severity, scores fraud risk, and returns a structured triage report. Use this example when you want to see how a workflow can combine parallel activity execution with deterministic routing and typed outputs.
    cite: https://docs.mistral.ai/studio/workflows/getting-started/cookbook_examples#insurance-claims

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/workflows/building-workflows/payload_offloading") to read hit 1 on its page
```

### 4. mistral_docs_read_page

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

### 5. mistral_docs_read_page

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

`RRFRanker` is the right way to do **hybrid search when you need to combine results from multiple, independent retrievers**—such as separate vector (dense) and keyword (sparse/BM25) stores, or multiple vector retrievers with different query profiles. It is especially useful when the retrievers produce **incomparable scores** (e.g., BM25 vs. cosine similarity) and you want a score-normalization-free fusion method. It is also suitable when you want to avoid additional model or cost constraints, as RRF operates purely on rank positions rather than raw scores.

---

### What `RRFRanker` needs in front of it:
- **At least two retrievers** (e.g., `VectorRetriever` and `KeywordRetriever`, or two `VectorRetriever` instances with different query profiles like `dense` and `hybrid`).
  These retrievers must be passed to a `QueryEngine`, and their results are then fused by `RRFRanker`.

- **Example setup**:
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
  ```
  This fuses the ranked results from both retrievers into a single, unified ranking.

