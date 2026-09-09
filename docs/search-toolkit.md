# The Mistral Search Toolkit, as used to build glossator

An engineer's assessment of `mistralai-search-toolkit` 0.0.13 and its Vespa plugin,
written from the parts glossator kept, worked around, and replaced. Every claim
below points at a line in the installed package, a `DECISIONS.md` entry, or a
committed run directory.

Source paths starting with a package directory (`plugins/`, `retrieval/`,
`ingestion/`, `evals/`, `search/`) are relative to
`.venv/lib/python3.14/site-packages/mistralai/search/toolkit/`. Paths starting
with `src/` or `eval/` are this repository. Reproductions are read-only: they
import the package, construct objects, call pure functions, or run a search
against the live index. None of them writes to Vespa.

## What it is

`mistralai-search-toolkit` 0.0.13 is a modular information-retrieval framework:
198 Python files and about 23,900 lines, of which the separately distributed
`mistralai-search-toolkit-plugins-vespa` 0.0.13 is 70 files and about 9,000
lines. It covers ingestion (filesystem and object-storage loaders, extractors for
PDF, HTML, email, spreadsheets and Mistral OCR, six text splitters, a `Pipeline`
that chains loader → extractor → splitter → embedder → store), embeddings
(`MistralEmbedder` with batching, retry and a concurrency semaphore), the Vespa
plugin (migrations that generate `DOCUMENT_PER_CHUNK` schemas —
`plugins/vespa/app/schemas/app.py:60` — one Vespa document per chunk, a generated
two-phase `weighted-rank2` ranking profile whose first phase selects candidates
and whose second phase reranks 100 per node,
`plugins/vespa/app/schemas/base.py:235-266` and `.../app.py:464-476`, plus
navigate/read/grep positional operations), retrieval (`VectorRetriever`,
`KeywordRetriever`, `RRFRanker`, `LLMReRanker`, `CrossEncoderReRanker`, a
`QueryEngine` that chains rewrite, extension, retrieval and reranking, and an
in-memory semantic cache), a retrieval-only evaluation harness, and — through the
`mistralai/search-starter-app` copier template — a FastMCP server with
`search`/`open`/`navigate`/`read`/`grep`/`ingest`/`delete` tools
(commit `919f2a6`, `src/entrypoints/mcp_server.py`). The source ships only as an
installed package: there is no public repository or issue tracker, and the
`dist-info/METADATA` carries no `Project-URL` (D-018). Reading the source is
therefore the only reference, which is why `AGENTS.md` forbids guessing a class
or parameter. The package also disagrees with itself about its own version:
`__init__.py:34` sets `__version__ = "0.1.0"` while the distribution is 0.0.13.

## Feature table

Status: **as is** (used unchanged), **wrap** (used behind a workaround),
**replace** (this repository wrote its own), **skip** (unreachable or not needed).
Package references carry a line number; this repository's own files are named
without one, because they move. `D-0xx` is a `DECISIONS.md` entry. In the "Index
and Vespa plugin" table only, package paths are relative to `plugins/vespa/`.

### Ingestion

| Feature | Does | Status | Why (evidence) | Advice |
|---|---|---|---|---|
| `Pipeline` | Chains extract, split, embed, store | as is | `run_file` takes in-memory bytes (`ingest/pipeline.py`, `build_pipeline`) | Keep, `loader=None` |
| `Document` / `DocumentChunk` | Frozen models, derived ids | as is | `compute_id` makes re-ingest idempotent (`ingest/extractor.py`) | Key on the URL |
| Chunk metadata dict | Free-form, round-trips through Vespa | as is | A same-named root field indexes it (migration `001`) | The citation seam |
| Extractors (OCR/PDF/HTML) | Bytes to `Document` | replace | HTML drops heading ids, so no deep link (D-002, D-003) | Only for binaries |
| `sanitize_text` | Strips code points Vespa rejects | as is | One point at a time, offsets survive (`ingest/extractor.py`) | Keep |
| Six text splitters | Split text into fragments | replace | None keeps heading metadata (`ingestion/text_splitters/markdown.py:107`, D-010) | Subclass `TextSplitter` |
| `MarkdownTextSplitter` default | 4096-char page chunks | replace | Section recall 0 (`eval/runs/2026-09-09-0136-dev-grid-v2`) | Replace if anchors matter |
| `SummaryEnricher` | Whole-document summary | skip | No per-chunk enricher ships (`ingestion/enrichment/`) | Skip |
| `MistralEmbedder` | Batched embeddings, retry | wrap | `max_retry` 3 exhausts on the free tier (`embedding/mistral_embedder.py:277`) | Set `max_retry` |
| `MistralEmbeddingPreset` | Model id plus dimensions | as is | Keeps model identity in the schema (`index/variants.py`) | Never pass bare dims |

