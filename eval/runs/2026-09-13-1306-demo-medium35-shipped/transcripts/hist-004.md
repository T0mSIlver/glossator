# hist-004 (history, 7 connector calls)

## Question

Since when do the custom vector store docs describe partial updates through the PatchableIndex protocol?

## Thinking

The user is asking about when the Mistral documentation started describing partial updates through the PatchableIndex protocol for custom vector stores. This is a historical question about the documentation itself. I need to track when this specific concept was introduced.

I should use the mistral_docs_history tool to search for the phrase "PatchableIndex protocol" or related terms like "partial updates" in the context of custom vector stores. Let me start by searching for the exact phrase "PatchableIndex protocol" to see when it first appeared in the documentation.

The error indicates I used an invalid path. The tool expects proper page URLs. Let me try searching for the phrase without specifying an "under" path, which should search across all documentation.

The phrase "PatchableIndex protocol" doesn't appear in any stored snapshot. Let me try searching for just "PatchableIndex" to see if the protocol is mentioned without the word "protocol".

Interesting! The term "PatchableIndex" first appears on 2026-09-07 in the changelog. But the user is asking about when the *custom vector store docs* describe partial updates through this protocol. The changelog might mention it, but I need to find where it's actually documented in the custom vector store documentation.

Let me search for "partial updates" in the context of vector stores or custom vector stores.

The path format is still wrong. Let me try a different approach - search for "partial updates" without specifying a path, but maybe filter by the studio/search area. Actually, let me first search for pages related to custom vector stores to understand the documentation structure.

Great! I found that the custom vector stores documentation has a section called "partial-updates" that mentions the PatchableIndex protocol. The search result shows:

"Custom vector stores > Optional partial updates
A backend can also expose partial updates without a full re-index by implementing the optional `PatchableIndex` protocol. This protocol can change one metadata value or one chunk's embedding without chunking and indexing the full document again."

Now I need to find out when this section was added. Let me use the history tool to track the custom-vector-stores page specifically.

I need to use the exact URL format from the search results. The search result shows the URL as "https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores". Let me try that exact format.

Perfect! The history tool shows that the "partial-updates" section on the custom vector stores page was:
- Absent at 2026-06-01
- Absent through 2026-09-01
- Added between 2026-09-01 and 2026-09-07

This means the documentation describing partial updates through the PatchableIndex protocol was added sometime between September 1, 2026 and September 7, 2026.

The user asked "Since when do the custom vector store docs describe partial updates through the PatchableIndex protocol?" The answer is that it was added between 2026-09-01 and 2026-09-07.

I should provide this information clearly, citing the documentation history.

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

### 2. mistral_docs_history

```json
{"text": "PatchableIndex protocol"}
```

Result:

```
history text: "PatchableIndex protocol"
Results: the phrase is absent from every stored snapshot.
```

### 3. mistral_docs_history

```json
{"text": "PatchableIndex"}
```

Result:

```
history text: "PatchableIndex"
first stored date with the phrase: 2026-09-07 | https://docs.mistral.ai/studio/search/search-toolkit/changelog (absent at 2026-09-01)
last stored date with the phrase: 2026-09-07 | https://docs.mistral.ai/studio/search/search-toolkit/changelog
Results: present in 1 of 8 stored snapshots
```

### 4. mistral_docs_history

```json
{"text": "partial updates", "under": "docs.mistral.ai/studio/search"}
```

Result:

```
Error executing tool mistral_docs_ca30_mistral_docs_history: error: E_BAD_PARAM
no stored page exists under "https://docs.mistral.ai/docs.mistral.ai/studio/search"
next: pass one documented history form.
```

### 5. mistral_docs_search

```json
{"q": "custom vector store PatchableIndex", "max_hits": 10}
```

Result:

```
q: "custom vector store PatchableIndex"

[1] https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores | section: partial-updates
    Custom vector stores > Optional partial updates
    A backend can also expose partial updates without a full re-index by implementing the optional `PatchableIndex` protocol. This protocol can change one metadata value or one chunk's embedding without chunking and indexing the full document again. Implement `patch_chunk` and `patch_document`: ```python from mistralai.search.toolkit.search import PatchableIndex class MyVectorStore(VectorStoreIndex): …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores#partial-updates

