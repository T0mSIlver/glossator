---
url: https://docs.mistral.ai/studio/knowledge-rag/embeddings
title: Embeddings
breadcrumbs: [Studio, Embeddings]
kind: doc
locale: en
source_path: src/content/en/docs/studio/knowledge-rag/embeddings/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Embeddings

**Embeddings** are vector representations of text that capture the semantic meaning of paragraphs through their position in a high-dimensional vector space. Mistral's Embeddings API provides embeddings for text and code, which you can use for natural language processing (NLP) tasks.

![embedding_graph](https://docs.mistral.ai/img/embedding_graph.png)

Embeddings can power retrieval systems for retrieval-augmented generation, clustering for unorganized data, document classification, semantic code search, code analytics, duplicate detection, and search across raw text or code sources.

If you want a managed feature that ingests, vectorizes, and searches documents for you, use [Libraries](https://docs.mistral.ai/studio/search/libraries). If you want to search connected sources such as Google Drive or SharePoint, use [Connectors](https://docs.mistral.ai/studio/connectors).

## Services {#services}

We provide two embedding models:

- [Text embeddings](https://docs.mistral.ai/studio/knowledge-rag/embeddings/text_embeddings): embed a wide variety of text with a general-purpose embedding model.
- [Code embeddings](https://docs.mistral.ai/studio/knowledge-rag/embeddings/code_embeddings): embed code databases and repositories for code retrieval.

We cover the fundamentals of the embeddings API, including how to measure the distance between text embeddings, and explore two main use cases: clustering and classification.

### More {#more}

For a quick example and introduction on how to use embeddings for RAG, see [RAG Quickstart](https://docs.mistral.ai/studio/knowledge-rag/rag_quickstart).
