# Decisions

Every choice in this repository, with the facts that drove it. Facts are dated and sourced so each decision can be re-checked when the facts move. Entries are appended, never rewritten; a reversed decision gets a new entry that links back.

Status values: **decided** (settled), **default** (inherited from the starter template or a tool, kept until it bites), **open** (to be settled by measurement), **deferred** (out of v1 scope, revisit criterion stated).

---

## D-001 · Corpus source: docs repo MDX, not llms.txt, not rendered HTML

**Status:** decided · 2026-09-08

**Decision.** Ingest Mistral's documentation from the public source repository `mistralai/platform-docs-public` (`src/content/en/docs/**/page.mdx`), pinned to a commit. Do not ingest `llms.txt`, `llms-full.txt`, or the rendered HTML.

**Facts.**
- `https://docs.mistral.ai/llms.txt` lists 75 links; all 75 return HTTP 404 (HEAD-checked 2026-09-08). They point at a `/docs/` prefix that no longer exists on the site. `llms-full.txt` (992 KB) contains zero occurrences of "Search Toolkit", "Vibe", or "Medium 3.5"; the live site has 54 Search Toolkit pages, 54 Vibe pages, and Medium 3.5 released 2026-04-28. Cause: `llms_txt/generate_llms_txt.py` in the docs repo reads `static/docs`, a directory that no longer exists, so the daily workflow regenerates the same obsolete file.
- Rendered HTML pages are ~1.5 MB each with a 1.7% text-to-markup ratio. Server-rendered tab panels other than the default are empty: on `/studio/conversations/function-calling`, 12 of 12 TypeScript code panels contain only closing tags while the MDX has 32 fenced code blocks. Code blocks carry no language class. Markdown headings have no `id` attribute; only `<SectionTab sectionId>` headings do.
- The repo at HEAD `2e094f7` (2026-09-07) matches the live site: 296 of 300 English docs routes resolve 200 directly and 4 via 308 redirects, 0 dead; sampled page prose is found verbatim in the live HTML; the live `openapi.yaml` is md5-identical to the repo's `openapi-public-doc.yaml`.
- Docs repo license: Apache-2.0.

**Consequence.** A corpus adapter converts MDX to normalized markdown. Its work is corpus-specific and lives in its own package; the rest of the engine sees markdown pages with URLs.

---

## D-002 · URL mapping: routing rule from the repo, sitemap as a cross-check only

**Status:** decided · 2026-09-08

**Decision.** Canonical URL = `https://docs.mistral.ai/` + MDX path with the leading `docs/` segment removed, normalized through the redirect table in the docs repo's `redirect.ts` (321 rules). The sitemap is used to cross-check, never to enumerate.

**Facts.**
- Rule verified on all 300 English docs routes: 296 × 200, 4 × 308 (legacy paths covered by `redirect.ts`), 0 × 4xx.
- `sitemap.xml` (888 URLs, 444 English) omits 41 live pages marked `hidden: true` in `_category_.json` (observability, deployment, model-selection guide, hidden collections) and every `/models/*` model-card page. It carries no `lastmod`.
- `/robots.txt` returns 404; `/robots` in the sitemap is a documentation page about robots.txt.

---

## D-003 · Anchors: `SectionTab` ids first, slugified markdown headings second

**Status:** decided · 2026-09-08

**Decision.** A citation carries URL plus anchor. Anchor = the `sectionId` prop of the enclosing `<SectionTab>` when present; otherwise the slug of the nearest markdown heading computed with the site's own `slugify` (lowercase, strip non-word chars, spaces to hyphens, dedupe with `-1`, `-2`), with a CI check that each emitted anchor exists on the target page.

**Facts.**
- 1,910 `<SectionTab as="h1|h2" sectionId="…">` uses across the English docs carry the heading text as a child and the anchor as a prop; these are the only headings that render an `id` attribute.
- Markdown heading ids are produced by `remark-heading-id` (`src/lib/frontmatter/headings.ts`) and appear only in the RSC TOC payload, not as HTML ids.
- Zero headings use explicit `{#id}` syntax.

---

## D-004 · Include hidden-but-live pages

