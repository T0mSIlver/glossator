# hist-004 (history, 3 connector calls)

## Question

Since when do the custom vector store docs describe partial updates through the PatchableIndex protocol?

## Thinking

The user is asking about when the custom vector store docs started describing partial updates through the PatchableIndex protocol. This is a specific historical question about Mistral's documentation. I need to search the documentation history to find when this feature was introduced.

I should use the mistral_docs_history tool to track when this phrase appeared in the documentation. I'll search for the exact phrase "PatchableIndex protocol" or related terms like "partial updates" in the context of custom vector store documentation.

Let me start by searching for the text "PatchableIndex" in the documentation history.

I got an error. The tool expects a proper page URL or path. Let me try a different approach. I should first search for where "PatchableIndex" is mentioned in the current documentation to understand the context, then use the history tool on that specific page.

Let me search for "PatchableIndex" in the documentation.

Good! I found a hit on the custom vector stores page. The search result shows that there's a section about "Optional partial updates" that mentions the PatchableIndex protocol. The URL is: https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores

Now I need to use the history tool to find when this section was added. Let me use the history tool on this specific page with the section "partial-updates".

Perfect! The history tool shows that the "partial-updates" section was:
- Absent at 2026-06-01
- Absent through 2026-09-01
- Added between 2026-09-01 and 2026-09-07

So the documentation for partial updates through the PatchableIndex protocol was added to the custom vector store docs sometime between September 1, 2026 and September 7, 2026.

The user asked "Since when do the custom vector store docs describe partial updates through the PatchableIndex protocol?" The answer is that it was added between 2026-09-01 and 2026-09-07.

I should provide this answer clearly, with the citation to the documentation section.

## Tool calls

### 1. mistral_docs_history

```json
{"text": "PatchableIndex protocol", "under": "docs.mistral.ai"}
```

Result:

```
Error executing tool mistral_docs_ca30_mistral_docs_history: error: E_BAD_PARAM
no stored page exists under "https://docs.mistral.ai/docs.mistral.ai"
next: pass one documented history form.
```

### 2. mistral_docs_search

```json
{"q": "PatchableIndex protocol partial updates custom vector store"}
```

Result:

```
q: "PatchableIndex protocol partial updates custom vector store"

[1] https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores | section: partial-updates
    Custom vector stores > Optional partial updates
    A backend can also expose partial updates without a full re-index by implementing the optional `PatchableIndex` protocol. This protocol can change one metadata value or one chunk's embedding without chunking and indexing the full document again. Implement `patch_chunk` and `patch_document`: ```python from mistralai.search.toolkit.search import PatchableIndex class MyVectorStore(VectorStoreIndex): …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores#partial-updates

[2] https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores | section: agentic-operations
    Custom vector stores > Optional agentic operations
    Beyond indexing and search, a backend can expose positional navigation by implementing the optional, `@runtime_checkable` `NavigableIndex` protocol. A store that doesn't implement the protocol doesn't advertise the capability, and callers gate access with `isinstance`.
    cite: https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores#agentic-operations

[3] https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores | section: custom-vector-stores
    Custom vector stores
    Implement a custom storage backend by subclassing `VectorStoreIndex` (or `KeywordStoreIndex` for keyword search) and implementing its three methods: ```python from mistralai.search.toolkit.context import IngestContext, RetrievalContext from mistralai.search.toolkit.search import VectorStoreIndex, VectorSearchQuery, SearchResult from mistralai.search.toolkit.document import Document class MyVectorS …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores

[4] https://docs.mistral.ai/studio/search/search-toolkit/changelog | section: 0-0-11
    Changelog > 0.0.11
    - For ingestion, made extraction checkpoints (saving snapshots between stages, for faster retrying) a backend-agnostic capability. [`Pipeline(checkpoint_store=...)`](https://docs.mistral.ai/studio/search/search-toolkit/ingestion#pipeline) accepts any `ObjectStorage` backend and saves checkpoints between the ingestion stages; `run_file(..., checkpoint_key=...)` loads and saves the extraction result …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/changelog#0-0-11

[5] https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores | section: agentic-operations/navigableindex
    Custom vector stores > Optional agentic operations > `NavigableIndex`
    These methods provide positional navigation over a chunk-per-document index. An agent can move to adjacent chunks, read a span, fetch a chunk by ID, and search within a source. In agentic `open` and `navigate` loops, the model keeps only an opaque `chunk_id` from a search result, and the server resolves its position. ```python from mistralai.search.toolkit.search import NavigableIndex, NavigationD …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores#agentic-operations

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores") to read hit 1 on its page
```

### 3. mistral_docs_history

```json
{"page_url": "https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores", "section": "partial-updates"}
```

Result:

```
history page: https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores | section: partial-updates
absent at 2026-06-01
absent through 2026-09-01
added between 2026-09-01 and 2026-09-07 | https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores#partial-updates
Results: 8 of 8 stored snapshots
```

## Answer

The custom vector store documentation has described partial updates through the `PatchableIndex` protocol **since between September 1, 2026 and September 7, 2026**.

[Custom vector stores > Optional partial updates](https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores#partial-updates)