### Index and Vespa plugin

| Feature | Does | Status | Why (evidence) | Advice |
|---|---|---|---|---|
| Migrations, `mistral-vespa` CLI | Generate and deploy the app | as is | Replayed at runtime, so nothing drifts (migration `001`) | Treat as immutable |
| `DOCUMENT_PER_CHUNK` | One Vespa document per chunk | as is | One hit is one chunk (`…/document_per_chunk_index.py:490`) | The other mode is deprecated |
| Custom root fields | Metadata becomes indexed fields | as is | Seven declared (migration `001`, `_chunk_metadata_fields`) | The plugin's best feature |
| `weighted-rank2` profile | Two-phase ranking | wrap | Phase-1 vector weight defaults to 0 (D-012) | Set every weight yourself |
| `set_default_ranking_weights` | Bakes weights into the schema | as is | Rejects unknown features (`app/schemas/base.py:210-234`) | Use the build-time check |
| Named query profiles | Stored YQL plus weights | replace | Kill `exclude_ids` and filters (`search/query_builder.py:128-135`) | Pass `query_profile=None` |
| `ranking_weights` per query | Override weights per request | wrap | Needs a `_weight` suffix nothing checks (`search/bodies.py:33-34`, D-025) | Translate in one place |
| `exclude_ids` | Skip chunks already seen | as is | Bound as a YQL param (`search/query_builder.py:118-126`) | Builder path only |
| `extra_yql_filter` | Raw YQL predicate per query | as is | The only per-query filter (`search/query.py:25-30`) | Close over the values |
| `NavigableIndex` ops | navigate, read, grep, get_chunk | as is | Most of the MCP surface (`retrieval/engine.py`, `Navigation`) | Keep |
| HNSW distance metric | Vector index configuration | wrap | Hardcoded euclidean (`app/schemas/field.py:29`) | Restrict by id to read cosine |
| `matchfeatures` | Per-hit feature values | replace | Dropped by the hit parser (`…/document_per_chunk_index.py:490-529`) | Budget a second query |
| Generated `services.xml` | Deployment descriptor | wrap | No `<resource-limits>` seam (`deploy/templates/services.xml.j2`) | Patch outside the toolkit |
| Name constraints | `^[a-z]+$`, `^[a-z_]+$` | wrap | Copier accepts underscores (`app/schemas/app.py:579,414`, D-022a) | Letters only for the app |
| `mistral-vespa bruno` | Bruno collection, lock file | as is | `Makefile`, `bruno` target | Keep for HTTP debugging |
| `MigrationContext` | Migration state | as is | Module global, guarded (`migration.py:133-141`) | One `VespaApp` per process |

### Retrieval

| Feature | Does | Status | Why (evidence) | Advice |
|---|---|---|---|---|
| `QueryEngine` | Rewrite, extend, retrieve, rerank | skip | Its seams do not reach Vespa (D-014); extension discarded | Ten lines you already own |
| `VectorRetriever` | Embeds and searches | replace | Plain query: no weights, no filter (`retrieval/retriever.py` header) | Subclass `Retriever` |
| `KeywordRetriever` | BM25-only retrieval | skip | Needs a `KeywordStoreIndex` (`plugins/vespa/search/index.py:11`) | Not on Vespa (D-013) |
| `RRFRanker` | Fuses result groups | skip | Only one retriever exists on this backend (D-013) | Not available on Vespa |
| `LLMReRanker` | LLM relevance reranking | replace | Sequential, drops its own score (`retrieval/rerankers/llm.py:68-76`, D-015) | One listwise call |
| `CrossEncoderReRanker` | Hosted cross-encoder scoring | skip | Needs a `/score` service you host (D-015) | Skip |
| `LLMQueryRewriter` | Rewrites before retrieval | replace | Bare string, no history, global prompts (D-035b) | Own it if you measure it |
| `LLMQueryExtension` | Generates sub-queries | skip | Generated and discarded (`retrieval/query_engine.py:114-129`) | A paid call for nothing |
| `CachedQueryEngine` | Semantic cache | skip | In-memory backend only (`retrieval/cache/backends/`) | Not for a served product |
| `include_metadata` / `_content` | Trim the payload | skip | Absent from the Vespa index implementation | Budget for full content |
| `max_candidates` | Candidate pool size | skip | A documented no-op on Vespa (`search/models.py:27-35`) | Ignore |

### Evaluation and starter scaffolding

