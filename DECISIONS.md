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

**Facts.** A reader must be able to run the project from the README in minutes; cloning and parsing the docs repo at first run adds a network dependency and a failure surface. The docs repo is Apache-2.0, which permits redistribution with notice.

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

**Facts.** The numbers are the argument; a number that cannot be traced back to raw model output cannot be defended. Runs cost real credits and GLM calls, and re-running to recover lost detail wastes both. Estimated size: a 600-judgement run is a few MB, acceptable in git.

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

**Decision.** `eval/mined.jsonl` is the second reporting set beside the generated dev set: never used for tuning, run with every answer evaluation from now on, and the set the reported numbers lead with, since these are the questions users actually had. Tom validates the rows from `.local/runs/t4/mined-validation.md` before the numbers are quoted.

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

---

## D-021a · The judge is blinded, and three judges agree enough to trust one

**Status:** decided · 2026-09-09 · re-judged runs `dev60-baseline`, `dev60-anchors`, `dev60-rerank`, `devfr-shipped`, `devfr-translated` (492 answers, 1,476 judgements)

**Facts.**
- Judge prompt `answer-judge/v2` shows the question, the reference answer, the answer with its markers, and each verified citation's quote and passage; no gold URL and no citation URL. Every run keeps its v1 judgement under `judges_v1`, so nothing was overwritten.
- Blinding moved the primary judge's correctness by at most 0.017 on the English runs and by 0.042 on the untranslated French run; citation relevance moved both ways (down 0.03 on the baseline, up 0.036 on the anchors run). The 0.89 to 0.98 rise that D-033a attributed to a possible URL-matching effect does not survive as such: the blinded judge still scores those two runs 0.864 and 0.985, and the answers themselves differ between them, so the rise is in the answers.
- Agreement over 492 answers: GLM 5.3 against GLM 5.3 Flash, quadratic-weighted kappa 0.869 and exact agreement 0.907; either GLM against Ministral 14B, kappa about 0.51. Krippendorff's ordinal alpha over the three is 0.617; on the reranked run it is 0.417 despite 0.825 exact agreement, because almost every answer there is labelled correct and chance agreement is high.
- Ministral 14B is the outlier: sole dissenter against the two GLM judges on 77 answers (GLM 5.3 on 19, Flash on 24), more lenient on API-reference and cross-page answers, stricter on capability and unanswerable ones, and in one audited case it marked an answer correct while stating that the reference treats the question as unanswerable, which the reference does not. The two GLM judges are one model family, so their agreement is not independent evidence.
- Human labels were not yet available; the reader, matching and confusion-matrix code are tested on a fixture.

**Decision.** GLM 5.3 stays the primary judge for published tables, GLM 5.3 Flash the second (kappa 0.87, faster), Ministral 14B the independent dissent check that is reported but never the primary. Every table now carries all three judges' means. Tom's labels from the annotation page decide whether Flash can become the primary and give the judge-versus-human number this record still lacks.

**D-038a · First numbers on the mined set** (run `*-mined-shipped`, 85 questions, shipped configuration, Ministral 14B, primary judge before blinding; 7 answers lost to free-tier 429s while other evaluations ran, to be re-run):

| metric | single_pass | search_loop | single_pass on the generated dev slice |
|---|---|---|---|
| correctness (judge) | 0.79 | 0.85 | 0.93 |
| judged partial | 0.23 | 0.24 | 0.05 |
| cited URL matches gold | 0.86 | 0.78 | 0.82 |
| refusal correct | 0.92 | 0.93 | 0.92 |
| fabricated quotes per answer | 0.59 | 0.82 | 0.40 |
| correctness on the 9 mined unanswerables | 0.67 | 0.69 | (0.9 on generated ones) |
| latency p50 | 12.0 s | 36.8 s | 7.2 s |

Real questions are found as well as generated ones (URL match 0.86) but answered less precisely: a quarter of the answers are partial, because these questions ask for one exact parameter, format or limit and the answer stops short of it or adds an unsupported detail. The mined unanswerables are the hardest cell, as D-038 predicted: relevant context exists and the model over-reaches from it. The search loop buys 6 points here at three times the latency. These are the headline numbers, and the ones the next product changes are measured against.

---

## D-035b · Badly worded questions: the loop's lead doubles, the default stands

**Status:** decided · 2026-09-09 · `eval/dev-noisy.jsonl` (105 degraded versions of a 120-question dev subset, five noise kinds: typos, keywords, vague, wrong term, chatty; run `2026-09-09-1222-dev-noisy`) and six paired runs, shipped retrieval, Ministral 14B, blind GLM judge

| strategy | clean correctness | noisy correctness | clean URL match | noisy URL match | noisy p50 | noisy prompt tokens |
|---|---|---|---|---|---|---|
| single pass | 0.87 | 0.68 | 0.81 | 0.68 | 11.2 s | 2.3k |
| single pass with query rewrite | 0.83 | 0.72 | 0.78 | 0.68 | 11.8 s | 2.2k |
| search loop | 0.90 | 0.74 | 0.82 | 0.74 | 36.4 s | 16.8k |

**Facts.**
- Noise costs the single pass 19 points of correctness and the loop 16; the loop's lead over the single pass doubles from 3 points to 6, which is the reformulation advantage D-035 could not see on questions written from the page that answers them.
- The damage is concentrated: vague wording (single pass 0.90 to 0.52) and a wrong product term (0.83 to 0.47) do the harm; typos cost 13 points, keyword-only 4, a chatty preamble 6. It is retrieval, not generation: on vague questions cited-URL match falls from 0.85 to 0.40 while quote verification stays at 0.95.
- Badly worded questions break refusal in the false-refusal direction first: 19 of 88 answerable noisy questions were refused (10 of 100 clean), against 6 of 17 unanswerable ones wrongly answered (4 of 20 clean).
- One query-rewrite call (275 prompt and 25 completion tokens, 0.66 s, 0.0006 USD at Medium prices) recovers about a fifth of the loss overall, is clearly positive on typos, vague and wrong-term questions, and clearly negative on keyword-only queries and on clean questions (minus 5 points), because a question already in the documentation's words can only lose specificity.
- The loop is not uniformly better under noise: it loses typos and keyword-only questions to the plain single pass, because its own reformulations wander.

**Decisions.** The default stays single pass: six points on badly worded questions do not pay for 3.3 times the latency and 4.6 times the cost, and the loop is the documented thorough mode. `rewrite_for_retrieval` stays off by default and available per request; the follow-up the split points at is rewriting only when the first retrieval comes back weak (a low top score or no lexical footing), which would take the gains on vague and wrong-term questions without the loss on clean ones. Refusal is now reported on noisy questions as well, since the generated set understates false refusals.

---

## D-039 · What the product is for: agents without a filesystem, and questions the source cannot answer

**Status:** decided · 2026-09-09 · product direction round; research memo on the documentation-server field (codex web research, 25 searches, sources dated 2026-09-09)

**Facts.**
- A coding agent with the SDK checked out can grep it. That covers questions about how a parameter is spelled; it does not cover rate limits, prices, deprecation dates, the capability matrix, regional availability, or what changed last month. Of the 85 real questions in `eval/mined.jsonl` (D-038), 54 came from GitHub issues opened by people who had the SDK and still failed.
- Agents inside Mistral Work, Le Chat, scheduled tasks and chat bots have no filesystem and no grep. Work reaches external knowledge only through Connectors, Libraries, Skills and custom instructions (`vibe/work/*` pages in the corpus).
- The field, checked 2026-09-09: Context7, Mintlify hosted MCP, GitMCP, llms.txt, the GitHub MCP server, DeepWiki, and the Cloudflare, Stripe, Vercel and Supabase documentation servers all return passages for the calling agent to interpret (DeepWiki also generates an answer); citations stop at the page for all of them; only Context7 and Mintlify pin a version; none publishes a retrieval or answer evaluation; none documents quote verification or text-fragment links. Mistral's own `llms.txt` still lists 75 legacy `/docs/*.md` paths that return 404, and Mistral's official MCP server exposes Studio Skills, not documentation search.
- The one published study close to "grep versus docs server" (510 sessions, 9 August 2026, menges.dev) found agents never called a merely available code-context server and did as well with repository tools on grep-shaped questions; it recommends comparing whole agents, verifying the tool was actually called, repeating trials, and reporting cost per successful task.

**Decision.** The product is grounded documentation for agents that cannot grep and for product questions the source does not contain, with the evaluation pipeline as a second deliverable: run on every documentation version, it is a documentation-quality tool (D-041). The differentiators the README claims are the ones the field lacks: a commit-pinned corpus, tested section anchors, verified quotes with text-fragment links, a refusal path, and a published evaluation. Exact-symbol questions are conceded to grep. The consumer evaluation (D-040) follows the study's recommendations: shell tools available in every arm, tool calls verified, cost per correct answer reported.

---

## D-040 · Tools for agents that can call tools: `cite` verifies, `ask` stays as the measured fallback

**Status:** decided · 2026-09-09 · supersedes the reading of `ask` as "context injection as a tool"

**Facts.**
- Context was injected into the prompt because models could not call tools. A consumer model that can call `search`, `open`, `read` and `grep` (D-029) can gather the same context itself, so an `ask` tool that runs a second model inside the server costs a nested generation and adds nothing a capable consumer could not do.
- What the consumer cannot do is verify its own citations: checking that a quoted span exists in the chunk it names needs both texts, which only the server has. The verifier (D-027) already does this for the server's own answers.
- Mistral Work decides on its own when to call a Connector; custom instructions "don't change how tools execute", Skills take precedence over custom instructions when active, and activation is the model's decision (`vibe/work/custom-instructions`, `vibe/work/skills`). There is no hook that forces a tool call per message.
- Consumers without a model of their own (a support widget, a batch script, a Slack bot) need an endpoint that returns a finished, cited answer; that is what the assignment text describes and what `/ask` is.

**Decision.** The MCP surface gains a `cite` tool: the consumer sends its draft answer and the quotes it relied on; the server verifies each quote against the chunks it served, returns a fragment link for each quote that holds and a reason for each that does not, and never rewrites the answer. `ask` stays, for consumers without a model and as the path whose quality is measured (0.93 tuned, 0.84 fresh, 0.79 mined). A blind consumer evaluation with weak models at low reasoning (D-032) runs three arms per consumer, no tools, retrieval tools plus `cite`, and `ask`, and reports correctness, citation precision, whether the tool was called, and cost per correct answer; the README recommends whichever arm wins for capable consumers and keeps `ask` for the others. In Work the documented mechanism is a workspace Skill that triggers on Mistral product questions and instructs the model to search first, cite through `cite`, and never answer from memory.

---

## D-041 · The time axis: the pipeline is a function of a commit, so it runs on every commit

**Status:** decided · 2026-09-09 · snapshot evaluation and history tool; the docs repository history was fetched in full on 2026-09-09 (1,294 commits since 2023-12-22)

**Facts.**
- The corpus adapter (D-002) turns one commit of `mistralai/platform-docs-public` into the corpus, and the evaluation runs in minutes, so both can run at any commit. A pipeline tuned on one commit and never run on another has no evidence that it survives the next docs release; the assignment leaves "the level of depth" to the candidate and asks for retrieval evaluation, so depth on evaluation over time is in scope.
- The repository has had three layouts: Docusaurus `docs/` until 20 October 2025 (27 to 87 Markdown files), a Next.js `src/app` tree until 28 May 2026 (267 to 373), and the current `src/content/<locale>/docs` tree since (1,256 to 1,419 files including French). The adapter reads the current layout only.
- Between two snapshots a fortnight apart most chunks are unchanged, so embeddings cached by content hash make a new snapshot cost a fraction of a full ingestion (a full sec1024 ingestion is about 1,033 chunks).
- Whether a question was answerable at an older snapshot must be decided on content, not on the page: sections move. The verifier's whitespace-normalized span search over the whole snapshot decides "present" (same page or moved) deterministically; a span found nowhere goes to a judged step (reference answer against the top five lexically retrieved pages of the snapshot: same fact, different value, or not stated), with a second judge and a human sample, and the tables report the two kinds of cells separately.

