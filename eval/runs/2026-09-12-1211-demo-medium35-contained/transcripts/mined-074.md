# mined-074 (single_page, 2 connector calls)

## Question

What does agentic search require of the index, and which navigation tools does it expose?

## Thinking

The user asks about "agentic search" and its requirements for the index, as well as the navigation tools it exposes. This is a specific technical question about Mistral's capabilities. I need to search the Mistral documentation for information about agentic search, its index requirements, and its navigation tools. I'll use the mistral_docs_search tool with a query that captures all these aspects.

I received search results pointing to the Agentic Search documentation. The results show there's a section about navigation tools. I need to read the full page to get complete information about index requirements and navigation tools. Let me fetch the page content.

I've now read the full Agentic Search documentation page. I can see the requirements for the index and the navigation tools. The key points are:
1. Index requirement: Must be a `NavigableIndex` with schema migration set to `IndexingMode.DOCUMENT_PER_CHUNK` so chunks carry source offsets
2. Navigation tools: There are 7 tools exposed by the MCP server: search, open, navigate, read, grep, ingest, delete

I need to structure this information clearly for the user, separating the index requirements from the navigation tools, and providing proper citations. I should also mention that these tools are exposed via MCP server.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "agentic search requirements for the index and navigation tools it exposes"}
```

Result:

```
q: "agentic search requirements for the index and navigation tools it exposes"

[1] https://docs.mistral.ai/studio/search/agentic-search | section: navigation-tools
    Agentic Search > How Agentic Search works > Navigation tools
    The model calls the following tools inside the loop. Each one operates on the search index and returns chunks with their content, score, and position metadata. | Tool | What it does | |------|-------------| | `search(query, top_k, exclude_ids)` | Runs semantic or hybrid retrieval across the collection. Pass `exclude_ids` to avoid returning chunks the agent already inspected. | | `open(source_id, s …
    cite: https://docs.mistral.ai/studio/search/agentic-search#navigation-tools

[2] https://docs.mistral.ai/studio/search/agentic-search | section: get-started
    Agentic Search > Get started with the starter app
    The fastest way to try Agentic Search is with the [search-starter-app](https://github.com/mistralai/search-starter-app) template. It is a [Copier](https://copier.readthedocs.io/) template that scaffolds a project with ingestion pipelines, a Vespa search index, an MCP server exposing the navigation tools, and sample data. The starter app is designed to be driven by an agent. You scaffold the projec …
    cite: https://docs.mistral.ai/studio/search/agentic-search#get-started

[3] https://docs.mistral.ai/studio/search/agentic-search | section: use-as-mcp
    Agentic Search > Use Agentic Search as MCP tools
    The MCP server exposes seven tools that any MCP-compatible agent can call. The starter app registers the server in `.mcp.json` so Vibe discovers it automatically, but you can also connect from Studio or a custom agent.
    cite: https://docs.mistral.ai/studio/search/agentic-search#use-as-mcp

[4] https://docs.mistral.ai/studio/search/agentic-search | section: retrieval-primitives-agentic-loop
    Agentic Search > Retrieval primitives and the agentic loop
    Agentic Search is not another retrieval method next to keyword or semantic search. Keyword and semantic search are retrieval primitives. Agentic Search is an orchestration layer that uses those primitives, adds navigation, and iterates until the model has enough evidence. | Layer | How it works | Best for | |-------|-------------|----------| | Keyword (lexical) | Matches exact terms or phrases | K …
    cite: https://docs.mistral.ai/studio/search/agentic-search#retrieval-primitives-agentic-loop

[5] https://docs.mistral.ai/studio/search/agentic-search | section: drive-with-agent
    Agentic Search > Get started with the starter app > Ingest and search with an agent
    The starter app registers an MCP server in `.mcp.json` that exposes the search and navigation tools. When you launch Vibe in the project directory, it discovers the server and its 7 tools automatically. Use the tabs to follow the same flow as the demo: start Vibe, ingest a document, then ask a question. **Start Vibe** ```bash vibe --trust ``` Vibe detects the MCP server and the search skill. You c …
    cite: https://docs.mistral.ai/studio/search/agentic-search#drive-with-agent

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/agentic-search") to read hit 1 on its page
```

