# mined2-084 (unanswerable, 19 connector calls)

## Question

What evaluation features does the Search Toolkit provide?

## Thinking

The user is asking about evaluation features provided by the Search Toolkit. This is a specific question about Mistral's documentation. I need to search the documentation to find information about the Search Toolkit and its evaluation features.

I should use the mistral_docs_search tool to find relevant sections. The query should be something like "Search Toolkit evaluation features" or similar. Let me start with a direct search.

The search returned results, but I need to find specific information about evaluation features. The first result is the main Search Toolkit page, but it doesn't explicitly mention evaluation features in the snippet. Let me search more specifically for "evaluation" within the Search Toolkit documentation.

The search results show that the Search Toolkit provides components for ingestion, retrieval, and evaluation, but I need more specific details about the evaluation features. Let me read the main Search Toolkit page to find the evaluation section.

The main page mentions that Search Toolkit provides components for evaluation, but doesn't list the specific evaluation features. I need to find a dedicated evaluation section or page. Let me search for pages under the search-toolkit path that might contain evaluation information.

I can see the list of pages under the search-toolkit path. I notice there's no explicit "evaluation" page listed. However, the main page mentioned that evaluation is one of the three main components (ingestion, retrieval, and evaluation). Let me search more specifically for evaluation-related terms in the documentation.

The search results are still not giving me the specific evaluation features. Let me try a different approach and search for "evaluation" as a standalone term to see if there's a dedicated evaluation page or section.

The search for "evaluation" under the search-toolkit path returned no results, which is odd since the main page explicitly mentions evaluation as a component. Let me try searching for related terms like "metrics", "benchmark", or "testing" which might be used in the evaluation context.

I found a reference to CacheMetrics in the semantic-cache section. This suggests there are evaluation/monitoring features. Let me read the semantic-cache page to see if it contains evaluation-related information. But I should also look for a dedicated evaluation page. Let me try searching for "evaluation" without the Search Toolkit qualifier to see if there's a broader evaluation framework.

The search results are showing evaluation features in the Observability section, but these seem to be for the broader Mistral platform, not specifically the Search Toolkit. Let me go back to the Search Toolkit and look for a dedicated evaluation page. I noticed in the list of pages there was no explicit evaluation page. Let me try to find if there's an evaluation module by searching for "evaluator" or similar terms.

I'm still not finding a dedicated evaluation page for Search Toolkit. Let me try to read the quickstart or other pages that might mention evaluation. Or perhaps the evaluation features are embedded within other components. Let me try searching for "retrieval evaluation" or "IR evaluation" which are common terms in information retrieval.

I see that the CacheMetrics is mentioned in the semantic-cache section. This is a metric for evaluation. Let me read the semantic-cache page to see if there are more evaluation features mentioned there. But I should also try to find if there's a dedicated evaluation page by checking the list of pages again more carefully. Maybe I missed something.

The semantic-cache page shows monitoring metrics like CacheMetrics, but this is specifically for the cache, not general evaluation. Let me try a different approach. Since the main page says Search Toolkit provides components for evaluation, but I haven't found a dedicated page, maybe the evaluation features are part of the retrieval components or there's a separate evaluation module. Let me search for "evaluation" in the context of the entire docs.mistral.ai site, not just under search-toolkit.

Let me try a more direct approach. Since the main page explicitly states that Search Toolkit provides components for evaluation, but I haven't found a dedicated evaluation page, perhaps the evaluation features are documented in a way that I'm not finding with my current search terms. Let me try searching for specific IR evaluation metrics like "precision", "recall", "NDCG", "MRR", etc.

I'm still not finding specific evaluation features. Let me try to look at the quickstart page, which might demonstrate evaluation features as part of a complete pipeline example.

The quickstart doesn't mention evaluation features. Let me try to search for a page that might be under a different path. Maybe the evaluation features are documented in a separate section like "evaluation" under the search path. Let me check what pages exist under the broader search path.

I've listed all pages under the search path and there's no explicit evaluation page for Search Toolkit. The main page mentions evaluation as a component, but I haven't found the details. Let me try a different approach - maybe the evaluation features are part of the retrieval components or are documented in the changelog. Let me check the changelog for any mentions of evaluation.

The changelog doesn't mention evaluation features explicitly. Let me try a more direct approach. Since the main Search Toolkit page mentions evaluation as a component, but I haven't found the details, perhaps the evaluation features are part of a module that isn't well-indexed. Let me try searching for "evaluation" in the context of the Python module structure. Maybe there's a `mistralai.search.toolkit.evaluation` module.

I found a reference to the Evaluation SDK (`mistralai-observability`) which provides offline evaluation capabilities. However, this seems to be a separate package from Search Toolkit. Let me read this page to see if it's related to Search Toolkit's evaluation features or if it's a different product.

The Evaluation SDK (`mistralai-observability`) is a separate package for offline evaluations, but the user is asking specifically about Search Toolkit's evaluation features. The main Search Toolkit page mentions it provides components for evaluation, but I haven't found the dedicated documentation. 

Let me try one more search approach - maybe the evaluation features are documented under a different term like "testing", "benchmarking", or "quality assurance" within the Search Toolkit docs.

I've exhausted my search options and haven't found a dedicated evaluation page for Search Toolkit. However, I have found that:

1. The main Search Toolkit page explicitly states it provides components for "ingestion, retrieval, and evaluation"
2. There are monitoring metrics for the semantic cache (CacheMetrics)
3. There's a separate Evaluation SDK (`mistralai-observability`) for offline evaluations

Since I cannot find specific documentation for Search Toolkit's evaluation features beyond the high-level mention, I should be honest with the user. The documentation mentions evaluation as a component but doesn't provide detailed information about what those evaluation features are in the current commit of the documentation.

Let me provide an answer based on what I've found, acknowledging the limitation.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "Search Toolkit evaluation features", "max_hits": 5}
```

Result:

```
q: "Search Toolkit evaluation features"

[1] https://docs.mistral.ai/studio/search/search-toolkit | section: search-toolkit
    Search Toolkit
    Search Toolkit is a Python framework for building information retrieval (IR) systems. It provides components for ingestion, retrieval, and evaluation. It works across backends, and every component can be swapped. LLMs are not trained on your private data. To ground their answers in your documents you need a retrieval pipeline that ingests, indexes, and searches your content. Search Toolkit gives y …
    cite: https://docs.mistral.ai/studio/search/search-toolkit