**Decision.** Eight biweekly snapshots from 1 June 2026 to the pinned commit, on the current layout, ingested into one schema with a `snapshot` field and the shipped weights; correctness is reported on present cells only, refusal rate on absent cells, and answers that change between snapshots are reported as the changelog in question form. A `history` tool exposes the stored snapshots without any model inside it: first and last appearance of a phrase, the state of a section at each date with the diff when it changed, and for a question the top retrieved section per date. A scheduled refresh workflow (weekly: pull, re-vendor, ingest changed pages, run the fixed question set, publish the diff) is committed with a manual trigger only, so it spends nothing until enabled. Adapters for the two older layouts, and the product graph built on the snapshots, are recorded as later work.

---

## D-035c · Loop caps are evaluated on a local Ministral 3 endpoint, as relative numbers

**Status:** decided · 2026-09-09

**Facts.**
- The search loop stops after 4 rounds with 4 searches per round and shows the model 600-character previews of search results (1,600 for `open`); none of the three values was ever varied. The final generation reads the full chunks of everything the loop collected, so a preview never truncates the answer's context; the risk is that the loop discards, or never reads, a chunk whose relevant sentence sat past the preview.
- The Mistral credits stand at 7.04 of 10 EUR used on 2026-09-09 (console), the promised 20 USD are not yet credited, and every answer evaluation spends Ministral calls; the eval records store a cost of 0 for every call although token counts are recorded (18.8 million Ministral tokens across 5,515 recorded calls, about 2.8 USD at the published Ministral 3 rate), which is a recording bug to fix.
- Tom hosts Ministral 3 on his own GPU (llama.cpp, tool-calling template); the SDK client accepts a `server_url`, so chat calls can go there while embeddings stay on the API, which llama.cpp does not serve.

**Decision.** Chat clients (answer model, reranker, translation) read an optional server URL from the environment; the grid over rounds (4, 6, 8), searches per round (4, 6) and preview size (600, 1,500, full) runs there on 60 questions, one axis at a time from the shipped point, with the GLM judge. Its numbers are relative comparisons between configurations on a quantized local model; every shipped figure keeps coming from the API. No further Mistral credits are spent before the promised credits arrive, except about 0.2 EUR of embeddings for the snapshots (D-041). Cost recording is fixed so every call carries its price, and the recorded totals are reconciled against the console.

---

## D-036a · Fragment links must survive code identifiers

**Status:** decided · 2026-09-09 · found while showing a demo answer from run `2026-09-09-1253-mined-shipped`

**Facts.** The fragment text is built from the quote with every `*`, `_` and backtick removed, so a quoted code block reading `function_name` and `tool_call_id` becomes `functionname` and `toolcallid` in the link; the rendered page keeps the underscores, so the browser finds no match and falls back to the section anchor. The verifier's second pass strips the same characters, which is why the quote still verified.

**Decision.** Strip emphasis markers only where they act as Markdown emphasis (at token boundaries), never inside a word, and build the fragment from the matched span of the source text rather than from the model's rendering of it. A resolvability check fetches the live page for a sample of verified citations, extracts its text, and reports the share of fragments whose text is found; that share is published with the citation metrics, and if it stays low after the fix the feature is removed rather than shipped half working.

---

## D-036b · Fragment links resolve on the live pages for five citations in six; cost is recorded again

**Status:** decided · 2026-09-09 · `glossator.eval.fragments` (resolvability check, 60-citation samples, seed 0, cached page fetches committed under each run directory); `answer_eval recost` on 15 answer runs

| run | links | found in sample | tab-panel exclusions | found among citations the HTML can contain |
|---|---|---|---|---|
| mined-shipped | before the fix | 33 of 60 | 5 | 0.60 |
| mined-shipped | source-span links | 50 of 60 | 2 | 0.86 |
| fresh60-shipped | source-span links | 49 of 60 | 2 | 0.85 |

**Facts.**
- The fix of D-036a (emphasis markers removed only at token boundaries, the fragment built from the matched span of the source text) changed 166 of 564 verified links on the mined run and lifted resolvability from 0.60 to 0.86; the fresh slice, which predates D-036 and had no links, lands at 0.85.
- The remaining misses are documented one by one in `fragments/results.jsonl`: quotes from non-default tab panels (absent from the HTML, D-003), Markdown table delimiters, link syntax and heading markers that do not appear in rendered text, text present only in the page's data scripts, and a few live pages that have moved on from the pinned commit. The check treats none of those as visible page text, so the number is a floor for what a browser highlights.
- A model quote that drops the underscores of an identifier no longer passes the emphasis-only verification pass, which is the intended tightening.
- Repricing: the eval had priced the 14B at zero from the night it had no published price (D-017). With the published Ministral 3 rate, the 15 answer runs cost 1.74 USD (3,539 answer calls, 11.6 million tokens); every priced chat call in every recorded run, reranker calls of the retrieval grid included, sums to 2.81 USD. The console shows 7.04 EUR; the difference is embeddings (three full ingestions, one re-ingestion after D-025b, every query embedding) and calls without a token row, so the recorded spend is a lower bound and the README says so.

**Decision.** Text fragments ship. The resolvability check is part of the evaluation set, reported with the citation metrics, and re-run whenever the verifier or the fragment builder changes. Recorded cost uses the published price table for every model in it; the reference column at Medium 3.5 prices stays for comparability across runs.

---

## D-041a · Eight snapshots indexed; the labels expose a site-wide rename in August

**Status:** decided · 2026-09-09 · `eval/snapshots/manifest.json` (8 snapshots, biweekly from 2026-06-01 plus the pinned commit), schema `docs_snapshot_fulldim` (migration 002, variant `snap1024`), run `2026-09-09-1929-snapshot-labels` (145 questions: fresh 60 and mined 85, times 8 dates, 1,160 cells)

| snapshot | pages | chunks | present, same page | present, moved | pending the judged step |
|---|---|---|---|---|---|
| 2026-06-01 | 327 | 3,387 | 44 | 64 | 37 |
| 2026-06-15 | 332 | 3,485 | 46 | 66 | 33 |
| 2026-07-01 | 368 | 4,058 | 54 | 65 | 26 |
| 2026-07-15 | 378 | 4,192 | 54 | 67 | 24 |
| 2026-08-01 | 392 | 4,281 | 54 | 67 | 24 |
| 2026-08-15 | 401 | 4,311 | 103 | 23 | 19 |
| 2026-09-01 | 408 | 4,389 | 125 | 5 | 15 |
| 2026-09-07 (pinned) | 411 | 4,440 | 135 | 0 | 10 |

**Facts.**
- One schema holds every date (32,543 chunks) behind a `snapshot` filter on the query-builder path; the three existing schemas were untouched (4,440 / 4,489 / 1,034 documents before and after). The snapshot for the pinned commit reproduces the shipped index chunk for chunk. Embeddings were cached by content hash, so the eight ingestions cost a fraction of eight full runs.
- The first version of the deterministic label called a span "moved" when it was found on a page other than the gold page; that was wrong, because the spans are the answers' own verified quotes, which may legitimately sit on a non-gold page. The rule now compares with the page the quote was cited from at the pinned commit, and 84% of cells are decided without a model.
- The moved cells are real: 300 of 357 are the same section under `/studio-api/...` before and `/studio/...` after. The documentation renamed its API section between 1 and 15 August 2026, a second wave landed before 1 September, and nothing has moved since. Every method that keys on URLs, including our own gold links and the redirect table (D-002), lives through this once per rename; the span search does not notice it.
- Pending cells fall from 37 to 10 from June to September: facts that appeared, or were reworded, over the summer; the judged step (two GLM judges, a human sample) will split those into rephrased, changed and absent. Ten cells are pending at the pinned commit itself, which is the fallback whole-page span failing on anchor-less gold pages, not a missing fact.

**Decision.** The snapshot index and the labels ship. The answer evaluation across the eight dates runs on the local server with reasoning off (D-035c) and is judged after the quota window resets; correctness is read on present cells only, refusal on absent ones. The August rename is the first entry of the changelog the time axis produces, and the history tool's `section` form is what shows it.

---

## D-040a · `cite` shipped; the first blind consumer used it

**Status:** decided · 2026-09-09 · `src/glossator/answer/cite.py`, `POST /cite`, MCP tool `cite`, `GLOSSATOR_MCP_TOOLS` allowlist, `GLOSSATOR_MCP_TOKEN`, `GET /health` on the MCP transport, `skills/mistral-docs/`; run `2026-09-09-1905-consumer-eval` (partial)

**Facts.**
- `cite` verifies a consumer's quotes against the chunks the server served (or a page's merged chunks when a URL is given), returns fragment links for the ones that hold and a reason for the ones that do not, lists the draft's markers that name nothing, and deduplicates sources by URL and anchor (D-027b). It never rewrites the draft and never calls a model. Nineteen fixture tests cover the cases, including a quote across a chunk boundary.
- The first blind consumer, a small model (muse spark 1.3 at its lowest reasoning) driven headless with no knowledge of being evaluated, ran 59 cells with no tools and 28 with the retrieval tools plus `cite` before its free tier rate-limited the run. With the tools available it called the server on 28 of 28 questions and `cite` on 27, five tool calls per question at the median (four searches, one open, one cite is the typical shape), in 26 s against 12 s without tools. Without tools it still produced links on 58 of 59 answers, from memory and shell tools; whether those links resolve and whether the answers are right is what the judged pass measures.
- The mechanism for Work is documented in the exact words of the Connector page: a custom MCP Connector with auto-detected bearer authentication, a workspace Skill that triggers on Mistral product questions and prescribes search, read, draft, `cite`, source list.

**Decision.** The tool set is search, open, navigate, read, grep, cite, ask, history, behind an allowlist so one deployment can expose one arm of the consumer evaluation. The remaining arms (`ask` only; the codex, GLM and sonnet consumers) and the judge run when the quota windows reopen, and the README's recommendation waits for those numbers.

---

## D-023b · Reranker calls made during answer evaluations were not in the call ledger

**Status:** decided · 2026-09-09

**Facts.** The answer evaluation built its search engine without a recorder, so every listwise reranker call it made (one per single-pass question, one per loop round) was neither in `calls.jsonl` nor in the record's trace; only the retrieval grid recorded its reranker calls. That is why the recorded spend (2.81 USD across every recorded chat call, D-036b) sits well under the console's 7.04 EUR: roughly one reranker call of about five thousand tokens per generation call went unrecorded, on top of embeddings. The answers themselves were unaffected.

**Decision.** The answer evaluation and the snapshot evaluation now share one recorder between the engine and the answer model, so reranker calls land in `calls.jsonl` beside generation calls. The evaluations already recorded keep their generation-only ledgers, stated as such; the console figure remains the number of record for spend, and the README says the recorded totals are a lower bound for runs before this date.

---

## D-021b · Forty human labels: the judges are stricter than the reader, so judged correctness is a floor

