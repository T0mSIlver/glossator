# Retrieval grid

## What this measures

Every one of 12 questions was run through 13 retrieval configurations, and the ranked hits of each run were kept. The question each row answers is: which index variant, which ranking weights, and reranking or not, put the documentation section that answers a question inside the top few results.

A hit counts as correct in two ways, reported separately:

- **page**: the hit's URL is one of the question's gold URLs. This is what a reader needs to reach the answer at all.
- **section**: the hit's URL *and* anchor match a gold URL and anchor. This is what a citation needs in order to deep-link.

Most markdown headings in this corpus carry no anchor (D-003a), so a question whose gold has no anchor cannot be scored at the section level. 9 of 11 answerable questions carry an anchor on every gold source and are the only ones in the section tables; the rest are page level only, and are not counted as section misses.

Unanswerable questions have no gold, so they are excluded from every recall number and reported on their own below.

Several chunks of one page are one result: the ranked list is collapsed to distinct pages (or sections) at their best rank before it is scored, so recall@k reads as "the answer was among the first k pages" rather than "among the first k chunks".

## Datasets

- Questions: `tests/fixtures/retrieval-dev.jsonl`, sha256 `f0744c029c3fee49`
- 12 questions: 2 api_reference, 2 capability, 2 cross_page, 5 single_page, 1 unanswerable
- Reranker prompt: `listwise-rerank/v1`, sha256 `257020c17044`
- Reranker model: `ministral-14b-2512`

## Configurations

| configuration | variant | weight set | rerank | ranking weights |
|---|---|---|---|---|
| `page128-shipped` | page128 | shipped | no | schema defaults |
| `page128-vector-heavy` | page128 | vector-heavy | no | `bm25_content` 0.3, `content_embedding_closeness` 8 |
| `page128-lexical-heavy` | page128 | lexical-heavy | no | `bm25_content` 3, `bm25_heading_path_max` 1, `bm25_page_title` 1, `content_embedding_closeness` 0.5, `content_embedding_cosine_similarity_score` 1 |
| `sec128-shipped` | sec128 | shipped | no | schema defaults |
| `sec128-vector-heavy` | sec128 | vector-heavy | no | `bm25_content` 0.3, `content_embedding_closeness` 8 |
| `sec128-lexical-heavy` | sec128 | lexical-heavy | no | `bm25_content` 3, `bm25_heading_path_max` 1, `bm25_page_title` 1, `content_embedding_closeness` 0.5, `content_embedding_cosine_similarity_score` 1 |
| `sec128-heading-path-off` | sec128 | heading-path-off | no | `bm25_heading_path_avg` 0, `bm25_heading_path_max` 0 |
| `sec1024-shipped` | sec1024 | shipped | no | schema defaults |
| `sec1024-vector-heavy` | sec1024 | vector-heavy | no | `bm25_content` 0.3, `content_embedding_closeness` 8 |
| `sec1024-lexical-heavy` | sec1024 | lexical-heavy | no | `bm25_content` 3, `bm25_heading_path_max` 1, `bm25_page_title` 1, `content_embedding_closeness` 0.5, `content_embedding_cosine_similarity_score` 1 |
| `sec1024-heading-path-off` | sec1024 | heading-path-off | no | `bm25_heading_path_avg` 0, `bm25_heading_path_max` 0 |
| `sec1024-shipped+rerank` | sec1024 | shipped | yes | schema defaults |
| `sec1024-vector-heavy+rerank` | sec1024 | vector-heavy | yes | `bm25_content` 0.3, `content_embedding_closeness` 8 |

Every row retrieves 10 hits.

## Results

### Page-level matching

**recall@1**

