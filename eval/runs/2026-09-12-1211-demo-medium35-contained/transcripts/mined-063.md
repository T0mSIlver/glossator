# mined-063 (single_page, 2 connector calls)

## Question

How many model calls does the LLM reranker make, and how should I keep its cost down?

## Thinking

The user is asking about the LLM reranker's model calls and cost optimization. I need to search the Mistral documentation for information about how the LLM reranker works, specifically how many model calls it makes and what the cost implications are. I'll use the mistral_docs_search tool to find relevant information.

The search returned a result about rerankers. I need to read the full page to get detailed information about the LLM reranker's behavior, particularly how many model calls it makes and cost considerations. Let me fetch the page content.

Now I have the information from the documentation. The LLM reranker makes one model call per chunk that it needs to score. The documentation explicitly states this. For cost optimization, I should explain the strategy of using a vector retriever to first narrow down to a manageable number of chunks (e.g., top 100) and then only rerank those, rather than reranking all possible chunks. This reduces the total number of LLM calls.

Let me structure the answer clearly:
1. Directly answer the number of model calls: 1 per chunk
2. Explain the cost optimization strategy: pre-filter with vector retriever
3. Provide the specific example from the docs
4. Cite the documentation properly

The key points are:
- 1 LLM call per chunk for scoring
- Cost optimization: use vector retriever to get top N chunks first, then only rerank those N chunks
- This reduces the number of LLM calls from "all chunks" to just the top N

I should make sure to include the exact citation from the documentation.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "LLM reranker number of model calls and cost reduction"}
```

Result:

```
q: "LLM reranker number of model calls and cost reduction"

[1] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers | section: llm-reranker
    Rerankers > LLM ReRanker
    Uses an LLM to re-score results with deeper understanding of relevance to the query. **Installation**: Core library (no extra required) **Example**: ```python from mistralai.search.toolkit.retrieval.rerankers import LLMReRanker from mistralai.search.toolkit.retrieval import QueryEngine from mistralai.search.toolkit.llm import MistralChat, LLMConfig from mistralai.client import Mistral llm = Mistra …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#llm-reranker

[2] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers | section: cross-encoder-reranker
    Rerankers > Cross-Encoder ReRanker
    Uses a hosted cross-encoder model optimized for reranking. Faster than LLM reranking but requires a dedicated model server. **Installation**: Core library (no extra required) **Example**: ```python from mistralai.search.toolkit.retrieval.rerankers import CrossEncoderReRanker from mistralai.search.toolkit.retrieval import QueryEngine reranker = CrossEncoderReRanker( base_url="http://localhost:8080" …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#cross-encoder-reranker

[3] https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning | section: where-can-i-find-information-on-cost-eta-number-of-tokens-number-of-passes-over-each-files
    Text & Vision Fine-tuning > FAQ > Where can I find information on cost/ ETA / number of tokens / number of passes over each files?
    Mistral API: When you create a fine-tuning job, you should automatically see these info with the default `auto_start=False` argument. Note that the `dry_run=True` argument will be removed in September. `mistral-finetune`: You can use the following script to find out: https://github.com/mistralai/mistral-finetune/blob/main/utils/validate_data.py. This script accepts a .yaml training file as input a …
    cite: https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#where-can-i-find-information-on-cost-eta-number-of-tokens-number-of-passes-over-each-files

[4] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers | section: available-rerankers
    Rerankers > Available rerankers
    | Reranker | Type | Purpose | |----------|------|---------| | **[LLM ReRanker](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#llm-reranker)** | ReRanker | Deep relevance scoring using an LLM | | **[Cross-Encoder ReRanker](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#cross-encoder-reranker)** | ReRanker | Fast reranking using dedicated model | | …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#available-rerankers

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

The **LLM reranker makes one LLM call per chunk** it scores for relevance.
To keep its cost down, first retrieve a larger set of results (e.g., top 100) with a fast vector retriever, then only pass that smaller subset to the LLM reranker for final scoring—this limits the number of LLM calls to the size of that subset rather than the entire corpus.

[LLM ReRanker – How it works & Cost optimization](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#llm-reranker)