**Status:** decided · 2026-09-09 · 40 answers from `2026-09-09-0312-dev60-rerank` (36 questions; 20 single pass, 20 search loop) labelled by hand on the annotation page, compared with the three blinded judges already stored in the run (judge prompt v2)

| judge | agrees with the human | weighted kappa | judge said partial or wrong where the human said correct | judge said correct where the human did not |
|---|---|---|---|---|
| GLM 5.3 (primary) | 35 of 40 | 0.46 | 3 | 0 |
| GLM 5.3 flash | 35 of 40 | 0.22 | 2 | 1 |
| Ministral 3 14B | 32 of 40 | 0.45 | 6 | 0 |

**Facts.**
- The human labelled 38 correct, 1 partial, 1 wrong. With that little disagreement mass the kappas are unstable (two off-diagonal labels decide them) and the raw agreement is the readable number: the primary judge matches the reader on 35 of 40 and never calls an answer correct that the reader rejected. Every primary-judge disagreement is in the strict direction, so the correctness figures in this file understate what a reader accepts.
- Ministral 14B is the strict outlier again (six "partial" on answers the reader accepted), consistent with D-021a.
- The reader's notes carry product feedback the judges cannot give: answers that produce code or pseudo-code for a simple factual question ("this tendency ... is frustrating"); examples added where none were asked for; a list whose items come from different sources should carry one marker per item, or one marker for the whole list when it comes from one source; one reference answer judged wrong by the reader while the answer under test was right (dev-188), which is a generated-reference defect, not a pipeline defect.
- On the one answer the reader called wrong (dev-052, search loop) the primary judge said partial and flash said correct; on the reader's partial (dev-052, single pass) all three judges said wrong. The two strategies disagree on that question in both directions, which is the kind of item the consumer evaluation should include.

**Decisions.** GLM 5.3 stays the primary judge, and every correctness number it produces is read as a floor. The answer prompt gains two rules from the notes: answer a factual question in prose and add code only when the question asks how to do something in code; cite each list item that comes from its own source. Both go into the precision-and-refusal stream and are measured before they ship. The reference-answer defect rate is estimated on the same 40 items (1 in 40 here) and reported beside the judge study.

---

## D-037a · Deployment: one image, two modes, a tunnel, and the rules travel in tool descriptions

**Status:** decided · 2026-09-09 · `Dockerfile`, `deploy/compose.yaml`, `deploy/deploy.sh`, `deploy/cloudflared/`, `deploy/README.md`, `make deploy`, `make deploy-check`, `tests/test_deploy.py` (28 tests without a host)

**Facts.**
- The image is a two-stage uv build on Debian slim, non-root, with the corpus vendored, so the only network access at build time is package installation. No secret is baked in; compose refuses to start without `MISTRAL_API_KEY` and `GLOSSATOR_MCP_TOKEN`.
- Two modes. `remote-index` runs only the MCP server (and optionally the API) on the host and points it at an existing Vespa over the network; verified here against the development index: health ok with 4,440 chunks and a passing embedding probe, 401 without the bearer token and 200 with it, a real `search` over the HTTP transport. `full` adds Vespa, the migrations and an ingestion that reads the embedding cache synced from the operator's machine; the cache now wraps the embedder for every variant, so a full deploy re-embeds nothing that was embedded before and spends no credits. Ingestion refuses to run above 80% disk with the feed-block message (D-025b).
- The public path is a named Cloudflare tunnel with a DNS route to `glossator.tomvaucourt.com`; the free random hostnames change on every restart, which a Connector registration cannot follow. The manual steps (login, create, route, credentials, unit) are listed in order in `deploy/README.md`.
- The Work documentation states that custom MCP Connectors "don't yet support" dynamic tool discovery, resources, or prompt templates (`vibe/work/connectors/mcp-connectors`, "Current limitations"). The `glossator://guide` resource therefore never reaches Work; the shared rules must live in the tool descriptions (they do: USE WHEN, DO NOT USE, START WITH on every tool) and in the workspace Skill (D-040a).

**Decision.** Deploy with `make deploy HOST=<ssh host> MODE=remote-index` first so the Connector can be tried tonight, then `MODE=full` with the Vespa data volume copied from this machine once the local evaluation runs finish, which moves all four schemas including the eight snapshots without one embedding call. The bearer token is compared in constant time, and lifespan is the only non-HTTP scope that bypasses it.

---

## D-035d · The reranker follows the generation client to the local server

**Status:** decided · 2026-09-09 · supersedes the routing in commit 11df2d7

**Facts.** Two changes landed in one evening with opposite rules: one kept the reranker on the Mistral API when generation went local, so "shipped reranking never depends on which server answers are generated on"; the other routed every chat call, reranker included, through one client factory that reads `GLOSSATOR_CHAT_SERVER_URL`. The merge kept the factory. The credit constraint decides it: a local run of 480 snapshot questions with the reranker on the API would spend about 2.4 million Ministral tokens, and the point of the local server is that these runs spend nothing.

**Decision.** Every chat call, reranker included, goes where the factory points, and every run records the server and the reasoning setting in its config, README and call ledger, so a local run can never pass for an API run (D-035c). Shipped numbers keep coming from runs with the variable unset.

---

## D-023c · Consumer transcripts belong in the run directory

**Status:** decided · 2026-09-09

**Facts.** The consumer evaluation (D-040a) writes the harness event streams of every consumer conversation under a scratch directory outside the repository, and only the extracted answer, tool calls and links into the run's records. About one hundred conversations so far take 5.7 MB. A reviewer of the run cannot open the conversation behind a row. The review pass also found that `--rejudge` could not change a verdict because the provider replayed its disk cache without a nonce, that the consumer runner had no `--retry-errors`, and that the run directory lacked its README, metrics, figures and call ledger; those three are fixed.

**Decision.** Consumer runs copy each conversation's event stream into `<run>/transcripts/<consumer>/<arm>/<question_id>.jsonl` at collection time, so the run directory is complete on its own (D-023). The scratch directory stays the consumer's working directory and nothing else.

---

## D-042 · When an answer fails, it is the generator, not retrieval

**Status:** decided · 2026-09-09 · `glossator.eval.failures` (`make failures`), run `2026-09-09-2028-failure-analysis` over five answer runs (575 answers), rules stated in its README, 38 tests

| run | answers | failed | retrieval miss | context miss | generation failure | refusal failure |
|---|---|---|---|---|---|---|
| mined-shipped | 170 | 52 (0.31) | 1 | 0 | 39 | 12 |
| fresh60-shipped | 60 | 17 (0.28) | 2 | 0 | 7 | 8 |
| dev60-rerank | 120 | 21 (0.18) | 1 | 0 | 8 | 12 |
| clean-single | 120 | 30 (0.25) | 3 | 0 | 11 | 16 |
| noisy-single | 105 | 44 (0.42) | 13 | 0 | 12 | 19 |
| all | 575 | 164 (0.29) | 20 | 0 | 77 | 67 |

**Facts.**
- Classes are decided in order from the records alone: no gold page among the retrieved chunks (retrieval miss); a gold chunk retrieved but dropped from the context (context miss); the gold section in the context and the answer still partial or wrong (generation failure, sub-labelled by what the citations say); a refusal with the gold section in context or an answer to an unanswerable question (refusal failure). Chunk ids resolve to pages offline by re-chunking the vendored corpus (6,397 of 6,397 ids resolved).
- Generation is the largest class, 47% of failures, and 53 of the 77 had a verified quote from the gold section in the answer: the model read the right passage and still answered short or wrong, most often one parameter or limit short of the reference on the mined set. This is the column a stronger generation model moves (D-017a), and the clearest evidence that the ceiling is the 14B model, not the pipeline.
- Retrieval misses are 1 to 3% of answers on well-formed questions and 12% on badly worded ones (D-035b); context misses are zero in every run, so the context budget is not a lever.
- Refusal failures split 35 false refusals and 32 missed refusals. The failure tool suggested trusting a verified citation over the model's insufficient-evidence flag; the recorded runs say no: the correct answers that were refused carried no verified quote at all (their refusal came from the "no verified citation" rule, not from the flag), while 43 correctly refused unanswerable questions do carry a verified quote and would flip to wrong answers under that change. The lever on false refusals is quoting, not the flag.
- The reference-defect flag's first signal does not discriminate (the judge names the reference on 91% of passing answers too, because the prompt tells it to grade against the reference); the human-lenient signal (D-021b) marks 4 rows. The judged check is implemented and not yet run.
- The pre-reranker candidate list is unrecoverable for these runs (D-023b); from now on the tool separates a reranker drop from a search miss.

**Decision.** The refusal rule stays as it is. The next product work is on the generator's side: the two prompt rules from D-021b, a "state the exact value or limit before explaining" instruction for the partial-answer shape, and a re-run on Medium or Small once the account allows it; retrieval work is limited to badly worded questions (conditional rewrite, D-035b). The failure table is reported with every answer evaluation from now on.

---

## D-029a · The public surface is rewritten for agents that decide on their own: names, budgets, concise results

**Status:** decided · 2026-09-10 · `docs/context-surface-audit.md` (sources: Anthropic, "Writing tools for agents"; the MCP specification 2025-06-18 on tools and server instructions; Mistral, `vibe/work/connectors/mcp-connectors`, "Current limitations"), two real sessions with the deployed server (Claude Sonnet in Claude Code, Mistral Work), commits 37d5828, 55fe570, dbf0d9d, 1f7c32c

**Facts.**
- In the Claude Code session the model answered a Mistral question from memory and only searched when told "use glossator": the tools appeared as `glossator-public: search`, nothing in the name said Mistral. In the Work session the connector was called unprompted, and Work rendered every tool result verbatim in its UI: index variant, "hybrid bm25+vector", scores, byte offsets, chunk ids, a paste-ready follow-up query.
- Measured on the old surface: a five-hit search cost 1,687 tokens of which 34% was documentation text; the score was the rank restated ((total minus position) divided by total) and `navigate` printed 0.000 for every hit; `read` returned 10,516 tokens for one page and a blind consumer received 36,612 characters in one call; the permanent context was 103 tokens of instructions plus 1,379 of descriptions, and Mistral's own known-limitations page says tool descriptions are billed against the message context.
- Work cannot read MCP resources, prompts or dynamic tool lists, so the `glossator://guide` resource never reaches it; the instructions string and the tool descriptions are the only server-side channel, the workspace Skill the only client-side one.
- Anthropic's guidance: namespace tools by service, write descriptions for a new hire (purpose first, when to use and when not), return what the agent acts on in natural language with a concise default and a detailed option, prefer meaningful identifiers over technical ones.

**Decision.** Server name `mistral-docs`, title "Mistral documentation search". Tools `mistral_docs_search`, `mistral_docs_open_section`, `mistral_docs_step`, `mistral_docs_read_page`, `mistral_docs_find_on_page`, `mistral_docs_answer`, `mistral_docs_verify_quotes`, `mistral_docs_history`, each description under 120 words with a first line naming what it reads in Mistral's documentation; parameters in plain words (`page_url`, `max_hits`, `max_chunks`, `max_matches`, `steps`). The instructions carry the corpus scope, the never-fabricate rule, the refusal rule and the `next:` convention in 240 tokens. Results are concise by default (URL with anchor, heading path, snippet, chunk id; one truncation note) and `response_format="detailed"` restores scores, offsets and full text for an engineer; a five-hit search now costs 1,098 tokens. `read_page` defaults to eight chunks under a 16,000-character budget, `history` renders under 12,000. Every `DO NOT USE` clause and `next:` hint goes through the registration check, so an allowlisted deployment never names a tool it did not register (the old short names in `GLOSSATOR_MCP_TOOLS` still work, with a warning). Permanent context rose to 240 plus 1,673 tokens for the seven deployed tools, which one search call repays. The `glossator` name stays on the repository.

