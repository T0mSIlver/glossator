# Context surface audit

*This audit describes the eight-tool surface used from 2026-09-09 to 2026-09-10; D-044 cut it to three tools on 2026-09-10, so its `src/entrypoints/mcp_server.py` line references are historical.*

Everything a consumer of the MCP server sees — the server name, the instructions string, eight tool
descriptions, and the text every tool returns — measured against published guidance on tool design
and against what two real consumers did with the deployed server.

Measurements come from the live index at `localhost:18080` (`sec1024`, 4,440 chunks) on 2026-09-09,
counted with the Mistral v1 tokenizer that the chunker and the reranker use
(`glossator.answer.context.count_mistral_tokens`), and from the recorded run ledgers under
`eval/runs/`.

## What the surface costs today

Permanent context, sent on every session before a single call:

| Element | Tokens |
|---|---|
| Server instructions | 103 |
| Eight tool descriptions (name, docstring, signature) | 1,807 |
| Six tool descriptions, as deployed (`search`, `open`, `navigate`, `read`, `grep`, `cite`) | 1,379 |
| `glossator://guide` resource | 1,028 |

Per call, on the query `function calling tool choice` against a page of the function-calling guide:

| Call | Tokens returned | Wall time |
|---|---|---|
| `search(top_k=5)` | 1,687 | 5.70 s |
| `search(top_k=3)` | 1,078 | 5.74 s |
| `open(window=2)` | 1,901 | 0.02 s |
| `read()` whole page, `top_k=20` | 10,516 | 0.01 s |
| `grep(mode="phrase")` | 533 | 0.01 s |
| `navigate(direction="next", top_k=1)` | 249 | 0.00 s |
| `cite(draft, 1 quote)` | 250 | 0.00 s |
| `ask(strategy="single_pass")`, median of 85 answers | 772 | 12.0 s |
| `history(text=…)` | 161 | 1.04 s |
| `history(section=…)` | 267 | 0.74 s |

The `ask` figure is the median rendering over `eval/runs/2026-09-09-1253-mined-shipped/records.jsonl`
(285 tokens of answer, 342 of source list, about 45 of footer); its latency is the median
`latency_ms` in the same file. The blind consumer run agrees on scale: median tool output over 38
cells was 4,320 characters for `search`, 4,237 for `open`, 4,586 for `read` (36,612 at the maximum),
1,782 for `grep`, 1,064 for `cite` (`eval/runs/2026-09-09-1905-consumer-eval/records.jsonl`).

Where a `search` page of five hits spends its 1,689 tokens:

| Component | Tokens | Share |
|---|---|---|
| Snippets | 574 | 34.0% |
| Footer (`Results:`, `go deeper` line, `next:`) | 287 | 17.0% |
| Chunk ids and byte offsets | 262 | 15.5% |
| Per-hit truncation markers | 238 | 14.1% |
| Citation URLs | 148 | 8.8% |
| Score, kind, heading path | 109 | 6.5% |
| Header (`query:`, `variant`, `hybrid bm25+vector`, `hits:`) | 35 | 2.1% |

A third of the payload is documentation text. Two thirds is apparatus.

## Naming and discoverability

The server is registered as `FastMCP("glossator", …)`. Nothing in the name, and nothing in the
instructions string, says the word "Mistral". A Claude Sonnet session with the deployed connector
attached answered a Mistral question — "can you do github automation with mistral agents?" — from
memory, hedging about what the platform supports, and only searched the documentation after the user
typed "use glossator". The client had listed the server as `glossator-public`, and the consumer
harness in the blind run named the same tools `glossator_search`, `glossator_open`, `glossator_read`.
In every case the domain is invisible: a model choosing tools sees a codename, and the tool that
would have answered the question first is indistinguishable from any other search tool.

The guidance is explicit about both halves of the fix.

> "For example, namespacing tools by service (e.g., `asana_search`, `jira_search`) and by resource
> (e.g., `asana_projects_search`, `asana_users_search`), can help agents select the right tools at
> the right time." — https://www.anthropic.com/engineering/writing-tools-for-agents

