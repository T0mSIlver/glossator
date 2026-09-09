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

---

## D-028 · Provider quotas that shape the evaluation schedule

**Status:** decided · 2026-09-09

**Facts.**
- The Mistral account is on the free tier (not yet provisioned for paid use as of 2026-09-08 night). Every Mistral call is free but rate-limited; the 429s seen while embedding the full corpus (D-011a) were free-tier limits. Evaluation runs against Mistral models are governed to about one request per second with retries instead of concurrency.
- The z.ai coding plan (level "lite") exposes its quota at `GET https://api.z.ai/api/monitor/usage/quota/limit`: a 5-hour token window reported as a percentage (33% used at 00:04 on 2026-09-09, reset 03:00), plus a separate limit for its search tools. The absolute token budget is not published.
- Codex on the ChatGPT plan hit its 5-hour usage limit at 23:1x on 2026-09-08 (reset 02:09), which cut one worker mid-turn and one review before it reported.

**Decision.** Every tool that calls GLM polls the quota endpoint before a batch and pauses when the window is above 80%; runs checkpoint per candidate so a pause resumes without loss (D-023 records are append-only). Long generations are split into batches spread over the quota windows. Reviews and workers move between codex, opencode (GLM, muse) and opus subagents according to which provider has headroom, and the ledger records which one did what.

---

## D-029 · MCP surface rules carried over from vidtheque

**Status:** decided · 2026-09-09

Rules that vidtheque paid for in two consumer evaluations (a tool-design bench with weaker models, and a blind evaluation with six agents of another vendor) and that apply unchanged to a documentation engine. Sources: vidtheque `docs/design/DECISIONS.md`, `research/mcp-design-bench-2026-08-09.md`, `research/mcp-eval-terra-2026-08-10.md`, `mcp/src/vidtheque_mcp/tools/{descriptions,resources,params}.py`, `errors.py`, `text.py`.

- **Server instructions name the happy-path order, the guide resource, and the one unforgivable sin in one breath.** glossator: "Start with search, open and read the section before answering; prefer `ask` for questions and the navigation tools for exploration. Read `glossator://guide` for the shared rules; never fabricate documentation URLs or anchors: cite only a URL and anchor exactly as a tool printed them."
- **Tool descriptions stay under about 120 words; shared rules live once in a guide resource.** Nine copies of shared rules cost about 4k tokens of permanent context per session. Each description keeps purpose, USE WHEN, DO NOT USE (naming the tool to use instead), and START WITH parameters. Line one is a complete clause under 80 characters, because some clients show only that.
- **Three resources, and the guide says there are no others**, so a cold-start model does not invent `glossator://help`: `glossator://guide` (rules and flow), `glossator://index` (page list), `glossator://context` (limits, id formats, corpus commit and freshness).
- **Every response ends with a `next:` hint tuned to that result, and it must agree with the guide.** Pagination lines are copy-pasteable ("Results: 5/12, use offset=5 for more").
- **Clamp server-side, never silently.** A clamp prints "note: clamped server-side: limit=500 → 50". Expensive paths (candidate pool, reranker candidates, loop rounds) are bounded independently of `limit`, so `limit` never changes ranking.
- **Truncation markers name only parameters the calling tool accepts.** A marker that names a parameter the tool lacks is a trap that reports no failure.
- **Unknown parameter names are rejected with `E_BAD_PARAM` naming the right one**, never dropped; a call that returned results applied every argument sent.
- **Errors are typed, carry an HTTP-shaped status, and name the next call.** `E_UNKNOWN_PAGE` tells the model to use a URL exactly as a result printed it, never one recalled from memory. `E_BUSY` says retry the identical call, because "narrow the query" taught a model to abandon search.
- **Empty results are never bare.** Say which kind of empty (no page matched the filter, legs ran with no lexical footing, corpus lacks the topic), echo the query, and give a `next:`.
- **Per-unit citations.** Every retrieved section carries its canonical `url#anchor` built by one constructor; long payloads print the anchor on each unit so the model never reuses the page-top link for a section further down. Citations in `ask` answers are drawn only from recorded evidence; an `[n]` naming nothing is stripped rather than rendered.
- **"all means all":** a search leg or filter that cannot apply prints a `note:` and never narrows silently; counts print kept over considered (`vec 11/800`), never a bare number.

---

## D-030 · Score floors and a lexical-footing gate make refusal possible

**Status:** decided, to calibrate · 2026-09-09

**Facts** (vidtheque `research/vec-floor-calibration-2026-08-10.md`, `research/mcp-eval-terra-2026-08-10.md` §4.1). With k-nearest-neighbour search and no ceiling, every query matches something: a junk query ("feline hyperthyroidism") returned 401 rows over 120 videos, and an unanswerable question got a confident wrong top hit at three identical RRF tie scores. Calibrating on 12 real and 10 junk queries showed a 0.12-wide empty corridor between the worst real best-hit distance and the best junk one; an absolute distance ceiling plus a relative margin over the query's own best hit cut junk to 0 rows and left rank-1 unchanged, at a quarter of the latency. A lexical-footing gate (skip vector legs when no query word occurs anywhere in the corpus) is what makes "0 results" reachable and lets the model say the corpus does not cover the topic; four of four unanswerable tasks were refused correctly in the blind evaluation after it shipped.

