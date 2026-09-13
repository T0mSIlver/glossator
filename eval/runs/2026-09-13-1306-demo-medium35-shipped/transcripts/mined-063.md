# mined-063 (single_page, 2 connector calls)

## Question

How many model calls does the LLM reranker make, and how should I keep its cost down?

## Thinking

The user is asking about the LLM reranker's model calls and cost optimization. I need to find documentation about Mistral's LLM reranker to answer this accurately. Let me search for information about how many model calls it makes and cost reduction strategies.

The search returned a relevant result about rerankers. I need to read the full page to get the complete details about the LLM reranker's behavior and cost optimization recommendations.

I have the information from the documentation. The LLM reranker makes 1 LLM call per chunk. The documentation provides specific cost optimization strategies. I should structure the answer clearly: first state the number of calls, then explain the cost implications, and finally provide the optimization recommendations with the example code. I need to include the citation link as shown in the original response.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "LLM reranker model calls cost"}
```

Result:

```
q: "LLM reranker model calls cost"

[1] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers | section: llm-reranker
    Rerankers > LLM ReRanker
    **Cost optimization**: LLM reranking is expensive (1 LLM call per chunk). Reduce cost by: ```python # 1. Get many results from retriever (fast) query_engine = QueryEngine( retriever=vector_retriever, rerankers=[LLMReRanker(llm_provider=llm, top_k=10)], ) # 2. Vector retriever returns top 100 to reranker (cheaper than querying LLM for all) result = await query_engine.search(query="...", top_k=10) ` …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#llm-reranker:~:text=Cost%20optimization%3A%20LLM

[2] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers | section: cross-encoder-reranker
    Rerankers > Cross-Encoder ReRanker
    Uses a hosted cross-encoder model optimized for reranking. Faster than LLM reranking but requires a dedicated model server. **Installation**: Core library (no extra required) **Example**: ```python from mistralai.search.toolkit.retrieval.rerankers import CrossEncoderReRanker from mistralai.search.toolkit.retrieval import QueryEngine reranker = CrossEncoderReRanker( base_url="http://localhost:8080" …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#cross-encoder-reranker

[3] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers | section: available-rerankers
    Rerankers > Available rerankers
    | Reranker | Type | Purpose | |----------|------|---------| | **[LLM ReRanker](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#llm-reranker)** | ReRanker | Deep relevance scoring using an LLM | | **[Cross-Encoder ReRanker](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#cross-encoder-reranker)** | ReRanker | Fast reranking using dedicated model | | …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#available-rerankers

[4] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/preprocessing | section: llm-query-rewriter
    Query preprocessing > LLM Query Rewriter
    **When to use**: - Short or informal queries that need expansion - Queries with acronyms or domain-specific abbreviations - Improving recall for vague user input - Converting questions into keyword combinations **Cost considerations**: - 1 LLM call per query - Adds 100-500ms latency - Use strategically, not for every query
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/preprocessing#llm-query-rewriter

[5] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/preprocessing | section: llm-query-extension
    Query preprocessing > LLM Query Extension
    Breaks a query into multiple sub-queries exploring different facets. Each sub-query runs an independent retrieval pass; results are combined for broader recall. **Installation**: Core library (no extra required) **Example**: ```python from mistralai.search.toolkit.retrieval.pre_processors import LLMQueryExtension from mistralai.search.toolkit.llm import MistralChat, LLMConfig from mistralai.client …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/preprocessing#llm-query-extension

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers") to read hit 1 on its page
```

### 2. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers", "section": "llm-reranker"}
```

Result:

```
page: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers | "Rerankers" | section: llm-reranker

## section: llm-reranker
    Rerankers > LLM ReRanker
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#llm-reranker
## LLM ReRanker {#llm-reranker}

Uses an LLM to re-score results with deeper understanding of relevance to the query.

**Installation**: Core library (no extra required)

**Example**:

```python
from mistralai.search.toolkit.retrieval.rerankers import LLMReRanker
from mistralai.search.toolkit.retrieval import QueryEngine
from mistralai.search.toolkit.llm import MistralChat, LLMConfig
from mistralai.client import Mistral

llm = MistralChat(
    client=Mistral(api_key="your-api-key"),
    config=LLMConfig(
        model="mistral-small-latest",
        temperature=0.1,
        response_format={"type": "json_object"},
    ),
)

reranker = LLMReRanker(
    llm_provider=llm,
    top_k=10,  # Return top 10 after reranking
)

# Use in QueryEngine
query_engine = QueryEngine(
    retriever=vector_retriever,
    rerankers=[reranker],
)

result = await query_engine.search(query="What is RAG?", top_k=10)
```

**Configuration options**:

| Option | Type | Default | Purpose |
|--------|------|---------|---------|
| `llm_provider` | LLMProvider | Required | LLM to use for scoring (MistralChat, etc.) |
| `top_k` | int \| None | `None` | Number of results to return after reranking (`None` returns all) |

**How it works**:
1. LLM receives the query and retrieved chunks
2. LLM scores relevance for each chunk
3. Chunks are sorted by LLM score
4. Top-k results are returned

**When to use**:
- Semantic relevance judgments beyond vector similarity
- Complex domain knowledge required for ranking
- After initial retrieval to improve quality
- Lower throughput tolerance (LLM calls are slower)

**Cost optimization**:

LLM reranking is expensive (1 LLM call per chunk). Reduce cost by:

**Cost optimization**:

LLM reranking is expensive (1 LLM call per chunk). Reduce cost by:

```python
# 1. Get many results from retriever (fast)
query_engine = QueryEngine(
    retriever=vector_retriever,
    rerankers=[LLMReRanker(llm_provider=llm, top_k=10)],
)

# 2. Vector retriever returns top 100 to reranker (cheaper than querying LLM for all)
result = await query_engine.search(query="...", top_k=10)
```

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers", section="cross-encoder-reranker") for the section after it
```

## Answer

The Mistral LLM reranker makes **1 LLM call per chunk** it evaluates. To keep its cost down, you should:

- **Pre-filter with a vector retriever**: Have the vector retriever return a large candidate set (e.g., top 100) and then only rerank those 100 with the LLM, rather than sending every chunk in your corpus to the LLM.
- **Limit the reranker’s `top_k`**: Only ask the reranker to return the final top-*k* results (e.g., 10) instead of rescoring everything.

[LLM ReRanker – Cost optimization](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#llm-reranker)

