# mined2-084 (unanswerable)

## Question

What evaluation features does the Search Toolkit provide?

## Thinking

The user is asking about evaluation features of the Search Toolkit. This is a specific question about Mistral's documentation. I need to search for information about the Search Toolkit and its evaluation capabilities. I'll use the mistral_docs_search tool with a query that captures this.

The initial search returned some results but they seem incomplete. The snippet shows the Search Toolkit page but doesn't explicitly mention evaluation features. I need to read the full page to find details about evaluation. Let me fetch the complete page content.

The page content mentions evaluation as one of the components but doesn't provide specific details. I need to search more specifically for evaluation features within the Search Toolkit documentation. Let me try a more targeted search query.

The search results are still not giving me the specific evaluation features. I notice there's a dedicated evaluation page in the documentation. Let me try to access that directly to get comprehensive information about evaluation features.

I'm still getting the same search results. Let me try a different approach - searching for pages under the search-toolkit directory to find the evaluation page.

I can see there's a search-index page but no explicit evaluation page in the listing. Let me try searching for "evaluation" specifically within the search-toolkit directory to see if there's a dedicated page.

The search didn't find an evaluation page under search-toolkit. Let me try a broader search for "evaluation" across the entire documentation to see if there's a page I'm missing.

The broader search shows evaluation-related content but it's about observability spans, not the Search Toolkit. Let me try one more targeted search specifically for "Search Toolkit evaluation features" to see if I can find the right information.

After multiple searches, I haven't found a dedicated evaluation page for the Search Toolkit, but the main page mentions that evaluation is a component. Based on the information I've gathered from the documentation, I can now synthesize an answer. The Search Toolkit provides evaluation capabilities as part of its framework for building IR systems. While the exact features aren't explicitly detailed in the snippets, I can infer from the context and typical IR evaluation practices what features it likely includes. I should provide a comprehensive answer based on what I found and mention that evaluation is a core component. I need to structure this clearly and include the citation to the main Search Toolkit page.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "Search Toolkit evaluation features"}
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

### 2. mistral_docs_read_page

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

### 3. mistral_docs_search

```json
{"q": "Search Toolkit evaluation"}
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

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit") to read hit 1 on its page
```

### 4. mistral_docs_search

```json
{"q": "Search Toolkit evaluation page"}
```

Result:

```
q: "Search Toolkit evaluation page"

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

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit") to read hit 1 on its page
```

### 5. mistral_docs_search

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

### 6. mistral_docs_search

```json
{"q": "evaluation", "under": "https://docs.mistral.ai/studio/search/search-toolkit"}
```

Result:

```
q: "evaluation" | under: https://docs.mistral.ai/studio/search/search-toolkit

Results: no section under https://docs.mistral.ai/studio/search/search-toolkit matched; 27 pages exist there.
next: mistral_docs_search(under="https://docs.mistral.ai/studio/search/search-toolkit") lists them; a page not listed does not exist at this commit.
```

### 7. mistral_docs_search

```json
{"q": "evaluation"}
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

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/api/endpoint/beta/observability/spans") to read hit 1 on its page
```

### 8. mistral_docs_search

```json
{"q": "Search Toolkit evaluation features metrics"}
```

Result:

```
q: "Search Toolkit evaluation features metrics"

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

## Answer

The **Search Toolkit** explicitly includes **evaluation** as one of its core components, alongside ingestion and retrieval. However, the current documentation does not provide a dedicated page or detailed breakdown of the specific evaluation features or metrics (e.g., precision, recall, nDCG) it supports.

The only confirmed information is that evaluation is part of the framework:
> *"Search Toolkit is a Python framework for building information retrieval (IR) systems. It provides components for ingestion, retrieval, and **evaluation**."*
[Search Toolkit](https://docs.mistral.ai/studio/search/search-toolkit)

If you need granular details about evaluation metrics or tools (e.g., benchmarks, custom evaluators), the documentation does not currently cover them. You may need to refer to the source code or additional resources.

