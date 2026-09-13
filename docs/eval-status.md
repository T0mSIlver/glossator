# Evaluation status, 12 September 2026

Where the evaluation stands at the ship of the Work demo. Every number names
the model that produced it. `D-0xx` is a `DECISIONS.md` entry; run names are
directories under `eval/runs/`.

## The demo, measured where it runs

Work has no API, but a Work session is a Connector-attached agent, and the
Conversations API runs the same server-side tool loop with the same model and
`reasoning_effort` (D-049). `glossator.eval.work_proxy` sends a question set
through that loop with the Skill as the agent's instructions and the workspace
Connector as its only tool. On `eval/demo.jsonl` (30 questions: 20 realistic
rows on agents, MCP, the Vibe CLI and the Search Toolkit, 5 the documentation
cannot answer, 5 that need the history tool), Medium 3.5 at `reasoning_effort=high`
scored 0.60 correctness with GLM 5.3 judging: 0.80 on the history rows, all five
answered through `mistral_docs_history` with the change as a bound between two
snapshot dates; 0.68 on single-page rows; 0.20 on the unanswerable rows, where
the model fills the gap from adjacent pages (`2026-09-12-1102-demo-medium35`,
D-049a). Links resolved 0.95, 0.76 of answers named a gold page, 5.2 tool calls
and 16 s per question at the median, 0.60 USD for the run.

Tool results are 82% of a Work session's tokens, so what `read_page` prints is
contained by rule: one language tab per sample group (`lang`, default Python),
a byte-identical sample printed once, a pasted output cut to its first 1,500
characters, code never cut (D-050). Measured on the same thirty questions:
characters per read 7,374 to 4,735, median input tokens per question 6,926 to
4,876, correctness 0.62 against 0.60, inside the noise of two runs
(`2026-09-12-1211-demo-medium35-contained`, D-050a). Every run's README now
carries a size table beside its cells: tokens per question and characters per
tool result.

## In one paragraph

The pipeline that ships is: section-aware chunks of the docs repo at a pinned
commit, embedded with `mistral-embed` at 1024 dimensions into one Vespa document
per chunk; hybrid retrieval inside Vespa with vector-heavy weights; a listwise
LLM reranker over 20 candidates; a single-pass generation with verified quotes,
per-claim markers, a deduplicated Sources block and text-fragment deep links;
a refusal path; and an MCP surface of three read-only tools (search, read a
page, history) where the agent does its own retrieval and writes the answer
(D-044). On 60 generated
development questions the shipped path scores 0.93 judged correctness with
Ministral 3 14B generating and GLM 5.3 judging; on 85 questions mined from real
GitHub issues it scores 0.76 under the same models. The failure analysis puts
the gap in generation, not retrieval, and the replay on Medium 3.5, the
product's default answer model, shows it is the prompt and the strictness of
the reference answers, not model capacity (D-017b): replaying the recorded
prompts leaves correctness unchanged within the interval, and the answers are
cleaner. Small 4, the default reranker, has never been run: the
key's quota for both models is zero (D-017a).

## The shipped pipeline, stage by stage

