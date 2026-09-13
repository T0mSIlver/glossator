# What goes upstream

Sixteen reproducible defects affect Mistral's packages, starter template or
documentation. `search-toolkit.md`, `mistral-stack.md` and `DECISIONS.md` contain
the evidence. The list is ordered by expected impact (D-018a).

`mistralai/search-starter-app` accepts pull requests.
`mistralai-search-toolkit` and its Vespa plugin have no public source repository.
Those fixes need reports with attached patches through Mistral support.
Documentation fixes belong in `mistralai/platform-docs-public`.

| # | Where | What | Evidence | Fix |
|---|---|---|---|---|
| 1 | starter app | Ships a ranking profile with the phase-one vector weight at 0; the toolkit's build check names the unset weight but only logs it. Candidate selection therefore uses only keyword search (BM25). Queries without shared words may never reach the second phase. | `plugins/vespa/app/schemas/base.py`, `_generate_closeness_function`; D-012 | Ship a non-zero vector weight, or fail the build instead of logging. |
| 2 | toolkit plugin | `ranking_weights` keys require a `_weight` suffix, but invalid keys are accepted and ignored. Four configurations then produced identical scores. | `search/bodies.py:33-34`; D-025 | Validate keys against the ranking profile inputs. |
| 3 | toolkit plugin | Named query profiles reject `exclude_ids` and `extra_yql_filter`. The starter always sets a profile, so exclusion fails. | `search/query_builder.py:128-135`; D-014 | Allow profiles on the query-builder path, or omit the starter's profile. |
| 4 | toolkit | Normalised discounted cumulative gain (nDCG) assumes each relevant ID appears once. URL-based scoring produced an impossible value of 1.220. | `evals/metrics.py:186`; D-016a | Remove duplicate URLs from the ranked list before scoring. |
| 5 | toolkit | `RetrieverEvaluator` stops at the first failed query and loses the rest of the batch. | `evals/evaluator.py:127-128`; D-025a | Record each failed query as an error row. |
| 6 | toolkit plugin | Generated `services.xml` cannot set `<resource-limits>`. Vespa blocks writes above 80% disk, and re-indexing deletes existing data before writing replacements. | `deploy/templates/services.xml.j2`, `deploy/xml.py:37-51`; D-025b | Add a `resource_limits` parameter and document the deletion risk. |
| 7 | toolkit | `MistralEmbedder` retries three times. Free-tier per-minute limits can exhaust all retries in one batch. | `embedding/mistral_embedder.py:277`; D-011a | Make retry count and delay configurable. |
| 8 | toolkit | `LLMReRanker` makes one sequential model call per result and then discards its score. | `retrieval/rerankers/llm.py:68-76`; D-015, D-034 | Add a listwise implementation that records `rerank_score`. |
| 9 | toolkit | `QueryEngine` calls query extension but retrieves with only the original query. | `retrieval/query_engine.py:114-129` | Retrieve with the extensions, or remove the option. |
| 10 | toolkit plugin | The approximate-neighbour index (HNSW) always uses Euclidean distance. The hit parser also drops ranking `matchfeatures`. | `app/schemas/field.py:29`, `search/document_per_chunk_index.py:490`; D-025, D-025a | Expose the distance metric and retain `matchfeatures`. |
| 11 | starter app | The template accepts an underscore in the app name, which the plugin rejects. Collection defaults also differ between migration and entry points. | D-022, D-022a | Validate the app name and define one collection default. |
| 12 | starter app | Quickstarts omit the required `extractor`. The `read()` offset documentation is wrong. The Vespa Skill recommends an unsupported keyword-plus-RRF configuration. | D-013, D-018 | Correct all three instructions. |
| 13 | toolkit | `__version__` says 0.1.0 while the distribution is 0.0.13 | `__init__.py:34` | read the version from package metadata |
| 14 | docs repo | `llms.txt` lists 75 links that all return 404 and `llms-full.txt` predates Vibe, the Search Toolkit and Medium 3.5, because the generator reads a directory that no longer exists | `llms_txt/generate_llms_txt.py`; D-001 | point the generator at the current content tree |
| 15 | docs repo | The Work Connectors page does not mention the `_confirmationReason` argument Work adds to a call that asks for approval; a server with a strict schema rejects it | D-037b | one paragraph on the Connectors page |
| 16 | docs repo | The Search Toolkit landing page names evaluation as one of its three components, and no page documents it; the package ships `mistralai.search.toolkit.evals` (`RetrieverEvaluator`, `MetricsCalculator`, `EvaluationDataset`, `RetrievalMetrics`). A Work session searched thirteen times for the page, then invented an evaluation section from the semantic cache's counters | `evals/`; `eval/runs/2026-09-11-1410-work-session-search-toolkit/`; D-044a | an evaluation page under `search-toolkit`, or drop the word from the landing page |

Rows 1 to 3 have the highest impact. Each produced plausible but wrong rankings
instead of an error. Rows 11 to 16 need only small template or documentation
changes.
