# Mistral Work session, 2026-09-11 14:59, the same question after the stop rules

Exported from Work (Vibe) and reduced to the conversation, as `transcript.md`.
The deployed server had carried the two stop rules of D-044a and the listing
form of D-044b since 14:51.

---

What are the main features in the new mistral search toolkit? Search the docs

2:59pm

Used Mistral Docs Ca30 · Used a tool

Thought for 1s
The user wants to know about the main features of the new Mistral Search Toolkit and specifically asks me to search the docs. This is a request for information from Mistral's documentation.
I should use the mistral-docs skill to properly search and retrieve the relevant documentation. Let me load that skill first.

Read mistral-docs

Thought for 1s
The user is asking about the main features in the new Mistral Search Toolkit and wants me to search the docs. I need to use the mistral-docs connector to search for information about this.
Let me search for "mistral search toolkit" or similar terms in the Mistral documentation.

Found relevant tools

Thought for 2s
The user wants to know about the main features in the new Mistral Search Toolkit. I need to search the Mistral documentation for this information.
Let me use the mistral_docs_search tool to find relevant documentation about the Mistral Search Toolkit.
Let me try again without the limit parameter, as it seems to not be accepted.

Mistral Docs Ca30 • Mistral Docs Search
Arguments

q
"search toolkit features"

Response

result
q: "search toolkit features"

