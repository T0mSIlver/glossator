# hist-003 (history, 5 connector calls)

## Question

When was the Agentic Search page added to the Search Toolkit documentation?

## Thinking

The user is asking about when a specific page ("Agentic Search") was added to the Search Toolkit documentation. This is a historical question about documentation changes. I need to use the mistral_docs_history tool to track when this page appeared.

I should search for the exact phrase "Agentic Search" in the context of the Search Toolkit documentation. The tool can track when text first appeared. I'll use the text parameter with "Agentic Search" and possibly filter by the Search Toolkit path.

Let me start by searching for when "Agentic Search" first appeared in the documentation.

I got an error because the path format was incorrect. Let me try again with a proper path. The Search Toolkit documentation is likely under a path like `/api/search-toolkit` or similar. Let me try with just the base path.

I'm still getting an error. The issue is with how I'm formatting the path. Let me try without the leading slash and just use the path directly.

I'm still getting errors. Let me try a different approach. Maybe I should first search for the page to see if it exists and get its exact URL, then use that to track its history.

Good! I found the page. The Agentic Search page is at `https://docs.mistral.ai/studio/search/agentic-search`. Now I need to track when this page was added. Let me use the history tool with the exact page URL.

Perfect! The history tool shows that the Agentic Search page was added between 2026-08-15 and 2026-09-01. This is the answer the user is looking for.

## Tool calls

### 1. mistral_docs_history

```json
{"text": "Agentic Search", "under": "docs.mistral.ai/api/search-toolkit"}
```

Result:

```
Error executing tool mistral_docs_ca30_mistral_docs_history: error: E_BAD_PARAM
no stored page exists under "https://docs.mistral.ai/docs.mistral.ai/api/search-toolkit"
next: pass one documented history form.
```

### 2. mistral_docs_history

```json
{"text": "Agentic Search", "under": "docs.mistral.ai/api/search-toolkit"}
```

Result:

```
Error executing tool mistral_docs_ca30_mistral_docs_history: error: E_BAD_PARAM
no stored page exists under "https://docs.mistral.ai/docs.mistral.ai/api/search-toolkit"
next: pass one documented history form.
```

### 3. mistral_docs_history

```json
{"text": "Agentic Search", "under": "api/search-toolkit"}
```

Result:

```
Error executing tool mistral_docs_ca30_mistral_docs_history: error: E_BAD_PARAM
no stored page exists under "https://docs.mistral.ai/api/search-toolkit"
next: pass one documented history form.
```

### 4. mistral_docs_search

```json
{"q": "Agentic Search", "under": "docs.mistral.ai"}
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

### 5. mistral_docs_history

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

The **Agentic Search** page in the Search Toolkit documentation was added between **August 15, 2026, and September 1, 2026** ([history](https://docs.mistral.ai/studio/search/agentic-search)).