| Feature | Does | Status | Why (evidence) | Advice |
|---|---|---|---|---|
| `MetricsCalculator` | recall, MRR, MAP, nDCG@k | wrap | nDCG assumes one hit per gold id (`evals/metrics.py:186`, D-016a) | De-duplicate first |
| `RetrieverEvaluator` | Walks the dataset | wrap | Aborts on the first failure (`evals/evaluator.py:127-128`) | Isolate each row |
| `relevant_reference_ids` | Score against URL proxies | as is | Chunk ids move with the chunker (`eval/retrieval_metrics.py` header) | Right default for docs |
| Vespa match evaluator | Match-phase recall | skip | End-to-end recall already covers it | Skip |
| Answer-quality metrics | — | replace | Not in the package at all (D-016) | Budget for all of it |
| Starter migration | Creates the first schema | replace | Invalid app name, deprecated dimensions (D-022a) | Rewrite before deploying |
| Starter `get_index()` | Live index handle | replace | Always sets `hybrid-search` (D-014) | Pass `query_profile=None` |
| Starter MCP server | FastMCP tools | replace | `ingest`/`delete` write uncitable chunks (D-026) | Keep the shape, rewrite the tools |
| Starter `COLLECTION_NAME` | Schema name from `.env` | replace | Entrypoints and migration disagree (D-022) | Own schema names in code |

## What worked well

**The schema generator is the reason the citations work.** A chunk carries a
free-form metadata dict, and declaring a same-named root field in the migration
turns that key into an indexed, filterable, rankable Vespa field. glossator
declares seven — `url`, `anchor`, `page_title`, `heading_path`, `kind`, `locale`,
`section_index` (`src/glossator/index/migrations/001_vespa_create_index_schema.py`, `_chunk_metadata_fields`)
— and gets BM25 over the heading path and a `kind in ("api")` filter for free.
`array<string>` heading paths yield elementwise `bm25_heading_path_max`. Nothing
had to be written for this.

**Migrations replay in memory, so the running process and the deployed schema
cannot drift.** `VespaApp.app_definition` re-executes the migration files, which
is why the schema this repository believes in is the schema Vespa holds. It also
means a reproduction can render the deployment descriptor without touching a
cluster:

```console
$ uv run python -c "
from mistralai.search.toolkit.plugins.vespa.app.generate_vespa_app import MistralApplicationPackage
from glossator.index import app
MistralApplicationPackage(app.app_definition)" 2>&1 | grep 'require an explicit weight' | head -1
[info] Ranking inputs require an explicit weight before they affect ranking; until
       then they default to 0 and do not contribute to relevance
       fields_requiring_explicit_weight=['ranking.features.query(bm25_heading_path_avg_weight)',
       'ranking.features.query(match_heading_path_weight)',
       'ranking.features.query(match_page_title_weight)'] schema=docs_page_lowdim
```

(one log line, wrapped here.) The generator names every ranking input left at zero, and
`_validate_default_ranking_weights` (`plugins/vespa/app/schemas/base.py:210-234`)
raises on a weight naming a feature that does not exist. Both checks caught real
typos during tuning.

**`DOCUMENT_PER_CHUNK` behaves as documented.** One hit is one chunk, the hit
parser surfaces declared root fields as first-class attributes
(`plugins/vespa/search/document_per_chunk_index.py:490-529`), and a re-ingest of a
page deletes its chunks by `source_id` before writing. Ids are derived
(`compute_id(source_id, locator)`), so keying `source_id` on the page URL makes a
re-ingest idempotent without a manifest of chunk ids.

**The positional operations gave the MCP server its whole navigation surface.**
`navigate`, `read`, `grep` and `get_chunk` are implemented in the plugin and
wrapped in about 70 lines (`src/glossator/retrieval/engine.py`, `Navigation`). Against
the live index:

```console
$ uv run python -m glossator.retrieval "how do I stream a chat completion" --top-k 3 --skip-probe
'how do I stream a chat completion' on docs_section_fulldim (3/3 hits, 288 ms)

1. https://docs.mistral.ai/studio/conversations/chat-completion#chat-completion  score=15.5187
   Chat completions > Chat completion
   ... **Streaming** For streaming chat completions requests, you will provide a list of ...
2. https://docs.mistral.ai/studio/conversations/chat-completion#chat-completion  score=15.1684
3. https://docs.mistral.ai/studio/conversations/chat-completion#chat-completion  score=15.1089
```

and from the top hit, `around(window=1)` returns the sections at offsets
3743-4606, 5975-7452 and 8755-10285 of the same page in reading order, `next()`
returns 8755-10285, and `grep("stream")` returns 5975-7452 and 7434-8773. Seven
MCP tools rest on that. The three top hits being three chunks of one section is
the crowding D-012a records and the reason the evaluation collapses the ranked
list before scoring (D-016a).