| Stage | Shipped choice | Decided by | Run | Models in the evidence |
|---|---|---|---|---|
| Corpus | `platform-docs-public` MDX at commit `2e094f7`, vendored, 411 pages | D-001, D-009 | none (HTTP checks) | none |
| URLs and anchors | Routing rule plus redirect table; anchor from `SectionTab`, fallback to nearest anchored ancestor | D-002, D-003, D-003a, D-033a | `dev60-anchors` | Ministral 3 14B gen, GLM 5.3 judge |
| Chunking | Section chunks with heading path and metadata, own splitter | D-010, D-034, D-035a | `dev-grid-v2`, `fresh60-page128` | Ministral 3 14B reranker and gen, GLM 5.3 judge |
| Embedding | `mistral-embed`, 1024 dims, idempotent ids, content-hash cache, sanity probe | D-011a, D-031a, D-034 | `dev-grid-v2` | `mistral-embed` |
| Retrieval | YQL `userInput OR nearestNeighbor`, weights closeness 8 and BM25 0.3, query-builder path, no floors | D-012, D-013, D-014, D-030b, D-034 | `dev-grid-v2`, `dev-floors` | `mistral-embed`, no LLM |
| Reranking | One listwise call over 20 candidates, on in `answer`, off by default in `search` | D-015, D-015a, D-015b, D-034 | `dev-grid-v2` | Ministral 3 14B (Small 4 is the untested default) |
| Non-English | Question rendered in English for retrieval, answered in its language | D-008a, D-008b | `devfr-shipped`, `devfr-translated` | Ministral 3 14B gen, GLM 5.3 judge, GLM 5.3 translated the set |
| Strategy | `single_pass`; `search_loop` is the thorough mode; `outline` is an experiment row | D-033, D-035, D-035b, D-035e | `dev60-rerank`, `*-noisy-*`, `loop-grid` | Ministral 3 14B (API) for the first two, local Ministral 3 14B Reasoning for the loop grid; GLM 5.3 judge |
| Query rewrite | Off by default, per-request switch | D-035b | `clean-rewrite`, `noisy-rewrite` | Ministral 3 14B gen, GLM 5.3 judge |
| Citations | Verified quotes, `[n]` per claim, one Sources line per (url, anchor), fragment link to the sentence | D-016, D-027b, D-027c, D-036, D-036a, D-036b | `fragments/` under `mined-shipped`, `fresh60-shipped` | none (live-page fetch) |
| Refusal | Insufficient-evidence flag plus "no verified citation" rule, unchanged | D-030b, D-042 | `failure-analysis`, `-v2` | Ministral 3 14B answers, GLM 5.3 verdicts |
| MCP surface | `mistral-docs`, three read-only tools addressed by url#anchor, no ids, no time or cost in model-facing text | D-044, D-029a, D-037b, D-037c, D-040b | `consumer-eval`, `consumer-eval-v2` | Claude Sonnet, GPT luna, muse spark 1.3 as consumers; GLM 5.3 judge |
| Deployment | One image, `remote-index` and `full`, Cloudflare tunnel, bearer token, index rebuilt from cache | D-037a, D-037d | `tests/test_deploy.py` | none |
| Time axis | Eight biweekly snapshots, `history` in three forms (phrase, page or section by key, changes under a path) over a precomputed changelog, every change a bound between two dates | D-041, D-041a, D-048, D-048a | `snapshot-labels`, `snapshot-eval`, `demo-medium35` | local Ministral 3 14B Reasoning gen, GLM 5.3 judge; Medium 3.5 on the demo |

## The Search Toolkit: what we use and what we do not

Full table with package line numbers in `docs/search-toolkit.md`. The short
version:

**Used as is.** The ingestion `Pipeline` and `Document` / `DocumentChunk` models
with derived ids; `sanitize_text`; `MistralEmbeddingPreset`; the Vespa migration
system and CLI; `DOCUMENT_PER_CHUNK`; custom root fields from chunk metadata,
which is what makes URL, anchor, heading path and kind filterable and rankable;
`set_default_ranking_weights` and its build-time check; `exclude_ids` and
`extra_yql_filter` on the builder path; the `NavigableIndex` positional
operations behind `read_page` and the section reads; `MetricsCalculator` and
`RetrieverEvaluator` for retrieval metrics.

**Used behind a workaround.** `MistralEmbedder` (retries raised from 3 to 8 for
the free tier); the `weighted-rank2` profile (phase-1 vector weight defaults to
0, D-012); per-query `ranking_weights` (undocumented `_weight` suffix);
the generated `services.xml` (no seam for the 80% disk limit, D-025b); nDCG
(collapse to distinct pages first, or it exceeds 1, D-016a); the evaluator
(isolate rows, it aborts on the first failure).

**Replaced.** The HTML extractors (drop heading ids); all six splitters (none
keeps heading metadata, and the default page chunks score section recall 0);
`VectorRetriever` (no weights, no filters); `LLMReRanker` (one sequential call
per candidate, discards its own score); `LLMQueryRewriter`; the starter's
migration, `get_index()`, MCP server and collection-name handling; everything
about answers, citations and answer quality, which the toolkit does not have.

**Skipped.** `KeywordRetriever` and `RRFRanker` (need a keyword index, Vespa's
plugin only implements the vector one, D-013); `QueryEngine` (its query
extension is generated and thrown away, and its seams do not reach Vespa);
`CrossEncoderReRanker` (needs a scoring service we would host);
`CachedQueryEngine` (in-memory only); `SummaryEnricher`; `max_candidates` and
`include_metadata` (no-ops on Vespa).