---

## D-037b · A host may send arguments the schema does not declare; read-only tools say so

**Status:** decided · 2026-09-10 · Mistral Work session of 2026-09-09 23:39; commits 37d5828, 1f7c32c

**Facts.** On the attempt that asks the user to approve a call, Work adds an argument `_confirmationReason` (a sentence saying why it wants to run the tool). Six calls in one two-question session failed with "Unexpected keyword argument" and succeeded only on the retry after "Allowed". The blind consumer harness had recorded zero tool errors over 160 calls, because it sends exactly what the schema declares. Nothing in the Work documentation mentions the argument. The MCP specification defines tool annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`) that a host may use to decide whether a call needs confirmation.

**Decision.** Arguments whose name starts with an underscore are host metadata: the parameter guard drops them before validation and announces it (`note: ignored host argument _confirmationReason`). Every tool is annotated read-only, non-destructive, idempotent and closed-world, so a host that reads the hints has no reason to ask for confirmation. The consumer evaluation gains a host-fidelity arm that sends the extra argument and counts tool errors, since a well-behaved harness cannot see this class of defect.

---

## D-015b · No reranker inside an agent's loop; the reranker stays in `answer`

**Status:** decided · 2026-09-10 · audit measurements from the recorded call ledgers; supersedes the search default of D-015 for the MCP surface only

**Facts.** Every search on the old surface ran one listwise reranker call: 4,111 prompt tokens, 5.2 s, about 0.0007 USD, which is 91% of a search's latency and all of its marginal cost, whatever `max_hits` is. The reranker buys +0.115 page recall@1 and +0.141 section recall@1 (D-035) but only +0.057 and +0.042 at depth 5, and an agent that iterates reads several hits and searches again rather than trusting the first one. In the Work session the model ran one search and five opens on its own.

**Decision.** `mistral_docs_search` takes `rerank`, default false, and says what true costs; `mistral_docs_answer` keeps the reranker because a single decisive retrieval is what it does. The consumer evaluation measures the arm with tools with rerank off against rerank on, on correctness, citation quality, seconds and cost per correct answer.

---

## D-027c · Markers stay; every source list is a Markdown block with the section and the quote

**Status:** decided · 2026-09-10 · `docs/context-surface-audit.md` section on citations; commit 55fe570

**Facts.** The owner found misplaced `[n]` markers sloppy and asked for a "Sources" block with a description and a link, as web-search answers render. In Work, Markdown links are clickable and a bare `[1]` is not. The old `cite` output repeated each fragment URL twice (40% of its payload) and its entries carried no description. Three shapes were compared: markers plus a list, inline Markdown links per claim, a sources-only block. Inline fragment links are about 170 percent-encoded characters that a weak consumer has to reproduce inside prose, and one wrong character breaks the link silently; a sources-only block loses the claim-to-quote pairing that makes a citation checkable (D-027b). A sibling project's rule, "give the user the link, not just the timestamp, one link per cited line", is the same idea with a short link.

**Decision.** Per-claim `[n]` markers stay in the prose. Every source list, from `mistral_docs_answer` and from `mistral_docs_verify_quotes`, is a Markdown "Sources" block, one line per distinct (url, anchor): `[1][3] [Heading path](fragment link) — "quoted sentence"`. `verify_quotes` prints failures in full with a remedy and successes as one count line. The API returns the same block as `sources_markdown` beside the structured citations. Dropping the markers is a rendering switch, kept available if use in Work says otherwise.

---

## D-037c · Without read-only annotations, a headless codex consumer never calls the server

**Status:** decided · 2026-09-10 · recorded twice against a stand-in stdio server replaying this server's outputs, codex `exec` with the default approval policy

**Facts.** With no tool annotations every MCP call from a headless codex session fails with "MCP tool call requires approval, but approval policy is never" and the model falls back to its own web search; with `readOnlyHint`, `destructiveHint`, `idempotentHint` and `openWorldHint` set as the server sets them, the same prompt runs `mistral_docs_search` and `mistral_docs_verify_quotes` and cites the fragment link. No per-server configuration key overrides the policy (`tool_approval`, `approval_mode`, `auto_approve` and `trusted` are all rejected under strict configuration). The consumer harness had also been counting a consumer's own `web_search` and `read` built-ins as calls to this server because the old bare tool names matched them; the namespaced names (D-029a) removed that ambiguity.

**Decision.** The annotations of D-037b are part of the contract, not a courtesy to one host: they are what lets an unattended consumer use the server at all. The consumer evaluation records, per consumer, whether calls were refused by the host's approval policy, and the deploy check lists the annotations beside the tool names.

---

## D-038b · A second mined set: the Vibe CLI is where users stumble now

**Status:** decided · 2026-09-10 · `eval/mined-v2.jsonl` (83 questions, sha256 `1e19ef8f…`), provenance in `eval/mined-v2.README.md`; run `2026-09-09-2305-mined-v2-shipped` (local Ministral 3 14B Reasoning, judged by GLM 5.3)

**Facts.**
- Sources the first pass did not reach: GitHub issues on `mistralai/mistral-vibe` (31 kept of 293 open issues), `client-ts` (20), `mistral-inference` (3), `mistral-finetune` (1); Stack Overflow (9 kept of 26 questions tagged for the platform since 2025; the `mistral-7b` tag is local inference with third-party tooling, outside the corpus); Hacker News (9 kept of 1,629 hits, almost all opinion); ten stumbles from the consumer sessions of 2026-09-09. The five repositories of the first pass had no new issue since 2026-09-08. Eleven candidates dropped, eight as duplicates of the first set by fact and page.
- Types: single_page 55, unanswerable 13, cross_page 11, api_reference 4. Product areas: Vibe 30 (one in the first set), document AI 10, agents 7, structured output 5. Examples: the realtime transcription WebSocket header a browser cannot set, answered by the client-auth page; the Devstral 2 model naming that support answered with screens that do not exist, answered by the model-lifecycle page; the Vibe CLI tool-permission key; an Azure-hosted OCR endpoint rejecting a documented parameter; and two documentation gaps (the web crawler's limits, whether API calls train models) recorded as unanswerable.
- On the shipped configuration, generated on the local reasoning model at the settings its card asks for (temperature 1, top_p 0.95, thinking on, effort low): correctness 0.65 (correct 0.52, partial 0.25, wrong 0.23), refusal correct 0.78, quote verification 0.83, URL match 0.57, anchor match 0.39, p50 29 s. Not comparable with the first mined set, which ran the API's instruct model with no reasoning; unanswerable questions are the strongest slice (0.85), api_reference the weakest (4 questions, 0.25).

**Decision.** `eval/mined-v2.jsonl` joins the reporting sets, to be validated by hand from the private evidence before its numbers are quoted, and re-run on the API model when credits allow so it is comparable with the first set. The Vibe CLI pages are the product area to read first when improving retrieval on real questions.

---

## D-040b · Two blind consumers on the agent-facing surface: the tools double a strong consumer's accuracy, and a consumer with its own web search never picks the server

**Status:** decided · 2026-09-10 · run `consumer-eval-v2` (30 questions: 20 mined, 10 fresh; three arms; Claude Sonnet at low effort, GPT luna at low effort; judge GLM 5.3 blind; transcripts in the run directory, D-023c)

| consumer | arm | correctness | refusal correct | called the server | links that resolve | tool calls | p50 |
|---|---|---|---|---|---|---|---|
| Sonnet | no tools | 0.50 | 0.70 | 0 of 30 | 0.35 | 3.9 (its own) | 22 s |
| Sonnet | retrieval tools plus verify | 0.77 | 0.80 | 30 of 30 | 0.92 | 5.2 | 21 s |
| Sonnet | answer only | 0.78 | 0.80 | 30 of 30 | 0.90 | 2.3 | 74 s |
| GPT luna | no tools | 0.58 | 0.80 | 0 of 30 | 0.86 | 2.0 | 15 s |
| GPT luna | retrieval tools plus verify | 0.52 | 0.80 | 0 of 30 | 0.85 | 2.2 | 14 s |
| GPT luna | answer only | 0.58 | 0.83 | 0 of 30 | 0.81 | 2.2 | 15 s |

**Facts.**
- With the retrieval tools, Sonnet's correctness rises from 0.50 to 0.77 and its links resolve 0.92 of the time instead of 0.35, at the same latency; the answer-only arm reaches the same correctness with fewer calls and three times the latency (the server's own generation on the local reasoning model). Sonnet called `mistral_docs_verify_quotes` on 14 of 30 questions and asked for the reranker on 7.
- GPT luna, which carries a built-in web search, never called the server in 60 cells with it available: every tools-arm transcript shows `site:docs.mistral.ai` web searches and no MCP call. A hand probe with the same configuration and a prompt that names the server shows it can call `mistral_docs_search` and read the result, so this is a choice, not a defect: with nothing in the prompt naming the server, a low-effort consumer with a competing tool keeps its habit. Its web search resolves links well (0.86) and answers at 0.52 to 0.58 across arms.
- The judge is the same blinded GLM 5.3 as everywhere else; the question set is 30 items, so a 95% interval is about ±0.17 per cell and only the large gaps are read.
- The earlier partial run on the old surface with a small consumer (D-040a) and this one are the only two consumer runs; neither had a host-fidelity arm yet.

**Decision.** The recommendation for capable consumers stands: retrieval tools plus `verify_quotes`, the consumer writes the answer. The next arm to run is the up-front instruction: the same consumers with one sentence naming the server (the CLAUDE.md block, the Work Skill), which is the lever D-029a and the improvement axes name for the discoverability failure GPT luna reproduces; the rerank-on comparison and the host-fidelity arm follow. Consumer runs report "called the server" beside correctness from now on, since a consumer that ignores the server scores its own habit.

---

## D-035e · The loop's caps are not a lever

**Status:** decided · 2026-09-10 · summary `2026-09-10-0120-loop-grid` over six run directories; 30 stratified fresh questions per configuration, search loop, generated on the local Ministral 3 14B Reasoning at the model card's settings, judged blind by GLM 5.3

| configuration | correctness | groundedness | rounds | tool calls | hit the round cap |
|---|---|---|---|---|---|
| shipped: 4 rounds, 4 searches per round, 600-char previews | 0.85 | 0.84 | 2.6 | 2.1 | 0.13 |
| 6 rounds | 0.77 | 0.74 | 2.9 | 2.4 | 0.07 |
| 8 rounds | 0.82 | 0.70 | 2.8 | 2.6 | 0.00 |
| 6 searches per round | 0.75 | 0.80 | 2.1 | 1.5 | 0.03 |
| 1,500-char previews | 0.87 | 0.71 | 2.0 | 1.3 | 0.00 |
| full previews | 0.77 | 0.80 | 2.0 | 1.3 | 0.00 |

**Facts.** Thirty questions give a 95% interval of about ±0.13 per cell, and every configuration lands inside the shipped point's interval. Lifting the round cap removes the 13% of questions that hit it without moving correctness; wider previews do not help either, and the reasoning model uses two to three rounds and about two tool calls whatever the cap. These are relative numbers on a local reasoning model, not the API figures (D-035c); the instruct model's partial run was set aside when the model changed.

**Decision.** The caps stay at 4 rounds, 4 searches per round and 600-character previews. The question "what if the answer is past the preview" is answered by the design (the final generation reads the full chunks of everything collected) and by this grid (wider previews change nothing); the loop's remaining cost is its tokens, which is why it is the thorough mode and not the default (D-035b).

---

## D-037d · The history tool is live on the public server; the index travels as a cache, not as a volume

**Status:** decided · 2026-09-10 · container redeployed 03:40, `deploy/compose.yaml` mounts the snapshot corpora into the server

**Facts.** Copying the development Vespa data volume to the container (1.5 GB) failed to start there: the config server's ZooKeeper refused its own copied state ("the current epoch, 1, is older than the last zxid"). Rebuilding from the embedding cache instead took under four minutes for the shipped index plus the eight snapshots (32,543 chunks) with zero embedding calls, because every chunk's embedding was already cached under its content hash. The public server now registers all eight tools, and `mistral_docs_history` answers over the tunnel: the sentence "Email domain authentication is available on Team plans and above", which a Work session quoted last night, first appears in the snapshot of 2026-07-01.

**Decision.** An index is reproduced from the vendored corpus, the manifest and the embedding cache, never moved as a Vespa volume. The deploy script's full mode plus the snapshot ingestion is the documented path, and the cache directory is the one artefact worth backing up beside the repository.

---

## D-021c · A free local judge agrees with the primary judge as well as the second cloud judge does

**Status:** decided · 2026-09-10 · `eval/runs/2026-09-10-0345-dev60-rerank-qwen-judge` (the 120 answers of dev60-rerank re-judged by Qwen 3.8 27B on the local server, reasoning off, judge prompt v2; `agreement-four-judges.json`)

| pair | weighted kappa | agreement |
|---|---|---|
| GLM 5.3 and Qwen 3.8 27B | 0.72 | 0.89 |
| GLM 5.3 and GLM 5.3 flash | 0.62 | 0.90 |
| GLM 5.3 flash and Qwen | 0.61 | 0.85 |
| Ministral 3 14B and Qwen | 0.58 | 0.80 |
| human (40 items) and Qwen | 0.43 | 0.85 |
| human (40 items) and GLM 5.3 | 0.46 | 0.88 |

**Facts.** Qwen judged all 120 answers with no parse failure at about 7 s per call on the local server. Its mean correctness (0.90) sits between the strict Ministral (0.85) and the two GLM judges (0.93 and 0.94). Krippendorff's alpha over the four judges is 0.49, pulled down by Ministral (D-021a).

**Decision.** Qwen on the local server is the judge for local-only nights and a third opinion on any run, at no cost; GLM 5.3 remains the reporting judge so the published tables stay on one scale. The judge study now covers four judges and one human.

---

## D-017b · Medium 3.5 measured by replaying the recorded prompts: the generator is not the ceiling

**Status:** decided · 2026-09-10 · `eval/replay/` (exporter, standard-library runner, importer with a rebuild proof); runs `2026-09-10-1615-medium35-replay-{dev60-rerank,fresh60-shipped,mined-shipped,mined-v2-shipped}`; completions produced by Mistral Medium 3.5 (endpoint name `Mistral-Medium-3.5-128B`) through an OpenAI-compatible gateway Tom has access to at work, 288 requests, zero errors, `json_schema` output accepted; judged blind by GLM 5.3 with GLM 5.3 Flash second

**How.** Every answer evaluation records the generator's request verbatim (D-023), and the user message of a `single_pass:grounded_answer` call is the whole assembled context. The 288 single-pass requests of the four reporting runs were exported at the shipped sampling (temperature 0.2, 1,600 completion tokens; mined-v2 had been generated at the local model's own settings, D-038b), sent to Medium from a machine with no access to Vespa or the index, and brought back. The import rebuilds each answer's sources from the recorded context plus a re-chunk of the vendored corpus, verifies the quotes with the answer layer's own verifier, strips markers nothing verified, and keeps the retrieval trace untouched. A check re-verifies each source run's own citations on the rebuilt sources: 286 of 286 answers reproduce the recorded verdicts and chunk ids, and feeding the Ministral completions back through the import reproduces the tuned-60 metrics to the last digit. Retrieval, reranking and context are therefore byte-identical between the two generators; the difference is the generator alone.

| set | correctness | partial | wrong | groundedness | citation relevance | refusal correct | gold URL cited | quote verification | fabricated quotes per answer | output tokens |
|---|---|---|---|---|---|---|---|---|---|---|
| tuned 60 | 0.93 → 0.91 | 0.12 → 0.15 | 0.02 → 0.02 | 0.82 → 0.81 | 0.93 → 0.98 | 0.92 → 0.83 | 0.82 → 0.74 | 0.86 → 0.87 | 0.40 → 0.23 | 312 → 205 |
| fresh 60 | 0.84 → 0.84 | 0.18 → 0.12 | 0.07 → 0.10 | 0.83 → 0.80 | 0.98 → 0.96 | 0.87 → 0.83 | 0.84 → 0.78 | 0.85 → 0.85 | 0.53 → 0.30 | 422 → 241 |
| mined 85 | 0.76 → 0.80 | 0.24 → 0.26 | 0.12 → 0.07 | 0.88 → 0.89 | 0.96 → 0.95 | 0.92 → 0.94 | 0.86 → 0.85 | 0.85 → 0.92 | 0.59 → 0.17 | 530 → 321 |
| mined-v2 83 | 0.64 → 0.62 | 0.25 → 0.33 | 0.23 → 0.22 | 0.71 → 0.77 | 0.93 → 0.95 | 0.78 → 0.82 | 0.57 → 0.63 | 0.83 → 0.89 | 0.41 → 0.22 | 387 → 231 |

Each cell reads Ministral 3 14B → Medium 3.5. The mined-v2 source run was generated on the local reasoning model; its Medium column is the first API-model number for that set. One mined answer is not scored because its source record ended in an error and has no trace.

**Facts.**
- Judged correctness does not move: −2, 0, +4 and −2 points on the four sets, every one inside the interval sixty to eighty-five questions allow (about ±0.09). Flash agrees (0.94 → 0.95, 0.83 → 0.84, 0.80 → 0.85). Paired per question, the changes are symmetric: on the mined set Medium is better on 11 and worse on 9, and 13 of the 20 partial answers stay partial. The "one parameter short of the reference" shape that D-042 read as a 14B limit survives the swap to Medium, so it is the prompt and the reference's strictness, not model capacity.
- Medium is the cleaner writer: fabricated quotes per answer fall by half on every set, dangling markers go to zero, citation relevance rises on the tuned set, and answers are a third shorter.
- Medium cites fewer sources (1.4 to 1.5 per answer against 1.7 to 2.3) and writes one long quote where the 14B wrote several short ones (156 characters against 91 on the tuned set). When that single quote fails verification, the answer has no verified citation and the refusal rule (D-042) turns a correct answer into a refusal: 7 answers on the tuned set against 3 for the 14B, 5 against 4 on the fresh set, which is the whole gap in the refusal and gold-URL columns. The failed quotes are not inventions. They span list items and table cells, drop Markdown link syntax, or splice with an ellipsis: Medium quotes the page as a reader sees it, and the verifier compares against the Markdown source.
- Per question at Medium's published prices the replayed answers cost 0.0046 to 0.0062 USD, below the reference column's estimate because Medium writes fewer tokens. Latency is not comparable: the replay measures one gateway call (2.6 to 3.9 s at the median) and the source runs measure the whole pipeline.

**Decisions.**
1. Medium 3.5 stays the shipped default (D-017); the published tables keep both columns. The claim "the ceiling is the 14B" is withdrawn: the next gains on the answer path are in the prompt (state the exact value or limit before explaining, one marker per list item, prose for factual questions, D-021b), which now can be measured on either model.
2. The quoting instruction gains an upper bound: one span per claim, one sentence or one table row, no ellipsis, copied from the source's Markdown. This is the rule a stronger model needs; the 14B was already writing short quotes. The verifier is not loosened: link syntax and ellipses are exactly what the resolvability check (D-036b) says the browser cannot highlight either.
3. The replay path is the way to measure any generator from now on: no index, no reranker, no credits beyond the endpoint's, and a rebuild proof that the comparison is exact. The search loop cannot be replayed, since it is multi-turn; it stays a Ministral number until the quota opens.

---

## D-043 · Page sizes in Medium 3.5 tokens

**Status:** open · 2026-09-10 · measured by `glossator.eval.corpus_stats`, outputs in `eval/corpus-stats/`

**Facts.** All 411 pages of the vendored corpus (commit `2e094f7`), page body counted with the tokenizer Mistral Medium 3.5 actually tokenizes with: model id `mistral-medium-2604`, the `tekken.json` of `mistralai/Mistral-Medium-3.5-128B` through `MistralTokenizer.from_hf_hub`. The answer layer's `count_mistral_tokens` is **not** this tokenizer: it pins `MistralTokenizer.v1()` so context budgets stay comparable with the chunker's (D-010a), and this run does not reuse it. Chunk counts are the shipped `sec1024` chunking's (and reproduce the index's 4,440 chunks exactly).

| pages | min | p50 | p75 | p90 | p95 | p99 | max | mean |
|---|---|---|---|---|---|---|---|---|
| 411 | 5 | 942 | 1,639 | 3,327 | 5,629 | 15,719 | 57,179 | 1,863 |

| under (tokens) | 2,000 | 4,000 | 8,000 | 16,000 | 32,000 |
|---|---|---|---|---|---|
| pages | 328 | 377 | 399 | 407 | 409 |
| share | 0.798 | 0.917 | 0.971 | 0.990 | 0.995 |

| budget (tokens) | pages fitting whole | share | median-sized pages per call |
|---|---|---|---|
| 8,000 | 399 | 0.971 | 8 |
| 16,000 | 407 | 0.990 | 16 |

| kind | pages | tokens | token share | characters | chunks |
|---|---|---|---|---|---|
| doc | 296 | 650,801 | 0.850 | 2,522,445 | 2,890 |
| api | 49 | 72,844 | 0.095 | 287,113 | 996 |
| model | 66 | 42,001 | 0.055 | 122,084 | 554 |

| # | page | kind | tokens | chunks |
|---|---|---|---|---|
| 1 | `/studio/batch-processing` | doc | 57,179 | 101 |
| 2 | `/studio/document-processing/basic_ocr` | doc | 44,457 | 80 |
| 3 | `/studio/audio/speech_to_text/offline_transcription` | doc | 25,690 | 50 |
| 4 | `/resources/deprecated/native-reasoning` | doc | 22,347 | 31 |
| 5 | `/studio/document-processing/annotations` | doc | 15,964 | 37 |
| 6 | `/studio/agents/agents-api` | doc | 13,519 | 29 |
| 7 | `/models` | model | 13,462 | 18 |
| 8 | `/resources/deprecated/customization` | doc | 9,273 | 44 |
| 9 | `/studio/conversations/function-calling` | doc | 9,137 | 24 |
| 10 | `/studio/audio/speech_to_text/realtime_transcription` | doc | 8,880 | 28 |

**Decision.** Pages are read whole by default and by section when a page is large (D-044): 97% of pages fit one call under 8,000 tokens, and the twelve that do not are named in the table.

---

## D-044 · The MCP surface is three tools: search, read a page, history

**Status:** decided by Tom · 2026-09-10 · replaces the eight-tool surface of D-029a; `src/entrypoints/mcp_server.py`, `tests/test_mcp_tools.py`, `skills/mistral-docs/`; evidence: Tom's Work session of 2026-09-10 21:27 (two questions, export in the worktree), D-043, D-040b, D-017b, D-015b

**Facts.**
- In the Work session the model ran ten calls for two questions: six searches, three section opens, one page read. It never called `verify_quotes` or `answer`, and its final answer carried one page link and no markers. Work rendered every tool result in the chat, including the chunk ids and the `note: index ranking only; rerank=true reorders with a model (about 5 s)` line.
- 97% of pages fit one call under 8,000 Medium 3.5 tokens; the median page is 942 tokens and twelve pages exceed 10,000 (D-043). Reading a page is the normal move; sectioning is the exception for a dozen pages.
- The reranker buys rank-1 precision an agent does not need, since it reads several hits and searches again (D-015b), and it was the only model call on the surface. The `answer` tool reaches the same correctness as the tools arm for a capable consumer (0.78 against 0.77 for Sonnet) at three times the latency and with a second model in the loop (D-040b); Medium 3.5 as that model changes nothing (D-017b).
- `verify_quotes` was called by Sonnet on 14 of 30 questions unprompted and by Work on 0 of 3. Its product is the sentence-highlight link, about 170 percent-encoded characters; most sections are short enough that the section anchor lands a reader on the sentence. Tom's ruling: no sentence-level highlighting on the agent surface, and no model should have to emit such a link.
- Chunk ids were a second identifier beside the URL. With whole-page reads the model never needs one: a section is addressed by the `url#anchor` a hit printed, or by its heading text on the pages whose headings carry no anchor (D-003a). `open_section`, `step` and `find_on_page` were three ways to move inside a page that `read_page` with an optional `section` covers.