**`exclude_ids` and per-query filters work, on the builder path.** The same query
object carries both, and the generated YQL shows it:

```console
$ uv run python -c "
from mistralai.search.toolkit.plugins.vespa.search.query import VespaSearchQuery
from mistralai.search.toolkit.plugins.vespa.search.query_builder import build_search_query_body
from glossator.index import app
schema = next(s for s in app.app_definition.schemas if s.document_type == 'docs_section_fulldim')
q = VespaSearchQuery(query='how do I stream', embedding=[0.0]*1024, top_k=5, exclude_ids={'abc'})
print(build_search_query_body(schema, None, q).to_dict()['yql'])"
select * from docs_section_fulldim where (userInput(@query) or
  ({targetHits:1000}nearestNeighbor(content_embedding, embedding))) and !(id in (@exclude_ids))
```

**The evaluation arithmetic did not have to be rewritten.** `MetricsCalculator`
and `RetrieverEvaluator` compute recall@k, MRR, MAP and nDCG@k, and
`relevant_reference_ids` proxies let gold be written as a URL rather than a chunk
id that changes whenever the chunker does
(`src/glossator/eval/retrieval_metrics.py`, module docstring). The 13-configuration grid in
`eval/runs/2026-09-09-0136-dev-grid-v2` runs on the toolkit's metrics with one
wrapper module.

**The source is commented honestly.** `_generate_closeness_function`
(`plugins/vespa/app/schemas/ranking_functions/embeddings.py:69-81`) states in full
that leaving the closeness weight at 0 makes phase 1 BM25-only and drops ANN-only
hits out of the rerank window. The bug in the starter template is described in
the library it ships with. That is worth more than most documentation.

## What did not

### The vector term is switched off in phase 1

**Symptom.** A paraphrased question ranks the right section second or third; a
purely semantic match scores 0 before reranking (D-012a).

**Cause.** The generated `weighted-rank2` profile weights every feature by
`query(<feature>_weight)`, and a feature with no explicit weight defaults to 0
(`plugins/vespa/app/schemas/base.py:178-189`,
`plugins/vespa/migration.py:551-575`: "features left unset keep defaulting to 0").
The starter's `hybrid-search` profile sets `bm25_content_weight=0.5`,
`match_content_weight=0.5` and
`content_embedding_cosine_similarity_score_weight=5.0`, and never sets
`content_embedding_closeness_weight` (commit `919f2a6`,
`src/search_app/migrations/001_vespa_create_index_schema.py:47-69`). Closeness is
the only vector term in phase 1; the cosine term is a phase-2 function
(`plugins/vespa/app/schemas/ranking_functions/embeddings.py:52-65` returns
`Rank2Function`).
Phase 1 keeps 10,000 documents per node and phase 2 reranks 100
(`plugins/vespa/app/schemas/app.py:464-476`), so a hit phase 1 scores at 0 never reaches
the cosine term.

**What we did.** Set `content_embedding_closeness` to 5.0 in the migration and
tuned it to 8.0 per query
(`src/glossator/index/migrations/001_vespa_create_index_schema.py`, `_RANKING_WEIGHTS`,
`src/glossator/retrieval/config.py`, `SHIPPED_RANKING_WEIGHTS`).

**Cost.** The grid carries the starter's weights as a baseline row for this
reason. In `eval/runs/2026-09-09-0136-dev-grid-v2`, vector-heavy weights
take section recall@1 from 0.704 to 0.732 and section recall@5 from 0.880 to 0.937
on `sec1024`; on `sec128`, section recall@5 goes from 0.915 to 0.958.

### `RRFRanker` and `KeywordRetriever` cannot run on Vespa

**Symptom.** The toolkit's own skill file recommends adding a `KeywordRetriever`
beside the `VectorRetriever` and fusing with `RRFRanker`. On Vespa that raises a
pydantic `ValidationError`.

**Cause.** `KeywordRetriever.__init__` takes a `KeywordStoreIndex`
(`retrieval/retrievers/keyword.py:18`), and the Vespa index is a
`VectorStoreIndex` only:

```console
$ uv run python -c "
from mistralai.search.toolkit.plugins.vespa.search.index import VespaSearchIndex
from mistralai.search.toolkit.search import KeywordStoreIndex, VectorStoreIndex
print(issubclass(VespaSearchIndex, VectorStoreIndex), issubclass(VespaSearchIndex, KeywordStoreIndex))"
True False
```

`plugins/vespa/search/index.py:11` is the declaration. `RRFRanker` fuses result
groups (`retrieval/rerankers/rrf.py:29-31`) and there is only ever one group.