| configuration | overall | api_reference | capability | cross_page | single_page |
|---|---|---|---|---|---|
| `page128-shipped` | 0.773 | 1.000 | 0.500 | 0.750 | 0.800 |
| `page128-vector-heavy` | 0.773 | 1.000 | 0.500 | 0.750 | 0.800 |
| `page128-lexical-heavy` | 0.864 | 1.000 | 0.500 | 0.750 | 1.000 |
| `sec128-shipped` | 0.773 | 1.000 | 0.500 | 0.750 | 0.800 |
| `sec128-vector-heavy` | 0.773 | 1.000 | 0.500 | 0.750 | 0.800 |
| `sec128-lexical-heavy` | 0.682 | 1.000 | 0.000 | 0.750 | 0.800 |
| `sec128-heading-path-off` | 0.773 | 1.000 | 0.500 | 0.750 | 0.800 |
| `sec1024-shipped` | 0.682 | 1.000 | 0.000 | 0.750 | 0.800 |
| `sec1024-vector-heavy` | 0.682 | 1.000 | 0.000 | 0.750 | 0.800 |
| `sec1024-lexical-heavy` | 0.682 | 1.000 | 0.000 | 0.750 | 0.800 |
| `sec1024-heading-path-off` | 0.773 | 1.000 | 0.500 | 0.750 | 0.800 |
| `sec1024-shipped+rerank` | 0.773 | 0.500 | 1.000 | 0.750 | 0.800 |
| `sec1024-vector-heavy+rerank` | 0.864 | 1.000 | 1.000 | 0.750 | 0.800 |

**recall@3**

| configuration | overall | api_reference | capability | cross_page | single_page |
|---|---|---|---|---|---|
| `page128-shipped` | 0.909 | 1.000 | 1.000 | 1.000 | 0.800 |
| `page128-vector-heavy` | 0.909 | 1.000 | 1.000 | 1.000 | 0.800 |
| `page128-lexical-heavy` | 0.955 | 1.000 | 1.000 | 0.750 | 1.000 |
| `sec128-shipped` | 0.909 | 1.000 | 0.500 | 1.000 | 1.000 |
| `sec128-vector-heavy` | 0.909 | 1.000 | 0.500 | 1.000 | 1.000 |
| `sec128-lexical-heavy` | 0.818 | 1.000 | 0.500 | 1.000 | 0.800 |
| `sec128-heading-path-off` | 0.909 | 1.000 | 0.500 | 1.000 | 1.000 |
| `sec1024-shipped` | 0.818 | 1.000 | 0.500 | 1.000 | 0.800 |
| `sec1024-vector-heavy` | 0.818 | 1.000 | 0.500 | 1.000 | 0.800 |
| `sec1024-lexical-heavy` | 0.818 | 1.000 | 0.500 | 1.000 | 0.800 |
| `sec1024-heading-path-off` | 0.909 | 1.000 | 0.500 | 1.000 | 1.000 |
| `sec1024-shipped+rerank` | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| `sec1024-vector-heavy+rerank` | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

**recall@5**

| configuration | overall | api_reference | capability | cross_page | single_page |
|---|---|---|---|---|---|
| `page128-shipped` | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| `page128-vector-heavy` | 0.909 | 1.000 | 1.000 | 1.000 | 0.800 |
| `page128-lexical-heavy` | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| `sec128-shipped` | 0.909 | 1.000 | 0.500 | 1.000 | 1.000 |
| `sec128-vector-heavy` | 0.909 | 1.000 | 0.500 | 1.000 | 1.000 |
| `sec128-lexical-heavy` | 0.818 | 1.000 | 0.500 | 1.000 | 0.800 |
| `sec128-heading-path-off` | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| `sec1024-shipped` | 0.818 | 1.000 | 0.500 | 1.000 | 0.800 |
| `sec1024-vector-heavy` | 0.818 | 1.000 | 0.500 | 1.000 | 0.800 |
| `sec1024-lexical-heavy` | 0.818 | 1.000 | 0.500 | 1.000 | 0.800 |
| `sec1024-heading-path-off` | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| `sec1024-shipped+rerank` | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| `sec1024-vector-heavy+rerank` | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