**Decision.** glossator's retriever gets (a) an absolute cosine-similarity floor and (b) a relative margin below the query's best hit, both calibrated on the live Vespa index with real questions from the dev set and junk questions, with the measured distributions recorded beside the constants; (c) a lexical-footing check that reports "no lexical footing" in the trace; (d) hit counts reported as kept over considered. The `unanswerable` question type in the eval measures the effect (D-016). Calibration is part of the retrieval grid work.

---

## D-031 · Embedding sanity probe at index time

**Status:** decided · 2026-09-09

**Facts** (vidtheque `research/embedding-random-init-2026-08-10.md`). A checkpoint-loading mismatch left an embedding model with random weights for 36 hours; every stored vector was noise, search still returned plausible results, and every shape check (model name, dimensions, unit norm) passed, because none of them describes whether the weights are real. The fix that caught it: embed fixed probe documents and queries, assert the known top-1 matches and a score separation between related and unrelated pairs, and refuse to serve on failure; plus a stored-versus-re-embedded round trip.

**Decision.** `make ingest` and the retrieval engine's startup run a semantic probe against the configured embedding model and variant: five fixed probe pairs with known nearest neighbours and a minimum separation; a stored chunk re-embedded must match its stored vector. Failure aborts ingestion or marks the engine unhealthy. The probe results and thresholds are recorded with the run.

---

## D-032 · Evaluate the MCP surface with blind consumers on a weaker model

**Status:** decided · 2026-09-09

**Facts.** vidtheque's two evaluations found their defects by giving real tasks to agents that were not told they were evaluating anything, on a weaker model than the author's, with every wrong turn treated as a surface defect until proven otherwise, every server-side claim reproduced by hand with the command printed, a severity scale (wrong or unreachable answer; extra calls; friction), and a byte-identical re-run after fixes to show regressions honestly.

**Decision.** Before the tag, run the same protocol on glossator's MCP server: several personas (first contact, exhaustive reader, unanswerable questions, stress tester, a coding agent integrating the SDK), on codex or GLM clients connected as ordinary consumers, transcripts kept, findings classified and fixed in prose or code, then re-run. Tom's own hand test on his private questions is the final pass.

---

## D-017a · Model ids and the free-tier model allowlist

**Status:** decided, blocked on account provisioning · 2026-09-09

**Facts** (verified against the project key, 2026-09-08 22:00 to 2026-09-09 00:30 UTC).
- `client.models.list()` returns 46 ids. Mistral Medium 3.5's fixed id is `mistral-medium-2604`, aliased by `mistral-medium-latest`, `mistral-medium-3-5`, `magistral-medium-latest` and five others. Mistral Small 4 is `mistral-small-2603`. No `mistral-large-*` id exists on this account, so the Large 3 price line in D-017 has no reachable model.
- On this key, every request to `mistral-medium-*`, `mistral-small-*` and `magistral-*` returns HTTP 429 with `x-ratelimit-limit-req-minute: 0`, a configured quota of zero, while `ministral-3b/8b/14b-2512`, `codestral-2508` and `mistral-embed` answer normally in the same second. Backoff cannot get through a zero limit. Tom's account had not been provisioned for paid use when this was observed.
- The answer-layer smoke therefore ran on `ministral-8b-2512`: 27 calls, 89,582 prompt and 10,679 completion tokens, 0.015 USD; the same tokens on Medium 3.5 prices would be 0.21 USD.

**Decision.** Until the account is provisioned, evaluations run on the largest reachable Mistral model (`ministral-14b-2512`) and the generation model is an explicit column of every answer eval, so the Medium 3.5 numbers are one re-run of the same records when the quota opens. The shipped default stays Medium 3.5 (D-017); the README states which model produced which table.

---

## D-027a · What the first answer-layer smoke showed

**Status:** decided · 2026-09-09 · refines D-027

**Facts** (five questions, three strategies, Ministral 8B, `eval/runs/2026-09-09-answer-smoke/`).
- A verified quote does not make a correct answer: on the unanswerable question "maximum number of tool calls in one response", two strategies answered "128", citing the genuine sentence "Maximum number of tools per request: 128", which is about declared tools. The quote verifier cannot see this; only the judge (D-016) can. `outline` alone refused.
- When the answer is a table (which models support function calling), one retrieval of eight chunks lost it; reading the page (`outline`) or opening the chunk's neighbourhood (`search_loop`) kept it.
- Roughly half the rejected citations were paraphrases presented as quotes; the verifier dropped 14 of 50 citations across the run.
- `single_pass` assembled 1.9k to 3.0k context tokens against a 6,000-token budget with `top_k` 8; `outline` overflowed the budget with four pages. `search_loop` cost 2.6 times `single_pass` and often stopped after its seed search.
- Markers are parsed outside code only and numbering starts at 1, because `choices[0]` in a code block was read as a citation.
- Serving-path calls are recorded but never cached; a cached answer to a repeated question would be a different product. The AGENTS.md convention applies to offline tools only.

