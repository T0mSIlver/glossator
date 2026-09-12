# mined2-084 (unanswerable, 16 connector calls)

## Question

What evaluation features does the Search Toolkit provide?

## Thinking

The user is asking about evaluation features provided by the Search Toolkit. This is a specific product question about Mistral AI's offerings. I need to search the documentation to find accurate information about this toolkit and its capabilities.

I should use the mistral_docs_search tool to find relevant documentation. The query should be precise: "Search Toolkit evaluation features" seems appropriate. I'll set max_hits to 5 to get a good range of results.

The search returned a hit for the Search Toolkit documentation page. I can see from the snippet that it mentions Search Toolkit is a Python framework for building information retrieval systems with components for ingestion, retrieval, and evaluation. However, the snippet doesn't provide the detailed evaluation features. I need to read the full page to extract the specific evaluation features mentioned.

Let me call mistral_docs_read_page to get the complete content of the Search Toolkit documentation.

The page content confirms that Search Toolkit provides components for evaluation, but it doesn't list the specific evaluation features in the snippet I received. I need to search more specifically for evaluation-related content within the Search Toolkit documentation. Let me try a more targeted search query.

The search results are still showing the same general page. I need to look for a dedicated evaluation section. Let me try searching for "evaluation" more broadly, or check if there's a specific evaluation page under the search-toolkit path. I'll search for pages under the search-toolkit directory.

I can see the list of pages under the search-toolkit path. There's no explicit "evaluation" page listed, but the main page mentioned that evaluation is one of the components. Let me check if there's a dedicated evaluation page or if the evaluation features are documented within one of the existing pages. I should look for any page that might contain evaluation-specific information. Let me try searching for "evaluation" across all pages again, but maybe with a different approach.

Actually, looking at the list, I don't see a dedicated evaluation page. The evaluation features might be embedded in the main documentation. Let me try to search for "evaluation" in the context of the entire search-toolkit documentation.

The search for "evaluation" under the search-toolkit path returned no results. This suggests that either:
1. There's no dedicated evaluation section with that exact term
2. The evaluation features are described using different terminology
3. The evaluation capabilities are implied but not explicitly detailed in the current documentation

Given that the main page explicitly states "It provides components for ingestion, retrieval, and evaluation", I should look for related terms. Maybe it's under "metrics", "benchmarking", "testing", or similar concepts. Let me try searching for those terms.

I found a reference to "Monitoring with metrics" in the semantic-cache section. This might be related to evaluation. Let me read that page to see if it contains evaluation features.

The semantic-cache page has monitoring metrics, but that's more about caching performance than evaluation of the retrieval system itself. Let me search more specifically for evaluation-related terms in the context of information retrieval. Maybe the evaluation features are described using terms like "retrieval evaluation", "RAG evaluation", or similar.

Let me try a broader search across the entire documentation for evaluation features related to search or retrieval.

The search results are showing API endpoints for observability and spans, which might be related to evaluation but seem to be part of a different system (Observability API) rather than the Search Toolkit itself. Let me refocus on the Search Toolkit specifically.

Looking back at the main Search Toolkit page, it explicitly states it provides "components for ingestion, retrieval, and evaluation". So evaluation is definitely a feature. Let me try to find if there's a dedicated evaluation section or page that I might have missed.

Let me check if there's an evaluation.py module or similar in the toolkit by searching for more specific terms.

I'm still not finding a dedicated evaluation page. Let me try a different approach. The main page says evaluation is a component. Maybe I need to look at the actual Python package structure. Let me search for "evaluation" in the context of the toolkit's modules or classes.

Alternatively, maybe the evaluation features are part of the observability or testing infrastructure. Let me check the changelog or other sections that might mention evaluation.

The changelog doesn't mention evaluation features explicitly. Let me try a different approach. Since the main page states that evaluation is one of the three core components (ingestion, retrieval, evaluation), there must be documentation about it. Let me try to search for any page that might contain the word "evaluation" in its URL or title.

Maybe I should look at the structure of the toolkit more carefully. The components table in the main page lists various components but doesn't show evaluation components. Let me check if there's a separate evaluation section that I'm missing.

Let me try searching for "evaluator" or "evaluation" in the context of the entire documentation site, not just under search-toolkit.

I'm getting results from the Observability Evaluations section, which seems to be a separate product (Mistral Observability) rather than the Search Toolkit. The user specifically asked about the Search Toolkit, not the Observability platform.

Let me go back to the Search Toolkit documentation and look more carefully. The main page says it provides components for evaluation. Maybe the evaluation features are embedded within the retrieval or ingestion components, or perhaps they're part of a testing/evaluation module that isn't prominently featured.

Let me try to search for any Python module or class names that might be related to evaluation in the Search Toolkit. Maybe there's an `evaluation` directory or module.

I'm still not finding explicit evaluation features in the Search Toolkit documentation. The main page mentions evaluation as a component, but there's no dedicated section or page for it in the search-toolkit directory. 

Let me reconsider: maybe the "evaluation" mentioned in the main page is a high-level concept rather than a specific set of features. Or perhaps the evaluation features are actually part of the Mistral Observability platform, which is separate from but complementary to the Search Toolkit.

However, the user specifically asked about the Search Toolkit. Let me try one more targeted search. Maybe there's a testing or benchmarking module within the toolkit. Let me search for "benchmark", "test", or "quality" in the context of Search Toolkit.

The search for benchmark/test/quality only returned information about rerankers improving ranking quality, which is not specifically about evaluation features.

At this point, I've exhausted the obvious search paths. Let me think about this differently. The main page of Search Toolkit explicitly states it provides components for "ingestion, retrieval, and evaluation". However, in all my searches, I haven't found a dedicated evaluation section or page.

There are a few possibilities:
1. The evaluation features are not yet documented in detail
2. The evaluation features are integrated into other components (like the cache metrics I found earlier)
3. The evaluation features are part of a separate but related system (like Mistral Observability)

Given that the user is asking a direct question and I have the main page that explicitly mentions evaluation as a component, I should provide an answer based on what I know:

- The Search Toolkit is a Python framework for building IR systems
- It provides components for ingestion, retrieval, **and evaluation**
- Every component can be swapped