**Status:** decided by Tom · 2026-09-08

**Decision.** The 41 pages excluded from the sitemap by `hidden: true` are ingested.

**Facts.** They return 200 and hold real content (16 observability pages, 13 deployment pages, the model selection guide). A user can land on them from search engines or links, and questions about deployment are plausible client questions.

---

## D-005 · API reference from `openapi.yaml`, not the generated MDX

**Status:** decided · 2026-09-08

**Decision.** The 49 `/api/endpoint/*` pages are derived from `https://docs.mistral.ai/openapi.yaml` (OpenAPI 3.1, 209 paths), one document per endpoint, mapped to its URL through `src/content/en/api/sidebar-metadata.json`.

**Facts.** `src/content/en/api` is 15 MB of Speakeasy-generated MDX containing 11,210 `<ExpandableProperty>` nodes; the hand-written docs are 4.3 MB. The live spec is md5-identical to the repo's `openapi-public-doc.yaml` (`316010c8…`). `openapi.json` variants at docs and api hosts return 404.

---

## D-006 · Derive a model capability matrix

**Status:** decided · 2026-09-08

**Decision.** Generate a synthetic document (and per-model cards) from `src/schema/models/models/*.ts` and `AVAILABLE_FEATURES` in `src/schema/models/schema.ts`, so questions of the form "which models support function calling" are answerable from one chunk and cite `/models/<slug>`.

**Facts.** Capabilities live only in 66 TypeScript files (`capabilities.features`: `function-calling` on 36 models, `structured-outputs` on 31, `document-qna` on 34, …) rendered by React on `/models`. No MDX table or JSON export exists. The hand-written table on `/studio/conversations/function-calling` is labelled non-exhaustive. The example question in the assignment brief ("What models support function calling?") targets exactly this data.

---

## D-007 · Cookbooks deferred from v1

**Status:** deferred · 2026-09-08 · revisit criterion: any held-out or dev-set question whose gold answer is only in a cookbook

**Facts.**
- 135 cookbook pages (`/resources/cookbooks/*`, 30% of sitemap URLs) come from the separate `mistralai/cookbook` repository (git submodule, not in the docs tree): 95 notebooks, 40 markdown files, ~113k words.
- Dates: 87 from 2024, 32 from 2025, 16 from 2026. Most predate the current SDK (`mistralai` 2.x), the Agents/Conversations API, and the Search Toolkit.
- Rendering requires notebook-to-markdown conversion including outputs.

**Reasoning.** The brief weighs answer quality over breadth. Old notebooks describe superseded APIs and would compete with current reference pages for the same query, which is the failure mode the eval must catch, not introduce. Include later only with a `source_type` field so they can be down-weighted, and only if real questions need them.

---

## D-008 · French pages: open, to be measured

**Status:** open · 2026-09-08

**Facts.** French is a full mirror: 444 sitemap URLs, 396 `page.mdx` (more than English, 362). `mistral-embed` is multilingual. Ingesting French doubles the index and creates near-duplicate chunks that split ranking mass between languages.

**Options to measure on French questions in the dev set:** (a) English index only, the model answers in the question's language; (b) both locales indexed with a `locale` field, retrieval filtered by detected query language; (c) both indexed, no filter. Measured by retrieval recall and answer groundedness on French questions.

---

## D-009 · Vendor the normalized corpus in the repo, with refresh built in

**Status:** decided by Tom · 2026-09-08

**Decision.** The normalized markdown corpus and its manifest (source commit, per-page URL, content hash) are committed. A `make corpus-refresh` target clones the docs repo at a chosen ref and regenerates it. Apache-2.0 license and attribution for the docs are kept alongside.

**Facts.** Reviewers must run the project from the README in minutes; cloning and parsing the docs repo at first run adds a network dependency and a failure surface. The docs repo is Apache-2.0, which permits redistribution with notice.

---

## D-010 · Chunking: section-aware, heading path prefixed, metadata on every chunk

**Status:** open until measured · 2026-09-08

