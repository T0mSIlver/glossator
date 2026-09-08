---
url: https://docs.mistral.ai/studio/search/search-toolkit
title: Search Toolkit
breadcrumbs: [Studio, Search]
kind: doc
locale: en
source_path: src/content/en/docs/studio/search/search-toolkit/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---
# Search Toolkit {#search-toolkit}

Search Toolkit builds ingestion and retrieval pipelines for application data.

## Pipeline components {#pipeline-components}

An ingestion pipeline loads files, extracts text, splits documents, embeds chunks, and stores them in an index. The operations are asynchronous, and each document needs a stable identifier before indexing. Metadata travels with each chunk and can hold a URL, heading path, or tenant field. Frozen document models cannot be mutated after construction; create a copy when an enrichment step adds metadata. A vector store requires an embedder, while a keyword-only store does not. Checkpoints can preserve extractor output when processing long documents. The same pipeline accepts local filesystem loaders and optional cloud storage loaders without changing later components.

## Retrieval components {#retrieval-components}

A query engine coordinates rewriting, retrieval, and reranking. Vector retrieval embeds the query and asks a compatible index for nearest neighbors. Keyword retrieval needs an index that implements the keyword store contract. Applications can combine retrievers and fuse their result lists before a reranker evaluates the candidates. Retrieval calls are asynchronous and can include content and metadata in each result. Context objects carry request-specific headers and tenant information without adding backend-specific keyword arguments to the query engine. Cache repeated searches when evaluation code issues identical queries across experiment rows.