**recall@10**

| configuration | overall | api_reference | capability | cross_page | single_page |
|---|---|---|---|---|---|
| `page128-shipped` | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| `page128-vector-heavy` | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| `page128-lexical-heavy` | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| `sec128-shipped` | 0.909 | 1.000 | 0.500 | 1.000 | 1.000 |
| `sec128-vector-heavy` | 0.909 | 1.000 | 0.500 | 1.000 | 1.000 |
| `sec128-lexical-heavy` | 0.909 | 1.000 | 1.000 | 1.000 | 0.800 |
| `sec128-heading-path-off` | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| `sec1024-shipped` | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| `sec1024-vector-heavy` | 0.909 | 1.000 | 0.500 | 1.000 | 1.000 |
| `sec1024-lexical-heavy` | 0.909 | 1.000 | 1.000 | 1.000 | 0.800 |
| `sec1024-heading-path-off` | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| `sec1024-shipped+rerank` | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| `sec1024-vector-heavy+rerank` | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

**mrr**

| configuration | overall | api_reference | capability | cross_page | single_page |
|---|---|---|---|---|---|
| `page128-shipped` | 0.882 | 1.000 | 0.750 | 1.000 | 0.840 |
| `page128-vector-heavy` | 0.877 | 1.000 | 0.750 | 1.000 | 0.829 |
| `page128-lexical-heavy` | 0.955 | 1.000 | 0.750 | 1.000 | 1.000 |
| `sec128-shipped` | 0.864 | 1.000 | 0.500 | 1.000 | 0.900 |
| `sec128-vector-heavy` | 0.864 | 1.000 | 0.500 | 1.000 | 0.900 |
| `sec128-lexical-heavy` | 0.786 | 1.000 | 0.321 | 1.000 | 0.800 |
| `sec128-heading-path-off` | 0.882 | 1.000 | 0.600 | 1.000 | 0.900 |
| `sec1024-shipped` | 0.801 | 1.000 | 0.321 | 1.000 | 0.833 |
| `sec1024-vector-heavy` | 0.788 | 1.000 | 0.250 | 1.000 | 0.833 |
| `sec1024-lexical-heavy` | 0.788 | 1.000 | 0.333 | 1.000 | 0.800 |
| `sec1024-heading-path-off` | 0.886 | 1.000 | 0.625 | 1.000 | 0.900 |
| `sec1024-shipped+rerank` | 0.879 | 0.667 | 1.000 | 1.000 | 0.867 |
| `sec1024-vector-heavy+rerank` | 0.939 | 1.000 | 1.000 | 1.000 | 0.867 |

**ndcg@10**

| configuration | overall | api_reference | capability | cross_page | single_page |
|---|---|---|---|---|---|
| `page128-shipped` | 0.903 | 1.000 | 0.816 | 0.960 | 0.877 |
| `page128-vector-heavy` | 0.906 | 1.000 | 0.816 | 1.000 | 0.867 |
| `page128-lexical-heavy` | 0.955 | 1.000 | 0.816 | 0.939 | 1.000 |
| `sec128-shipped` | 0.875 | 1.000 | 0.500 | 1.000 | 0.926 |
| `sec128-vector-heavy` | 0.868 | 1.000 | 0.500 | 0.960 | 0.926 |
| `sec128-lexical-heavy` | 0.815 | 1.000 | 0.482 | 1.000 | 0.800 |
| `sec128-heading-path-off` | 0.911 | 1.000 | 0.693 | 1.000 | 0.926 |
| `sec1024-shipped` | 0.847 | 1.000 | 0.482 | 1.000 | 0.871 |
| `sec1024-vector-heavy` | 0.810 | 1.000 | 0.316 | 0.960 | 0.871 |
| `sec1024-lexical-heavy` | 0.817 | 1.000 | 0.494 | 1.000 | 0.800 |
| `sec1024-heading-path-off` | 0.915 | 1.000 | 0.715 | 1.000 | 0.926 |
| `sec1024-shipped+rerank` | 0.902 | 0.750 | 1.000 | 0.960 | 0.900 |
| `sec1024-vector-heavy+rerank` | 0.955 | 1.000 | 1.000 | 1.000 | 0.900 |

