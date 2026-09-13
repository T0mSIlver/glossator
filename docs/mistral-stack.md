# Mistral stack

Installed-package paths below are relative to `.venv/lib/python3.14/site-packages/`.
Repository versions come from `uv.lock`, not import-time version strings.

## Dependency inventory

| Component | Exact installed version or revision | Role |
|---|---:|---|
| `mistralai` | 2.9.4 | Mistral API client for chat and embeddings (`uv.lock:1616-1625`) |
| `mistral-common` | 1.11.7 | Token counting and token-bounded truncation (`uv.lock:1591-1600`) |
| `mistralai-search-toolkit` | 0.0.13 | Ingestion and retrieval abstractions (`uv.lock:1635-1644`) |
| `mistralai-search-toolkit-plugins-vespa` | 0.0.13 | Vespa schema, index, queries and navigation (`uv.lock:1666-1675`) |
| `mistralai/search-starter-app` | upstream commit `919f2a6` | Copier origin of the Vespa and FastMCP scaffold (`docs/search-toolkit.md:32-35`) |
| `fastmcp` and `fastmcp-slim` | 3.4.7 | MCP server framework and installed implementation (`uv.lock:700-714`) |
| `mcp` | 1.29.1 | MCP wire types, transports and version negotiation, pulled by FastMCP (`uv.lock:1557-1565`) |
| Documentation corpus | `mistralai/platform-docs-public` commit `2e094f7` | Pinned source material for answers (D-001, D-009) |

The toolkit core and Vespa plugin are intentionally pinned to the same version. The plugin declares no lower bound on core, so independently resolved releases can import names missing from the older package (`pyproject.toml:10-14`). The toolkit's `__version__` incorrectly says `0.1.0`; its distribution metadata and lock both say `0.0.13` (`mistralai/search/toolkit/__init__.py:34`; `mistralai_search_toolkit-0.0.13.dist-info/METADATA:1-4`).

## `mistralai` Python SDK

The serving path constructs two `Mistral` clients. `chat_client()` uses the SDK's default Mistral endpoint unless `GLOSSATOR_CHAT_SERVER_URL` is set; then `server_url` points all chat work at that Mistral-compatible endpoint. `embedding_client()` always uses `MISTRAL_API_URL`, defaulting to `https://api.mistral.ai`, because the local llama.cpp chat server does not expose `mistral-embed` (`src/glossator/clients.py:32-39,73-94`; D-035c).

`MistralLLM` calls `client.chat.complete_async` for answer generation, the search-loop turns, query translation and rewrite, and the repository's listwise reranker. Requests carry messages, tools, `tool_choice`, sampling, reasoning effort, timeout and structured-output format; responses supply text, tool calls, usage and finish reason (`src/glossator/answer/llm.py:195-296,322-344`; `src/glossator/answer/service.py:59`; `src/glossator/retrieval/reranker.py:161-179,241-252`).

For Pydantic output, `response_format_from_pydantic_model()` converts the model
to the SDK's `json_schema` payload. Glossator still validates the returned JSON
and makes one repair call if it is invalid. A local server that cannot enforce a
schema can use `json_object`; that mode, and fenced JSON returned by llama.cpp,
are handled and recorded explicitly (`src/glossator/answer/llm.py:244-251,395-404,430-466`;
`src/glossator/answer/config.py:161-166`). Structured output is used for grounded
answers, reranker rankings, English renderings and optional query rewrites
(`src/glossator/answer/generation.py:57-64`; `src/glossator/retrieval/reranker.py:73-78,255-268`;
`src/glossator/answer/language.py:88-101,167-176,216-225`).

Embeddings reach the same SDK through the toolkit's `MistralEmbedder`, which calls `client.embeddings.create_async`. Both ingestion and retrieval inject the dedicated embedding client and raise the toolkit's default three retries to eight (`mistralai/search/toolkit/embedding/mistral_embedder.py:520-560`; `src/glossator/ingest/pipeline.py:330-334`; `src/glossator/retrieval/engine.py:218-226`; D-011a).

