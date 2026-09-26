---
url: https://docs.mistral.ai/studio/search/search-toolkit/search-index/qdrant
title: Qdrant
breadcrumbs: [Studio, Search, Search Toolkit, Search index]
kind: doc
locale: en
source_path: src/content/en/docs/studio/search/search-toolkit/search-index/qdrant/page.mdx
source_commit: bee3023d26c331c00fa6c24bc746ef4cf5e97031
---

# Qdrant

[Qdrant](https://qdrant.tech/) is an open-source vector search engine. The Qdrant plugin integrates it as a search index backend for Search Toolkit. It implements the `VectorStoreIndex`, `NavigableIndex`, and `PatchableIndex` protocols and provides schema management for your Qdrant collections.

- **PyPI**: `mistralai-search-toolkit-plugins-qdrant` — [pypi.org/project/mistralai-search-toolkit-plugins-qdrant](https://pypi.org/project/mistralai-search-toolkit-plugins-qdrant/)
- **Source and documentation**: [github.com/qdrant-labs/mistral-qdrant-plugin](https://github.com/qdrant-labs/mistral-qdrant-plugin)

Install the plugin with `uv` or `pip`:

```bash
uv add mistralai-search-toolkit-plugins-qdrant
```

For installation steps, configuration, and usage, refer to the plugin's repository.
