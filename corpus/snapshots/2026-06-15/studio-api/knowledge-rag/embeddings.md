---
url: https://docs.mistral.ai/studio-api/knowledge-rag/embeddings
title: Embeddings
breadcrumbs: [Studio, Knowledge & RAG]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/knowledge-rag/embeddings/page.mdx
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
---

# Embeddings

**Embeddings** are **vector representations** of text that capture the **semantic meaning** of paragraphs through their position in a high-dimensional vector space. Mistral AI's Embeddings API offers cutting-edge, state-of-the-art embeddings for text and code, which can be used for many natural language processing (NLP) tasks.

![embedding_graph](https://docs.mistral.ai/img/embedding_graph.png)

Among the vast array of use cases for embeddings are **retrieval systems** powering **retrieval-augmented generation**, **clustering** of unorganized data, **classification** of vast amounts of documents, **semantic code search** to explore databases and repositories, **code analytics**, **duplicate detection**, and various kinds of search when dealing with multiple sources of raw text or code.

## Services {#services}

We provide two state-of-the-art embeddings:
- [Text Embeddings](https://docs.mistral.ai/studio-api/knowledge-rag/embeddings/text_embeddings): For embedding a wide variety of text, a general-purpose, efficient embedding model.
- [Code Embeddings](https://docs.mistral.ai/studio-api/knowledge-rag/embeddings/code_embeddings): Specially designed for code, perfect for embedding code databases, repositories, and powering coding assistants with state-of-the-art retrieval.

We will cover the fundamentals of the embeddings API, including how to measure the distance between text embeddings, and explore two main use cases: clustering and classification.

### More {#services}

For a quick example and introduction on how to leverage embeddings for RAG (Retrieval-Augmented Generation), check out our [RAG Quickstart](https://docs.mistral.ai/studio-api/knowledge-rag/embeddings/rag_quickstart).