But I need to find more specific information. Let me check if there's any mention of evaluation in the architecture or components sections more carefully. The components table didn't show evaluation components, but maybe they exist.

Let me try one final search: maybe the evaluation features are documented under a different name or in a different location. Let me search for any page that might contain evaluation-related functionality.

I've conducted extensive searches through the Mistral documentation for the Search Toolkit, and while the main page explicitly states that it "provides components for ingestion, retrieval, and evaluation", I cannot find any dedicated documentation or specific details about the evaluation features.

The only evaluation-related content I found is:
1. The main page stating evaluation is a component
2. Cache metrics in the semantic cache section (which is more about monitoring than evaluation)

Given that I've exhausted all reasonable search paths and the documentation doesn't appear to have a dedicated evaluation section, I need to provide an honest answer. The documentation mentions evaluation as a component but doesn't detail what those evaluation features are.

However, I should not guess or make up information. The most accurate answer is that while the Search Toolkit is stated to include evaluation components, the current documentation does not provide specific details about these evaluation features. I should acknowledge this limitation.

But wait - let me reconsider. Maybe the evaluation features are actually part of the Mistral Observability platform, which is a separate product. The user asked specifically about Search Toolkit, but perhaps the evaluation capabilities are provided through integration with Observability.

Actually, looking back at my search results, I found extensive documentation for "Mistral Observability Evaluations" which includes:
- Run evaluators
- Datasets
- Judges
- Scorers
- Goals
- Statistics

These seem to be evaluation features, but they're part of the Observability platform, not the Search Toolkit itself.

Given the explicit statement in the Search Toolkit documentation that it provides evaluation components, but the lack of specific documentation for those components, I should state what I know from the documentation and be honest about the gap.

The most accurate answer based on the documentation is:
1. The Search Toolkit provides components for evaluation (as stated in the main page)
2. The documentation does not currently detail what those evaluation features are specifically

But I should check one more time if there's any mention of evaluation in the quickstart or other pages.

The quickstart page also doesn't mention evaluation features. At this point, I've thoroughly searched the Search Toolkit documentation and found:

1. The main page explicitly states: "Search Toolkit is a Python framework for building information retrieval (IR) systems. It provides components for ingestion, retrieval, and evaluation."

2. However, there is no dedicated evaluation section or page in the Search Toolkit documentation.

3. The only evaluation-related content I found is in the Mistral Observability documentation, which is a separate product.

Given this, I need to provide an honest answer. The documentation states that evaluation is a component, but doesn't detail what those features are. I should not make up information. 

The most accurate answer is that while the Search Toolkit is stated to include evaluation components, the current documentation does not provide specific details about these evaluation features. The documentation only explicitly mentions evaluation in the overview, without detailing the actual evaluation capabilities.

However, I should check if there's any mention of evaluation in the context of the toolkit's relationship with other Mistral products. Maybe evaluation is provided through integration with Mistral Observability.

Let me try one final search to see if there's any connection between Search Toolkit and evaluation features.

I've completed a thorough search of the Mistral documentation for the Search Toolkit. The only explicit mention of evaluation is in the main page's overview statement: "Search Toolkit is a Python framework for building information retrieval (IR) systems. It provides components for ingestion, retrieval, and evaluation."

However, I cannot find any dedicated documentation page or section that details the specific evaluation features provided by the Search Toolkit. The documentation does not elaborate on what these evaluation components are or how to use them.

Given this situation, I have two options:
1. State that the documentation mentions evaluation as a component but doesn't provide details
2. Look at the Mistral Observability Evaluations documentation, which does have extensive evaluation features, and clarify that these are separate products

I think the most honest and helpful answer is to state what the documentation says (that evaluation is a component) but acknowledge that the current documentation does not provide specific details about the evaluation features. I should not make up features that aren't documented.

However, I notice that the user might be conflating two different Mistral products: Search Toolkit and Observability Evaluations. The Observability product has extensive evaluation features (run evaluators, datasets, judges, scorers, goals, statistics, etc.), but these are part of the Observability platform, not the Search Toolkit.

The most accurate answer is:
- The Search Toolkit documentation states it provides evaluation components
- However, the documentation does not currently detail what these evaluation features are
- The evaluation features might be planned but not yet documented, or they might be provided through integration with other Mistral products

I should provide this honest assessment rather than making up information.

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
{"q": "Search Toolkit evaluation", "max_hits": 5}
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
{"q": "evaluation", "under": "https://docs.mistral.ai/studio/search/search-toolkit", "max_hits": 10}
```

Result:

```
q: "evaluation" | under: https://docs.mistral.ai/studio/search/search-toolkit

Results: no section under https://docs.mistral.ai/studio/search/search-toolkit matched; 27 pages exist there.
next: mistral_docs_search(under="https://docs.mistral.ai/studio/search/search-toolkit") lists them; a page not listed does not exist at this commit.
```

### 6. mistral_docs_search

```json
{"q": "metrics OR benchmarking OR testing", "under": "https://docs.mistral.ai/studio/search/search-toolkit", "max_hits": 10}
```

Result:

```
q: "metrics OR benchmarking OR testing" | under: https://docs.mistral.ai/studio/search/search-toolkit

[1] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache | section: monitoring
    Semantic cache > Monitoring with metrics
    Track cache performance: ```python from mistralai.search.toolkit.retrieval.cache import CacheMetrics # Create metrics tracker metrics = CacheMetrics() cached_engine = CachedQueryEngine( engine=query_engine, cache=cache, embedder=embedder, metrics=metrics, ) # Run queries for query in queries: result = await cached_engine.search(query) # Check performance snapshot = metrics.snapshot() print(f"Hit r …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache#monitoring

[2] https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli | section: cli-reference
    CLI reference
    The `mistral-vespa` CLI manages the Vespa application lifecycle, from generating migrations to deployment and testing. > **Tip** > > Run `uv run mistral-vespa --help` for the full list of available commands and flags.
    cite: https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli

[3] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache | section: fault-tolerance
    Semantic cache > Fault tolerance
    All cache operations are non-fatal. If the cache or embedder throws an exception, the query falls through to the uncached path: ```python # Even if cache fails, retrieval continues cached_engine = CachedQueryEngine( engine=query_engine, cache=cache, embedder=embedder, ) # If embedder or cache throws exception: # - Exception is logged # - Query runs through normal pipeline # - Result is NOT cached …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache#fault-tolerance