## Decisions that were close, and why they went the way they did

- **Single pass over search loop as the default.** On the shipped retrieval the
  loop leads by 2 points of correctness (0.95 against 0.93, Ministral 3 14B,
  GLM 5.3 judge) and by 6 on badly worded questions, at three times the latency
  and five times the cost. The loop stays one parameter away. D-035, D-035b.
- **No reranker on the agent path, kept in `answer`.** The reranker is 91%
  of a search's latency and buys +0.14 section recall@1 but only +0.04 at depth
  5; an agent reads several hits. D-015b.
- **Query rewrite off.** One call recovers 4 of the 19 points noise costs and
  loses 5 on clean questions. The conditional rewrite (only when the first
  retrieval is weak) is the named follow-up. D-035b.
- **1024 over 128 dimensions.** Without the reranker, 128 is not worse (section
  recall@1 0.747 against 0.704). The reranker was only run on 1024, so 1024
  ships on the numbers that exist; storage is the only cost difference. D-034.
- **Similarity floors off.** The corridor between the worst real question and
  the best off-topic one is 0.017 wide, and every unanswerable question clears
  any floor. D-030b.
- **Markers and a Sources block in the generated answer** (D-027c); on the agent
  path the citation is a Markdown link on the `url#anchor` a hit printed, and
  sentence-level fragment links were dropped with the verifier tool (D-044).
- **GLM 5.3 as the reporting judge.** It matches the human reader on 35 of 40
  and never calls correct what the reader rejected; every disagreement is in
  the strict direction, so its numbers are floors. Flash agrees at kappa 0.87
  over 492 answers but 0.62 on the reranked run, where almost everything is
  correct. D-021a, D-021b, D-021c.
- **Loop caps stay at 4 rounds, 4 searches, 600-char previews.** All six
  configurations land inside the shipped point's confidence interval on 30
  questions (local Ministral 3 14B Reasoning, GLM 5.3 judge). D-035e.
- **Refusal rule unchanged.** Trusting a verified citation over the model's flag
  would flip 43 correct refusals into wrong answers. D-042.

## Discarded without much contest

- `llms.txt` and `llms-full.txt` as the corpus: 75 of 75 links 404, no Vibe or
  Search Toolkit content. Rendered HTML: 1.7% text, empty tab panels. D-001.
