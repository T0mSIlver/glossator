# hist-003 (history, 4 connector calls)

## Question

When was the Agentic Search page added to the Search Toolkit documentation?

## Thinking

The user wants to know when the "Agentic Search" page was added to the Search Toolkit documentation. This is a question about the history of a specific documentation page. I need to use the mistral_docs_history tool to track when this page first appeared.

I should search for the page itself first to understand its context, then check its history. Let me start by searching for the Agentic Search page in the documentation.

I got an error because I provided both `under` and `text` parameters, but the tool requires exactly one of them. Let me try again with just the `under` parameter to track the Search Toolkit path.

The path format seems incorrect. Let me try searching for the Agentic Search page directly to find its actual URL first.

Good, I found the Agentic Search page at `https://docs.mistral.ai/studio/search/agentic-search`. Now I need to find when this page was added. Let me use the history tool with the page_url parameter.

Perfect! The history tool shows that the Agentic Search page was:
- Absent on 2026-06-01
- Absent through 2026-08-15
- Added between 2026-08-15 and 2026-09-01
- Same through 2026-09-07

So the page was added sometime between August 15, 2026 and September 1, 2026. This is the most precise answer I can give based on the available data.

## Tool calls

### 1. mistral_docs_history

```json
{"under": "docs.mistral.ai/api/search-toolkit", "text": "Agentic Search"}
```

Result:

```
Error executing tool mistral_docs_ca30_mistral_docs_history: error: E_BAD_PARAM
history takes exactly one of text, page_url or under.
next: mistral_docs_history(text="phrase"), mistral_docs_history(page_url="url", section="key") or mistral_docs_history(under="path", since="date").
```

### 2. mistral_docs_history

```json
{"under": "docs.mistral.ai/api/search-toolkit"}
```

Result:

```
Error executing tool mistral_docs_ca30_mistral_docs_history: error: E_BAD_PARAM
no stored page exists under "https://docs.mistral.ai/docs.mistral.ai/api/search-toolkit".
next: pass one documented history form.
```

### 3. mistral_docs_search

```json
{"q": "Agentic Search page in Search Toolkit documentation"}
```

Result:

```
q: "Agentic Search page in Search Toolkit documentation"

[1] https://docs.mistral.ai/studio/search/agentic-search | section: agentic-search
    Agentic Search
    Agentic Search helps agents answer questions when the answer is not in the first chunk returned by retrieval. Instead of searching again and hoping for a better result, the model can work inside the corpus: search to find a source, open it, move through nearby chunks, grep for exact terms, and search again without repeating chunks. In short, retrieval finds likely sources. Agentic Search lets the …
    cite: https://docs.mistral.ai/studio/search/agentic-search

[2] https://docs.mistral.ai/studio/search/agentic-search | section: use-with-sdk
    Agentic Search > Use Agentic Search with the SDK
    If you need more control than the MCP server provides, build retrieval pipelines directly with the Search Toolkit SDK. The SDK gives you the same `QueryEngine` and `VectorRetriever` that the MCP server uses, plus advanced features like query rewriting, multi-retriever fusion, and semantic caching.
    cite: https://docs.mistral.ai/studio/search/agentic-search#use-with-sdk

[3] https://docs.mistral.ai/studio/search/agentic-search | section: next-steps
    Agentic Search > Next steps
    - [Search Toolkit](https://docs.mistral.ai/studio/search/search-toolkit): learn about ingestion pipelines, retrieval strategies, and the full SDK. - [Libraries](https://docs.mistral.ai/studio/search/libraries): use managed document ingestion and search for built-in RAG. - [Connectors](https://docs.mistral.ai/studio/connectors): connect models and agents to external tools and data sources. - [Agent …
    cite: https://docs.mistral.ai/studio/search/agentic-search#next-steps

[4] https://docs.mistral.ai/studio/search/agentic-search | section: latency
    Agentic Search > Latency and tradeoffs
    Each tool call has a cost, but navigation can reduce end-to-end latency and token usage because the model converges faster. Instead of repeatedly issuing broad searches, the agent can stay inside the right source, use `grep` to jump to specific terms, and use `exclude_ids` to avoid revisiting the same chunks. In the Agentic Search benchmarks cited in the Search Toolkit launch materials, the full a …
    cite: https://docs.mistral.ai/studio/search/agentic-search#latency

[5] https://docs.mistral.ai/studio/search/agentic-search | section: sdk-patterns
    Agentic Search > Use Agentic Search with the SDK > Core SDK patterns
    The SDK snippets build from the smallest setup to more advanced retrieval. Use the tabs to start with the client, run a query, then add preprocessing or hybrid retrieval. **Client** ```python from mistralai.client import Mistral from mistralai.search.toolkit.embedders import MistralEmbedder client = Mistral(api_key="your-api-key") embedder = MistralEmbedder(client=client) ``` **Query engine** Crea …
    cite: https://docs.mistral.ai/studio/search/agentic-search#sdk-patterns

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/agentic-search") to read hit 1 on its page
```

### 4. mistral_docs_history

```json
{"page_url": "https://docs.mistral.ai/studio/search/agentic-search"}
```

Result:

```
history page: https://docs.mistral.ai/studio/search/agentic-search
absent at 2026-06-01
absent through 2026-08-15
added between 2026-08-15 and 2026-09-01 | https://docs.mistral.ai/studio/search/agentic-search
same through 2026-09-07 | https://docs.mistral.ai/studio/search/agentic-search
Results: 8 of 8 stored snapshots
```

## Answer

The **Agentic Search** page in the Search Toolkit documentation was added between **August 15, 2026, and September 1, 2026**.

[Agentic Search page history](https://docs.mistral.ai/studio/search/agentic-search)