Results: 3 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache") to read hit 1 on its page
```

### 7. mistral_docs_read_page

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

### 8. mistral_docs_search

```json
{"q": "retrieval evaluation OR RAG evaluation OR evaluation metrics", "max_hits": 10}
```

Result:

```
q: "retrieval evaluation OR RAG evaluation OR evaluation metrics"

[1] https://docs.mistral.ai/api/endpoint/beta/observability/spans | section: operation-get_span_evaluation_fields_v1_observability_spans_evaluations_fields_get
    Beta Observability Spans API > Get span evaluation field definitions
    `GET /v1/observability/spans/evaluations/fields` - Operation id: `get_span_evaluation_fields_v1_observability_spans_evaluations_fields_get` - Tag: beta/observability/spans
    cite: https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_evaluation_fields_v1_observability_spans_evaluations_fields_get

[2] https://docs.mistral.ai/api/endpoint/beta/observability/spans | section: operation-get_span_evaluation_field_options_v1_observability_spans_evaluations_fields_field_name_options_get
    Beta Observability Spans API > Get options for a span evaluation field
    `GET /v1/observability/spans/evaluations/fields/{field_name}/options` - Operation id: `get_span_evaluation_field_options_v1_observability_spans_evaluations_fields__field_name__options_get` - Tag: beta/observability/spans
    cite: https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_evaluation_field_options_v1_observability_spans_evaluations_fields_field_name_options_get

[3] https://docs.mistral.ai/api/endpoint/beta/observability/spans | section: operation-get_span_evaluation_field_options_v1_observability_spans_evaluations_fields_field_name_options_get/parameters
    Beta Observability Spans API > Get options for a span evaluation field > Parameters
    - `field_name` (string, required, in path) - `from` (string (date-time) or null, optional, in query) - `to` (string (date-time) or null, optional, in query)
    cite: https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_evaluation_field_options_v1_observability_spans_evaluations_fields_field_name_options_get

[4] https://docs.mistral.ai/studio/knowledge-rag/rag_quickstart | section: rag-quickstart
    RAG Quickstart
    Retrieval-augmented generation (RAG) combines retrieval with model generation. It helps you answer questions or generate content from external knowledge. There are two main steps in RAG: 1. **Retrieval**: retrieve relevant information from a knowledge base or an external source, for example, using text embeddings stored in a vector store. 2. **Generation**: insert the relevant information into the …
    cite: https://docs.mistral.ai/studio/knowledge-rag/rag_quickstart

[5] https://docs.mistral.ai/api/endpoint/beta/observability/spans | section: operation-get_span_evaluation_fields_v1_observability_spans_evaluations_fields_get/responses
    Beta Observability Spans API > Get span evaluation field definitions > Responses
    - `200` — Successful Response (application/json, schema GetSpanEvaluationFields) - `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError) - `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError) - `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError) - `409` — Conflict - Resourc …
    cite: https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_evaluation_fields_v1_observability_spans_evaluations_fields_get

[6] https://docs.mistral.ai/resources/observability-integrations | section: workflow-patterns
    Observability integrations > Workflow patterns to trace
    Trace each step that can change the final answer. For retrieval-augmented generation (RAG), trace document retrieval, ranking, context assembly, and generation. For agent workflows, trace each model call, tool call, handoff, retry, and final response. These traces help you answer operational questions: - Which prompt, model, or tool version produced the response? - Which retrieved documents influe …
    cite: https://docs.mistral.ai/resources/observability-integrations#workflow-patterns

[7] https://docs.mistral.ai/studio/observability/evaluations/datasets | section: can-i-pass-a-studio-dataset-id-directly-to-evaluationrun
    Datasets > FAQ > Can I pass a Studio Dataset ID directly to evaluation.run()?
    Not currently. `evaluation.run()` expects records in memory. Fetch records from Studio first, transform them into your evaluation record shape, then pass the resulting list to `dataset`.
    cite: https://docs.mistral.ai/studio/observability/evaluations/datasets#can-i-pass-a-studio-dataset-id-directly-to-evaluationrun

[8] https://docs.mistral.ai/studio/observability/evaluations/judges | section: can-i-use-the-same-judge-across-multiple-evaluation-runs
    Judges > FAQ > Can I use the same judge across multiple evaluation runs?
    Yes. A judge is a function. Reuse it across any number of evaluators and runs. If you change the judge prompt between runs, scores won't be directly comparable.
    cite: https://docs.mistral.ai/studio/observability/evaluations/judges#can-i-use-the-same-judge-across-multiple-evaluation-runs

[9] https://docs.mistral.ai/studio/observability/evaluations/system-params | section: how-it-works
    Configure system params > How it works
    Pass a `System` to `evaluation.run()`. It becomes available via `ctx.system` in both tasks and scorers: ```python from mistralai.observability import Evaluation, Evaluator, Goal, Mistral, System, TaskContext client = Mistral(api_key=os.environ["MISTRAL_API_KEY"]) async def task(ctx: TaskContext) -> str: response = await client.chat.complete_async( model=str(ctx.system.params["model"]), temperature …
    cite: https://docs.mistral.ai/studio/observability/evaluations/system-params#how-it-works

[10] https://docs.mistral.ai/api/endpoint/beta/observability/spans | section: operation-get_span_evaluation_field_options_v1_observability_spans_evaluations_fields_field_name_options_get/responses
    Beta Observability Spans API > Get options for a span evaluation field > Responses
    - `200` — Successful Response (application/json, schema GetSpanEvaluationFieldOptions) - `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError) - `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError) - `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError) - `409` — Conflict - R …
    cite: https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_evaluation_field_options_v1_observability_spans_evaluations_fields_field_name_options_get

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/api/endpoint/beta/observability/spans") to read hit 1 on its page
```