- Whole-page chunks (the starter's splitter): section recall 0, twice the
  prompt tokens, more fabricated quotes. D-034, D-035a.
- The `outline` strategy: weakest on eight of eleven metrics. D-033.
- Lexical-heavy weights: lose everywhere. D-034.
- The toolkit's reranker, RRF, `QueryEngine`, query extension, semantic cache:
  see the toolkit section. D-013, D-014, D-015.
- A rehosted docs mirror with generated anchors: the product links to the live
  documentation pages, not to a mirror. D-036.
- Copying the Vespa data volume to deploy: ZooKeeper rejects its own copied
  state; rebuild from the embedding cache takes four minutes. D-037d.
- A French index: deferred, since rendering the question in English closes
  the gap to within 2 points. D-008b.

## How far the evaluation has gone

**Question sets.**

| Set | Rows | Origin | Role |
|---|---|---|---|
| `dev.jsonl` | 294 | generated by GLM 5.3 Flash over the corpus | tuning |
| `dev-fresh60.jsonl` | 60 | stratified slice of `dev.jsonl` never used for tuning | reporting |
| `dev-fr.jsonl` | 36 | dev questions translated by GLM 5.3 | French |
| `dev-noisy.jsonl` | 105 | dev questions degraded five ways | robustness |
| `mined.jsonl` | 85 | GitHub issues and agent sessions, hand-traceable | reporting, validated by Tom |
| `mined-v2.jsonl` | 84 | Vibe, client-ts, Stack Overflow, HN, consumer and Work sessions | reporting, not yet validated by hand; the 84th row was added after the runs below |
| `labels/dev60-rerank-human.jsonl` | 40 | Tom's labels | judge calibration |
| `snapshots/manifest.json` | 8 dates | biweekly commits since 1 June 2026 | time axis |

**Headline numbers, all with Ministral 3 14B generating and GLM 5.3 judging
blind unless stated.**

| Question set | Correctness | Refusal correct | Gold URL cited | Run |
|---|---|---|---|---|
| tuned 60 | 0.93 | 0.92 | 0.82 | `dev60-rerank` |
| fresh 60 | 0.84 | 0.87 | 0.84 | `fresh60-shipped` |
| mined 85, re-judged blind | 0.76 | 0.92 | 0.86 | `mined-shipped` |
| noisy 105 | 0.68 | see D-035b | 0.68 | `noisy-single` |
| French 36, rendered in English | 0.94 | not reported | 0.80 | `devfr-translated` |
| mined-v2 83, local Ministral 3 14B Reasoning | 0.65 | 0.78 | 0.57 | `mined-v2-shipped` |
| fresh 60 across eight snapshots, local Ministral 3 14B Reasoning | 0.76 to 0.82 on present cells | 0.33 to 0.80 on absent cells | | `snapshot-eval` |

**Where failures sit.** Over 575 answers from five runs, generation is 47% of
failures and retrieval misses are 1 to 3% on well-formed questions. Context
misses are zero everywhere. 53 of 77 generation failures quoted the gold section
verbatim and still answered short. D-042, refreshed in `failure-analysis-v2`.

**Judges.** Four models and one human. GLM 5.3 primary, GLM 5.3 Flash second,
Qwen 3.8 27B on the local server as the free third opinion (kappa 0.72 with the
primary), Ministral 3 14B as the strict outlier reported but never primary.
D-021a, D-021b, D-021c.

**Consumers on the MCP surface** (30 questions, GLM 5.3 judge). Claude Sonnet
at low effort goes from 0.50 correct with no tools to 0.77 with the retrieval
tools plus `verify_quotes`, links resolving 0.92 instead of 0.35. GPT luna at
low effort never called the server in 60 cells because it has its own web
search and nothing in the prompt named the server. D-040b.

**Citations.** Text-fragment links resolve on the live page for 0.86 of
citations the HTML can contain. D-036b.

**Spend.** 7.04 EUR on the console as of 9 September; the recorded ledger is a
lower bound (2.81 USD across priced chat calls) because reranker calls before
D-023b and all embeddings are not in it. The further 20 USD are not yet
credited.

## What is not measured, and matters for shipping

- **Medium 3.5 is now measured on the single pass, by replay** (D-017b, added
  the evening of 10 September): the recorded prompts of the four reporting runs
  were sent to Medium through a gateway and scored on identical retrieval and
  context. Judged correctness does not move (0.93 → 0.91, 0.84 → 0.84,
  0.76 → 0.80, 0.64 → 0.62 with GLM 5.3), fabricated quotes halve, and the
  partial-answer shape on real questions survives the swap, so it is the prompt
  and the references, not the 14B. Still unmeasured: the search loop on Medium,
  and Small 4 as the reranker. The key's quota for both models is still zero,
  so before the Work test check which model the deployed server is pointed at
  (`GLOSSATOR_MODEL`, `GLOSSATOR_CHAT_SERVER_URL`), or `mistral_docs_answer`
  will fail on the default.
- **`mined-v2` is not comparable** with the first mined set (local reasoning
  model at the card's sampling, not the API instruct model) and its rows are not
  yet validated by hand.
- **The consumer evaluation is 30 questions**, so a cell moves by about ±0.17.
  The up-front-instruction arm (a sentence naming the server, which is what the
  Work Skill and the CLAUDE.md block do), the rerank-on arm and the host-fidelity
  arm are the three arms not run.
- **Prompt rules from the human labels** (prose for factual questions, one
  marker per list item, state the exact value first) are decided, D-021b and
  D-042, but not yet measured or shipped.
- **Nothing in Work has been measured beyond hand sessions**: two on 9 September
  (D-029a, D-037b) and one on 10 September (D-044). A host-fidelity arm in the
  consumer evaluation is the follow-up.

## What the Work test showed

Tom's session of 10 September (two questions) ran ten calls: six searches,
three section opens, one page read; never the quote verifier, never the answer
tool; a correct answer with one page link. Work rendered every tool result in
the chat, ids and cost notes included. With the page-size numbers (D-043) that
decided D-044: three tools, sections addressed by `url#anchor`, no ids, no time
or cost in model-facing text, the answer path kept behind the HTTP API as the
baseline. The Skill under `skills/mistral-docs/` describes the three-tool flow.
