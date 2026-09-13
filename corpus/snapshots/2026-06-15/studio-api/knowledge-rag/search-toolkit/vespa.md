---
url: https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/vespa
title: Manage and deploy Vespa applications
breadcrumbs: [Studio, Knowledge & RAG, Search Toolkit]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/knowledge-rag/search-toolkit/vespa/page.mdx
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
---

# Manage and deploy Vespa applications

## Manage and Deploy Vespa Applications {#manage-and-deploy-vespa-applications}

Build and operate Vespa applications with the Search Toolkit plugin. Define schemas via Python migrations, configure ranking and query profiles, deploy with the `mistral-vespa` CLI, and manage production clusters.

## Getting Started {#getting-started}

Follow these guides to build and deploy a Vespa application:

| Guide | Purpose |
|---|---|
| **[Anatomy of an Application](https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/vespa/anatomy)** | Understand application packages, schemas, fields, ranking profiles, query profiles, and migrations |
| **[Manage Schema](https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/vespa/migrations)** | Create and evolve schemas using Python migrations |
| **[Manage Ranking](https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/vespa/query-profiles)** | Configure ranking at query time without schema changes |
| **[Local Development](https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/vespa/local-development)** | Full local development loop: create, deploy, feed, query, iterate |
| **[Deploy and Operate](https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/vespa/operations)** | Production configuration, health checks, monitoring |
| **[CLI Reference](https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/vespa/cli)** | mistral-vespa command reference |

## Using Vespa as a Search Backend {#using-vespa-as-a-search-backend}

To use Vespa as a search backend in your Search Toolkit pipelines, see **[Search Index](https://docs.mistral.ai/studio-api/knowledge-rag/search-toolkit/search-index)**.

## Installation {#installation}

```bash
uv add "mistralai-search-toolkit[vespa]"
```