### 9. mistral_docs_search

```json
{"q": "Search Toolkit evaluation components OR evaluation module", "max_hits": 10}
```

Result:

```
q: "Search Toolkit evaluation components OR evaluation module"

[1] https://docs.mistral.ai/studio/search/search-toolkit | section: search-toolkit
    Search Toolkit
    Search Toolkit is a Python framework for building information retrieval (IR) systems. It provides components for ingestion, retrieval, and evaluation. It works across backends, and every component can be swapped. LLMs are not trained on your private data. To ground their answers in your documents you need a retrieval pipeline that ingests, indexes, and searches your content. Search Toolkit gives y …
    cite: https://docs.mistral.ai/studio/search/search-toolkit

[2] https://docs.mistral.ai/studio/search/search-toolkit | section: components
    Search Toolkit > Architecture > Components
    | Component | Built-in options | |-----------|-----------------| | **File loaders** | `FilesystemFileLoader`, custom loaders | | **Extractors** | `MistralOCRExtractor`, `SmartPDFExtractor`, `PlainTextExtractor`, `PyMuPDFExtractor`, `HTMLExtractor`, `SpreadsheetExtractor`, `EmailExtractor`, `EmailWithAttachmentsExtractor`, `NumbersExtractor`, `LegacyOfficeExtractor`, `MistralAudioTranscriptionExtra …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#components