**Facts.**
- Starter default: `MarkdownTextSplitter(chunk_size=4096, chunk_overlap=50)`, character-based, so most pages become one chunk and citations can only land on pages.
- None of the toolkit's six splitters records heading metadata; `markdown.py` computes the langchain header hierarchy and discards it. `MarkdownTokenTextSplitter` is token-budgeted (fits the embedder's 8192-token limit) and header-aligned.
- Chunk metadata is a frozen `extra="allow"` model; any key round-trips through Vespa and comes back on search results. Declaring a same-named root field in the migration makes it indexed and filterable.

**Plan.** Eval columns: R0 starter default vs R2 section chunks (~600-token target, 1024 max, never crossing a heading unless oversized) with `heading_path`, `url`, `anchor`, `page_title` in metadata and as schema fields.

---

## D-011 · Embedding dimensions: 128 (starter) vs 1024, one eval column

**Status:** open until measured · 2026-09-08

**Facts.** `MistralEmbedder` defaults to `mistral-embed-dim128-2510`; the starter migration uses the deprecated `embedding_dimensions=128` form. The 128 and 256 variants have no public model card or price entry (verified 2026-09-08), while `mistral-embed` (1024) is priced at 0.10 USD per M tokens. Embedding the corpus (~1.2M tokens) costs cents either way. Changing dimensions after freeze requires a migration plus a full re-index.

---

## D-012 · Fix phase-1 ranking: vector closeness weight must be non-zero

**Status:** decided · 2026-09-08

**Facts.** The starter's `hybrid-search` query profile sets `bm25_content_weight=0.5` (first phase), `match_content_weight=0.5` and `content_embedding_cosine_similarity_score_weight=5.0` (second phase), and leaves `content_embedding_closeness_weight` at 0. In the toolkit's generated `weighted-rank2` profile, first phase selects candidates and second phase reranks the top 100 per node; with closeness at 0, first phase is BM25-only and purely semantic matches score 0 before reranking. The toolkit's own `_generate_closeness_function` docstring warns about this configuration.

**Decision.** Set a non-zero closeness weight; keep R0 (starter config) as a baseline row.

---

## D-013 · Hybrid search happens inside Vespa; the toolkit's RRF path is unusable here

**Status:** decided · 2026-09-08

**Facts.** `VespaSearchIndex` implements `VectorStoreIndex` only. `KeywordRetriever` requires a `KeywordStoreIndex`; passing a keyword query to the Vespa index raises a pydantic `ValidationError`. Therefore `RRFRanker` has nothing to fuse on this backend. The toolkit skill's advice to "add KeywordRetriever alongside VectorRetriever; fuse with RRFRanker" does not apply to Vespa. Hybrid = YQL `userInput OR nearestNeighbor` plus the weighted rank profile.

---

## D-014 · Named query profile and `exclude_ids` are mutually exclusive in the toolkit

**Status:** decided · 2026-09-08

**Facts.** `exclude_ids` and `extra_yql_filter` raise `SearchError` when a `query_profile` is set. The starter's `get_index()` always sets `hybrid-search`, yet its MCP `search` tool exposes `exclude_ids`; any non-empty value errors. Per-query filters are also unreachable through `QueryEngine`/`VectorRetriever`, which build a plain `VectorSearchQuery`.

**Decision.** Use the query-builder path (`query_profile=None`) with ranking weights passed on `VespaSearchQuery.ranking_weights`, through a retriever of our own, so exclusion and filters work.

---

## D-015 · Reranking: write a listwise reranker; do not use the toolkit's

**Status:** decided · 2026-09-08

**Facts.** `LLMReRanker` issues one sequential LLM call per candidate (no concurrency) and does not write its score onto results. `CrossEncoderReRanker` needs a self-hosted scoring service; Mistral exposes no reranker model or endpoint (verified 2026-09-08). A single listwise call scoring 20 truncated candidates costs one round-trip.

---

## D-016 · Answer layer, citations, and answer evals are written here

**Status:** decided · 2026-09-08

**Facts.** The toolkit's `llm` package holds a chat client and four prompts (OCR, query rewrite, query extension, reranker). There is no answer generation, citation type, groundedness control, streaming, or answer-quality metric. The `evals` package covers retrieval only (recall, precision, F1, MRR, MAP, nDCG at k, plus a Vespa match-phase evaluator) and aborts on the first failing query.

