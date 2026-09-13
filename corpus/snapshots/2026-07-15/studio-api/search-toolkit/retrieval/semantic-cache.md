---
url: https://docs.mistral.ai/studio-api/search-toolkit/retrieval/semantic-cache
title: Semantic cache
breadcrumbs: [Studio, Search Toolkit, Retrieval]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/search-toolkit/retrieval/semantic-cache/page.mdx
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
---

# Semantic cache

The semantic cache matches queries by meaning rather than exact string matching. When a query is semantically similar to a previously cached one, the cache returns stored results and skips embedding, retrieval, preprocessing, and reranking.

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

## See also {#see-also}

- [Retrieval overview](https://docs.mistral.ai/studio-api/search-toolkit/retrieval): retrieval pipeline architecture
- [Retrievers](https://docs.mistral.ai/studio-api/search-toolkit/retrieval/retrievers): vector search
- [Rerankers](https://docs.mistral.ai/studio-api/search-toolkit/retrieval/rerankers): refine results after retrieval
- [Query preprocessing](https://docs.mistral.ai/studio-api/search-toolkit/retrieval/preprocessing): improve queries before retrieval