[3] https://docs.mistral.ai/studio/search/search-toolkit/ingestion | section: components
    Ingestion > Components
    Each ingestion component is documented in detail with configuration options, best practices, and examples: - **[File loaders](https://docs.mistral.ai/studio/search/search-toolkit/ingestion/loaders)**: load files from filesystem, cloud storage, or custom sources - **[Document extractors](https://docs.mistral.ai/studio/search/search-toolkit/ingestion/extractors)**: extract content from PDFs, HTML, s …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/ingestion#components

[4] https://docs.mistral.ai/studio/search/search-toolkit/retrieval | section: components
    Retrieval > Components
    Each retrieval component is documented in detail with examples and best practices: - **[Retrievers](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers)**: VectorRetriever, KeywordRetriever, and hybrid search patterns - **[Rerankers](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers)**: LLMReRanker, CrossEncoderReRanker, RRF fusion, and custom rerankers …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval#components

[5] https://docs.mistral.ai/api/endpoint/beta/observability/spans | section: operation-get_span_evaluation_fields_v1_observability_spans_evaluations_fields_get
    Beta Observability Spans API > Get span evaluation field definitions
    `GET /v1/observability/spans/evaluations/fields` - Operation id: `get_span_evaluation_fields_v1_observability_spans_evaluations_fields_get` - Tag: beta/observability/spans
    cite: https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_evaluation_fields_v1_observability_spans_evaluations_fields_get

[6] https://docs.mistral.ai/api/endpoint/beta/observability/spans | section: operation-get_span_evaluation_field_options_v1_observability_spans_evaluations_fields_field_name_options_get
    Beta Observability Spans API > Get options for a span evaluation field
    `GET /v1/observability/spans/evaluations/fields/{field_name}/options` - Operation id: `get_span_evaluation_field_options_v1_observability_spans_evaluations_fields__field_name__options_get` - Tag: beta/observability/spans
    cite: https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_evaluation_field_options_v1_observability_spans_evaluations_fields_field_name_options_get

[7] https://docs.mistral.ai/api/endpoint/beta/observability/spans | section: operation-get_span_evaluation_field_options_v1_observability_spans_evaluations_fields_field_name_options_get/parameters
    Beta Observability Spans API > Get options for a span evaluation field > Parameters
    - `field_name` (string, required, in path) - `from` (string (date-time) or null, optional, in query) - `to` (string (date-time) or null, optional, in query)
    cite: https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_evaluation_field_options_v1_observability_spans_evaluations_fields_field_name_options_get

[8] https://docs.mistral.ai/studio/search/search-toolkit/changelog | section: 0-0-12
    Changelog > 0.0.12
    **Breaking changes** _Checkpoint serialization_ - A new `document/serialization.py` module introduces a `DocumentTypeRegistry` and stable type ids so that document classes can be round-tripped through an external service safely. **Improvements** - Added `MistralClientConfig` and `build_mistral_client()` to centralize Mistral SDK client creation for whole pipelines. - Added [`SmartPDFExtractor`](ht …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/changelog#0-0-12

[9] https://docs.mistral.ai/studio/observability/evaluations/datasets | section: can-i-pass-a-studio-dataset-id-directly-to-evaluationrun
    Datasets > FAQ > Can I pass a Studio Dataset ID directly to evaluation.run()?
    Not currently. `evaluation.run()` expects records in memory. Fetch records from Studio first, transform them into your evaluation record shape, then pass the resulting list to `dataset`.
    cite: https://docs.mistral.ai/studio/observability/evaluations/datasets#can-i-pass-a-studio-dataset-id-directly-to-evaluationrun

[10] https://docs.mistral.ai/studio/observability/evaluations/judges | section: can-i-use-the-same-judge-across-multiple-evaluation-runs
    Judges > FAQ > Can I use the same judge across multiple evaluation runs?
    Yes. A judge is a function. Reuse it across any number of evaluators and runs. If you change the judge prompt between runs, scores won't be directly comparable.
    cite: https://docs.mistral.ai/studio/observability/evaluations/judges#can-i-use-the-same-judge-across-multiple-evaluation-runs

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit") to read hit 1 on its page
```

### 10. mistral_docs_read_page

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

### 11. mistral_docs_search

```json
{"q": "evaluator OR evaluation", "max_hits": 15}
```

Result:

```
q: "evaluator OR evaluation"

[1] https://docs.mistral.ai/studio/observability/evaluations/run-evaluators | section: basic-run-evaluator
    Use run-level evaluators > Basic run evaluator
    A run evaluator receives a `RunEvaluatorContext` with all records, statistics, and metadata: ```python import asyncio import os from mistralai.observability import ( Evaluation, Evaluator, Mistral, RunEvaluator, RunEvaluatorContext, ScorerContext, System, TaskContext, ) client = Mistral(api_key=os.environ["MISTRAL_API_KEY"]) def accuracy_scorer(ctx: ScorerContext) -> int: return 1 if ctx.input_rec …
    cite: https://docs.mistral.ai/studio/observability/evaluations/run-evaluators#basic-run-evaluator

[2] https://docs.mistral.ai/studio/observability/evaluations/local-mode | section: usage
    Iterate locally > Usage
    ```python run = await client.evaluation.run( dataset=dataset, task=task, evaluators=[Evaluator(name="accuracy", scorer=scorer)], local=True, ) run.show(level="records") ``` In local mode: - No data is sent to Studio. - You don't need to specify a `project` or `evaluation`. - Results are only available in your terminal or as JSON.
    cite: https://docs.mistral.ai/studio/observability/evaluations/local-mode#usage

[3] https://docs.mistral.ai/studio/observability/evaluations/multiple-evaluators | section: independent-goals-per-evaluator
    Combine evaluators > Independent goals per evaluator
    Set different pass/fail criteria on each evaluator: ```python from mistralai.observability import Goal evaluators=[ Evaluator(name="exact_match", description="1 if output matches expected exactly.", scorer=exact_match_scorer, goal=Goal.gte(0.8)), Evaluator(name="llm_quality", description="LLM judge quality score (0 to 5).", scorer=llm_judge, goal=Goal.gte(3.5)), Evaluator(name="response_length", d …
    cite: https://docs.mistral.ai/studio/observability/evaluations/multiple-evaluators#independent-goals-per-evaluator

[4] https://docs.mistral.ai/studio/observability/evaluations/multiple-evaluators | section: statistics-computed-per-evaluator
    Combine evaluators > Statistics computed per evaluator
    | Statistic | Description | |-----------|-------------| | `avg` | Mean score across all records | | `min` | Minimum score | | `max` | Maximum score | | `std` | Standard deviation | | `count` | Number of scored records | For non-numeric scores (categorical values), the SDK computes frequency distributions and mode instead.
    cite: https://docs.mistral.ai/studio/observability/evaluations/multiple-evaluators#statistics-computed-per-evaluator

[5] https://docs.mistral.ai/studio/observability/evaluations/run-evaluators | section: when-does-the-run-evaluator-run
    Use run-level evaluators > Adding goals > When does the run evaluator run?
    After all records have been processed and scored. If any record fails, the run evaluator still runs on the successfully processed records.
    cite: https://docs.mistral.ai/studio/observability/evaluations/run-evaluators#when-does-the-run-evaluator-run

[6] https://docs.mistral.ai/studio/observability/evaluations/local-mode | section: recommended-workflow
    Iterate locally > Recommended workflow
    1. **Iterate locally**: set `local=True` and adjust your task and scorers until results look right. 2. **Push to Studio**: remove `local=True` and add `project` and `evaluation` to track results over time. ```python # Step 1: iterate locally run = await client.evaluation.run( dataset=dataset, task=task, evaluators=[Evaluator(name="accuracy", scorer=scorer)], local=True, ) # Step 2: happy with resu …
    cite: https://docs.mistral.ai/studio/observability/evaluations/local-mode#recommended-workflow

[7] https://docs.mistral.ai/studio/observability/evaluations/multiple-evaluators | section: example-multiple-rule-based-scorers
    Combine evaluators > Example: multiple rule-based scorers
    ```python import asyncio import os from mistralai.observability import Evaluation, Evaluator, Mistral, ScorerContext, System, TaskContext client = Mistral(api_key=os.environ["MISTRAL_API_KEY"]) def contains_expected(ctx: ScorerContext) -> int: return 1 if ctx.input_record["expected"] in str(ctx.output).lower() else 0 def is_short(ctx: ScorerContext) -> int: return 1 if len(str(ctx.output)) < 80 el …
    cite: https://docs.mistral.ai/studio/observability/evaluations/multiple-evaluators#example-multiple-rule-based-scorers

[8] https://docs.mistral.ai/studio/observability/evaluations/run-evaluators | section: runevaluatorcontext-reference
    Use run-level evaluators > RunEvaluatorContext reference
    | Field | Type | Description | |-------|------|-------------| | `records` | `list[RunEvaluatorRecord]` | All processed records with their scores | | `statistics` | `dict[str, EvaluatorStatistics]` | Per-evaluator aggregate statistics | | `metadata` | `dict[str, JsonValue]` | Run metadata | | `system` | `System \| None` | System config from `evaluation.run(system=...)` |
    cite: https://docs.mistral.ai/studio/observability/evaluations/run-evaluators#runevaluatorcontext-reference

[9] https://docs.mistral.ai/studio/observability/evaluations/context-objects | section: runevaluatorcontext
    Use context objects > RunEvaluatorContext
    [Run evaluators](https://docs.mistral.ai/studio/observability/evaluations/run-evaluators) receive all records and aggregated statistics after the run completes: ```python from mistralai.observability import RunEvaluatorContext def accuracy_gate(ctx: RunEvaluatorContext): return ctx.statistics["accuracy"].avg >= 0.8 ``` | Field | Type | Description | |-------|------|-------------| | `records` | `li …
    cite: https://docs.mistral.ai/studio/observability/evaluations/context-objects#runevaluatorcontext

[10] https://docs.mistral.ai/studio/observability/evaluations/system-params | section: how-it-works
    Configure system params > How it works
    Pass a `System` to `evaluation.run()`. It becomes available via `ctx.system` in both tasks and scorers: ```python from mistralai.observability import Evaluation, Evaluator, Goal, Mistral, System, TaskContext client = Mistral(api_key=os.environ["MISTRAL_API_KEY"]) async def task(ctx: TaskContext) -> str: response = await client.chat.complete_async( model=str(ctx.system.params["model"]), temperature …
    cite: https://docs.mistral.ai/studio/observability/evaluations/system-params#how-it-works

[11] https://docs.mistral.ai/studio/observability/evaluations/retry-failed-records | section: basic-workflow
    Retry failed records > Basic workflow
    ```python import asyncio import os from mistralai.observability import ( Evaluation, Evaluator, Mistral, ScorerContext, System, TaskContext, ) client = Mistral(api_key=os.environ["MISTRAL_API_KEY"]) dataset = [ {"prompt": "Say hello", "expected": "hello"}, {"prompt": "Say goodbye", "expected": "goodbye"}, ] async def task(ctx: TaskContext): response = await client.chat.complete_async( model=str(ct …
    cite: https://docs.mistral.ai/studio/observability/evaluations/retry-failed-records#basic-workflow

[12] https://docs.mistral.ai/studio/observability/evaluations/run-evaluators | section: can-i-access-individual-record-scores-inside-a-run-evaluator
    Use run-level evaluators > Adding goals > Can I access individual record scores inside a run evaluator?
    Yes. Use `get_score(record, "evaluator_name")` to retrieve a specific evaluator's score for any record in `ctx.records`.
    cite: https://docs.mistral.ai/studio/observability/evaluations/run-evaluators#can-i-access-individual-record-scores-inside-a-run-evaluator

[13] https://docs.mistral.ai/studio/observability/evaluations/system-params | section: comparing-configurations
    Configure system params > Comparing configurations
    Run the same evaluation with different systems to compare: ```python import asyncio import os from mistralai.observability import Evaluation, Evaluator, Goal, Mistral, System, TaskContext, ScorerContext client = Mistral(api_key=os.environ["MISTRAL_API_KEY"]) async def task(ctx: TaskContext) -> str: response = await client.chat.complete_async( model=str(ctx.system.params["model"]), messages=[{"role …
    cite: https://docs.mistral.ai/studio/observability/evaluations/system-params#comparing-configurations

[14] https://docs.mistral.ai/studio/observability/evaluations | section: core-concepts
    Offline evaluations > Core concepts
    **Task** A task is an async (or sync) function that receives a `TaskContext` and returns an output. This is the code you want to evaluate: ```python from mistralai.observability import TaskContext async def task(ctx: TaskContext) -> str: response = await client.chat.complete_async( model=str(ctx.system.params["model"]), messages=[ {"role": "system", "content": str(ctx.system.params["system_prompt" …
    cite: https://docs.mistral.ai/studio/observability/evaluations#core-concepts

[15] https://docs.mistral.ai/studio/observability/evaluations/num-generations | section: usage
    Reduce variance with multiple generations > Usage
    ```python import asyncio import os from mistralai.observability import ( Evaluation, Evaluator, Goal, Mistral, ScorerContext, System, TaskContext, ) client = Mistral(api_key=os.environ["MISTRAL_API_KEY"]) dataset = [ {"prompt": "What is the capital of France?", "expected": "Paris"}, {"prompt": "What is 2+2?", "expected": "4"}, ] async def task(ctx: TaskContext) -> str: response = await client.chat …
    cite: https://docs.mistral.ai/studio/observability/evaluations/num-generations#usage

Results: 15 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/observability/evaluations/run-evaluators") to read hit 1 on its page
```

### 12. mistral_docs_search

```json
{"q": "Search Toolkit evaluation OR retrieval evaluation OR ingestion evaluation", "max_hits": 10}
```

Result:

```
q: "Search Toolkit evaluation OR retrieval evaluation OR ingestion evaluation"

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

[4] https://docs.mistral.ai/studio/search/search-toolkit | section: ingestion
    Search Toolkit > Key features > Ingestion
    [Ingestion](https://docs.mistral.ai/studio/search/search-toolkit/ingestion) includes: - **Multi-format extraction**: PDF/DOCX/PPTX via Mistral OCR, HTML, spreadsheets, emails, plain text - **File loading**: Load from the local filesystem or implement custom loaders for any source - **Flexible chunking**: Character, token, markdown-aware, or separator-based splitting - **Enrichment**: Enrich docume …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#ingestion

[5] https://docs.mistral.ai/studio/search/search-toolkit | section: architecture
    Search Toolkit > Architecture
    **Ingestion** transforms raw documents into searchable chunks. A `FileLoader` reads raw bytes from a source, a `DocumentExtractor` converts them into a structured document, a `TextSplitter` divides it into chunks, optional `DocumentProcessor` stages (such as a `ChunkEnricher` or `SummaryEnricher`) add metadata, and an `Embedder` produces vectors for indexing into a vector store. **Retrieval** find …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#architecture

[6] https://docs.mistral.ai/studio/search/search-toolkit/retrieval | section: retrieval
    Retrieval
    Retrieval finds relevant chunks for a given user query. Search Toolkit supports vector (semantic), keyword (BM25), and hybrid search strategies that can be combined for optimal results. An optional **query preprocessor** transforms the raw query before search — rewriting it for clarity or expanding it into multiple variants. One or more **Retrievers** execute the search against the index. They can …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval

[7] https://docs.mistral.ai/studio/search/search-toolkit/ingestion | section: components
    Ingestion > Components
    Each ingestion component is documented in detail with configuration options, best practices, and examples: - **[File loaders](https://docs.mistral.ai/studio/search/search-toolkit/ingestion/loaders)**: load files from filesystem, cloud storage, or custom sources - **[Document extractors](https://docs.mistral.ai/studio/search/search-toolkit/ingestion/extractors)**: extract content from PDFs, HTML, s …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/ingestion#components

[8] https://docs.mistral.ai/studio/search/search-toolkit/retrieval | section: query-engine
    Retrieval > Query engine
    `QueryEngine` orchestrates the retrieval pipeline. It accepts one or more retrievers, optional query preprocessing, and optional rerankers: ```python from mistralai.search.toolkit.retrieval import QueryEngine from mistralai.search.toolkit.retrieval.retrievers import VectorRetriever from mistralai.search.toolkit.retrieval.rerankers import LLMReRanker from mistralai.search.toolkit.retrieval.pre_proc …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval#query-engine

[9] https://docs.mistral.ai/api/endpoint/beta/observability/spans | section: operation-get_span_evaluation_fields_v1_observability_spans_evaluations_fields_get
    Beta Observability Spans API > Get span evaluation field definitions
    `GET /v1/observability/spans/evaluations/fields` - Operation id: `get_span_evaluation_fields_v1_observability_spans_evaluations_fields_get` - Tag: beta/observability/spans
    cite: https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_evaluation_fields_v1_observability_spans_evaluations_fields_get

[10] https://docs.mistral.ai/studio/search/search-toolkit/ingestion | section: ingestion
    Ingestion
    Ingestion transforms raw documents into searchable chunks indexed in a vector store. You can swap pipeline components based on your needs. A `FileLoader` reads raw bytes from a source (local filesystem, cloud storage, or any custom source) and returns a `File` object. A `DocumentExtractor` converts that `File` into a structured `Document` by parsing PDFs via OCR, converting HTML to Markdown, or re …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/ingestion

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit") to read hit 1 on its page
```

### 13. mistral_docs_search

```json
{"q": "benchmark OR test OR quality OR accuracy", "under": "https://docs.mistral.ai/studio/search/search-toolkit", "max_hits": 10}
```

Result:

```
q: "benchmark OR test OR quality OR accuracy" | under: https://docs.mistral.ai/studio/search/search-toolkit

[1] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers | section: rerankers
    Rerankers
    Rerankers apply more sophisticated scoring to improve ranking quality. Initial retrieval is fast but approximate; rerankers use deeper models or logic to refine results. Search Toolkit provides rerankers in two categories: - **`ReRanker`**: operates on a single result list (LLMReRanker, CrossEncoderReRanker) - **`GroupedRanker`**: operates on multiple result groups (RRFRanker for fusion) Multiple …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers

[2] https://docs.mistral.ai/studio/search/search-toolkit/ingestion | section: ingestion
    Ingestion
    Ingestion transforms raw documents into searchable chunks indexed in a vector store. You can swap pipeline components based on your needs. A `FileLoader` reads raw bytes from a source (local filesystem, cloud storage, or any custom source) and returns a `File` object. A `DocumentExtractor` converts that `File` into a structured `Document` by parsing PDFs via OCR, converting HTML to Markdown, or re …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/ingestion

Results: 2 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers") to read hit 1 on its page
```

### 14. mistral_docs_search

```json
{"q": "Search Toolkit evaluation features metrics OR scoring OR assessment", "max_hits": 10}
```

Result:

```
q: "Search Toolkit evaluation features metrics OR scoring OR assessment"

[1] https://docs.mistral.ai/studio/search/search-toolkit | section: retrieval
    Search Toolkit > Key features > Retrieval
    [Retrieval](https://docs.mistral.ai/studio/search/search-toolkit/retrieval) includes: - **Multiple strategies**: Vector (semantic) search with optional reranking - **Query preprocessing**: Improve user queries with LLM reformulation or query extension - **Reranking**: LLM reranker, cross-encoder reranker, or custom rerankers - **Semantic caching**: Cache results by query similarity to skip redunda …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#retrieval

[2] https://docs.mistral.ai/studio/search/search-toolkit | section: ingestion
    Search Toolkit > Key features > Ingestion
    [Ingestion](https://docs.mistral.ai/studio/search/search-toolkit/ingestion) includes: - **Multi-format extraction**: PDF/DOCX/PPTX via Mistral OCR, HTML, spreadsheets, emails, plain text - **File loading**: Load from the local filesystem or implement custom loaders for any source - **Flexible chunking**: Character, token, markdown-aware, or separator-based splitting - **Enrichment**: Enrich docume …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#ingestion

[3] https://docs.mistral.ai/studio/search/search-toolkit | section: search-toolkit
    Search Toolkit
    Search Toolkit is a Python framework for building information retrieval (IR) systems. It provides components for ingestion, retrieval, and evaluation. It works across backends, and every component can be swapped. LLMs are not trained on your private data. To ground their answers in your documents you need a retrieval pipeline that ingests, indexes, and searches your content. Search Toolkit gives y …
    cite: https://docs.mistral.ai/studio/search/search-toolkit

[4] https://docs.mistral.ai/studio/search/search-toolkit | section: components
    Search Toolkit > Architecture > Components
    | Component | Built-in options | |-----------|-----------------| | **File loaders** | `FilesystemFileLoader`, custom loaders | | **Extractors** | `MistralOCRExtractor`, `SmartPDFExtractor`, `PlainTextExtractor`, `PyMuPDFExtractor`, `HTMLExtractor`, `SpreadsheetExtractor`, `EmailExtractor`, `EmailWithAttachmentsExtractor`, `NumbersExtractor`, `LegacyOfficeExtractor`, `MistralAudioTranscriptionExtra …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#components

[5] https://docs.mistral.ai/studio/search/search-toolkit | section: architecture
    Search Toolkit > Architecture
    **Ingestion** transforms raw documents into searchable chunks. A `FileLoader` reads raw bytes from a source, a `DocumentExtractor` converts them into a structured document, a `TextSplitter` divides it into chunks, optional `DocumentProcessor` stages (such as a `ChunkEnricher` or `SummaryEnricher`) add metadata, and an `Embedder` produces vectors for indexing into a vector store. **Retrieval** find …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#architecture

[6] https://docs.mistral.ai/studio/search/search-toolkit/retrieval | section: retrieval
    Retrieval
    Retrieval finds relevant chunks for a given user query. Search Toolkit supports vector (semantic), keyword (BM25), and hybrid search strategies that can be combined for optimal results. An optional **query preprocessor** transforms the raw query before search — rewriting it for clarity or expanding it into multiple variants. One or more **Retrievers** execute the search against the index. They can …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval

[7] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers | section: available-rerankers
    Rerankers > Available rerankers
    | Reranker | Type | Purpose | |----------|------|---------| | **[LLM ReRanker](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#llm-reranker)** | ReRanker | Deep relevance scoring using an LLM | | **[Cross-Encoder ReRanker](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#cross-encoder-reranker)** | ReRanker | Fast reranking using dedicated model | | …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#available-rerankers

[8] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers | section: rerankers
    Rerankers
    Rerankers apply more sophisticated scoring to improve ranking quality. Initial retrieval is fast but approximate; rerankers use deeper models or logic to refine results. Search Toolkit provides rerankers in two categories: - **`ReRanker`**: operates on a single result list (LLMReRanker, CrossEncoderReRanker) - **`GroupedRanker`**: operates on multiple result groups (RRFRanker for fusion) Multiple …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers

[9] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache | section: monitoring
    Semantic cache > Monitoring with metrics
    Track cache performance: ```python from mistralai.search.toolkit.retrieval.cache import CacheMetrics # Create metrics tracker metrics = CacheMetrics() cached_engine = CachedQueryEngine( engine=query_engine, cache=cache, embedder=embedder, metrics=metrics, ) # Run queries for query in queries: result = await cached_engine.search(query) # Check performance snapshot = metrics.snapshot() print(f"Hit r …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/semantic-cache#monitoring

[10] https://docs.mistral.ai/studio/search/agentic-search | section: latency
    Agentic Search > Latency and tradeoffs
    Each tool call has a cost, but navigation can reduce end-to-end latency and token usage because the model converges faster. Instead of repeatedly issuing broad searches, the agent can stay inside the right source, use `grep` to jump to specific terms, and use `exclude_ids` to avoid revisiting the same chunks. In the Agentic Search benchmarks cited in the Search Toolkit launch materials, the full a …
    cite: https://docs.mistral.ai/studio/search/agentic-search#latency

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit") to read hit 1 on its page
```

### 15. mistral_docs_read_page

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

### 16. mistral_docs_search

```json
{"q": "Search Toolkit AND evaluation", "max_hits": 5}
```

Result:

```
q: "Search Toolkit AND evaluation"

[1] https://docs.mistral.ai/studio/search/search-toolkit | section: search-toolkit
    Search Toolkit
    Search Toolkit is a Python framework for building information retrieval (IR) systems. It provides components for ingestion, retrieval, and evaluation. It works across backends, and every component can be swapped. LLMs are not trained on your private data. To ground their answers in your documents you need a retrieval pipeline that ingests, indexes, and searches your content. Search Toolkit gives y …
    cite: https://docs.mistral.ai/studio/search/search-toolkit

[2] https://docs.mistral.ai/studio/search/search-toolkit | section: next-steps
    Search Toolkit > Next steps
    - **[Quickstart](https://docs.mistral.ai/studio/search/search-toolkit/quickstart)**: build your first ingestion and retrieval pipeline end to end. - **[Document model](https://docs.mistral.ai/studio/search/search-toolkit/concepts/document-model)**: understand `Document`, `DocumentChunk`, and the identity that ties them together. - **[Embedding model](https://docs.mistral.ai/studio/search/search-to …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#next-steps

[3] https://docs.mistral.ai/studio/search/search-toolkit | section: packages
    Search Toolkit > Installation and extras
    Install the core package: ```bash uv add mistralai-search-toolkit ``` Optional extras add specialized functionality: | Extra | Description | |-------|-------------| | `vespa` | Vespa plugin for vector storage and semantic search | | `extractor-pymupdf` | Advanced PDF extraction with PyMuPDF Pro | | `extractor-spreadsheet` | Spreadsheet parsing (Excel, CSV, Calamine format) | | `extractor-email` | …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#packages

[4] https://docs.mistral.ai/studio/search/search-toolkit | section: ingestion
    Search Toolkit > Key features > Ingestion
    [Ingestion](https://docs.mistral.ai/studio/search/search-toolkit/ingestion) includes: - **Multi-format extraction**: PDF/DOCX/PPTX via Mistral OCR, HTML, spreadsheets, emails, plain text - **File loading**: Load from the local filesystem or implement custom loaders for any source - **Flexible chunking**: Character, token, markdown-aware, or separator-based splitting - **Enrichment**: Enrich docume …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#ingestion

[5] https://docs.mistral.ai/studio/search/search-toolkit | section: architecture
    Search Toolkit > Architecture
    **Ingestion** transforms raw documents into searchable chunks. A `FileLoader` reads raw bytes from a source, a `DocumentExtractor` converts them into a structured document, a `TextSplitter` divides it into chunks, optional `DocumentProcessor` stages (such as a `ChunkEnricher` or `SummaryEnricher`) add metadata, and an `Embedder` produces vectors for indexing into a vector store. **Retrieval** find …
    cite: https://docs.mistral.ai/studio/search/search-toolkit#architecture

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit") to read hit 1 on its page
```

## Answer

The **Search Toolkit** documentation explicitly states that it provides **components for ingestion, retrieval, and evaluation** for building information retrieval (IR) systems, but it does **not currently detail specific evaluation features** in its dedicated pages.

### What We Know from the Documentation:
- The [Search Toolkit overview](https://docs.mistral.ai/studio/search/search-toolkit) confirms that **evaluation is a core component** alongside ingestion and retrieval, and that all components are swappable.
- However, **no dedicated evaluation section or page exists** under the Search Toolkit documentation at this time. The available pages focus on:
  - [Ingestion](https://docs.mistral.ai/studio/search/search-toolkit/ingestion) (loaders, extractors, splitters, enrichers, embedders)
  - [Retrieval](https://docs.mistral.ai/studio/search/search-toolkit/retrieval) (retrievers, rerankers, query preprocessing, semantic caching)
  - [Search index backends](https://docs.mistral.ai/studio/search/search-toolkit/search-index) (Vespa, Postgres, custom vector stores)

### Related Evaluation Features in Mistral’s Ecosystem:
If you are looking for **evaluation capabilities**, Mistral’s **[Observability Evaluations](https://docs.mistral.ai/studio/observability/evaluations)** product provides a full suite of tools for evaluating RAG and agent workflows, including:
- **Run evaluators** (aggregate statistics, goals, and pass/fail criteria)
- **Datasets** (structured evaluation data)
- **Judges** (LLM-based or rule-based scorers)
- **Metrics** (hit rate, latency, accuracy, etc.)

### Summary:
The **Search Toolkit itself does not currently document specific evaluation features** beyond the high-level mention in its overview. For evaluation workflows, you may need to integrate with **[Mistral Observability Evaluations](https://docs.mistral.ai/studio/observability/evaluations)** or implement custom evaluation logic using the toolkit’s swappable components.