**Decision.** Citations are `url + anchor + chunk id + quoted span`; a verifier rejects citations whose span is not in the cited chunk. Answer evals combine deterministic checks (cited URL vs gold, span verification rate, refusal on unanswerable) with an LLM judge for groundedness and correctness.

---

## D-017 · All models in the shipped path are Mistral's

**Status:** decided by Tom · 2026-09-08

**Facts.** Prices (USD per M tokens, input/output, pricing page 2026-09-08): Mistral Medium 3.5 1.50/7.50; Mistral Large 3 0.50/1.50; Mistral Small 4 0.15/0.60; Ministral 3 8B 0.15/0.15; `mistral-embed` 0.10 input. Budget: 20 USD.

**Decision.** Generation on Mistral Medium 3.5. Cheaper Mistral models may serve reranking, dataset generation, and judging; each such use is recorded with its cost.

---

## D-018 · Upstream: no issues or PRs on Mistral repositories

**Status:** decided by Tom · 2026-09-08

**Facts.** The toolkit has no public source repository or issue tracker (PyPI sdist only, Apache-2.0). The starter app is public (MIT) and accepts pull requests. Findings worth reporting so far: phase-1 closeness weight at zero (D-012); `exclude_ids` broken under a named profile (D-014); deprecated `embedding_dimensions` in the migration; the skill's incorrect RRF advice for Vespa; README quickstarts that omit the required `extractor` argument; `read()` docstring saying inclusive end offset while the implementation is exclusive.

**Decision.** Drafts go to Tom's fork of the starter app only, as low priority, held to the fork's public quality bar.

---

## D-019 · Deliverable: FastAPI service plus MCP server over one engine

**Status:** decided by Tom · 2026-09-08

**Decision.** No UI in v1. One engine package; `entrypoints/api.py` (FastAPI) and `entrypoints/mcp_server.py` both call it. The MCP surface keeps the starter's search and navigation tools for agent clients and adds an `ask` tool returning answer plus verified citations.

---

## D-007a · Cookbooks: confirmed out of v1

**Status:** decided by Tom · 2026-09-08 · supersedes the revisit criterion in D-007

**Decision.** Cookbooks stay out. The 16 entries dated 2026 may be considered later; the 2024 and 2025 ones are not candidates.

---

## D-020 · Dev-set generation on GLM 5.3 through the z.ai API, swappable

**Status:** decided by Tom · 2026-09-08

**Decision.** Generated questions (single-section, cross-page, unanswerable, post-cutoff) are produced by `glm-5.3-flash`, escalating to `glm-5.3` when a generator needs more capability, called directly through the z.ai coding-plan OpenAI-compatible endpoint. The generator is a swappable provider so the same prompts can later run on a Mistral model as an eval of its own. That comparison is deferred until the data point is needed.

**Facts.**
- The value of the dev set is in tricky and cross-page questions. A small model is unlikely to write those reliably; even GLM will need care.
- Endpoint `https://api.z.ai/api/coding/paas/v4/chat/completions` accepts `glm-5.3-flash` and `glm-5.3`; `glm-5.3-air` is unknown there (probe 2026-09-08). `glm-5.3` honours `thinking: {"type": "disabled"}`; `glm-5.3-flash` ignored it and spent 122 reasoning tokens on a one-word reply. Reasoning level must be set and checked per call, and usage recorded.
- Cost to the Mistral budget: zero. The README discloses that dataset generation and judging used a non-Mistral model; every model in the serving path stays Mistral (D-017).

---

## D-021 · Judge on GLM through the z.ai API, swappable; reranker in the serving path stays Mistral

**Status:** decided by Tom · 2026-09-08

**Decision.** The answer judge (correctness against the reference answer, groundedness of claims in cited chunks, citation relevance) runs on GLM via the same provider abstraction as D-020, so a Mistral judge can be swapped in later as a check on judge agreement. Deterministic checks (cited URL vs gold, quoted-span verification, refusal on unanswerable) carry no model dependency and are the primary reported numbers.

