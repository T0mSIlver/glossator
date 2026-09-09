# Retrieval grid

## What this measures

Every one of 294 questions was run through 13 retrieval configurations, and the ranked hits of each run were kept. The question each row answers is: which index variant, which ranking weights, and reranking or not, put the documentation section that answers a question inside the top few results.

A hit counts as correct in two ways, reported separately:

- **page**: the hit's URL is one of the question's gold URLs. This is what a reader needs to reach the answer at all.
- **section**: the hit's URL *and* anchor match a gold URL and anchor. This is what a citation needs in order to deep-link.

Most markdown headings in this corpus carry no anchor (D-003a), so a question whose gold has no anchor cannot be scored at the section level. 142 of 244 answerable questions carry an anchor on every gold source and are the only ones in the section tables; the rest are page level only, and are not counted as section misses.

Unanswerable questions have no gold, so they are excluded from every recall number and reported on their own below.

Several chunks of one page are one result: the ranked list is collapsed to distinct pages (or sections) at their best rank before it is scored, so recall@k reads as "the answer was among the first k pages" rather than "among the first k chunks".

## Datasets

- Questions: `eval/dev.jsonl`, sha256 `acf3c2e148f1aa40`
- 294 questions: 50 api_reference, 44 capability, 50 cross_page, 50 post_cutoff, 50 single_page, 50 unanswerable
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

Every row retrieves 20 hits.

## Results

### Page-level matching

**recall@1**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `page128-shipped` | 0.619 | 0.840 | 0.318 | 0.360 | 0.840 | 0.700 |
| `page128-vector-heavy` | 0.607 | 0.860 | 0.295 | 0.360 | 0.820 | 0.660 |
| `page128-lexical-heavy` | 0.609 | 0.780 | 0.364 | 0.370 | 0.860 | 0.640 |
| `sec128-shipped` | 0.619 | 0.640 | 0.295 | 0.320 | 0.920 | 0.880 |
| `sec128-vector-heavy` | 0.605 | 0.680 | 0.227 | 0.310 | 0.920 | 0.840 |
| `sec128-lexical-heavy` | 0.594 | 0.580 | 0.330 | 0.310 | 0.920 | 0.800 |
| `sec128-heading-path-off` | 0.617 | 0.600 | 0.375 | 0.300 | 0.920 | 0.860 |
| `sec1024-shipped` | 0.592 | 0.620 | 0.273 | 0.330 | 0.920 | 0.780 |
| `sec1024-vector-heavy` | 0.596 | 0.640 | 0.193 | 0.320 | 0.920 | 0.860 |
| `sec1024-lexical-heavy` | 0.584 | 0.540 | 0.330 | 0.320 | 0.920 | 0.780 |
| `sec1024-heading-path-off` | 0.600 | 0.520 | 0.386 | 0.330 | 0.920 | 0.820 |
| `sec1024-shipped+rerank` | 0.703 | 0.800 | 0.614 | 0.390 | 0.880 | 0.820 |
| `sec1024-vector-heavy+rerank` | 0.711 | 0.900 | 0.511 | 0.380 | 0.880 | 0.860 |

**recall@3**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `page128-shipped` | 0.840 | 0.920 | 0.625 | 0.750 | 0.960 | 0.920 |
| `page128-vector-heavy` | 0.842 | 0.920 | 0.625 | 0.760 | 0.980 | 0.900 |
| `page128-lexical-heavy` | 0.836 | 0.880 | 0.705 | 0.740 | 0.960 | 0.880 |
| `sec128-shipped` | 0.797 | 0.780 | 0.580 | 0.680 | 0.940 | 0.980 |
| `sec128-vector-heavy` | 0.826 | 0.960 | 0.534 | 0.680 | 0.960 | 0.960 |
| `sec128-lexical-heavy` | 0.787 | 0.720 | 0.614 | 0.680 | 0.940 | 0.960 |
| `sec128-heading-path-off` | 0.820 | 0.780 | 0.682 | 0.700 | 0.960 | 0.960 |
| `sec1024-shipped` | 0.783 | 0.740 | 0.557 | 0.690 | 0.940 | 0.960 |
| `sec1024-vector-heavy` | 0.760 | 0.740 | 0.432 | 0.690 | 0.940 | 0.960 |
| `sec1024-lexical-heavy` | 0.791 | 0.740 | 0.614 | 0.680 | 0.940 | 0.960 |
| `sec1024-heading-path-off` | 0.811 | 0.740 | 0.682 | 0.720 | 0.940 | 0.960 |
| `sec1024-shipped+rerank` | 0.875 | 0.860 | 0.761 | 0.800 | 0.960 | 0.980 |
| `sec1024-vector-heavy+rerank` | 0.889 | 0.960 | 0.705 | 0.800 | 0.960 | 1.000 |

**recall@5**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `page128-shipped` | 0.900 | 0.920 | 0.750 | 0.850 | 1.000 | 0.960 |
| `page128-vector-heavy` | 0.908 | 0.920 | 0.784 | 0.860 | 1.000 | 0.960 |
| `page128-lexical-heavy` | 0.895 | 0.900 | 0.818 | 0.850 | 0.960 | 0.940 |
| `sec128-shipped` | 0.871 | 0.860 | 0.727 | 0.790 | 0.960 | 1.000 |
| `sec128-vector-heavy` | 0.879 | 0.960 | 0.670 | 0.780 | 0.960 | 1.000 |
| `sec128-lexical-heavy` | 0.859 | 0.740 | 0.784 | 0.800 | 0.960 | 1.000 |
| `sec128-heading-path-off` | 0.885 | 0.840 | 0.830 | 0.790 | 0.960 | 1.000 |
| `sec1024-shipped` | 0.861 | 0.800 | 0.750 | 0.780 | 0.960 | 1.000 |
| `sec1024-vector-heavy` | 0.863 | 0.900 | 0.659 | 0.770 | 0.960 | 1.000 |
| `sec1024-lexical-heavy` | 0.859 | 0.740 | 0.784 | 0.800 | 0.960 | 1.000 |
| `sec1024-heading-path-off` | 0.869 | 0.760 | 0.841 | 0.780 | 0.960 | 1.000 |
| `sec1024-shipped+rerank` | 0.895 | 0.860 | 0.795 | 0.850 | 0.960 | 1.000 |
| `sec1024-vector-heavy+rerank` | 0.920 | 0.980 | 0.773 | 0.870 | 0.960 | 1.000 |

**recall@10**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `page128-shipped` | 0.959 | 0.920 | 0.932 | 0.940 | 1.000 | 1.000 |
| `page128-vector-heavy` | 0.965 | 0.940 | 0.955 | 0.950 | 1.000 | 0.980 |
| `page128-lexical-heavy` | 0.949 | 0.920 | 0.932 | 0.930 | 1.000 | 0.960 |
| `sec128-shipped` | 0.941 | 0.980 | 0.852 | 0.900 | 0.960 | 1.000 |
| `sec128-vector-heavy` | 0.920 | 0.980 | 0.773 | 0.870 | 0.960 | 1.000 |
| `sec128-lexical-heavy` | 0.895 | 0.780 | 0.864 | 0.870 | 0.960 | 1.000 |
| `sec128-heading-path-off` | 0.947 | 0.960 | 0.909 | 0.900 | 0.960 | 1.000 |
| `sec1024-shipped` | 0.936 | 0.920 | 0.886 | 0.890 | 0.980 | 1.000 |
| `sec1024-vector-heavy` | 0.926 | 0.980 | 0.784 | 0.870 | 0.980 | 1.000 |
| `sec1024-lexical-heavy` | 0.900 | 0.780 | 0.886 | 0.870 | 0.960 | 1.000 |
| `sec1024-heading-path-off` | 0.916 | 0.820 | 0.909 | 0.890 | 0.960 | 1.000 |
| `sec1024-shipped+rerank` | 0.939 | 0.920 | 0.886 | 0.900 | 0.980 | 1.000 |
| `sec1024-vector-heavy+rerank` | 0.934 | 0.980 | 0.784 | 0.910 | 0.980 | 1.000 |

**mrr**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `page128-shipped` | 0.816 | 0.872 | 0.647 | 0.821 | 0.906 | 0.816 |
| `page128-vector-heavy` | 0.811 | 0.888 | 0.628 | 0.820 | 0.902 | 0.797 |
| `page128-lexical-heavy` | 0.807 | 0.831 | 0.672 | 0.828 | 0.911 | 0.775 |
| `sec128-shipped` | 0.791 | 0.737 | 0.581 | 0.757 | 0.932 | 0.924 |
| `sec128-vector-heavy` | 0.789 | 0.803 | 0.527 | 0.747 | 0.933 | 0.902 |
| `sec128-lexical-heavy` | 0.767 | 0.654 | 0.608 | 0.741 | 0.932 | 0.882 |
| `sec128-heading-path-off` | 0.794 | 0.710 | 0.654 | 0.743 | 0.933 | 0.913 |
| `sec1024-shipped` | 0.771 | 0.700 | 0.570 | 0.757 | 0.934 | 0.872 |
| `sec1024-vector-heavy` | 0.774 | 0.736 | 0.501 | 0.754 | 0.933 | 0.912 |
| `sec1024-lexical-heavy` | 0.765 | 0.636 | 0.623 | 0.747 | 0.932 | 0.869 |
| `sec1024-heading-path-off` | 0.786 | 0.647 | 0.679 | 0.766 | 0.932 | 0.895 |
| `sec1024-shipped+rerank` | 0.868 | 0.834 | 0.829 | 0.858 | 0.915 | 0.901 |
| `sec1024-vector-heavy+rerank` | 0.880 | 0.935 | 0.744 | 0.867 | 0.912 | 0.927 |

**ndcg@10**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `page128-shipped` | 0.838 | 0.883 | 0.684 | 0.813 | 0.929 | 0.861 |
| `page128-vector-heavy` | 0.836 | 0.900 | 0.673 | 0.818 | 0.927 | 0.842 |
| `page128-lexical-heavy` | 0.829 | 0.853 | 0.718 | 0.811 | 0.932 | 0.819 |
| `sec128-shipped` | 0.813 | 0.794 | 0.616 | 0.748 | 0.939 | 0.943 |
| `sec128-vector-heavy` | 0.803 | 0.848 | 0.543 | 0.726 | 0.940 | 0.927 |
| `sec128-lexical-heavy` | 0.786 | 0.685 | 0.645 | 0.731 | 0.939 | 0.912 |
| `sec128-heading-path-off` | 0.819 | 0.769 | 0.693 | 0.742 | 0.940 | 0.935 |
| `sec1024-shipped` | 0.797 | 0.751 | 0.619 | 0.745 | 0.944 | 0.905 |
| `sec1024-vector-heavy` | 0.792 | 0.794 | 0.524 | 0.730 | 0.944 | 0.934 |
| `sec1024-lexical-heavy` | 0.784 | 0.671 | 0.662 | 0.733 | 0.939 | 0.902 |
| `sec1024-heading-path-off` | 0.803 | 0.684 | 0.710 | 0.752 | 0.939 | 0.921 |
| `sec1024-shipped+rerank` | 0.870 | 0.854 | 0.813 | 0.817 | 0.931 | 0.926 |
| `sec1024-vector-heavy+rerank` | 0.875 | 0.947 | 0.717 | 0.818 | 0.928 | 0.946 |

Question counts per column: overall 244, api_reference 50, capability 44, cross_page 50, post_cutoff 50, single_page 50.

### Section-level matching

**recall@1**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `page128-shipped` | 0.000 | 0.000 | -- | -- | 0.000 | 0.000 |
| `page128-vector-heavy` | 0.000 | 0.000 | -- | -- | 0.000 | 0.000 |
| `page128-lexical-heavy` | 0.000 | 0.000 | -- | -- | 0.000 | 0.000 |
| `sec128-shipped` | 0.747 | 0.600 | -- | -- | 0.894 | 0.756 |
| `sec128-vector-heavy` | 0.761 | 0.640 | -- | -- | 0.915 | 0.733 |
| `sec128-lexical-heavy` | 0.683 | 0.500 | -- | -- | 0.872 | 0.689 |
| `sec128-heading-path-off` | 0.753 | 0.580 | -- | -- | 0.894 | 0.800 |
| `sec1024-shipped` | 0.704 | 0.540 | -- | -- | 0.894 | 0.689 |
| `sec1024-vector-heavy` | 0.732 | 0.560 | -- | -- | 0.894 | 0.756 |
| `sec1024-lexical-heavy` | 0.662 | 0.460 | -- | -- | 0.872 | 0.667 |
| `sec1024-heading-path-off` | 0.697 | 0.480 | -- | -- | 0.872 | 0.756 |
| `sec1024-shipped+rerank` | 0.817 | 0.780 | -- | -- | 0.851 | 0.822 |
| `sec1024-vector-heavy+rerank` | 0.873 | 0.880 | -- | -- | 0.851 | 0.889 |

**recall@3**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `page128-shipped` | 0.000 | 0.000 | -- | -- | 0.000 | 0.000 |
| `page128-vector-heavy` | 0.000 | 0.000 | -- | -- | 0.000 | 0.000 |
| `page128-lexical-heavy` | 0.000 | 0.000 | -- | -- | 0.000 | 0.000 |
| `sec128-shipped` | 0.845 | 0.740 | -- | -- | 0.936 | 0.867 |
| `sec128-vector-heavy` | 0.922 | 0.940 | -- | -- | 0.957 | 0.867 |
| `sec128-lexical-heavy` | 0.810 | 0.680 | -- | -- | 0.936 | 0.822 |
| `sec128-heading-path-off` | 0.859 | 0.740 | -- | -- | 0.957 | 0.889 |
| `sec1024-shipped` | 0.831 | 0.720 | -- | -- | 0.936 | 0.844 |
| `sec1024-vector-heavy` | 0.838 | 0.720 | -- | -- | 0.936 | 0.867 |
| `sec1024-lexical-heavy` | 0.824 | 0.700 | -- | -- | 0.936 | 0.844 |
| `sec1024-heading-path-off` | 0.838 | 0.720 | -- | -- | 0.936 | 0.867 |
| `sec1024-shipped+rerank` | 0.894 | 0.860 | -- | -- | 0.915 | 0.911 |
| `sec1024-vector-heavy+rerank` | 0.958 | 0.960 | -- | -- | 0.915 | 1.000 |

**recall@5**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `page128-shipped` | 0.000 | 0.000 | -- | -- | 0.000 | 0.000 |
| `page128-vector-heavy` | 0.000 | 0.000 | -- | -- | 0.000 | 0.000 |
| `page128-lexical-heavy` | 0.000 | 0.000 | -- | -- | 0.000 | 0.000 |
| `sec128-shipped` | 0.915 | 0.820 | -- | -- | 0.957 | 0.978 |
| `sec128-vector-heavy` | 0.958 | 0.960 | -- | -- | 0.957 | 0.956 |
| `sec128-lexical-heavy` | 0.866 | 0.720 | -- | -- | 0.957 | 0.933 |
| `sec128-heading-path-off` | 0.915 | 0.820 | -- | -- | 0.957 | 0.978 |
| `sec1024-shipped` | 0.880 | 0.740 | -- | -- | 0.957 | 0.956 |
| `sec1024-vector-heavy` | 0.937 | 0.880 | -- | -- | 0.957 | 0.978 |
| `sec1024-lexical-heavy` | 0.866 | 0.720 | -- | -- | 0.957 | 0.933 |
| `sec1024-heading-path-off` | 0.887 | 0.760 | -- | -- | 0.957 | 0.956 |
| `sec1024-shipped+rerank` | 0.922 | 0.860 | -- | -- | 0.957 | 0.956 |
| `sec1024-vector-heavy+rerank` | 0.979 | 0.980 | -- | -- | 0.957 | 1.000 |

**recall@10**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `page128-shipped` | 0.000 | 0.000 | -- | -- | 0.000 | 0.000 |
| `page128-vector-heavy` | 0.000 | 0.000 | -- | -- | 0.000 | 0.000 |
| `page128-lexical-heavy` | 0.000 | 0.000 | -- | -- | 0.000 | 0.000 |
| `sec128-shipped` | 0.958 | 0.940 | -- | -- | 0.957 | 0.978 |
| `sec128-vector-heavy` | 0.979 | 0.980 | -- | -- | 0.957 | 1.000 |
| `sec128-lexical-heavy` | 0.901 | 0.780 | -- | -- | 0.957 | 0.978 |
| `sec128-heading-path-off` | 0.937 | 0.880 | -- | -- | 0.957 | 0.978 |
| `sec1024-shipped` | 0.937 | 0.880 | -- | -- | 0.957 | 0.978 |
| `sec1024-vector-heavy` | 0.965 | 0.960 | -- | -- | 0.957 | 0.978 |
| `sec1024-lexical-heavy` | 0.901 | 0.780 | -- | -- | 0.957 | 0.978 |
| `sec1024-heading-path-off` | 0.908 | 0.800 | -- | -- | 0.957 | 0.978 |
| `sec1024-shipped+rerank` | 0.937 | 0.880 | -- | -- | 0.957 | 0.978 |
| `sec1024-vector-heavy+rerank` | 0.979 | 0.980 | -- | -- | 0.957 | 1.000 |

**mrr**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `page128-shipped` | 0.000 | 0.000 | -- | -- | 0.000 | 0.000 |
| `page128-vector-heavy` | 0.000 | 0.000 | -- | -- | 0.000 | 0.000 |
| `page128-lexical-heavy` | 0.000 | 0.000 | -- | -- | 0.000 | 0.000 |
| `sec128-shipped` | 0.814 | 0.701 | -- | -- | 0.917 | 0.832 |
| `sec128-vector-heavy` | 0.841 | 0.780 | -- | -- | 0.929 | 0.817 |
| `sec128-lexical-heavy` | 0.761 | 0.601 | -- | -- | 0.906 | 0.789 |
| `sec128-heading-path-off` | 0.818 | 0.686 | -- | -- | 0.918 | 0.859 |
| `sec1024-shipped` | 0.784 | 0.649 | -- | -- | 0.917 | 0.794 |
| `sec1024-vector-heavy` | 0.807 | 0.684 | -- | -- | 0.916 | 0.831 |
| `sec1024-lexical-heavy` | 0.752 | 0.582 | -- | -- | 0.906 | 0.780 |
| `sec1024-heading-path-off` | 0.780 | 0.615 | -- | -- | 0.906 | 0.831 |
| `sec1024-shipped+rerank` | 0.864 | 0.822 | -- | -- | 0.893 | 0.881 |
| `sec1024-vector-heavy+rerank` | 0.918 | 0.924 | -- | -- | 0.889 | 0.941 |