### 2. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/search/agentic-search"}
```

Result:

```
page: https://docs.mistral.ai/studio/search/agentic-search | "Agentic Search"

## section: agentic-search
    Agentic Search
    cite: https://docs.mistral.ai/studio/search/agentic-search
# Agentic Search

Agentic Search helps agents answer questions when the answer is not in the first chunk returned by retrieval. Instead of searching again and hoping for a better result, the model can work inside the corpus: search to find a source, open it, move through nearby chunks, grep for exact terms, and search again without repeating chunks.

In short, retrieval finds likely sources. Agentic Search lets the model inspect those sources and gather enough evidence to answer. You can use it as a set of MCP tools that drop into any agent, or as part of the [Search Toolkit](https://docs.mistral.ai/studio/search/search-toolkit) SDK for custom retrieval pipelines. It works in Studio, in open-source deployments, and in [Libraries](https://docs.mistral.ai/studio/search/libraries).

## section: retrieval-primitives-agentic-loop
    Agentic Search > Retrieval primitives and the agentic loop
    cite: https://docs.mistral.ai/studio/search/agentic-search#retrieval-primitives-agentic-loop
## Retrieval primitives and the agentic loop {#retrieval-primitives-agentic-loop}

Agentic Search is not another retrieval method next to keyword or semantic search. Keyword and semantic search are retrieval primitives. Agentic Search is an orchestration layer that uses those primitives, adds navigation, and iterates until the model has enough evidence.

| Layer | How it works | Best for |
|-------|-------------|----------|
| Keyword (lexical) | Matches exact terms or phrases | Known identifiers, code, exact quotes |
| Hybrid or semantic retrieval | Combines keyword and vector search, or uses vector search alone | Natural-language questions over a corpus |
| Agentic Search | Calls retrieval tools, navigates inside documents, excludes already-seen chunks, and searches again | Complex questions that require source verification or evidence across documents |

Most production search setups start with hybrid retrieval because it combines keyword precision with semantic recall. Agentic Search builds on that foundation: `search` uses semantic or hybrid retrieval, and `grep` adds targeted keyword matching inside a specific document.

## section: how-it-works
    Agentic Search > How Agentic Search works
    cite: https://docs.mistral.ai/studio/search/agentic-search#how-it-works
## How Agentic Search works {#how-it-works}

Agentic Search runs a retrieval loop. The model does not just receive chunks and stop. It can inspect a result, drill into the source document to read surrounding context, then re-query with what it learned.

## section: the-retrieval-loop
    Agentic Search > How Agentic Search works > The retrieval loop
    cite: https://docs.mistral.ai/studio/search/agentic-search#the-retrieval-loop
### The retrieval loop {#the-retrieval-loop}

1. **Search**: The model runs a query across the collection and receives the most relevant chunks.
2. **Inspect**: The model picks a promising hit and reads the surrounding context within that document, without re-running a global search.
3. **Grep**: The model searches for an exact term or phrase inside the same document to jump to a more specific region.
4. **Navigate or read**: The model steps through adjacent chunks or reads a known source range to gather evidence.
5. **Re-query**: Armed with new context, the model runs another search with `exclude_ids` so already-seen chunks don't come back again.

The loop continues until the model has enough evidence to answer the question. `exclude_ids` makes corpus-level pagination possible: the agent can move through new results instead of cycling over the same chunks.

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

## section: get-started
    Agentic Search > Get started with the starter app
    cite: https://docs.mistral.ai/studio/search/agentic-search#get-started
## Get started with the starter app {#get-started}

The fastest way to try Agentic Search is with the [search-starter-app](https://github.com/mistralai/search-starter-app) template. It is a [Copier](https://copier.readthedocs.io/) template that scaffolds a project with ingestion pipelines, a Vespa search index, an MCP server exposing the navigation tools, and sample data.

The starter app is designed to be driven by an agent. You scaffold the project, start Vespa, then launch an agent like [Vibe](https://docs.mistral.ai/vibe) that discovers the MCP server and calls the search and ingestion tools through natural language.

## section: prerequisites
    Agentic Search > Get started with the starter app > Prerequisites
    cite: https://docs.mistral.ai/studio/search/agentic-search#prerequisites
### Prerequisites {#prerequisites}

- A **Mistral API key** from [console.mistral.ai](https://console.mistral.ai/)
- **Docker** for running Vespa locally
- [**uv**](https://docs.astral.sh/uv/) for Python package management
- [**Copier**](https://copier.readthedocs.io/) for scaffolding the project
- [**Vibe**](https://docs.mistral.ai/vibe) (or any MCP-compatible agent) to drive the search loop

## section: scaffold
    Agentic Search > Get started with the starter app > Scaffold and start the index
    cite: https://docs.mistral.ai/studio/search/agentic-search#scaffold
### Scaffold and start the index {#scaffold}

Create a new project from the template, then start Vespa and apply the schema migrations. Use the tabs to copy the commands or inspect the generated structure.

**Commands**

```bash
uvx copier copy gh:mistralai/search-starter-app my-search-project
cd my-search-project
make setup-vespa
```

Copier asks for your Mistral API key and a collection name. The `make setup-vespa` target starts a Vespa container with Docker and deploys the schema migrations. When it finishes, the search index is ready.

**Project layout**

```text
my-search-project/
├── Makefile                      # setup, ingest, search, mcp, bruno targets
├── .env                          # API key, collection name, Vespa ports
├── .mcp.json                     # MCP server registration for Vibe
├── .agents/skills/search/        # Search Toolkit agent skill
├── src/
│   ├── entrypoints/
│   │   ├── ingest.py             # Ingestion pipeline into the search index
│   │   ├── search.py             # Query engine over the index
│   │   └── mcp_server.py         # MCP server with search and navigation tools
│   └── search_app/
│       ├── __init__.py           # Vespa app definition
│       └── migrations/           # Schema migrations
└── sample_data/
    └── hello.txt                 # Sample document
```

## section: drive-with-agent
    Agentic Search > Get started with the starter app > Ingest and search with an agent
    cite: https://docs.mistral.ai/studio/search/agentic-search#drive-with-agent
### Ingest and search with an agent {#drive-with-agent}

The starter app registers an MCP server in `.mcp.json` that exposes the search and navigation tools. When you launch Vibe in the project directory, it discovers the server and its 7 tools automatically. Use the tabs to follow the same flow as the demo: start Vibe, ingest a document, then ask a question.

**Start Vibe**

```bash
vibe --trust
```

Vibe detects the MCP server and the search skill. You can verify the connection with `/mcp`, which lists the server and its tools.

**Ingest**

Ask the agent to ingest a document in natural language. The agent picks the `ingest` MCP tool and asks for your approval:

```text
Ingest https://arxiv.org/pdf/1706.03762.pdf
```

The agent calls the `ingest` tool, which downloads the PDF, extracts text with Mistral OCR, splits it into chunks, generates embeddings, and indexes them. You see the result:

```text
MCP tool ingest completed
Indexed 16 chunks from 'https://arxiv.org/pdf/1706.03762.pdf' into 'exampledocs'.
```

The `ingest` tool accepts local paths, `file://` URIs, and `http(s)://` URLs. Text files use plain-text extraction; PDFs, DOCX, and images use Mistral OCR.

**Ask**

Once documents are indexed, ask the agent a question. The agent calls the `search` tool to retrieve relevant chunks, then uses the navigation tools to drill into the source and build a grounded answer:

```text
How does the attention mechanism work?
```

The agent runs the retrieval loop:

(same sample as above)

The agent runs the retrieval loop:

1. Calls `search` with the question and receives the most relevant chunks.
2. Calls `open` to read surrounding context within the source document.
3. Calls `grep` to jump to exact terms such as `scaled dot-product attention` or `multi-head attention` inside the same document.
4. Calls `navigate` or `read` to gather nearby evidence.
5. Calls `search` again with `exclude_ids` if it needs to connect information across documents.
6. Produces a final answer grounded in the indexed content.

```text
MCP tool search completed

The attention mechanism uses scaled dot-product attention to compute
compatibility between queries and keys, then applies a softmax to obtain
weights for a weighted sum of values. Multi-head attention runs several
attention functions in parallel, allowing the model to attend to
information from different representation subspaces.
```

> **Tip**
>
> You can also run ingestion and search directly from the shell with `make ingest path=sample_data/hello.txt` and `make search query="hello world"`. The MCP server is the recommended path for agentic workflows.

## section: use-as-mcp
    Agentic Search > Use Agentic Search as MCP tools
    cite: https://docs.mistral.ai/studio/search/agentic-search#use-as-mcp
## Use Agentic Search as MCP tools {#use-as-mcp}

The MCP server exposes seven tools that any MCP-compatible agent can call. The starter app registers the server in `.mcp.json` so Vibe discovers it automatically, but you can also connect from Studio or a custom agent.

## section: run-mcp-server
    Agentic Search > Use Agentic Search as MCP tools > Run the MCP server
    cite: https://docs.mistral.ai/studio/search/agentic-search#run-mcp-server
### Run the MCP server {#run-mcp-server}

The MCP server starts automatically when Vibe launches in the project directory. To run it standalone, use the tab that matches your transport mode.

**Stdio**

```bash
uv run python -m entrypoints.mcp_server
```

Use stdio mode for local agents such as Vibe.

**HTTP**

```bash
uv run python -m entrypoints.mcp_server --http --host 127.0.0.1 --port 8000
```

Use HTTP mode for remote or shared deployments.

**Makefile shortcut**

```bash
make mcp
```

The Makefile shortcut runs the server in HTTP mode.

## section: register-agent
    Agentic Search > Use Agentic Search as MCP tools > Register with an agent
    cite: https://docs.mistral.ai/studio/search/agentic-search#register-agent
### Register with an agent {#register-agent}

- **Vibe**: The `.mcp.json` file in the generated project registers the server. Run `vibe --trust` in the project directory and Vibe discovers it.
- **Studio**: Add the server as a connector or MCP server in the agent configuration.
- **Custom agents**: Connect any MCP-compatible client to the server's stdio or HTTP endpoint.

The MCP server includes instructions that describe the retrieval loop, so the agent knows to start with `search`, drill into results with `open`, `grep`, `navigate`, and `read`, then call `search` again with `exclude_ids` to connect information across documents without repeating the same chunks.

> **Tip**
>
> To scope a search to a single document, include the document title or `source_id` in the query. This narrows the global search and reduces latency.

## section: use-with-sdk
    Agentic Search > Use Agentic Search with the SDK
    cite: https://docs.mistral.ai/studio/search/agentic-search#use-with-sdk
## Use Agentic Search with the SDK {#use-with-sdk}

If you need more control than the MCP server provides, build retrieval pipelines directly with the Search Toolkit SDK. The SDK gives you the same `QueryEngine` and `VectorRetriever` that the MCP server uses, plus advanced features like query rewriting, multi-retriever fusion, and semantic caching.

## section: sdk-patterns
    Agentic Search > Use Agentic Search with the SDK > Core SDK patterns
    cite: https://docs.mistral.ai/studio/search/agentic-search#sdk-patterns
### Core SDK patterns {#sdk-patterns}

The SDK snippets build from the smallest setup to more advanced retrieval. Use the tabs to start with the client, run a query, then add preprocessing or hybrid retrieval.

**Client**

```python
from mistralai.client import Mistral
from mistralai.search.toolkit.embedders import MistralEmbedder

client = Mistral(api_key="your-api-key")
embedder = MistralEmbedder(client=client)
```

**Query engine**

Create a `QueryEngine` with a `VectorRetriever` backed by your search index:

```python
from mistralai.search.toolkit.retrieval import QueryEngine, VectorRetriever
from search_app import get_index

vector_store = get_index("exampledocs")
query_engine = QueryEngine(
    retriever=[VectorRetriever(client=vector_store, embedder=embedder)],
)

result = await query_engine.search(
    query="What is RAG?",
    top_k=5,
    include_metadata=True,
    include_content=True,
)

for hit in result.results:
    print(f"Score: {hit.score:.3f}")
    print(f"Content: {hit.chunk.content[:200]}")
```

**Preprocessing**

Two preprocessors are particularly relevant for agentic behavior:

- `LLMQueryExtension` breaks a query into sub-queries. Each runs an independent retrieval pass, and the results are combined. This improves recall for multi-faceted questions.
- `LLMQueryRewriter` rewrites informal queries into a more structured form before retrieval.

```python
from mistralai.search.toolkit.retrieval.pre_processors import LLMQueryExtension
from mistralai.search.toolkit.llm import MistralChat, LLMConfig

llm = MistralChat(
    client=client,
    config=LLMConfig(model="mistral-small-latest"),
)

query_engine = QueryEngine(
    retriever=[VectorRetriever(client=vector_store, embedder=embedder)],
    query_rewriter=LLMQueryExtension(llm_provider=llm, num_queries=3),
)
```

**Hybrid retrieval**

**Hybrid retrieval**

Run multiple retrievers with different query profiles, then fuse the results with `RRFRanker` (Reciprocal Rank Fusion). This combines dense and hybrid retrieval for better coverage.

```python
from mistralai.search.toolkit.retrieval.rerankers import RRFRanker

dense_store = get_index("exampledocs", query_profile="dense")
hybrid_store = get_index("exampledocs", query_profile="hybrid")

query_engine = QueryEngine(
    retriever=[
        VectorRetriever(client=dense_store, embedder=embedder),
        VectorRetriever(client=hybrid_store, embedder=embedder),
    ],
    rerankers=[RRFRanker(rrf_k=60, top_k=10)],
)
```

You can chain rerankers from cheap to expensive for progressive refinement. For example, fuse with `RRFRanker` first, then apply an `LLMReRanker` for a final quality pass.

## section: ingest-documents
    Agentic Search > Ingest documents
    cite: https://docs.mistral.ai/studio/search/agentic-search#ingest-documents
## Ingest documents {#ingest-documents}

The ingestion pipeline loads files, extracts text, splits into chunks, optionally enriches them, generates embeddings, and indexes the result. The starter app routes files by extension: text files use plain-text extraction, and everything else uses Mistral OCR. Use the tabs to compare the two extractor paths.

**Text files**

```python
from mistralai.search.toolkit.ingestion.pipelines import Pipeline
from mistralai.search.toolkit.ingestion.loaders import FilesystemFileLoader
from mistralai.search.toolkit.ingestion.extractors import PlainTextExtractor
from mistralai.search.toolkit.ingestion.text_splitters import (
    MarkdownTextSplitter,
    MarkdownTextSplitterConfig,
)

pipeline = Pipeline(
    loader=FilesystemFileLoader(),
    extractor=PlainTextExtractor(),
    text_splitter=MarkdownTextSplitter(
        MarkdownTextSplitterConfig(chunk_size=4096, chunk_overlap=50)
    ),
    embedder=embedder,
    stores=vector_store,
)

total = await pipeline.run(documents=["doc.txt"], use_checkpoint=False)
print(f"Indexed {total} chunks.")
```

**PDFs and scans**

Swap `PlainTextExtractor` with `MistralOCRExtractor` to handle PDFs, DOCX, and images:

```python
from mistralai.search.toolkit.ingestion.extractors import MistralOCRExtractor

pipeline = Pipeline(
    loader=FilesystemFileLoader(),
    extractor=MistralOCRExtractor(client=client),
    text_splitter=MarkdownTextSplitter(
        MarkdownTextSplitterConfig(chunk_size=4096, chunk_overlap=50)
    ),
    embedder=embedder,
    stores=vector_store,
)
```

You can also ingest documents through the MCP server's `ingest` tool, which accepts local paths, `file://` URIs, and HTTP URLs. The server handles the routing automatically.

## section: latency
    Agentic Search > Latency and tradeoffs
    cite: https://docs.mistral.ai/studio/search/agentic-search#latency
## Latency and tradeoffs {#latency}

Each tool call has a cost, but navigation can reduce end-to-end latency and token usage because the model converges faster. Instead of repeatedly issuing broad searches, the agent can stay inside the right source, use `grep` to jump to specific terms, and use `exclude_ids` to avoid revisiting the same chunks.

In the Agentic Search benchmarks cited in the Search Toolkit launch materials, the full agentic loop with navigation improved FinanceBench accuracy from 27% for single-shot RAG to 86%. Compared with a search-only loop, the full navigation and tool stack reduced FinanceBench p90 latency by 40%, reduced OfficeQA token usage by 1.8x, and shortened a Vibe task from 368 seconds to 227 seconds. For background on Search Toolkit, see [Introducing Search Toolkit](https://mistral.ai/news/search-toolkit/).

To keep the loop efficient:

- **Use `exclude_ids` on follow-up searches** so the agent sees new chunks instead of repeated results.
- **Scope searches to a single document** by including its title or `source_id` in the query.
- **Use `grep` before broad re-querying** when the agent already knows the term or phrase it needs.
- **Tune `top_k` per hop** to keep context windows manageable.
- **Use a semantic cache** to skip redundant retrieval across similar queries.
- **Bound the number of hops** in your agent definitions to limit the loop depth.

> **Info**
>
> For an overview of semantic caching, see the [Search Toolkit retrieval guide](https://docs.mistral.ai/studio/search/search-toolkit/retrieval).

## section: agents
    Agentic Search > Integrate into agents, workflows, and deployments > Agents
    cite: https://docs.mistral.ai/studio/search/agentic-search#agents
### Agents {#agents}

Register the search MCP server so an agent can call the search and navigation tools autonomously. With Vibe, the `.mcp.json` file in the generated project handles registration. Run `vibe --trust` in the project directory, then use `/mcp` to verify the connection. The server's instructions describe the retrieval loop, so the agent knows to start with `search`, drill into results, then re-query to connect information.

## section: workflows
    Agentic Search > Integrate into agents, workflows, and deployments > Workflows
    cite: https://docs.mistral.ai/studio/search/agentic-search#workflows
### Workflows {#workflows}

Use the Mistral Workflows API to orchestrate ingestion and retrieval as workflow activities. Start from the starter app's `src/entrypoints/` scripts when you need workflow tasks that ingest documents or query an index.

## section: deployments
    Agentic Search > Integrate into agents, workflows, and deployments > Customer deployments
    cite: https://docs.mistral.ai/studio/search/agentic-search#deployments
### Customer deployments {#deployments}

- Self-host the index with Vespa and Docker, or use a managed backend.
- Expose the MCP server in HTTP mode behind your own authentication for production agents.
- Generate a `vespa.lock` snapshot for CI reproducibility with `make generate-vespa-lock`.

## section: next-steps
    Agentic Search > Next steps
    cite: https://docs.mistral.ai/studio/search/agentic-search#next-steps
## Next steps {#next-steps}

- [Search Toolkit](https://docs.mistral.ai/studio/search/search-toolkit): learn about ingestion pipelines, retrieval strategies, and the full SDK.
- [Libraries](https://docs.mistral.ai/studio/search/libraries): use managed document ingestion and search for built-in RAG.
- [Connectors](https://docs.mistral.ai/studio/connectors): connect models and agents to external tools and data sources.
- [Agents](https://docs.mistral.ai/studio/agents/introduction): combine language models with built-in tools for multi-step reasoning.
- [search-starter-app](https://github.com/mistralai/search-starter-app): the Copier template for bootstrapping a Search Toolkit project.

Results: 20 sections, the whole page.
```

## Answer

Agentic Search requires the index to be a **`NavigableIndex`**, with the schema migration explicitly set to **`IndexingMode.DOCUMENT_PER_CHUNK`** so that chunks carry source offsets and can be traversed in order.
[Navigation tools](https://docs.mistral.ai/studio/search/agentic-search#navigation-tools)

It exposes the following **seven navigation tools** (via an MCP server) that operate on the search index and return chunks with content, score, and position metadata:

| Tool | Purpose |
|------|---------|
| `search(query, top_k, exclude_ids)` | Semantic or hybrid retrieval across the collection; `exclude_ids` prevents re-returning already inspected chunks. |
| `open(source_id, start_offset, end_offset, window)` | Expands context around a retrieved chunk, returning adjacent chunks in reading order. |
| `navigate(source_id, start_offset, end_offset, direction, top_k)` | Steps forward/backward through a document from a known position. |
| `read(source_id, start_offset, end_offset, top_k)` | Reads chunks from a known source range (e.g., returned by search or navigation). |
| `grep(source_id, pattern, mode, top_k)` | Lexical search for an exact term/phrase within a single document. |
| `ingest(uri)` | Adds a document to the index (local path, `file://`, or `http(s)://` URL). |
| `delete(source_id)` | Removes a document and all its chunks from the index. |
[Navigation tools](https://docs.mistral.ai/studio/search/agentic-search#navigation-tools)