The listwise reranker (D-015) is part of the serving path, so its shipped configuration and reported numbers use a Mistral model; GLM may be used only while iterating on the reranker prompt.

**Facts.** Judge cost on Mistral Medium 3.5 would be about 3.60 USD for 600 judgements (D-017 prices), a fifth of the budget, for a component that never ships.

---

## D-022 · Starter defaults the collection name inconsistently

**Status:** default, flagged · 2026-09-08

**Facts.** The generated `.env` sets only `MISTRAL_API_KEY`. `src/entrypoints/*.py` default `COLLECTION_NAME` to `exampledocs`; `src/search_app/migrations/001_*.py` defaults it to `mistral_docs` (the copier answer). Without `COLLECTION_NAME` in `.env`, the starter as generated indexes and searches a schema that the migration never created.

**Decision.** Schema names are owned by the index package (D-010, S3), not by an environment variable; `.env` carries only secrets and ports. Candidate for the fork notes (D-018).

---

## D-023 · Evaluation records: nothing is discarded, every run is self-describing

**Status:** decided by Tom · 2026-09-08

**Decision.** Every evaluation or dataset-generation run writes a directory `eval/runs/<date>-<name>/` that is committed:
- `README.md`: what is being measured, in plain words; the question it answers; the configurations compared; the datasets used (with their commit hash); the result tables; charts under `figures/`; the conclusion and the decision it feeds (linked D-number).
- `config.json`: every parameter (models, prompts by hash, weights, chunking, top-k, seeds).
- `records.jsonl`: one line per question with the retrieval hits (ids, scores, url, anchor), the assembled context, every prompt and raw model response (generation, rerank, judge), verified citations, token usage, latency, and errors.
- `calls.jsonl`: every LLM request and response in the run, verbatim, with provider, model, thinking setting, and usage. The disk cache under `.cache/` is for deduplication only and is not the durable record.
- `metrics.json`: aggregate numbers used in the tables.

Datasets in `eval/` carry the generator run that produced them. Charts are rendered from `metrics.json` by a script so they can be regenerated.

**Facts.** The numbers are the argument in the review and the talk; a number that cannot be traced back to raw model output cannot be defended. Runs cost real credits and GLM calls, and re-running to recover lost detail wastes both. Estimated size: a 600-judgement run is a few MB, acceptable in git.

---

## D-003a · Anchors: markdown headings have none; only SectionTab, FAQ, and API operations deep-link

**Status:** decided · 2026-09-08 · corrects D-003

**Facts** (from building and live-checking the corpus, 411 pages, 2,199 anchors, 0 failures):
- Markdown headings on docs.mistral.ai carry no `id`, in the HTML or in the table-of-contents payload. The site's heading plugin honours only explicit `{#id}` syntax, which no heading uses, and its TOC builder reads `SectionTab` components only. The slugify port planned in D-003 has no target.
- Deep-linkable anchors come from three sources: `<SectionTab sectionId>` (1,799 emitted), `<FaqItem>` through the FAQ component's own slugify (110), and the `elementId` values in the API sidebar metadata (290).
- The site has two slugify implementations: the heading one keeps underscores and collapses hyphens; the FAQ one drops underscores and does not collapse. FAQ anchors must use the second.
- A `SectionTab` nested inside other JSX, inside a non-active tab panel, or reached through an inlined partial is not rendered with an id and is not in the TOC: 99 such headings keep their text and level but get no anchor.
- A `SectionTab`'s rendered heading level is not its `as` prop: `variant="secondary"` demotes h1/h2 to h3, and a plain h1 renders as h2.

**Consequence.** Many sections have no anchor. Chunk metadata carries `anchor: None` for them and the citation degrades to the page URL, with `heading_path` still identifying the section in the answer. 83 pages carry no anchor at all (66 model pages, 17 docs pages).

---

## D-002a · Redirects and unreachable routes

**Status:** decided · 2026-09-08 · refines D-002

**Facts.** `redirect.ts` yields 320 parseable rules. A `:path*` wildcard whose destination has no `:path*` is a fixed target (Next.js drops the captured tail). Applying the table collapses 3 legacy routes onto pages already in the set, leaving 296 docs pages. One route (`studio-api/workflows/building-workflows/workflow_tags`) redirects to a page that does not exist on the live site (404); it is excluded from the corpus and reported by the build.