**Decision.**
1. Tools: `mistral_docs_search(q, max_hits, kind)`, `mistral_docs_read_page(page_url, section)`, `mistral_docs_history(text | section | question)`. No ids, no response formats, no rerank, no exclusions, no locales. Search collapses the chunks of one section into one hit at its best rank and marks a hit on a large page with the section to pass to `read_page`.
2. Model-facing text names no time, cost, token or budget figure. Descriptions are under 120 words; the instructions carry the corpus scope, the citation rule (link the printed `url#anchor` next to each claim) and the refusal rule.
3. `answer`, the reranker, the search loop and `cite` stay in the package and the HTTP API as the measured context-injection baseline (`POST /ask`, `POST /cite`); the MCP surface is the agent path. The argument for the agent path is the evidence above: equal correctness, one fewer model, a third of the latency, and the consumer keeps its own reasoning and can reformulate, which is where the loop won on badly worded questions (D-035b).
4. The Work Skill, the custom instructions and the CLAUDE.md block describe the three-tool flow; the consumer evaluation's arms are `no tools` and `tools` from now on, with `answer` measured through the API.
5. The server serves an unauthenticated landing page and favicon on the subdomain beside `/health`.

---

## D-018a · The upstream list is written; nothing is sent yet

**Status:** decided by Tom · 2026-09-10 · `docs/upstream.md`