> "When writing tool descriptions and specs, think of how you would describe your tool to a new hire
> on your team. Consider the context that you might implicitly bring—specialized query formats,
> definitions of niche terminology, relationships between underlying resources—and make it
> explicit." — https://www.anthropic.com/engineering/writing-tools-for-agents

The protocol supplies a display slot that the server does not use. `serverInfo` and every tool carry
an optional `title` alongside `name`:

> "`title`: Optional human-readable name of the tool for display purposes."
> — https://modelcontextprotocol.io/specification/2025-06-18/server/tools

> "Intended for UI and end-user contexts — optimized to be human-readable and easily understood, even
> by those unfamiliar with domain-specific terminology."
> — https://modelcontextprotocol.io/specification/2025-06-18/schema

Proposed surface, with the repository name unchanged:

| Slot | Today | Proposed |
|---|---|---|
| MCP server `name` | `glossator` | `mistral-docs` |
| MCP server `title` | absent | `Mistral documentation search` |
| Work connector name | operator's choice | `mistral_docs` (the field takes "a unique identifier (no spaces or special characters)") |
| Work connector description | absent | `Searches docs.mistral.ai at a pinned commit and verifies quoted sentences.` |
| `search` | `search` | `mistral_docs_search` |
| `open` | `open` | `mistral_docs_open_section` |
| `read` | `read` | `mistral_docs_read_page` |
| `grep` | `grep` | `mistral_docs_find_on_page` |
| `navigate` | `navigate` | `mistral_docs_step` |
| `ask` | `ask` | `mistral_docs_answer` |
| `cite` | `cite` | `mistral_docs_verify_quotes` |
| `history` | `history` | `mistral_docs_history` |

Three of the current names — `open`, `read`, `grep` — are the names of tools a coding agent already
has for its filesystem, and `search` is the name of its web search. A model that reaches for `read`
with a file path, or `grep` with a repository-wide pattern, has made a reasonable mistake with an
ambiguous name. Prefixing removes the collision; renaming to the resource (`open_section`,
`read_page`, `find_on_page`) removes the ambiguity even where a client strips prefixes.

The first line of every description must carry the domain too, because some clients render only that
line (D-029) and because the connector page's own description field is optional and often empty. The
first lines today open with the verb — "Search the indexed Mistral documentation by meaning or
keywords" names Mistral, but "Read a chunk and its neighbours in reading order, on its own page",
"Step to the chunk before or after a known position on one page", "Fetch the chunks of one page
between two offsets, verbatim", "Find an exact phrase or set of terms inside one indexed page" and
"Verify your own quotes against the chunks they claim to come from" name nothing a model can attach
to a question about Mistral.

Parameter names have the same problem in miniature:

> "In particular, input parameters should be unambiguously named: instead of a parameter named
> `user`, try a parameter named `user_id`."
> — https://www.anthropic.com/engineering/writing-tools-for-agents

`source_id` is the page URL — the `glossator://index` resource has to say so in a trailing comment,
"the url column is the source_id the tools take" — and `top_k` means hits in `search`, chunks in
`open` and `read`, matching chunks in `grep`, and steps in `navigate`. `page_url`, `max_hits`,
`max_chunks`, `max_matches` and `steps` say what they take.

## Result formats

What an agent needs from one hit is the citation target, a name it can reason about, enough text to
judge relevance, and one handle for the follow-up call.

> "Tool implementations should take care to return only high signal information back to agents. They
> should prioritize contextual relevance over flexibility, and eschew low-level technical
> identifiers." — https://www.anthropic.com/engineering/writing-tools-for-agents

> "Agents also tend to grapple with natural language names, terms, or identifiers significantly more
> successfully than they do with cryptic identifiers."
> — https://www.anthropic.com/engineering/writing-tools-for-agents

Against that standard, per hit:

| Field | Verdict |
|---|---|
| `url#anchor` | Keep. It is the citation and the deep link. |
| Heading path | Keep. It is the only natural-language identifier in the block. |
| Snippet | Keep, minus the heading path it repeats verbatim at the start of every chunk's text. |
| Chunk id | Keep, one per hit; it is the handle `open` and `cite` take. |
| `score 1.000 · 0.950 · 0.900 …` | Drop. With the reranker on, `score` is `(total - position) / total` — the rank position printed as a decimal (`retrieval/reranker.py`, `_scored`). It restates the `[n]` above it, and on `navigate` results, where nothing is ranked, it prints `score 0.000`, which reads as an assertion of irrelevance. |
| `offsets 14057..16095` | Drop from `search` and `open`. Only `read` and `navigate` take offsets, and only `read`'s range form needs them; the truncation marker that quotes them can carry them. |
| `variant sec1024 · hybrid bm25+vector` | Drop. The retrieval backend is not a fact about the documentation; `glossator://context` and `/health` already publish the variant. |
| `hits: 5/20 kept/considered` | Keep, one line. It is the honest-count rule of D-029 and it tells an agent whether a deeper page exists. |
| Per-hit truncation marker with a full paste-ready `read(...)` call | Compress. Five copies cost 238 tokens; one line at the end of the block naming the tool once does the same work. |
| `go deeper, copy-paste:` line enumerating every chunk id seen | Move to the detailed format. It reprints ids that are three lines above it, and it grows linearly: after four rounds it carries twenty ids, roughly 560 tokens. |

That trim takes a five-hit page from 1,687 tokens to roughly 700 without touching a character of
documentation text. It is in tension with one clause of D-029 — pagination lines are meant to be
copy-pasteable — which the `response_format` parameter resolves rather than overrides:

> "You can enable both by exposing a simple `response_format` enum parameter in your tool, allowing
> your agent to control whether tools return `"concise"` or `"detailed"` responses."
> — https://www.anthropic.com/engineering/writing-tools-for-agents

`response_format` is warranted on `search`, `open`, `read` and `grep`, whose payloads scale with the
corpus. `concise` returns url, heading path, snippet and chunk id. `detailed` adds offsets, the
kept/considered breakdown, the exclusion line and the full untruncated chunk. It is not warranted on
`navigate` (249 tokens), `cite` (250) or `history` (161–267): there is nothing to elide.

`read` is the outlier. Its default `top_k=20` returned 10,516 tokens for one page, and the blind
consumer hit 36,612 characters in a single call. Pages average about eleven chunks, so the default
usually means "the whole page, untruncated, however long it is".

> "We suggest implementing some combination of pagination, range selection, filtering, and/or
> truncation with sensible default parameter values for any tool responses that could use up lots of
> context." — https://www.anthropic.com/engineering/writing-tools-for-agents

> "If you choose to truncate responses, be sure to steer agents with helpful instructions. You can
> directly encourage agents to pursue more token-efficient strategies, like making many small and
> targeted searches instead of a single, broad search."
> — https://www.anthropic.com/engineering/writing-tools-for-agents

A default of `max_chunks=8` with a per-call character budget, a footer naming the offset to continue
from, and a description line that says to prefer `open` around a hit, keeps the tool useful and stops
one call from consuming a small model's whole window. `history`'s section form has the same shape of
hazard from the other end: `DIFF_MAX_CHARS = 6000` is a per-state clamp and the manifest holds eight
snapshots (`eval/snapshots/manifest.json`), so a heavily edited section can render eight diffs, about
15,000 tokens, with no per-call ceiling. The two measured calls returned 161 and 267 tokens because
the section did not change; the ceiling is what a consumer will eventually meet.

Proposed formats, in tokens for the calls measured above:

| Tool | Today | Concise | Detailed |
|---|---|---|---|
| `search`, 5 hits | 1,687 | ~700 | ~1,700 |
| `open`, window 2 | 1,901 | ~1,500 | ~1,900 |
| `read`, one page | 10,516 | ~3,500 (8 chunks) | today's, on request |
| `grep`, 5 matches | 533 | ~450 | 533 |
| `navigate` | 249 | 249 | — |
| `cite`, 1 quote | 250 | ~170 (see citations) | — |
| `ask` | 772 | ~600 (see citations) | — |
| `history` | 161–267 | capped per call | — |

