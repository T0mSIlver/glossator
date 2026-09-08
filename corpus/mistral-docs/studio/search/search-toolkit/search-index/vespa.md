---
url: https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa
title: Vespa
breadcrumbs: [Studio, Search, Search Toolkit, Search index]
kind: doc
locale: en
source_path: src/content/en/docs/studio/search/search-toolkit/search-index/vespa/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# Vespa

## Manage and deploy Vespa applications {#manage-and-deploy-vespa-applications}

Build and operate Vespa applications with the Search Toolkit plugin. Define schemas via Python migrations, configure ranking and query profiles, deploy with the `mistral-vespa` CLI, and manage production clusters.

## Getting started {#getting-started}

Follow these guides to build and deploy a Vespa application:

| Guide | Purpose |
|---|---|
| **[Anatomy of an Application](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/anatomy)** | Understand application packages, schemas, fields, ranking profiles, query profiles, and migrations |
| **[Manage Schema](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/migrations)** | Create and evolve schemas using Python migrations |
| **[Manage Ranking](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/query-profiles)** | Configure ranking at query time without schema changes |
| **[Local Development](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/local-development)** | Full local development loop: create, deploy, feed, query, iterate |
| **[Deploy and Operate](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/operations)** | Production configuration, health checks, monitoring |
| **[CLI Reference](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli)** | mistral-vespa command reference |

## Use Vespa as a search backend {#using-vespa-as-a-search-backend}

To use Vespa as a search backend in your Search Toolkit pipelines, see [Search index](https://docs.mistral.ai/studio/search/search-toolkit/search-index).

## Installation {#installation}

```bash
uv add "mistralai-search-toolkit[vespa]"
```
