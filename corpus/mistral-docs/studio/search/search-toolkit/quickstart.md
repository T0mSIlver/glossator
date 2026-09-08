---
url: https://docs.mistral.ai/studio/search/search-toolkit/quickstart
title: Quickstart
breadcrumbs: [Studio, Search, Search Toolkit]
kind: doc
locale: en
source_path: src/content/en/docs/studio/search/search-toolkit/quickstart/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# Quickstart

Build a RAG pipeline in 5 minutes: ingest documents into a vector store, then search them.

## Prerequisites {#prerequisites}

- **Python 3.12+**
- **Docker** (for running Vespa locally)
- A **Mistral API key** from [console.mistral.ai](https://console.mistral.ai/)

## Install {#install}

Install Search Toolkit with the Vespa plugin using [uv](https://docs.astral.sh/uv/):

```bash
uv add "mistralai-search-toolkit[vespa]"
```

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

## Deploy from migrations {#deploy-schema}

Deploy the schema to your local Vespa instance:

```bash
mistral-vespa migrate \
  --app-dir ./vespa/migrations \
  --config-server http://localhost:19071 \
  --query-port 8080
```

This builds the application package from your migrations in memory, deploys it, and waits until the app is ready.

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
