# Why this shape, and the alternatives considered

An MCP server with section search beat three alternatives: a one-million-token context costs more per question, server-side generation takes three times as long, and web search answers fewer questions correctly.

## Why an MCP server

The agent a user already works with, in Work, the Vibe CLI, Claude Code or a
bot, can query the documentation mid-task through an MCP server, at a pinned
commit and with the link to cite. The other options are a separate RAG system,
or a copy of the docs uploaded into every agent and every chat, where Work keeps
an uploaded file in that one chat's context. A coding agent can search an SDK
checkout for a parameter name, but product facts often live elsewhere.

This gap appears in `eval/mined.jsonl`. Of its 85 real questions, 54 came from
public GitHub issues, 40 on the SDK repositories and 14 on the documentation
and cookbook (`DECISIONS.md` D-038, D-039). The server
provides documentation from a pinned commit and prints, beside every section,
the link a reader opens. Snapshot search also shows when a fact changed.

## What decided the shape

Every choice is in `DECISIONS.md` with the run that decided it. The ones that
shaped the product:

| Decision | Evidence | Entry |
|---|---|---|
| Source the docs repo at a commit, not `llms.txt` or HTML | all 75 `llms.txt` links return 404; rendered HTML is 1.7% text with empty tab panels | D-001 |
| Section chunks with tested anchors, not whole pages | whole-page chunks cannot return an exact section link and use twice the answer prompt tokens | D-034, D-035a |
| Vector-heavy hybrid ranking inside Vespa | best exact-section retrieval on a 13-configuration grid over 294 questions | D-034 |
| The agent writes the answer; nothing generates inside the server | with retrieval tools a capable agent scored 0.77, against 0.78 for server-side generation at three times the latency and with a second model | D-040b, D-044 |
| No reranker on the agent path | it accounted for 91% of search latency and mainly improved which result ranked first, which an agent that reads several hits does not need | D-015b |
| Medium 3.5 as the answer model | replayed on Mistral's API, fabricated quotes per answer fell to 0.17 to 0.19 on four sets, less than half Ministral 3 14B's; judged correctness 0.90, 0.82, 0.73 and 0.65, within 0.03 of the 14B | D-017c |
| Three tools, no ids | 97% of pages fit one read under 8,000 tokens; the Work session never used the other five tools | D-043, D-044 |
| Every section has a key, and the link to cite is printed beside it | 1,823 of 4,016 headings have no anchor on the live site, so anchors alone collapse sibling sections and land a click far from the text; a text fragment is printed only when it moves the landing | D-047 |
| Read-only tool annotations | without them Work asks for approval on every call and a headless consumer never calls at all | D-037b, D-037c |
| A time axis: eight biweekly snapshots and a history tool | the docs renamed their API section in August; `-latest` aliases moved under users' feet | D-041, D-041a |
| GLM 5.3 as the primary judge | four judges were compared; the primary agreed with 35 of 40 labels by the author | D-021a, D-021b, D-021c |

## Why not the alternatives

### Put the whole documentation in a one-million-token context

The corpus contains 765,646 Medium 3.5 tokens (`eval/corpus-stats/`). It exceeds
Medium 3.5's 256,000-token context window. It fits Z.ai GLM 5.2's one-million-token
window. The vendored model card prices input at 1.4 USD per million tokens, or
0.14 USD for cached input. Reading the corpus would therefore cost about 1.07
USD uncached or 0.11 USD cached per question. Search returns a much smaller
passage with its exact section link.

### Generate inside the server

The FastAPI `POST /ask` route implements retrieval-augmented generation. The
repository keeps it as the measured baseline. On the same questions, Sonnet
scored 0.77 with the retrieval tools and 0.78 with `answer`. The
server-side answer took three times as long and required a second model
(D-040b). Replayed on Mistral's API in place of Ministral 3 14B, Medium 3.5
halved fabricated quotes on the same prompts, with judged correctness within
0.03 of the 14B on every set (D-017c).

The MCP server now provides the parts that calling agents lack: a pinned
corpus, tested section anchors and dated history. Agents can reformulate a
search with their own reasoning.

### Use Libraries or web search

Libraries index uploaded files for the `document_library` tool and cite the
document. They do not retain docs.mistral.ai section anchors, source commits or
dated changes. In the consumer run, built-in web search resolved 0.86 of its
links. Its correctness was 0.52 to 0.58, compared with 0.77 for the retrieval
tools (D-040b). The live site has no history, and all 75
links in its `llms.txt` returned 404 (D-001).

[`search-toolkit.md`](search-toolkit.md) records what the project kept,
wrapped, replaced or skipped. [`mistral-stack.md`](mistral-stack.md)
lists each Mistral dependency, its version and known defects.
[`eval-status.md`](eval-status.md) summarises the evaluation.