Question counts per column: overall 11, api_reference 2, capability 2, cross_page 2, single_page 5.

### Section-level matching

**recall@1**

| configuration | overall | api_reference | capability | cross_page | single_page |
|---|---|---|---|---|---|
| `page128-shipped` | 0.000 | 0.000 | 0.000 | -- | 0.000 |
| `page128-vector-heavy` | 0.000 | 0.000 | 0.000 | -- | 0.000 |
| `page128-lexical-heavy` | 0.000 | 0.000 | 0.000 | -- | 0.000 |
| `sec128-shipped` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec128-vector-heavy` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec128-lexical-heavy` | 0.556 | 1.000 | 0.000 | -- | 0.600 |
| `sec128-heading-path-off` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-shipped` | 0.556 | 1.000 | 0.000 | -- | 0.600 |
| `sec1024-vector-heavy` | 0.556 | 1.000 | 0.000 | -- | 0.600 |
| `sec1024-lexical-heavy` | 0.556 | 1.000 | 0.000 | -- | 0.600 |
| `sec1024-heading-path-off` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-shipped+rerank` | 0.556 | 0.500 | 0.500 | -- | 0.600 |
| `sec1024-vector-heavy+rerank` | 0.667 | 1.000 | 0.500 | -- | 0.600 |

**recall@3**

| configuration | overall | api_reference | capability | cross_page | single_page |
|---|---|---|---|---|---|
| `page128-shipped` | 0.000 | 0.000 | 0.000 | -- | 0.000 |
| `page128-vector-heavy` | 0.000 | 0.000 | 0.000 | -- | 0.000 |
| `page128-lexical-heavy` | 0.000 | 0.000 | 0.000 | -- | 0.000 |
| `sec128-shipped` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec128-vector-heavy` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec128-lexical-heavy` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec128-heading-path-off` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-shipped` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-vector-heavy` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-lexical-heavy` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-heading-path-off` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-shipped+rerank` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-vector-heavy+rerank` | 0.667 | 1.000 | 0.500 | -- | 0.600 |

**recall@5**

| configuration | overall | api_reference | capability | cross_page | single_page |
|---|---|---|---|---|---|
| `page128-shipped` | 0.000 | 0.000 | 0.000 | -- | 0.000 |
| `page128-vector-heavy` | 0.000 | 0.000 | 0.000 | -- | 0.000 |
| `page128-lexical-heavy` | 0.000 | 0.000 | 0.000 | -- | 0.000 |
| `sec128-shipped` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec128-vector-heavy` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec128-lexical-heavy` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec128-heading-path-off` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-shipped` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-vector-heavy` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-lexical-heavy` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-heading-path-off` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-shipped+rerank` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-vector-heavy+rerank` | 0.667 | 1.000 | 0.500 | -- | 0.600 |

**recall@10**

