# mined-083 (single_page, 2 connector calls)

## Question

How do I stop a search from returning chunks the loop has already seen?

## Thinking

The user is asking how to prevent a search from returning chunks that have already been processed in a loop. This is a specific technical question about deduplication or avoiding duplicates in search results. I need to search the Mistral documentation to see if there's any guidance on this topic.

Let me break down what the user is asking:
- They have a loop that processes search results
- They want to avoid processing the same chunk multiple times
- They need a way to deduplicate or track seen chunks

This could be about:
1. Using a deduplication parameter in the search API
2. Implementing client-side tracking of seen chunks
3. Using pagination or offset parameters to avoid re-fetching
4. Some specific feature in Mistral's search functionality

I should search the documentation for terms related to deduplication, avoiding duplicates, or tracking seen results.

The search results show information about Agentic Search and its retrieval loop. I can see there's a mention of `exclude_ids` parameter in the search tool. Let me read the full page to get the complete details about how to use this parameter to avoid returning chunks the loop has already seen.

Perfect! I found the answer in the documentation. The `search` tool in Agentic Search has an `exclude_ids` parameter that can be used to avoid returning chunks the agent has already inspected. This is exactly what the user is looking for.

From the documentation:
- The `search(query, top_k, exclude_ids)` tool runs semantic or hybrid retrieval across the collection
- You can pass `exclude_ids` to avoid returning chunks the agent already inspected

This is the direct answer to the user's question. I should provide a clear, concise answer with the relevant documentation link.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "stop search returning chunks the loop has already seen", "max_hits": 5}
```

Result:

```
q: "stop search returning chunks the loop has already seen"

[1] https://docs.mistral.ai/studio/search/agentic-search | section: the-retrieval-loop
    Agentic Search > How Agentic Search works > The retrieval loop
    1. **Search**: The model runs a query across the collection and receives the most relevant chunks. 2. **Inspect**: The model picks a promising hit and reads the surrounding context within that document, without re-running a global search. 3. **Grep**: The model searches for an exact term or phrase inside the same document to jump to a more specific region. 4. **Navigate or read**: The model steps …
    cite: https://docs.mistral.ai/studio/search/agentic-search#the-retrieval-loop

[2] https://docs.mistral.ai/studio/search/agentic-search | section: retrieval-primitives-agentic-loop
    Agentic Search > Retrieval primitives and the agentic loop
    Agentic Search is not another retrieval method next to keyword or semantic search. Keyword and semantic search are retrieval primitives. Agentic Search is an orchestration layer that uses those primitives, adds navigation, and iterates until the model has enough evidence. | Layer | How it works | Best for | |-------|-------------|----------| | Keyword (lexical) | Matches exact terms or phrases | K …
    cite: https://docs.mistral.ai/studio/search/agentic-search#retrieval-primitives-agentic-loop

[3] https://docs.mistral.ai/studio/search/agentic-search | section: how-it-works
    Agentic Search > How Agentic Search works
    Agentic Search runs a retrieval loop. The model does not just receive chunks and stop. It can inspect a result, drill into the source document to read surrounding context, then re-query with what it learned.
    cite: https://docs.mistral.ai/studio/search/agentic-search#how-it-works

[4] https://docs.mistral.ai/studio/search/agentic-search | section: navigation-tools
    Agentic Search > How Agentic Search works > Navigation tools
    The model calls the following tools inside the loop. Each one operates on the search index and returns chunks with their content, score, and position metadata. | Tool | What it does | |------|-------------| | `search(query, top_k, exclude_ids)` | Runs semantic or hybrid retrieval across the collection. Pass `exclude_ids` to avoid returning chunks the agent already inspected. | | `open(source_id, s …
    cite: https://docs.mistral.ai/studio/search/agentic-search#navigation-tools

[5] https://docs.mistral.ai/studio/search/agentic-search | section: latency
    Agentic Search > Latency and tradeoffs
    Each tool call has a cost, but navigation can reduce end-to-end latency and token usage because the model converges faster. Instead of repeatedly issuing broad searches, the agent can stay inside the right source, use `grep` to jump to specific terms, and use `exclude_ids` to avoid revisiting the same chunks. In the Agentic Search benchmarks cited in the Search Toolkit launch materials, the full a …
    cite: https://docs.mistral.ai/studio/search/agentic-search#latency

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/agentic-search") to read hit 1 on its page
```

### 2. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/search/agentic-search", "section": "navigation-tools"}
```

Result:

```
page: https://docs.mistral.ai/studio/search/agentic-search | "Agentic Search" | section: navigation-tools

## section: navigation-tools
    Agentic Search > How Agentic Search works > Navigation tools
    cite: https://docs.mistral.ai/studio/search/agentic-search#navigation-tools
### Navigation tools {#navigation-tools}

The model calls the following tools inside the loop. Each one operates on the search index and returns chunks with their content, score, and position metadata.

| Tool | What it does |
|------|-------------|
| `search(query, top_k, exclude_ids)` | Runs semantic or hybrid retrieval across the collection. Pass `exclude_ids` to avoid returning chunks the agent already inspected. |
| `open(source_id, start_offset, end_offset, window)` | Expands context around a retrieved chunk. Returns adjacent chunks in reading order. |
| `navigate(source_id, start_offset, end_offset, direction, top_k)` | Steps forward or backward through a document from a known position. |
| `read(source_id, start_offset, end_offset, top_k)` | Reads chunks from a known source range returned by search or navigation results. |
| `grep(source_id, pattern, mode, top_k)` | Lexical search for an exact term or phrase within a single document. |
| `ingest(uri)` | Adds a document to the index. Accepts a local path, `file://` URI, or `http(s)://` URL. |
| `delete(source_id)` | Removes a document and all its chunks from the index. |

> **Info**
>
> Agentic navigation requires a `NavigableIndex`. When you define your schema migration, set `IndexingMode.DOCUMENT_PER_CHUNK` so that chunks carry source offsets and can be walked in order.

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/agentic-search", section="get-started") for the section after it
```

## Answer

To prevent the search from returning chunks that the loop has already seen, use the `exclude_ids` parameter in the `search` tool.

Pass the IDs of the chunks you've already processed to `exclude_ids` so they are not returned again in subsequent searches.

[Navigation tools > search(exclude_ids)](https://docs.mistral.ai/studio/search/agentic-search#navigation-tools)