The direct SDK surface in `src/` is confined to the two client factories, serving chat
wrapper, type injection into ingestion and the embedding probe. Offline dataset generation and judging use a small `httpx`
OpenAI-compatible provider instead of the SDK
(`src/glossator/clients.py:17,73-94`; `src/glossator/answer/llm.py:16-25`;
`src/glossator/ingest/pipeline.py:19,312-334`;
`src/glossator/retrieval/probe.py:12-13,142`;
`src/glossator/eval/providers/wire.py:13-42`).

Two SDK behaviours required explicit handling. Connection failures can escape as
`httpx.TransportError`, while `NoResponseError` is a plain `Exception`; neither
is caught by a `MistralError` handler alone. The wrapper classifies and records
all three families (`src/glossator/answer/llm.py:51-54`). Also, `server_url`
routes the whole client rather than one API group, so chat and embeddings need
separate clients when generation is local (D-035c;
`tests/test_clients.py:65-76`).

## Models and account constraints

| Component | Configured model | Models used in evidence |
|---|---|---|
| Shipped embeddings | `mistral-embed`, 1,024 dimensions | `mistral-embed`; baseline variants also used `mistral-embed-dim128-2510` at 128 dimensions (`src/glossator/index/variants.py:48-70`; `mistralai/search/toolkit/embedding/models.py:110-113`) |
| Answer generation | `mistral-medium-2604`, the fixed Medium 3.5 id | Early smoke: `ministral-8b-2512`; primary API evaluations: `ministral-14b-2512`; Medium 3.5 was later measured by exact prompt replay on Mistral's API (D-017a, D-017c; `src/glossator/answer/config.py:16-19,103`) |
| Reranking | `mistral-small-2603` | Retrieval and answer evaluations used `ministral-14b-2512`; Small 4, the default, has never been run: the key had no quota for it until 12 September 2026 (`src/glossator/retrieval/config.py:18-19`; `docs/eval-status.md:52-54`) |
| Translation, rewrite and search loop | Same model as answer generation | Evaluations used `ministral-14b-2512` or the local `llamacpp/ministral3-14b`; all calls share `MistralLLM` (`src/glossator/answer/service.py:59`; `src/glossator/answer/language.py:167-176,216-225`; D-035c) |
| Dataset generation and answer judge | No shipped model | GLM models behind the swappable offline provider; these are evaluation dependencies, not serving dependencies (D-020, D-021) |

The project key listed 46 models, but until 12 September 2026 every Medium, Small and Magistral request returned
HTTP 429 with `x-ratelimit-limit-req-minute: 0`. Ministral 3, Codestral and
`mistral-embed` worked on the same key, so retries could not solve the Medium and Small
failures. No Mistral Large id was available (D-017a). The shipped defaults
remain Medium 3.5 for generation and Small 4 for reranking; before that date,
deployment had to point chat at a reachable server or those calls failed
(`docs/eval-status.md:52-54,219-222`).

## Search Toolkit and Vespa plugin

[The full assessment](search-toolkit.md) contains the feature-by-feature tables,
reproductions and measured costs. Keep `Pipeline`, frozen document models,
`MistralEmbedder` with more retries, Vespa migrations and CLI,
`DOCUMENT_PER_CHUNK`, custom root fields, the generated two-phase rank profile,
the query-builder path, positional navigation, and the retrieval metrics behind
a de-duplication wrapper. Glossator replaces the extractor, section chunker,
retriever, reranker, answer layer and ingestion safety check. It does not use
`QueryEngine`, `KeywordRetriever`, `RRFRanker`, either toolkit reranker, query
extension, or the in-memory semantic cache because their contracts do not fit
the Vespa and served-answer path (`docs/search-toolkit.md:128-201,603-617`).

Defects and omissions that affected the project:

- The starter leaves phase-one vector closeness at zero, ignoring the build
  check that names it, so candidate selection is BM25-only (D-012).
- Vespa implements only `VectorStoreIndex`, so the documented
  `KeywordRetriever` plus `RRFRanker` path cannot run (D-013).
- A named query profile makes `exclude_ids` and `extra_yql_filter` error, although
  the starter exposes `exclude_ids` while always selecting a profile (D-014).
- `LLMReRanker` makes one sequential call per candidate and discards its generated
  score; no Mistral reranker endpoint is available for the cross-encoder option
  (D-015).