| configuration | overall | api_reference | capability | cross_page | single_page |
|---|---|---|---|---|---|
| `page128-shipped` | 0.000 | 0.000 | 0.000 | -- | 0.000 |
| `page128-vector-heavy` | 0.000 | 0.000 | 0.000 | -- | 0.000 |
| `page128-lexical-heavy` | 0.000 | 0.000 | 0.000 | -- | 0.000 |
| `sec128-shipped` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec128-vector-heavy` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec128-lexical-heavy` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec128-heading-path-off` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-shipped` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-vector-heavy` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-lexical-heavy` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-heading-path-off` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-shipped+rerank` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-vector-heavy+rerank` | 0.667 | 1.000 | 0.500 | -- | 0.600 |

**mrr**

| configuration | overall | api_reference | capability | cross_page | single_page |
|---|---|---|---|---|---|
| `page128-shipped` | 0.000 | 0.000 | 0.000 | -- | 0.000 |
| `page128-vector-heavy` | 0.000 | 0.000 | 0.000 | -- | 0.000 |
| `page128-lexical-heavy` | 0.000 | 0.000 | 0.000 | -- | 0.000 |
| `sec128-shipped` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec128-vector-heavy` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec128-lexical-heavy` | 0.593 | 1.000 | 0.167 | -- | 0.600 |
| `sec128-heading-path-off` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-shipped` | 0.611 | 1.000 | 0.250 | -- | 0.600 |
| `sec1024-vector-heavy` | 0.611 | 1.000 | 0.250 | -- | 0.600 |
| `sec1024-lexical-heavy` | 0.593 | 1.000 | 0.167 | -- | 0.600 |
| `sec1024-heading-path-off` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-shipped+rerank` | 0.593 | 0.667 | 0.500 | -- | 0.600 |
| `sec1024-vector-heavy+rerank` | 0.667 | 1.000 | 0.500 | -- | 0.600 |

**ndcg@10**

| configuration | overall | api_reference | capability | cross_page | single_page |
|---|---|---|---|---|---|
| `page128-shipped` | 0.000 | 0.000 | 0.000 | -- | 0.000 |
| `page128-vector-heavy` | 0.000 | 0.000 | 0.000 | -- | 0.000 |
| `page128-lexical-heavy` | 0.000 | 0.000 | 0.000 | -- | 0.000 |
| `sec128-shipped` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec128-vector-heavy` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec128-lexical-heavy` | 0.611 | 1.000 | 0.250 | -- | 0.600 |
| `sec128-heading-path-off` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-shipped` | 0.626 | 1.000 | 0.316 | -- | 0.600 |
| `sec1024-vector-heavy` | 0.626 | 1.000 | 0.316 | -- | 0.600 |
| `sec1024-lexical-heavy` | 0.611 | 1.000 | 0.250 | -- | 0.600 |
| `sec1024-heading-path-off` | 0.667 | 1.000 | 0.500 | -- | 0.600 |
| `sec1024-shipped+rerank` | 0.611 | 0.750 | 0.500 | -- | 0.600 |
| `sec1024-vector-heavy+rerank` | 0.667 | 1.000 | 0.500 | -- | 0.600 |

Question counts per column: overall 9, api_reference 2, capability 2, cross_page 0, single_page 5.

## Latency, cost and failures

| configuration | median ms | p90 ms | rerank calls | applied | fell back | budget skipped | rerank USD | errors |
|---|---|---|---|---|---|---|---|---|
| `page128-shipped` | 8 | 9 | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| `page128-vector-heavy` | 8 | 9 | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| `page128-lexical-heavy` | 8 | 8 | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| `sec128-shipped` | 6 | 8 | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| `sec128-vector-heavy` | 6 | 7 | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| `sec128-lexical-heavy` | 6 | 6 | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| `sec128-heading-path-off` | 7 | 7 | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| `sec1024-shipped` | 9 | 10 | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| `sec1024-vector-heavy` | 8 | 9 | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| `sec1024-lexical-heavy` | 8 | 9 | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| `sec1024-heading-path-off` | 8 | 9 | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| `sec1024-shipped+rerank` | 3899 | 4376 | 12 | 12 | 0 | 0 | 0.00885 | 0 |
| `sec1024-vector-heavy+rerank` | 5747 | 7940 | 12 | 10 | 2 | 0 | 0.00908 | 0 |

Latency is wall-clock for one question through one configuration: the Vespa round trip and, where it ran, the reranker's model call. The query's embedding is not in it -- a question is embedded once per embedding model and the vector is reused across every configuration that shares it, so charging that call to one configuration and not the others would be arbitrary.