**ndcg@10**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `page128-shipped` | 0.000 | 0.000 | -- | -- | 0.000 | 0.000 |
| `page128-vector-heavy` | 0.000 | 0.000 | -- | -- | 0.000 | 0.000 |
| `page128-lexical-heavy` | 0.000 | 0.000 | -- | -- | 0.000 | 0.000 |
| `sec128-shipped` | 0.848 | 0.755 | -- | -- | 0.927 | 0.867 |
| `sec128-vector-heavy` | 0.875 | 0.831 | -- | -- | 0.936 | 0.862 |
| `sec128-lexical-heavy` | 0.796 | 0.644 | -- | -- | 0.919 | 0.835 |
| `sec128-heading-path-off` | 0.845 | 0.729 | -- | -- | 0.928 | 0.887 |
| `sec1024-shipped` | 0.820 | 0.701 | -- | -- | 0.927 | 0.840 |
| `sec1024-vector-heavy` | 0.845 | 0.749 | -- | -- | 0.926 | 0.866 |
| `sec1024-lexical-heavy` | 0.789 | 0.631 | -- | -- | 0.919 | 0.829 |
| `sec1024-heading-path-off` | 0.810 | 0.655 | -- | -- | 0.919 | 0.867 |
| `sec1024-shipped+rerank` | 0.881 | 0.834 | -- | -- | 0.909 | 0.905 |
| `sec1024-vector-heavy+rerank` | 0.933 | 0.938 | -- | -- | 0.906 | 0.956 |

Question counts per column: overall 142, api_reference 50, capability 0, cross_page 0, post_cutoff 47, single_page 45.

## Latency, cost and failures

| configuration | median ms | p90 ms | rerank calls | applied | fell back | budget skipped | rerank USD | errors |
|---|---|---|---|---|---|---|---|---|
| `page128-shipped` | 12 | 15 | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| `page128-vector-heavy` | 10 | 13 | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| `page128-lexical-heavy` | 10 | 13 | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| `sec128-shipped` | 7 | 9 | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| `sec128-vector-heavy` | 6 | 9 | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| `sec128-lexical-heavy` | 7 | 10 | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| `sec128-heading-path-off` | 7 | 10 | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| `sec1024-shipped` | 11 | 13 | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| `sec1024-vector-heavy` | 9 | 11 | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| `sec1024-lexical-heavy` | 9 | 11 | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| `sec1024-heading-path-off` | 9 | 12 | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| `sec1024-shipped+rerank` | 4427 | 5186 | 294 | 248 | 46 | 0 | 0.20602 | 0 |
| `sec1024-vector-heavy+rerank` | 4392 | 5332 | 294 | 257 | 37 | 0 | 0.20409 | 0 |

Latency is wall-clock for one question through one configuration: the Vespa round trip and, where it ran, the reranker's model call. The query's embedding is not in it -- a question is embedded once per embedding model and the vector is reused across every configuration that shares it, so charging that call to one configuration and not the others would be arbitrary.

## Unanswerable questions

The dataset holds 50 questions with no gold source, so they carry no recall. What they measure is whether the engine returns something confident anyway. Across every configuration, 650 of 650 runs returned a top hit, and 0 were reported as having no lexical footing.