[2] https://docs.mistral.ai/studio/search/search-toolkit | section: retrieval
    Search Toolkit > Key features > Retrieval
    [Retrieval](https://docs.mistral.ai/studio/search/search-toolkit/retrieval) includes: - **Multiple strategies**: Vector (semantic) search with optional reranking - **Query preprocessing**: Improve user queries with LLM reformulation or query extension - **Reranking**: LLM reranker, cross-encoder reranker, or custom rerankers - **Semantic caching**: Cache results by query similarity to skip redunda …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#retrieval

[3] https://docs.mistral.ai/studio/search/search-toolkit | section: ingestion
    Search Toolkit > Key features > Ingestion
    [Ingestion](https://docs.mistral.ai/studio/search/search-toolkit/ingestion) includes: - **Multi-format extraction**: PDF/DOCX/PPTX via Mistral OCR, HTML, spreadsheets, emails, plain text - **File loading**: Load from the local filesystem or implement custom loaders for any source - **Flexible chunking**: Character, token, markdown-aware, or separator-based splitting - **Enrichment**: Enrich docume …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#ingestion

[4] https://docs.mistral.ai/studio/search/search-toolkit | section: next-steps
    Search Toolkit > Next steps
    - **[Quickstart](https://docs.mistral.ai/studio/search/search-toolkit/quickstart)**: build your first ingestion and retrieval pipeline end to end. - **[Document model](https://docs.mistral.ai/studio/search/search-toolkit/concepts/document-model)**: understand `Document`, `DocumentChunk`, and the identity that ties them together. - **[Embedding model](https://docs.mistral.ai/studio/search/search-to …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#next-steps

[5] https://docs.mistral.ai/studio/search/search-toolkit | section: packages
    Search Toolkit > Installation and extras
    Install the core package: ```bash uv add mistralai-search-toolkit ``` Optional extras add specialized functionality: | Extra | Description | |-------|-------------| | `vespa` | Vespa plugin for vector storage and semantic search | | `extractor-pymupdf` | Advanced PDF extraction with PyMuPDF Pro | | `extractor-spreadsheet` | Spreadsheet parsing (Excel, CSV, Calamine format) | | `extractor-email` | …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#packages

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit") to read hit 1 on its page
```

### 2. mistral_docs_search

```json
{"q": "Search Toolkit evaluation", "max_hits": 10}
```

Result:

```
q: "Search Toolkit evaluation"

[1] https://docs.mistral.ai/studio/search/search-toolkit | section: search-toolkit
    Search Toolkit
    Search Toolkit is a Python framework for building information retrieval (IR) systems. It provides components for ingestion, retrieval, and evaluation. It works across backends, and every component can be swapped. LLMs are not trained on your private data. To ground their answers in your documents you need a retrieval pipeline that ingests, indexes, and searches your content. Search Toolkit gives y …
    cite: https://docs.mistral.ai/studio/search/search-toolkit

[2] https://docs.mistral.ai/studio/search/search-toolkit | section: next-steps
    Search Toolkit > Next steps
    - **[Quickstart](https://docs.mistral.ai/studio/search/search-toolkit/quickstart)**: build your first ingestion and retrieval pipeline end to end. - **[Document model](https://docs.mistral.ai/studio/search/search-toolkit/concepts/document-model)**: understand `Document`, `DocumentChunk`, and the identity that ties them together. - **[Embedding model](https://docs.mistral.ai/studio/search/search-to …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#next-steps

[3] https://docs.mistral.ai/studio/search/search-toolkit | section: retrieval
    Search Toolkit > Key features > Retrieval
    [Retrieval](https://docs.mistral.ai/studio/search/search-toolkit/retrieval) includes: - **Multiple strategies**: Vector (semantic) search with optional reranking - **Query preprocessing**: Improve user queries with LLM reformulation or query extension - **Reranking**: LLM reranker, cross-encoder reranker, or custom rerankers - **Semantic caching**: Cache results by query similarity to skip redunda …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#retrieval

[4] https://docs.mistral.ai/studio/search/search-toolkit | section: packages
    Search Toolkit > Installation and extras
    Install the core package: ```bash uv add mistralai-search-toolkit ``` Optional extras add specialized functionality: | Extra | Description | |-------|-------------| | `vespa` | Vespa plugin for vector storage and semantic search | | `extractor-pymupdf` | Advanced PDF extraction with PyMuPDF Pro | | `extractor-spreadsheet` | Spreadsheet parsing (Excel, CSV, Calamine format) | | `extractor-email` | …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#packages

[5] https://docs.mistral.ai/studio/search/search-toolkit | section: ingestion
    Search Toolkit > Key features > Ingestion
    [Ingestion](https://docs.mistral.ai/studio/search/search-toolkit/ingestion) includes: - **Multi-format extraction**: PDF/DOCX/PPTX via Mistral OCR, HTML, spreadsheets, emails, plain text - **File loading**: Load from the local filesystem or implement custom loaders for any source - **Flexible chunking**: Character, token, markdown-aware, or separator-based splitting - **Enrichment**: Enrich docume …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#ingestion

[6] https://docs.mistral.ai/studio/search/search-toolkit | section: components
    Search Toolkit > Architecture > Components
    | Component | Built-in options | |-----------|-----------------| | **File loaders** | `FilesystemFileLoader`, custom loaders | | **Extractors** | `MistralOCRExtractor`, `SmartPDFExtractor`, `PlainTextExtractor`, `PyMuPDFExtractor`, `HTMLExtractor`, `SpreadsheetExtractor`, `EmailExtractor`, `EmailWithAttachmentsExtractor`, `NumbersExtractor`, `LegacyOfficeExtractor`, `MistralAudioTranscriptionExtra …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#components

[7] https://docs.mistral.ai/studio/search/search-toolkit | section: architecture
    Search Toolkit > Architecture
    **Ingestion** transforms raw documents into searchable chunks. A `FileLoader` reads raw bytes from a source, a `DocumentExtractor` converts them into a structured document, a `TextSplitter` divides it into chunks, optional `DocumentProcessor` stages (such as a `ChunkEnricher` or `SummaryEnricher`) add metadata, and an `Embedder` produces vectors for indexing into a vector store. **Retrieval** find …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#architecture

[8] https://docs.mistral.ai/studio/search/agentic-search | section: next-steps
    Agentic Search > Next steps
    - [Search Toolkit](https://docs.mistral.ai/studio/search/search-toolkit): learn about ingestion pipelines, retrieval strategies, and the full SDK. - [Libraries](https://docs.mistral.ai/studio/search/libraries): use managed document ingestion and search for built-in RAG. - [Connectors](https://docs.mistral.ai/studio/connectors): connect models and agents to external tools and data sources. - [Agent …
    cite: https://docs.mistral.ai/studio/search/agentic-search#next-steps

[9] https://docs.mistral.ai/studio/search/search-toolkit/search-index | section: available-vector-stores
    Search index > Available backends
    | Backend | Purpose | |---------|---------| | **[Vespa](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa)** | Vector database with schema management, ranking, clustering, and replication | | **[Postgres](https://docs.mistral.ai/studio/search/search-toolkit/search-index/postgres)** | PostgreSQL with `pgvector` and `pg_textsearch` for dense and hybrid search | | **[Custom vect …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/search-index#available-vector-stores

[10] https://docs.mistral.ai/studio/search/agentic-search | section: latency
    Agentic Search > Latency and tradeoffs
    Each tool call has a cost, but navigation can reduce end-to-end latency and token usage because the model converges faster. Instead of repeatedly issuing broad searches, the agent can stay inside the right source, use `grep` to jump to specific terms, and use `exclude_ids` to avoid revisiting the same chunks. In the Agentic Search benchmarks cited in the Search Toolkit launch materials, the full a …
    cite: https://docs.mistral.ai/studio/search/agentic-search#latency

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit") to read hit 1 on its page
```

### 3. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/search/search-toolkit"}
```

Result:

```
page: https://docs.mistral.ai/studio/search/search-toolkit | "Search Toolkit"

## section: search-toolkit
    Search Toolkit
    cite: https://docs.mistral.ai/studio/search/search-toolkit
# Search Toolkit

Search Toolkit is a Python framework for building information retrieval (IR) systems. It provides components for ingestion, retrieval, and evaluation. It works across backends, and every component can be swapped.

LLMs are not trained on your private data. To ground their answers in your documents you need a retrieval pipeline that ingests, indexes, and searches your content. Search Toolkit gives you every building block to assemble that pipeline.

## section: ingestion
    Search Toolkit > Key features > Ingestion
    cite: https://docs.mistral.ai/studio/search/search-toolkit#ingestion
### Ingestion {#ingestion}

[Ingestion](https://docs.mistral.ai/studio/search/search-toolkit/ingestion) includes:

- **Multi-format extraction**: PDF/DOCX/PPTX via Mistral OCR, HTML, spreadsheets, emails, plain text
- **File loading**: Load from the local filesystem or implement custom loaders for any source
- **Flexible chunking**: Character, token, markdown-aware, or separator-based splitting
- **Enrichment**: Enrich documents and chunks with custom metadata or LLM-generated summaries
- **Indexing**: Index to vector stores for semantic search

## section: retrieval
    Search Toolkit > Key features > Retrieval
    cite: https://docs.mistral.ai/studio/search/search-toolkit#retrieval
### Retrieval {#retrieval}

[Retrieval](https://docs.mistral.ai/studio/search/search-toolkit/retrieval) includes:

- **Multiple strategies**: Vector (semantic) search with optional reranking
- **Query preprocessing**: Improve user queries with LLM reformulation or query extension
- **Reranking**: LLM reranker, cross-encoder reranker, or custom rerankers
- **Semantic caching**: Cache results by query similarity to skip redundant retrieval

## section: architecture
    Search Toolkit > Architecture
    cite: https://docs.mistral.ai/studio/search/search-toolkit#architecture
## Architecture {#architecture}

**Ingestion** transforms raw documents into searchable chunks. A `FileLoader` reads raw bytes from a source, a `DocumentExtractor` converts them into a structured document, a `TextSplitter` divides it into chunks, optional `DocumentProcessor` stages (such as a `ChunkEnricher` or `SummaryEnricher`) add metadata, and an `Embedder` produces vectors for indexing into a vector store.

**Retrieval** finds relevant chunks for a given query. An optional query preprocessor rewrites or expands the query, a `Retriever` searches the vector index, and an optional `Reranker` re-scores the results before returning them.

Both workflows are orchestrated by high-level classes (`Pipeline` for ingestion, `QueryEngine` for retrieval) that handle component wiring and execution. Every component can be swapped: use the built-in implementations or bring your own.

## section: components
    Search Toolkit > Architecture > Components
    cite: https://docs.mistral.ai/studio/search/search-toolkit#components
### Components {#components}

| Component | Built-in options |
|-----------|-----------------|
| **File loaders** | `FilesystemFileLoader`, custom loaders |
| **Extractors** | `MistralOCRExtractor`, `SmartPDFExtractor`, `PlainTextExtractor`, `PyMuPDFExtractor`, `HTMLExtractor`, `SpreadsheetExtractor`, `EmailExtractor`, `EmailWithAttachmentsExtractor`, `NumbersExtractor`, `LegacyOfficeExtractor`, `MistralAudioTranscriptionExtractor` |
| **Text splitters** | `CharacterTextSplitter`, `TokenTextSplitter`, `MarkdownTextSplitter`, `ParagraphTokenTextSplitter`, `MarkdownTokenTextSplitter`, `SeparatorTextSplitter` |
| **Enrichers** | `SummaryEnricher`, custom `ChunkEnricher` |
| **Embedders** | `MistralEmbedder`, custom `Embedder` |
| **Storage** | Vespa, Postgres (pgvector), or custom vector store |
| **Retrievers** | `VectorRetriever`, `KeywordRetriever` with a custom `KeywordStoreIndex` |
| **Rerankers** | `LLMReRanker`, `CrossEncoderReRanker`, `RRFRanker` |
| **Preprocessing** | `LLMQueryRewriter`, `LLMQueryExtension` |
| **Caching** | `SemanticCache` with `InMemoryCacheBackend` |

## section: packages
    Search Toolkit > Installation and extras
    cite: https://docs.mistral.ai/studio/search/search-toolkit#packages
## Installation and extras {#packages}

Install the core package:

```bash
uv add mistralai-search-toolkit
```

Optional extras add specialized functionality:

| Extra | Description |
|-------|-------------|
| `vespa` | Vespa plugin for vector storage and semantic search |
| `extractor-pymupdf` | Advanced PDF extraction with PyMuPDF Pro |
| `extractor-spreadsheet` | Spreadsheet parsing (Excel, CSV, Calamine format) |
| `extractor-email` | Email file parsing (EML, MSG formats) |
| `html-converter-markdownify` | Convert HTML to Markdown |
| `text-splitter-langchain` | Additional text splitting strategies via LangChain |
| `storage-gcs` | Google Cloud Storage integration |
| `storage-azure` | Azure Blob Storage integration |
| `storage-s3` | Amazon S3 integration |
| `language-detection-fasttext` | Language detection via fastText |
| `all` | All optional extras |

Install extras with the core package:

```bash
uv add "mistralai-search-toolkit[vespa]"
uv add "mistralai-search-toolkit[vespa,extractor-pymupdf]"
uv add "mistralai-search-toolkit[all]"  # Install all extras
```

All packages are available on [PyPI](https://pypi.org/project/mistralai-search-toolkit/).

> **Info**
>
> Requires **Python 3.12+**. We recommend using [uv](https://docs.astral.sh/uv/) for dependency management.

## section: next-steps
    Search Toolkit > Next steps
    cite: https://docs.mistral.ai/studio/search/search-toolkit#next-steps
## Next steps {#next-steps}

- **[Quickstart](https://docs.mistral.ai/studio/search/search-toolkit/quickstart)**: build your first ingestion and retrieval pipeline end to end.
- **[Document model](https://docs.mistral.ai/studio/search/search-toolkit/concepts/document-model)**: understand `Document`, `DocumentChunk`, and the identity that ties them together.
- **[Embedding model](https://docs.mistral.ai/studio/search/search-toolkit/concepts/embedding-model)**: understand how the schema describes embedding vectors, separately from the embedder.
- **[Search index](https://docs.mistral.ai/studio/search/search-toolkit/search-index)**: set up your vector store.
- **[Ingestion](https://docs.mistral.ai/studio/search/search-toolkit/ingestion)**: load, extract, chunk, enrich, and index your documents.
- **[Retrieval](https://docs.mistral.ai/studio/search/search-toolkit/retrieval)**: configure vector search with optional reranking.

Results: 7 sections, the whole page.
```

### 4. mistral_docs_search

```json
{"q": "", "under": "https://docs.mistral.ai/studio/search/search-toolkit", "max_hits": 20}
```

Result:

```
pages under https://docs.mistral.ai/studio/search/search-toolkit

- https://docs.mistral.ai/studio/search/search-toolkit
    Search Toolkit
- https://docs.mistral.ai/studio/search/search-toolkit/changelog
    Changelog
- https://docs.mistral.ai/studio/search/search-toolkit/concepts/document-model
    Document model
- https://docs.mistral.ai/studio/search/search-toolkit/concepts/embedding-model
    Embedding model
- https://docs.mistral.ai/studio/search/search-toolkit/ingestion
    Ingestion
- https://docs.mistral.ai/studio/search/search-toolkit/ingestion/embedders
    Embedders
- https://docs.mistral.ai/studio/search/search-toolkit/ingestion/enrichers
    Chunk enrichers
- https://docs.mistral.ai/studio/search/search-toolkit/ingestion/extractors
    Document extractors
- https://docs.mistral.ai/studio/search/search-toolkit/ingestion/loaders
    File loaders
- https://docs.mistral.ai/studio/search/search-toolkit/ingestion/splitters
    Text splitters
- https://docs.mistral.ai/studio/search/search-toolkit/quickstart
    Quickstart
- https://docs.mistral.ai/studio/search/search-toolkit/retrieval
    Retrieval
- https://docs.mistral.ai/studio/search/search-toolkit/retrieval/preprocessing
    Query preprocessing
- https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers
    Rerankers
- https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers
    Retrievers
- https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache
    Semantic cache
- https://docs.mistral.ai/studio/search/search-toolkit/search-index
    Search index
- https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores
    Custom vector stores
- https://docs.mistral.ai/studio/search/search-toolkit/search-index/postgres
    Postgres
- https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa
    Vespa
- https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/anatomy
    Anatomy of a Vespa application
- https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli
    CLI reference
- https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/local-development
    Local development
- https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/migration-helpers
    Migration helpers reference
- https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/migrations
    Manage schema
- https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/operations
    Deploy and operate
- https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/query-profiles
    Manage ranking

Results: 27 pages; a page not listed does not exist at this commit.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit") reads the first one.
```

### 5. mistral_docs_search

```json
{"q": "evaluation metrics Search Toolkit", "max_hits": 10}
```

Result:

```
q: "evaluation metrics Search Toolkit"

[1] https://docs.mistral.ai/studio/search/search-toolkit | section: search-toolkit
    Search Toolkit
    Search Toolkit is a Python framework for building information retrieval (IR) systems. It provides components for ingestion, retrieval, and evaluation. It works across backends, and every component can be swapped. LLMs are not trained on your private data. To ground their answers in your documents you need a retrieval pipeline that ingests, indexes, and searches your content. Search Toolkit gives y …
    cite: https://docs.mistral.ai/studio/search/search-toolkit

[2] https://docs.mistral.ai/studio/search/search-toolkit | section: next-steps
    Search Toolkit > Next steps
    - **[Quickstart](https://docs.mistral.ai/studio/search/search-toolkit/quickstart)**: build your first ingestion and retrieval pipeline end to end. - **[Document model](https://docs.mistral.ai/studio/search/search-toolkit/concepts/document-model)**: understand `Document`, `DocumentChunk`, and the identity that ties them together. - **[Embedding model](https://docs.mistral.ai/studio/search/search-to …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#next-steps

[3] https://docs.mistral.ai/studio/search/search-toolkit | section: retrieval
    Search Toolkit > Key features > Retrieval
    [Retrieval](https://docs.mistral.ai/studio/search/search-toolkit/retrieval) includes: - **Multiple strategies**: Vector (semantic) search with optional reranking - **Query preprocessing**: Improve user queries with LLM reformulation or query extension - **Reranking**: LLM reranker, cross-encoder reranker, or custom rerankers - **Semantic caching**: Cache results by query similarity to skip redunda …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#retrieval

[4] https://docs.mistral.ai/studio/search/search-toolkit | section: packages
    Search Toolkit > Installation and extras
    Install the core package: ```bash uv add mistralai-search-toolkit ``` Optional extras add specialized functionality: | Extra | Description | |-------|-------------| | `vespa` | Vespa plugin for vector storage and semantic search | | `extractor-pymupdf` | Advanced PDF extraction with PyMuPDF Pro | | `extractor-spreadsheet` | Spreadsheet parsing (Excel, CSV, Calamine format) | | `extractor-email` | …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#packages

[5] https://docs.mistral.ai/studio/search/search-toolkit | section: ingestion
    Search Toolkit > Key features > Ingestion
    [Ingestion](https://docs.mistral.ai/studio/search/search-toolkit/ingestion) includes: - **Multi-format extraction**: PDF/DOCX/PPTX via Mistral OCR, HTML, spreadsheets, emails, plain text - **File loading**: Load from the local filesystem or implement custom loaders for any source - **Flexible chunking**: Character, token, markdown-aware, or separator-based splitting - **Enrichment**: Enrich docume …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#ingestion

[6] https://docs.mistral.ai/studio/search/search-toolkit | section: components
    Search Toolkit > Architecture > Components
    | Component | Built-in options | |-----------|-----------------| | **File loaders** | `FilesystemFileLoader`, custom loaders | | **Extractors** | `MistralOCRExtractor`, `SmartPDFExtractor`, `PlainTextExtractor`, `PyMuPDFExtractor`, `HTMLExtractor`, `SpreadsheetExtractor`, `EmailExtractor`, `EmailWithAttachmentsExtractor`, `NumbersExtractor`, `LegacyOfficeExtractor`, `MistralAudioTranscriptionExtra …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#components

[7] https://docs.mistral.ai/studio/search/search-toolkit | section: architecture
    Search Toolkit > Architecture
    **Ingestion** transforms raw documents into searchable chunks. A `FileLoader` reads raw bytes from a source, a `DocumentExtractor` converts them into a structured document, a `TextSplitter` divides it into chunks, optional `DocumentProcessor` stages (such as a `ChunkEnricher` or `SummaryEnricher`) add metadata, and an `Embedder` produces vectors for indexing into a vector store. **Retrieval** find …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#architecture

[8] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache | section: monitoring
    Semantic cache > Monitoring with metrics
    Track cache performance: ```python from mistralai.search.toolkit.retrieval.cache import CacheMetrics # Create metrics tracker metrics = CacheMetrics() cached_engine = CachedQueryEngine( engine=query_engine, cache=cache, embedder=embedder, metrics=metrics, ) # Run queries for query in queries: result = await cached_engine.search(query) # Check performance snapshot = metrics.snapshot() print(f"Hit r …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache#monitoring

[9] https://docs.mistral.ai/api/endpoint/beta/rag/search_indexes | section: operation-update_index_metrics_v1_rag_deployments_deployment_id_metrics_put
    Beta Rag Search Indexes API > Update Index Metrics
    `PUT /v1/rag/deployments/{deployment_id}/metrics` Update the metrics for a given index - Operation id: `update_index_metrics_v1_rag_deployments__deployment_id__metrics_put` - Tag: beta/rag/search_indexes
    cite: https://docs.mistral.ai/api/endpoint/beta/rag/search_indexes#operation-update_index_metrics_v1_rag_deployments_deployment_id_metrics_put

[10] https://docs.mistral.ai/api/endpoint/beta/rag/search_indexes | section: operation-update_index_metrics_v1_rag_deployments_deployment_id_metrics_put/request-body
    Beta Rag Search Indexes API > Update Index Metrics > Request body
    `application/json` (required) - one of 2 (anyOf): - UpdateMetricsRequestDeploymentMetricsOnline - `status` (string, required) - `document_count` (integer, required) - `index_metrics` (array of UpdateMetricsRequestIndexMetrics, required) - UpdateMetricsRequestDeploymentMetricsOffline - `status` (string, required) - `clear_metrics` (boolean, optional)
    cite: https://docs.mistral.ai/api/endpoint/beta/rag/search_indexes#operation-update_index_metrics_v1_rag_deployments_deployment_id_metrics_put

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit") to read hit 1 on its page
```

### 6. mistral_docs_search

```json
{"q": "evaluation", "under": "https://docs.mistral.ai/studio/search/search-toolkit", "max_hits": 10}
```

Result:

```
q: "evaluation" | under: https://docs.mistral.ai/studio/search/search-toolkit

Results: no section under https://docs.mistral.ai/studio/search/search-toolkit matched; 27 pages exist there.
next: mistral_docs_search(under="https://docs.mistral.ai/studio/search/search-toolkit") lists them; a page not listed does not exist at this commit.
```

### 7. mistral_docs_search

```json
{"q": "metrics benchmark testing Search Toolkit", "max_hits": 10}
```

Result:

```
q: "metrics benchmark testing Search Toolkit"

[1] https://docs.mistral.ai/studio/search/search-toolkit | section: search-toolkit
    Search Toolkit
    Search Toolkit is a Python framework for building information retrieval (IR) systems. It provides components for ingestion, retrieval, and evaluation. It works across backends, and every component can be swapped. LLMs are not trained on your private data. To ground their answers in your documents you need a retrieval pipeline that ingests, indexes, and searches your content. Search Toolkit gives y …
    cite: https://docs.mistral.ai/studio/search/search-toolkit

[2] https://docs.mistral.ai/studio/search/search-toolkit | section: next-steps
    Search Toolkit > Next steps
    - **[Quickstart](https://docs.mistral.ai/studio/search/search-toolkit/quickstart)**: build your first ingestion and retrieval pipeline end to end. - **[Document model](https://docs.mistral.ai/studio/search/search-toolkit/concepts/document-model)**: understand `Document`, `DocumentChunk`, and the identity that ties them together. - **[Embedding model](https://docs.mistral.ai/studio/search/search-to …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#next-steps

[3] https://docs.mistral.ai/studio/search/search-toolkit | section: retrieval
    Search Toolkit > Key features > Retrieval
    [Retrieval](https://docs.mistral.ai/studio/search/search-toolkit/retrieval) includes: - **Multiple strategies**: Vector (semantic) search with optional reranking - **Query preprocessing**: Improve user queries with LLM reformulation or query extension - **Reranking**: LLM reranker, cross-encoder reranker, or custom rerankers - **Semantic caching**: Cache results by query similarity to skip redunda …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#retrieval

[4] https://docs.mistral.ai/studio/search/search-toolkit | section: packages
    Search Toolkit > Installation and extras
    Install the core package: ```bash uv add mistralai-search-toolkit ``` Optional extras add specialized functionality: | Extra | Description | |-------|-------------| | `vespa` | Vespa plugin for vector storage and semantic search | | `extractor-pymupdf` | Advanced PDF extraction with PyMuPDF Pro | | `extractor-spreadsheet` | Spreadsheet parsing (Excel, CSV, Calamine format) | | `extractor-email` | …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#packages

[5] https://docs.mistral.ai/studio/search/search-toolkit | section: ingestion
    Search Toolkit > Key features > Ingestion
    [Ingestion](https://docs.mistral.ai/studio/search/search-toolkit/ingestion) includes: - **Multi-format extraction**: PDF/DOCX/PPTX via Mistral OCR, HTML, spreadsheets, emails, plain text - **File loading**: Load from the local filesystem or implement custom loaders for any source - **Flexible chunking**: Character, token, markdown-aware, or separator-based splitting - **Enrichment**: Enrich docume …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#ingestion

[6] https://docs.mistral.ai/studio/search/search-toolkit | section: components
    Search Toolkit > Architecture > Components
    | Component | Built-in options | |-----------|-----------------| | **File loaders** | `FilesystemFileLoader`, custom loaders | | **Extractors** | `MistralOCRExtractor`, `SmartPDFExtractor`, `PlainTextExtractor`, `PyMuPDFExtractor`, `HTMLExtractor`, `SpreadsheetExtractor`, `EmailExtractor`, `EmailWithAttachmentsExtractor`, `NumbersExtractor`, `LegacyOfficeExtractor`, `MistralAudioTranscriptionExtra …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#components

[7] https://docs.mistral.ai/studio/search/search-toolkit | section: architecture
    Search Toolkit > Architecture
    **Ingestion** transforms raw documents into searchable chunks. A `FileLoader` reads raw bytes from a source, a `DocumentExtractor` converts them into a structured document, a `TextSplitter` divides it into chunks, optional `DocumentProcessor` stages (such as a `ChunkEnricher` or `SummaryEnricher`) add metadata, and an `Embedder` produces vectors for indexing into a vector store. **Retrieval** find …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#architecture

[8] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache | section: monitoring
    Semantic cache > Monitoring with metrics
    Track cache performance: ```python from mistralai.search.toolkit.retrieval.cache import CacheMetrics # Create metrics tracker metrics = CacheMetrics() cached_engine = CachedQueryEngine( engine=query_engine, cache=cache, embedder=embedder, metrics=metrics, ) # Run queries for query in queries: result = await cached_engine.search(query) # Check performance snapshot = metrics.snapshot() print(f"Hit r …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache#monitoring

[9] https://docs.mistral.ai/api/endpoint/beta/rag/search_indexes | section: operation-update_index_metrics_v1_rag_deployments_deployment_id_metrics_put
    Beta Rag Search Indexes API > Update Index Metrics
    `PUT /v1/rag/deployments/{deployment_id}/metrics` Update the metrics for a given index - Operation id: `update_index_metrics_v1_rag_deployments__deployment_id__metrics_put` - Tag: beta/rag/search_indexes
    cite: https://docs.mistral.ai/api/endpoint/beta/rag/search_indexes#operation-update_index_metrics_v1_rag_deployments_deployment_id_metrics_put

[10] https://docs.mistral.ai/api/endpoint/beta/rag/search_indexes | section: operation-update_index_metrics_v1_rag_deployments_deployment_id_metrics_put/request-body
    Beta Rag Search Indexes API > Update Index Metrics > Request body
    `application/json` (required) - one of 2 (anyOf): - UpdateMetricsRequestDeploymentMetricsOnline - `status` (string, required) - `document_count` (integer, required) - `index_metrics` (array of UpdateMetricsRequestIndexMetrics, required) - UpdateMetricsRequestDeploymentMetricsOffline - `status` (string, required) - `clear_metrics` (boolean, optional)
    cite: https://docs.mistral.ai/api/endpoint/beta/rag/search_indexes#operation-update_index_metrics_v1_rag_deployments_deployment_id_metrics_put

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit") to read hit 1 on its page
```

### 8. mistral_docs_search

```json
{"q": "evaluation", "max_hits": 15}
```

Result:

```
q: "evaluation"

[1] https://docs.mistral.ai/api/endpoint/beta/observability/spans | section: operation-get_span_evaluation_fields_v1_observability_spans_evaluations_fields_get
    Beta Observability Spans API > Get span evaluation field definitions
    `GET /v1/observability/spans/evaluations/fields` - Operation id: `get_span_evaluation_fields_v1_observability_spans_evaluations_fields_get` - Tag: beta/observability/spans
    cite: https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_evaluation_fields_v1_observability_spans_evaluations_fields_get

[2] https://docs.mistral.ai/inference/prompting | section: prompting-examples/introduce-an-evaluation-step
    Prompting > Prompting Examples > Introduce an evaluation step
    We can also add a second step in the prompt for evaluation. We ask the LLM to generate three summaries and evaluate these three summaries. **Assistant** ``` Summary 1: The essay discusses the author's experiences with writing and programming before college, his initial struggles with learning Fortran on an IBM 1401, and the shift towards microcomputers that led to his interest in AI. He also touch …
    cite: https://docs.mistral.ai/inference/prompting#prompting-examples:~:text=We%20can%20also

[3] https://docs.mistral.ai/studio/conversations/chat-completion/prompting | section: prompting-examples/introduce-an-evaluation-step
    Prompting > Prompting Examples > Introduce an evaluation step
    We can also add a second step in the prompt for evaluation. We ask the LLM to generate three summaries and evaluate these three summaries. **Assistant** ``` Summary 1: The essay discusses the author's experiences with writing and programming before college, his initial struggles with learning Fortran on an IBM 1401, and the shift towards microcomputers that led to his interest in AI. He also touch …
    cite: https://docs.mistral.ai/studio/conversations/chat-completion/prompting#prompting-examples:~:text=We%20can%20also

[4] https://docs.mistral.ai/studio/observability/evaluations/judges | section: can-i-use-the-same-judge-across-multiple-evaluation-runs
    Judges > FAQ > Can I use the same judge across multiple evaluation runs?
    Yes. A judge is a function. Reuse it across any number of evaluators and runs. If you change the judge prompt between runs, scores won't be directly comparable.
    cite: https://docs.mistral.ai/studio/observability/evaluations/judges#can-i-use-the-same-judge-across-multiple-evaluation-runs

[5] https://docs.mistral.ai/api/endpoint/beta/observability/spans | section: operation-get_span_evaluation_field_options_v1_observability_spans_evaluations_fields_field_name_options_get
    Beta Observability Spans API > Get options for a span evaluation field
    `GET /v1/observability/spans/evaluations/fields/{field_name}/options` - Operation id: `get_span_evaluation_field_options_v1_observability_spans_evaluations_fields__field_name__options_get` - Tag: beta/observability/spans
    cite: https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_evaluation_field_options_v1_observability_spans_evaluations_fields_field_name_options_get

[6] https://docs.mistral.ai/inference/prompting | section: prompting-examples/employ-another-llm-for-evaluation
    Prompting > Prompting Examples > Employ another LLM for evaluation
    In production systems, it is common to employ another LLM for evaluation so that the evaluation step can be separate from the generation summaries. - **Step 1**: use the first LLM to generate three summaries **Assistant** ``` Summary 1: The author writes about their experiences with programming and writing before college. They started programming using Fortran on an IBM 1401 and wrote short storie …
    cite: https://docs.mistral.ai/inference/prompting#prompting-examples:~:text=In%20production%20systems%2C

[7] https://docs.mistral.ai/studio/conversations/chat-completion/prompting | section: prompting-examples/employ-another-llm-for-evaluation
    Prompting > Prompting Examples > Employ another LLM for evaluation
    In production systems, it is common to employ another LLM for evaluation so that the evaluation step can be separate from the generation summaries. - **Step 1**: use the first LLM to generate three summaries **Assistant** ``` Summary 1: The author writes about their experiences with programming and writing before college. They started programming using Fortran on an IBM 1401 and wrote short storie …
    cite: https://docs.mistral.ai/studio/conversations/chat-completion/prompting#prompting-examples:~:text=In%20production%20systems%2C

[8] https://docs.mistral.ai/studio/observability | section: offline-evaluations
    Observability > Offline evaluations
    Production traces tell you what your application _did_. Offline evaluations tell you how _well_ it performed, and whether it's improving or regressing as you change your pipeline. You define a set of test cases, run them through your pipeline, and score the outputs against criteria you control. Results upload to Studio, where you can track quality trends over time and compare pipeline configuratio …
    cite: https://docs.mistral.ai/studio/observability#offline-evaluations

[9] https://docs.mistral.ai/studio/observability/evaluations | section: organizing-in-studio
    Offline evaluations > Organizing runs in Studio
    Use **Projects** and **Evaluations** to organize runs: - **Project**: groups related evaluations for a system (for example, `"Language Detection"`). - **Evaluation**: a specific evaluation within a project (for example, `"Accuracy Eval"`). - **Run**: each call to `evaluation.run()` creates a new run under the evaluation. ```python run = await client.evaluation.run( project=Project(name="My Project …
    cite: https://docs.mistral.ai/studio/observability/evaluations#organizing-in-studio

[10] https://docs.mistral.ai/studio/observability/evaluations/datasets | section: can-i-pass-a-studio-dataset-id-directly-to-evaluationrun
    Datasets > FAQ > Can I pass a Studio Dataset ID directly to evaluation.run()?
    Not currently. `evaluation.run()` expects records in memory. Fetch records from Studio first, transform them into your evaluation record shape, then pass the resulting list to `dataset`.
    cite: https://docs.mistral.ai/studio/observability/evaluations/datasets#can-i-pass-a-studio-dataset-id-directly-to-evaluationrun

[11] https://docs.mistral.ai/studio/observability/evaluations/local-mode | section: recommended-workflow
    Iterate locally > Recommended workflow
    1. **Iterate locally**: set `local=True` and adjust your task and scorers until results look right. 2. **Push to Studio**: remove `local=True` and add `project` and `evaluation` to track results over time. ```python # Step 1: iterate locally run = await client.evaluation.run( dataset=dataset, task=task, evaluators=[Evaluator(name="accuracy", scorer=scorer)], local=True, ) # Step 2: happy with resu …
    cite: https://docs.mistral.ai/studio/observability/evaluations/local-mode#recommended-workflow

[12] https://docs.mistral.ai/studio/observability/evaluations/datasets | section: organizing-in-studio
    Datasets > Organizing in Studio
    The Evaluation SDK organizes results using **Projects**, **Evaluations**, and **Runs** in Studio, not by the dataset itself. Pass your dataset directly to `evaluation.run()`: ```python from mistralai.observability import Evaluation, Project run = await client.evaluation.run( project=Project(name="Language Detection"), evaluation=Evaluation(name="Accuracy Eval"), dataset=dataset, # your list of dic …
    cite: https://docs.mistral.ai/studio/observability/evaluations/datasets#organizing-in-studio

[13] https://docs.mistral.ai/api/endpoint/beta/observability/spans | section: operation-get_span_evaluation_fields_v1_observability_spans_evaluations_fields_get/responses
    Beta Observability Spans API > Get span evaluation field definitions > Responses
    - `200` — Successful Response (application/json, schema GetSpanEvaluationFields) - `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError) - `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError) - `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError) - `409` — Conflict - Resourc …
    cite: https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_evaluation_fields_v1_observability_spans_evaluations_fields_get

[14] https://docs.mistral.ai/studio/observability/evaluations/local-mode | section: usage
    Iterate locally > Usage
    ```python run = await client.evaluation.run( dataset=dataset, task=task, evaluators=[Evaluator(name="accuracy", scorer=scorer)], local=True, ) run.show(level="records") ``` In local mode: - No data is sent to Studio. - You don't need to specify a `project` or `evaluation`. - Results are only available in your terminal or as JSON.
    cite: https://docs.mistral.ai/studio/observability/evaluations/local-mode#usage

[15] https://docs.mistral.ai/studio/observability/evaluations/run-evaluators | section: basic-run-evaluator
    Use run-level evaluators > Basic run evaluator
    A run evaluator receives a `RunEvaluatorContext` with all records, statistics, and metadata: ```python import asyncio import os from mistralai.observability import ( Evaluation, Evaluator, Mistral, RunEvaluator, RunEvaluatorContext, ScorerContext, System, TaskContext, ) client = Mistral(api_key=os.environ["MISTRAL_API_KEY"]) def accuracy_scorer(ctx: ScorerContext) -> int: return 1 if ctx.input_rec …
    cite: https://docs.mistral.ai/studio/observability/evaluations/run-evaluators#basic-run-evaluator

Results: 15 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/api/endpoint/beta/observability/spans") to read hit 1 on its page
```

### 9. mistral_docs_search

```json
{"q": "Search Toolkit evaluator", "max_hits": 10}
```

Result:

```
q: "Search Toolkit evaluator"

[1] https://docs.mistral.ai/studio/search/search-toolkit | section: search-toolkit
    Search Toolkit
    Search Toolkit is a Python framework for building information retrieval (IR) systems. It provides components for ingestion, retrieval, and evaluation. It works across backends, and every component can be swapped. LLMs are not trained on your private data. To ground their answers in your documents you need a retrieval pipeline that ingests, indexes, and searches your content. Search Toolkit gives y …
    cite: https://docs.mistral.ai/studio/search/search-toolkit

[2] https://docs.mistral.ai/studio/search/search-toolkit | section: next-steps
    Search Toolkit > Next steps
    - **[Quickstart](https://docs.mistral.ai/studio/search/search-toolkit/quickstart)**: build your first ingestion and retrieval pipeline end to end. - **[Document model](https://docs.mistral.ai/studio/search/search-toolkit/concepts/document-model)**: understand `Document`, `DocumentChunk`, and the identity that ties them together. - **[Embedding model](https://docs.mistral.ai/studio/search/search-to …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#next-steps

[3] https://docs.mistral.ai/studio/search/search-toolkit | section: retrieval
    Search Toolkit > Key features > Retrieval
    [Retrieval](https://docs.mistral.ai/studio/search/search-toolkit/retrieval) includes: - **Multiple strategies**: Vector (semantic) search with optional reranking - **Query preprocessing**: Improve user queries with LLM reformulation or query extension - **Reranking**: LLM reranker, cross-encoder reranker, or custom rerankers - **Semantic caching**: Cache results by query similarity to skip redunda …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#retrieval

[4] https://docs.mistral.ai/studio/search/search-toolkit | section: packages
    Search Toolkit > Installation and extras
    Install the core package: ```bash uv add mistralai-search-toolkit ``` Optional extras add specialized functionality: | Extra | Description | |-------|-------------| | `vespa` | Vespa plugin for vector storage and semantic search | | `extractor-pymupdf` | Advanced PDF extraction with PyMuPDF Pro | | `extractor-spreadsheet` | Spreadsheet parsing (Excel, CSV, Calamine format) | | `extractor-email` | …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#packages

[5] https://docs.mistral.ai/studio/search/search-toolkit | section: ingestion
    Search Toolkit > Key features > Ingestion
    [Ingestion](https://docs.mistral.ai/studio/search/search-toolkit/ingestion) includes: - **Multi-format extraction**: PDF/DOCX/PPTX via Mistral OCR, HTML, spreadsheets, emails, plain text - **File loading**: Load from the local filesystem or implement custom loaders for any source - **Flexible chunking**: Character, token, markdown-aware, or separator-based splitting - **Enrichment**: Enrich docume …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#ingestion

[6] https://docs.mistral.ai/studio/search/search-toolkit | section: components
    Search Toolkit > Architecture > Components
    | Component | Built-in options | |-----------|-----------------| | **File loaders** | `FilesystemFileLoader`, custom loaders | | **Extractors** | `MistralOCRExtractor`, `SmartPDFExtractor`, `PlainTextExtractor`, `PyMuPDFExtractor`, `HTMLExtractor`, `SpreadsheetExtractor`, `EmailExtractor`, `EmailWithAttachmentsExtractor`, `NumbersExtractor`, `LegacyOfficeExtractor`, `MistralAudioTranscriptionExtra …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#components

[7] https://docs.mistral.ai/studio/search/search-toolkit | section: architecture
    Search Toolkit > Architecture
    **Ingestion** transforms raw documents into searchable chunks. A `FileLoader` reads raw bytes from a source, a `DocumentExtractor` converts them into a structured document, a `TextSplitter` divides it into chunks, optional `DocumentProcessor` stages (such as a `ChunkEnricher` or `SummaryEnricher`) add metadata, and an `Embedder` produces vectors for indexing into a vector store. **Retrieval** find …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#architecture

[8] https://docs.mistral.ai/studio/search/agentic-search | section: next-steps
    Agentic Search > Next steps
    - [Search Toolkit](https://docs.mistral.ai/studio/search/search-toolkit): learn about ingestion pipelines, retrieval strategies, and the full SDK. - [Libraries](https://docs.mistral.ai/studio/search/libraries): use managed document ingestion and search for built-in RAG. - [Connectors](https://docs.mistral.ai/studio/connectors): connect models and agents to external tools and data sources. - [Agent …
    cite: https://docs.mistral.ai/studio/search/agentic-search#next-steps

[9] https://docs.mistral.ai/studio/search/search-toolkit/search-index | section: available-vector-stores
    Search index > Available backends
    | Backend | Purpose | |---------|---------| | **[Vespa](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa)** | Vector database with schema management, ranking, clustering, and replication | | **[Postgres](https://docs.mistral.ai/studio/search/search-toolkit/search-index/postgres)** | PostgreSQL with `pgvector` and `pg_textsearch` for dense and hybrid search | | **[Custom vect …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/search-index#available-vector-stores

[10] https://docs.mistral.ai/studio/search/agentic-search | section: latency
    Agentic Search > Latency and tradeoffs
    Each tool call has a cost, but navigation can reduce end-to-end latency and token usage because the model converges faster. Instead of repeatedly issuing broad searches, the agent can stay inside the right source, use `grep` to jump to specific terms, and use `exclude_ids` to avoid revisiting the same chunks. In the Agentic Search benchmarks cited in the Search Toolkit launch materials, the full a …
    cite: https://docs.mistral.ai/studio/search/agentic-search#latency

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit") to read hit 1 on its page
```

### 10. mistral_docs_search

```json
{"q": "retrieval evaluation metrics Search Toolkit", "max_hits": 10}
```

Result:

```
q: "retrieval evaluation metrics Search Toolkit"

[1] https://docs.mistral.ai/studio/search/search-toolkit | section: search-toolkit
    Search Toolkit
    Search Toolkit is a Python framework for building information retrieval (IR) systems. It provides components for ingestion, retrieval, and evaluation. It works across backends, and every component can be swapped. LLMs are not trained on your private data. To ground their answers in your documents you need a retrieval pipeline that ingests, indexes, and searches your content. Search Toolkit gives y …
    cite: https://docs.mistral.ai/studio/search/search-toolkit

[2] https://docs.mistral.ai/studio/search/search-toolkit | section: retrieval
    Search Toolkit > Key features > Retrieval
    [Retrieval](https://docs.mistral.ai/studio/search/search-toolkit/retrieval) includes: - **Multiple strategies**: Vector (semantic) search with optional reranking - **Query preprocessing**: Improve user queries with LLM reformulation or query extension - **Reranking**: LLM reranker, cross-encoder reranker, or custom rerankers - **Semantic caching**: Cache results by query similarity to skip redunda …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#retrieval

[3] https://docs.mistral.ai/studio/search/search-toolkit/retrieval | section: components
    Retrieval > Components
    Each retrieval component is documented in detail with examples and best practices: - **[Retrievers](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers)**: VectorRetriever, KeywordRetriever, and hybrid search patterns - **[Rerankers](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers)**: LLMReRanker, CrossEncoderReRanker, RRF fusion, and custom rerankers …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval#components

[4] https://docs.mistral.ai/studio/search/search-toolkit | section: next-steps
    Search Toolkit > Next steps
    - **[Quickstart](https://docs.mistral.ai/studio/search/search-toolkit/quickstart)**: build your first ingestion and retrieval pipeline end to end. - **[Document model](https://docs.mistral.ai/studio/search/search-toolkit/concepts/document-model)**: understand `Document`, `DocumentChunk`, and the identity that ties them together. - **[Embedding model](https://docs.mistral.ai/studio/search/search-to …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#next-steps

[5] https://docs.mistral.ai/studio/search/search-toolkit/retrieval | section: retrieval
    Retrieval
    Retrieval finds relevant chunks for a given user query. Search Toolkit supports vector (semantic), keyword (BM25), and hybrid search strategies that can be combined for optimal results. An optional **query preprocessor** transforms the raw query before search — rewriting it for clarity or expanding it into multiple variants. One or more **Retrievers** execute the search against the index. They can …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval

[6] https://docs.mistral.ai/studio/search/search-toolkit/retrieval | section: query-engine
    Retrieval > Query engine
    `QueryEngine` orchestrates the retrieval pipeline. It accepts one or more retrievers, optional query preprocessing, and optional rerankers: ```python from mistralai.search.toolkit.retrieval import QueryEngine from mistralai.search.toolkit.retrieval.retrievers import VectorRetriever from mistralai.search.toolkit.retrieval.rerankers import LLMReRanker from mistralai.search.toolkit.retrieval.pre_proc …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval#query-engine

[7] https://docs.mistral.ai/studio/search/search-toolkit | section: architecture
    Search Toolkit > Architecture
    **Ingestion** transforms raw documents into searchable chunks. A `FileLoader` reads raw bytes from a source, a `DocumentExtractor` converts them into a structured document, a `TextSplitter` divides it into chunks, optional `DocumentProcessor` stages (such as a `ChunkEnricher` or `SummaryEnricher`) add metadata, and an `Embedder` produces vectors for indexing into a vector store. **Retrieval** find …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#architecture

[8] https://docs.mistral.ai/studio/search/search-toolkit | section: packages
    Search Toolkit > Installation and extras
    Install the core package: ```bash uv add mistralai-search-toolkit ``` Optional extras add specialized functionality: | Extra | Description | |-------|-------------| | `vespa` | Vespa plugin for vector storage and semantic search | | `extractor-pymupdf` | Advanced PDF extraction with PyMuPDF Pro | | `extractor-spreadsheet` | Spreadsheet parsing (Excel, CSV, Calamine format) | | `extractor-email` | …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#packages

[9] https://docs.mistral.ai/studio/search/search-toolkit | section: ingestion
    Search Toolkit > Key features > Ingestion
    [Ingestion](https://docs.mistral.ai/studio/search/search-toolkit/ingestion) includes: - **Multi-format extraction**: PDF/DOCX/PPTX via Mistral OCR, HTML, spreadsheets, emails, plain text - **File loading**: Load from the local filesystem or implement custom loaders for any source - **Flexible chunking**: Character, token, markdown-aware, or separator-based splitting - **Enrichment**: Enrich docume …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#ingestion

[10] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache | section: monitoring
    Semantic cache > Monitoring with metrics
    Track cache performance: ```python from mistralai.search.toolkit.retrieval.cache import CacheMetrics # Create metrics tracker metrics = CacheMetrics() cached_engine = CachedQueryEngine( engine=query_engine, cache=cache, embedder=embedder, metrics=metrics, ) # Run queries for query in queries: result = await cached_engine.search(query) # Check performance snapshot = metrics.snapshot() print(f"Hit r …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache#monitoring

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit") to read hit 1 on its page
```

### 11. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache"}
```

Result:

```
page: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache | "Semantic cache"

## section: semantic-cache
    Semantic cache
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache
# Semantic cache

The semantic cache matches queries by meaning rather than exact string matching. When a query is semantically similar to a previously cached one, the cache returns stored results and skips embedding, retrieval, preprocessing, and reranking.

## section: basic-setup
    Semantic cache > Basic setup
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache#basic-setup
## Basic setup {#basic-setup}

**Installation**: Core library (no extra required)

**Example**:

```python
from mistralai.search.toolkit.retrieval.cache import (
    CachedQueryEngine,
    InMemoryCacheBackend,
    SemanticCache,
    EvictionPolicy,
)

# 1. Create a cache backend
backend = InMemoryCacheBackend(
    dim=1024,                          # Embedding dimensionality
    max_entries=500,                   # Max cached queries
    ttl_seconds=3600,                  # 1-hour expiration
    eviction_policy=EvictionPolicy.LRU,
)

# 2. Create the semantic cache
cache = SemanticCache(
    backend=backend,
    similarity_threshold=0.95,  # 95% cosine similarity = cache hit
)

# 3. Wrap your QueryEngine
cached_engine = CachedQueryEngine(
    engine=query_engine,
    cache=cache,
    embedder=embedder,  # Used to embed incoming queries
)

# 4. Use normally. Caching is transparent.
result = await cached_engine.search("What is RAG?", top_k=10)
# First call: embedding + retrieval → cached
# Second call with similar query: cache hit → instant
```

**How it works**:

1. Query comes in
2. Embedder converts query to vector
3. Cache searches for similar cached query vectors
4. If similarity > threshold: return cached results (fast)
5. If no match: run full retrieval pipeline, cache results (slow but cached for future)

## section: configuration
    Semantic cache > Configuration
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache#configuration
## Configuration {#configuration}

**Backend options**:

| Option | Default | Purpose |
|--------|---------|---------|
| `dim` | *(required)* | Embedding dimensionality (1024 for mistral-embed) |
| `max_entries` | 1000 | Max cached queries before eviction |
| `ttl_seconds` | None | Entry expiration in seconds (None = no expiry) |
| `eviction_policy` | LRU | LRU, LFU, or FIFO |

**Cache sensitivity**:

| Setting | Effect | Use case |
|---------|--------|----------|
| `similarity_threshold=0.99` | Very strict, fewer hits | Exact answer matching |
| `similarity_threshold=0.95` | Balanced (default) | Most use cases |
| `similarity_threshold=0.90` | Permissive, more hits | Approximate answers acceptable |

```python
# High sensitivity (strict matching)
cache = SemanticCache(
    backend=InMemoryCacheBackend(dim=1024, max_entries=500),
    similarity_threshold=0.99,
)

# Low sensitivity (broad matching)
cache = SemanticCache(
    backend=InMemoryCacheBackend(dim=1024, max_entries=500),
    similarity_threshold=0.90,
)
```

**Eviction policies**:

- **LRU** (Least Recently Used): evict least recently accessed entries
- **LFU** (Least Frequently Used): evict least frequently accessed entries
- **FIFO** (First In First Out): evict oldest entries

```python
backend = InMemoryCacheBackend(
    dim=1024,
    max_entries=500,
    eviction_policy=EvictionPolicy.LFU,  # Cache frequently asked queries
)
```

## section: monitoring
    Semantic cache > Monitoring with metrics
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache#monitoring
## Monitoring with metrics {#monitoring}

Track cache performance:

```python
from mistralai.search.toolkit.retrieval.cache import CacheMetrics

# Create metrics tracker
metrics = CacheMetrics()

cached_engine = CachedQueryEngine(
    engine=query_engine,
    cache=cache,
    embedder=embedder,
    metrics=metrics,
)

# Run queries
for query in queries:
    result = await cached_engine.search(query)

# Check performance
snapshot = metrics.snapshot()
print(f"Hit rate: {snapshot.hit_rate:.1%}")
print(f"Avg hit similarity: {snapshot.avg_hit_similarity:.3f}")
print(f"Total requests: {snapshot.total_requests}")
print(f"Evictions: {snapshot.evictions}")
```

**Available metrics**:

| Metric | Description |
|--------|-------------|
| `hit_rate` | Fraction of queries served from cache |
| `avg_hit_similarity` | Average cosine similarity on cache hits |
| `total_requests` | Total queries processed |
| `avg_embed_time_ms` | Average embedding time per query |
| `avg_lookup_time_ms` | Average cache lookup time per query |
| `avg_retrieval_time_ms` | Average retrieval time when cache misses |
| `evictions` | Total entries evicted due to capacity |
| `errors` | Total cache/embedder errors |

**Example monitoring**:

```python
# Track performance over time
if snapshot.hit_rate > 0.5:
    print(f"✓ Good hit rate: {snapshot.hit_rate:.1%}")
    print(f"  Avg similarity: {snapshot.avg_hit_similarity:.3f}")
else:
    print(f"⚠ Low hit rate: {snapshot.hit_rate:.1%}")
    print(f"  Consider lowering similarity_threshold")

if snapshot.evictions > max_entries * 0.1:
    print(f"⚠ High eviction rate")
    print(f"  Consider increasing max_entries or using LFU policy")
```

## section: fault-tolerance
    Semantic cache > Fault tolerance
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache#fault-tolerance
## Fault tolerance {#fault-tolerance}

All cache operations are non-fatal. If the cache or embedder throws an exception, the query falls through to the uncached path:

```python
# Even if cache fails, retrieval continues
cached_engine = CachedQueryEngine(
    engine=query_engine,
    cache=cache,
    embedder=embedder,
)

# If embedder or cache throws exception:
# - Exception is logged
# - Query runs through normal pipeline
# - Result is NOT cached
# - Pipeline reliability is unaffected

result = await cached_engine.search(query="...", top_k=10)
# Always returns a result, cache is best-effort
```

**Monitoring errors**:

```python
snapshot = metrics.snapshot()
if snapshot.errors > 0:
    print(f"Cache errors: {snapshot.errors}")
    print("Check logs for details. Retrieval pipeline is unaffected.")
```

## section: cache-invalidation
    Semantic cache > Cache management
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache#cache-invalidation
## Cache management {#cache-invalidation}

**Invalidate by namespace**:

```python
# Invalidate cache for a specific namespace
await cache.invalidate(namespace="query_engine")

# All entries in that namespace are removed
```

**Clear entire cache**:

```python
# Remove all cached entries
await cache.clear()
```

**TTL-based expiration**:

```python
# Entries expire automatically after ttl_seconds
backend = InMemoryCacheBackend(
    dim=1024,
    max_entries=500,
    ttl_seconds=3600,  # 1-hour expiration
)

# Expired entries are removed on next access or eviction
```

**Custom backends** implement the `CacheBackend` ABC to plug in any storage (Redis, pgvector, etc.):

```python
from mistralai.search.toolkit.retrieval.cache import CacheBackend, CacheEntry

class CustomCacheBackend(CacheBackend):
    @property
    def max_entries(self) -> int:
        return 1000

    async def search(self, query_embedding, namespace, n_results):
        # Vector similarity search in your store
        ...

    async def store(self, entry: CacheEntry) -> None:
        # Store entry, evict if needed
        ...

    async def delete(self, entry_id: str):
        ...

    async def get_all(self, namespace=None):
        ...

    async def count(self, namespace=None) -> int:
        ...

    async def clear(self):
        ...

    async def update_hit(self, entry: CacheEntry):
        ...
```

## section: best-practices
    Semantic cache > Best practices
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache#best-practices
## Best practices {#best-practices}

**1. Monitor hit rate**:

```python
# Track performance to validate cache effectiveness
if metrics.snapshot().hit_rate < 0.2:
    # Cache isn't being used effectively
    # Consider:
    # - Lowering similarity_threshold
    # - Increasing max_entries
    # - Analyzing query patterns
    ...
```

**2. Right-size the cache**:

```python
# Based on expected queries and memory
# 1024-dim embeddings ≈ 4KB per entry
backend = InMemoryCacheBackend(
    dim=1024,
    max_entries=1000,  # ~4MB cache
    ttl_seconds=3600,
)
```

**3. Use with multi-stage retrieval**:

```python
# Caching is most valuable when downstream is expensive
cached_engine = CachedQueryEngine(
    engine=QueryEngine(
        retriever=vector_retriever,
        rerankers=[
            LLMReRanker(llm_provider=llm, top_k=10),  # Expensive!
        ],
    ),
    cache=cache,
    embedder=embedder,
)

# Cache avoids expensive LLM reranking on cache hits
```

**4. Thresholds for different use cases**:

```python
# Conservative (exact answers)
similarity_threshold=0.98

# Balanced (most Q&A systems)
similarity_threshold=0.95

# Permissive (approximate answers ok)
similarity_threshold=0.90
```

## section: see-also
    Semantic cache > See also
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache#see-also
## See also {#see-also}

- [Retrieval overview](https://docs.mistral.ai/studio/search/search-toolkit/retrieval): retrieval pipeline architecture
- [Retrievers](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers): vector search
- [Rerankers](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers): refine results after retrieval
- [Query preprocessing](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/preprocessing): improve queries before retrieval

Results: 8 sections, the whole page.
```

### 12. mistral_docs_search

```json
{"q": "Search Toolkit evaluation module", "max_hits": 10}
```

Result:

```
q: "Search Toolkit evaluation module"

[1] https://docs.mistral.ai/studio/search/search-toolkit | section: search-toolkit
    Search Toolkit
    Search Toolkit is a Python framework for building information retrieval (IR) systems. It provides components for ingestion, retrieval, and evaluation. It works across backends, and every component can be swapped. LLMs are not trained on your private data. To ground their answers in your documents you need a retrieval pipeline that ingests, indexes, and searches your content. Search Toolkit gives y …
    cite: https://docs.mistral.ai/studio/search/search-toolkit

[2] https://docs.mistral.ai/studio/search/search-toolkit | section: next-steps
    Search Toolkit > Next steps
    - **[Quickstart](https://docs.mistral.ai/studio/search/search-toolkit/quickstart)**: build your first ingestion and retrieval pipeline end to end. - **[Document model](https://docs.mistral.ai/studio/search/search-toolkit/concepts/document-model)**: understand `Document`, `DocumentChunk`, and the identity that ties them together. - **[Embedding model](https://docs.mistral.ai/studio/search/search-to …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#next-steps

[3] https://docs.mistral.ai/studio/search/search-toolkit | section: retrieval
    Search Toolkit > Key features > Retrieval
    [Retrieval](https://docs.mistral.ai/studio/search/search-toolkit/retrieval) includes: - **Multiple strategies**: Vector (semantic) search with optional reranking - **Query preprocessing**: Improve user queries with LLM reformulation or query extension - **Reranking**: LLM reranker, cross-encoder reranker, or custom rerankers - **Semantic caching**: Cache results by query similarity to skip redunda …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#retrieval

[4] https://docs.mistral.ai/studio/search/search-toolkit | section: packages
    Search Toolkit > Installation and extras
    Install the core package: ```bash uv add mistralai-search-toolkit ``` Optional extras add specialized functionality: | Extra | Description | |-------|-------------| | `vespa` | Vespa plugin for vector storage and semantic search | | `extractor-pymupdf` | Advanced PDF extraction with PyMuPDF Pro | | `extractor-spreadsheet` | Spreadsheet parsing (Excel, CSV, Calamine format) | | `extractor-email` | …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#packages

[5] https://docs.mistral.ai/studio/search/search-toolkit | section: ingestion
    Search Toolkit > Key features > Ingestion
    [Ingestion](https://docs.mistral.ai/studio/search/search-toolkit/ingestion) includes: - **Multi-format extraction**: PDF/DOCX/PPTX via Mistral OCR, HTML, spreadsheets, emails, plain text - **File loading**: Load from the local filesystem or implement custom loaders for any source - **Flexible chunking**: Character, token, markdown-aware, or separator-based splitting - **Enrichment**: Enrich docume …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#ingestion

[6] https://docs.mistral.ai/studio/search/search-toolkit | section: components
    Search Toolkit > Architecture > Components
    | Component | Built-in options | |-----------|-----------------| | **File loaders** | `FilesystemFileLoader`, custom loaders | | **Extractors** | `MistralOCRExtractor`, `SmartPDFExtractor`, `PlainTextExtractor`, `PyMuPDFExtractor`, `HTMLExtractor`, `SpreadsheetExtractor`, `EmailExtractor`, `EmailWithAttachmentsExtractor`, `NumbersExtractor`, `LegacyOfficeExtractor`, `MistralAudioTranscriptionExtra …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#components

[7] https://docs.mistral.ai/studio/search/search-toolkit | section: architecture
    Search Toolkit > Architecture
    **Ingestion** transforms raw documents into searchable chunks. A `FileLoader` reads raw bytes from a source, a `DocumentExtractor` converts them into a structured document, a `TextSplitter` divides it into chunks, optional `DocumentProcessor` stages (such as a `ChunkEnricher` or `SummaryEnricher`) add metadata, and an `Embedder` produces vectors for indexing into a vector store. **Retrieval** find …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#architecture

[8] https://docs.mistral.ai/studio/search/search-toolkit/changelog | section: 0-0-12
    Changelog > 0.0.12
    **Breaking changes** _Checkpoint serialization_ - A new `document/serialization.py` module introduces a `DocumentTypeRegistry` and stable type ids so that document classes can be round-tripped through an external service safely. **Improvements** - Added `MistralClientConfig` and `build_mistral_client()` to centralize Mistral SDK client creation for whole pipelines. - Added [`SmartPDFExtractor`](ht …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/changelog#0-0-12

[9] https://docs.mistral.ai/studio/search/agentic-search | section: next-steps
    Agentic Search > Next steps
    - [Search Toolkit](https://docs.mistral.ai/studio/search/search-toolkit): learn about ingestion pipelines, retrieval strategies, and the full SDK. - [Libraries](https://docs.mistral.ai/studio/search/libraries): use managed document ingestion and search for built-in RAG. - [Connectors](https://docs.mistral.ai/studio/connectors): connect models and agents to external tools and data sources. - [Agent …
    cite: https://docs.mistral.ai/studio/search/agentic-search#next-steps

[10] https://docs.mistral.ai/studio/search/search-toolkit/search-index | section: available-vector-stores
    Search index > Available backends
    | Backend | Purpose | |---------|---------| | **[Vespa](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa)** | Vector database with schema management, ranking, clustering, and replication | | **[Postgres](https://docs.mistral.ai/studio/search/search-toolkit/search-index/postgres)** | PostgreSQL with `pgvector` and `pg_textsearch` for dense and hybrid search | | **[Custom vect …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/search-index#available-vector-stores

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit") to read hit 1 on its page
```

### 13. mistral_docs_search

```json
{"q": "precision recall NDCG MRR Search Toolkit", "max_hits": 10}
```

Result:

```
q: "precision recall NDCG MRR Search Toolkit"

[1] https://docs.mistral.ai/studio/search/search-toolkit | section: search-toolkit
    Search Toolkit
    Search Toolkit is a Python framework for building information retrieval (IR) systems. It provides components for ingestion, retrieval, and evaluation. It works across backends, and every component can be swapped. LLMs are not trained on your private data. To ground their answers in your documents you need a retrieval pipeline that ingests, indexes, and searches your content. Search Toolkit gives y …
    cite: https://docs.mistral.ai/studio/search/search-toolkit

[2] https://docs.mistral.ai/studio/search/search-toolkit | section: next-steps
    Search Toolkit > Next steps
    - **[Quickstart](https://docs.mistral.ai/studio/search/search-toolkit/quickstart)**: build your first ingestion and retrieval pipeline end to end. - **[Document model](https://docs.mistral.ai/studio/search/search-toolkit/concepts/document-model)**: understand `Document`, `DocumentChunk`, and the identity that ties them together. - **[Embedding model](https://docs.mistral.ai/studio/search/search-to …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#next-steps

[3] https://docs.mistral.ai/studio/search/search-toolkit | section: retrieval
    Search Toolkit > Key features > Retrieval
    [Retrieval](https://docs.mistral.ai/studio/search/search-toolkit/retrieval) includes: - **Multiple strategies**: Vector (semantic) search with optional reranking - **Query preprocessing**: Improve user queries with LLM reformulation or query extension - **Reranking**: LLM reranker, cross-encoder reranker, or custom rerankers - **Semantic caching**: Cache results by query similarity to skip redunda …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#retrieval

[4] https://docs.mistral.ai/studio/search/search-toolkit | section: packages
    Search Toolkit > Installation and extras
    Install the core package: ```bash uv add mistralai-search-toolkit ``` Optional extras add specialized functionality: | Extra | Description | |-------|-------------| | `vespa` | Vespa plugin for vector storage and semantic search | | `extractor-pymupdf` | Advanced PDF extraction with PyMuPDF Pro | | `extractor-spreadsheet` | Spreadsheet parsing (Excel, CSV, Calamine format) | | `extractor-email` | …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#packages

[5] https://docs.mistral.ai/studio/search/search-toolkit | section: ingestion
    Search Toolkit > Key features > Ingestion
    [Ingestion](https://docs.mistral.ai/studio/search/search-toolkit/ingestion) includes: - **Multi-format extraction**: PDF/DOCX/PPTX via Mistral OCR, HTML, spreadsheets, emails, plain text - **File loading**: Load from the local filesystem or implement custom loaders for any source - **Flexible chunking**: Character, token, markdown-aware, or separator-based splitting - **Enrichment**: Enrich docume …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#ingestion

[6] https://docs.mistral.ai/studio/observability/evaluations/run-evaluators | section: computing-f1-with-get-score
    Use run-level evaluators > Computing F1 with get_score
    The `get_score()` helper extracts individual evaluator scores from run evaluator records: ```python from mistralai.observability import RunEvaluator, RunEvaluatorContext, Score, get_score def f1_scorer(ctx: RunEvaluatorContext) -> Score: tp = fp = fn = 0 for record in ctx.records: predicted = get_score(record, "predicted_label").value expected = get_score(record, "expected_label").value if predict …
    cite: https://docs.mistral.ai/studio/observability/evaluations/run-evaluators#computing-f1-with-get-score

[7] https://docs.mistral.ai/studio/search/search-toolkit | section: components
    Search Toolkit > Architecture > Components
    | Component | Built-in options | |-----------|-----------------| | **File loaders** | `FilesystemFileLoader`, custom loaders | | **Extractors** | `MistralOCRExtractor`, `SmartPDFExtractor`, `PlainTextExtractor`, `PyMuPDFExtractor`, `HTMLExtractor`, `SpreadsheetExtractor`, `EmailExtractor`, `EmailWithAttachmentsExtractor`, `NumbersExtractor`, `LegacyOfficeExtractor`, `MistralAudioTranscriptionExtra …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#components

[8] https://docs.mistral.ai/studio/search/agentic-search | section: retrieval-primitives-agentic-loop
    Agentic Search > Retrieval primitives and the agentic loop
    Agentic Search is not another retrieval method next to keyword or semantic search. Keyword and semantic search are retrieval primitives. Agentic Search is an orchestration layer that uses those primitives, adds navigation, and iterates until the model has enough evidence. | Layer | How it works | Best for | |-------|-------------|----------| | Keyword (lexical) | Matches exact terms or phrases | K …
    cite: https://docs.mistral.ai/studio/search/agentic-search#retrieval-primitives-agentic-loop

[9] https://docs.mistral.ai/studio/search/search-toolkit | section: architecture
    Search Toolkit > Architecture
    **Ingestion** transforms raw documents into searchable chunks. A `FileLoader` reads raw bytes from a source, a `DocumentExtractor` converts them into a structured document, a `TextSplitter` divides it into chunks, optional `DocumentProcessor` stages (such as a `ChunkEnricher` or `SummaryEnricher`) add metadata, and an `Embedder` produces vectors for indexing into a vector store. **Retrieval** find …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#architecture

[10] https://docs.mistral.ai/studio/search/agentic-search | section: sdk-patterns
    Agentic Search > Use Agentic Search with the SDK > Core SDK patterns
    The SDK snippets build from the smallest setup to more advanced retrieval. Use the tabs to start with the client, run a query, then add preprocessing or hybrid retrieval. **Client** ```python from mistralai.client import Mistral from mistralai.search.toolkit.embedders import MistralEmbedder client = Mistral(api_key="your-api-key") embedder = MistralEmbedder(client=client) ``` **Query engine** Crea …
    cite: https://docs.mistral.ai/studio/search/agentic-search#sdk-patterns

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit") to read hit 1 on its page
```

### 14. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/search/search-toolkit/quickstart"}
```

Result:

```
page: https://docs.mistral.ai/studio/search/search-toolkit/quickstart | "Quickstart"

## section: quickstart
    Quickstart
    cite: https://docs.mistral.ai/studio/search/search-toolkit/quickstart
# Quickstart

Build a RAG pipeline in 5 minutes: ingest documents into a vector store, then search them.

## section: prerequisites
    Quickstart > Prerequisites
    cite: https://docs.mistral.ai/studio/search/search-toolkit/quickstart#prerequisites
## Prerequisites {#prerequisites}

- **Python 3.12+**
- **Docker** (for running Vespa locally)
- A **Mistral API key** from [console.mistral.ai](https://console.mistral.ai/)

## section: install
    Quickstart > Install
    cite: https://docs.mistral.ai/studio/search/search-toolkit/quickstart#install
## Install {#install}

Install Search Toolkit with the Vespa plugin using [uv](https://docs.astral.sh/uv/):

```bash
uv add "mistralai-search-toolkit[vespa]"
```

## section: setup-vespa
    Quickstart > Set up Vespa
    cite: https://docs.mistral.ai/studio/search/search-toolkit/quickstart#setup-vespa
## Set up Vespa {#setup-vespa}

Start a local Vespa instance with Docker:

```bash
docker run --detach \
  --name vespa \
  --hostname vespa-container \
  --publish 8080:8080 \
  --publish 19071:19071 \
  vespaengine/vespa
```

Wait for Vespa to be healthy:

```bash
curl --retry 10 --retry-delay 3 --retry-all-errors \
  http://localhost:19071/state/v1/health
```

Set your Mistral API key:

```bash
export MISTRAL_API_KEY=your-api-key
```

## section: define-schema
    Quickstart > Define your schema
    cite: https://docs.mistral.ai/studio/search/search-toolkit/quickstart#define-schema
## Define your schema {#define-schema}

Create a migration to describe the structure of your documents:

```bash
mistral-vespa generate-migration \
  --app-dir ./vespa/migrations \
  initial_schema
```

Fill in the generated file:

```python
from mistralai.search.toolkit.embedding import MistralEmbeddingPreset
from mistralai.search.toolkit.plugins.vespa.app.schemas.app import FieldDefinition, IndexingMode, SearchMode
from mistralai.search.toolkit.plugins.vespa.migration import VespaMigration, create_schema, set_app_name


class InitialSchema(VespaMigration):
    def migrate(self) -> None:
        set_app_name("myquickstart")
        create_schema(
            name="quickstart_collection",
            mode=SearchMode.INDEX,
            embedding_model=MistralEmbeddingPreset.MISTRAL_EMBED_DIM_1024,
            indexing_mode=IndexingMode.DOCUMENT_PER_CHUNK,
            # The standard chunk fields (content, embedding, identity, metadata) are
            # added automatically. `fields` only declares your extra fields.
            fields=[
                FieldDefinition.TextField(name="title"),
            ],
        )
```

> **Info**
>
> **Application name restrictions:** The name passed to `set_app_name()` must contain only lowercase letters (`a-z`). Numbers, underscores, hyphens, and other special characters are not allowed.

For more details on Vespa application management and deployment, see [Vespa](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa).

## section: deploy-schema
    Quickstart > Deploy from migrations
    cite: https://docs.mistral.ai/studio/search/search-toolkit/quickstart#deploy-schema
## Deploy from migrations {#deploy-schema}

Deploy the schema to your local Vespa instance:

```bash
mistral-vespa migrate \
  --app-dir ./vespa/migrations \
  --config-server http://localhost:19071 \
  --query-port 8080
```

This builds the application package from your migrations in memory, deploys it, and waits until the app is ready.

## section: ingest
    Quickstart > Ingest documents
    cite: https://docs.mistral.ai/studio/search/search-toolkit/quickstart#ingest
## Ingest documents {#ingest}

Create a pipeline that loads files, extracts text, splits into chunks, embeds, and indexes into Vespa:

```python
import asyncio
from pathlib import Path

from mistralai.client import Mistral
from mistralai.search.toolkit.embedding import MistralEmbedder
from mistralai.search.toolkit.ingestion.extractors import PlainTextExtractor
from mistralai.search.toolkit.ingestion.loaders import FilesystemFileLoader
from mistralai.search.toolkit.ingestion.pipelines import Pipeline
from mistralai.search.toolkit.ingestion.text_splitters import CharacterTextSplitter
from mistralai.search.toolkit.plugins.vespa import VespaClientConfig
from vespa_app import app


async def main():
    mistral_client = Mistral(api_key="your-api-key")

    # Configure Vespa
    config = VespaClientConfig(
        endpoint="http://localhost:8080",
    )
    vector_store = app.get_search_index(config, collection_name="quickstart_collection")

    # Create the pipeline
    pipeline = Pipeline(
        loader=FilesystemFileLoader(),
        extractor=PlainTextExtractor(),
        text_splitter=CharacterTextSplitter(chunk_size=500),
        embedder=MistralEmbedder(client=mistral_client, model_name="mistral-embed"),
        stores=vector_store,
    )

    # Ingest documents
    await pipeline.run(documents=[Path("doc1.txt"), Path("doc2.txt")])
    print("Documents ingested!")


asyncio.run(main())
```

The pipeline chains five stages:

1. **`FilesystemFileLoader`** reads raw file bytes from disk.
2. **`PlainTextExtractor`** extracts text content from the file. For PDFs, use `MistralOCRExtractor` instead.
3. **`CharacterTextSplitter`** breaks the text into chunks of 500 characters.
4. **`MistralEmbedder`** generates a vector embedding for each chunk.
5. **`vector_store`** (Vespa) indexes each chunk, storing the embedding for vector search.

## section: search
    Quickstart > Search
    cite: https://docs.mistral.ai/studio/search/search-toolkit/quickstart#search
## Search {#search}

Query the indexed documents using vector search:

```python
import asyncio

from mistralai.client import Mistral
from mistralai.search.toolkit.embedding import MistralEmbedder
from mistralai.search.toolkit.plugins.vespa import VespaClientConfig
from mistralai.search.toolkit.retrieval import QueryEngine
from mistralai.search.toolkit.retrieval.retrievers import VectorRetriever
from vespa_app import app


async def main():
    mistral_client = Mistral(api_key="your-api-key")
    embedder = MistralEmbedder(client=mistral_client, model_name="mistral-embed")

    # Configure Vespa for search
    config = VespaClientConfig(
        endpoint="http://localhost:8080",
    )
    vector_store = app.get_search_index(config, collection_name="quickstart_collection")

    # Build query engine
    query_engine = QueryEngine(
        retriever=[VectorRetriever(client=vector_store, embedder=embedder)],
    )

    # Search
    result = await query_engine.search(
        query="What is RAG?",
        top_k=5,
        include_metadata=True,
        include_content=True,
    )

    for i, r in enumerate(result.results, 1):
        print(f"{i}. [Score: {r.score:.3f}] {r.chunk.content[:200]}...")


asyncio.run(main())
```

## section: pdf-ingestion
    Quickstart > Ingesting PDFs with OCR
    cite: https://docs.mistral.ai/studio/search/search-toolkit/quickstart#pdf-ingestion
## Ingesting PDFs with OCR {#pdf-ingestion}

For PDF documents, swap `PlainTextExtractor` with `MistralOCRExtractor` and use `MarkdownTextSplitter` for structure-aware chunking:

```python
from mistralai.search.toolkit.ingestion.extractors import MistralOCRExtractor
from mistralai.search.toolkit.ingestion.text_splitters import (
    MarkdownTextSplitter,
    MarkdownTextSplitterConfig,
)

pipeline = Pipeline(
    loader=FilesystemFileLoader(),
    extractor=MistralOCRExtractor(client=mistral_client),
    text_splitter=MarkdownTextSplitter(
        MarkdownTextSplitterConfig(chunk_size=5048, chunk_overlap=50)
    ),
    embedder=MistralEmbedder(client=mistral_client),
    stores=vector_store,
)
```

Results: 9 sections, the whole page.
```

### 15. mistral_docs_search

```json
{"q": "", "under": "https://docs.mistral.ai/studio/search", "max_hits": 30}
```

Result:

```
pages under https://docs.mistral.ai/studio/search

- https://docs.mistral.ai/studio/search/agentic-search
    Agentic Search
- https://docs.mistral.ai/studio/search/libraries
    Libraries
- https://docs.mistral.ai/studio/search/search-toolkit
    Search Toolkit
- https://docs.mistral.ai/studio/search/search-toolkit/changelog
    Changelog
- https://docs.mistral.ai/studio/search/search-toolkit/concepts/document-model
    Document model
- https://docs.mistral.ai/studio/search/search-toolkit/concepts/embedding-model
    Embedding model
- https://docs.mistral.ai/studio/search/search-toolkit/ingestion
    Ingestion
- https://docs.mistral.ai/studio/search/search-toolkit/ingestion/embedders
    Embedders
- https://docs.mistral.ai/studio/search/search-toolkit/ingestion/enrichers
    Chunk enrichers
- https://docs.mistral.ai/studio/search/search-toolkit/ingestion/extractors
    Document extractors
- https://docs.mistral.ai/studio/search/search-toolkit/ingestion/loaders
    File loaders
- https://docs.mistral.ai/studio/search/search-toolkit/ingestion/splitters
    Text splitters
- https://docs.mistral.ai/studio/search/search-toolkit/quickstart
    Quickstart
- https://docs.mistral.ai/studio/search/search-toolkit/retrieval
    Retrieval
- https://docs.mistral.ai/studio/search/search-toolkit/retrieval/preprocessing
    Query preprocessing
- https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers
    Rerankers
- https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers
    Retrievers
- https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache
    Semantic cache
- https://docs.mistral.ai/studio/search/search-toolkit/search-index
    Search index
- https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores
    Custom vector stores
- https://docs.mistral.ai/studio/search/search-toolkit/search-index/postgres
    Postgres
- https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa
    Vespa
- https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/anatomy
    Anatomy of a Vespa application
- https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli
    CLI reference
- https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/local-development
    Local development
- https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/migration-helpers
    Migration helpers reference
- https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/migrations
    Manage schema
- https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/operations
    Deploy and operate
- https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/query-profiles
    Manage ranking

Results: 29 pages; a page not listed does not exist at this commit.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/agentic-search") reads the first one.
```

### 16. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/search/search-toolkit/changelog"}
```

Result:

```
page: https://docs.mistral.ai/studio/search/search-toolkit/changelog | "Changelog"

## section: changelog
    Changelog
    cite: https://docs.mistral.ai/studio/search/search-toolkit/changelog
# Changelog

All notable changes to Search Toolkit are documented here.

## section: 0-0-13
    Changelog > 0.0.13
    cite: https://docs.mistral.ai/studio/search/search-toolkit/changelog#0-0-13
## 0.0.13 {#0-0-13}

**Breaking changes**

_Embedding model on the schema_

- [`create_schema()`](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/migration-helpers#creating-schemas) and `create_default_schema()` now take `embedding_model` (an [`EmbeddingModel`](https://docs.mistral.ai/studio/search/search-toolkit/concepts/embedding-model) or [`MistralEmbeddingPreset`](https://docs.mistral.ai/studio/search/search-toolkit/concepts/embedding-model#presets)) instead of `embedding_dimensions: int`. `embedding_dimensions` is deprecated (emits a `DeprecationWarning` and builds a `CustomEmbeddingModel(name="unknown")` under the hood); passing both raises `ValueError`.
- `VespaSchemaDefinition.embedding_dimensions` is replaced by `embedding_model: EmbeddingModel`, threading the full model config (name, dimensions, dtype, distance metric) through the schema layer. [`VespaSearchIndex`](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/anatomy#schemas) now exposes an `embedding_model` property.

**Improvements**

- Added a **[Postgres search backend](https://docs.mistral.ai/studio/search/search-toolkit/search-index/postgres)** (`mistralai-search-toolkit-plugins-postgres`) as a second index alongside Vespa. `PostgresStoreIndex` implements [`VectorStoreIndex`](https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores) (dense and hybrid search), [`NavigableIndex`](https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores#agentic-operations) (`navigate`/`read`/`grep`/`get_chunk`), and [`PatchableIndex`](https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores#partial-updates) (partial updates). A `VectorSearchQuery` that carries both `query` and `embedding` runs BM25 (`pg_textsearch`) and HNSW (`pgvector`) retrieval fused by weighted reciprocal rank fusion; the new `PostgresSearchQuery` tunes `vector_weight` / `text_weight` / `rrf_k`. The `PostgresApp` mirrors the Vespa app's `get_search_index(config, collection)` shape, and collections are declared with `PostgresCollectionSchema(collection_name, document_type, embedding_model)`. Requires the `vector` and `pg_textsearch` extensions provisioned in the target database.
- Added an [`EmbeddingModel`](https://docs.mistral.ai/studio/search/search-toolkit/concepts/embedding-model) abstraction (`embedding/models.py`) as the single source of truth for vector config: `MistralEmbeddingModel` and `CustomEmbeddingModel` (discriminated union via `EmbeddingModel`), the `MistralEmbeddingPreset` enum (`MISTRAL_EMBED_DIM_1024` / `MISTRAL_EMBED_DIM_256` / `MISTRAL_EMBED_DIM_128`) with `build_embedding_model()`, plus [`VectorDType`](https://docs.mistral.ai/studio/search/search-toolkit/concepts/embedding-model#vector-config) (`FLOAT32` / `FLOAT16`), `DistanceMetric` (`COSINE` / `INNER_PRODUCT` / `L2`), and a `VectorConfig` protocol.
- [`SmartPDFExtractor`](https://docs.mistral.ai/studio/search/search-toolkit/ingestion/extractors#smart-pdf-extractor) and [`LegacyOfficeExtractor`](https://docs.mistral.ai/studio/search/search-toolkit/ingestion/extractors#legacy-office-extractor) now accept any [`DocumentExtractor`](https://docs.mistral.ai/studio/search/search-toolkit/ingestion/extractors#creating-custom-extractors) as an OCR delegate instead of requiring `MistralOCRExtractor`, so a deployment with no reachable Mistral API can supply its own engine.
- Added opt-in text-first PDF extraction via `pdf_min_chars_per_page` (`PdfTextFirstExtractor`); off by default. PDFs dispatched to the heuristic leave `.docx`/`.pptx`/`.odt`/`.epub` and image attachments on the OCR route untouched.
- Threaded `exclude_ids` through the retrieval layer: [`QueryEngine`](https://docs.mistral.ai/studio/search/search-toolkit/retrieval#query-engine).search(..., exclude_ids=...) forwards to retrievers and onto the search query. [`CachedQueryEngine`](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache).search forwards it and bypasses the cache when exclusions are set.

**Bugfixes**

- Updated `markdownify` from `>=0.14,<1` to `>=1.0.0,<2` and adapted the [custom converter](https://docs.mistral.ai/studio/search/search-toolkit/ingestion/extractors#html-extractor) to the 1.x API.

## section: 0-0-12
    Changelog > 0.0.12
    cite: https://docs.mistral.ai/studio/search/search-toolkit/changelog#0-0-12
## 0.0.12 {#0-0-12}

**Breaking changes**

_Checkpoint serialization_

- A new `document/serialization.py` module introduces a `DocumentTypeRegistry` and stable type ids so that document classes can be round-tripped through an external service safely.

**Improvements**

- Added `MistralClientConfig` and `build_mistral_client()` to centralize Mistral SDK client creation for whole pipelines.
- Added [`SmartPDFExtractor`](https://docs.mistral.ai/studio/search/search-toolkit/ingestion/extractors#smart-pdf-extractor), which chooses between PyMuPDF and Mistral OCR automatically for PDFs that already have a text layer.
- Added `EmailWithAttachmentsExtractor`, which adds attachment text to the parent email's Markdown under an `## Attachments` section.
- Improved error reporting for ingestion problems.

**Bugfixes**

- Deterministic ingestion failures now fail faster.

**Chores**

- Bumped `mistralai` to `>=2.9.1,<2.10`.
- Bumped `dynaconf` from `>=3.2.11` to `>=3.3.4`.
- Renamed the `mistralai.search.toolkit.embedders` module to `mistralai.search.toolkit.embedding`. A backward-compatible `embedders` shim re-exports public symbols and emits a `DeprecationWarning`. See the [Embedders](https://docs.mistral.ai/studio/search/search-toolkit/ingestion/embedders) page.

## section: 0-0-11
    Changelog > 0.0.11
    cite: https://docs.mistral.ai/studio/search/search-toolkit/changelog#0-0-11
## 0.0.11 {#0-0-11}

**Improvements**

- For ingestion, made extraction checkpoints (saving snapshots between stages, for faster retrying) a backend-agnostic capability. [`Pipeline(checkpoint_store=...)`](https://docs.mistral.ai/studio/search/search-toolkit/ingestion#pipeline) accepts any `ObjectStorage` backend and saves checkpoints between the ingestion stages; `run_file(..., checkpoint_key=...)` loads and saves the extraction result so retries and re-ingestion skip re-extraction.
- Introduced a `DocumentProcessor` protocol for ingestion, unifying [`TextSplitter`](https://docs.mistral.ai/studio/search/search-toolkit/ingestion/splitters), [`Embedder`](https://docs.mistral.ai/studio/search/search-toolkit/ingestion/embedders), and [`ChunkEnricher`](https://docs.mistral.ai/studio/search/search-toolkit/ingestion/enrichers).
- Added map-reduce summarization for long documents: `SummarizeRequestConfig` with `overflow_strategy: OverflowStrategy.MAP_REDUCE` can split a document, summarize the different parts, and merge them into a final summary. See the [Summary Enricher](https://docs.mistral.ai/studio/search/search-toolkit/ingestion/enrichers#summary-enricher).
- Added [OCR v4](https://docs.mistral.ai/studio/search/search-toolkit/ingestion/extractors#mistral-ocr-extractor) features: inline markdown table embedding in page chunks, per-chunk confidence scores, and basic bounding-box support.
- Added a [`PatchableIndex`](https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores#partial-updates) capability with `patch_chunk` and `patch_document` for partial updates on `DOCUMENT_PER_CHUNK` indices, avoiding a full re-index when only metadata changes.
- Added `get_chunk(chunk_id)` to the [`NavigableIndex`](https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores#agentic-operations) protocol.
- Vespa: added `set_default_ranking_weights()` to bake default ranking-feature weights into a schema and its default query profile. See [Manage ranking](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/query-profiles).
- Vespa: added a phase-1 vector `closeness` ranking function for embedding fields, putting vector relevance into candidate selection. See [Ranking profiles](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/anatomy#ranking-profiles).
- Vespa: [`BoolField`](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/anatomy#fields) gained a `fast_search` option.

**Bugfixes**

- Sanitize illegal Unicode code points (lone surrogates) from extracted content.

**Chores**

- Updated `mistralai` bound from `<2.7` to `<2.9`.
- Bumped `pypdf` from 6.13.3 to 6.14.2.
- Bumped `azure-storage-blob` to 12.30.0.

## section: 0-0-10
    Changelog > 0.0.10
    cite: https://docs.mistral.ai/studio/search/search-toolkit/changelog#0-0-10
## 0.0.10 {#0-0-10}

**Improvements**

- Added embeddings batch API support for ingestion: [`MistralEmbedder`](https://docs.mistral.ai/studio/search/search-toolkit/ingestion/embedders#mistral-embedder).`run_batch_embedding_job()` can be used to lower embedding costs for large ingestion jobs.
- Added header-aware token-budgeted chunking for ingestion: new `ParagraphTokenTextSplitter` and `MarkdownTokenTextSplitter` splitters. See the [Text splitters](https://docs.mistral.ai/studio/search/search-toolkit/ingestion/splitters) page.
- Added a [`NavigableIndex`](https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores#agentic-operations) protocol with `navigate`, `read`, and `grep` methods for positional chunk navigation on `DOCUMENT_PER_CHUNK` indices.
- Vespa: added YQL search on `DocumentPerChunkSearchIndex` via `VespaSearchQuery`, with ranking tuning and chunk-id exclusion (`exclude_ids`). See [Manage ranking](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/query-profiles).

**Bugfixes**

- Fixed [`TokenTextSplitter`](https://docs.mistral.ai/studio/search/search-toolkit/ingestion/splitters#token-text-splitter) reporting wrong offsets for repeated content.

**Chores**

- Relaxed the toolkit `mistralai` constraint to `>=2.5.0,<2.7`.

## section: 0-0-9
    Changelog > 0.0.9
    cite: https://docs.mistral.ai/studio/search/search-toolkit/changelog#0-0-9
## 0.0.9 {#0-0-9}

**Breaking changes**

_Document model_

Search Toolkit now uses a unified document model built around `Document` and `DocumentChunk`, with a deterministic identity derived from a `source_id` and a `locator`. See the [Document model](https://docs.mistral.ai/studio/search/search-toolkit/concepts/document-model) page for full details.

- Extractors now produce `DocumentChunk` objects directly; the separate *page* representation has been removed.
- `Document.id` and `DocumentChunk.id` are now computed deterministically from `source_id` (plus `locator` for chunks), making indexing idempotent. The explicit `id` field on `File` and `document_id` on `DocumentChunk` have been removed.
- Added `source_id`, `locator`, `parent_ref`, and `chunk_type` as first-class fields, along with typed, extensible metadata models. The same identity contract is mirrored on `SearchResultChunk`.

_Vespa indexing model_

Vespa now indexes one chunk per document via the new `DOCUMENT_PER_CHUNK` indexing mode, which becomes the recommended model. The previous single-document model is deprecated.

- Added the `DOCUMENT_PER_CHUNK` indexing mode, including default fields, ranking profiles, and the full write, delete, and search paths. See [Anatomy of a Vespa application](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/anatomy#schemas).
- Added an `IndexingMode` to the schema definition with deprecation hooks for migrating existing schemas.
- The index API is split into a base `VespaSearchIndex` and a dedicated `SingleDocumentSearchIndex`; the single-document model is deprecated in favor of `DOCUMENT_PER_CHUNK`.
- The schema `id_field` is deprecated and is no longer allowed for `DOCUMENT_PER_CHUNK` indexes.

_Other_

- Renamed the `indices` module to `search`. Update imports accordingly.

**Improvements**

_Other_

- Renamed the `indices` module to `search`. Update imports accordingly.

**Improvements**

- Added blob-storage `FileLoader` implementations for S3, Azure, and GCS, plus a `storage-s3` extra. See the [File loaders](https://docs.mistral.ai/studio/search/search-toolkit/ingestion/loaders) page.
- Added OCR model literals and constants.
- Vespa: extracted a dedicated `VespaClient` with improved error handling.
- Vespa: added a backend-agnostic services definition, topology v2, and a translator, with automatic v2 topology generation for single-node Docker deployments.
- Vespa: added Vespa-to-Vespa copy and index-to-streaming migration workflows.
- Vespa: emit a metrics consumer in `services.xml`.
- Vespa: warn when rank2 features are configured without rank1, and when ranking weights default to 0.

**Security**

- Updated `langchain-core` to `~=1.4`.

**Bugfixes**

- Vespa: rank by cosine similarity instead of euclidean distance.
- Vespa: fix retrieval of the document count.
- Vespa: thread `distribute_across_groups` into `load_topology_file`.
- Vespa CLI: lazy-import index registration SDK models.
- Treat truncated LLM responses as retryable and enrich `LLMException` / `SummaryGenerationError` for structured logging.
- [OCR extractor](https://docs.mistral.ai/studio/search/search-toolkit/ingestion/extractors#mistral-ocr-extractor): use mimetype metadata for filetype detection.
- Added `text/x-file` and `text/x-script.python` MIME types to the registry.

## section: 0-0-8
    Changelog > 0.0.8
    cite: https://docs.mistral.ai/studio/search/search-toolkit/changelog#0-0-8
## 0.0.8 {#0-0-8}

Initial release of Search Toolkit as a tech preview.

Results: 7 sections, the whole page.
```

### 17. mistral_docs_search

```json
{"q": "mistralai.search.toolkit.evaluation", "max_hits": 10}
```

Result:

```
q: "mistralai.search.toolkit.evaluation"

[1] https://docs.mistral.ai/studio/observability/evaluations | section: offline-evaluations
    Offline evaluations
    The Evaluation SDK (`mistralai-observability`) lets you run offline evaluations on your LLM pipelines in a few lines of Python. Define a dataset, a task, and scorers to get results in your terminal and in Studio. > **Info** > > Offline evaluations are available to **Enterprise-tier organizations** only. Contact your Mistral representative to get access to the `mistralai-observability` package. The …
    cite: https://docs.mistral.ai/studio/observability/evaluations

[2] https://docs.mistral.ai/studio/search/search-toolkit/ingestion/embedders | section: mistral-embedder
    Embedders > Mistral Embedder
    | Constant | Model Name | Dimensions | Matching preset | Best for | |----------|-----------|-----------|-----------------|----------| | `MODEL_1024_EMBEDDING` | `"mistral-embed"` | 1024 | `MistralEmbeddingPreset.MISTRAL_EMBED_DIM_1024` | Default for Search Toolkit pipelines | | `MODEL_256_EMBEDDING` | `"mistral-embed-dim256-2510"` | 256 | `MistralEmbeddingPreset.MISTRAL_EMBED_DIM_256` | Low-latenc …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/ingestion/embedders#mistral-embedder

[3] https://docs.mistral.ai/studio/search/search-toolkit | section: next-steps
    Search Toolkit > Next steps
    - **[Quickstart](https://docs.mistral.ai/studio/search/search-toolkit/quickstart)**: build your first ingestion and retrieval pipeline end to end. - **[Document model](https://docs.mistral.ai/studio/search/search-toolkit/concepts/document-model)**: understand `Document`, `DocumentChunk`, and the identity that ties them together. - **[Embedding model](https://docs.mistral.ai/studio/search/search-to …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#next-steps

[4] https://docs.mistral.ai/resources/deprecated/customization | section: developer-examples/eval-2
    Fine-tuning API (legacy) > Developer Examples > Eval
    Human evaluation by the Content Design team. The objective was simple: A translator from dry, factual, generated language to the playful Tone of Voice of Cleo. For that, we fine-tuned Mistral using Studio on company data crafted and evaluated by the Content Design team. The goal was to lift the writing style that is characteristic of Cleo and its brand. For example a typical message to our users c …
    cite: https://docs.mistral.ai/resources/deprecated/customization#developer-examples:~:text=Human%20evaluation%20by
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/resources/deprecated/customization", section="developer-examples/eval-2") reads this section

[5] https://docs.mistral.ai/resources/deprecated/customization | section: developer-examples/eval
    Fine-tuning API (legacy) > Developer Examples > Eval
    To evaluate our fine-tuned model, we run inference of the test set of our dataset, then use binary classification metrics (Accuracy, Recall, F1 score). We test whether we were able to align the behavior of Mistral 7b to the classification behavior of OpenAI GPT-4-turbo, while maintaining the expected structured output. Indeed, we removed the function calling. ![Performance Metrics](https://docs.mi …
    cite: https://docs.mistral.ai/resources/deprecated/customization#developer-examples:~:text=To%20evaluate%20our
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/resources/deprecated/customization", section="developer-examples/eval") reads this section

[6] https://docs.mistral.ai/studio/search/search-toolkit/retrieval | section: components
    Retrieval > Components
    Each retrieval component is documented in detail with examples and best practices: - **[Retrievers](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers)**: VectorRetriever, KeywordRetriever, and hybrid search patterns - **[Rerankers](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers)**: LLMReRanker, CrossEncoderReRanker, RRF fusion, and custom rerankers …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval#components

[7] https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa | section: installation
    Vespa > Installation
    ```bash uv add "mistralai-search-toolkit[vespa]" ```
    cite: https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa#installation

[8] https://docs.mistral.ai/studio/search/search-toolkit | section: retrieval
    Search Toolkit > Key features > Retrieval
    [Retrieval](https://docs.mistral.ai/studio/search/search-toolkit/retrieval) includes: - **Multiple strategies**: Vector (semantic) search with optional reranking - **Query preprocessing**: Improve user queries with LLM reformulation or query extension - **Reranking**: LLM reranker, cross-encoder reranker, or custom rerankers - **Semantic caching**: Cache results by query similarity to skip redunda …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#retrieval

[9] https://docs.mistral.ai/studio/search/agentic-search | section: next-steps
    Agentic Search > Next steps
    - [Search Toolkit](https://docs.mistral.ai/studio/search/search-toolkit): learn about ingestion pipelines, retrieval strategies, and the full SDK. - [Libraries](https://docs.mistral.ai/studio/search/libraries): use managed document ingestion and search for built-in RAG. - [Connectors](https://docs.mistral.ai/studio/connectors): connect models and agents to external tools and data sources. - [Agent …
    cite: https://docs.mistral.ai/studio/search/agentic-search#next-steps

[10] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers | section: see-also
    Rerankers > See also
    - [Retrieval overview](https://docs.mistral.ai/studio/search/search-toolkit/retrieval): retrieval pipeline architecture - [Retrievers](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers): vector search and custom retrievers - [Query preprocessing](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/preprocessing): improve queries before retrieval
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#see-also

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/observability/evaluations") to read hit 1 on its page
```

### 18. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/observability/evaluations"}
```

Result:

```
page: https://docs.mistral.ai/studio/observability/evaluations | "Offline evaluations"

## section: offline-evaluations
    Offline evaluations
    cite: https://docs.mistral.ai/studio/observability/evaluations
# Offline evaluations

The Evaluation SDK (`mistralai-observability`) lets you run offline evaluations on your LLM pipelines in a few lines of Python. Define a dataset, a task, and scorers to get results in your terminal and in Studio.

> **Info**
>
> Offline evaluations are available to **Enterprise-tier organizations** only. Contact your Mistral representative to get access to the `mistralai-observability` package.

The SDK follows a simple mental model:

```
Dataset  →  Task  →  Evaluators  →  Results
```

- **Dataset**: a list of input records (dicts) with your test cases.
- **Task**: an async or sync function that receives a `TaskContext` and produces an output.
- **Evaluators**: functions that receive a `ScorerContext` and score each output.
- **Results**: statistics and per-record scores, displayed in the terminal and uploaded to Studio.

## section: installation
    Offline evaluations > Installation
    cite: https://docs.mistral.ai/studio/observability/evaluations#installation
## Installation {#installation}

**Prerequisites:** Python 3.12+, [uv](https://docs.astral.sh/uv/), and a Mistral API key.

After you receive your entitlement token from Mistral, configure your credentials:

```bash
export UV_INDEX_CLOUDSMITH_USERNAME=token
export UV_INDEX_CLOUDSMITH_PASSWORD=<your-entitlement-token>
```

Add the package and the Mistral private repository to your `pyproject.toml`:

```toml
[project]
name = "my-eval-project"
version = "0.1.0"
dependencies = ["mistralai-observability"]

[[tool.uv.index]]
name = "cloudsmith"
url = "https://dl.cloudsmith.io/basic/mistral-ai/sdk-distribution/python/simple/"
```

Then install:

```bash
uv sync
```

Set your API key:

```bash
export MISTRAL_API_KEY=<your-api-key>
```

## section: quickstart
    Offline evaluations > Quickstart
    cite: https://docs.mistral.ai/studio/observability/evaluations#quickstart
## Quickstart {#quickstart}

Create an `eval.py` file:

```python
import asyncio
import os

from mistralai.observability import (
    Evaluation, Evaluator, Goal, Mistral, Project, ScorerContext, System, TaskContext,
)

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

dataset = [
    {"sentence": "Hello, how are you?", "groundtruth": "English"},
    {"sentence": "Bonjour, comment ça va?", "groundtruth": "French"},
    {"sentence": "Hola, ¿cómo estás?", "groundtruth": "Spanish"},
]

async def task(ctx: TaskContext) -> str:
    response = await client.chat.complete_async(
        model=str(ctx.system.params["model"]),
        messages=[
            {"role": "system", "content": str(ctx.system.params["system_prompt"])},
            {"role": "user", "content": ctx.input_record["sentence"]},
        ],
    )
    return str(response.choices[0].message.content)

def scorer(ctx: ScorerContext) -> int:
    return 1 if ctx.input_record["groundtruth"].lower() == str(ctx.output).lower() else 0

async def main():
    run = await client.evaluation.run(
        project=Project(name="Language Detection"),
        evaluation=Evaluation(name="Accuracy Eval"),
        system=System(name="mistral-small", params={
            "model": "mistral-small-latest",
            "system_prompt": "What language is this sentence in? Reply with ONLY the language name.",
        }),
        dataset=dataset,
        task=task,
        evaluators=[
            Evaluator(
                name="accuracy",
                description="1 if the detected language matches the groundtruth, 0 otherwise.",
                scorer=scorer,
                goal=Goal.gte(0.8),
            ),
        ],
    )
    run.show(level="records")

asyncio.run(main())
```

Run it:

```bash
uv run eval.py
```

Results are printed in your terminal and uploaded to Studio under **Observability > Evaluate > Evaluations**.

## section: core-concepts
    Offline evaluations > Core concepts
    cite: https://docs.mistral.ai/studio/observability/evaluations#core-concepts
## Core concepts {#core-concepts}

**Task**

A task is an async (or sync) function that receives a `TaskContext` and returns an output. This is the code you want to evaluate:

```python
from mistralai.observability import TaskContext

async def task(ctx: TaskContext) -> str:
    response = await client.chat.complete_async(
        model=str(ctx.system.params["model"]),
        messages=[
            {"role": "system", "content": str(ctx.system.params["system_prompt"])},
            {"role": "user", "content": ctx.input_record["prompt"]},
        ],
    )
    return str(response.choices[0].message.content)
```

The task can return any type: strings, Pydantic models, or dicts. The SDK serializes the output for upload.

`TaskContext` gives you typed access to `ctx.input_record` (the current dataset record), `ctx.system` (the `System` config from `evaluation.run()`), and `ctx.metadata` (run metadata).

**Evaluators**

An evaluator has a name, an optional description, and a scorer function. The scorer receives a `ScorerContext` and returns a score:

```python
from mistralai.observability import Evaluator, Goal, ScorerContext

def accuracy_scorer(ctx: ScorerContext) -> int:
    return 1 if ctx.input_record["expected"].lower() in str(ctx.output).lower() else 0

evaluator = Evaluator(
    name="accuracy",
    description="1 if expected answer appears in the output.",
    scorer=accuracy_scorer,
    goal=Goal.gte(0.8),
)
```

`ScorerContext` gives you `ctx.input_record` (the current dataset record), `ctx.output` (the task output for this generation), and `ctx.system` (the `System` config).

You can stack as many evaluators as you need in a single run. The SDK computes statistics (avg, min, max, std) per evaluator automatically.

**System**

`System` externalizes your task configuration so each run records which settings produced its results:

**System**

`System` externalizes your task configuration so each run records which settings produced its results:

```python
from mistralai.observability import System

system = System(name="mistral-small-t0", params={
    "model": "mistral-small-latest",
    "temperature": 0,
    "system_prompt": "Answer concisely in one sentence.",
})
```

`params` is free-form: include model, temperature, system prompt, max tokens, tool definitions, or any other setting that drives your task.

In Studio, each run shows its `System` config, so you can compare runs side by side.

:::tip Compare configurations
Run the same evaluation with different `System` objects to compare model versions or prompt variants without changing your task code.
:::

**Goals**

Goals let you define pass/fail criteria on evaluator scores. When a goal is set, the SDK displays `PASS` or `FAIL` verdicts in the terminal output:

```python
from mistralai.observability import Goal

Evaluator(
    name="accuracy",
    scorer=accuracy_scorer,
    goal=Goal.gte(0.8),           # each record must score >= 0.8
    aggregate_goal=Goal.gte(0.9), # overall average must be >= 0.9
)
```

| Goal | Meaning |
|------|---------|
| `Goal.gte(0.8)` | Score must be `>= 0.8` |
| `Goal.lte(0.1)` | Score must be `<= 0.1` |
| `Goal.between(0.2, 0.8)` | Score must be in [0.2, 0.8] |
| `Goal.higher_is_better()` | Direction hint only, no threshold |
| `Goal.lower_is_better()` | Direction hint only, no threshold |

## section: organizing-in-studio
    Offline evaluations > Organizing runs in Studio
    cite: https://docs.mistral.ai/studio/observability/evaluations#organizing-in-studio
## Organizing runs in Studio {#organizing-in-studio}

Use **Projects** and **Evaluations** to organize runs:

- **Project**: groups related evaluations for a system (for example, `"Language Detection"`).
- **Evaluation**: a specific evaluation within a project (for example, `"Accuracy Eval"`).
- **Run**: each call to `evaluation.run()` creates a new run under the evaluation.

```python
run = await client.evaluation.run(
    project=Project(name="My Project"),       # created if it doesn't exist
    evaluation=Evaluation(name="My Eval"),    # created if it doesn't exist
    dataset=dataset,
    task=task,
    evaluators=[...],
)
```

You can also reference existing entities by slug:

```python
project=Project(slug="my-project")
evaluation=Evaluation(slug="my-eval")
```

Tags and metadata help you filter and compare runs in Studio:

```python
run = await client.evaluation.run(
    ...
    tags=["model:mistral-small", "prompt:v2"],
    metadata={"commit": "abc123"},
)
```

## section: local-mode
    Offline evaluations > Local mode
    cite: https://docs.mistral.ai/studio/observability/evaluations#local-mode
## Local mode {#local-mode}

Use `local=True` to run evaluations without uploading results to Studio. This is useful for fast iteration during development:

```python
run = await client.evaluation.run(
    dataset=dataset,
    task=task,
    evaluators=[Evaluator(name="accuracy", scorer=scorer)],
    local=True,  # no upload, no project/evaluation required
)
run.show(level="records")
```

A typical development workflow:

1. **Iterate locally**: set `local=True` and adjust your task and scorers until results look right.
2. **Push to Studio**: remove `local=True` and add `project` and `evaluation` to track results over time.

## section: displaying-results
    Offline evaluations > Displaying results
    cite: https://docs.mistral.ai/studio/observability/evaluations#displaying-results
## Displaying results {#displaying-results}

The `run.show()` method prints results at different levels of detail:

```python
run.show(level="run")          # Summary statistics only
run.show(level="records")      # Per-record results
run.show(level="generations")  # Per-generation details
run.show(level="scores")       # Full score breakdown
```

Export as JSON for further processing:

```python
run.show(mode="json", level="records")
```

## section: results-in-studio
    Offline evaluations > Results in Studio
    cite: https://docs.mistral.ai/studio/observability/evaluations#results-in-studio
## Results in Studio {#results-in-studio}

Once a run completes, results are available at **Observability > Evaluate > Evaluations** in Studio. Each run uploads its scores, statistics, and metadata automatically.

The Studio UI gives you four ways to explore results:

- **Trend charts**: score averages over time with min/max bands, so you can spot regressions across runs.
- **Distribution charts**: pie and stacked area charts showing score distribution across records and runs.
- **Composable filters**: filter by tag, run ID, or metric threshold to isolate specific subsets.
- **Run detail view**: open any run to inspect per-record inputs, outputs, and scores — with expandable generation details when `num_generations > 1`.

Cell values render automatically based on type: plain text, JSON objects, and LLM conversation arrays each get their own display format.

## section: guides
    Offline evaluations > Guides
    cite: https://docs.mistral.ai/studio/observability/evaluations#guides
## Guides {#guides}

- [Judges](https://docs.mistral.ai/studio/observability/evaluations/judges): use LLM-based scorers for criteria that rule-based functions can't capture.
- [Datasets](https://docs.mistral.ai/studio/observability/evaluations/datasets): structure your test cases as typed Python records.
- [Use context objects](https://docs.mistral.ai/studio/observability/evaluations/context-objects): `TaskContext`, `ScorerContext`, and `RunEvaluatorContext` reference.
- [Set goals](https://docs.mistral.ai/studio/observability/evaluations/goals): define pass/fail thresholds and direction hints on evaluator scores.
- [Configure system params](https://docs.mistral.ai/studio/observability/evaluations/system-params): externalize task configuration for side-by-side comparison in Studio.
- [Combine evaluators](https://docs.mistral.ai/studio/observability/evaluations/multiple-evaluators): combine rule-based and LLM-based scorers in a single run.
- [Use run-level evaluators](https://docs.mistral.ai/studio/observability/evaluations/run-evaluators): aggregate metrics (F1, custom gates) computed after all records are scored.
- [Iterate locally](https://docs.mistral.ai/studio/observability/evaluations/local-mode): iterate without uploading results to Studio.
- [Reduce variance with multiple generations](https://docs.mistral.ai/studio/observability/evaluations/num-generations): reduce variance by running each record N times.
- [Retry failed records](https://docs.mistral.ai/studio/observability/evaluations/retry-failed-records): rerun only the records that errored, patch results in place.

## section: what-python-version-is-required
    Offline evaluations > FAQ > What Python version is required?
    cite: https://docs.mistral.ai/studio/observability/evaluations#what-python-version-is-required
### What Python version is required? {#what-python-version-is-required}

Python 3.12 or later is required. The package uses `uv` for dependency management.

## section: can-i-use-synchronous-functions-for-tasks-and-scorers
    Offline evaluations > FAQ > Can I use synchronous functions for tasks and scorers?
    cite: https://docs.mistral.ai/studio/observability/evaluations#can-i-use-synchronous-functions-for-tasks-and-scorers
### Can I use synchronous functions for tasks and scorers? {#can-i-use-synchronous-functions-for-tasks-and-scorers}

Yes. Both async and sync functions work for tasks and scorers. The SDK detects which style you're using automatically.

## section: how-do-i-use-an-llm-as-a-judge
    Offline evaluations > FAQ > How do I use an LLM as a judge?
    cite: https://docs.mistral.ai/studio/observability/evaluations#how-do-i-use-an-llm-as-a-judge
### How do I use an LLM as a judge? {#how-do-i-use-an-llm-as-a-judge}

An evaluator is a function: call the Mistral API inside your scorer and return a numeric score. See [Judges](https://docs.mistral.ai/studio/observability/evaluations/judges) for detailed examples including structured output and variance reduction.

## section: can-i-run-multiple-evaluators-in-a-single-run
    Offline evaluations > FAQ > Can I run multiple evaluators in a single run?
    cite: https://docs.mistral.ai/studio/observability/evaluations#can-i-run-multiple-evaluators-in-a-single-run
### Can I run multiple evaluators in a single run? {#can-i-run-multiple-evaluators-in-a-single-run}

Yes. Pass a list to `evaluators`. The SDK runs all of them and computes statistics independently per evaluator. See [Combine evaluators](https://docs.mistral.ai/studio/observability/evaluations/multiple-evaluators) for details.

## section: how-do-i-compare-two-model-versions
    Offline evaluations > FAQ > How do I compare two model versions?
    cite: https://docs.mistral.ai/studio/observability/evaluations#how-do-i-compare-two-model-versions
### How do I compare two model versions? {#how-do-i-compare-two-model-versions}

Run the same evaluation twice, each time with a different `System` object. Studio displays the runs side by side with their system configs. See [Configure system params](https://docs.mistral.ai/studio/observability/evaluations/system-params) for details.

Results: 14 sections, the whole page.
```

### 19. mistral_docs_search

```json
{"q": "Search Toolkit testing benchmark quality", "max_hits": 10}
```

Result:

```
q: "Search Toolkit testing benchmark quality"

[1] https://docs.mistral.ai/studio/search/search-toolkit | section: search-toolkit
    Search Toolkit
    Search Toolkit is a Python framework for building information retrieval (IR) systems. It provides components for ingestion, retrieval, and evaluation. It works across backends, and every component can be swapped. LLMs are not trained on your private data. To ground their answers in your documents you need a retrieval pipeline that ingests, indexes, and searches your content. Search Toolkit gives y …
    cite: https://docs.mistral.ai/studio/search/search-toolkit

[2] https://docs.mistral.ai/studio/search/search-toolkit | section: next-steps
    Search Toolkit > Next steps
    - **[Quickstart](https://docs.mistral.ai/studio/search/search-toolkit/quickstart)**: build your first ingestion and retrieval pipeline end to end. - **[Document model](https://docs.mistral.ai/studio/search/search-toolkit/concepts/document-model)**: understand `Document`, `DocumentChunk`, and the identity that ties them together. - **[Embedding model](https://docs.mistral.ai/studio/search/search-to …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#next-steps

[3] https://docs.mistral.ai/studio/search/search-toolkit | section: retrieval
    Search Toolkit > Key features > Retrieval
    [Retrieval](https://docs.mistral.ai/studio/search/search-toolkit/retrieval) includes: - **Multiple strategies**: Vector (semantic) search with optional reranking - **Query preprocessing**: Improve user queries with LLM reformulation or query extension - **Reranking**: LLM reranker, cross-encoder reranker, or custom rerankers - **Semantic caching**: Cache results by query similarity to skip redunda …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#retrieval

[4] https://docs.mistral.ai/studio/search/search-toolkit | section: packages
    Search Toolkit > Installation and extras
    Install the core package: ```bash uv add mistralai-search-toolkit ``` Optional extras add specialized functionality: | Extra | Description | |-------|-------------| | `vespa` | Vespa plugin for vector storage and semantic search | | `extractor-pymupdf` | Advanced PDF extraction with PyMuPDF Pro | | `extractor-spreadsheet` | Spreadsheet parsing (Excel, CSV, Calamine format) | | `extractor-email` | …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#packages

[5] https://docs.mistral.ai/studio/search/search-toolkit | section: ingestion
    Search Toolkit > Key features > Ingestion
    [Ingestion](https://docs.mistral.ai/studio/search/search-toolkit/ingestion) includes: - **Multi-format extraction**: PDF/DOCX/PPTX via Mistral OCR, HTML, spreadsheets, emails, plain text - **File loading**: Load from the local filesystem or implement custom loaders for any source - **Flexible chunking**: Character, token, markdown-aware, or separator-based splitting - **Enrichment**: Enrich docume …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#ingestion

[6] https://docs.mistral.ai/studio/search/search-toolkit | section: components
    Search Toolkit > Architecture > Components
    | Component | Built-in options | |-----------|-----------------| | **File loaders** | `FilesystemFileLoader`, custom loaders | | **Extractors** | `MistralOCRExtractor`, `SmartPDFExtractor`, `PlainTextExtractor`, `PyMuPDFExtractor`, `HTMLExtractor`, `SpreadsheetExtractor`, `EmailExtractor`, `EmailWithAttachmentsExtractor`, `NumbersExtractor`, `LegacyOfficeExtractor`, `MistralAudioTranscriptionExtra …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#components

[7] https://docs.mistral.ai/studio/search/search-toolkit | section: architecture
    Search Toolkit > Architecture
    **Ingestion** transforms raw documents into searchable chunks. A `FileLoader` reads raw bytes from a source, a `DocumentExtractor` converts them into a structured document, a `TextSplitter` divides it into chunks, optional `DocumentProcessor` stages (such as a `ChunkEnricher` or `SummaryEnricher`) add metadata, and an `Embedder` produces vectors for indexing into a vector store. **Retrieval** find …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#architecture

[8] https://docs.mistral.ai/studio/search/agentic-search | section: sdk-patterns
    Agentic Search > Use Agentic Search with the SDK > Core SDK patterns
    **Hybrid retrieval** Run multiple retrievers with different query profiles, then fuse the results with `RRFRanker` (Reciprocal Rank Fusion). This combines dense and hybrid retrieval for better coverage. ```python from mistralai.search.toolkit.retrieval.rerankers import RRFRanker dense_store = get_index("exampledocs", query_profile="dense") hybrid_store = get_index("exampledocs", query_profile="hyb …
    cite: https://docs.mistral.ai/studio/search/agentic-search#sdk-patterns:~:text=Hybrid%20retrieval%20Run

[9] https://docs.mistral.ai/studio/search/search-toolkit/retrieval | section: components
    Retrieval > Components
    Each retrieval component is documented in detail with examples and best practices: - **[Retrievers](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers)**: VectorRetriever, KeywordRetriever, and hybrid search patterns - **[Rerankers](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers)**: LLMReRanker, CrossEncoderReRanker, RRF fusion, and custom rerankers …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval#components

[10] https://docs.mistral.ai/studio/search/agentic-search | section: latency
    Agentic Search > Latency and tradeoffs
    Each tool call has a cost, but navigation can reduce end-to-end latency and token usage because the model converges faster. Instead of repeatedly issuing broad searches, the agent can stay inside the right source, use `grep` to jump to specific terms, and use `exclude_ids` to avoid revisiting the same chunks. In the Agentic Search benchmarks cited in the Search Toolkit launch materials, the full a …
    cite: https://docs.mistral.ai/studio/search/agentic-search#latency

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit") to read hit 1 on its page
```

## Answer

Based on the current Mistral documentation, the **Search Toolkit** explicitly states that it provides components for **ingestion, retrieval, and evaluation** as part of its Python framework for building information retrieval (IR) systems.

However, after thoroughly searching the Search Toolkit documentation, I could not find a dedicated page or detailed section outlining the specific **evaluation features** it provides. The documentation mentions evaluation as a core component, but does not elaborate on its capabilities, metrics, or implementation details in the pages I reviewed.

### What I Found:
- The [Search Toolkit overview](https://docs.mistral.ai/studio/search/search-toolkit) confirms that evaluation is one of its three main components (ingestion, retrieval, evaluation).
- The [Semantic Cache](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache) includes **monitoring metrics** (e.g., `CacheMetrics` for tracking hit rate, similarity, latency, and errors), which can be used for performance evaluation of the cache layer.
- Mistral offers a separate **[Evaluation SDK (`mistralai-observability`)](https://docs.mistral.ai/studio/observability/evaluations)** for offline evaluations of LLM pipelines, but this is a distinct package (Enterprise-tier only) and not part of Search Toolkit itself.

### Conclusion:
The Search Toolkit documentation does not currently provide explicit details on its evaluation features beyond the high-level mention. If you need **retrieval-specific evaluation metrics** (e.g., precision, recall, NDCG, MRR), these are not documented in the available Search Toolkit pages at this time.

For offline evaluation of LLM pipelines (including RAG), you may need to use the separate [Evaluation SDK](https://docs.mistral.ai/studio/observability/evaluations).

