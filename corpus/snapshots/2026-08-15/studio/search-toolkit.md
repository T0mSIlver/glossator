---
url: https://docs.mistral.ai/studio/search-toolkit
title: Search Toolkit
breadcrumbs: [Studio]
kind: doc
locale: en
source_path: src/content/en/docs/studio/search-toolkit/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
---

# Search Toolkit

Search Toolkit is a Python framework for building information retrieval (IR) systems. It provides components for ingestion, retrieval, and evaluation. It works across backends, and every component can be swapped.

LLMs are not trained on your private data. To ground their answers in your documents you need a retrieval pipeline that ingests, indexes, and searches your content. Search Toolkit gives you every building block to assemble that pipeline.

## Key features {#key-features}

### Ingestion {#ingestion}

[Ingestion](https://docs.mistral.ai/studio/search-toolkit/ingestion) includes:

- **Multi-format extraction**: PDF/DOCX/PPTX via Mistral OCR, HTML, spreadsheets, emails, plain text
- **File loading**: Load from the local filesystem or implement custom loaders for any source
- **Flexible chunking**: Character, token, markdown-aware, or separator-based splitting
- **Enrichment**: Enrich documents and chunks with custom metadata or LLM-generated summaries
- **Indexing**: Index to vector stores for semantic search

### Retrieval {#retrieval}

[Retrieval](https://docs.mistral.ai/studio/search-toolkit/retrieval) includes:

- **Multiple strategies**: Vector (semantic) search with optional reranking
- **Query preprocessing**: Improve user queries with LLM reformulation or query extension
- **Reranking**: LLM reranker, cross-encoder reranker, or custom rerankers
- **Semantic caching**: Cache results by query similarity to skip redundant retrieval

## Architecture {#architecture}

**Ingestion** transforms raw documents into searchable chunks. A `FileLoader` reads raw bytes from a source, a `DocumentExtractor` converts them into a structured document, a `TextSplitter` divides it into chunks, an optional `ChunkEnricher` adds metadata, and an `Embedder` produces vectors for indexing into a vector store.

**Retrieval** finds relevant chunks for a given query. An optional query preprocessor rewrites or expands the query, a `Retriever` searches the vector index, and an optional `Reranker` re-scores the results before returning them.

Both workflows are orchestrated by high-level classes (`Pipeline` for ingestion, `QueryEngine` for retrieval) that handle component wiring and execution. Every component can be swapped: use the built-in implementations or bring your own.

### Components {#components}

| Component | Built-in options |
|-----------|-----------------|
| **File loaders** | `FilesystemFileLoader`, custom loaders |
| **Extractors** | `MistralOCRExtractor`, `PlainTextExtractor`, `HTMLExtractor`, `SpreadsheetExtractor`, `EmailExtractor`, `NumbersExtractor`, `LegacyOfficeExtractor` |
| **Text splitters** | `CharacterTextSplitter`, `TokenTextSplitter`, `MarkdownTextSplitter`, `SeparatorTextSplitter` |
| **Enrichers** | `SummaryEnricher`, custom `ChunkEnricher` |
| **Embedders** | `MistralEmbedder`, custom `Embedder` |
| **Storage** | Vespa or custom vector store |
| **Retrievers** | `VectorRetriever` |
| **Rerankers** | `LLMReRanker`, `CrossEncoderReRanker`, `RRFRanker` |
| **Preprocessing** | `LLMQueryRewriter`, `LLMQueryExtension` |
| **Caching** | `SemanticCache` with `InMemoryCacheBackend` |

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

## Next steps {#next-steps}

- **[Quickstart](https://docs.mistral.ai/studio/search-toolkit/quickstart)**: build your first ingestion and retrieval pipeline end to end.
- **[Document model](https://docs.mistral.ai/studio/search-toolkit/document-model)**: understand `Document`, `DocumentChunk`, and the identity that ties them together.
- **[Search index](https://docs.mistral.ai/studio/search-toolkit/search-index)**: set up your vector store.
- **[Ingestion](https://docs.mistral.ai/studio/search-toolkit/ingestion)**: load, extract, chunk, enrich, and index your documents.
- **[Retrieval](https://docs.mistral.ai/studio/search-toolkit/retrieval)**: configure vector search with optional reranking.
