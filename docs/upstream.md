# What goes upstream

Every defect this project hit in Mistral's packages and documentation is
recorded with a reproduction (`docs/search-toolkit.md`, `docs/mistral-stack.md`,
`DECISIONS.md`). None has been reported yet: the review is on the work, not on
public noise, so issues and pull requests wait until after it (D-018). This is
the list, ranked by what a fix saves the next person, with where each one goes.

Targets. `mistralai/search-starter-app` is public and accepts pull requests.
`mistralai-search-toolkit` and its Vespa plugin ship as an installed package
with no public repository, so those fixes go as reports with a patch attached
through Mistral's support channel until a repository exists.
`mistralai/platform-docs-public` is the documentation source.

| # | Where | What | Evidence | Fix |
|---|---|---|---|---|
| 1 | toolkit plugin | Phase-1 vector weight defaults to 0, so the candidate phase is BM25-only and purely semantic matches never reach the reranking phase | `plugins/vespa/app/schemas/base.py`, `_generate_closeness_function` docstring warns about it; D-012 | non-zero default, or a build-time error instead of a log line |
| 2 | toolkit plugin | `ranking_weights` keys need a `_weight` suffix that nothing validates; a bare feature name is accepted and ignored, four configurations scored byte-identical | `search/bodies.py:33-34`; D-025 | validate keys against the profile's inputs, as `set_default_ranking_weights` already does |
| 3 | toolkit plugin | A named query profile raises on `exclude_ids` and `extra_yql_filter`, and the starter's `get_index()` always sets one, so the starter's own `search` tool fails on a non-empty `exclude_ids` | `search/query_builder.py:128-135`; D-014 | let the builder path carry a profile, or drop the profile from `get_index()` |
| 4 | toolkit | nDCG's ideal DCG assumes each relevant id appears once; under URL proxies it exceeds 1 (1.220 measured) | `evals/metrics.py:186`; D-016a | collapse the ranked list to distinct proxies before scoring |
| 5 | toolkit | `RetrieverEvaluator` raises on the first failing query and loses the batch | `evals/evaluator.py:127-128`; D-025a | isolate each row, report errors as rows |
| 6 | toolkit plugin | Generated `services.xml` has no seam for `<resource-limits>`; Vespa blocks feeds above 80% disk and re-indexing deletes before it writes, so a redeploy on a full disk emptied a schema | `deploy/templates/services.xml.j2`, `deploy/xml.py:37-51`; D-025b | a `resource_limits` parameter on `write_services_xml`, and a documented warning |
| 7 | toolkit | `MistralEmbedder` retries three times; the free tier's per-minute limits exhaust that on every batch | `embedding/mistral_embedder.py:277`; D-011a | make `max_retry` and the backoff configurable from the preset |
| 8 | toolkit | `LLMReRanker` issues one sequential call per candidate and discards its own score | `retrieval/rerankers/llm.py:68-76`; D-015 | a listwise variant that writes `rerank_score`; it was this project's largest retrieval gain |
| 9 | toolkit | `QueryEngine` pays for query extension and retrieves with the original query only | `retrieval/query_engine.py:114-129` | either use the extensions or remove the option |
| 10 | toolkit plugin | HNSW distance is hard-coded euclidean whatever the embedding model declares; `matchfeatures` are emitted by the profile and dropped by the hit parser | `app/schemas/field.py:29`, `search/document_per_chunk_index.py:490`; D-025, D-025a | expose the metric; surface `matchfeatures` on the hit |
| 11 | starter app | The copier template accepts an app name with an underscore that the plugin rejects, so a fresh starter cannot run its first migration; `COLLECTION_NAME` defaults differ between the entry points and the migration | D-022, D-022a | validate the answer in the template; one default in one place |
| 12 | starter app | The README quickstarts omit the required `extractor` argument; the `read()` docstring says inclusive end offset, the implementation is exclusive; the skill advises `KeywordRetriever` plus `RRFRanker` on Vespa, where the plugin implements only the vector index | D-013, D-018 | documentation fixes |
| 13 | toolkit | `__version__` says 0.1.0 while the distribution is 0.0.13 | `__init__.py:34` | read the version from package metadata |
| 14 | docs repo | `llms.txt` lists 75 links that all return 404 and `llms-full.txt` predates Vibe, the Search Toolkit and Medium 3.5, because the generator reads a directory that no longer exists | `llms_txt/generate_llms_txt.py`; D-001 | point the generator at the current content tree |
| 15 | docs repo | The Work Connectors page does not mention the `_confirmationReason` argument Work adds to a call that asks for approval; a server with a strict schema rejects it | D-037b | one paragraph on the Connectors page |

Rows 1 to 3 are the ones that cost the most time here and are invisible until
measured: each produced a plausible but wrong ranking rather than an error.
Rows 11 to 15 are small and safe to send first.