Breadcrumbs reproduce the site's own search index exactly (0 mismatches on the 257 routes it lists) by porting its title precedence: page title, then category label, then title-cased directory name.

---

## D-024 · Seven data-driven pages are near-empty after conversion

**Status:** open · 2026-09-08

**Facts.** `/resources/release-notes`, `/resources/glossary`, `/inference/model-selection-guide`, `/admin`, `/inference`, `/resources`, `/community` render React widgets from data files with no MDX children; after conversion their bodies are 17 to 344 bytes. Release notes come from `src/data/releases/en/*.json` and the glossary from a term list. The model catalog pages are already covered by the 66 generated model pages.

**Revisit criterion.** A dev-set or held-out question that needs release notes or glossary content; then synthesize those two pages from their data files the way model pages are.

---

## D-022a · The generated starter cannot migrate: its app name is invalid

**Status:** default, flagged · 2026-09-08 · extends D-022

**Facts.** The starter migration calls `set_app_name(COLLECTION_NAME)` with the copier value `mistral_docs`. In the pinned toolkit, `VespaAppDefinition.name` is constrained to `^[a-z]+$` (lowercase letters only; `plugins/vespa/app/schemas/app.py`), while schema document types allow `^[a-z_]+$`. Any collection name containing an underscore, which copier accepts, makes `make setup-vespa` fail at validation. Found by the eval worker's offline test configuration; verified in the source.

**Decision.** The index package names the Vespa app with letters only (`glossator`) and keeps schema names separate from the app name (D-010, S3). Candidate for the fork notes (D-018).

---

## D-010a · Chunking measured on the full corpus

**Status:** decided · 2026-09-08 · refines D-010

**Facts** (411 pages, section chunker: target 600 Mistral tokens, hard cap 1024, whole-block packing, no split across headings, context line `page_title > H2 > H3` prefixed to the embedded text but excluded from the located span so `content == prefix + body[start:end]`):

| strategy | chunks | per page | tokens min / median / mean / max | with anchor |
|---|---|---|---|---|
| section | 4,430 | 10.8 | 9 / 135 / 219 / 5,737 | 2,360 (53%) |
| page (starter splitter, 4096 chars) | 1,022 | 2.5 | 4 / 972 / 889 / 2,593 | 0 |

- 110 section chunks exceed the cap; each is a table or code fence kept whole. Four corpus blocks exceed the embedder's 8,192-token input limit (largest 39k tokens); the chunker keeps blocks whole up to 7,000 tokens and cuts above, otherwise those blocks would never be indexed.
- The `/models` capability table is one 4,827-token chunk; on "which models support function calling" it loses to a migration-guide FAQ. D-006's matrix needs per-feature sections, not one table.
- The corpus contains an XML-illegal code point (`0x08` in a security advisory); Vespa rejects the whole document. Sanitization is applied at ingest and belongs in the corpus adapter as well.

---

## D-011a · Embedding cost and model availability, measured

**Status:** decided · 2026-09-08 · refines D-011

**Facts.** Full corpus into the section variant: 983,093 tokens, about 0.10 USD per variant; all three variants about 0.30 USD. Both `mistral-embed` (1024) and `mistral-embed-dim128-2510` (128) accept requests on the project key. On the 8-page fixture, 128 and 1024 dimensions order results almost identically; the comparison needs the eval set. The embedding API rate-limits a full run: at concurrency 8 with the embedder's default 3 retries, 81 of 411 pages were lost to 429s; at concurrency 3, 8 retries, plus one sequential retry pass, none.

---

## D-012a · Default ranking weights, with phases

**Status:** decided, to be tuned · 2026-09-08 · implements D-012

| feature | weight | phase | role |
|---|---|---|---|
| `bm25_content` | 0.5 | 1 | lexical relevance of the chunk body |
| `content_embedding_closeness` | 5.0 | 1 | vector term in candidate selection (0 in the starter) |
| `bm25_page_title` | 0.3 | 1 | question names the page |
| `bm25_heading_path_max` | 0.3 | 1 | best-matching heading in the path |
| `match_content` | 0.5 | 2 | proximity-aware field match |
| `content_embedding_cosine_similarity_score` | 5.0 | 2 | exact cosine on the rerank window |