[1] https://docs.mistral.ai/studio/search/search-toolkit#retrieval
    Search Toolkit > Key features > Retrieval
    [Retrieval](https://docs.mistral.ai/studio/search/search-toolkit/retrieval) includes: - **Multiple strategies**: Vector (semantic) search with optional reranking - **Query preprocessing**: Improve user queries with LLM reformulation or query extension - **Reranking**: LLM reranker, cross-encoder reranker, or custom rerankers - **Semantic caching**: Cache results by query similarity to skip redunda …

[2] https://docs.mistral.ai/studio/search/search-toolkit#ingestion
    Search Toolkit > Key features > Ingestion
    [Ingestion](https://docs.mistral.ai/studio/search/search-toolkit/ingestion) includes: - **Multi-format extraction**: PDF/DOCX/PPTX via Mistral OCR, HTML, spreadsheets, emails, plain text - **File loading**: Load from the local filesystem or implement custom loaders for any source - **Flexible chunking**: Character, token, markdown-aware, or separator-based splitting - **Enrichment**: Enrich docume …

[3] https://docs.mistral.ai/studio/search/search-toolkit
    Search Toolkit
    Search Toolkit is a Python framework for building information retrieval (IR) systems. It provides components for ingestion, retrieval, and evaluation. It works across backends, and every component can be swapped. LLMs are not trained on your private data. To ground their answers in your documents you need a retrieval pipeline that ingests, indexes, and searches your content. Search Toolkit gives y …

[4] https://docs.mistral.ai/studio/search/search-toolkit#next-steps
    Search Toolkit > Next steps
    - **[Quickstart](https://docs.mistral.ai/studio/search/search-toolkit/quickstart)**: build your first ingestion and retrieval pipeline end to end. - **[Document model](https://docs.mistral.ai/studio/search/search-toolkit/concepts/document-model)**: understand `Document`, `DocumentChunk`, and the identity that ties them together. - **[Embedding model](https://docs.mistral.ai/studio/search/search-to …

[5] https://docs.mistral.ai/studio/search/search-toolkit#packages
    Search Toolkit > Installation and extras
    Install the core package: ```bash uv add mistralai-search-toolkit ``` Optional extras add specialized functionality: | Extra | Description | |-------|-------------| | `vespa` | Vespa plugin for vector storage and semantic search | | `extractor-pymupdf` | Advanced PDF extraction with PyMuPDF Pro | | `extractor-spreadsheet` | Spreadsheet parsing (Excel, CSV, Calamine format) | | `extractor-email` | …

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit") to read hit 1 on its page

Thought
Good, I found some results. Let me read the main Search Toolkit page to get a comprehensive overview of its features.

Mistral Docs Ca30 • Mistral Docs Read Page
Arguments

page_url
"https://docs.mistral.ai/studio/search/search-toolkit"

Response

result
page: https://docs.mistral.ai/studio/search/search-toolkit | "Search Toolkit"

## https://docs.mistral.ai/studio/search/search-toolkit
    Search Toolkit
# Search Toolkit

Search Toolkit is a Python framework for building information retrieval (IR) systems. It provides components for ingestion, retrieval, and evaluation. It works across backends, and every component can be swapped.

LLMs are not trained on your private data. To ground their answers in your documents you need a retrieval pipeline that ingests, indexes, and searches your content. Search Toolkit gives you every building block to assemble that pipeline.

## https://docs.mistral.ai/studio/search/search-toolkit#ingestion
    Search Toolkit > Key features > Ingestion
### Ingestion {#ingestion}

[Ingestion](https://docs.mistral.ai/studio/search/search-toolkit/ingestion) includes:

- **Multi-format extraction**: PDF/DOCX/PPTX via Mistral OCR, HTML, spreadsheets, emails, plain text
- **File loading**: Load from the local filesystem or implement custom loaders for any source
- **Flexible chunking**: Character, token, markdown-aware, or separator-based splitting
- **Enrichment**: Enrich documents and chunks with custom metadata or LLM-generated summaries
- **Indexing**: Index to vector stores for semantic search

## https://docs.mistral.ai/studio/search/search-toolkit#retrieval
    Search Toolkit > Key features > Retrieval
### Retrieval {#retrieval}

[Retrieval](https://docs.mistral.ai/studio/search/search-toolkit/retrieval) includes:

- **Multiple strategies**: Vector (semantic) search with optional reranking
- **Query preprocessing**: Improve user queries with LLM reformulation or query extension
- **Reranking**: LLM reranker, cross-encoder reranker, or custom rerankers
- **Semantic caching**: Cache results by query similarity to skip redundant retrieval

## https://docs.mistral.ai/studio/search/search-toolkit#architecture
    Search Toolkit > Architecture
## Architecture {#architecture}

**Ingestion** transforms raw documents into searchable chunks. A `FileLoader` reads raw bytes from a source, a `DocumentExtractor` converts them into a structured document, a `TextSplitter` divides it into chunks, optional `DocumentProcessor` stages (such as a `ChunkEnricher` or `SummaryEnricher`) add metadata, and an `Embedder` produces vectors for indexing into a vector store.

**Retrieval** finds relevant chunks for a given query. An optional query preprocessor rewrites or expands the query, a `Retriever` searches the vector index, and an optional `Reranker` re-scores the results before returning them.

Both workflows are orchestrated by high-level classes (`Pipeline` for ingestion, `QueryEngine` for retrieval) that handle component wiring and execution. Every component can be swapped: use the built-in implementations or bring your own.

## https://docs.mistral.ai/studio/search/search-toolkit#components
    Search Toolkit > Architecture > Components
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

## https://docs.mistral.ai/studio/search/search-toolkit#packages
    Search Toolkit > Installation and extras
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

## https://docs.mistral.ai/studio/search/search-toolkit#next-steps
    Search Toolkit > Next steps
## Next steps {#next-steps}

- **[Quickstart](https://docs.mistral.ai/studio/search/search-toolkit/quickstart)**: build your first ingestion and retrieval pipeline end to end.
- **[Document model](https://docs.mistral.ai/studio/search/search-toolkit/concepts/document-model)**: understand `Document`, `DocumentChunk`, and the identity that ties them together.
- **[Embedding model](https://docs.mistral.ai/studio/search/search-toolkit/concepts/embedding-model)**: understand how the schema describes embedding vectors, separately from the embedder.
- **[Search index](https://docs.mistral.ai/studio/search/search-toolkit/search-index)**: set up your vector store.
- **[Ingestion](https://docs.mistral.ai/studio/search/search-toolkit/ingestion)**: load, extract, chunk, enrich, and index your documents.
- **[Retrieval](https://docs.mistral.ai/studio/search/search-toolkit/retrieval)**: configure vector search with optional reranking.

Results: 7 sections, the whole page.

Thought
Great! I now have comprehensive information about the Mistral Search Toolkit. Let me also check if there are any other relevant pages that might contain additional features or details. Let me search for more specific information about the toolkit.

Mistral Docs Ca30 • Mistral Docs Search
Arguments

q
"search toolkit evaluation"

Response

result
q: "search toolkit evaluation"

[1] https://docs.mistral.ai/studio/search/search-toolkit
    Search Toolkit
    Search Toolkit is a Python framework for building information retrieval (IR) systems. It provides components for ingestion, retrieval, and evaluation. It works across backends, and every component can be swapped. LLMs are not trained on your private data. To ground their answers in your documents you need a retrieval pipeline that ingests, indexes, and searches your content. Search Toolkit gives y …

[2] https://docs.mistral.ai/studio/search/search-toolkit#next-steps
    Search Toolkit > Next steps
    - **[Quickstart](https://docs.mistral.ai/studio/search/search-toolkit/quickstart)**: build your first ingestion and retrieval pipeline end to end. - **[Document model](https://docs.mistral.ai/studio/search/search-toolkit/concepts/document-model)**: understand `Document`, `DocumentChunk`, and the identity that ties them together. - **[Embedding model](https://docs.mistral.ai/studio/search/search-to …

[3] https://docs.mistral.ai/studio/search/search-toolkit#packages
    Search Toolkit > Installation and extras
    Install the core package: ```bash uv add mistralai-search-toolkit ``` Optional extras add specialized functionality: | Extra | Description | |-------|-------------| | `vespa` | Vespa plugin for vector storage and semantic search | | `extractor-pymupdf` | Advanced PDF extraction with PyMuPDF Pro | | `extractor-spreadsheet` | Spreadsheet parsing (Excel, CSV, Calamine format) | | `extractor-email` | …

[4] https://docs.mistral.ai/studio/search/search-toolkit#retrieval
    Search Toolkit > Key features > Retrieval
    [Retrieval](https://docs.mistral.ai/studio/search/search-toolkit/retrieval) includes: - **Multiple strategies**: Vector (semantic) search with optional reranking - **Query preprocessing**: Improve user queries with LLM reformulation or query extension - **Reranking**: LLM reranker, cross-encoder reranker, or custom rerankers - **Semantic caching**: Cache results by query similarity to skip redunda …

[5] https://docs.mistral.ai/studio/search/search-toolkit#ingestion
    Search Toolkit > Key features > Ingestion
    [Ingestion](https://docs.mistral.ai/studio/search/search-toolkit/ingestion) includes: - **Multi-format extraction**: PDF/DOCX/PPTX via Mistral OCR, HTML, spreadsheets, emails, plain text - **File loading**: Load from the local filesystem or implement custom loaders for any source - **Flexible chunking**: Character, token, markdown-aware, or separator-based splitting - **Enrichment**: Enrich docume …

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit") to read hit 1 on its page

Thought for 1s
I have enough information now. Let me compile a comprehensive answer about the main features of the Mistral Search Toolkit based on the documentation I've retrieved.
From the documentation, I can see that the Search Toolkit is a Python framework for building information retrieval (IR) systems with three main areas: Ingestion, Retrieval, and Evaluation. The documentation also mentions Architecture and Components.
Let me structure the answer clearly with the main features organized by category.

The Mistral Search Toolkit is a Python framework for building modular information retrieval (IR) systems. Here are its main features, organized by capability:
📥 Ingestion
Multi-format extraction: PDF/DOCX/PPTX (via Mistral OCR), HTML, spreadsheets, emails, plain text
File loading: Local filesystem or custom loaders for any source
Flexible chunking: Character, token, markdown-aware, or separator-based splitting
Enrichment: Add custom metadata or LLM-generated summaries to documents/chunks
Indexing: Vector store indexing for semantic search
Ingestion
🔍 Retrieval
Multiple search strategies: Vector (semantic) search with optional reranking
Query preprocessing: LLM reformulation or query extension to improve user queries
Reranking: LLM reranker, cross-encoder reranker, or custom rerankers
Semantic caching: Cache results by query similarity to skip redundant retrieval
Retrieval
⚙️ Architecture & Components
Every component is swappable—use built-ins or bring your own:
Category

Built-in Options

File loaders

FilesystemFileLoader, custom loaders

Extractors

Mistral OCR, SmartPDF, PyMuPDF, HTML, Spreadsheet, Email, Legacy Office, Audio Transcription

Text splitters

Character, Token, Markdown-aware, Paragraph, Separator-based

Enrichers

Summary, custom Chunk/Document enrichers

Embedders

MistralEmbedder, custom embedders

Storage

Vespa, Postgres (pgvector), or custom vector stores

Retrievers

VectorRetriever, KeywordRetriever

Rerankers

LLM, Cross-Encoder, RRF

Preprocessing

LLM Query Rewriter, Query Extension

Caching

SemanticCache with in-memory backend

Components
📦 Installation & Extras
Core: uv add mistralai-search-toolkit
Optional extras: Vespa, PyMuPDF, spreadsheet/email parsers, HTML→Markdown, LangChain splitters, cloud storage (GCS/Azure/S3), language detection
Requires Python 3.12+
Packages
🎯 Key Design Principles
Backend-agnostic: Works across vector stores and databases
Modular: Swap any component (extractors, embedders, retrievers, etc.)
Private by design: LLMs are not trained on your data; retrieval grounds answers in your documents
Orchestrated workflows: Pipeline (ingestion) and QueryEngine (retrieval) handle component wiring
Search Toolkit overview