**What we did.** Hybrid happens inside Vespa: the builder emits
`userInput OR nearestNeighbor` and the two-phase profile combines the lexical and
vector features (D-013, `src/glossator/retrieval/retriever.py`, `DocsRetriever`).

**Cost.** None to quality. The cost is that the documented path is wrong, so the
class hierarchy has to be read before the advice is followed.

### A named query profile disables `exclude_ids` and every filter

**Symptom.** The starter ships an MCP `search` tool with an `exclude_ids`
parameter that raises on any non-empty value.

**Cause.** `build_search_query_body` raises when a profile is set:

```console
$ uv run python -c "
from mistralai.search.toolkit.plugins.vespa.search.query import VespaSearchQuery
from mistralai.search.toolkit.plugins.vespa.search.query_builder import build_search_query_body
from glossator.index import app
schema = next(s for s in app.app_definition.schemas if s.document_type == 'docs_section_fulldim')
q = VespaSearchQuery(query='q', embedding=[0.0]*1024, exclude_ids={'abc'})
build_search_query_body(schema, 'hybrid-search', q)"
mistralai.search.toolkit.search.errors.SearchError: exclude_ids requires the query
builder (unset query_profile)
```

`plugins/vespa/search/query_builder.py:128-135` raises for both `exclude_ids` and
`extra_yql_filter`, and the starter's `get_index()` passes
`query_profile="hybrid-search"` on every call (commit `919f2a6`,
`src/search_app/__init__.py:21-27`). The named profile is also the starter's only
way to set ranking weights, so it is weights or filters, not both.

**What we did.** Query with `query_profile=None`. The builder still attaches the
schema's generated default profile, so the migration's baked-in weights apply and
`ranking_weights` overrides them per request
(`src/glossator/index/__init__.py`, `get_index`, D-025 resolving D-014). `exclude_ids`
then works: excluding the top hit's chunk id promotes the second hit, which is
what the MCP `search` tool and the answer layer's search loop rely on.

**Cost.** One custom `Retriever` (139 lines,
`src/glossator/retrieval/retriever.py`).

### Ranking weights are silently ignored unless the key carries a suffix

**Symptom.** Four weight configurations produced byte-identical scores (D-025).

**Cause.** The two APIs that set the same weight disagree about the key.
`set_default_ranking_weights` takes the feature name and appends `_weight` itself
(`plugins/vespa/app/schemas/base.py:178-180`), while
`SearchBody.to_dict` interpolates the caller's key verbatim into
`ranking.features.query(<key>)` (`plugins/vespa/search/bodies.py:33-34`). A bare
feature name names a query input no rank expression reads. Nothing validates it:
`plugins/vespa/search/query_builder.py:146` passes the dict straight through, and
Vespa accepts unknown
query features. Against the live index, the same override spelled two ways:

```python
# suffix_probe.py — one query against the live index, three spellings of one weight.
import asyncio
from dotenv import load_dotenv; load_dotenv()
from mistralai.search.toolkit.plugins.vespa.search.query import VespaSearchQuery
from glossator.index import get_index
from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.context import restrict_to
from glossator.retrieval.engine import SearchEngine

Q = "how do I stream a chat completion"

async def main():
    index, engine = get_index("sec1024"), SearchEngine(RetrievalConfig(rerank=False))
    embedding = await engine.retriever.embed_query(Q)
    ctx = restrict_to("docs_section_fulldim")

    async def scores(weights):
        q = VespaSearchQuery(query=Q, embedding=embedding, top_k=5, ranking_weights=weights)
        return [round(r.score, 6) for r in await index.search(query=q, context=ctx)]

    print("no override        :", await scores({}))
    print("bare feature name  :", await scores({"content_embedding_closeness": 999.0}))
    print("with _weight suffix:", await scores({"content_embedding_closeness_weight": 999.0}))

asyncio.run(main())
```

```console
$ uv run python suffix_probe.py
no override        : [15.518717, 15.168377, 15.108882, 14.686734, 14.56864]
bare feature name  : [15.518717, 15.168377, 15.108882, 14.686734, 14.56864]
with _weight suffix: [617.736553, 597.569368, 597.556562, 591.823906, 586.815293]
```

The bare spelling is accepted and does nothing; the suffixed one moves the scores
by two orders of magnitude.

**What we did.** One vocabulary — the feature name — everywhere in the package,
translated in one function (`query_weights`,
`src/glossator/retrieval/config.py`), and a closed set of known feature
names rejected at config time (`RANKING_FEATURES`, and the validator that
rejects anything outside it).

**Cost.** Four weight configurations produced byte-identical scores until the
suffix was added (D-025).