One structural option stays open: the protocol allows a machine-readable result beside the text.

> "Structured content is returned as a JSON object in the `structuredContent` field of a result."
> — https://modelcontextprotocol.io/specification/2025-06-18/server/tools

> "For backwards compatibility, a tool that returns structured content SHOULD also return the
> serialized JSON in a TextContent block."
> — https://modelcontextprotocol.io/specification/2025-06-18/server/tools

Since the fallback duplicates the payload in text, structured content costs tokens rather than saving
them for a text-first consumer, and the Work connector page lists capabilities it does not yet
support. Text stays the primary rendering.

## Tool descriptions

Each description follows the same template: a two-line purpose, `USE WHEN`, `DO NOT USE` naming the
tool to use instead, `START WITH`, and an `Args` block. The template matches the guidance closely.

> "A good tool definition often includes example usage, edge cases, input format requirements, and
> clear boundaries from other tools."
> — https://www.anthropic.com/engineering/building-effective-agents

> "Tool definitions and specifications should be given just as much prompt engineering attention as
> your overall prompts." — https://www.anthropic.com/engineering/building-effective-agents

Per tool, against the rules the descriptions set themselves (D-029: under about 120 words, a first
line under 80 characters):

| Tool | Tokens | Words | First line | Notes |
|---|---|---|---|---|
| `search` | 285 | 135 | 64 chars | Over the word budget. `DO NOT USE` points at `ask`. |
| `open` | 178 | 104 | 66 chars | Within budget. |
| `navigate` | 240 | 121 | 63 chars | At the budget. Three positional ids to copy correctly. |
| `read` | 241 | 116 | 59 chars | Within budget; the default it recommends is the expensive one. |
| `grep` | 188 | 82 | 61 chars | Within budget. |
| `ask` | 253 | 141 | 65 chars | Over the budget; carries the strategy trade-off in prose. |
| `cite` | 247 | 140 | 66 chars | Over the budget. |
| `history` | 175 | 85 | 65 chars | Within budget. |

Three things a consumer can misread:

The `DO NOT USE` lines name tools that may not exist. `search` says "to answer a question end to end
(ask does that with verified citations)" and `cite` says "to get an answer written for you (ask does
that, with its own verified citations)". The deployed server registers `cite, grep, navigate, open,
read, search` and no `ask` (`GET /health`). The `next:` hints and truncation markers are routed
through `_hint()` precisely so they never name an unregistered tool; the descriptions are static
docstrings and are not. This is the trap D-029 describes — a pointer to a tool that answers "unknown
tool" — in the one place the rule was not applied.

`cite`'s purpose is stated as a conditional the model can decline. "USE WHEN: you wrote an answer
from search, open or read hits and need to check each quote before showing it" leaves the model to
decide whether it needs checking. The Sonnet session made three calls, wrote an answer with three
markers and a source list, and never called `cite`, though `cite` was registered. The blind consumer,
driven by a Skill that prescribes the flow step by step, called it on 27 of 28 questions (D-040a).
The difference is the imperative, not the model.

`ask`'s trade-off is stated in units a model cannot act on: "about 7 s" against "three times the
latency and five times the cost". The recorded medians are 12.0 s and $0.0011 for `single_pass`
against 36.8 s and $0.0037 for `search_loop` (`eval/runs/2026-09-09-1253-mined-shipped`, plus one
reranker call per round). Writing the seconds a consumer will actually wait is both more accurate and
shorter.

Two smaller notes. `navigate` requires `source_id`, `start_offset`, `end_offset` and `direction` — a
four-field handle copied from another result, where `open` needs one id.

> "Poka-yoke your tools. Change the arguments so that it is harder to make mistakes."
> — https://www.anthropic.com/engineering/building-effective-agents

A `chunk_id` plus `direction` would carry the same information with one field the model already holds
and cannot mistype into a valid-but-wrong position. And `open` shadows the Python builtin in the
module that defines it, which is a code hazard rather than a surface one, but the rename removes it.

## Server instructions and the guide resource

The Work connector page states the constraint:

> "Custom MCP Connectors don't yet support all MCP capabilities:" — dynamic tool discovery,
> resources, automatic prompt templates.
> — `corpus/mistral-docs/vibe/work/connectors/mcp-connectors.md`, "Current limitations"
> (https://docs.mistral.ai/vibe/work/connectors/mcp-connectors)

So in Work the instructions string and the tool descriptions are the whole surface. The protocol
gives the instructions field the weight this requires:

> "Instructions describing how to use the server and its features. This can be used by clients to
> improve the LLM's understanding of available tools, resources, etc. It can be thought of like a
> "hint" to the model. For example, this information MAY be added to the system prompt."
> — https://modelcontextprotocol.io/specification/2025-06-18/schema

Today's instructions are 103 tokens and spend one of their four clauses pointing at
`glossator://guide`, which Work cannot read. They never name Mistral, never say what the corpus
covers, and never say what to do when it does not cover the question. The 1,028-token guide holds all
three, plus a limits table that every description already carries and that every clamp announces at
the point of use, plus an error taxonomy that every error prints with its own `next:` line.