**Consequence.** The answer eval grid varies `top_k`, the context budget, and the page cap, and reports distinct cited sources rather than citation counts. Anchorless first chunks should fall back to the nearest following anchor when one exists.

---

## D-020a · The development set, as generated

**Status:** decided · 2026-09-09

**Facts.** `eval/dev.jsonl`: 294 questions (50 each of single_page, cross_page, api_reference, post_cutoff, unanswerable; 44 capability after 6 duplicates were dropped, the feature space being small), generated by `glm-5.3-flash` in four runs (one 12-question smoke, three 96-question batches with seeds 1 to 3) over the vendored corpus, each run under `eval/runs/` with every call and every candidate recorded. Each batch filled all six types from 192 candidates in about seven minutes and 515 calls (about 720k tokens); the z.ai token window did not move measurably (44% before and after), while an agentic opencode review moved it by about 10 points. Three 429s per batch were retried. A hand spot check of twelve questions found realistic, standalone questions with correct gold pages and anchors. `eval/dev.README.md` records the hash and provenance.

`eval/dev-fr.jsonl`: 36 stratified questions from the dev set translated into French by `glm-5.3` with identifiers, model names and code kept verbatim (`glossator.eval.translate`, run `eval/runs/2026-09-08-2253-dev-fr`), so D-008 can be measured as French questions over English pages without a French corpus.

