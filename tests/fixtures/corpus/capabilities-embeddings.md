---
url: https://docs.mistral.ai/capabilities/embeddings
title: Embeddings
breadcrumbs:
  - Capabilities
  - Embeddings
kind: doc
locale: en
source_path: src/content/en/docs/capabilities/embeddings/page.mdx
source_commit: 2e094f7
---

# Embeddings

An embedding turns a piece of text into a vector of numbers whose geometry
reflects meaning: texts about the same thing land near each other, regardless of
the words they use. That is what makes semantic search work where keyword search
fails.

## The models {#the-models}

`mistral-embed` returns 1024-dimensional vectors and is the default choice. Two
reduced-dimension variants trade a little quality for a smaller index:

| Model | Dimensions | Max input tokens |
| --- | --- | --- |
| `mistral-embed` | 1024 | 8192 |
| `mistral-embed-dim256-2510` | 256 | 8192 |
| `mistral-embed-dim128-2510` | 128 | 8192 |

The dimension is a property of the stored index, not of a request: changing it
means re-embedding the whole corpus, so decide before you build the index rather
than after.

## Embedding documents {#embedding-documents}

Send a batch of inputs in one request. Batching is what keeps throughput usable;
a request per document spends most of its time in round trips.

```python
response = client.embeddings.create(
    model="mistral-embed",
    inputs=["How do I stream a response?", "What is a tool call?"],
)
vectors = [item.embedding for item in response.data]
```

The response carries a `usage.total_tokens` field. Embedding is billed per input
token, so this is the number to log if you want to know what an index cost.

## Chunking {#chunking}

Embed passages, not whole documents. A vector is a single point, and a page that
covers five topics lands between all five, close to none of them.

For technical documentation, chunking on the page's own headings works better than
chunking on a fixed character count: a heading is the author's own statement about
where one topic ends. Keep chunks under a few hundred tokens, and prefix each one
with its heading path so a chunk taken from the middle of a page still says what
it is about.

## Similarity {#similarity}

Compare vectors with cosine similarity. The embeddings are not normalised to unit
length, so use a cosine implementation rather than a dot product.

```python
import numpy as np

def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

A similarity score is only meaningful relative to other scores from the same
model. There is no absolute threshold that separates relevant from irrelevant, so
rank and take the top k rather than filtering on a fixed cut-off.

## Hybrid retrieval {#hybrid-retrieval}

Dense retrieval is weak exactly where keyword search is strong: exact identifiers,
version numbers, error codes, rare product names. Run both and combine them.

The simplest combination that works is a weighted sum of a BM25 score and a vector
similarity score, computed in the search engine so that neither list has to be
truncated before the other is consulted.
