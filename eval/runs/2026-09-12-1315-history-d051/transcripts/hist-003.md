# hist-003 (history, 3 connector calls)

## Question

When was the Agentic Search page added to the Search Toolkit documentation?

## Thinking

The user is asking about when a specific page ("Agentic Search") was added to the Search Toolkit documentation. This is a historical question about documentation changes. I need to use the `mistral_docs_history` tool to track when this page appeared in the documentation.

I should search for the phrase "Agentic Search" and look under the Search Toolkit path. Let me start by checking the history for this specific phrase.

The error indicates that the path doesn't exist. Let me try a broader search. I should first search for the "Agentic Search" page in the documentation to find its actual URL, then check its history.

Good, I found the page at `https://docs.mistral.ai/studio/search/agentic-search`. Now I need to check its history to see when it was added. Let me use the history tool with this exact URL.

The history tool shows that the page was:
- Absent at 2026-06-01
- Absent through 2026-08-15
- Added between 2026-08-15 and 2026-09-01
- Same through 2026-09-07

So the page was added sometime between August 15, 2026 and September 1, 2026. The tool gives me an interval, not a specific date. I should report this interval as the answer.

The user asked "When was the Agentic Search page added to the Search Toolkit documentation?" The answer is that it was added between August 15, 2026 and September 1, 2026.

## Tool calls

### 1. mistral_docs_history

```json
{"text": "Agentic Search", "under": "https://docs.mistral.ai/api/search-toolkit"}
```

Result:

```
Error executing tool mistral_docs_ca30_mistral_docs_history: error: E_BAD_PARAM
no stored page exists under "https://docs.mistral.ai/api/search-toolkit"
next: pass one documented history form.
```

### 2. mistral_docs_search

```json
{"q": "Agentic Search", "under": "https://docs.mistral.ai"}
```

Result:

```
q: "Agentic Search" | under: https://docs.mistral.ai

[1] https://docs.mistral.ai/studio/search/agentic-search | section: agentic-search
    Agentic Search
    Agentic Search helps agents answer questions when the answer is not in the first chunk returned by retrieval. Instead of searching again and hoping for a better result, the model can work inside the corpus: search to find a source, open it, move through nearby chunks, grep for exact terms, and search again without repeating chunks. In short, retrieval finds likely sources. Agentic Search lets the …
    cite: https://docs.mistral.ai/studio/search/agentic-search

[2] https://docs.mistral.ai/studio/search/agentic-search | section: how-it-works
    Agentic Search > How Agentic Search works
    Agentic Search runs a retrieval loop. The model does not just receive chunks and stop. It can inspect a result, drill into the source document to read surrounding context, then re-query with what it learned.
    cite: https://docs.mistral.ai/studio/search/agentic-search#how-it-works

[3] https://docs.mistral.ai/studio/search/agentic-search | section: retrieval-primitives-agentic-loop
    Agentic Search > Retrieval primitives and the agentic loop
    Agentic Search is not another retrieval method next to keyword or semantic search. Keyword and semantic search are retrieval primitives. Agentic Search is an orchestration layer that uses those primitives, adds navigation, and iterates until the model has enough evidence. | Layer | How it works | Best for | |-------|-------------|----------| | Keyword (lexical) | Matches exact terms or phrases | K …
    cite: https://docs.mistral.ai/studio/search/agentic-search#retrieval-primitives-agentic-loop

[4] https://docs.mistral.ai/studio/search/agentic-search | section: use-with-sdk
    Agentic Search > Use Agentic Search with the SDK
    If you need more control than the MCP server provides, build retrieval pipelines directly with the Search Toolkit SDK. The SDK gives you the same `QueryEngine` and `VectorRetriever` that the MCP server uses, plus advanced features like query rewriting, multi-retriever fusion, and semantic caching.
    cite: https://docs.mistral.ai/studio/search/agentic-search#use-with-sdk

[5] https://docs.mistral.ai/studio/search/agentic-search | section: use-as-mcp
    Agentic Search > Use Agentic Search as MCP tools
    The MCP server exposes seven tools that any MCP-compatible agent can call. The starter app registers the server in `.mcp.json` so Vibe discovers it automatically, but you can also connect from Studio or a custom agent.
    cite: https://docs.mistral.ai/studio/search/agentic-search#use-as-mcp

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/agentic-search") to read hit 1 on its page
```

### 3. mistral_docs_history

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

The **Agentic Search** page was added to the Search Toolkit documentation **between August 15, 2026 and September 1, 2026**.

[Documentation history](https://docs.mistral.ai/studio/search/agentic-search)