[2] https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores | section: custom-vector-stores
    Custom vector stores
    Implement a custom storage backend by subclassing `VectorStoreIndex` (or `KeywordStoreIndex` for keyword search) and implementing its three methods: ```python from mistralai.search.toolkit.context import IngestContext, RetrievalContext from mistralai.search.toolkit.search import VectorStoreIndex, VectorSearchQuery, SearchResult from mistralai.search.toolkit.document import Document class MyVectorS …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores

[3] https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores | section: agentic-operations
    Custom vector stores > Optional agentic operations
    Beyond indexing and search, a backend can expose positional navigation by implementing the optional, `@runtime_checkable` `NavigableIndex` protocol. A store that doesn't implement the protocol doesn't advertise the capability, and callers gate access with `isinstance`.
    cite: https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores#agentic-operations

[4] https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores | section: agentic-operations/navigableindex
    Custom vector stores > Optional agentic operations > `NavigableIndex`
    These methods provide positional navigation over a chunk-per-document index. An agent can move to adjacent chunks, read a span, fetch a chunk by ID, and search within a source. In agentic `open` and `navigate` loops, the model keeps only an opaque `chunk_id` from a search result, and the server resolves its position. ```python from mistralai.search.toolkit.search import NavigableIndex, NavigationD …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores#agentic-operations

[5] https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores | section: see-also
    Custom vector stores > See also
    - **[Search index](https://docs.mistral.ai/studio/search/search-toolkit/search-index)**: the built-in backends. - **[Vespa](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa)** and **[Postgres](https://docs.mistral.ai/studio/search/search-toolkit/search-index/postgres)**: the built-in implementations, useful as reference for your own.
    cite: https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores#see-also

[6] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers | section: vector-retriever
    Retrievers > Vector Retriever
    Performs semantic search using embeddings. Finds chunks with similar meaning to the query, even if they use different words. **Installation**: Core library (no extra required) **Example**: ```python from mistralai.search.toolkit.retrieval.retrievers import VectorRetriever retriever = VectorRetriever( client=vector_store, # Vector store client (Vespa or custom implementation) embedder=embedder, # M …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers#vector-retriever

[7] https://docs.mistral.ai/studio/search/search-toolkit/ingestion/enrichers | section: creating-custom-enrichers/combining-multiple-enrichers
    Chunk enrichers > Creating custom enrichers > Combining multiple enrichers
    ```python from mistralai.search.toolkit.ingestion.pipelines import Pipeline pipeline = Pipeline( loader=loader, extractor=extractor, text_splitter=splitter, embedder=embedder, stores=vector_store, processors=[ SummaryEnricher(llm_provider=llm), EntityTagger(), CustomMetadataEnricher(), ], ) ``` Enrichers are applied sequentially in the order listed. Each enricher receives the output of the previou …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/ingestion/enrichers#creating-custom-enrichers:~:text=Enrichers%20are%20applied

[8] https://docs.mistral.ai/studio/knowledge-rag/rag_quickstart | section: load-vector-database
    RAG Quickstart > RAG from scratch > Load into a vector database
    Once we get the text embeddings, a common practice is to store them in a vector database for efficient processing and retrieval. There are several vector database to choose from. In our simple example, we are using an open-source vector database Faiss, which allows for efficient similarity search. With Faiss, we instantiate an instance of the Index class, which defines the indexing structure of th …
    cite: https://docs.mistral.ai/studio/knowledge-rag/rag_quickstart#load-vector-database

[9] https://docs.mistral.ai/studio/search/search-toolkit | section: components
    Search Toolkit > Architecture > Components
    | Component | Built-in options | |-----------|-----------------| | **File loaders** | `FilesystemFileLoader`, custom loaders | | **Extractors** | `MistralOCRExtractor`, `SmartPDFExtractor`, `PlainTextExtractor`, `PyMuPDFExtractor`, `HTMLExtractor`, `SpreadsheetExtractor`, `EmailExtractor`, `EmailWithAttachmentsExtractor`, `NumbersExtractor`, `LegacyOfficeExtractor`, `MistralAudioTranscriptionExtra …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#components

[10] https://docs.mistral.ai/studio/search/search-toolkit/ingestion | section: ingestion
    Ingestion
    Ingestion transforms raw documents into searchable chunks indexed in a vector store. You can swap pipeline components based on your needs. A `FileLoader` reads raw bytes from a source (local filesystem, cloud storage, or any custom source) and returns a `File` object. A `DocumentExtractor` converts that `File` into a structured `Document` by parsing PDFs via OCR, converting HTML to Markdown, or re …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/ingestion

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores") to read hit 1 on its page
```

### 6. mistral_docs_history

```json
{"page_url": "docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores", "section": "partial-updates"}
```

Result:

```
Error executing tool mistral_docs_ca30_mistral_docs_history: error: E_UNKNOWN_PAGE
no indexed page has the URL "https://docs.mistral.ai/docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores".
next: pass a page URL exactly as a mistral_docs_search hit printed it, without the #anchor.
```

### 7. mistral_docs_history

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

The **custom vector store docs** have described partial updates through the **`PatchableIndex` protocol** since **between 2026-09-01 and 2026-09-07**, when the [`partial-updates` section](https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores#partial-updates) was added to the page. It was absent in all snapshots up to 2026-09-01 and first appears on 2026-09-07.