| question | configuration | top hit | footing |
|---|---|---|---|
| Is there a timeout or expiration period for the open SSO configuration modal after which the setup must be restarted? | `page128-shipped` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso | not checked |
| What is the maximum retention period for a SCIM sync run's result before it is deleted, and can completed runs be purged early via the API? | `page128-shipped` | https://docs.mistral.ai/api/endpoint/beta/admin/scim | not checked |
| Is there a maximum number of Organizations that can be linked to a single Enterprise Account, and what happens if that limit is exceeded? | `page128-shipped` | https://docs.mistral.ai/admin/set-up-organization/enterprise-accounts | not checked |
| What is the maximum historical retention period for usage data retrievable via the Get Usage endpoint? | `page128-shipped` | https://docs.mistral.ai/admin/monitor-comply/zero-data-retention | not checked |
| What is the maximum number of messages allowed in a single chat completion request? | `page128-shipped` | https://docs.mistral.ai/studio/conversations/chat-completion | not checked |
| Does the Mistral GCP deployment support server-side prompt caching, and is there a cache hit discount on rawPredict calls? | `page128-shipped` | https://docs.mistral.ai/studio/conversations/advanced/prompt-caching | not checked |
| What is the maximum number of web pages MistralAI-User may visit for a single user request in Vibe, and is there a per-minute rate limit? | `page128-shipped` | https://docs.mistral.ai/studio/conversations/vision | not checked |
| Does `mistral-vespa generate` validate that the output directory is empty before writing, or does it have a flag to force overwriting existing files? | `page128-shipped` | https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli | not checked |
| Is there a keyboard shortcut to switch directly to Work mode from Chat or Code without opening the sidebar? | `page128-shipped` | https://docs.mistral.ai/vibe/work/switch-organization-workspace | not checked |
| Is there a maximum number of credentials (API keys or workload identity credentials) that can be attached to a single service account? | `page128-shipped` | https://docs.mistral.ai/admin/identity-access/service-accounts | not checked |
| Is there a limit on the number of handoff targets an agent can have, and what happens if a handoff references a nonexistent agent? | `page128-shipped` | https://docs.mistral.ai/studio/agents/handoffs | not checked |
| What is the maximum number of API keys a single Mistral AI account can generate? | `page128-shipped` | https://docs.mistral.ai/studio/conversations/vision | not checked |
| Is there a recommended maximum length or word limit for the role statement when providing a purpose in a prompt? | `page128-shipped` | https://docs.mistral.ai/studio/conversations/chat-completion/prompting | not checked |
| Is there a limit on how many agents a single account or workspace can create? | `page128-shipped` | https://docs.mistral.ai/getting-started/quickstarts/admin/manage-workspaces | not checked |
| How long does an invitation remain valid before it expires, and can the expiration period be customized? | `page128-shipped` | https://docs.mistral.ai/admin/identity-access/api-key-policy | not checked |
| What is the maximum number of selected event ids returned in a single ListCampaignSelectedEventsResponse, and does the endpoint support pagination? | `page128-shipped` | https://docs.mistral.ai/api/endpoint/beta/observability/campaigns | not checked |
| What is the minimum GPU VRAM requirement to fine-tune the Ministral 3 14B Instruct weights locally? | `page128-shipped` | https://docs.mistral.ai/models/ministral-3-14b-25-12 | not checked |
| Is there a maximum character or token length enforced for system prompts in Mistral models, and what happens if it is exceeded? | `page128-shipped` | https://docs.mistral.ai/resources/known-limitations | not checked |
| What is the per-token price charged when pay-as-you-go usage kicks in after the included monthly allowance is exhausted? | `page128-shipped` | https://docs.mistral.ai/admin/billing-usage/subscriptions | not checked |
| Is there a maximum number of campaigns that can be stored or returned per request, and is there a pagination limit for the campaigns list? | `page128-shipped` | https://docs.mistral.ai/api/endpoint/beta/observability/campaigns | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Ministral 3 8B? | `page128-shipped` | https://docs.mistral.ai/models/ministral-3-8b-25-12 | not checked |
| What is the maximum rate at which MistralAI-User requests can be sent to a single site during user actions in Vibe? | `page128-shipped` | https://docs.mistral.ai/robots | not checked |
| Can I apply document_annotation_format when passing an image (ImageURLChunk) instead of a PDF document, and does the annotation then apply per image? | `page128-shipped` | https://docs.mistral.ai/studio/document-processing/annotations | not checked |
| Is there a limit on how many hooks can be declared, or a defined execution order when multiple hooks match the same tool call? | `page128-shipped` | https://docs.mistral.ai/vibe/code/cli/hooks | not checked |
| Does the platform offer a grace period or retry policy for failed invoice payments before account suspension? | `page128-shipped` | https://docs.mistral.ai/studio/observability/evaluations/retry-failed-records | not checked |
| Is there a rate limit on how many observability datasets can be deleted per minute via the API? | `page128-shipped` | https://docs.mistral.ai/studio/conversations/vision | not checked |
| What is the maximum total byte size allowed for a request body before a 400 error is returned? | `page128-shipped` | https://docs.mistral.ai/resources/error-glossary | not checked |
| Is there a timeout limit for code interpreter executions, and what happens if the executed code exceeds it? | `page128-shipped` | https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter | not checked |
| Is there a limit on how many agents can be created per workspace or per API key? | `page128-shipped` | https://docs.mistral.ai/studio/conversations/vision | not checked |
| When deleting a judge that is currently referenced by active evaluations, does the API return a 409 Conflict, or does the deletion succeed and leave the evaluations without a judge? | `page128-shipped` | https://docs.mistral.ai/api/endpoint/beta/observability/judges | not checked |
| Is there a way to configure a timeout so that pending approval prompts auto-reject if left unanswered, and can that timeout duration be customized? | `page128-shipped` | https://docs.mistral.ai/studio/workflows/building-workflows/waiting_for_conditions | not checked |
| What are the specific numeric rate limits per model included in the custom Priority Tier limits? | `page128-shipped` | https://docs.mistral.ai/inference/priority-tier | not checked |
| What is the maximum number of fine-tuning jobs that can run concurrently per project on the fine-tuning API? | `page128-shipped` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning | not checked |
| Is there an air-gapped license validation mode, and how often does an offline installation re-check entitlements before degrading? | `page128-shipped` | https://docs.mistral.ai/studio/search/search-toolkit/ingestion/extractors | not checked |
| Is there a way to automatically revoke API keys and deactivate active sessions for a member the moment they are removed from the Organization? | `page128-shipped` | https://docs.mistral.ai/admin/identity-access/user-management | not checked |
| Is there a limit on the number of characters or options allowed in the instructions or JudgeClassificationOutput options fields? | `page128-shipped` | https://docs.mistral.ai/api/endpoint/beta/observability/judges | not checked |
| Is there a limit on the number of users that can auto-join per day through email-domain authentication, or a maximum organization size it enforces? | `page128-shipped` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/email-domain-authentication | not checked |
| What are the valid ranges or allowed values for the learning_rate hyperparameter when creating a classifier fine-tuning job? | `page128-shipped` | https://docs.mistral.ai/resources/deprecated/finetuning/classifier_factory | not checked |
| Is there a documented rate limit or maximum number of page visits MistralAI-User will make per user request in Vibe? | `page128-shipped` | https://docs.mistral.ai/studio/conversations/vision | not checked |
| Is there a documented maximum number of concurrent token-stream tasks a single workflow can run, and what happens if that limit is exceeded? | `page128-shipped` | https://docs.mistral.ai/studio/workflows/managing-workflows-in-production/concurrency | not checked |
| What is the maximum disk size available in the sandbox's default image, and can it be increased? | `page128-shipped` | https://docs.mistral.ai/studio/conversations/vision | not checked |
| What is the maximum number of live-judging requests per minute that can be made against a single chat completion event via this endpoint? | `page128-shipped` | https://docs.mistral.ai/api/endpoint/beta/observability/chat_completion_events | not checked |
| Is there a limit on how many fine-tuned custom models I can have active at the same time on my Mistral AI account? | `page128-shipped` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning | not checked |
| Does Mistral AI's documentation specify any recommended or maximum token budget for an LLM judge prompt when evaluating large evaluation sets? | `page128-shipped` | https://docs.mistral.ai/resources/known-limitations | not checked |
| Is there a way to export or share the todos list from the Work panel once a task is complete? | `page128-shipped` | https://docs.mistral.ai/vibe/work/get-started | not checked |
| What is the maximum number of span field definitions that the Get span fields endpoint can return in a single response, and is there pagination support? | `page128-shipped` | https://docs.mistral.ai/api/endpoint/beta/observability/spans | not checked |
| Is there an API to programmatically list or delete reusable Prompts, and what are the rate limits for Prompt execution? | `page128-shipped` | https://docs.mistral.ai/getting-started/quickstarts/studio/create-reusable-prompt | not checked |
| Does Mistral Document AI on Azure impose a maximum page count per document for processing, and if so, what is the limit? | `page128-shipped` | https://docs.mistral.ai/resources/known-limitations | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Magistral Small 1.0? | `page128-shipped` | https://docs.mistral.ai/studio/document-processing/document_qna | not checked |
| What is the maximum file size allowed for a FileField upload, and is there a limit on the number of files when multiple=True? | `page128-shipped` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning | not checked |
| Is there a timeout or expiration period for the open SSO configuration modal after which the setup must be restarted? | `page128-vector-heavy` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso | not checked |
| What is the maximum retention period for a SCIM sync run's result before it is deleted, and can completed runs be purged early via the API? | `page128-vector-heavy` | https://docs.mistral.ai/api/endpoint/beta/admin/scim | not checked |
| Is there a maximum number of Organizations that can be linked to a single Enterprise Account, and what happens if that limit is exceeded? | `page128-vector-heavy` | https://docs.mistral.ai/admin/set-up-organization/enterprise-accounts | not checked |
| What is the maximum historical retention period for usage data retrievable via the Get Usage endpoint? | `page128-vector-heavy` | https://docs.mistral.ai/admin/monitor-comply/zero-data-retention | not checked |
| What is the maximum number of messages allowed in a single chat completion request? | `page128-vector-heavy` | https://docs.mistral.ai/studio/conversations/chat-completion | not checked |
| Does the Mistral GCP deployment support server-side prompt caching, and is there a cache hit discount on rawPredict calls? | `page128-vector-heavy` | https://docs.mistral.ai/studio/conversations/advanced/prompt-caching | not checked |
| What is the maximum number of web pages MistralAI-User may visit for a single user request in Vibe, and is there a per-minute rate limit? | `page128-vector-heavy` | https://docs.mistral.ai/studio/conversations/vision | not checked |
| Does `mistral-vespa generate` validate that the output directory is empty before writing, or does it have a flag to force overwriting existing files? | `page128-vector-heavy` | https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli | not checked |
| Is there a keyboard shortcut to switch directly to Work mode from Chat or Code without opening the sidebar? | `page128-vector-heavy` | https://docs.mistral.ai/vibe/work/switch-organization-workspace | not checked |
| Is there a maximum number of credentials (API keys or workload identity credentials) that can be attached to a single service account? | `page128-vector-heavy` | https://docs.mistral.ai/admin/identity-access/workload-identity | not checked |
| Is there a limit on the number of handoff targets an agent can have, and what happens if a handoff references a nonexistent agent? | `page128-vector-heavy` | https://docs.mistral.ai/studio/agents/handoffs | not checked |
| What is the maximum number of API keys a single Mistral AI account can generate? | `page128-vector-heavy` | https://docs.mistral.ai/admin/identity-access/api-keys | not checked |
| Is there a recommended maximum length or word limit for the role statement when providing a purpose in a prompt? | `page128-vector-heavy` | https://docs.mistral.ai/studio/conversations/chat-completion/prompting | not checked |
| Is there a limit on how many agents a single account or workspace can create? | `page128-vector-heavy` | https://docs.mistral.ai/getting-started/quickstarts/admin/manage-workspaces | not checked |
| How long does an invitation remain valid before it expires, and can the expiration period be customized? | `page128-vector-heavy` | https://docs.mistral.ai/admin/identity-access/api-key-policy | not checked |
| What is the maximum number of selected event ids returned in a single ListCampaignSelectedEventsResponse, and does the endpoint support pagination? | `page128-vector-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/campaigns | not checked |
| What is the minimum GPU VRAM requirement to fine-tune the Ministral 3 14B Instruct weights locally? | `page128-vector-heavy` | https://docs.mistral.ai/models/ministral-3-14b-25-12 | not checked |
| Is there a maximum character or token length enforced for system prompts in Mistral models, and what happens if it is exceeded? | `page128-vector-heavy` | https://docs.mistral.ai/resources/known-limitations | not checked |
| What is the per-token price charged when pay-as-you-go usage kicks in after the included monthly allowance is exhausted? | `page128-vector-heavy` | https://docs.mistral.ai/admin/billing-usage/subscriptions | not checked |
| Is there a maximum number of campaigns that can be stored or returned per request, and is there a pagination limit for the campaigns list? | `page128-vector-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/campaigns | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Ministral 3 8B? | `page128-vector-heavy` | https://docs.mistral.ai/models/ministral-3-8b-25-12 | not checked |
| What is the maximum rate at which MistralAI-User requests can be sent to a single site during user actions in Vibe? | `page128-vector-heavy` | https://docs.mistral.ai/studio/conversations/vision | not checked |
| Can I apply document_annotation_format when passing an image (ImageURLChunk) instead of a PDF document, and does the annotation then apply per image? | `page128-vector-heavy` | https://docs.mistral.ai/studio/document-processing/annotations | not checked |
| Is there a limit on how many hooks can be declared, or a defined execution order when multiple hooks match the same tool call? | `page128-vector-heavy` | https://docs.mistral.ai/vibe/code/cli/hooks | not checked |
| Does the platform offer a grace period or retry policy for failed invoice payments before account suspension? | `page128-vector-heavy` | https://docs.mistral.ai/studio/observability/evaluations/retry-failed-records | not checked |
| Is there a rate limit on how many observability datasets can be deleted per minute via the API? | `page128-vector-heavy` | https://docs.mistral.ai/studio/conversations/vision | not checked |
| What is the maximum total byte size allowed for a request body before a 400 error is returned? | `page128-vector-heavy` | https://docs.mistral.ai/resources/error-glossary | not checked |
| Is there a timeout limit for code interpreter executions, and what happens if the executed code exceeds it? | `page128-vector-heavy` | https://docs.mistral.ai/vibe/chat-legacy/code-interpreter | not checked |
| Is there a limit on how many agents can be created per workspace or per API key? | `page128-vector-heavy` | https://docs.mistral.ai/studio/conversations/vision | not checked |
| When deleting a judge that is currently referenced by active evaluations, does the API return a 409 Conflict, or does the deletion succeed and leave the evaluations without a judge? | `page128-vector-heavy` | https://docs.mistral.ai/studio/observability/evaluations | not checked |
| Is there a way to configure a timeout so that pending approval prompts auto-reject if left unanswered, and can that timeout duration be customized? | `page128-vector-heavy` | https://docs.mistral.ai/studio/workflows/building-workflows/waiting_for_conditions | not checked |
| What are the specific numeric rate limits per model included in the custom Priority Tier limits? | `page128-vector-heavy` | https://docs.mistral.ai/inference/priority-tier | not checked |
| What is the maximum number of fine-tuning jobs that can run concurrently per project on the fine-tuning API? | `page128-vector-heavy` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning | not checked |
| Is there an air-gapped license validation mode, and how often does an offline installation re-check entitlements before degrading? | `page128-vector-heavy` | https://docs.mistral.ai/studio/search/search-toolkit/ingestion/extractors | not checked |
| Is there a way to automatically revoke API keys and deactivate active sessions for a member the moment they are removed from the Organization? | `page128-vector-heavy` | https://docs.mistral.ai/admin/identity-access/user-management | not checked |
| Is there a limit on the number of characters or options allowed in the instructions or JudgeClassificationOutput options fields? | `page128-vector-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/chat_completion_events/fields | not checked |
| Is there a limit on the number of users that can auto-join per day through email-domain authentication, or a maximum organization size it enforces? | `page128-vector-heavy` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/email-domain-authentication | not checked |
| What are the valid ranges or allowed values for the learning_rate hyperparameter when creating a classifier fine-tuning job? | `page128-vector-heavy` | https://docs.mistral.ai/resources/deprecated/finetuning/classifier_factory | not checked |
| Is there a documented rate limit or maximum number of page visits MistralAI-User will make per user request in Vibe? | `page128-vector-heavy` | https://docs.mistral.ai/studio/conversations/vision | not checked |
| Is there a documented maximum number of concurrent token-stream tasks a single workflow can run, and what happens if that limit is exceeded? | `page128-vector-heavy` | https://docs.mistral.ai/studio/workflows/managing-workflows-in-production/concurrency | not checked |
| What is the maximum disk size available in the sandbox's default image, and can it be increased? | `page128-vector-heavy` | https://docs.mistral.ai/studio/conversations/vision | not checked |
| What is the maximum number of live-judging requests per minute that can be made against a single chat completion event via this endpoint? | `page128-vector-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/chat_completion_events | not checked |
| Is there a limit on how many fine-tuned custom models I can have active at the same time on my Mistral AI account? | `page128-vector-heavy` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning | not checked |
| Does Mistral AI's documentation specify any recommended or maximum token budget for an LLM judge prompt when evaluating large evaluation sets? | `page128-vector-heavy` | https://docs.mistral.ai/resources/known-limitations | not checked |
| Is there a way to export or share the todos list from the Work panel once a task is complete? | `page128-vector-heavy` | https://docs.mistral.ai/vibe/work/get-started | not checked |
| What is the maximum number of span field definitions that the Get span fields endpoint can return in a single response, and is there pagination support? | `page128-vector-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/spans | not checked |
| Is there an API to programmatically list or delete reusable Prompts, and what are the rate limits for Prompt execution? | `page128-vector-heavy` | https://docs.mistral.ai/getting-started/quickstarts/studio/create-reusable-prompt | not checked |
| Does Mistral Document AI on Azure impose a maximum page count per document for processing, and if so, what is the limit? | `page128-vector-heavy` | https://docs.mistral.ai/resources/known-limitations | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Magistral Small 1.0? | `page128-vector-heavy` | https://docs.mistral.ai/studio/document-processing/document_qna | not checked |
| What is the maximum file size allowed for a FileField upload, and is there a limit on the number of files when multiple=True? | `page128-vector-heavy` | https://docs.mistral.ai/studio/conversations/vision | not checked |
| Is there a timeout or expiration period for the open SSO configuration modal after which the setup must be restarted? | `page128-lexical-heavy` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso | not checked |
| What is the maximum retention period for a SCIM sync run's result before it is deleted, and can completed runs be purged early via the API? | `page128-lexical-heavy` | https://docs.mistral.ai/api/endpoint/beta/admin/scim | not checked |
| Is there a maximum number of Organizations that can be linked to a single Enterprise Account, and what happens if that limit is exceeded? | `page128-lexical-heavy` | https://docs.mistral.ai/admin/set-up-organization/enterprise-accounts | not checked |
| What is the maximum historical retention period for usage data retrievable via the Get Usage endpoint? | `page128-lexical-heavy` | https://docs.mistral.ai/admin/monitor-comply/zero-data-retention | not checked |
| What is the maximum number of messages allowed in a single chat completion request? | `page128-lexical-heavy` | https://docs.mistral.ai/studio/conversations/chat-completion | not checked |
| Does the Mistral GCP deployment support server-side prompt caching, and is there a cache hit discount on rawPredict calls? | `page128-lexical-heavy` | https://docs.mistral.ai/studio/conversations/advanced/prompt-caching | not checked |
| What is the maximum number of web pages MistralAI-User may visit for a single user request in Vibe, and is there a per-minute rate limit? | `page128-lexical-heavy` | https://docs.mistral.ai/studio/conversations/vision | not checked |
| Does `mistral-vespa generate` validate that the output directory is empty before writing, or does it have a flag to force overwriting existing files? | `page128-lexical-heavy` | https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli | not checked |
| Is there a keyboard shortcut to switch directly to Work mode from Chat or Code without opening the sidebar? | `page128-lexical-heavy` | https://docs.mistral.ai/vibe/code/cli/work-with-cli | not checked |
| Is there a maximum number of credentials (API keys or workload identity credentials) that can be attached to a single service account? | `page128-lexical-heavy` | https://docs.mistral.ai/admin/identity-access/service-accounts | not checked |
| Is there a limit on the number of handoff targets an agent can have, and what happens if a handoff references a nonexistent agent? | `page128-lexical-heavy` | https://docs.mistral.ai/studio/agents/handoffs | not checked |
| What is the maximum number of API keys a single Mistral AI account can generate? | `page128-lexical-heavy` | https://docs.mistral.ai/studio/conversations/vision | not checked |
| Is there a recommended maximum length or word limit for the role statement when providing a purpose in a prompt? | `page128-lexical-heavy` | https://docs.mistral.ai/studio/conversations/chat-completion/prompting | not checked |
| Is there a limit on how many agents a single account or workspace can create? | `page128-lexical-heavy` | https://docs.mistral.ai/vibe/code/vs-code-extension/migration-mistral-code-enterprise | not checked |
| How long does an invitation remain valid before it expires, and can the expiration period be customized? | `page128-lexical-heavy` | https://docs.mistral.ai/admin/identity-access/api-key-policy | not checked |
| What is the maximum number of selected event ids returned in a single ListCampaignSelectedEventsResponse, and does the endpoint support pagination? | `page128-lexical-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/campaigns | not checked |
| What is the minimum GPU VRAM requirement to fine-tune the Ministral 3 14B Instruct weights locally? | `page128-lexical-heavy` | https://docs.mistral.ai/models/ministral-3-14b-25-12 | not checked |
| Is there a maximum character or token length enforced for system prompts in Mistral models, and what happens if it is exceeded? | `page128-lexical-heavy` | https://docs.mistral.ai/resources/known-limitations | not checked |
| What is the per-token price charged when pay-as-you-go usage kicks in after the included monthly allowance is exhausted? | `page128-lexical-heavy` | https://docs.mistral.ai/admin/billing-usage/subscriptions | not checked |
| Is there a maximum number of campaigns that can be stored or returned per request, and is there a pagination limit for the campaigns list? | `page128-lexical-heavy` | https://docs.mistral.ai/studio/conversations/vision | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Ministral 3 8B? | `page128-lexical-heavy` | https://docs.mistral.ai/models/ministral-3-8b-25-12 | not checked |
| What is the maximum rate at which MistralAI-User requests can be sent to a single site during user actions in Vibe? | `page128-lexical-heavy` | https://docs.mistral.ai/robots | not checked |
| Can I apply document_annotation_format when passing an image (ImageURLChunk) instead of a PDF document, and does the annotation then apply per image? | `page128-lexical-heavy` | https://docs.mistral.ai/studio/document-processing/annotations | not checked |
| Is there a limit on how many hooks can be declared, or a defined execution order when multiple hooks match the same tool call? | `page128-lexical-heavy` | https://docs.mistral.ai/vibe/code/cli/hooks | not checked |
| Does the platform offer a grace period or retry policy for failed invoice payments before account suspension? | `page128-lexical-heavy` | https://docs.mistral.ai/studio/observability/evaluations/retry-failed-records | not checked |
| Is there a rate limit on how many observability datasets can be deleted per minute via the API? | `page128-lexical-heavy` | https://docs.mistral.ai/studio/conversations/vision | not checked |
| What is the maximum total byte size allowed for a request body before a 400 error is returned? | `page128-lexical-heavy` | https://docs.mistral.ai/resources/error-glossary | not checked |
| Is there a timeout limit for code interpreter executions, and what happens if the executed code exceeds it? | `page128-lexical-heavy` | https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter | not checked |
| Is there a limit on how many agents can be created per workspace or per API key? | `page128-lexical-heavy` | https://docs.mistral.ai/studio/conversations/vision | not checked |
| When deleting a judge that is currently referenced by active evaluations, does the API return a 409 Conflict, or does the deletion succeed and leave the evaluations without a judge? | `page128-lexical-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/judges | not checked |
| Is there a way to configure a timeout so that pending approval prompts auto-reject if left unanswered, and can that timeout duration be customized? | `page128-lexical-heavy` | https://docs.mistral.ai/studio/workflows/building-workflows/waiting_for_conditions | not checked |
| What are the specific numeric rate limits per model included in the custom Priority Tier limits? | `page128-lexical-heavy` | https://docs.mistral.ai/inference/priority-tier | not checked |
| What is the maximum number of fine-tuning jobs that can run concurrently per project on the fine-tuning API? | `page128-lexical-heavy` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning | not checked |
| Is there an air-gapped license validation mode, and how often does an offline installation re-check entitlements before degrading? | `page128-lexical-heavy` | https://docs.mistral.ai/studio/search/search-toolkit/ingestion/extractors | not checked |
| Is there a way to automatically revoke API keys and deactivate active sessions for a member the moment they are removed from the Organization? | `page128-lexical-heavy` | https://docs.mistral.ai/admin/identity-access/user-management | not checked |
| Is there a limit on the number of characters or options allowed in the instructions or JudgeClassificationOutput options fields? | `page128-lexical-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/judges | not checked |
| Is there a limit on the number of users that can auto-join per day through email-domain authentication, or a maximum organization size it enforces? | `page128-lexical-heavy` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/email-domain-authentication | not checked |
| What are the valid ranges or allowed values for the learning_rate hyperparameter when creating a classifier fine-tuning job? | `page128-lexical-heavy` | https://docs.mistral.ai/resources/deprecated/finetuning/classifier_factory | not checked |
| Is there a documented rate limit or maximum number of page visits MistralAI-User will make per user request in Vibe? | `page128-lexical-heavy` | https://docs.mistral.ai/studio/conversations/vision | not checked |
| Is there a documented maximum number of concurrent token-stream tasks a single workflow can run, and what happens if that limit is exceeded? | `page128-lexical-heavy` | https://docs.mistral.ai/studio/workflows/managing-workflows-in-production/concurrency | not checked |
| What is the maximum disk size available in the sandbox's default image, and can it be increased? | `page128-lexical-heavy` | https://docs.mistral.ai/studio/conversations/vision | not checked |
| What is the maximum number of live-judging requests per minute that can be made against a single chat completion event via this endpoint? | `page128-lexical-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/chat_completion_events | not checked |
| Is there a limit on how many fine-tuned custom models I can have active at the same time on my Mistral AI account? | `page128-lexical-heavy` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning | not checked |
| Does Mistral AI's documentation specify any recommended or maximum token budget for an LLM judge prompt when evaluating large evaluation sets? | `page128-lexical-heavy` | https://docs.mistral.ai/resources/known-limitations | not checked |
| Is there a way to export or share the todos list from the Work panel once a task is complete? | `page128-lexical-heavy` | https://docs.mistral.ai/vibe/work/get-started | not checked |
| What is the maximum number of span field definitions that the Get span fields endpoint can return in a single response, and is there pagination support? | `page128-lexical-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/spans | not checked |
| Is there an API to programmatically list or delete reusable Prompts, and what are the rate limits for Prompt execution? | `page128-lexical-heavy` | https://docs.mistral.ai/getting-started/quickstarts/studio/create-reusable-prompt | not checked |
| Does Mistral Document AI on Azure impose a maximum page count per document for processing, and if so, what is the limit? | `page128-lexical-heavy` | https://docs.mistral.ai/studio/batch-processing | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Magistral Small 1.0? | `page128-lexical-heavy` | https://docs.mistral.ai/studio/document-processing/document_qna | not checked |
| What is the maximum file size allowed for a FileField upload, and is there a limit on the number of files when multiple=True? | `page128-lexical-heavy` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning | not checked |
| Is there a timeout or expiration period for the open SSO configuration modal after which the setup must be restarted? | `sec128-shipped` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso#start-in-admin | not checked |
| What is the maximum retention period for a SCIM sync run's result before it is deleted, and can completed runs be purged early via the API? | `sec128-shipped` | https://docs.mistral.ai/api/endpoint/beta/admin/scim#operation-users_api_admin_scim_sync_get_scim_sync_run | not checked |
| Is there a maximum number of Organizations that can be linked to a single Enterprise Account, and what happens if that limit is exceeded? | `sec128-shipped` | https://docs.mistral.ai/admin/set-up-organization/enterprise-accounts#organizations | not checked |
| What is the maximum historical retention period for usage data retrievable via the Get Usage endpoint? | `sec128-shipped` | https://docs.mistral.ai/admin/monitor-comply/zero-data-retention#what-zdr-covers | not checked |
| What is the maximum number of messages allowed in a single chat completion request? | `sec128-shipped` | https://docs.mistral.ai/studio/conversations/vision#whats-the-maximum-number-images-per-request | not checked |
| Does the Mistral GCP deployment support server-side prompt caching, and is there a cache hit discount on rawPredict calls? | `sec128-shipped` | https://docs.mistral.ai/studio/conversations/advanced/prompt-caching | not checked |
| What is the maximum number of web pages MistralAI-User may visit for a single user request in Vibe, and is there a per-minute rate limit? | `sec128-shipped` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Does `mistral-vespa generate` validate that the output directory is empty before writing, or does it have a flag to force overwriting existing files? | `sec128-shipped` | https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli#generate | not checked |
| Is there a keyboard shortcut to switch directly to Work mode from Chat or Code without opening the sidebar? | `sec128-shipped` | https://docs.mistral.ai/getting-started/quickstarts/vibe-work/first-task#step-1 | not checked |
| Is there a maximum number of credentials (API keys or workload identity credentials) that can be attached to a single service account? | `sec128-shipped` | https://docs.mistral.ai/admin/identity-access/workload-identity#how-setup-works | not checked |
| Is there a limit on the number of handoff targets an agent can have, and what happens if a handoff references a nonexistent agent? | `sec128-shipped` | https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#multi-agent-handoffs | not checked |
| What is the maximum number of API keys a single Mistral AI account can generate? | `sec128-shipped` | https://docs.mistral.ai/studio/conversations/vision#whats-the-maximum-number-images-per-request | not checked |
| Is there a recommended maximum length or word limit for the role statement when providing a purpose in a prompt? | `sec128-shipped` | https://docs.mistral.ai/inference/prompting#purpose | not checked |
| Is there a limit on how many agents a single account or workspace can create? | `sec128-shipped` | https://docs.mistral.ai/studio/agents/handoffs#create-an-agentic-workflow | not checked |
| How long does an invitation remain valid before it expires, and can the expiration period be customized? | `sec128-shipped` | https://docs.mistral.ai/admin/identity-access/api-key-policy#default-state | not checked |
| What is the maximum number of selected event ids returned in a single ListCampaignSelectedEventsResponse, and does the endpoint support pagination? | `sec128-shipped` | https://docs.mistral.ai/api/endpoint/beta/observability/campaigns#operation-get_campaign_selected_events_v1_observability_campaigns_campaign_id_selected_events_get | not checked |
| What is the minimum GPU VRAM requirement to fine-tune the Ministral 3 14B Instruct weights locally? | `sec128-shipped` | https://docs.mistral.ai/models/ministral-3-14b-25-12 | not checked |
| Is there a maximum character or token length enforced for system prompts in Mistral models, and what happens if it is exceeded? | `sec128-shipped` | https://docs.mistral.ai/admin/identity-access/api-key-policy#workspace-limit-above-org-limit | not checked |
| What is the per-token price charged when pay-as-you-go usage kicks in after the included monthly allowance is exhausted? | `sec128-shipped` | https://docs.mistral.ai/admin/billing-usage/subscriptions#included-monthly-usage | not checked |
| Is there a maximum number of campaigns that can be stored or returned per request, and is there a pagination limit for the campaigns list? | `sec128-shipped` | https://docs.mistral.ai/studio/batch-processing#whats-the-max-number-of-batch-jobs-one-can-create | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Ministral 3 8B? | `sec128-shipped` | https://docs.mistral.ai/models/ministral-3-8b-25-12 | not checked |
| What is the maximum rate at which MistralAI-User requests can be sent to a single site during user actions in Vibe? | `sec128-shipped` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Can I apply document_annotation_format when passing an image (ImageURLChunk) instead of a PDF document, and does the annotation then apply per image? | `sec128-shipped` | https://docs.mistral.ai/studio/document-processing/annotations#usage | not checked |
| Is there a limit on how many hooks can be declared, or a defined execution order when multiple hooks match the same tool call? | `sec128-shipped` | https://docs.mistral.ai/vibe/code/cli/hooks#post-tool | not checked |
| Does the platform offer a grace period or retry policy for failed invoice payments before account suspension? | `sec128-shipped` | https://docs.mistral.ai/studio/observability/evaluations/retry-failed-records | not checked |
| Is there a rate limit on how many observability datasets can be deleted per minute via the API? | `sec128-shipped` | https://docs.mistral.ai/studio/observability/evaluations/datasets#how-large-can-my-dataset-be | not checked |
| What is the maximum total byte size allowed for a request body before a 400 error is returned? | `sec128-shipped` | https://docs.mistral.ai/resources/error-glossary#400-bad-request | not checked |
| Is there a timeout limit for code interpreter executions, and what happens if the executed code exceeds it? | `sec128-shipped` | https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#explanation-of-the-output | not checked |
| Is there a limit on how many agents can be created per workspace or per API key? | `sec128-shipped` | https://docs.mistral.ai/vibe/work/switch-organization-workspace#scoped | not checked |
| When deleting a judge that is currently referenced by active evaluations, does the API return a 409 Conflict, or does the deletion succeed and leave the evaluations without a judge? | `sec128-shipped` | https://docs.mistral.ai/studio/observability/evaluations#how-do-i-use-an-llm-as-a-judge | not checked |
| Is there a way to configure a timeout so that pending approval prompts auto-reject if left unanswered, and can that timeout duration be customized? | `sec128-shipped` | https://docs.mistral.ai/studio/workflows/interacting-with-workflows/conversational_workflows#timeout | not checked |
| What are the specific numeric rate limits per model included in the custom Priority Tier limits? | `sec128-shipped` | https://docs.mistral.ai/inference/priority-tier#quotas-and-limits | not checked |
| What is the maximum number of fine-tuning jobs that can run concurrently per project on the fine-tuning API? | `sec128-shipped` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#jobs-management | not checked |
| Is there an air-gapped license validation mode, and how often does an offline installation re-check entitlements before degrading? | `sec128-shipped` | https://docs.mistral.ai/vibe/code/cli/install-setup#prerequisites | not checked |
| Is there a way to automatically revoke API keys and deactivate active sessions for a member the moment they are removed from the Organization? | `sec128-shipped` | https://docs.mistral.ai/admin/identity-access/user-management#remove-members | not checked |
| Is there a limit on the number of characters or options allowed in the instructions or JudgeClassificationOutput options fields? | `sec128-shipped` | https://docs.mistral.ai/api/endpoint/beta/observability/datasets/records#operation-judge_dataset_record_v1_observability_dataset_records_dataset_record_id_live_judging_post | not checked |
| Is there a limit on the number of users that can auto-join per day through email-domain authentication, or a maximum organization size it enforces? | `sec128-shipped` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/email-domain-authentication | not checked |
| What are the valid ranges or allowed values for the learning_rate hyperparameter when creating a classifier fine-tuning job? | `sec128-shipped` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#what-is-the-recommended-learning-rate | not checked |
| Is there a documented rate limit or maximum number of page visits MistralAI-User will make per user request in Vibe? | `sec128-shipped` | https://docs.mistral.ai/studio/conversations/vision#whats-the-maximum-number-images-per-request | not checked |
| Is there a documented maximum number of concurrent token-stream tasks a single workflow can run, and what happens if that limit is exceeded? | `sec128-shipped` | https://docs.mistral.ai/admin/identity-access/api-key-policy#workspace-limit-above-org-limit | not checked |
| What is the maximum disk size available in the sandbox's default image, and can it be increased? | `sec128-shipped` | https://docs.mistral.ai/studio/conversations/vision#how-many-tokens-correspond-to-an-image-andor-what-is-the-maximum-resolution | not checked |
| What is the maximum number of live-judging requests per minute that can be made against a single chat completion event via this endpoint? | `sec128-shipped` | https://docs.mistral.ai/api/endpoint/beta/observability/chat_completion_events#operation-judge_chat_completion_event_v1_observability_chat_completion_events_event_id_live_judging_post | not checked |
| Is there a limit on how many fine-tuned custom models I can have active at the same time on my Mistral AI account? | `sec128-shipped` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#fine-tuned-models | not checked |
| Does Mistral AI's documentation specify any recommended or maximum token budget for an LLM judge prompt when evaluating large evaluation sets? | `sec128-shipped` | https://docs.mistral.ai/studio/observability/evaluations/judges#basic-llm-judge | not checked |
| Is there a way to export or share the todos list from the Work panel once a task is complete? | `sec128-shipped` | https://docs.mistral.ai/vibe/work/safety-and-approvals#todos-panel | not checked |
| What is the maximum number of span field definitions that the Get span fields endpoint can return in a single response, and is there pagination support? | `sec128-shipped` | https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_fields_v1_observability_spans_fields_get | not checked |
| Is there an API to programmatically list or delete reusable Prompts, and what are the rate limits for Prompt execution? | `sec128-shipped` | https://docs.mistral.ai/getting-started/quickstarts/studio/create-reusable-prompt#verify | not checked |
| Does Mistral Document AI on Azure impose a maximum page count per document for processing, and if so, what is the limit? | `sec128-shipped` | https://docs.mistral.ai/vibe/work/libraries#limits | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Magistral Small 1.0? | `sec128-shipped` | https://docs.mistral.ai/models/magistral-small-1-0-25-06 | not checked |
| What is the maximum file size allowed for a FileField upload, and is there a limit on the number of files when multiple=True? | `sec128-shipped` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#whats-the-size-limit-of-the-training-data | not checked |
| Is there a timeout or expiration period for the open SSO configuration modal after which the setup must be restarted? | `sec128-vector-heavy` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso#start-in-admin | not checked |
| What is the maximum retention period for a SCIM sync run's result before it is deleted, and can completed runs be purged early via the API? | `sec128-vector-heavy` | https://docs.mistral.ai/api/endpoint/beta/admin/scim#operation-users_api_admin_scim_sync_get_scim_sync_run | not checked |
| Is there a maximum number of Organizations that can be linked to a single Enterprise Account, and what happens if that limit is exceeded? | `sec128-vector-heavy` | https://docs.mistral.ai/admin/set-up-organization/enterprise-accounts#organizations | not checked |
| What is the maximum historical retention period for usage data retrievable via the Get Usage endpoint? | `sec128-vector-heavy` | https://docs.mistral.ai/admin/monitor-comply/zero-data-retention#what-zdr-covers | not checked |
| What is the maximum number of messages allowed in a single chat completion request? | `sec128-vector-heavy` | https://docs.mistral.ai/studio/conversations/vision#whats-the-maximum-number-images-per-request | not checked |
| Does the Mistral GCP deployment support server-side prompt caching, and is there a cache hit discount on rawPredict calls? | `sec128-vector-heavy` | https://docs.mistral.ai/studio/conversations/advanced/prompt-caching | not checked |
| What is the maximum number of web pages MistralAI-User may visit for a single user request in Vibe, and is there a per-minute rate limit? | `sec128-vector-heavy` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Does `mistral-vespa generate` validate that the output directory is empty before writing, or does it have a flag to force overwriting existing files? | `sec128-vector-heavy` | https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli#generate | not checked |
| Is there a keyboard shortcut to switch directly to Work mode from Chat or Code without opening the sidebar? | `sec128-vector-heavy` | https://docs.mistral.ai/vibe/work/switch-organization-workspace#switcher | not checked |
| Is there a maximum number of credentials (API keys or workload identity credentials) that can be attached to a single service account? | `sec128-vector-heavy` | https://docs.mistral.ai/admin/identity-access/workload-identity#how-setup-works | not checked |
| Is there a limit on the number of handoff targets an agent can have, and what happens if a handoff references a nonexistent agent? | `sec128-vector-heavy` | https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#multi-agent-handoffs | not checked |
| What is the maximum number of API keys a single Mistral AI account can generate? | `sec128-vector-heavy` | https://docs.mistral.ai/api/endpoint/beta/admin/api-keys#operation-users_api_admin_api_keys_get_api_keys | not checked |
| Is there a recommended maximum length or word limit for the role statement when providing a purpose in a prompt? | `sec128-vector-heavy` | https://docs.mistral.ai/inference/prompting#purpose | not checked |
| Is there a limit on how many agents a single account or workspace can create? | `sec128-vector-heavy` | https://docs.mistral.ai/studio/agents/handoffs#create-an-agentic-workflow | not checked |
| How long does an invitation remain valid before it expires, and can the expiration period be customized? | `sec128-vector-heavy` | https://docs.mistral.ai/admin/identity-access/api-key-policy#default-state | not checked |
| What is the maximum number of selected event ids returned in a single ListCampaignSelectedEventsResponse, and does the endpoint support pagination? | `sec128-vector-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/campaigns#operation-get_campaign_selected_events_v1_observability_campaigns_campaign_id_selected_events_get | not checked |
| What is the minimum GPU VRAM requirement to fine-tune the Ministral 3 14B Instruct weights locally? | `sec128-vector-heavy` | https://docs.mistral.ai/models/ministral-3-14b-25-12 | not checked |
| Is there a maximum character or token length enforced for system prompts in Mistral models, and what happens if it is exceeded? | `sec128-vector-heavy` | https://docs.mistral.ai/admin/identity-access/api-key-policy#workspace-limit-above-org-limit | not checked |
| What is the per-token price charged when pay-as-you-go usage kicks in after the included monthly allowance is exhausted? | `sec128-vector-heavy` | https://docs.mistral.ai/admin/billing-usage/subscriptions#included-monthly-usage | not checked |
| Is there a maximum number of campaigns that can be stored or returned per request, and is there a pagination limit for the campaigns list? | `sec128-vector-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/campaigns#operation-get_campaigns_v1_observability_campaigns_get | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Ministral 3 8B? | `sec128-vector-heavy` | https://docs.mistral.ai/models/ministral-3-8b-25-12 | not checked |
| What is the maximum rate at which MistralAI-User requests can be sent to a single site during user actions in Vibe? | `sec128-vector-heavy` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Can I apply document_annotation_format when passing an image (ImageURLChunk) instead of a PDF document, and does the annotation then apply per image? | `sec128-vector-heavy` | https://docs.mistral.ai/studio/document-processing/annotations#document-annotation-explanation | not checked |
| Is there a limit on how many hooks can be declared, or a defined execution order when multiple hooks match the same tool call? | `sec128-vector-heavy` | https://docs.mistral.ai/vibe/code/cli/hooks#post-tool | not checked |
| Does the platform offer a grace period or retry policy for failed invoice payments before account suspension? | `sec128-vector-heavy` | https://docs.mistral.ai/studio/observability/evaluations/retry-failed-records | not checked |
| Is there a rate limit on how many observability datasets can be deleted per minute via the API? | `sec128-vector-heavy` | https://docs.mistral.ai/studio/observability/evaluations/datasets#how-large-can-my-dataset-be | not checked |
| What is the maximum total byte size allowed for a request body before a 400 error is returned? | `sec128-vector-heavy` | https://docs.mistral.ai/resources/error-glossary#400-bad-request | not checked |
| Is there a timeout limit for code interpreter executions, and what happens if the executed code exceeds it? | `sec128-vector-heavy` | https://docs.mistral.ai/vibe/chat-legacy/code-interpreter#running-code | not checked |
| Is there a limit on how many agents can be created per workspace or per API key? | `sec128-vector-heavy` | https://docs.mistral.ai/vibe/work/switch-organization-workspace#scoped | not checked |
| When deleting a judge that is currently referenced by active evaluations, does the API return a 409 Conflict, or does the deletion succeed and leave the evaluations without a judge? | `sec128-vector-heavy` | https://docs.mistral.ai/studio/observability/evaluations#how-do-i-use-an-llm-as-a-judge | not checked |
| Is there a way to configure a timeout so that pending approval prompts auto-reject if left unanswered, and can that timeout duration be customized? | `sec128-vector-heavy` | https://docs.mistral.ai/studio/workflows/interacting-with-workflows/conversational_workflows#timeout | not checked |
| What are the specific numeric rate limits per model included in the custom Priority Tier limits? | `sec128-vector-heavy` | https://docs.mistral.ai/inference/priority-tier#quotas-and-limits | not checked |
| What is the maximum number of fine-tuning jobs that can run concurrently per project on the fine-tuning API? | `sec128-vector-heavy` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#jobs-management | not checked |
| Is there an air-gapped license validation mode, and how often does an offline installation re-check entitlements before degrading? | `sec128-vector-heavy` | https://docs.mistral.ai/inference/deployment/local-deployment/vllm#offline-mode-inference | not checked |
| Is there a way to automatically revoke API keys and deactivate active sessions for a member the moment they are removed from the Organization? | `sec128-vector-heavy` | https://docs.mistral.ai/admin/identity-access/user-management#remove-members | not checked |
| Is there a limit on the number of characters or options allowed in the instructions or JudgeClassificationOutput options fields? | `sec128-vector-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/chat_completion_events#operation-judge_chat_completion_event_v1_observability_chat_completion_events_event_id_live_judging_post | not checked |
| Is there a limit on the number of users that can auto-join per day through email-domain authentication, or a maximum organization size it enforces? | `sec128-vector-heavy` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/email-domain-authentication | not checked |
| What are the valid ranges or allowed values for the learning_rate hyperparameter when creating a classifier fine-tuning job? | `sec128-vector-heavy` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#what-is-the-recommended-learning-rate | not checked |
| Is there a documented rate limit or maximum number of page visits MistralAI-User will make per user request in Vibe? | `sec128-vector-heavy` | https://docs.mistral.ai/studio/conversations/vision#whats-the-maximum-number-images-per-request | not checked |
| Is there a documented maximum number of concurrent token-stream tasks a single workflow can run, and what happens if that limit is exceeded? | `sec128-vector-heavy` | https://docs.mistral.ai/admin/identity-access/api-key-policy#workspace-limit-above-org-limit | not checked |
| What is the maximum disk size available in the sandbox's default image, and can it be increased? | `sec128-vector-heavy` | https://docs.mistral.ai/studio/conversations/vision#how-many-tokens-correspond-to-an-image-andor-what-is-the-maximum-resolution | not checked |
| What is the maximum number of live-judging requests per minute that can be made against a single chat completion event via this endpoint? | `sec128-vector-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/chat_completion_events#operation-judge_chat_completion_event_v1_observability_chat_completion_events_event_id_live_judging_post | not checked |
| Is there a limit on how many fine-tuned custom models I can have active at the same time on my Mistral AI account? | `sec128-vector-heavy` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#fine-tuned-models | not checked |
| Does Mistral AI's documentation specify any recommended or maximum token budget for an LLM judge prompt when evaluating large evaluation sets? | `sec128-vector-heavy` | https://docs.mistral.ai/studio/observability/evaluations/judges#basic-llm-judge | not checked |
| Is there a way to export or share the todos list from the Work panel once a task is complete? | `sec128-vector-heavy` | https://docs.mistral.ai/vibe/work/safety-and-approvals#todos-panel | not checked |
| What is the maximum number of span field definitions that the Get span fields endpoint can return in a single response, and is there pagination support? | `sec128-vector-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_fields_v1_observability_spans_fields_get | not checked |
| Is there an API to programmatically list or delete reusable Prompts, and what are the rate limits for Prompt execution? | `sec128-vector-heavy` | https://docs.mistral.ai/getting-started/quickstarts/studio/create-reusable-prompt#verify | not checked |
| Does Mistral Document AI on Azure impose a maximum page count per document for processing, and if so, what is the limit? | `sec128-vector-heavy` | https://docs.mistral.ai/vibe/work/libraries#limits | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Magistral Small 1.0? | `sec128-vector-heavy` | https://docs.mistral.ai/models/magistral-small-1-0-25-06 | not checked |
| What is the maximum file size allowed for a FileField upload, and is there a limit on the number of files when multiple=True? | `sec128-vector-heavy` | https://docs.mistral.ai/studio/workflows/interacting-with-workflows/conversational_workflows/forms_and_confirmations#filefield | not checked |
| Is there a timeout or expiration period for the open SSO configuration modal after which the setup must be restarted? | `sec128-lexical-heavy` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso#start-in-admin | not checked |
| What is the maximum retention period for a SCIM sync run's result before it is deleted, and can completed runs be purged early via the API? | `sec128-lexical-heavy` | https://docs.mistral.ai/api/endpoint/beta/admin/scim#operation-users_api_admin_scim_sync_get_scim_sync_run | not checked |
| Is there a maximum number of Organizations that can be linked to a single Enterprise Account, and what happens if that limit is exceeded? | `sec128-lexical-heavy` | https://docs.mistral.ai/admin/set-up-organization/enterprise-accounts#organizations | not checked |
| What is the maximum historical retention period for usage data retrievable via the Get Usage endpoint? | `sec128-lexical-heavy` | https://docs.mistral.ai/admin/monitor-comply/zero-data-retention#what-zdr-covers | not checked |
| What is the maximum number of messages allowed in a single chat completion request? | `sec128-lexical-heavy` | https://docs.mistral.ai/studio/conversations/vision#whats-the-maximum-number-images-per-request | not checked |
| Does the Mistral GCP deployment support server-side prompt caching, and is there a cache hit discount on rawPredict calls? | `sec128-lexical-heavy` | https://docs.mistral.ai/studio/conversations/advanced/prompt-caching | not checked |
| What is the maximum number of web pages MistralAI-User may visit for a single user request in Vibe, and is there a per-minute rate limit? | `sec128-lexical-heavy` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Does `mistral-vespa generate` validate that the output directory is empty before writing, or does it have a flag to force overwriting existing files? | `sec128-lexical-heavy` | https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli#generate | not checked |
| Is there a keyboard shortcut to switch directly to Work mode from Chat or Code without opening the sidebar? | `sec128-lexical-heavy` | https://docs.mistral.ai/getting-started/quickstarts/vibe-work/first-task#step-1 | not checked |
| Is there a maximum number of credentials (API keys or workload identity credentials) that can be attached to a single service account? | `sec128-lexical-heavy` | https://docs.mistral.ai/admin/identity-access/workload-identity#how-setup-works | not checked |
| Is there a limit on the number of handoff targets an agent can have, and what happens if a handoff references a nonexistent agent? | `sec128-lexical-heavy` | https://docs.mistral.ai/studio/agents/agents-api | not checked |
| What is the maximum number of API keys a single Mistral AI account can generate? | `sec128-lexical-heavy` | https://docs.mistral.ai/studio/batch-processing#whats-the-max-number-of-batch-jobs-one-can-create | not checked |
| Is there a recommended maximum length or word limit for the role statement when providing a purpose in a prompt? | `sec128-lexical-heavy` | https://docs.mistral.ai/inference/prompting#purpose | not checked |
| Is there a limit on how many agents a single account or workspace can create? | `sec128-lexical-heavy` | https://docs.mistral.ai/studio/agents/handoffs#create-an-agentic-workflow | not checked |
| How long does an invitation remain valid before it expires, and can the expiration period be customized? | `sec128-lexical-heavy` | https://docs.mistral.ai/studio/batch-processing#how-long-does-the-batch-api-take-to-process | not checked |
| What is the maximum number of selected event ids returned in a single ListCampaignSelectedEventsResponse, and does the endpoint support pagination? | `sec128-lexical-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/campaigns#operation-get_campaign_selected_events_v1_observability_campaigns_campaign_id_selected_events_get | not checked |
| What is the minimum GPU VRAM requirement to fine-tune the Ministral 3 14B Instruct weights locally? | `sec128-lexical-heavy` | https://docs.mistral.ai/models/ministral-3-14b-25-12 | not checked |
| Is there a maximum character or token length enforced for system prompts in Mistral models, and what happens if it is exceeded? | `sec128-lexical-heavy` | https://docs.mistral.ai/admin/identity-access/api-key-policy#workspace-limit-above-org-limit | not checked |
| What is the per-token price charged when pay-as-you-go usage kicks in after the included monthly allowance is exhausted? | `sec128-lexical-heavy` | https://docs.mistral.ai/admin/billing-usage/subscriptions#included-monthly-usage | not checked |
| Is there a maximum number of campaigns that can be stored or returned per request, and is there a pagination limit for the campaigns list? | `sec128-lexical-heavy` | https://docs.mistral.ai/studio/batch-processing#whats-the-max-number-of-batch-jobs-one-can-create | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Ministral 3 8B? | `sec128-lexical-heavy` | https://docs.mistral.ai/studio/conversations/vision#whats-the-maximum-number-images-per-request | not checked |
| What is the maximum rate at which MistralAI-User requests can be sent to a single site during user actions in Vibe? | `sec128-lexical-heavy` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Can I apply document_annotation_format when passing an image (ImageURLChunk) instead of a PDF document, and does the annotation then apply per image? | `sec128-lexical-heavy` | https://docs.mistral.ai/studio/document-processing/annotations#usage | not checked |
| Is there a limit on how many hooks can be declared, or a defined execution order when multiple hooks match the same tool call? | `sec128-lexical-heavy` | https://docs.mistral.ai/vibe/code/cli/hooks#file-locations | not checked |
| Does the platform offer a grace period or retry policy for failed invoice payments before account suspension? | `sec128-lexical-heavy` | https://docs.mistral.ai/studio/observability/evaluations/retry-failed-records#fixing-the-task-before-retrying | not checked |
| Is there a rate limit on how many observability datasets can be deleted per minute via the API? | `sec128-lexical-heavy` | https://docs.mistral.ai/studio/observability/evaluations/datasets#how-large-can-my-dataset-be | not checked |
| What is the maximum total byte size allowed for a request body before a 400 error is returned? | `sec128-lexical-heavy` | https://docs.mistral.ai/resources/error-glossary#400-bad-request | not checked |
| Is there a timeout limit for code interpreter executions, and what happens if the executed code exceeds it? | `sec128-lexical-heavy` | https://docs.mistral.ai/vibe/code/vibe-code-web/slack-integration#what-happens-next | not checked |
| Is there a limit on how many agents can be created per workspace or per API key? | `sec128-lexical-heavy` | https://docs.mistral.ai/vibe/work/switch-organization-workspace#scoped | not checked |
| When deleting a judge that is currently referenced by active evaluations, does the API return a 409 Conflict, or does the deletion succeed and leave the evaluations without a judge? | `sec128-lexical-heavy` | https://docs.mistral.ai/studio/observability/evaluations#how-do-i-use-an-llm-as-a-judge | not checked |
| Is there a way to configure a timeout so that pending approval prompts auto-reject if left unanswered, and can that timeout duration be customized? | `sec128-lexical-heavy` | https://docs.mistral.ai/studio/workflows/interacting-with-workflows/conversational_workflows#timeout | not checked |
| What are the specific numeric rate limits per model included in the custom Priority Tier limits? | `sec128-lexical-heavy` | https://docs.mistral.ai/inference/priority-tier#quotas-and-limits | not checked |
| What is the maximum number of fine-tuning jobs that can run concurrently per project on the fine-tuning API? | `sec128-lexical-heavy` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#jobs-management | not checked |
| Is there an air-gapped license validation mode, and how often does an offline installation re-check entitlements before degrading? | `sec128-lexical-heavy` | https://docs.mistral.ai/studio/search/search-toolkit/ingestion/extractors#pymupdf-extractor | not checked |
| Is there a way to automatically revoke API keys and deactivate active sessions for a member the moment they are removed from the Organization? | `sec128-lexical-heavy` | https://docs.mistral.ai/admin/identity-access/user-management#remove-members | not checked |
| Is there a limit on the number of characters or options allowed in the instructions or JudgeClassificationOutput options fields? | `sec128-lexical-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/datasets/records#operation-judge_dataset_record_v1_observability_dataset_records_dataset_record_id_live_judging_post | not checked |
| Is there a limit on the number of users that can auto-join per day through email-domain authentication, or a maximum organization size it enforces? | `sec128-lexical-heavy` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/email-domain-authentication | not checked |
| What are the valid ranges or allowed values for the learning_rate hyperparameter when creating a classifier fine-tuning job? | `sec128-lexical-heavy` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#what-is-the-recommended-learning-rate | not checked |
| Is there a documented rate limit or maximum number of page visits MistralAI-User will make per user request in Vibe? | `sec128-lexical-heavy` | https://docs.mistral.ai/api/endpoint/beta/admin/user-groups#operation-users_api_admin_user_groups_get_user_groups | not checked |
| Is there a documented maximum number of concurrent token-stream tasks a single workflow can run, and what happens if that limit is exceeded? | `sec128-lexical-heavy` | https://docs.mistral.ai/admin/identity-access/api-key-policy#workspace-limit-above-org-limit | not checked |
| What is the maximum disk size available in the sandbox's default image, and can it be increased? | `sec128-lexical-heavy` | https://docs.mistral.ai/studio/conversations/vision#how-many-tokens-correspond-to-an-image-andor-what-is-the-maximum-resolution | not checked |
| What is the maximum number of live-judging requests per minute that can be made against a single chat completion event via this endpoint? | `sec128-lexical-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/chat_completion_events#operation-judge_chat_completion_event_v1_observability_chat_completion_events_event_id_live_judging_post | not checked |
| Is there a limit on how many fine-tuned custom models I can have active at the same time on my Mistral AI account? | `sec128-lexical-heavy` | https://docs.mistral.ai/studio/observability/evaluations/datasets#how-large-can-my-dataset-be | not checked |
| Does Mistral AI's documentation specify any recommended or maximum token budget for an LLM judge prompt when evaluating large evaluation sets? | `sec128-lexical-heavy` | https://docs.mistral.ai/studio/observability/evaluations/judges#basic-llm-judge | not checked |
| Is there a way to export or share the todos list from the Work panel once a task is complete? | `sec128-lexical-heavy` | https://docs.mistral.ai/vibe/work/safety-and-approvals#todos-panel | not checked |
| What is the maximum number of span field definitions that the Get span fields endpoint can return in a single response, and is there pagination support? | `sec128-lexical-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_fields_v1_observability_spans_fields_get | not checked |
| Is there an API to programmatically list or delete reusable Prompts, and what are the rate limits for Prompt execution? | `sec128-lexical-heavy` | https://docs.mistral.ai/getting-started/quickstarts/studio/create-reusable-prompt#verify | not checked |
| Does Mistral Document AI on Azure impose a maximum page count per document for processing, and if so, what is the limit? | `sec128-lexical-heavy` | https://docs.mistral.ai/vibe/work/libraries#limits | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Magistral Small 1.0? | `sec128-lexical-heavy` | https://docs.mistral.ai/studio/conversations/vision#whats-the-maximum-number-images-per-request | not checked |
| What is the maximum file size allowed for a FileField upload, and is there a limit on the number of files when multiple=True? | `sec128-lexical-heavy` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#whats-the-size-limit-of-the-training-data | not checked |
| Is there a timeout or expiration period for the open SSO configuration modal after which the setup must be restarted? | `sec128-heading-path-off` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso#start-in-admin | not checked |
| What is the maximum retention period for a SCIM sync run's result before it is deleted, and can completed runs be purged early via the API? | `sec128-heading-path-off` | https://docs.mistral.ai/api/endpoint/beta/admin/scim#operation-users_api_admin_scim_sync_get_scim_sync_run | not checked |
| Is there a maximum number of Organizations that can be linked to a single Enterprise Account, and what happens if that limit is exceeded? | `sec128-heading-path-off` | https://docs.mistral.ai/admin/set-up-organization/enterprise-accounts#organizations | not checked |
| What is the maximum historical retention period for usage data retrievable via the Get Usage endpoint? | `sec128-heading-path-off` | https://docs.mistral.ai/admin/monitor-comply/zero-data-retention#what-zdr-covers | not checked |
| What is the maximum number of messages allowed in a single chat completion request? | `sec128-heading-path-off` | https://docs.mistral.ai/studio/conversations/vision#whats-the-maximum-number-images-per-request | not checked |
| Does the Mistral GCP deployment support server-side prompt caching, and is there a cache hit discount on rawPredict calls? | `sec128-heading-path-off` | https://docs.mistral.ai/studio/conversations/advanced/prompt-caching | not checked |
| What is the maximum number of web pages MistralAI-User may visit for a single user request in Vibe, and is there a per-minute rate limit? | `sec128-heading-path-off` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Does `mistral-vespa generate` validate that the output directory is empty before writing, or does it have a flag to force overwriting existing files? | `sec128-heading-path-off` | https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli#generate | not checked |
| Is there a keyboard shortcut to switch directly to Work mode from Chat or Code without opening the sidebar? | `sec128-heading-path-off` | https://docs.mistral.ai/getting-started/quickstarts/vibe-work/first-task#step-1 | not checked |
| Is there a maximum number of credentials (API keys or workload identity credentials) that can be attached to a single service account? | `sec128-heading-path-off` | https://docs.mistral.ai/admin/identity-access/workload-identity#how-setup-works | not checked |
| Is there a limit on the number of handoff targets an agent can have, and what happens if a handoff references a nonexistent agent? | `sec128-heading-path-off` | https://docs.mistral.ai/studio/agents/handoffs#how-it-works | not checked |
| What is the maximum number of API keys a single Mistral AI account can generate? | `sec128-heading-path-off` | https://docs.mistral.ai/api/endpoint/beta/admin/api-keys#operation-users_api_admin_api_keys_get_api_keys | not checked |
| Is there a recommended maximum length or word limit for the role statement when providing a purpose in a prompt? | `sec128-heading-path-off` | https://docs.mistral.ai/inference/prompting#purpose | not checked |
| Is there a limit on how many agents a single account or workspace can create? | `sec128-heading-path-off` | https://docs.mistral.ai/studio/agents/handoffs#create-an-agentic-workflow | not checked |
| How long does an invitation remain valid before it expires, and can the expiration period be customized? | `sec128-heading-path-off` | https://docs.mistral.ai/admin/identity-access/api-key-policy#default-state | not checked |
| What is the maximum number of selected event ids returned in a single ListCampaignSelectedEventsResponse, and does the endpoint support pagination? | `sec128-heading-path-off` | https://docs.mistral.ai/api/endpoint/beta/observability/campaigns#operation-get_campaign_selected_events_v1_observability_campaigns_campaign_id_selected_events_get | not checked |
| What is the minimum GPU VRAM requirement to fine-tune the Ministral 3 14B Instruct weights locally? | `sec128-heading-path-off` | https://docs.mistral.ai/models/ministral-3-14b-25-12 | not checked |
| Is there a maximum character or token length enforced for system prompts in Mistral models, and what happens if it is exceeded? | `sec128-heading-path-off` | https://docs.mistral.ai/admin/identity-access/api-key-policy#workspace-limit-above-org-limit | not checked |
| What is the per-token price charged when pay-as-you-go usage kicks in after the included monthly allowance is exhausted? | `sec128-heading-path-off` | https://docs.mistral.ai/admin/billing-usage/subscriptions#included-monthly-usage | not checked |
| Is there a maximum number of campaigns that can be stored or returned per request, and is there a pagination limit for the campaigns list? | `sec128-heading-path-off` | https://docs.mistral.ai/studio/batch-processing#whats-the-max-number-of-batch-jobs-one-can-create | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Ministral 3 8B? | `sec128-heading-path-off` | https://docs.mistral.ai/getting-started/quickstarts/developer/rag-document-search#verify | not checked |
| What is the maximum rate at which MistralAI-User requests can be sent to a single site during user actions in Vibe? | `sec128-heading-path-off` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Can I apply document_annotation_format when passing an image (ImageURLChunk) instead of a PDF document, and does the annotation then apply per image? | `sec128-heading-path-off` | https://docs.mistral.ai/studio/document-processing/annotations#usage | not checked |
| Is there a limit on how many hooks can be declared, or a defined execution order when multiple hooks match the same tool call? | `sec128-heading-path-off` | https://docs.mistral.ai/vibe/code/cli/hooks#post-tool | not checked |
| Does the platform offer a grace period or retry policy for failed invoice payments before account suspension? | `sec128-heading-path-off` | https://docs.mistral.ai/studio/observability/evaluations/retry-failed-records | not checked |
| Is there a rate limit on how many observability datasets can be deleted per minute via the API? | `sec128-heading-path-off` | https://docs.mistral.ai/studio/observability/evaluations/datasets#how-large-can-my-dataset-be | not checked |
| What is the maximum total byte size allowed for a request body before a 400 error is returned? | `sec128-heading-path-off` | https://docs.mistral.ai/resources/error-glossary#400-bad-request | not checked |
| Is there a timeout limit for code interpreter executions, and what happens if the executed code exceeds it? | `sec128-heading-path-off` | https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#explanation-of-the-output | not checked |
| Is there a limit on how many agents can be created per workspace or per API key? | `sec128-heading-path-off` | https://docs.mistral.ai/vibe/work/switch-organization-workspace#scoped | not checked |
| When deleting a judge that is currently referenced by active evaluations, does the API return a 409 Conflict, or does the deletion succeed and leave the evaluations without a judge? | `sec128-heading-path-off` | https://docs.mistral.ai/studio/observability/evaluations#how-do-i-use-an-llm-as-a-judge | not checked |
| Is there a way to configure a timeout so that pending approval prompts auto-reject if left unanswered, and can that timeout duration be customized? | `sec128-heading-path-off` | https://docs.mistral.ai/studio/workflows/interacting-with-workflows/conversational_workflows#timeout | not checked |
| What are the specific numeric rate limits per model included in the custom Priority Tier limits? | `sec128-heading-path-off` | https://docs.mistral.ai/inference/priority-tier#quotas-and-limits | not checked |
| What is the maximum number of fine-tuning jobs that can run concurrently per project on the fine-tuning API? | `sec128-heading-path-off` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#jobs-management | not checked |
| Is there an air-gapped license validation mode, and how often does an offline installation re-check entitlements before degrading? | `sec128-heading-path-off` | https://docs.mistral.ai/vibe/code/cli/install-setup#prerequisites | not checked |
| Is there a way to automatically revoke API keys and deactivate active sessions for a member the moment they are removed from the Organization? | `sec128-heading-path-off` | https://docs.mistral.ai/admin/identity-access/user-management#manage-members | not checked |
| Is there a limit on the number of characters or options allowed in the instructions or JudgeClassificationOutput options fields? | `sec128-heading-path-off` | https://docs.mistral.ai/api/endpoint/beta/observability/judges#operation-update_judge_v1_observability_judges_judge_id_put | not checked |
| Is there a limit on the number of users that can auto-join per day through email-domain authentication, or a maximum organization size it enforces? | `sec128-heading-path-off` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/email-domain-authentication | not checked |
| What are the valid ranges or allowed values for the learning_rate hyperparameter when creating a classifier fine-tuning job? | `sec128-heading-path-off` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#what-is-the-recommended-learning-rate | not checked |
| Is there a documented rate limit or maximum number of page visits MistralAI-User will make per user request in Vibe? | `sec128-heading-path-off` | https://docs.mistral.ai/api/endpoint/beta/admin/user-groups#operation-users_api_admin_user_groups_get_user_groups | not checked |
| Is there a documented maximum number of concurrent token-stream tasks a single workflow can run, and what happens if that limit is exceeded? | `sec128-heading-path-off` | https://docs.mistral.ai/studio/workflows/managing-workflows-in-production/concurrency#configuration-options-offset | not checked |
| What is the maximum disk size available in the sandbox's default image, and can it be increased? | `sec128-heading-path-off` | https://docs.mistral.ai/studio/conversations/vision#how-many-tokens-correspond-to-an-image-andor-what-is-the-maximum-resolution | not checked |
| What is the maximum number of live-judging requests per minute that can be made against a single chat completion event via this endpoint? | `sec128-heading-path-off` | https://docs.mistral.ai/api/endpoint/beta/observability/chat_completion_events#operation-judge_chat_completion_event_v1_observability_chat_completion_events_event_id_live_judging_post | not checked |
| Is there a limit on how many fine-tuned custom models I can have active at the same time on my Mistral AI account? | `sec128-heading-path-off` | https://docs.mistral.ai/vibe/work/libraries#data-privacy | not checked |
| Does Mistral AI's documentation specify any recommended or maximum token budget for an LLM judge prompt when evaluating large evaluation sets? | `sec128-heading-path-off` | https://docs.mistral.ai/studio/observability/evaluations/judges#basic-llm-judge | not checked |
| Is there a way to export or share the todos list from the Work panel once a task is complete? | `sec128-heading-path-off` | https://docs.mistral.ai/vibe/work/safety-and-approvals#todos-panel | not checked |
| What is the maximum number of span field definitions that the Get span fields endpoint can return in a single response, and is there pagination support? | `sec128-heading-path-off` | https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_fields_v1_observability_spans_fields_get | not checked |
| Is there an API to programmatically list or delete reusable Prompts, and what are the rate limits for Prompt execution? | `sec128-heading-path-off` | https://docs.mistral.ai/getting-started/quickstarts/studio/create-reusable-prompt#verify | not checked |
| Does Mistral Document AI on Azure impose a maximum page count per document for processing, and if so, what is the limit? | `sec128-heading-path-off` | https://docs.mistral.ai/vibe/work/libraries#limits | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Magistral Small 1.0? | `sec128-heading-path-off` | https://docs.mistral.ai/studio/document-processing/document_qna#usage | not checked |
| What is the maximum file size allowed for a FileField upload, and is there a limit on the number of files when multiple=True? | `sec128-heading-path-off` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#whats-the-size-limit-of-the-training-data | not checked |
| Is there a timeout or expiration period for the open SSO configuration modal after which the setup must be restarted? | `sec1024-shipped` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso#start-in-admin | not checked |
| What is the maximum retention period for a SCIM sync run's result before it is deleted, and can completed runs be purged early via the API? | `sec1024-shipped` | https://docs.mistral.ai/api/endpoint/beta/admin/scim#operation-users_api_admin_scim_sync_get_scim_sync_run | not checked |
| Is there a maximum number of Organizations that can be linked to a single Enterprise Account, and what happens if that limit is exceeded? | `sec1024-shipped` | https://docs.mistral.ai/admin/set-up-organization/enterprise-accounts#organizations | not checked |
| What is the maximum historical retention period for usage data retrievable via the Get Usage endpoint? | `sec1024-shipped` | https://docs.mistral.ai/admin/monitor-comply/zero-data-retention#what-zdr-covers | not checked |
| What is the maximum number of messages allowed in a single chat completion request? | `sec1024-shipped` | https://docs.mistral.ai/studio/conversations/chat-completion#chat-completion | not checked |
| Does the Mistral GCP deployment support server-side prompt caching, and is there a cache hit discount on rawPredict calls? | `sec1024-shipped` | https://docs.mistral.ai/studio/conversations/advanced/prompt-caching | not checked |
| What is the maximum number of web pages MistralAI-User may visit for a single user request in Vibe, and is there a per-minute rate limit? | `sec1024-shipped` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Does `mistral-vespa generate` validate that the output directory is empty before writing, or does it have a flag to force overwriting existing files? | `sec1024-shipped` | https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli#generate | not checked |
| Is there a keyboard shortcut to switch directly to Work mode from Chat or Code without opening the sidebar? | `sec1024-shipped` | https://docs.mistral.ai/getting-started/quickstarts/vibe-work/first-task#step-1 | not checked |
| Is there a maximum number of credentials (API keys or workload identity credentials) that can be attached to a single service account? | `sec1024-shipped` | https://docs.mistral.ai/admin/identity-access/workload-identity#how-setup-works | not checked |
| Is there a limit on the number of handoff targets an agent can have, and what happens if a handoff references a nonexistent agent? | `sec1024-shipped` | https://docs.mistral.ai/studio/agents/agents-api | not checked |
| What is the maximum number of API keys a single Mistral AI account can generate? | `sec1024-shipped` | https://docs.mistral.ai/studio/batch-processing#whats-the-max-number-of-batch-jobs-one-can-create | not checked |
| Is there a recommended maximum length or word limit for the role statement when providing a purpose in a prompt? | `sec1024-shipped` | https://docs.mistral.ai/studio/conversations/chat-completion/prompting#purpose | not checked |
| Is there a limit on how many agents a single account or workspace can create? | `sec1024-shipped` | https://docs.mistral.ai/studio/agents/handoffs#create-an-agentic-workflow | not checked |
| How long does an invitation remain valid before it expires, and can the expiration period be customized? | `sec1024-shipped` | https://docs.mistral.ai/studio/batch-processing#how-long-does-the-batch-api-take-to-process | not checked |
| What is the maximum number of selected event ids returned in a single ListCampaignSelectedEventsResponse, and does the endpoint support pagination? | `sec1024-shipped` | https://docs.mistral.ai/api/endpoint/beta/observability/campaigns#operation-get_campaign_selected_events_v1_observability_campaigns_campaign_id_selected_events_get | not checked |
| What is the minimum GPU VRAM requirement to fine-tune the Ministral 3 14B Instruct weights locally? | `sec1024-shipped` | https://docs.mistral.ai/models/ministral-3-14b-25-12 | not checked |
| Is there a maximum character or token length enforced for system prompts in Mistral models, and what happens if it is exceeded? | `sec1024-shipped` | https://docs.mistral.ai/admin/identity-access/api-key-policy#workspace-limit-above-org-limit | not checked |
| What is the per-token price charged when pay-as-you-go usage kicks in after the included monthly allowance is exhausted? | `sec1024-shipped` | https://docs.mistral.ai/admin/billing-usage/subscriptions#included-monthly-usage | not checked |
| Is there a maximum number of campaigns that can be stored or returned per request, and is there a pagination limit for the campaigns list? | `sec1024-shipped` | https://docs.mistral.ai/studio/batch-processing#whats-the-max-number-of-batch-jobs-one-can-create | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Ministral 3 8B? | `sec1024-shipped` | https://docs.mistral.ai/models/ministral-3-8b-25-12 | not checked |
| What is the maximum rate at which MistralAI-User requests can be sent to a single site during user actions in Vibe? | `sec1024-shipped` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Can I apply document_annotation_format when passing an image (ImageURLChunk) instead of a PDF document, and does the annotation then apply per image? | `sec1024-shipped` | https://docs.mistral.ai/studio/document-processing/annotations#usage | not checked |
| Is there a limit on how many hooks can be declared, or a defined execution order when multiple hooks match the same tool call? | `sec1024-shipped` | https://docs.mistral.ai/vibe/code/cli/hooks#file-locations | not checked |
| Does the platform offer a grace period or retry policy for failed invoice payments before account suspension? | `sec1024-shipped` | https://docs.mistral.ai/studio/observability/evaluations/retry-failed-records#fixing-the-task-before-retrying | not checked |
| Is there a rate limit on how many observability datasets can be deleted per minute via the API? | `sec1024-shipped` | https://docs.mistral.ai/studio/observability/evaluations/datasets#how-large-can-my-dataset-be | not checked |
| What is the maximum total byte size allowed for a request body before a 400 error is returned? | `sec1024-shipped` | https://docs.mistral.ai/resources/error-glossary#400-bad-request | not checked |
| Is there a timeout limit for code interpreter executions, and what happens if the executed code exceeds it? | `sec1024-shipped` | https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#explanation-of-the-output | not checked |
| Is there a limit on how many agents can be created per workspace or per API key? | `sec1024-shipped` | https://docs.mistral.ai/vibe/work/switch-organization-workspace#scoped | not checked |
| When deleting a judge that is currently referenced by active evaluations, does the API return a 409 Conflict, or does the deletion succeed and leave the evaluations without a judge? | `sec1024-shipped` | https://docs.mistral.ai/studio/observability/evaluations#how-do-i-use-an-llm-as-a-judge | not checked |
| Is there a way to configure a timeout so that pending approval prompts auto-reject if left unanswered, and can that timeout duration be customized? | `sec1024-shipped` | https://docs.mistral.ai/studio/workflows/interacting-with-workflows/conversational_workflows#timeout | not checked |
| What are the specific numeric rate limits per model included in the custom Priority Tier limits? | `sec1024-shipped` | https://docs.mistral.ai/inference/priority-tier#quotas-and-limits | not checked |
| What is the maximum number of fine-tuning jobs that can run concurrently per project on the fine-tuning API? | `sec1024-shipped` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#jobs-management | not checked |
| Is there an air-gapped license validation mode, and how often does an offline installation re-check entitlements before degrading? | `sec1024-shipped` | https://docs.mistral.ai/studio/observability/evaluations#how-do-i-use-an-llm-as-a-judge | not checked |
| Is there a way to automatically revoke API keys and deactivate active sessions for a member the moment they are removed from the Organization? | `sec1024-shipped` | https://docs.mistral.ai/admin/identity-access/user-management#remove-members | not checked |
| Is there a limit on the number of characters or options allowed in the instructions or JudgeClassificationOutput options fields? | `sec1024-shipped` | https://docs.mistral.ai/api/endpoint/beta/observability/datasets/records#operation-judge_dataset_record_v1_observability_dataset_records_dataset_record_id_live_judging_post | not checked |
| Is there a limit on the number of users that can auto-join per day through email-domain authentication, or a maximum organization size it enforces? | `sec1024-shipped` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/email-domain-authentication | not checked |
| What are the valid ranges or allowed values for the learning_rate hyperparameter when creating a classifier fine-tuning job? | `sec1024-shipped` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#what-is-the-recommended-learning-rate | not checked |
| Is there a documented rate limit or maximum number of page visits MistralAI-User will make per user request in Vibe? | `sec1024-shipped` | https://docs.mistral.ai/studio/conversations/vision#whats-the-maximum-number-images-per-request | not checked |
| Is there a documented maximum number of concurrent token-stream tasks a single workflow can run, and what happens if that limit is exceeded? | `sec1024-shipped` | https://docs.mistral.ai/admin/identity-access/api-key-policy#workspace-limit-above-org-limit | not checked |
| What is the maximum disk size available in the sandbox's default image, and can it be increased? | `sec1024-shipped` | https://docs.mistral.ai/studio/conversations/vision#how-many-tokens-correspond-to-an-image-andor-what-is-the-maximum-resolution | not checked |
| What is the maximum number of live-judging requests per minute that can be made against a single chat completion event via this endpoint? | `sec1024-shipped` | https://docs.mistral.ai/api/endpoint/beta/observability/chat_completion_events#operation-judge_chat_completion_event_v1_observability_chat_completion_events_event_id_live_judging_post | not checked |
| Is there a limit on how many fine-tuned custom models I can have active at the same time on my Mistral AI account? | `sec1024-shipped` | https://docs.mistral.ai/studio/observability/evaluations/datasets#how-large-can-my-dataset-be | not checked |
| Does Mistral AI's documentation specify any recommended or maximum token budget for an LLM judge prompt when evaluating large evaluation sets? | `sec1024-shipped` | https://docs.mistral.ai/studio/observability/evaluations/judges#basic-llm-judge | not checked |
| Is there a way to export or share the todos list from the Work panel once a task is complete? | `sec1024-shipped` | https://docs.mistral.ai/vibe/work/safety-and-approvals#todos-panel | not checked |
| What is the maximum number of span field definitions that the Get span fields endpoint can return in a single response, and is there pagination support? | `sec1024-shipped` | https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_fields_v1_observability_spans_fields_get | not checked |
| Is there an API to programmatically list or delete reusable Prompts, and what are the rate limits for Prompt execution? | `sec1024-shipped` | https://docs.mistral.ai/getting-started/quickstarts/studio/create-reusable-prompt#verify | not checked |
| Does Mistral Document AI on Azure impose a maximum page count per document for processing, and if so, what is the limit? | `sec1024-shipped` | https://docs.mistral.ai/vibe/work/libraries#limits | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Magistral Small 1.0? | `sec1024-shipped` | https://docs.mistral.ai/studio/document-processing/document_qna#usage | not checked |
| What is the maximum file size allowed for a FileField upload, and is there a limit on the number of files when multiple=True? | `sec1024-shipped` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#whats-the-size-limit-of-the-training-data | not checked |
| Is there a timeout or expiration period for the open SSO configuration modal after which the setup must be restarted? | `sec1024-vector-heavy` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso#start-in-admin | not checked |
| What is the maximum retention period for a SCIM sync run's result before it is deleted, and can completed runs be purged early via the API? | `sec1024-vector-heavy` | https://docs.mistral.ai/api/endpoint/beta/admin/scim#operation-users_api_admin_scim_sync_get_scim_sync_run | not checked |
| Is there a maximum number of Organizations that can be linked to a single Enterprise Account, and what happens if that limit is exceeded? | `sec1024-vector-heavy` | https://docs.mistral.ai/admin/set-up-organization/enterprise-accounts#organizations | not checked |
| What is the maximum historical retention period for usage data retrievable via the Get Usage endpoint? | `sec1024-vector-heavy` | https://docs.mistral.ai/admin/monitor-comply/zero-data-retention#what-zdr-covers | not checked |
| What is the maximum number of messages allowed in a single chat completion request? | `sec1024-vector-heavy` | https://docs.mistral.ai/studio/conversations/chat-completion#chat-completion | not checked |
| Does the Mistral GCP deployment support server-side prompt caching, and is there a cache hit discount on rawPredict calls? | `sec1024-vector-heavy` | https://docs.mistral.ai/studio/conversations/advanced/prompt-caching | not checked |
| What is the maximum number of web pages MistralAI-User may visit for a single user request in Vibe, and is there a per-minute rate limit? | `sec1024-vector-heavy` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Does `mistral-vespa generate` validate that the output directory is empty before writing, or does it have a flag to force overwriting existing files? | `sec1024-vector-heavy` | https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli#generate | not checked |
| Is there a keyboard shortcut to switch directly to Work mode from Chat or Code without opening the sidebar? | `sec1024-vector-heavy` | https://docs.mistral.ai/vibe/work/switch-organization-workspace#switcher | not checked |
| Is there a maximum number of credentials (API keys or workload identity credentials) that can be attached to a single service account? | `sec1024-vector-heavy` | https://docs.mistral.ai/admin/identity-access/workload-identity#how-setup-works | not checked |
| Is there a limit on the number of handoff targets an agent can have, and what happens if a handoff references a nonexistent agent? | `sec1024-vector-heavy` | https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#multi-agent-handoffs | not checked |
| What is the maximum number of API keys a single Mistral AI account can generate? | `sec1024-vector-heavy` | https://docs.mistral.ai/studio/conversations/vision#whats-the-maximum-number-images-per-request | not checked |
| Is there a recommended maximum length or word limit for the role statement when providing a purpose in a prompt? | `sec1024-vector-heavy` | https://docs.mistral.ai/inference/prompting#purpose | not checked |
| Is there a limit on how many agents a single account or workspace can create? | `sec1024-vector-heavy` | https://docs.mistral.ai/studio/agents/handoffs#create-an-agentic-workflow | not checked |
| How long does an invitation remain valid before it expires, and can the expiration period be customized? | `sec1024-vector-heavy` | https://docs.mistral.ai/admin/identity-access/api-key-policy#default-state | not checked |
| What is the maximum number of selected event ids returned in a single ListCampaignSelectedEventsResponse, and does the endpoint support pagination? | `sec1024-vector-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/campaigns#operation-get_campaign_selected_events_v1_observability_campaigns_campaign_id_selected_events_get | not checked |
| What is the minimum GPU VRAM requirement to fine-tune the Ministral 3 14B Instruct weights locally? | `sec1024-vector-heavy` | https://docs.mistral.ai/models/ministral-3-14b-25-12 | not checked |
| Is there a maximum character or token length enforced for system prompts in Mistral models, and what happens if it is exceeded? | `sec1024-vector-heavy` | https://docs.mistral.ai/vibe/code/vibe-code-web/slack-integration#what-happens-next | not checked |
| What is the per-token price charged when pay-as-you-go usage kicks in after the included monthly allowance is exhausted? | `sec1024-vector-heavy` | https://docs.mistral.ai/admin/billing-usage/subscriptions#included-monthly-usage | not checked |
| Is there a maximum number of campaigns that can be stored or returned per request, and is there a pagination limit for the campaigns list? | `sec1024-vector-heavy` | https://docs.mistral.ai/studio/batch-processing#whats-the-max-number-of-batch-jobs-one-can-create | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Ministral 3 8B? | `sec1024-vector-heavy` | https://docs.mistral.ai/models/ministral-3-8b-25-12 | not checked |
| What is the maximum rate at which MistralAI-User requests can be sent to a single site during user actions in Vibe? | `sec1024-vector-heavy` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Can I apply document_annotation_format when passing an image (ImageURLChunk) instead of a PDF document, and does the annotation then apply per image? | `sec1024-vector-heavy` | https://docs.mistral.ai/studio/document-processing/annotations#usage | not checked |
| Is there a limit on how many hooks can be declared, or a defined execution order when multiple hooks match the same tool call? | `sec1024-vector-heavy` | https://docs.mistral.ai/vibe/code/cli/hooks#post-tool | not checked |
| Does the platform offer a grace period or retry policy for failed invoice payments before account suspension? | `sec1024-vector-heavy` | https://docs.mistral.ai/studio/observability/evaluations/retry-failed-records | not checked |
| Is there a rate limit on how many observability datasets can be deleted per minute via the API? | `sec1024-vector-heavy` | https://docs.mistral.ai/studio/observability/evaluations/datasets#how-large-can-my-dataset-be | not checked |
| What is the maximum total byte size allowed for a request body before a 400 error is returned? | `sec1024-vector-heavy` | https://docs.mistral.ai/resources/error-glossary#400-bad-request | not checked |
| Is there a timeout limit for code interpreter executions, and what happens if the executed code exceeds it? | `sec1024-vector-heavy` | https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#explanation-of-the-output | not checked |
| Is there a limit on how many agents can be created per workspace or per API key? | `sec1024-vector-heavy` | https://docs.mistral.ai/vibe/work/switch-organization-workspace#scoped | not checked |
| When deleting a judge that is currently referenced by active evaluations, does the API return a 409 Conflict, or does the deletion succeed and leave the evaluations without a judge? | `sec1024-vector-heavy` | https://docs.mistral.ai/studio/observability/evaluations#how-do-i-use-an-llm-as-a-judge | not checked |
| Is there a way to configure a timeout so that pending approval prompts auto-reject if left unanswered, and can that timeout duration be customized? | `sec1024-vector-heavy` | https://docs.mistral.ai/studio/workflows/interacting-with-workflows/conversational_workflows#timeout | not checked |
| What are the specific numeric rate limits per model included in the custom Priority Tier limits? | `sec1024-vector-heavy` | https://docs.mistral.ai/inference/priority-tier#quotas-and-limits | not checked |
| What is the maximum number of fine-tuning jobs that can run concurrently per project on the fine-tuning API? | `sec1024-vector-heavy` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#jobs-management | not checked |
| Is there an air-gapped license validation mode, and how often does an offline installation re-check entitlements before degrading? | `sec1024-vector-heavy` | https://docs.mistral.ai/studio/observability/evaluations#how-do-i-use-an-llm-as-a-judge | not checked |
| Is there a way to automatically revoke API keys and deactivate active sessions for a member the moment they are removed from the Organization? | `sec1024-vector-heavy` | https://docs.mistral.ai/admin/identity-access/user-management#remove-members | not checked |
| Is there a limit on the number of characters or options allowed in the instructions or JudgeClassificationOutput options fields? | `sec1024-vector-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/datasets/records#operation-judge_dataset_record_v1_observability_dataset_records_dataset_record_id_live_judging_post | not checked |
| Is there a limit on the number of users that can auto-join per day through email-domain authentication, or a maximum organization size it enforces? | `sec1024-vector-heavy` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/email-domain-authentication | not checked |
| What are the valid ranges or allowed values for the learning_rate hyperparameter when creating a classifier fine-tuning job? | `sec1024-vector-heavy` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#what-is-the-recommended-learning-rate | not checked |
| Is there a documented rate limit or maximum number of page visits MistralAI-User will make per user request in Vibe? | `sec1024-vector-heavy` | https://docs.mistral.ai/studio/conversations/vision#whats-the-maximum-number-images-per-request | not checked |
| Is there a documented maximum number of concurrent token-stream tasks a single workflow can run, and what happens if that limit is exceeded? | `sec1024-vector-heavy` | https://docs.mistral.ai/admin/identity-access/api-key-policy#workspace-limit-above-org-limit | not checked |
| What is the maximum disk size available in the sandbox's default image, and can it be increased? | `sec1024-vector-heavy` | https://docs.mistral.ai/studio/conversations/vision#how-many-tokens-correspond-to-an-image-andor-what-is-the-maximum-resolution | not checked |
| What is the maximum number of live-judging requests per minute that can be made against a single chat completion event via this endpoint? | `sec1024-vector-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/chat_completion_events#operation-judge_chat_completion_event_v1_observability_chat_completion_events_event_id_live_judging_post | not checked |
| Is there a limit on how many fine-tuned custom models I can have active at the same time on my Mistral AI account? | `sec1024-vector-heavy` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#fine-tuned-models | not checked |
| Does Mistral AI's documentation specify any recommended or maximum token budget for an LLM judge prompt when evaluating large evaluation sets? | `sec1024-vector-heavy` | https://docs.mistral.ai/studio/observability/evaluations/judges#basic-llm-judge | not checked |
| Is there a way to export or share the todos list from the Work panel once a task is complete? | `sec1024-vector-heavy` | https://docs.mistral.ai/vibe/work/safety-and-approvals#todos-panel | not checked |
| What is the maximum number of span field definitions that the Get span fields endpoint can return in a single response, and is there pagination support? | `sec1024-vector-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_fields_v1_observability_spans_fields_get | not checked |
| Is there an API to programmatically list or delete reusable Prompts, and what are the rate limits for Prompt execution? | `sec1024-vector-heavy` | https://docs.mistral.ai/getting-started/quickstarts/studio/create-reusable-prompt#verify | not checked |
| Does Mistral Document AI on Azure impose a maximum page count per document for processing, and if so, what is the limit? | `sec1024-vector-heavy` | https://docs.mistral.ai/inference/deployment/cloud-deployments/azure | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Magistral Small 1.0? | `sec1024-vector-heavy` | https://docs.mistral.ai/studio/document-processing/document_qna#usage | not checked |
| What is the maximum file size allowed for a FileField upload, and is there a limit on the number of files when multiple=True? | `sec1024-vector-heavy` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#whats-the-size-limit-of-the-training-data | not checked |
| Is there a timeout or expiration period for the open SSO configuration modal after which the setup must be restarted? | `sec1024-lexical-heavy` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso#start-in-admin | not checked |
| What is the maximum retention period for a SCIM sync run's result before it is deleted, and can completed runs be purged early via the API? | `sec1024-lexical-heavy` | https://docs.mistral.ai/api/endpoint/beta/admin/scim#operation-users_api_admin_scim_sync_get_scim_sync_run | not checked |
| Is there a maximum number of Organizations that can be linked to a single Enterprise Account, and what happens if that limit is exceeded? | `sec1024-lexical-heavy` | https://docs.mistral.ai/admin/set-up-organization/enterprise-accounts#organizations | not checked |
| What is the maximum historical retention period for usage data retrievable via the Get Usage endpoint? | `sec1024-lexical-heavy` | https://docs.mistral.ai/admin/monitor-comply/zero-data-retention#what-zdr-covers | not checked |
| What is the maximum number of messages allowed in a single chat completion request? | `sec1024-lexical-heavy` | https://docs.mistral.ai/studio/conversations/chat-completion#chat-completion | not checked |
| Does the Mistral GCP deployment support server-side prompt caching, and is there a cache hit discount on rawPredict calls? | `sec1024-lexical-heavy` | https://docs.mistral.ai/studio/conversations/advanced/prompt-caching | not checked |
| What is the maximum number of web pages MistralAI-User may visit for a single user request in Vibe, and is there a per-minute rate limit? | `sec1024-lexical-heavy` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Does `mistral-vespa generate` validate that the output directory is empty before writing, or does it have a flag to force overwriting existing files? | `sec1024-lexical-heavy` | https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli#generate | not checked |
| Is there a keyboard shortcut to switch directly to Work mode from Chat or Code without opening the sidebar? | `sec1024-lexical-heavy` | https://docs.mistral.ai/getting-started/quickstarts/vibe-work/first-task#step-1 | not checked |
| Is there a maximum number of credentials (API keys or workload identity credentials) that can be attached to a single service account? | `sec1024-lexical-heavy` | https://docs.mistral.ai/admin/identity-access/workload-identity#how-setup-works | not checked |
| Is there a limit on the number of handoff targets an agent can have, and what happens if a handoff references a nonexistent agent? | `sec1024-lexical-heavy` | https://docs.mistral.ai/studio/agents/agents-api | not checked |
| What is the maximum number of API keys a single Mistral AI account can generate? | `sec1024-lexical-heavy` | https://docs.mistral.ai/studio/batch-processing#whats-the-max-number-of-batch-jobs-one-can-create | not checked |
| Is there a recommended maximum length or word limit for the role statement when providing a purpose in a prompt? | `sec1024-lexical-heavy` | https://docs.mistral.ai/studio/conversations/chat-completion/prompting#purpose | not checked |
| Is there a limit on how many agents a single account or workspace can create? | `sec1024-lexical-heavy` | https://docs.mistral.ai/studio/agents/handoffs#create-an-agentic-workflow | not checked |
| How long does an invitation remain valid before it expires, and can the expiration period be customized? | `sec1024-lexical-heavy` | https://docs.mistral.ai/studio/batch-processing#how-long-does-the-batch-api-take-to-process | not checked |
| What is the maximum number of selected event ids returned in a single ListCampaignSelectedEventsResponse, and does the endpoint support pagination? | `sec1024-lexical-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/campaigns#operation-get_campaign_selected_events_v1_observability_campaigns_campaign_id_selected_events_get | not checked |
| What is the minimum GPU VRAM requirement to fine-tune the Ministral 3 14B Instruct weights locally? | `sec1024-lexical-heavy` | https://docs.mistral.ai/models/ministral-3-14b-25-12 | not checked |
| Is there a maximum character or token length enforced for system prompts in Mistral models, and what happens if it is exceeded? | `sec1024-lexical-heavy` | https://docs.mistral.ai/admin/identity-access/api-key-policy#workspace-limit-above-org-limit | not checked |
| What is the per-token price charged when pay-as-you-go usage kicks in after the included monthly allowance is exhausted? | `sec1024-lexical-heavy` | https://docs.mistral.ai/admin/billing-usage/subscriptions#included-monthly-usage | not checked |
| Is there a maximum number of campaigns that can be stored or returned per request, and is there a pagination limit for the campaigns list? | `sec1024-lexical-heavy` | https://docs.mistral.ai/studio/batch-processing#whats-the-max-number-of-batch-jobs-one-can-create | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Ministral 3 8B? | `sec1024-lexical-heavy` | https://docs.mistral.ai/getting-started/quickstarts/developer/rag-document-search#verify | not checked |
| What is the maximum rate at which MistralAI-User requests can be sent to a single site during user actions in Vibe? | `sec1024-lexical-heavy` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Can I apply document_annotation_format when passing an image (ImageURLChunk) instead of a PDF document, and does the annotation then apply per image? | `sec1024-lexical-heavy` | https://docs.mistral.ai/studio/document-processing/annotations#usage | not checked |
| Is there a limit on how many hooks can be declared, or a defined execution order when multiple hooks match the same tool call? | `sec1024-lexical-heavy` | https://docs.mistral.ai/vibe/code/cli/hooks#file-locations | not checked |
| Does the platform offer a grace period or retry policy for failed invoice payments before account suspension? | `sec1024-lexical-heavy` | https://docs.mistral.ai/studio/observability/evaluations/retry-failed-records#fixing-the-task-before-retrying | not checked |
| Is there a rate limit on how many observability datasets can be deleted per minute via the API? | `sec1024-lexical-heavy` | https://docs.mistral.ai/studio/observability/evaluations/datasets#how-large-can-my-dataset-be | not checked |
| What is the maximum total byte size allowed for a request body before a 400 error is returned? | `sec1024-lexical-heavy` | https://docs.mistral.ai/resources/error-glossary#400-bad-request | not checked |
| Is there a timeout limit for code interpreter executions, and what happens if the executed code exceeds it? | `sec1024-lexical-heavy` | https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#explanation-of-the-output | not checked |
| Is there a limit on how many agents can be created per workspace or per API key? | `sec1024-lexical-heavy` | https://docs.mistral.ai/vibe/work/switch-organization-workspace#scoped | not checked |
| When deleting a judge that is currently referenced by active evaluations, does the API return a 409 Conflict, or does the deletion succeed and leave the evaluations without a judge? | `sec1024-lexical-heavy` | https://docs.mistral.ai/studio/observability/evaluations#how-do-i-use-an-llm-as-a-judge | not checked |
| Is there a way to configure a timeout so that pending approval prompts auto-reject if left unanswered, and can that timeout duration be customized? | `sec1024-lexical-heavy` | https://docs.mistral.ai/studio/workflows/interacting-with-workflows/conversational_workflows#timeout | not checked |
| What are the specific numeric rate limits per model included in the custom Priority Tier limits? | `sec1024-lexical-heavy` | https://docs.mistral.ai/inference/priority-tier#quotas-and-limits | not checked |
| What is the maximum number of fine-tuning jobs that can run concurrently per project on the fine-tuning API? | `sec1024-lexical-heavy` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#jobs-management | not checked |
| Is there an air-gapped license validation mode, and how often does an offline installation re-check entitlements before degrading? | `sec1024-lexical-heavy` | https://docs.mistral.ai/studio/search/search-toolkit/ingestion/extractors#pymupdf-extractor | not checked |
| Is there a way to automatically revoke API keys and deactivate active sessions for a member the moment they are removed from the Organization? | `sec1024-lexical-heavy` | https://docs.mistral.ai/admin/identity-access/user-management#remove-members | not checked |
| Is there a limit on the number of characters or options allowed in the instructions or JudgeClassificationOutput options fields? | `sec1024-lexical-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/datasets/records#operation-judge_dataset_record_v1_observability_dataset_records_dataset_record_id_live_judging_post | not checked |
| Is there a limit on the number of users that can auto-join per day through email-domain authentication, or a maximum organization size it enforces? | `sec1024-lexical-heavy` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/email-domain-authentication | not checked |
| What are the valid ranges or allowed values for the learning_rate hyperparameter when creating a classifier fine-tuning job? | `sec1024-lexical-heavy` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#what-is-the-recommended-learning-rate | not checked |
| Is there a documented rate limit or maximum number of page visits MistralAI-User will make per user request in Vibe? | `sec1024-lexical-heavy` | https://docs.mistral.ai/api/endpoint/beta/admin/user-groups#operation-users_api_admin_user_groups_get_user_groups | not checked |
| Is there a documented maximum number of concurrent token-stream tasks a single workflow can run, and what happens if that limit is exceeded? | `sec1024-lexical-heavy` | https://docs.mistral.ai/admin/identity-access/api-key-policy#workspace-limit-above-org-limit | not checked |
| What is the maximum disk size available in the sandbox's default image, and can it be increased? | `sec1024-lexical-heavy` | https://docs.mistral.ai/studio/conversations/vision#how-many-tokens-correspond-to-an-image-andor-what-is-the-maximum-resolution | not checked |
| What is the maximum number of live-judging requests per minute that can be made against a single chat completion event via this endpoint? | `sec1024-lexical-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/chat_completion_events#operation-judge_chat_completion_event_v1_observability_chat_completion_events_event_id_live_judging_post | not checked |
| Is there a limit on how many fine-tuned custom models I can have active at the same time on my Mistral AI account? | `sec1024-lexical-heavy` | https://docs.mistral.ai/studio/observability/evaluations/datasets#how-large-can-my-dataset-be | not checked |
| Does Mistral AI's documentation specify any recommended or maximum token budget for an LLM judge prompt when evaluating large evaluation sets? | `sec1024-lexical-heavy` | https://docs.mistral.ai/studio/observability/evaluations/judges#basic-llm-judge | not checked |
| Is there a way to export or share the todos list from the Work panel once a task is complete? | `sec1024-lexical-heavy` | https://docs.mistral.ai/vibe/work/safety-and-approvals#todos-panel | not checked |
| What is the maximum number of span field definitions that the Get span fields endpoint can return in a single response, and is there pagination support? | `sec1024-lexical-heavy` | https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_fields_v1_observability_spans_fields_get | not checked |
| Is there an API to programmatically list or delete reusable Prompts, and what are the rate limits for Prompt execution? | `sec1024-lexical-heavy` | https://docs.mistral.ai/getting-started/quickstarts/studio/create-reusable-prompt#verify | not checked |
| Does Mistral Document AI on Azure impose a maximum page count per document for processing, and if so, what is the limit? | `sec1024-lexical-heavy` | https://docs.mistral.ai/vibe/work/libraries#limits | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Magistral Small 1.0? | `sec1024-lexical-heavy` | https://docs.mistral.ai/studio/conversations/vision#whats-the-maximum-number-images-per-request | not checked |
| What is the maximum file size allowed for a FileField upload, and is there a limit on the number of files when multiple=True? | `sec1024-lexical-heavy` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#whats-the-size-limit-of-the-training-data | not checked |
| Is there a timeout or expiration period for the open SSO configuration modal after which the setup must be restarted? | `sec1024-heading-path-off` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso#start-in-admin | not checked |
| What is the maximum retention period for a SCIM sync run's result before it is deleted, and can completed runs be purged early via the API? | `sec1024-heading-path-off` | https://docs.mistral.ai/api/endpoint/beta/admin/scim#operation-users_api_admin_scim_sync_get_scim_sync_run | not checked |
| Is there a maximum number of Organizations that can be linked to a single Enterprise Account, and what happens if that limit is exceeded? | `sec1024-heading-path-off` | https://docs.mistral.ai/admin/set-up-organization/enterprise-accounts#organizations | not checked |
| What is the maximum historical retention period for usage data retrievable via the Get Usage endpoint? | `sec1024-heading-path-off` | https://docs.mistral.ai/admin/monitor-comply/zero-data-retention#what-zdr-covers | not checked |
| What is the maximum number of messages allowed in a single chat completion request? | `sec1024-heading-path-off` | https://docs.mistral.ai/studio/conversations/chat-completion#chat-completion | not checked |
| Does the Mistral GCP deployment support server-side prompt caching, and is there a cache hit discount on rawPredict calls? | `sec1024-heading-path-off` | https://docs.mistral.ai/studio/conversations/advanced/prompt-caching | not checked |
| What is the maximum number of web pages MistralAI-User may visit for a single user request in Vibe, and is there a per-minute rate limit? | `sec1024-heading-path-off` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Does `mistral-vespa generate` validate that the output directory is empty before writing, or does it have a flag to force overwriting existing files? | `sec1024-heading-path-off` | https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli#generate | not checked |
| Is there a keyboard shortcut to switch directly to Work mode from Chat or Code without opening the sidebar? | `sec1024-heading-path-off` | https://docs.mistral.ai/getting-started/quickstarts/vibe-work/first-task#step-1 | not checked |
| Is there a maximum number of credentials (API keys or workload identity credentials) that can be attached to a single service account? | `sec1024-heading-path-off` | https://docs.mistral.ai/admin/identity-access/workload-identity#how-setup-works | not checked |
| Is there a limit on the number of handoff targets an agent can have, and what happens if a handoff references a nonexistent agent? | `sec1024-heading-path-off` | https://docs.mistral.ai/studio/agents/handoffs#how-it-works | not checked |
| What is the maximum number of API keys a single Mistral AI account can generate? | `sec1024-heading-path-off` | https://docs.mistral.ai/studio/batch-processing#whats-the-max-number-of-batch-jobs-one-can-create | not checked |
| Is there a recommended maximum length or word limit for the role statement when providing a purpose in a prompt? | `sec1024-heading-path-off` | https://docs.mistral.ai/studio/conversations/chat-completion/prompting#purpose | not checked |
| Is there a limit on how many agents a single account or workspace can create? | `sec1024-heading-path-off` | https://docs.mistral.ai/studio/agents/handoffs#create-an-agentic-workflow | not checked |
| How long does an invitation remain valid before it expires, and can the expiration period be customized? | `sec1024-heading-path-off` | https://docs.mistral.ai/admin/identity-access/api-key-policy#default-state | not checked |
| What is the maximum number of selected event ids returned in a single ListCampaignSelectedEventsResponse, and does the endpoint support pagination? | `sec1024-heading-path-off` | https://docs.mistral.ai/api/endpoint/beta/observability/campaigns#operation-get_campaign_selected_events_v1_observability_campaigns_campaign_id_selected_events_get | not checked |
| What is the minimum GPU VRAM requirement to fine-tune the Ministral 3 14B Instruct weights locally? | `sec1024-heading-path-off` | https://docs.mistral.ai/models/ministral-3-14b-25-12 | not checked |
| Is there a maximum character or token length enforced for system prompts in Mistral models, and what happens if it is exceeded? | `sec1024-heading-path-off` | https://docs.mistral.ai/admin/identity-access/api-key-policy#workspace-limit-above-org-limit | not checked |
| What is the per-token price charged when pay-as-you-go usage kicks in after the included monthly allowance is exhausted? | `sec1024-heading-path-off` | https://docs.mistral.ai/admin/billing-usage/subscriptions#included-monthly-usage | not checked |
| Is there a maximum number of campaigns that can be stored or returned per request, and is there a pagination limit for the campaigns list? | `sec1024-heading-path-off` | https://docs.mistral.ai/studio/batch-processing#whats-the-max-number-of-batch-jobs-one-can-create | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Ministral 3 8B? | `sec1024-heading-path-off` | https://docs.mistral.ai/getting-started/quickstarts/developer/rag-document-search#verify | not checked |
| What is the maximum rate at which MistralAI-User requests can be sent to a single site during user actions in Vibe? | `sec1024-heading-path-off` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Can I apply document_annotation_format when passing an image (ImageURLChunk) instead of a PDF document, and does the annotation then apply per image? | `sec1024-heading-path-off` | https://docs.mistral.ai/studio/document-processing/annotations#usage | not checked |
| Is there a limit on how many hooks can be declared, or a defined execution order when multiple hooks match the same tool call? | `sec1024-heading-path-off` | https://docs.mistral.ai/vibe/code/cli/hooks#file-locations | not checked |
| Does the platform offer a grace period or retry policy for failed invoice payments before account suspension? | `sec1024-heading-path-off` | https://docs.mistral.ai/studio/observability/evaluations/retry-failed-records#fixing-the-task-before-retrying | not checked |
| Is there a rate limit on how many observability datasets can be deleted per minute via the API? | `sec1024-heading-path-off` | https://docs.mistral.ai/studio/observability/evaluations/datasets#how-large-can-my-dataset-be | not checked |
| What is the maximum total byte size allowed for a request body before a 400 error is returned? | `sec1024-heading-path-off` | https://docs.mistral.ai/resources/error-glossary#400-bad-request | not checked |
| Is there a timeout limit for code interpreter executions, and what happens if the executed code exceeds it? | `sec1024-heading-path-off` | https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#explanation-of-the-output | not checked |
| Is there a limit on how many agents can be created per workspace or per API key? | `sec1024-heading-path-off` | https://docs.mistral.ai/vibe/work/switch-organization-workspace#scoped | not checked |
| When deleting a judge that is currently referenced by active evaluations, does the API return a 409 Conflict, or does the deletion succeed and leave the evaluations without a judge? | `sec1024-heading-path-off` | https://docs.mistral.ai/studio/observability/evaluations#how-do-i-use-an-llm-as-a-judge | not checked |
| Is there a way to configure a timeout so that pending approval prompts auto-reject if left unanswered, and can that timeout duration be customized? | `sec1024-heading-path-off` | https://docs.mistral.ai/studio/workflows/interacting-with-workflows/conversational_workflows#timeout | not checked |
| What are the specific numeric rate limits per model included in the custom Priority Tier limits? | `sec1024-heading-path-off` | https://docs.mistral.ai/inference/priority-tier#quotas-and-limits | not checked |
| What is the maximum number of fine-tuning jobs that can run concurrently per project on the fine-tuning API? | `sec1024-heading-path-off` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#jobs-management | not checked |
| Is there an air-gapped license validation mode, and how often does an offline installation re-check entitlements before degrading? | `sec1024-heading-path-off` | https://docs.mistral.ai/studio/search/search-toolkit/ingestion/extractors#pymupdf-extractor | not checked |
| Is there a way to automatically revoke API keys and deactivate active sessions for a member the moment they are removed from the Organization? | `sec1024-heading-path-off` | https://docs.mistral.ai/admin/identity-access/user-management#manage-members | not checked |
| Is there a limit on the number of characters or options allowed in the instructions or JudgeClassificationOutput options fields? | `sec1024-heading-path-off` | https://docs.mistral.ai/api/endpoint/beta/observability/judges#operation-create_judge_v1_observability_judges_post | not checked |
| Is there a limit on the number of users that can auto-join per day through email-domain authentication, or a maximum organization size it enforces? | `sec1024-heading-path-off` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/email-domain-authentication | not checked |
| What are the valid ranges or allowed values for the learning_rate hyperparameter when creating a classifier fine-tuning job? | `sec1024-heading-path-off` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#what-is-the-recommended-learning-rate | not checked |
| Is there a documented rate limit or maximum number of page visits MistralAI-User will make per user request in Vibe? | `sec1024-heading-path-off` | https://docs.mistral.ai/api/endpoint/beta/admin/user-groups#operation-users_api_admin_user_groups_get_user_groups | not checked |
| Is there a documented maximum number of concurrent token-stream tasks a single workflow can run, and what happens if that limit is exceeded? | `sec1024-heading-path-off` | https://docs.mistral.ai/admin/identity-access/api-key-policy#workspace-limit-above-org-limit | not checked |
| What is the maximum disk size available in the sandbox's default image, and can it be increased? | `sec1024-heading-path-off` | https://docs.mistral.ai/studio/conversations/vision#how-many-tokens-correspond-to-an-image-andor-what-is-the-maximum-resolution | not checked |
| What is the maximum number of live-judging requests per minute that can be made against a single chat completion event via this endpoint? | `sec1024-heading-path-off` | https://docs.mistral.ai/api/endpoint/beta/observability/chat_completion_events#operation-judge_chat_completion_event_v1_observability_chat_completion_events_event_id_live_judging_post | not checked |
| Is there a limit on how many fine-tuned custom models I can have active at the same time on my Mistral AI account? | `sec1024-heading-path-off` | https://docs.mistral.ai/vibe/work/libraries#data-privacy | not checked |
| Does Mistral AI's documentation specify any recommended or maximum token budget for an LLM judge prompt when evaluating large evaluation sets? | `sec1024-heading-path-off` | https://docs.mistral.ai/resources/deprecated/customization#step-3-create-your-application-evals | not checked |
| Is there a way to export or share the todos list from the Work panel once a task is complete? | `sec1024-heading-path-off` | https://docs.mistral.ai/vibe/work/safety-and-approvals#todos-panel | not checked |
| What is the maximum number of span field definitions that the Get span fields endpoint can return in a single response, and is there pagination support? | `sec1024-heading-path-off` | https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_fields_v1_observability_spans_fields_get | not checked |
| Is there an API to programmatically list or delete reusable Prompts, and what are the rate limits for Prompt execution? | `sec1024-heading-path-off` | https://docs.mistral.ai/getting-started/quickstarts/studio/create-reusable-prompt#verify | not checked |
| Does Mistral Document AI on Azure impose a maximum page count per document for processing, and if so, what is the limit? | `sec1024-heading-path-off` | https://docs.mistral.ai/vibe/work/libraries#limits | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Magistral Small 1.0? | `sec1024-heading-path-off` | https://docs.mistral.ai/studio/document-processing/document_qna#usage | not checked |
| What is the maximum file size allowed for a FileField upload, and is there a limit on the number of files when multiple=True? | `sec1024-heading-path-off` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#whats-the-size-limit-of-the-training-data | not checked |
| Is there a timeout or expiration period for the open SSO configuration modal after which the setup must be restarted? | `sec1024-shipped+rerank` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso#start-in-admin | not checked |
| What is the maximum retention period for a SCIM sync run's result before it is deleted, and can completed runs be purged early via the API? | `sec1024-shipped+rerank` | https://docs.mistral.ai/api/endpoint/beta/admin/scim#operation-users_api_admin_scim_sync_get_scim_sync_run | not checked |
| Is there a maximum number of Organizations that can be linked to a single Enterprise Account, and what happens if that limit is exceeded? | `sec1024-shipped+rerank` | https://docs.mistral.ai/admin/set-up-organization/enterprise-accounts#admin-hierarchy | not checked |
| What is the maximum historical retention period for usage data retrievable via the Get Usage endpoint? | `sec1024-shipped+rerank` | https://docs.mistral.ai/api/endpoint/beta/admin/billing#operation-users_api_admin_usage_get_usage | not checked |
| What is the maximum number of messages allowed in a single chat completion request? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/conversations/chat-completion#chat-completion | not checked |
| Does the Mistral GCP deployment support server-side prompt caching, and is there a cache hit discount on rawPredict calls? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/conversations/advanced/prompt-caching | not checked |
| What is the maximum number of web pages MistralAI-User may visit for a single user request in Vibe, and is there a per-minute rate limit? | `sec1024-shipped+rerank` | https://docs.mistral.ai/vibe/work/web-search-open-url#limitations | not checked |
| Does `mistral-vespa generate` validate that the output directory is empty before writing, or does it have a flag to force overwriting existing files? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli#generate | not checked |
| Is there a keyboard shortcut to switch directly to Work mode from Chat or Code without opening the sidebar? | `sec1024-shipped+rerank` | https://docs.mistral.ai/getting-started/quickstarts/vibe-work/first-task#step-1 | not checked |
| Is there a maximum number of credentials (API keys or workload identity credentials) that can be attached to a single service account? | `sec1024-shipped+rerank` | https://docs.mistral.ai/admin/identity-access/service-accounts#manage | not checked |
| Is there a limit on the number of handoff targets an agent can have, and what happens if a handoff references a nonexistent agent? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/agents/handoffs#define-handoffs-responsibilities | not checked |
| What is the maximum number of API keys a single Mistral AI account can generate? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/batch-processing#whats-the-max-number-of-batch-jobs-one-can-create | not checked |
| Is there a recommended maximum length or word limit for the role statement when providing a purpose in a prompt? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/conversations/chat-completion/prompting#purpose | not checked |
| Is there a limit on how many agents a single account or workspace can create? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/agents/handoffs#create-an-agentic-workflow | not checked |
| How long does an invitation remain valid before it expires, and can the expiration period be customized? | `sec1024-shipped+rerank` | https://docs.mistral.ai/admin/identity-access/user-management#invite-members | not checked |
| What is the maximum number of selected event ids returned in a single ListCampaignSelectedEventsResponse, and does the endpoint support pagination? | `sec1024-shipped+rerank` | https://docs.mistral.ai/api/endpoint/beta/observability/campaigns#operation-get_campaign_selected_events_v1_observability_campaigns_campaign_id_selected_events_get | not checked |
| What is the minimum GPU VRAM requirement to fine-tune the Ministral 3 14B Instruct weights locally? | `sec1024-shipped+rerank` | https://docs.mistral.ai/vibe/code/cli/offline-models#hardware | not checked |
| Is there a maximum character or token length enforced for system prompts in Mistral models, and what happens if it is exceeded? | `sec1024-shipped+rerank` | https://docs.mistral.ai/inference/prompting#system-prompt | not checked |
| What is the per-token price charged when pay-as-you-go usage kicks in after the included monthly allowance is exhausted? | `sec1024-shipped+rerank` | https://docs.mistral.ai/admin/billing-usage/invoices#payment-schedule | not checked |
| Is there a maximum number of campaigns that can be stored or returned per request, and is there a pagination limit for the campaigns list? | `sec1024-shipped+rerank` | https://docs.mistral.ai/api/endpoint/beta/observability/campaigns#operation-get_campaigns_v1_observability_campaigns_get | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Ministral 3 8B? | `sec1024-shipped+rerank` | https://docs.mistral.ai/models/ministral-3-8b-25-12 | not checked |
| What is the maximum rate at which MistralAI-User requests can be sent to a single site during user actions in Vibe? | `sec1024-shipped+rerank` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Can I apply document_annotation_format when passing an image (ImageURLChunk) instead of a PDF document, and does the annotation then apply per image? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/batch-processing#prepare-batch-file | not checked |
| Is there a limit on how many hooks can be declared, or a defined execution order when multiple hooks match the same tool call? | `sec1024-shipped+rerank` | https://docs.mistral.ai/vibe/code/cli/hooks#declare | not checked |
| Does the platform offer a grace period or retry policy for failed invoice payments before account suspension? | `sec1024-shipped+rerank` | https://docs.mistral.ai/admin/billing-usage/billing#monthly-spending-limit | not checked |
| Is there a rate limit on how many observability datasets can be deleted per minute via the API? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/observability/evaluations/datasets#how-large-can-my-dataset-be | not checked |
| What is the maximum total byte size allowed for a request body before a 400 error is returned? | `sec1024-shipped+rerank` | https://docs.mistral.ai/resources/error-glossary#400-bad-request | not checked |
| Is there a timeout limit for code interpreter executions, and what happens if the executed code exceeds it? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/workflows/building-workflows/activities/basics#timeouts | not checked |
| Is there a limit on how many agents can be created per workspace or per API key? | `sec1024-shipped+rerank` | https://docs.mistral.ai/admin/workspaces/your-first-workspace | not checked |
| When deleting a judge that is currently referenced by active evaluations, does the API return a 409 Conflict, or does the deletion succeed and leave the evaluations without a judge? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/observability/evaluations#how-do-i-use-an-llm-as-a-judge | not checked |
| Is there a way to configure a timeout so that pending approval prompts auto-reject if left unanswered, and can that timeout duration be customized? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/workflows/interacting-with-workflows/conversational_workflows#timeout | not checked |
| What are the specific numeric rate limits per model included in the custom Priority Tier limits? | `sec1024-shipped+rerank` | https://docs.mistral.ai/inference/priority-tier#before-you-start | not checked |
| What is the maximum number of fine-tuning jobs that can run concurrently per project on the fine-tuning API? | `sec1024-shipped+rerank` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#jobs-management | not checked |
| Is there an air-gapped license validation mode, and how often does an offline installation re-check entitlements before degrading? | `sec1024-shipped+rerank` | https://docs.mistral.ai/vibe/code/cli/install-setup#prerequisites | not checked |
| Is there a way to automatically revoke API keys and deactivate active sessions for a member the moment they are removed from the Organization? | `sec1024-shipped+rerank` | https://docs.mistral.ai/admin/identity-access/user-management#api-keys | not checked |
| Is there a limit on the number of characters or options allowed in the instructions or JudgeClassificationOutput options fields? | `sec1024-shipped+rerank` | https://docs.mistral.ai/api/endpoint/beta/observability/judges#operation-create_judge_v1_observability_judges_post | not checked |
| Is there a limit on the number of users that can auto-join per day through email-domain authentication, or a maximum organization size it enforces? | `sec1024-shipped+rerank` | https://docs.mistral.ai/getting-started/quickstarts/admin/configure-sso#step-2 | not checked |
| What are the valid ranges or allowed values for the learning_rate hyperparameter when creating a classifier fine-tuning job? | `sec1024-shipped+rerank` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#what-is-the-recommended-learning-rate | not checked |
| Is there a documented rate limit or maximum number of page visits MistralAI-User will make per user request in Vibe? | `sec1024-shipped+rerank` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Is there a documented maximum number of concurrent token-stream tasks a single workflow can run, and what happens if that limit is exceeded? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/workflows/managing-workflows-in-production/concurrency#configuration-options-offset | not checked |
| What is the maximum disk size available in the sandbox's default image, and can it be increased? | `sec1024-shipped+rerank` | https://docs.mistral.ai/vibe/work/libraries#limits | not checked |
| What is the maximum number of live-judging requests per minute that can be made against a single chat completion event via this endpoint? | `sec1024-shipped+rerank` | https://docs.mistral.ai/api/endpoint/beta/observability/chat_completion_events#operation-judge_chat_completion_event_v1_observability_chat_completion_events_event_id_live_judging_post | not checked |
| Is there a limit on how many fine-tuned custom models I can have active at the same time on my Mistral AI account? | `sec1024-shipped+rerank` | https://docs.mistral.ai/vibe/work/scheduled-tasks#limits | not checked |
| Does Mistral AI's documentation specify any recommended or maximum token budget for an LLM judge prompt when evaluating large evaluation sets? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/observability/evaluations/judges#basic-llm-judge | not checked |
| Is there a way to export or share the todos list from the Work panel once a task is complete? | `sec1024-shipped+rerank` | https://docs.mistral.ai/getting-started/quickstarts/vibe-work/analyze-data#step-3 | not checked |
| What is the maximum number of span field definitions that the Get span fields endpoint can return in a single response, and is there pagination support? | `sec1024-shipped+rerank` | https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_fields_v1_observability_spans_fields_get | not checked |
| Is there an API to programmatically list or delete reusable Prompts, and what are the rate limits for Prompt execution? | `sec1024-shipped+rerank` | https://docs.mistral.ai/getting-started/quickstarts/studio/create-reusable-prompt#verify | not checked |
| Does Mistral Document AI on Azure impose a maximum page count per document for processing, and if so, what is the limit? | `sec1024-shipped+rerank` | https://docs.mistral.ai/vibe/work/libraries#limits | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Magistral Small 1.0? | `sec1024-shipped+rerank` | https://docs.mistral.ai/models | not checked |
| What is the maximum file size allowed for a FileField upload, and is there a limit on the number of files when multiple=True? | `sec1024-shipped+rerank` | https://docs.mistral.ai/api/endpoint/files#operation-files_api_routes_upload_file | not checked |
| Is there a timeout or expiration period for the open SSO configuration modal after which the setup must be restarted? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso#start-in-admin | not checked |
| What is the maximum retention period for a SCIM sync run's result before it is deleted, and can completed runs be purged early via the API? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/admin/monitor-comply/zero-data-retention#what-zdr-does-not-cover | not checked |
| Is there a maximum number of Organizations that can be linked to a single Enterprise Account, and what happens if that limit is exceeded? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/api/endpoint/beta/users#operation-users_api_list_organizations | not checked |
| What is the maximum historical retention period for usage data retrievable via the Get Usage endpoint? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/api/endpoint/beta/admin/billing#operation-users_api_admin_usage_get_usage | not checked |
| What is the maximum number of messages allowed in a single chat completion request? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/api/endpoint/chat#operation-chat_completion_v1_chat_completions_post | not checked |
| Does the Mistral GCP deployment support server-side prompt caching, and is there a cache hit discount on rawPredict calls? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/studio/conversations/advanced/prompt-caching | not checked |
| What is the maximum number of web pages MistralAI-User may visit for a single user request in Vibe, and is there a per-minute rate limit? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Does `mistral-vespa generate` validate that the output directory is empty before writing, or does it have a flag to force overwriting existing files? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli#generate | not checked |
| Is there a keyboard shortcut to switch directly to Work mode from Chat or Code without opening the sidebar? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/getting-started/quickstarts/vibe-work/first-task#step-1 | not checked |
| Is there a maximum number of credentials (API keys or workload identity credentials) that can be attached to a single service account? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/admin/identity-access/service-accounts#manage | not checked |
| Is there a limit on the number of handoff targets an agent can have, and what happens if a handoff references a nonexistent agent? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/studio/agents/handoffs#define-handoffs-responsibilities | not checked |
| What is the maximum number of API keys a single Mistral AI account can generate? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/admin/identity-access/api-key-policy#workspace-limit-above-org-limit | not checked |
| Is there a recommended maximum length or word limit for the role statement when providing a purpose in a prompt? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/inference/prompting#purpose | not checked |
| Is there a limit on how many agents a single account or workspace can create? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/studio/agents/handoffs#create-an-agentic-workflow | not checked |
| How long does an invitation remain valid before it expires, and can the expiration period be customized? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/admin/identity-access/user-management#invite-members | not checked |
| What is the maximum number of selected event ids returned in a single ListCampaignSelectedEventsResponse, and does the endpoint support pagination? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/api/endpoint/beta/observability/campaigns#operation-get_campaign_selected_events_v1_observability_campaigns_campaign_id_selected_events_get | not checked |
| What is the minimum GPU VRAM requirement to fine-tune the Ministral 3 14B Instruct weights locally? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/vibe/code/cli/offline-models#hardware | not checked |
| Is there a maximum character or token length enforced for system prompts in Mistral models, and what happens if it is exceeded? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/api/endpoint/chat#operation-chat_completion_v1_chat_completions_post | not checked |
| What is the per-token price charged when pay-as-you-go usage kicks in after the included monthly allowance is exhausted? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/admin/billing-usage/invoices#payment-schedule | not checked |
| Is there a maximum number of campaigns that can be stored or returned per request, and is there a pagination limit for the campaigns list? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/studio/batch-processing#whats-the-max-number-of-batch-jobs-one-can-create | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Ministral 3 8B? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/models/ministral-3-8b-25-12 | not checked |
| What is the maximum rate at which MistralAI-User requests can be sent to a single site during user actions in Vibe? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Can I apply document_annotation_format when passing an image (ImageURLChunk) instead of a PDF document, and does the annotation then apply per image? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/studio/document-processing/annotations#usage | not checked |
| Is there a limit on how many hooks can be declared, or a defined execution order when multiple hooks match the same tool call? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/vibe/code/cli/hooks#declare | not checked |
| Does the platform offer a grace period or retry policy for failed invoice payments before account suspension? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/admin/billing-usage/usage-limits#organization-spending-limit | not checked |
| Is there a rate limit on how many observability datasets can be deleted per minute via the API? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/api/endpoint/beta/observability/datasets#operation-delete_dataset_v1_observability_datasets_dataset_id_delete | not checked |
| What is the maximum total byte size allowed for a request body before a 400 error is returned? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/resources/error-glossary#400-bad-request | not checked |
| Is there a timeout limit for code interpreter executions, and what happens if the executed code exceeds it? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#explanation-of-the-output | not checked |
| Is there a limit on how many agents can be created per workspace or per API key? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/admin/workspaces/your-first-workspace | not checked |
| When deleting a judge that is currently referenced by active evaluations, does the API return a 409 Conflict, or does the deletion succeed and leave the evaluations without a judge? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/studio/observability/evaluations#how-do-i-use-an-llm-as-a-judge | not checked |
| Is there a way to configure a timeout so that pending approval prompts auto-reject if left unanswered, and can that timeout duration be customized? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/vibe/work/safety-and-approvals#approvals | not checked |
| What are the specific numeric rate limits per model included in the custom Priority Tier limits? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/inference/priority-tier#quotas-and-limits | not checked |
| What is the maximum number of fine-tuning jobs that can run concurrently per project on the fine-tuning API? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#jobs-management | not checked |
| Is there an air-gapped license validation mode, and how often does an offline installation re-check entitlements before degrading? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/inference/deployment/local-deployment/vllm#offline-mode-inference | not checked |
| Is there a way to automatically revoke API keys and deactivate active sessions for a member the moment they are removed from the Organization? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/admin/identity-access/user-management#remove-members | not checked |
| Is there a limit on the number of characters or options allowed in the instructions or JudgeClassificationOutput options fields? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/api/endpoint/beta/observability/judges#operation-create_judge_v1_observability_judges_post | not checked |
| Is there a limit on the number of users that can auto-join per day through email-domain authentication, or a maximum organization size it enforces? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/email-domain-authentication | not checked |
| What are the valid ranges or allowed values for the learning_rate hyperparameter when creating a classifier fine-tuning job? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#what-is-the-recommended-learning-rate | not checked |
| Is there a documented rate limit or maximum number of page visits MistralAI-User will make per user request in Vibe? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/studio/conversations/vision#whats-the-maximum-number-images-per-request | not checked |
| Is there a documented maximum number of concurrent token-stream tasks a single workflow can run, and what happens if that limit is exceeded? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/studio/workflows/managing-workflows-in-production/concurrency#configuration-options-offset | not checked |
| What is the maximum disk size available in the sandbox's default image, and can it be increased? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/vibe/work/libraries#limits | not checked |
| What is the maximum number of live-judging requests per minute that can be made against a single chat completion event via this endpoint? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/api/endpoint/beta/observability/chat_completion_events#operation-judge_chat_completion_event_v1_observability_chat_completion_events_event_id_live_judging_post | not checked |
| Is there a limit on how many fine-tuned custom models I can have active at the same time on my Mistral AI account? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/vibe/work/scheduled-tasks#limits | not checked |
| Does Mistral AI's documentation specify any recommended or maximum token budget for an LLM judge prompt when evaluating large evaluation sets? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/studio/observability/evaluations/judges#basic-llm-judge | not checked |
| Is there a way to export or share the todos list from the Work panel once a task is complete? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/vibe/work/safety-and-approvals#todos-panel | not checked |
| What is the maximum number of span field definitions that the Get span fields endpoint can return in a single response, and is there pagination support? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_fields_v1_observability_spans_fields_get | not checked |
| Is there an API to programmatically list or delete reusable Prompts, and what are the rate limits for Prompt execution? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/api/endpoint/beta/prompts#operation-prompts_delete | not checked |
| Does Mistral Document AI on Azure impose a maximum page count per document for processing, and if so, what is the limit? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/vibe/work/libraries#limits | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Magistral Small 1.0? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/models | not checked |
| What is the maximum file size allowed for a FileField upload, and is there a limit on the number of files when multiple=True? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/api/endpoint/files#operation-files_api_routes_upload_file | not checked |

## Figures

Regenerated from `metrics.json` by `make eval-report run=<dir>`.

- `figures/recall-at-k-page.svg`, `figures/recall-at-k-section.svg`: recall against k, one line per configuration
- `figures/best-two-by-type-page.svg`, `figures/best-two-by-type-section.svg`: recall@5 per question type, for the two leading configurations

## Conclusion

At the page level, over the 244 questions that matching can score, `sec1024-vector-heavy+rerank` leads on recall@5 with 0.920, +0.012 over `page128-vector-heavy` (0.908).

At the section level, over the 142 questions that matching can score, `sec1024-vector-heavy+rerank` leads on recall@5 with 0.979, +0.021 over `sec128-vector-heavy` (0.958).

The reranker made 588 calls for $0.4101, about $0.000697 a call, and its ranking was applied 505 of those times; the other 83 returned a ranking the reordering could not use and fell back to retrieval order, which the per-question records name.

This feeds D-012a: the shipped ranking weights are a starting point and the winning row above is what replaces them, and D-015: whether one listwise call buys enough ordering to be worth its latency in the serving path.