A budget of 250 tokens for the instructions, and 150 tokens per tool description, puts the permanent
context at about 250 + 6 × 150 = 1,150 tokens for the deployed six-tool set, against 1,482 today, and
makes it self-sufficient without the guide. What moves in:

| Moves into instructions | Why |
|---|---|
| What the corpus is: docs.mistral.ai guides, API reference and model cards, 411 pages at a pinned commit | The discoverability failure above; a model cannot choose a tool for a corpus it cannot name |
| The flow: search, then open or read the section, then verify with `cite` | Already there; keep |
| Never fabricate a URL, anchor or id; cite `url#anchor` exactly as printed | The one unforgivable sin (D-029) |
| Not the whole internet: say so when the corpus lacks the topic, never answer from memory | The refusal path, and the behaviour the Sonnet session skipped |
| Read the `next:` line of every response | Makes every other hint self-installing |

| Stays in the guide only | Why |
|---|---|
| The limits table | Each description states its own range; clamps announce themselves |
| The error taxonomy | Every error prints its code and its `next:` line |
| The resource list and the "there are exactly three" rule | Meaningless where resources cannot be read; keep for clients that can |
| The tool-flow table | The prose flow in the instructions covers it in a quarter of the tokens |

The guide stays registered: the blind consumer's client read MCP resources nine times across 28
questions, so it is not dead weight everywhere.

## Citations

Today an `ask` answer carries `[n]` markers in the prose and a source list built by
`sources_markdown`, one entry per distinct `(url, anchor)`, each entry naming its markers, the
canonical link, the heading path, and one fragment link per marker. `cite` returns the same list plus
one verdict line per quote. Two costs are structural: the source list is 342 of the 772 tokens of a
median `ask` rendering, and every verified quote prints its fragment URL twice — once in the verdict
line, once under its source entry. Fragment URLs are long by construction: the example measured here
is 170 characters of percent-encoded quote.

Neither surface emits a Markdown link. `sources_markdown` writes bare URLs after the marker numbers.
In Work the answer is rendered as Markdown, where a bare `[1]` is inert text and an unlinked URL is at
the mercy of the renderer's autolinking; in Claude Code a Markdown link renders as its text with the
URL in parentheses, which is what the Sonnet session produced by hand when it wrote its own sources
block.