## Unanswerable questions

The dataset holds 1 question with no gold source, so they carry no recall. What they measure is whether the engine returns something confident anyway. Across every configuration, 13 of 13 runs returned a top hit, and 0 were reported as having no lexical footing.

| question | configuration | top hit | footing |
|---|---|---|---|
| What is the maximum number of tool calls a single assistant message may contain? | `page128-shipped` | https://docs.mistral.ai/capabilities/function-calling | not checked |
| What is the maximum number of tool calls a single assistant message may contain? | `page128-vector-heavy` | https://docs.mistral.ai/capabilities/function-calling | not checked |
| What is the maximum number of tool calls a single assistant message may contain? | `page128-lexical-heavy` | https://docs.mistral.ai/api/endpoint/chat-completions | not checked |
| What is the maximum number of tool calls a single assistant message may contain? | `sec128-shipped` | https://docs.mistral.ai/capabilities/function-calling#parallel-tool-calls | not checked |
| What is the maximum number of tool calls a single assistant message may contain? | `sec128-vector-heavy` | https://docs.mistral.ai/capabilities/function-calling#parallel-tool-calls | not checked |
| What is the maximum number of tool calls a single assistant message may contain? | `sec128-lexical-heavy` | https://docs.mistral.ai/capabilities/function-calling#parallel-tool-calls | not checked |
| What is the maximum number of tool calls a single assistant message may contain? | `sec128-heading-path-off` | https://docs.mistral.ai/resources/known-limitations#function-calling | not checked |
| What is the maximum number of tool calls a single assistant message may contain? | `sec1024-shipped` | https://docs.mistral.ai/capabilities/function-calling#parallel-tool-calls | not checked |
| What is the maximum number of tool calls a single assistant message may contain? | `sec1024-vector-heavy` | https://docs.mistral.ai/capabilities/function-calling#parallel-tool-calls | not checked |
| What is the maximum number of tool calls a single assistant message may contain? | `sec1024-lexical-heavy` | https://docs.mistral.ai/capabilities/function-calling#parallel-tool-calls | not checked |
| What is the maximum number of tool calls a single assistant message may contain? | `sec1024-heading-path-off` | https://docs.mistral.ai/resources/known-limitations#function-calling | not checked |
| What is the maximum number of tool calls a single assistant message may contain? | `sec1024-shipped+rerank` | https://docs.mistral.ai/resources/known-limitations#function-calling | not checked |
| What is the maximum number of tool calls a single assistant message may contain? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/resources/known-limitations#function-calling | not checked |

## Figures

Regenerated from `metrics.json` by `make eval-report run=<dir>`.

- `figures/recall-at-k-page.svg`, `figures/recall-at-k-section.svg`: recall against k, one line per configuration
- `figures/best-two-by-type-page.svg`, `figures/best-two-by-type-section.svg`: recall@5 per question type, for the two leading configurations

## Conclusion

At the page level, over the 11 questions that matching can score, `page128-lexical-heavy` leads on recall@5 with 1.000, +0.000 over `page128-shipped` (1.000); 6 configurations are tied at that number, so the lead is the alphabetical tie-break and not a difference the dataset can see.

At the section level, over the 9 questions that matching can score, `sec1024-heading-path-off` leads on recall@5 with 0.667, +0.000 over `sec1024-lexical-heavy` (0.667); 10 configurations are tied at that number, so the lead is the alphabetical tie-break and not a difference the dataset can see.

The reranker made 24 calls for $0.0179, about $0.000747 a call, and its ranking was applied 22 of those times; the other 2 returned a ranking the reordering could not use and fell back to retrieval order, which the per-question records name.

This feeds D-012a: the shipped ranking weights are a starting point and the winning row above is what replaces them, and D-015: whether one listwise call buys enough ordering to be worth its latency in the serving path.