### The LLM reranker reorders without scoring, one call at a time

**Symptom.** Reranking 20 candidates takes 20 round trips, and the returned
results still carry retrieval scores, so a downstream consumer that reads `score`
sees the ranking it did not get.

**Cause.** `retrieval/rerankers/llm.py:68-70` is a `for` loop with an `await`
inside and no `TaskGroup`; line 76 rebuilds the list from the results alone and
drops the `relevance_score`. With a stub provider that answers in a fixed 100 ms
and never touches the network:

```python
# rerank_probe.py
import asyncio, time
from types import SimpleNamespace
from mistralai.search.toolkit.llm.base import LLMProvider
from mistralai.search.toolkit.retrieval.rerankers.llm import LLMReRanker
from mistralai.search.toolkit.search import SearchResult, SearchResultChunk

CALLS = 0

class Stub(LLMProvider):
    def _create_client(self): return None
    async def call_llm(self, *a, **k): raise NotImplementedError
    async def parse_llm(self, *a, **k): raise NotImplementedError
    async def call_llm_with_config(self, system_prompt, user_prompt, **k):
        global CALLS; CALLS += 1
        await asyncio.sleep(0.1)
        message = SimpleNamespace(content='{"relevance_score": 0.5, "reasoning": ""}')
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])

def result(i):
    return SearchResult(
        chunk=SearchResultChunk(id=f"c{i}", source_id="p", locator="char:0-10",
                                content=f"candidate {i}", start_offset=0,
                                end_offset=10, chunk_type="content"),
        score=1.0 - i / 100)

async def main():
    candidates = [result(i) for i in range(20)]
    start = time.monotonic()
    out = await LLMReRanker(llm_provider=Stub()).rerank("stream a chat completion", candidates)
    print(f"candidates={len(candidates)} llm_calls={CALLS} wall={time.monotonic()-start:.2f}s")
    print("scores on returned results:", sorted({r.score for r in out})[:5])

asyncio.run(main())
```

```console
$ uv run python rerank_probe.py
candidates=20 llm_calls=20 wall=2.00s
scores on returned results: [0.81, 0.8200000000000001, 0.83, 0.84, 0.85]
```

20 candidates, 20 calls, 2.00 s at 100 ms each — exactly serial — and the returned
scores are the retrieval scores, unchanged. `CrossEncoderReRanker` does
rewrite `score`, so the two rerankers in the same package have different
semantics.

**What we did.** One listwise call that reads all 20 candidates side by side and
returns positions, with the position written back as `rerank_score` and the Vespa
score kept as `retrieval_score`
(`src/glossator/retrieval/reranker.py`, D-015).

**Cost.** 336 lines. It bought the largest single retrieval gain measured:
in `eval/runs/2026-09-09-0136-dev-grid-v2`, page recall@1 0.596 → 0.711, section
recall@1 0.732 → 0.873, section recall@5 0.937 → 0.979, API-reference recall@1
0.64 → 0.90, at a median 4,392 ms against 9 ms and 0.204 USD for 294 questions.
37 of 294 calls (13%) returned a ranking that could not be applied and fell back
to retrieval order.

### nDCG can exceed 1 when gold is a URL proxy

**Symptom.** nDCG@10 of 1.220 on the first grid (D-016a); the metric is bounded by
1 by definition.

**Cause.** `evals/metrics.py:186` builds the ideal DCG as
`[1.0] * min(k, len(ground_truth_set))`, assuming each relevant id appears once in
the ranked list. Under URL proxies several chunks of one page all match the same
gold URL, so the actual DCG sums more relevant positions than the ideal:

```console
$ uv run python -c "
from mistralai.search.toolkit.evals.metrics import MetricsCalculator as M
print(M._calculate_ndcg_at_k(['/api/chat']*3 + ['/models', '/agents'], {'/api/chat'}, [10]))"
{10: 2.1309297535714578}
```

**What we did.** Collapse the ranked list to distinct proxies at their best rank
before scoring, which also makes recall@k read as "the answer was among the first
k pages" and makes page-level numbers comparable across chunkings
(`src/glossator/eval/retrieval_metrics.py`, module docstring; D-016a, D-034).

**Cost.** The first grid's nDCG column was unusable and the run had to be redone
with de-duplication (`eval/runs/2026-09-08-2340-dev-grid` superseded by
`eval/runs/2026-09-09-0136-dev-grid-v2`).

### The generated `services.xml` has no seam for resource limits, and Vespa blocks feeds at 80% disk

**Symptom.** Every feed rejected, and because re-indexing deletes a page's chunks
before writing the new ones, a schema left with zero documents (D-025b).