**Facts.** Fifteen defects across the toolkit, its Vespa plugin, the starter app and the documentation repository are reproduced with package lines in `docs/search-toolkit.md` and `docs/mistral-stack.md`. The toolkit still has no public repository; the starter app and the docs repository accept pull requests.

**Decision.** `docs/upstream.md` ranks them by what a fix saves the next person and names where each goes. Reports and pull requests go out once the work here is finished, so what reaches upstream is the final form; the three ranking defects that produce a plausible wrong order rather than an error go first.

---

## D-045 · The refresh is gated on a paired evaluation, and the criterion is a net loss beyond the repeat-run noise

**Status:** decided, cron default proposed for Tom to confirm · 2026-09-11 · `.github/workflows/refresh.yml`, `glossator.corpus.refresh`, `glossator.eval.gate`, `eval/refresh/served.json`, `tests/eval/test_gate.py`, `tests/corpus/test_refresh.py`; reviewed headless by opencode on GLM 5.2 (twelve findings, all applied: two would have failed every workflow run, and two corrected numbers in this entry)

**Facts.**
- The refresh workflow of D-041 built the fixed snapshots, ingested the newest, labelled and evaluated it, and uploaded an artifact. It gated nothing, and because the snapshot builder resolves the fixed dates and the pinned commit only, it never looked past the pin: the "newest snapshot" it evaluated was the served one. Nothing stopped a bad docs commit from becoming the served index, and nothing fetched a new docs commit either.
- The served index is reproduced from the vendored corpus, the manifest and the embedding cache (D-037d). "Flipping the live index" is therefore not an action a workflow can take on a runner: it is a change to the vendored corpus and a pointer, followed by `make deploy`. The gate can approve that change; it cannot serve it.
- Noise floor, from a repeat run rather than an assumption: the tuned sixty were answered twice under the same configuration nine hours apart (`2026-09-09-0312-dev60-rerank` and `2026-09-09-1230-clean-single`, same model, variant, weights, reranker and judge). Judged verdicts flipped on 6 of 60, three up and three down, for identical means of 0.925; refusal flipped on 6 of 60 with no net change; gold-URL citation flipped on 8 of 60, five up and three down, a net of two. Per-question churn of about one in ten is the noise, and the net sits within two of zero. A criterion that fires on any flipped question would fire on every refresh. The judge study (D-021a, D-021c) says the same for the judge alone: two judges agree exactly on 0.90 of verdicts.
- Rehearsal on the recorded eight-date evaluation, 1 September against 7 September: 47 paired answerable questions, retrieval 0 worse 0 better, citation 5 worse 3 better, correctness 5 worse 5 better. That is the churn above with no regression, and the gate passes it. Between the pinned commit and the docs head on 10 September (`d77fe6c8`, 412 pages) there is one page of difference, so the first real run has something to gate.
- A generator swap produces the same symmetric churn (7 worse, 7 better on the fresh sixty between Ministral 14B and Medium 3.5, D-017b). So a baseline recorded under one generator and a candidate under another would pass the net criterion, but by luck rather than by design.