| Shape | Verification | Readability in Work | Readability in Claude Code | Weak consumers |
|---|---|---|---|---|
| Markers plus a numbered list (today) | Unaffected: the verifier pairs quote to source in the structured citations, and a marker naming no verified quote is stripped (D-027b) | Nothing in the prose is clickable; the list is bare URLs | Readable; the list is scannable; nothing clickable | Cheapest to emit — a marker is two characters and the server builds the list |
| Inline Markdown links per claim, href = text fragment | Unaffected for the same reason, but the link now has to be placed on the right span, which is the misplacement problem restated | Every claim is clickable, which is the best case here | Every claim becomes `text (https://…170 chars…)`, and prose with four links becomes hard to read | Worst: the model must reproduce a 170-character percent-encoded URL inside prose, and a single mangled character breaks the link silently |
| Sources block only | Breaks: no claim-to-source pairing survives into the rendering, so "point at a sentence, click once, land on the paragraph" (D-027b) fails, and a reader cannot tell which of four sources backs which sentence | Clean and clickable | Clean | Easiest of all, and the least useful |

The recommendation is the first shape with the list rewritten: keep one `[n]` per claim, and render
the source list as Markdown links with a description, so the block reads like a web-search answer
while the markers keep the per-claim audit trail that verification exists to produce. The
misplacement complaint is a placement problem, not a marker problem, and the verifier already deletes
markers that name nothing; a sources-only answer would remove the evidence rather than fix it.

Under that shape `cite` returns:

- one Markdown source block, ready to paste, one entry per distinct `(url, anchor)`, each entry
  reading `[1][3] [Function calling — Five steps › Generate function arguments](fragment url) —
  "purpose (enum: 'fine-tune', 'batch', 'ocr', optional)"`, with the canonical `url#anchor` as the
  href only where no fragment could be built;
- the heading path for each entry, which `dedupe_sources` does not currently populate for `cite` —
  `entries_with_headings` is called only by the answer path, so `cite`'s entries render with no
  description at all today;
- failures in full, one line each, with the reason and what to do about it;
- successes as a single count line rather than a verdict line per quote carrying a duplicate fragment
  URL, which removes roughly 40% of the current `cite` payload;
- the uncovered-marker list and the `next:` line, unchanged.

`ask` renders the same block, so an answer written by the server and an answer written by a consumer
and verified by the server look identical to the reader.

## Cost and latency per call

Every `search` embeds the query and then makes one listwise reranker call over 20 candidates. Two
live calls, logged during this measurement:

| Measure | `search(top_k=5)` | `search(top_k=3)` |
|---|---|---|
| Reranker prompt / completion tokens | 4,111 / 407 | 4,111 / 415 |
| Reranker latency | 5.22 s | 5.55 s |
| Reranker cost | $0.000678 | $0.000679 |
| Total call | 5.70 s | 5.74 s |

The reranker is 91% of a search's latency and all of its marginal cost; `top_k` does not change
either, because the candidate pool is fixed at 20 independently of `limit` (D-029). The ledgers agree:
across the four reranking grid runs, 1,252 calls at 4,204–4,585 prompt tokens, median 4.3–4.8 s,
$0.00069 each (`eval/runs/2026-09-09-0020-dev-grid-rerank/calls.jsonl`,
`eval/runs/2026-09-09-0136-dev-grid-v2/calls.jsonl`); D-015a records mean 4,585/396 tokens and a
median 4.0 s against 7.6 ms without it.

Answer-level costs, from `records.jsonl` medians:

| Strategy | Run | Latency | Generation cost | Prompt / completion tokens | Reranker calls |
|---|---|---|---|---|---|
| `single_pass` | mined-shipped | 11.99 s | $0.00044 | 2,391 / 436 | 1 |
| `single_pass` | fresh60-shipped | 10.25 s | $0.00036 | 2,036 / 322 | 1 |
| `search_loop` | mined-shipped | 36.84 s | $0.00304 | 19,840 / 694 | up to 4 |
| `search_loop` | clean-loop | 30.19 s | $0.00226 | 14,365 / 500 | up to 4 |

So `ask(single_pass)` costs about $0.0011 all-in and twelve seconds; `ask(search_loop)` about $0.0058
and thirty to thirty-seven seconds. Reranker calls made during answer evaluations are absent from the
ledgers by construction (D-023b), which is why they are added here rather than read off.