**Cause.** Vespa blocks external feeds above 80% disk by default. The rendered
descriptor has nowhere to raise it:

```console
$ uv run python -c "
import tempfile; from pathlib import Path
from mistralai.search.toolkit.plugins.vespa.app.generate_vespa_app import MistralApplicationPackage
from mistralai.search.toolkit.plugins.vespa.deploy.xml import write_services_xml
from glossator.index import app
with tempfile.TemporaryDirectory() as d:
    write_services_xml(Path(d), MistralApplicationPackage(app.app_definition), None)
    print((Path(d)/'services.xml').read_text())"
<?xml version="1.0" encoding="UTF-8" ?>
<services>
  <container id="default" version="1.0">
    <document-api/>
    <search/>
  </container>
  <content id="glossator" version="1.0">
    <min-redundancy>1</min-redundancy>
    <documents>
      <document type="docs_page_lowdim" mode="index"></document>
      ...
    </documents>
  </content>
</services>
```

`plugins/vespa/deploy/templates/services.xml.j2` contains no `<tuning>` and no
`<resource-limits>`, and `write_services_xml`
(`plugins/vespa/deploy/xml.py:37-51`) takes no parameter for one. So a
hand-patched limit lives outside the repository, and any redeploy through
`mistral-vespa` resets it.

**What we did.** Ingestion feeds and removes one small document before it is
allowed to delete anything
(`src/glossator/ingest/pipeline.py`, `_verify_index_writable`), and aborts on the first rejected
write instead of continuing through 411 pages. The README states the 80% limit.

**Cost.** The `sec1024` schema was left holding zero documents. Two reranked grid
rows and one floor calibration ran against the empty schema, scored zero, and
were re-run as separate run directories; `sec1024` was re-ingested at 4,440 chunks
with zero failures (D-025b). The numbers that stand are
`eval/runs/2026-09-09-0136-dev-grid-v2` (D-034) and
`eval/runs/2026-09-09-0115-dev-floors` (D-030b).

### `QueryEngine` pays for query extension and throws it away

**Symptom.** Configuring `query_extension` costs an LLM call per query and changes
nothing.

**Cause.** `retrieval/query_engine.py:114-115` says so in a comment, and line 127
retrieves with `search_query` alone; `extension_result` is only carried out in the
result object (line 152).

**What we did.** Never constructed a `QueryEngine`. Multi-query fan-out is the
answer layer's search loop, which is measured
(`eval/runs/2026-09-08-2305-dev60-baseline`, D-033).

**Cost.** None: it was never constructed.

### Nothing in the toolkit tells you the embedding model is real

**Symptom.** Every shape check an embedding pipeline runs — model name, dimension
count, non-zero norm — passes when the weights are random, and search over noise
still returns plausible results (D-031).

**Cause.** Not a defect so much as an absence: `MistralEmbedder` validates
dimensions and retries transport errors, and there is no semantic assertion
anywhere in `embedding/`.

**What we did.** A probe with five fixed question/passage pairs plus two unrelated
passages: each question must be closest to its own passage and beat every other by
a margin, and one stored chunk re-embedded must match the vector Vespa holds
(`src/glossator/retrieval/probe.py`). `make ingest` runs it before embedding
anything; the engine runs it once per process; `GET /health` reports it.

**Cost.** 305 lines. The measured headroom (D-031a): related similarity 0.755 at
1024 dimensions against a 0.55 floor, separation 0.095 against 0.05, round trip
0.99997 against 0.999. Separation is the check that catches random weights, since
untrained embeddings put every text at the same distance from every other.

### Smaller ones, each reproducible

- **App name pattern.** `VespaAppDefinition(name="mistral_docs", schemas=[])`
  raises `String should match pattern '^[a-z]+$'`
  (`plugins/vespa/app/schemas/app.py:579`), while the copier template accepts an
  underscore, so a freshly generated starter cannot run `make setup-vespa`
  (D-022a). Schema document types allow `^[a-z_]+$` but no digits
  (`app.py:414`), which is why the variants are named `docs_section_fulldim`
  rather than `docs_section_1024`.
- **HNSW is always euclidean.**
  `RankingType2Defaults[RankingType.EMBEDDING]["ann"] == HNSW(distance_metric="euclidean")`
  (`plugins/vespa/app/schemas/field.py:29`), with no parameter, whatever the
  embedding model declares. Reading a hit's cosine therefore needs a query
  restricted to the hits' ids; an unrestricted vector-only query returns a
  different candidate set whose top cosine was 0.7251 against 0.7884 on the same
  query (D-025a).