Observed on the real corpus: phase-1 BM25 is overweighted for paraphrased questions ("how do I stream a chat completion" ranks the right section 2nd or 3rd, vector-only ranks it 1st); heading-path BM25 matches question-shaped headings regardless of subject ("what is the rate limit for the embeddings endpoint" returns a vision FAQ first); several chunks of one section crowd the top. These are the tuning targets for the retrieval grid.

---

## D-025 · Toolkit and Vespa facts from the index build

**Status:** decided · 2026-09-08

- Name constraints: app name `^[a-z]+$`, schema document type `^[a-z_]+$` (no digits). Variants are named `docs_page_lowdim`, `docs_section_lowdim`, `docs_section_fulldim`; the dimension lives in the config table.
- One Vespa application cannot serve two embedding dimensions unless every query restricts itself to its schema: `query(embedding)`'s type is resolved across all rank profiles, and the YQL `from` clause does not disambiguate. `model.restrict` passed through the retrieval context does.
- `VespaSearchQuery.ranking_weights` keys need the `_weight` suffix while `set_default_ranking_weights` keys do not. A bare feature name at query time is accepted and has no effect: four weight configurations produced byte-identical scores until the suffix was added. Fork-note candidate (D-018).
- The Vespa plugin hardcodes euclidean HNSW regardless of the embedding model's declared cosine metric. Fork-note candidate.
- An all-zero query embedding yields NaN relevance and a "Malformed search hit" error from the response parser.
- Retrieval uses the query-builder path with no named profile; the schema's generated default profile still carries the baked-in weights, so `exclude_ids` and filters work alongside tuned ranking (resolves D-014).
- The host disk sat at 90% during the build, above Vespa's 80% feed-block limit; the local deployment was patched with a higher resource limit outside the repository. A reviewer's machine below 80% is unaffected; the README should mention the limit.

---

## D-026 · The MCP server does not ingest

**Status:** decided · 2026-09-08

**Decision.** The starter's `ingest(uri)` and `delete(source_id)` MCP tools are removed. The index is built from the vendored corpus by `make ingest`; the MCP surface exposes search, navigation, and (later) `ask`.

**Facts.** The starter's ingest tool routes any URL or file through OCR or plain-text extraction with page-level chunks and no `url`, `anchor`, or `kind` metadata. Chunks written that way land in the serving variant and can never be cited or filtered (review finding on the S3 changes, 2026-09-08). A client-facing documentation engine should not let an agent push arbitrary content into the index it answers from; corpus changes go through the adapter, the manifest, and the link check.

---

## D-027 · Answer contract: structured answer with verifiable quotes, no streaming in v1

**Status:** decided · 2026-09-09

**Decision.** Every strategy returns the same `Answer`: markdown text with inline `[n]` markers, a list of citations `{n, url, anchor, chunk_id, quote, verified}`, an `insufficient_evidence` flag, the retrieval or tool trace, token usage, latency, and cost. The model produces the answer as structured output (JSON schema) whose citations carry a verbatim quote from the numbered source; a verifier checks each quote against the cited chunk's content after whitespace normalization and drops citations that fail, marking them in the trace. An answer with no verified citation is returned as insufficient evidence. Answers are not streamed in v1.

**Facts.** A citation that only names a source cannot be checked without a judge; a quote can be checked in code for free and is the primary "citation correctness" number (D-016). Streaming a JSON object token by token would make the quote check possible only after the stream ends, which removes the point of streaming; the API can add a streamed text-first mode later if latency numbers justify it. Mistral Medium 3.5 supports structured outputs and function calling (model card, 2026-09-08).

**Strategies compared** (named by what differs, D-016): `single_pass` (one retrieval, one generation), `search_loop` (tool-use loop over search, open, grep, read with a round cap and seen-chunk deduplication), `outline` (the model picks pages from the site outline, reads their sections, then answers).