- The toolkit has no answer generation, citation contract, groundedness control,
  streaming answer path or answer-quality evaluation (D-016).
- nDCG can exceed 1 when several chunks match one URL proxy; ranked proxies must
  be collapsed before scoring (D-016a).
- The embedder's three retries lost pages to free-tier 429s; eight retries and a
  sequential retry pass completed the corpus (D-011a, D-025a).
- Query-time ranking weights silently do nothing without an undocumented
  `_weight` suffix; HNSW is hard-coded to Euclidean distance; hit parsing drops
  Vespa `matchfeatures` (D-025, D-025a).
- Generated `services.xml` cannot set Vespa resource limits. A redeploy restored
  the 80% disk feed block, and delete-before-write left an index empty (D-025b).
- The generated app name rejects the template's underscore, schema and entrypoint
  collection defaults disagree, and the migration uses deprecated
  `embedding_dimensions` (D-022, D-022a, D-018).
- The toolkit skill's RRF advice is invalid for Vespa, README quickstarts omit the
  required extractor, and `read()` documents an inclusive end while implementing
  an exclusive one (D-018).
- Runtime `__version__` is `0.1.0` rather than the installed `0.0.13`
  (`mistralai/search/toolkit/__init__.py:34`;
  `mistralai_search_toolkit-0.0.13.dist-info/METADATA:1-4`).

## `mistral-common` tokenizer

The chunker, answer-context budget and listwise-reranker candidate truncation all
load the bundled `MistralTokenizer.v1()` and encode text without BOS or EOS
tokens (`src/glossator/ingest/chunker.py:246-277`;
`src/glossator/answer/context.py:129-137`;
`src/glossator/retrieval/reranker.py:236-238`). The toolkit also uses v1 for every
embedding model's request-size accounting
(`mistralai/search/toolkit/embedding/mistral_embedder.py:42-44`). Keeping these
four counters aligned makes chunk caps, prompt budgets and billed-token estimates
comparable (D-010a).

Tokenizer v1 loads `tokenizer.model.v1`, a SentencePiece file, and the installed
model map associates it with `mistral-medium-2312`, not the shipped
`mistral-medium-2604` (`mistral_common/tokens/tokenizers/mistral.py:159-166,449-465`).
The corpus-size analysis therefore loads Medium 3.5's Tekken tokenizer separately
from `mistralai/Mistral-Medium-3.5-128B` with
`MistralTokenizer.from_hf_hub`; those measurements are not mixed into serving
budgets (`src/glossator/eval/corpus_stats/__init__.py:1-15`; `src/glossator/eval/corpus_stats/tokens.py:9-14,21-47`).

## Copier starter template

The `mistralai/search-starter-app` template supplied toolkit ingestion, a Vespa
application and migrations, and a FastMCP surface for search, navigation, ingestion and
deletion (`docs/search-toolkit.md:17-35`). Glossator kept the pipeline abstraction,
Vespa migration and CLI machinery,
`DOCUMENT_PER_CHUNK`, custom metadata fields, `MistralEmbedder`, positional
navigation, and the retrieval metric arithmetic (`docs/search-toolkit.md:202-297`).

The collection name moved from inconsistent environment defaults into the index
package (D-022). The Vespa application is named `glossator`, separately from
underscore-bearing schema names, because the generated `mistral_docs` name fails
the toolkit's lowercase-letters-only validator (D-022a). The starter migration,
`get_index()`, chunker, retriever and MCP functions were rewritten around cited
section chunks and the query-builder path (`docs/search-toolkit.md:89-117,359-393`). The
MCP `ingest` and `delete` tools were removed: they admitted arbitrary page-level
chunks without URL, anchor or kind metadata into the serving index. Corpus writes
now go through the vendored adapter, manifest and link checks (D-026).

## MCP protocol stack