**Decision.**
1. **What is compared.** Both snapshots, the served one from the vendored corpus and the candidate from the docs head, are ingested, labelled and answered in the same workflow run with the same code, model, prompts and judge. The gate reads that one run at two dates. No stored baseline run is trusted across days, so judge and prompt drift cannot masquerade as a regression or hide one. The cost of the served half is what buys that.
2. **Population.** Questions of the frozen sets labelled present in both snapshots (D-041 labels), answerable ones for retrieval, citation and correctness; unanswerable questions and cells labelled absent in both for refusal. A fact the documentation removed is never a regression of the pipeline; it goes to the changelog.
3. **Signals and criterion.** Four signals per question: `retrieved` (a chunk of an accepted page reached the context), `cited` (a verified citation on an accepted page), `refused` (`insufficient_evidence`), `correct` (the primary judge's verdict on the three-point scale). For each signal, the questions that got worse are counted against those that got better. A signal regresses when the net loss exceeds `max(4, 5% of the paired population)`: 4 on sixty questions, 8 on a hundred and forty-five. With a flip rate of one in ten and no drift, the net loss has a standard deviation of about `sqrt(0.1 n)`: 2.4 on sixty, 3.8 on a hundred and forty-five. The floor of 4 is 1.6 standard deviations on sixty (about one spurious regression per signal in twenty no-change refreshes), and the 5% share is 2.1 on a hundred and forty-five, which is one reason to answer the mined set too (point 7). The verdict is `regression` if any signal regresses; `inconclusive` if more than 10% of questions have no answer, label or verdict on the candidate side while the baseline has one, or if fewer than twenty answerable questions were paired (an outage is not evidence of no regression, and a verdict on a handful is not a verdict); and `pass` otherwise. The gate exits 0, 1, 2 for those and 3 when it could not run, so the workflow can tell a regression from a crash. The thresholds are parameters of the command and constants in the module, so a change to them is a diff.
4. **What happens on each verdict.** Pass: the workflow moves the served pointer, copies the candidate corpus over the vendored one exactly as it was evaluated (not a fresh build against the live OpenAPI and search index), advances the pinned commit in the code and the Makefile, commits the run and opens a pull request; merging it and running `make deploy` is what changes the served index. Regression or inconclusive: nothing moves; an issue is opened with the gate table and each question that got worse or better with its previous and current value. Every run uploads its records as an artifact either way.
5. **Cost of one run**, at the published prices, evaluating the fresh sixty on both snapshots (120 answers) and labelling the fresh sixty plus the mined eighty-five: two ingestions on a cold runner, 2 × 1.2 M embedding tokens, 0.24 USD (cents once the embedding cache is restored on the runner, the named follow-up); the reranker on Mistral Small 4, 120 calls, 0.11 USD; generation on Mistral Medium 3.5, 120 calls, 0.70 USD; labelling and judging on GLM through z.ai, 0 USD against the Mistral budget. About **1.05 USD per run on the shipped model**, 0.40 USD with Ministral 3 14B generating, and about forty runner minutes. Weekly on Medium is 4.5 USD a month; the 20 USD of credits are nineteen runs.
6. **Cron: proposed off at v1.0, manual trigger on.** Two reasons, both facts today: the key's quota for Medium 3.5 and Small 4 is zero (D-017a), so a scheduled run would fail at the reranker until the account is provisioned; and a run is a real dollar against twenty. The README states the schedule is off, the cost of a run, and that turning it on is uncommenting two lines once the first manual run has passed on a provisioned key. Tom confirms or overturns.
7. The mined set is labelled on every run but not yet answered, since no judged run on it exists at any snapshot; adding it to the answered set doubles the generation cost to about 1.9 USD per run and is the next extension of the gate.

---

## D-045a · The gate's second review: an API-only runner, the verdict read before accepting, symmetric errors are not an outage

**Status:** decided · 2026-09-11 · reviewed by Codex (gpt-5.6-sol) and opencode on GLM 5.3 in Herdr panes, fixes applied by GLM 5.3 and checked here; `tests/eval/test_snapshots.py`, `tests/eval/test_gate.py`, `tests/corpus/test_refresh.py`

**Facts.**
- The answering step required `GLOSSATOR_CHAT_SERVER_URL` and the workflow ran it unconditionally, so a runner holding the Mistral and z.ai keys alone failed every run; the 1.05 USD figure in D-045 assumes Medium 3.5 on the API, which the code could not select.
- After an upstream failure the issue step built its directory from an empty step output and ran `mkdir -p /gate`, so the one thing it promises on a crash, an issue, was never opened.
- `_openapi_path` checked two file names where the snapshot builder checks three, so a spec moved to `public/openapi.yaml` would have been replaced by a live download and recorded as exact, the case D-045 point 4 rules out.
- `accept` took the gate directory and never read it. A second passing run on the same day could not push `refresh/<date>`, and an artifact name without the attempt number fails "re-run all jobs".
- The unscored count included questions erroring on both sides: seven shared 429s on sixty questions gave 11.7% and `inconclusive`. The verdict order in the code was `inconclusive` before `regression`, the reverse of point 3.
- The accepted snapshot's manifest row names a runner path; on the server the snapshot corpora are mounted from `SNAPSHOTS_DIR` and the eight dates were ingested by hand (D-037d), so the history tool does not gain the accepted date on its own.
- mypy failed with three errors on the branch, and the CLI test of `refresh` passed only inside the full suite, where an earlier test had configured logging.

**Decision.**
1. Generation falls back to the Mistral API on the shipped model when no local server is configured; `GLOSSATOR_CHAT_MODEL` still overrides, and a configured server still generates on the Ministral it serves. The unit test covers the three cases.
2. The issue step resolves its directory once, falling back to the runner's temporary directory, so a crash before the gate still opens an issue.
3. The candidate builder uses the snapshot builder's list of OpenAPI file names.
4. `accept` reads `gate.json` and refuses any verdict but `pass`; the workflow's exit-code check is no longer the only guard.
5. An outage is a baseline question with usable data whose candidate counterpart has none; questions failing on both sides and candidate-only cells do not count, and the share is over the baseline's usable questions. `regression` outranks `inconclusive`, as point 3 says.
6. The PR branch carries the run id and the artifact name the attempt number.
7. The deploy README and the generated PR body state the operator's two steps after merging an accepted refresh: `make deploy` for the served index, and copying the vendored corpus into `SNAPSHOTS_DIR/<date>` plus a `snap1024` ingestion for the history tool. A deploy-script change is deferred until a refresh has actually been accepted.
8. The weekly schedule stays off and the manual trigger on: Tom confirmed on 2026-09-11 that the refresh should work end to end but not run on its own yet.

---

## D-044a · Two stop rules in the instructions, from a Work session that searched thirteen times for a page that does not exist

**Status:** decided · 2026-09-11 · `eval/runs/2026-09-11-1410-work-session-search-toolkit/` (the reduced transcript and its reading), `docs/upstream.md` row 16, `eval/mined-v2.jsonl` row `mined2-084`

**Facts.**
- Asked "what are the main features in the new Mistral search toolkit", the Work model made 13 searches and 4 page reads in about a minute over the deployed three-tool server. Eight searches returned the same five sections of the Search Toolkit landing page; two reads guessed the URL `search-toolkit/evaluation` and got `E_UNKNOWN_PAGE` both times.
- The cause is a documentation claim with nothing behind it: the landing page says the toolkit "provides components for ingestion, retrieval, and evaluation", ingestion and retrieval each have a page tree, and evaluation has no page in the pinned corpus or on the live site. The package does ship `mistralai.search.toolkit.evals` (`RetrieverEvaluator`, `MetricsCalculator`, `EvaluationDataset`, `RetrievalMetrics`), which no page mentions.
- The model's draft said the evaluation details were not documented; the answer it sent replaced that with an "Evaluation" section built from the semantic cache's hit-rate counter, cited to the cache page. The refusal rule held for twelve calls and broke at the write-up, the over-reach cell of D-038.
- The server was correct on every call and stateless, so it could not tell the model that the results repeated. The model asked for a listing twice (`site:` and a path as `q`), which no tool provides since D-044 cut `navigate`.

**Decision.**
1. The instructions gain two sentences: a search that returns the pages already read means the corpus has nothing more on it, and an unknown page URL means the page does not exist at this commit and is not retried. No tool, parameter or result text changes.
2. The missing page is upstream row 16, with the session as evidence. The question the session could not answer is `mined2-084`, typed `unanswerable`, so the over-reach is measured from now on.
3. A URL-prefix form of search (a `q` that is a page URL lists the pages under it) is the candidate answer to the two listing attempts. It is not the `outline` strategy of D-033, which handed the model the whole site outline instead of retrieval; it would be a scoped listing after a search has named the neighbourhood. Tom decides whether it ships; nothing is built until then.

---

## D-044b · A page URL in `q` lists the pages under it

**Status:** decided by Tom · 2026-09-11 · `src/entrypoints/mcp_server.py` (`_prefix_query`, `_list_pages_under`), `tests/test_mcp_tools.py`; deployed the same day

**Facts.** The Work session of D-044a asked the server for a listing twice, as `site:docs.mistral.ai/studio/search/search-toolkit` and as `search-toolkit/evaluation`, and guessed a page URL twice; the three-tool surface (D-044) has no way to answer "does this page exist". The `outline` strategy of D-033 is not that: it handed the model the whole site outline (411 titles, about 9k tokens) before any retrieval and lost on eight of eleven metrics because titles carry little signal and its page budget overflowed. A listing scoped to a path, asked for after a search hit has named the neighbourhood, is a different operation: twenty lines, no ranking replaced. The server already loads every page's URL, title and kind from the vendored corpus at startup.

**Decision.** `mistral_docs_search` keeps its three arguments. When `q` is a page URL, a `site:` form of one, or a bare path, the tool lists the pages whose URL starts with that path, sorted, one line for the URL and one for the title, from the loaded corpus and without a Vespa call; `kind` still filters. Forty pages at most, then "narrow the prefix"; zero pages prints the nearest ancestor path that has pages, never the site root, or says to search with words. The `q` description gains one clause, "or a page URL to list the pages under it". Words never start with the site or a slash, so no word query changes behaviour.

---

## D-044c · The same question after the stop rules: two searches, one read, no invented section

**Status:** recorded · 2026-09-11 · `eval/runs/2026-09-11-1410-work-session-search-toolkit/transcript-after.md`

**Facts.** Tom asked the D-044a question again in Work at 14:59, eight minutes after the redeployed server came up with the two stop rules and the listing form. The model searched twice, read the landing page once, and answered from it: the two documented pillars, the components table, the extras. When its second search returned the landing page again it wrote "I have enough information now" and stopped. No evaluation section, no guessed URL, no retry. One distortion stays: the landing page's "LLMs are not trained on your private data" became a design principle "Private by design". The listing form was not called; the question did not need it.

**Reading.** One session each way is an observation; the counted measure is `mined2-084` in every answer evaluation from now on (D-044a).


---

## D-046 · What ships: the agent path with an explicit `under` argument, the answer path stays the API baseline

**Status:** decided by Tom · 2026-09-11, points 2 and 4 implemented and deployed the same day · evidence: D-017b, D-033, D-035b, D-038a, D-040b, D-044, D-044a to D-044c, a quota probe at 15:30 today, and a dated survey of MCP design guidance (sources inline)

**The question.** Three Work sessions on a Mistral model over the three-tool surface: a plain question took two searches and a clean answer; the same question before the stop rules took thirteen searches and an invented section; a follow-up on an absent page took fourteen searches and borrowed a separate product as the answer. The model calls the server, over-searches when the corpus is silent, and over-reaches at the write-up. Is the agent path the wrong product for a mid-tier host, and should the context-injection path (`POST /ask`) be the product instead?

**Facts.**
- The answer path is measured on the same sets: 0.84 correctness on the fresh sixty and 0.76 to 0.80 on the mined set, refusal correct 0.83 to 0.94, at 7 to 12 s median and one extra model call per question (D-017b, D-038a). Its weakest cell is the same one: 0.67 to 0.69 correctness on the nine mined unanswerables, where the context is relevant and the generator over-reaches (D-038a). Swapping the generator for Medium 3.5 moved no correctness number (D-017b). The path is not immune to the failure observed in Work; it bounds it with a verifier and a refusal rule the host model does not have.
- The agent path is measured on a capable consumer only: Sonnet reaches 0.77 with the tools and 0.78 with the answer tool, at a third of the latency (D-040b). No consumer run has driven a Mistral model; the harness has no Mistral consumer, and the key's quota for Medium 3.5 and Small 4 is still zero at 15:30 today (429 on both; `ministral-14b-2512` answers). A deployed `ask` would generate on Ministral 3 14B.
- The field returns passages, not answers. OpenAI's connector contract is `search` plus `fetch`; Context7, Mintlify and Cloudflare's documentation servers return content; the one answer tool in the field, DeepWiki's `ask_question`, ships beside a structure tool and a contents tool (Cognition, 2025). The one head-to-head measurement, Infragistics' 100-query benchmark (July 2026, Claude on both arms), puts tools ahead of single-shot RAG on quality at 2.5 times the latency and 36 times the cost.
- Mid-tier models do not abstain when the context is insufficient, and retrieval lowers abstention further (Google, "Sufficient context", arXiv 2411.06037, 2024-11). Over-searching tracks the model's uncertainty about its own knowledge boundary, at 20 to 28% of searches in agentic RAG (Wu et al., arXiv 2505.17281, 2025-05). What stops loops in practice is a budget or a positive proof of absence, then a shaped result, then instruction text; nothing published says more tool surface helps a weak model.
- No published guidance endorses one argument that accepts several syntaxes. Anthropic's rule is unambiguous parameters and enums for modes ("Writing tools for agents", 2025-09-11); Prefect's Lowin recommends literals over free strings that invite guessing (AI Engineer, 2026-01-12). The follow-up session sent "URL plus word" twice, the form D-044b's parser mishandles.
- Our own measurement on stop rules is the best evidence on that point: thirteen searches became two on the same question after two sentences in the instructions (D-044c), and the listing gave the model the certainty that no evaluation page exists (D-044a).

**Decision proposed.**
1. **The product direction stands.** The MCP surface stays the agent path: three read-only tools, the host writes the answer. `POST /ask` and `POST /cite` stay in the API as the measured context-injection baseline (D-044). Reversing direction now, from a measured surface to one measured only on a different host, is a worse bet than shipping the measured surface with the two fixes below. The observed failure is a sufficient-context failure the answer path shares; what changes it is making absence unmissable, not moving generation into the server.
2. **The listing form becomes an explicit argument.** `mistral_docs_search(q, max_hits, kind, under)`: `under` is a page URL; with `q`, hits are kept to pages under it (a scoped search, which is what "URL plus word" meant); with `q` empty, the pages under it are listed, sorted, capped at forty, zero pages naming the nearest ancestor that has pages. The polymorphic `q` of D-044b is withdrawn: nothing endorses it and the model already got it wrong. Three tools, four arguments, every argument one thing.
3. **The stop rules stay** (D-044a). A per-session call counter in results is the next lever the literature names; it needs session state and is deferred to after v1.0.
4. **The `q` description asks for a sentence, not keywords.** D-035b measured keyword-only queries at 4 points below the clean question on this index, and the ranking was tuned on whole questions; Mixedbread reports the same for coding-trained models (AI Engineer, 2026-07-07). The description reads "what you want to find, in one sentence".
5. **The gap is named, not papered over.** No number exists for a Mistral model as the consumer. The next run after v1.0 is the consumer evaluation with a Mistral model through opencode's Mistral provider, tools arm and answer arm, on Ministral 3 14B now and on Medium 3.5 when the quota opens. If that run shows the answer tool ahead on the unanswerable cells for a Mistral host, `ask` returns to the surface as a fourth tool for that host through the allowlist, DeepWiki's shape; the code for it is in the history of this repository.

---

## D-047 · Every section has a key, every hit prints the link to cite, and `kind` is gone

**Status:** decided by Tom · 2026-09-11, deployed to the public server at 23:34 (the first deploy at 23:28 crash-looped on a stale `GLOSSATOR_MCP_TOOLS` in the deploy env file, which still named the eight retired tools; the public endpoint returned 502 for six minutes) · `src/glossator/citing.py`, `src/entrypoints/mcp_server.py`, `tests/test_citing.py`, `tests/test_mcp_tools.py`, `eval/corpus-map/` (the generator of the corpus map Tom read), `eval/runs/2026-09-11-2130-consumer-haiku/` (collected, not judged); evidence: the Work session of 2026-09-11 20:36 (export deleted from history, its reading below), the live docs.mistral.ai page and stylesheets fetched at 22:35, D-036, D-036b, D-043, D-044, D-044a to D-046

**Terms.** These words are used with one meaning each from here on.

| term | meaning |
|---|---|
| path | a URL folder on docs.mistral.ai. The site's only hierarchy. Some paths are also pages: `/studio/search/search-toolkit` is a page with 26 pages under it |
| page | one markdown file, one URL without a fragment. What `read_page(page_url)` reads. 411 |
| section | one markdown heading and the text under it, up to the next heading of any level. A subsection is a section of its own. 4,016, of which 143 are heading only and carry no chunk |
| heading path | page title, then ancestor headings, down to the section's own. Printed above every hit and read |
| anchor | the id a heading has on the rendered page, the part after `#` in `url#prepare-batch-file`. Only a heading written `## Title {#anchor}` in the source has one; the live site renders the others as plain `<h2>`/`<h3>` without an id. 2,193 headings have one, 1,823 do not |
| key | the name the tools use for a section. The anchor when the heading has one; otherwise `<nearest ancestor anchor>/<heading slug>`, or the slug alone when nothing above is anchored, with `-2`, `-3` on repeats: `prepare-batch-file/explanation-4`. Never presented as a link. The model copies it, never builds it |
| text fragment | the `:~:text=phrase` directive that makes a browser scroll to a phrase; independent of anchors |
| citation link | what the model cites: `url#anchor` when the section's heading has an anchor, otherwise the nearest ancestor's anchor or the bare page URL, plus a text fragment when one is warranted. Printed on a `cite:` line beside every hit and every section of a read |
| chunk | what the index ranks: a section under the token budget, or a piece of one at paragraph boundaries. Never spans two headings. 4,440 |
| over budget | a page longer than 24,000 characters: a whole-page read stops early and names the key to continue at. 20 pages |
| large page | a page of 32,000 characters or more: a hit on it names the key to read. 10 pages |
| noise | a section holding 20 or more float literals or a line over 1,500 characters: embedding vectors and pasted API responses. 26 sections on 14 pages |

**Facts.**
- The Work session of 20:36 asked the D-044a question with "to evaluate a retrieval pipeline" added, over the deployed D-046 server. 19 calls in a minute: 12 searches, 7 reads. Five searches returned the same five landing-page sections already read; the `under` listing gave positive proof at call 7 that no evaluation page exists, and six more searches followed. The answer opened with "the Search Toolkit provides a comprehensive evaluation framework through its Evaluation SDK", a separate Enterprise-only package no page links to the toolkit, and listed MRR and NDCG, which appear in no tool result. Twelve of twelve queries were keyword strings. The D-044a stop rule held once at 14:59 and failed here on the same server text: one transcript each way is noise.
- Haiku 4.5 at low effort on the same server and the same question set as D-040b plus `mined2-084` (`2026-09-11-2130-consumer-haiku`, 30 questions, two arms, 60 cells, no errors, judge pending): tools arm links resolve 0.89 against 0.44 without tools, on gold 0.78 against 0.43, 3.8 server calls per question, 15.7 s median. Twenty of thirty questions took one search and one read. The four heaviest cells were unanswerable questions, 5 to 10 searches each, and all four ended in a stated refusal that named what the documentation does say; on `mined2-084` Haiku searched five times, listed the subtree once, and wrote that the landing page names evaluation and no page documents it. The no-tools arm is not memory: headless claude ships web search and Haiku fetched 107 pages with it. Two parameter errors in 60 cells, both corrected on the next call.
- The corpus map (`eval/corpus-map/`, published as an artifact for Tom) is built from the same loader and chunker as the index. 41% of all characters sit inside code fences, 48% on doc pages, 0% on api and model pages. The twenty over-budget pages are the noisy ones: Batch Processing alone holds 174 float literals and 7 lines over 1,500 characters, 190,913 characters, 101 chunks.
- On Batch Processing, seven `###` headings under `## Prepare Batch {#prepare-batch-file}` have no anchor. Under D-044 all seven were addressed as `prepare-batch-file`: a hit on the fourth printed a link that scrolls to the top of Prepare Batch, 168,007 characters above the cited sentence, and `read_page(section="prepare-batch-file")` returned all seven at once, cut at the budget, with a `next:` line pointing at itself. The 124,000-character run under that one anchor could not be read past its first 17 chunks by any call. `section` was defined as "one heading" by the parser and as "everything under one anchor" by the tool, and the two disagree on 1,823 headings.
- The live site (fetched 22:35): headings carry `scroll-mt-[calc(var(--header)+2rem)]`, the root sets `scroll-padding-top: calc(var(--header) + 6rem)`, no stylesheet styles `::target-text`. Anchor links land below the top bar by the site's own design; text fragments should honour the same padding, and Chromium centres the match. Tom saw a text fragment scroll without a highlight and land under the bar; the browser is not recorded, and nothing on the link side changes that.
- Text fragments, measured over every chunk with the rule below: 3,727 chunks sit within 1,500 characters of where their anchor link lands and cite the anchor alone; 310 sit farther and get a fragment of 3 to 8 words; 403 sit farther and get none, because no run of 3 to 8 consecutive words of their first prose sentence is unique on the page, or the chunk holds no prose sentence. On the agents API page the sentence "Chunk of content, usually tokens corresponding to the function tool call" shares its first eight words with its neighbour and is unique from the ninth; searching runs anywhere in the sentence finds `to the function` in three.
- `kind` came in as an `exclude` list in the first read-only server commit (b9eb8af), survived as "exclusions" on the eight-tool surface, and became `kind` in D-044. No decision introduced it and nothing measured it. The one related measurement runs the other way: the outline strategy excluded API pages by design and scored 0.15 on API questions for it (D-033). Haiku passed a kind in about 4 of 30 tool cells with no visible effect.
- A per-session memory in the server was considered for the repeat-search problem and dropped: Work may open a session per call, a restart forgets everything, and results that depend on history break the read-only, idempotent contract of D-037b. Everything wanted from it is had statelessly by the changes below.

**Decision.**
1. **`kind` is removed** from `mistral_docs_search`. The kind stays in the index and the page table for rendering; a call that still sends it gets the bad-parameter reply naming the three accepted arguments.
2. **Every section has a key** (`glossator.citing.section_keys`), computed from the vendored corpus at startup and index-aligned with the chunker's `section_index`. A hit prints `[n] <page url> | section: <key>`; a section header in a read prints `## section: <key>`. The six Explanations are six sections.
3. **Every hit and every section of a read prints `cite: <citation link>`**, and the instructions say to cite the `cite:` link printed beside the text used. A hit's link points at the chunk the snippet came from, so a model that answers from a search alone cites correctly; a section's link points at the section's first prose. `mistral_docs_history` keeps taking `url#anchor`.
4. **A text fragment is printed only when it moves the landing**: the cited text starts more than 1,500 characters below where the anchor link lands, and the shortest run of 3 to 8 consecutive words of its first prose sentence occurs exactly once on the page. Otherwise the anchor link alone. Never a fragment that lands where the page already opens.
5. **`read_page(page_url, section=<key>)` returns that section and continues in reading order.** A read that stops early names the key to continue at, or `<key>:<n>` for the chunk after the last one shown when one section alone overflows; a section read whole names the section after it. No neighbour chunks, no `next:` that points at itself. The heading text still matches for a page outside the vendored corpus.
6. The Haiku run is judged when the z.ai key is at hand; its unjudged cells stand as the baseline the design above is measured against, with `mined2-084` in the set.

**Not decided.** The 403 far chunks without a fragment are a measured gap: a longer phrase, or a `start,end` range, would close part of it. The content normalization the map argues for, response bodies and float arrays first, is a separate entry once measured on the paired gate.

---

## D-047a · The same question six minutes after D-047 went live: no invented section, a hedged over-reach, no `cite:` link copied

**Status:** recorded · 2026-09-11 · `eval/runs/2026-09-11-2340-work-session-after-d047/`

**Facts.** Tom asked the 20:36 question again in Work at 23:40. 26 calls: 16 word searches, 2 listings, 8 reads, one of them a guessed URL that the server refused and the model did not retry. Twelve of sixteen queries were keyword strings and five returned the landing-page sections already read, as at 20:36. The answer opens by saying the evaluation documentation is not published and names no metric the tools did not print. It then lists precision, recall, F1, hit rate and MRR as toolkit capabilities and states that the toolkit "integrates with" the Observability Evaluation SDK; the model's last thought calls these "standard metrics that would be relevant" and features that "likely integrate". No page says either. The answer links two bare page URLs; none of the eight `cite:` lines in the tool results was copied.

**Reading.** Three things moved between 20:36 and 23:40 on the same question, one of them from D-047: the unknown-page rule held, the listings were read as proof, and no section was invented. The write-up still fills the gap by inference, in a hedged form, which is the D-038 cell and not a tool problem. The `cite:` line was not taken up on a question where the model had no fact to cite; a question with an answer is the test of it. Two Work transcripts on one question remain two samples; the Haiku run is the counted measure.

---

## D-047b · Two answerable questions in Work: reads by key, citations copied from the `cite:` lines, a text fragment in an answer

**Status:** recorded · 2026-09-11 · `eval/runs/2026-09-11-2349-work-session-two-answerable/`

**Facts.** At 23:49 Tom asked how to generate the follow-up answer after a tool call in function calling: one search, two reads by key (`five-steps/generate-followup-answer`, then `five-steps`), and an answer with the tool message shape, both code samples and the recursive case, citing the one link `…/function-calling#five-steps:~:text=We%20can%20now`, the text fragment the hit printed for a section 18,000 characters below its anchor. At 23:50 he asked which endpoints a batch job can target and how many requests a batch file holds: one search, three reads by key on the 190,913-character Batch Processing page, never the whole page, and an answer with the nine endpoints and the one-million limit citing `#batch-creation`, `#file-batching` and `#whats-the-max-number-of-requests-in-a-batch`. Every claim in both answers is on the cited section. Seven calls for two questions.

**Reading.** The three mechanisms of D-047 were each exercised once by a Work model and each did what it was built for: keys named the sections to read, `read_page` by key returned one section of a large page, and the `cite:` line was copied into the answer, text fragment included. The unanswerable question of D-047a stays the cell where the host model over-reaches.

---

## D-047c · Open: keep text fragments in citation links, or turn them off

**Status:** open · 2026-09-12 · to be decided by Tom after one check

**Facts.**
- Tom clicked the D-047b link `…/function-calling#five-steps:~:text=We%20can%20now` from Work in Brave: the page opened at the `five-steps` anchor with no highlight. Pasted into a new tab, the same link scrolled to the sentence and highlighted it.
- Work renders the link as the specification asks: `target="_blank"` with `rel="nofollow noopener noreferrer external"` (the export of the 23:49 session). The site's root scroll padding and the absence of any `::target-text` rule were checked on 2026-09-11 (D-047).
- Browsers honour a `:~:text=` directive only on navigations they consider safe from cross-site attacks: address bar, bookmarks, or a user-activated click into a fresh top-level context with no opener. Which clicks count is decided per browser engine, and a click routed through a script handler can fail the test. Brave is Chromium-based and adds its own link-privacy layers; whether the drop is Chromium's gate, Brave's, or Work's click path is not known from one observation.
- The fragment is printed on 310 of 4,440 chunk links, about 7%; the other links are unaffected. When a browser drops the directive the link still lands on the anchor, which is the D-044 behaviour. The cost of a fragment is about 50 characters on a `cite:` line the model copies.

**The choice.** A feature that helps on paste and on some hosts, and is silently ignored on others, may cost more in confusion than it returns: a reader who sees the highlight once expects it every time. The alternative is to turn fragments off and keep `url#anchor` only, accepting that 1,823 headings without an anchor land a click on their parent or the page top.

**The check before deciding.** Click the same link from Work in Chrome. If Chrome highlights, the drop is Brave's and the feature stands for other browsers; if Chrome does not, Work's click path drops the directive for every Chromium browser and the fragment only helps on paste, which argues for turning it off until the host changes. Either result goes in this entry with the decision.