**Decision.** The dev set is frozen at this hash for tuning; the held-out set (Tom's, hand-written) is the reporting set. Questions the answer eval flags as broken are fixed by regenerating with a new seed, never by hand-editing a generated question, so provenance holds.

---

## D-033 · Baseline answer evaluation: what the three strategies do on sixty development questions

**Status:** decided · 2026-09-09 · run `eval/runs/2026-09-08-2305-dev60-baseline`

**Facts** (60 stratified dev questions, `sec1024`, shipped retrieval defaults, no reranker, Ministral 3 14B as the generator because Medium 3.5 is rate-limited to zero on this key, GLM 5.3 as the blinded judge; 180 answers, 0 errors):

| metric (all types) | single_pass | search_loop | outline |
|---|---|---|---|
| correctness (judge, 1 / 0.5 / 0) | 0.81 | **0.93** | 0.65 |
| groundedness (judge) | 0.75 | **0.81** | 0.65 |
| refusal correct (both directions) | 0.82 | **0.88** | 0.72 |
| cited URL matches gold | 0.70 | **0.78** | 0.42 |
| cited anchor matches gold | **0.50** | 0.40 | 0.18 |
| quote verification rate | 0.86 | 0.82 | **0.89** |
| fabricated quotes per answer | 0.40 | 0.55 | **0.23** |
| latency p50 | **3.0 s** | 7.4 s | 3.7 s |
| prompt tokens per answer | **1.9k** | 16.0k | 8.9k |
| USD per question at Medium 3.5 prices | **0.005** | 0.028 | 0.016 |

- `search_loop` wins every quality metric except anchor precision and quote verification, at 8 times the tokens and 2.5 times the latency of `single_pass`; it averages 4.7 tool calls and 3.1 rounds, and 8.7 calls on unanswerable questions, where it keeps searching.
- `outline` is the weakest on eight of eleven metrics. Its API-reference correctness is 0.15 because the outline offered to the model excludes API pages by design (their titles carry no signal), and cross-page questions overflow its page budget.
- Anchor precision is low for a structural reason: of 42 verified citations on the right page, 22 carry no anchor at all and 12 a different one. The generator's gold anchor is the section heading's, while the cited chunk sits in a nested subsection whose heading is not deep-linkable (D-003a), so the chunk has `anchor: None`.
- Capability questions: retrieval ranks the `/models` matrix first (checked on "which models support FIM"), yet `single_pass` cites model cards and feature pages instead (URL match 0.10, correctness 0.80): the gold is stricter than the content, since a model card is also a correct source.
- Fabricated quotes (a sentence not in the cited source) run 0.2 to 0.55 per answer on Ministral 14B; cosmetic rejections are zero after the emphasis-normalization fallback.
- Refusals still write `[n]` markers that name nothing (0.8 to 1.0 per unanswerable answer).

**Decisions.**
1. `outline` leaves the candidate list for the shipped default; it stays in the grid as a documented experiment.
2. The default strategy is decided after the retrieval improvements (reranker, floors) are measured, because `single_pass` gains the most from better ranking; `search_loop` is the quality reference and the cost row beside it.
3. Product changes taken now: a chunk's citation anchor falls back to the nearest anchored ancestor heading, so a deep link lands on the closest linkable section instead of the page top; `[n]` markers that name no citation are stripped from the answer text (D-029); the outline strategy's page list includes API pages when the question mentions an endpoint, method or path.
4. Capability gold accepts the model card of a model the question names, in addition to the matrix page, at the next dataset regeneration.

---

## D-015a · The listwise reranker, measured

**Status:** decided · 2026-09-09

**Facts.** One call per query, 20 candidates each cut to 300 Mistral tokens; hits past the twentieth come back after the ranked ones rather than being dropped. On `ministral-14b-2512` (fixture run, 24 calls): mean 4,585 prompt and 396 completion tokens, 0.00075 USD per call at Ministral prices and 0.00093 USD at Mistral Small 4 prices; median latency 4.0 s against 7.6 ms without it. 2 of 24 calls (8%; 12.5% on an earlier run) returned an unusable ranking, always by dropping candidates, never by repeating or inventing one; the reranker then falls back to retrieval order and says so in the trace. Billed calls, applied rankings and budget-skipped rows are three separate counts.

**Decision.** Serving default stays Mistral Small 4 (D-017); every evaluation names its reranker model (D-017a). The reranker budget for the dev-set grid is 600 calls so both reranked rows cover every question.

---

## D-016a · What counts as a retrieval hit

**Status:** decided · 2026-09-09

**Decision.** Two matchings, reported separately: page level (hit URL equals a gold URL) and section level (URL and anchor). A question whose gold carries no anchor on any source is scored at page level only, never as a section miss, so the two matchings score different numbers of questions and every table carries its own count. The ranked list is collapsed to distinct pages (or sections) at their best rank before scoring, so recall@k means "the answer was among the first k pages". Unanswerable questions are excluded from recall and reported with the top hit each configuration returned.

**Facts.** The toolkit's nDCG builds its ideal DCG as if each relevant id appears once; under URL proxies several chunks of one page score the same proxy and nDCG@10 came out at 1.220 before the de-duplication. Fork-note candidate (D-018).

---

## D-025a · Two more toolkit facts

**Status:** decided · 2026-09-09

- A hit's cosine similarity cannot be read from a search result: the toolkit drops Vespa's `matchfeatures`. Reading it takes a second query restricted to the hits' ids (`id in (...)`) and ranked with every weight zeroed except the cosine term. The restriction is required because the HNSW index is euclidean (D-025): an unrestricted vector-only query returns a different candidate set whose top cosine can be lower (0.7251 against 0.7884 on the same query).
- A grid that embeds each question once per configuration loses queries to free-tier 429s (6 of 156 on the first fixture run). The query vector depends on the embedding model, not the weights, so the grid embeds once per (model, question) and throttles every API call at 1.1 s; the engine's embedder retries 8 times instead of the toolkit's 3 (D-011a). Zero errors on the second run.

---

## D-030a · First sighting of the similarity corridor

**Status:** open · 2026-09-09 · refines D-030

**Facts** (fixture calibration, `eval/runs/2026-09-08-2331-fixture-floors`, not to be adopted): real questions' best-hit cosine 0.798 to 0.840 (median), junk questions 0.609 median and 0.675 max, a corridor 0.12 wide; 5 of 15 junk queries had no lexical footing, 0 of 11 real ones. The one unanswerable question's best hit was 0.824, above any floor that keeps the real questions. A floor separates another subject from this documentation; it does not separate answerable from unanswerable, and the footing gate cannot either, because unanswerable questions are made of the corpus's own words.

**Decision.** Floors stay unset until the dev-set calibration is read; the unanswerable case is the generator's and the judge's problem (D-016, D-033), not the retriever's.

---

## D-031a · Embedding probe thresholds, measured

**Status:** decided · 2026-09-09

| constant | value | measured at 1024 dims | measured at 128 dims |
|---|---|---|---|
| minimum related similarity | 0.55 | 0.755 | 0.666 |
| minimum separation from the next-best passage | 0.05 | 0.095 | 0.132 |
| minimum stored-versus-re-embedded similarity | 0.999 | 0.99997 | 0.99999 |

Separation is the check that catches random weights; raw similarity does not, because untrained embeddings put every text at the same distance from every other. The stored vector is read back through `get_chunk`, which surfaces the tensor. `make ingest` runs the probe before embedding anything; the search CLI runs it once per process.

---

## D-023a · Test runs mutate the serving index

**Status:** open · 2026-09-09

**Facts.** The ingestion integration test writes the fixture corpus into the shared `sec128` schema, and one fixture page shares its URL with a real page, so `make test` replaces that page's chunks and adds eight fixture pages beside the real corpus. The fixture retrieval grid did the same to all three variants; the real `/models` page was re-ingested afterwards and the fixture-only pages deleted from `sec1024` and `page128`.

**Decision.** Fixture pages get a URL prefix that cannot collide with the corpus, and the integration test filters to its own pages (done); a test-only schema is the durable fix if the collision recurs.

---

## D-025b · A redeploy on a full disk empties the index

**Status:** decided · 2026-09-09

**Facts.** The host disk sat at 92%. Vespa blocks external feeds above 80% of disk, and the toolkit's generated `services.xml` offers no seam for `<resource-limits>`, so the local deployment carried a hand-patched limit (D-025). At 01:55 a worker redeployed the application package through the toolkit's CLI, which reset the limit; its `make ingest` then had every feed rejected, and because re-indexing deletes a page's chunks before writing the new ones, the `sec1024` schema was left with zero documents. The retrieval grid's two reranked rows and the first floor calibration ran against the empty schema and scored zero; the eleven non-reranked rows had completed before it. The patched package was redeployed and `sec1024` re-ingested (4,440 chunks, zero failures); the reranked rows and the calibration were re-run as separate run directories.

**Decisions.** (1) Ingestion must not delete before it has something to write: the pipeline verifies that the embedding step succeeded and the feed is accepted for the first page before deleting anything, and aborts on the first "Failed to index document" instead of continuing through 411 pages. (2) The README warns that Vespa refuses feeds above 80% disk. (3) Only one process writes to Vespa at a time during evaluation runs.

---

## D-030b · Similarity floors stay off in v1

**Status:** decided · 2026-09-09 · reverses the "to calibrate" part of D-030 · run `eval/runs/2026-09-09-0115-dev-floors`

**Facts** (294 dev questions and 15 junk questions against `sec1024`, cosine of the top-50 hits):

| population | n | best hit, min | best hit, median | best hit, max |
|---|---|---|---|---|
| real (answerable) | 244 | 0.696 | 0.865 | 0.927 |
| junk (cooking, veterinary, astronomy, sport) | 15 | 0.546 | 0.609 | 0.679 |
| unanswerable (corpus vocabulary) | 50 | 0.723 | 0.825 | 0.871 |

- The corridor between the worst real question and the best junk question is 0.017 wide (0.679 to 0.696); the proposed floor 0.687 sits inside it with no safety margin for a held-out question the corpus phrases differently.
- All 50 unanswerable questions clear any floor that keeps the real ones, by a wide margin (their median best hit is 0.825). The floor cannot help the refusal case, which is the case that matters for answer quality (D-033).
- The lexical-footing gate never fires on this corpus: 0 of 15 junk questions lack a content word found somewhere in 411 pages of prose. The vocabulary is too broad for the gate that worked on vidtheque's transcript corpus.

**Decision.** `similarity_floor` and `similarity_margin` stay `None` in v1; the footing check stays available in the trace but gates nothing. Off-topic questions are handled by the answer layer's insufficient-evidence path and measured by the judge. The calibration tool and this run stay in the repository so the decision can be revisited on a corpus where the corridor is wide.

---

## D-034 · Shipped retrieval: section chunks, vector-heavy weights, listwise reranker on

**Status:** decided · 2026-09-09 · run `eval/runs/2026-09-09-0136-dev-grid-v2` (294 dev questions, 13 configurations, 20 hits per row collapsed to distinct pages or sections before scoring, reranker on Ministral 14B)

| configuration | page r@1 | page r@5 | page r@10 | page MRR | section r@1 | section r@5 | section MRR | median ms |
|---|---|---|---|---|---|---|---|---|
| page128-shipped (starter chunking, 128 dims) | 0.619 | 0.900 | 0.959 | 0.816 | 0 | 0 | 0 | 12 |
| sec128-shipped | 0.619 | 0.871 | 0.941 | 0.791 | 0.747 | 0.915 | 0.814 | 7 |
| sec128-vector-heavy | 0.605 | 0.879 | 0.920 | 0.789 | 0.761 | 0.958 | 0.841 | 6 |
| sec1024-shipped | 0.592 | 0.861 | 0.936 | 0.771 | 0.704 | 0.880 | 0.784 | 11 |
| sec1024-vector-heavy | 0.596 | 0.863 | 0.926 | 0.774 | 0.732 | 0.937 | 0.807 | 9 |
| sec1024-lexical-heavy | 0.584 | 0.859 | 0.900 | 0.765 | 0.662 | 0.866 | 0.752 | 9 |
| sec1024-heading-path-off | 0.600 | 0.869 | 0.916 | 0.786 | 0.697 | 0.887 | 0.780 | 9 |
| sec1024-shipped+rerank | 0.703 | 0.895 | 0.939 | 0.868 | 0.817 | 0.922 | 0.864 | 4,427 |
| **sec1024-vector-heavy+rerank** | **0.711** | **0.920** | 0.934 | **0.880** | **0.873** | **0.979** | **0.918** | 4,392 |

Section-level numbers cover the 142 questions whose gold names an anchor; page-level numbers cover all 244 answerable questions.

**Facts.**
- Whole-page chunks (the starter's splitter) cannot deep-link at all (section recall 0) and only match section chunks at page level once the depth is equalized: ten page chunks are eight distinct pages, ten section chunks are six. The 20-hit depth is what makes page-level numbers comparable across chunkings.
- The reranker is the largest single gain: page recall@1 from 0.60 to 0.71, section recall@1 from 0.73 to 0.87, API-reference recall@1 from 0.64 to 0.90, at a median 4.4 s per query and 0.0007 USD per call on Ministral (0.0009 at Small 4 prices); 37 of 294 calls (13%) returned a ranking that could not be applied and fell back to retrieval order.
- Vector-heavy weights (closeness 8, BM25 0.3) beat the migration's baked-in weights on section metrics for both dimensions; lexical-heavy weights lose everywhere; switching heading-path BM25 off changes little.
- 128 dimensions are not worse than 1024 without the reranker (section recall@1 0.747 against 0.704); the reranker was only run on 1024. Storage is the only cost difference, since the embedding tokens are the same.
- Capability questions stay hard for retrieval at rank 1 (0.51 reranked): the gold is the matrix page while model cards also carry the fact (D-033).

**Decision.** The product serves `RetrievalConfig.shipped()`: `sec1024`, vector-heavy weights, reranker on, with `rerank=False` as the documented fast path (median 9 ms). The reranker's serving model is Mistral Small 4 (D-017); `GLOSSATOR_RERANK_MODEL` overrides it, and every evaluation records the model used. Reranking on `sec128` and the reranker prompt's 13% fallback rate are the two follow-ups the numbers point at.

---

## D-033a · The anchor fallback and marker stripping, measured

**Status:** decided · 2026-09-09 · runs `dev60-baseline` against `dev60-anchors` (same 60 questions, Ministral 14B, shipped weights, no reranker)

| metric | single_pass before → after | search_loop before → after |
|---|---|---|
| cited URL matches gold | 0.70 → 0.76 | 0.78 → 0.80 |
| cited anchor matches gold | 0.50 → 0.58 | 0.40 → 0.48 |
| quote verification rate | 0.86 → 0.89 | 0.82 → 0.87 |
| fabricated quotes per answer | 0.40 → 0.28 | 0.55 → 0.37 |
| correctness (judge) | 0.81 → 0.83 | 0.93 → 0.94 |
| citation relevance (judge) | 0.89 → 0.98 | 0.91 → 0.94 |
| refusal correct | 0.82 → 0.87 | 0.88 → 0.88 |

Every chunk now carries the anchor of the nearest anchored heading above it, so citations deep-link to the closest linkable section instead of the page top; markers that name no verified citation are stripped from the answer text and kept in the trace. The fabricated-quote drop is partly the emphasis-normalized verification counting cosmetic matches as verified (D-027a). One capability question per strategy matched gold only through the model-card relaxation (D-033, decision 4), reported as `gold_relaxed_matches`.

---

## D-035 · Shipped strategy: single pass over reranked retrieval; the search loop is the thorough mode

**Status:** decided · 2026-09-09 · run `eval/runs/*-dev60-rerank` (same 60 questions as D-033, shipped retrieval per D-034, Ministral 14B generating and reranking, GLM 5.3 judging)

| metric | single_pass, no rerank (D-033) | single_pass, shipped | search_loop, shipped |
|---|---|---|---|
| correctness (judge) | 0.81 | **0.93** | 0.95 |
| groundedness (judge) | 0.75 | 0.82 | 0.85 |
| citation relevance (judge) | 0.89 | 0.94 | 0.98 |
| refusal correct | 0.82 | **0.92** | 0.90 |
| cited URL matches gold | 0.70 | 0.82 | 0.82 |
| cited anchor matches gold | 0.50 | **0.62** | 0.54 |
| quote verification rate | 0.86 | 0.86 | 0.86 |
| latency p50 / p95 | 3.0 / 7.7 s | **7.2 / 12.0 s** | 20.7 / 46.0 s |
| prompt tokens per answer | 1.9k | **2.0k** | 14.8k |
| USD per question at Medium 3.5 prices | 0.005 | **0.005** | 0.026 |

**Facts.**
- Reranking closed most of the gap between the two strategies: single pass gained 12 points of correctness, while the search loop, which already read around its hits, gained one. What the loop still buys is 2 to 4 points of judged quality at three times the latency and five times the cost.
- The loop's latency tripled under the shipped retrieval because every tool search now reranks; a loop whose intermediate searches skip the reranker and only the final assembly reranks would recover most of that, and is the natural follow-up if the thorough mode is used.
- Refusal on unanswerable questions is the one metric where single pass leads, because the loop keeps searching (8.7 tool calls on unanswerable questions in D-033) and finds something to cite.

**Decision.** `ask` defaults to `single_pass` on the shipped retrieval. `search_loop` stays available through the `strategy` parameter of the API and the MCP `ask` tool as the thorough mode, with its cost stated in the tool description; `outline` stays as an experiment row only (D-033). The numbers above are Ministral 14B's; the same three run directories are re-run on Mistral Medium 3.5 by one command when the account is provisioned (D-017a).

---

## D-008a · French questions over the English index, measured

**Status:** decided · 2026-09-09 · run `eval/runs/*-devfr-shipped` (36 French translations of dev questions, shipped retrieval, single pass, Ministral 14B, GLM judge) against the same strategy on English questions (`dev60-rerank`)

| metric | French questions | English questions |
|---|---|---|
| cited URL matches gold | 0.47 | 0.82 |
| cited anchor matches gold | 0.40 | 0.62 |
| correctness (judge) | 0.75 | 0.93 |
| groundedness (judge) | 0.65 | 0.82 |
| fabricated quotes per answer | 0.67 | 0.40 |
| refusal correct | 0.83 | 0.92 |
| prompt tokens per answer | 3.8k | 2.0k |

**Facts.** Option (a) of D-008 (English index, the model answers in the question's language) loses a third of its retrieval precision: `mistral-embed` is multilingual but the hybrid ranking's BM25 half sees no French term in English pages, and the reranker reads French against English. The model does answer in French and cites English sources, and citation relevance stays at 0.95, so the failure is in finding the right page, not in writing the answer.

**Decision.** The engine translates a non-English question into English for retrieval and reranking, and generates the answer in the question's language from the English sources. This costs one short model call per non-English question and no index change. Indexing the French mirror (option b) stays the follow-up if the translated-query result is still short of the English numbers, since French pages would let citations land on French URLs.

---

## D-008b · Rendering the question in English for retrieval closes the French gap

**Status:** decided · 2026-09-09 · run `eval/runs/2026-09-09-0420-devfr-translated` (same 36 French questions as D-008a, shipped configuration)

| metric | French as asked | French rendered in English for retrieval | English |
|---|---|---|---|
| cited URL matches gold | 0.47 | **0.80** | 0.82 |
| cited anchor matches gold | 0.40 | **0.57** | 0.62 |
| correctness (judge) | 0.75 | **0.94** | 0.93 |
| groundedness (judge) | 0.65 | **0.80** | 0.82 |
| judged wrong | 0.14 | **0.00** | 0.02 |
| fabricated quotes per answer | 0.67 | 0.67 | 0.40 |
| latency p50 | 8.3 s | 12.6 s | 7.2 s |

**Facts.** Language detection is deterministic (stopword scores with diacritics folded, `und` for non-Latin scripts) and was right on 294 of 294 English and 36 of 36 French questions, so English questions pay nothing. The rendering is one structured call (about 215 tokens, 0.7 s median, 0 failures in 36) recorded like every other call; the model still sees the original question and answers in its language. The extra latency is mostly a longer generation now that the sources are usable (two cited sources per answer instead of 1.3). Fabricated quotes did not move: French prose around English sources still costs two thirds of a mistranslated quote per answer, the one French-specific failure that remains; a French index (D-008 option b) would address it by letting citations land on French pages.

**Decision.** `translate_for_retrieval` is on by default in the answer layer. The MCP `search` tool and the retrieval CLI still search the raw query; rendering there is a follow-up. D-008 is closed for v1 with option (a) plus rendering.

---

## D-036 · Citations deep-link to the quoted sentence with text fragments

**Status:** decided · 2026-09-09

**Decision.** Every verified citation carries a second link, `url#anchor:~:text=<quote>` (URL Fragment Text Directives), built from the quote the verifier already checked; the canonical `url#anchor` stays beside it. Chromium, Safari 16 and Firefox 131 and later scroll to and highlight the span; other browsers land on the anchor or the page. Quotes over 120 characters use the `start,end` form.

**Facts.** Most headings on docs.mistral.ai have no anchor (D-003a), so a citation often lands on a section top or the page top even when the engine holds the exact sentence. The verified quote is, by construction, a span of the page; on three citations checked by hand the stripped quote occurs exactly once in the vendored page. Rehosting the documentation with generated anchors was rejected: the brief asks for links back to the documentation pages, and a mirror would break that.

---

## D-037 · Demo target: a custom Connector in Mistral Work, behind a tunnel

**Status:** decided by Tom · 2026-09-09

**Decision.** The engine is demonstrated inside Mistral Work as a custom MCP Connector: the MCP server runs on Tom's machine behind a Cloudflare tunnel to an LXC container (the vidtheque deployment pattern), registered from the Connectors page with the server URL and a bearer token. Vibe Code CLI over stdio is the local fallback that cannot fail on conference network, and `client.beta.connectors.create_async(name, server=url)` is the API-side registration shown as the "ship to a client" path.

**Facts** (docs corpus, 2026-09-07 commit). Work's Connectors page has a "Custom MCP Connector" tab taking a server URL; auth is auto-detected (none, HTTP bearer or basic, OAuth 2.1); users can pre-authorize read functions per Connector so `search` and `ask` run without approval prompts (`vibe/work/connectors/mcp-connectors`). The Vibe Code CLI configures MCP servers in `config.toml` over `stdio`, `http` or `streamable-http` with a static header and does not support OAuth yet (`vibe/code/cli/mcp-servers`). The Agents API registers a Connector by URL with private, workspace or organization visibility, and a Connectors Debugger validates connectivity (`studio/connectors/management`). Tom confirmed his plan can add a custom Connector.

**Consequences for the code.** A bearer-token check on the HTTP transport (`GLOSSATOR_MCP_TOKEN`; the Connector and Vibe both send a static `Authorization` header); `/health` reachable for the Connectors Debugger; the tunnel and LXC setup documented outside the repository, with only a `make mcp` bind option in the README. The blind consumer evaluation (D-032) runs against the same HTTP transport the Connector will use.

---

## D-038 · A second question set mined from real failures

**Status:** decided · 2026-09-09 · `eval/mined.jsonl` (85 questions, sha256 `a276e09f…`), provenance in `eval/mined.README.md`

**Facts.**
- Sources: 54 questions from public GitHub issues (client-python 38, platform-docs-public 10, cookbook 4, mistral-common 2; client-js has issues disabled) and 31 from agent sessions on this machine, every row traceable to an excerpt. Types: single_page 60, api_reference 11, unanswerable 9, cross_page 4, capability 1. All gold links validate against the corpus, and the test suite now validates every dataset under `eval/` so a gold link that stops resolving fails the build.
- Real failures have a different shape from generated questions: one fact on one page (cross-page is 4 of 85), a quarter of the answers on two long FAQ-shaped pages (`resources/known-limitations`, `basic_ocr#faq`), and nine questions the documentation genuinely does not answer (no status page, no local token counting, no server-side timeout), which is a stricter refusal test than invented unanswerables because relevant context exists to over-reach from.
- The commonest stumble classes: a parameter present on the endpoint but absent from the caller's SDK build (14), formats and limits nobody could find (13), constraints discovered only by hitting them (11), a quickstart that does not run (8), rate limits and error bodies (5), deprecation drift (5).
- Search Toolkit and Vespa questions (29 of 85) exist only in transcripts, because the toolkit has no public issue tracker (D-018). Other Claude Code projects on this machine (159 directories, five mentioning Mistral) held no usable stumble.

**Decision.** `eval/mined.jsonl` is the second reporting set beside the generated dev set: never used for tuning, run with every answer evaluation from now on, and the set the talk leads with, since these are the questions users actually had. Tom validates the rows from `.local/runs/t4/mined-validation.md` before the numbers are quoted.

---

## D-035a · Sanity check on questions never used for tuning, and chunking at the answer level

**Status:** decided · 2026-09-09 · runs `*-fresh60-shipped`, `*-fresh60-page128` (60 stratified dev questions never used in an answer evaluation; `eval/dev-fresh60.jsonl`), single pass, Ministral 14B

| metric | tuned 60, S1024 · W-vec · R | fresh 60, S1024 · W-vec · R | fresh 60, P128 · W-vec · R |
|---|---|---|---|
| cited URL matches gold | 0.82 | 0.84 | 0.72 |
| cited anchor matches gold | 0.62 | 0.74 | 0.34 |
| quote verification rate | 0.86 | 0.85 | 0.79 |
| fabricated quotes per answer | 0.40 | 0.53 | 0.75 |
| refusal correct | 0.92 | 0.87 | 0.85 |
| correctness (judge) | 0.93 | 0.84 | 0.81 (44 of 60 judged) |
| prompt tokens per answer | 2.0k | 2.2k | 4.8k |

**Facts.** The retrieval-side numbers hold on unseen questions (URL and anchor match are equal or better), so the shipped configuration was not tuned to the sixty questions it was chosen on; judged correctness is 8 points lower on the fresh slice, within what sixty questions and one judge can swing (a 95% interval on 60 is about ±0.09), and the judge study (T1) re-scores both slices with blinded prompts and several judges before that gap is read further. Whole-page chunks lose at the answer level as well as in the grid: 12 points of URL precision, 40 of anchor precision, more fabricated quotes, and twice the prompt tokens, because a page-sized context gives the model more text to misquote from. Fifteen judge calls on the P128 run failed with z.ai per-minute 429s while another process was judging; the answers are recorded and the re-judge pass covers them.

**Decision.** Section chunks stay (D-034). All later answer evaluations report both the tuned slice and the fresh slice, plus the mined set (D-038), so tuning and reporting never share a slice again.

---

## D-027b · Citation convention: one marker per claim, one entry per source

**Status:** decided · 2026-09-09

**Decision.** Every factual sentence carries the `[n]` of the source it leans on, so a number repeats when several claims come from one source; the source list shows each source once (deduplicated by URL and anchor), with the checked quotes under it, and each citation links to the exact sentence through a text fragment (D-036). Two sources on one page with different anchors stay separate, since they are two deep links.

**Facts.** Per-claim numbered markers over a deduplicated source list is the convention of Perplexity and of ChatGPT search, and the reason reviewers rate Perplexity's answers easier to audit claim by claim. Vidtheque found that many lines under one link made the model cite the wrong moment and moved to one link per line (D-029). The test the convention has to pass: point at a sentence, click once, land on the paragraph. The verifier makes each marker a checked quote, so the marker is evidence rather than decoration; a marker naming nothing is stripped.