`src/entrypoints/mcp_server.py` creates a plain `FastMCP` instance, adds parameter
middleware and registers only `mistral_docs_search`, `mistral_docs_read_page` and
`mistral_docs_history` (D-044). It exposes stdio and Streamable HTTP and passes no
protocol revision. No MCP resources, answer tool or verification tool are registered
(`src/glossator/surface/names.py:4-6`; `src/entrypoints/mcp_server.py:126,154,204-208,266-278`).
FastMCP delegates initialisation to the official `mcp` low-level server
(`fastmcp/server/low_level.py:178-195`; `fastmcp/server/http.py:440-450`).

The installed MCP SDK declares `2025-11-25` as its latest protocol and supports
`2024-11-05`, `2025-03-26`, `2025-06-18` and `2025-11-25`
(`mcp/types.py:27-35`; `mcp/shared/version.py:1-3`). A server echoes a client's
requested version when it is supported and otherwise returns its latest version
(`mcp/server/session.py:175-199`). The installed MCP client requests that latest
version and rejects a response outside the same supported list
(`mcp/client/session.py:160-209`). Therefore two current installed endpoints
negotiate `2025-11-25`; an older compatible client can negotiate an older listed
revision.

Mistral Work's Connectors debugger reports a passing server as `Protocol 2025-11-25`.
The deployment probe now requests the same revision, prints the server's returned
revision and fails if it is missing or different (`docs/improvement-axes.md:415-419`;
`deploy/probe.py:16-30,48-74,92-111`). A newer specification revision, `2026-07-28`,
exists, but it is absent from the installed SDK's supported protocol constants; this
stack cannot negotiate it (`docs/improvement-axes.md:397-405`;
`mcp/shared/version.py:1-3`).

The protocol revision is not pinned by the starter template, FastMCP, or
glossator. The `mcp` SDK performs negotiation. FastMCP constrains that SDK to
`mcp>=1.24.0,<2.0`; `uv.lock` fixes the resolved installation at 1.29.1
(`fastmcp_slim-3.4.7.dist-info/METADATA:33-39,54-63`;
`uv.lock:1557-1559`). Glossator selects a client revision only in its deployment
probe; that does not pin the server.

Supporting a later wire revision requires an `mcp` release whose generated types
and supported-version list include it, a compatible FastMCP release, an updated
lock, a matching deployment-probe request, and contract tests for initialisation,
the three-tool discovery surface, schemas, annotations, errors, bearer
authentication and both transports. If that support first appears in `mcp` 2.x,
FastMCP must first remove or raise its current `<2.0` bound
(`fastmcp_slim-3.4.7.dist-info/METADATA:37,49,63`).

## Mistral Work and Connector constraints

Mistral Work does not expose MCP resources, prompt templates or dynamic tool
discovery. The current server therefore exposes only the three D-044 tools; shared
rules fit in server instructions, individual tool descriptions and the workspace
Skill (D-037a, D-029a, D-044;
`src/glossator/surface/descriptions.py:7-89`).

Work bills tool descriptions against every message's context and renders every
result verbatim. D-044 reduced that permanent surface to search, page reading and
history, with descriptions under 120 words and bounded outputs (D-029a, D-044).

When Work asks for confirmation, it adds the undeclared
`_confirmationReason` argument. Six calls failed before execution until the user
allowed a retry. `_ParamGuard` now removes underscore-prefixed host metadata before
validation; every tool also advertises read-only,
non-destructive, idempotent and closed-world annotations (D-037b;
`src/glossator/surface/params.py:61-80`; `src/entrypoints/mcp_server.py:129-154,194-208`).

## Outdated Mistral material excluded or corrected

- Mistral's `llms.txt` links were all dead and `llms-full.txt` omitted current
  Search Toolkit, Vibe and Medium 3.5 content because its generator reads a
  removed directory. The pinned documentation repository replaced it (D-001).
- The 2024 and 2025 cookbooks predate `mistralai` 2.x, Agents/Conversations and
  the Search Toolkit, so they are excluded rather than allowed to outrank current
  reference material (D-007, D-007a).
- The starter's deprecated embedding-dimension form, impossible Vespa app name,
  conflicting collection defaults and unusable MCP writes were replaced
  (D-018, D-022, D-022a, D-026).
- The deployment probe requests `2025-11-25`, prints the negotiated revision and
  rejects any other answer (`deploy/probe.py:16-30,48-74,92-111`; `mcp/types.py:27`).