For an agent, the reranker is charged per search and the agent searches several times: the blind
consumer's tool arm made a median of four tool calls per question and 64 searches over 28 questions,
with a median wall time of 30.3 s against 11.9 s for the same model with no server
(`eval/runs/2026-09-09-1905-consumer-eval/records.jsonl`). At four searches a session, the reranker
alone is about 21 s and $0.0027.

What it buys, measured on 294 dev questions (D-034, `eval/runs/2026-09-09-0136-dev-grid-v2`):

| Metric | `sec1024-vector-heavy` | `+rerank` | Delta |
|---|---|---|---|
| page recall@1 | 0.596 | 0.711 | +0.115 |
| page recall@5 | 0.863 | 0.920 | +0.057 |
| section recall@1 | 0.732 | 0.873 | +0.141 |
| section recall@5 | 0.937 | 0.979 | +0.042 |
| median ms | 9 | 4,392 | ×490 |

The gain is concentrated at rank 1, which is exactly the position `ask` depends on: `single_pass`
reads the top sections once and cannot recover from a bad order. An agent reads five hits and can
search again, so it collects the +0.04 to +0.06 at depth 5 and pays five seconds for it on every
query, including the exploratory ones and the exact-symbol lookups the product concedes to grep
(D-039).

The reranker therefore belongs unconditionally in `ask`, and by default but not unconditionally in
`search`. D-034 already documents `rerank=False` as a fast path at a median 9 ms, and the surface does
not expose it. A `rerank: bool = True` parameter, with a description line that says to set it false
for follow-up searches, exact identifiers and page-finding, turns a five-second fixed tax into an
agent's choice — and matches the guidance to steer agents toward "many small and targeted searches
instead of a single, broad search"
(https://www.anthropic.com/engineering/writing-tools-for-agents). The `note:` line already exists for
announcing what the server did, so a call that skipped reranking can say so.

The evaluation guidance names the metrics this section reports, and one it does not:

> "We recommend collecting other metrics like the total runtime of individual tool calls and tasks,
> the total number of tool calls, the total token consumption, and tool errors."
> — https://www.anthropic.com/engineering/writing-tools-for-agents

Tool errors are not counted anywhere. The consumer records carry `tool_calls` with an `error` field
and nothing aggregates it, so the rate at which a consumer sends an unknown chunk id, an offset pair
that matches nothing, or a parameter name the guard rejects, is unknown.

## Changes, ordered by expected effect

1. Rename the server to `mistral-docs`, give it the title `Mistral documentation search`, and open the
   instructions with the sentence that says it holds docs.mistral.ai.
2. Namespace every tool as `mistral_docs_*` by resource, and start every description's first line with
   what it searches or reads in Mistral's documentation.
3. Move the corpus scope, the never-fabricate rule, the refusal rule and the `next:` rule into the
   instructions string within a 250-token budget, since Work never reads the guide.
4. Cut the `search` hit block to `url#anchor`, heading path, snippet and chunk id, dropping the
   rank-derived score, the byte offsets, the backend line and four of the five truncation markers.
5. Render every source list as Markdown links with a heading-path description, and give `cite`'s
   entries the heading path the answer path already computes.
6. Lower `read`'s default to eight chunks under a per-call character budget, and give `history` a
   per-call ceiling instead of a per-snapshot one.
7. Add `response_format: "concise" | "detailed"` to `search`, `open`, `read` and `grep`, with
   `concise` as the default.
8. Add `rerank: bool = True` to `search`, so an agent can take the 9 ms path for follow-ups and exact
   identifiers instead of paying five seconds per query.
9. Print each verified quote's fragment link once, in the source block, and collapse the per-quote
   verdicts to failures plus a count.
10. Route the `DO NOT USE` clauses through the same registration check as the `next:` hints, so no
    description names a tool the deployment did not register.
11. Rename `source_id` to `page_url` and `top_k` to `max_hits`, `max_chunks`, `max_matches` and
    `steps` per tool, and let `navigate` take a `chunk_id` instead of three positional fields.
12. Trim `search`, `ask` and `cite` to the 120-word description budget the rest of the set keeps, and
    state `ask`'s strategy trade-off in measured seconds and dollars.