- **`matchfeatures` never reach the caller.** The profile emits them
  (`plugins/vespa/app/schemas/base.py:249,265`) and the hit parser reads only
  `fields` and `relevance` (`plugins/vespa/search/document_per_chunk_index.py:490`),
  so any feature value costs
  a second query with every weight zeroed but one
  (`src/glossator/retrieval/config.py`, `cosine_only_weights`).
- **The evaluator aborts the run on the first failing query.**
  `evals/evaluator.py:127-128` raises `RuntimeError` inside the batch, so one 429
  loses the whole grid. The grid embeds once per (model, question), throttles at
  1.1 s and retries 8 times instead of 3; the second run had zero errors (D-025a).
- **`include_metadata` and `include_content` are ignored** by the
  `DOCUMENT_PER_CHUNK` index — neither name appears in the file — and
  `ApproximateQueryOptions.max_candidates` is a documented no-op on Vespa
  (`search/models.py:27-35`).
- **No document count API.** `SearchEngine.document_count` reaches into
  `index._client` (`src/glossator/retrieval/engine.py`, `document_count`).
- **`MigrationContext` is a module global** with a "cannot initialize twice" guard
  (`plugins/vespa/migration.py:133-141`), so two `VespaApp` instances in one
  process collide.
- **`__version__` is `0.1.0`** in `__init__.py:34` while the distribution is
  0.0.13, so a runtime version check reports the wrong number.

## Which parts to use on a new project

Use these, unchanged:

1. **The Vespa migrations and the `mistral-vespa` CLI.** Schema generation,
   deployment, the Bruno export and the lock file are the strongest part of the
   package, and re-executing migrations to rebuild the schema in memory removes a
   whole class of drift bug.
2. **`DOCUMENT_PER_CHUNK` schemas with custom root fields.** Declare every piece of
   metadata a citation needs as a root field and it becomes filterable and
   rankable at no cost.
3. **The generated two-phase ranking profile** — but set every weight explicitly
   in the migration, and read `get_unset_ranking_inputs` output on every build.
4. **`VespaSearchQuery` on the builder path**, never a named query profile. It is
   the only configuration in which weights, filters and exclusions coexist.
5. **The positional operations** (`navigate`, `read`, `grep`, `get_chunk`). If you
   are building an agent-facing surface, this is most of it.
6. **`MistralEmbedder`**, with `max_retry` raised, and `MistralEmbeddingPreset`
   instead of a bare dimension count.
7. **`Pipeline`** as the ingestion spine, with your own extractor and splitter
   plugged into it.
8. **`MetricsCalculator` and `RetrieverEvaluator`**, on a de-duplicated ranked
   list.

Write these yourself:

- **The chunker.** No splitter records heading metadata, and heading path,
  anchor and page title are what make a citation deep-link. Subclass
  `TextSplitter` so the `Pipeline` still drives it.
- **The retriever.** `VectorRetriever` builds a query object with no seam for
  weights or filters. Roughly 140 lines replaces it and unlocks everything above.
- **The reranker.** One listwise call instead of n pointwise ones: it was the
  largest measured retrieval gain and it costs one round trip, not twenty.
- **The answer layer.** There is no answer generation, no citation type, no
  groundedness control, no streaming and no answer-quality metric anywhere in the
  package (D-016). Budget for all of it.
- **An embedding sanity probe.** Nothing upstream will tell you the vectors mean
  anything.
- **The ingestion safety rail.** Verify a write is accepted before deleting the
  documents you are about to replace.

Skip: `QueryEngine`, `KeywordRetriever`, `RRFRanker`, `LLMReRanker`,
`CrossEncoderReRanker`, `LLMQueryExtension`, `CachedQueryEngine`, and the starter
app's `ingest`/`delete` MCP tools.

## Recap

| Feature | Verdict | Reason |
|---|---|---|
| Vespa migrations, schema generation, CLI | keep | Custom root fields make metadata filterable and rankable; migrations replay so nothing drifts |
| `DOCUMENT_PER_CHUNK` index and positional ops | keep | One hit is one chunk, and navigate/read/grep is most of an agent surface for free |
| Two-phase ranking profile | wrap | Right features, but phase-1 vector weight defaults to 0 and query-time weights need a suffix nothing validates |
| Named query profiles | replace | They disable `exclude_ids` and every per-query filter (D-014) |
| `VectorRetriever` / `QueryEngine` | replace | No seam for ranking weights or filters; query extension is generated and discarded |
| `LLMReRanker` | replace | Sequential, one call per candidate, and it discards its own score; one listwise call gave section recall@1 0.732 → 0.873 |
| Retrieval eval harness | wrap | Sound arithmetic, but nDCG assumes each gold id appears once and the runner aborts on the first failure |
| Answer generation and citations | replace | Not in the package at all |
