# Improvement axes

Where the documentation server loses value between the index and the consumer, ordered by how much
each change is expected to move the product as it is actually used: from a custom Connector in
Mistral Work, and from a coding agent such as Claude Code.

The evidence is three runs against the deployed server. A Mistral Work session on 2026-09-09 asked
two questions through the Connector. A Claude Code session on the same evening asked one question
with the connector attached. A blind consumer run
(`eval/runs/2026-09-09-1905-consumer-eval/records.jsonl`) put a small model at its lowest reasoning
setting through 60 questions with no tools and 38 with the retrieval tools, recording every tool
call. The measured surface costs come from `docs/context-surface-audit.md`.

| # | Axis | Where it bites |
|---|---|---|
| 1 | Declare the tools read-only so the host stops asking twice | Work |
| 2 | Make the workspace Skill the whole rulebook, and keep it current | Work |
| 3 | Ship a paste-ready `CLAUDE.md` block for coding agents | Claude Code |
| 4 | Write results a person can read, because Work shows them raw | Work |
| 5 | Add structured content where a host can render it, and never half of it | Work, later; Claude Code now |
| 6 | Budget the session, not the call | Both |
| 7 | Make continuation one opaque handle instead of a growing list | Both |
| 8 | Evaluate against a host that behaves badly, and count what breaks | Both |
| 9 | Adopt the surface mechanisms a sibling project already paid for | Both |

## 1. Declare the tools read-only so the host stops asking twice

**What to change.** Every tool carries MCP annotations: `readOnlyHint: true`, `idempotentHint:
true`, `destructiveHint: false`, and `openWorldHint: false` for everything except
`mistral_docs_answer`, which calls a model and is neither idempotent nor closed-world. The
annotations go on the registration alongside the title the tools already carry.

**Evidence.** In the Work session every one of six tool calls failed on its first attempt with a
validation error on `_confirmationReason`, an argument the host adds to the call that asks the user
for approval; the user then approved and the identical call succeeded. Work's approval model is
documented: "Before Work performs an action that touches an external system, it **stops and asks for
your approval**" and functions are "split into two groups", where "**Read-only tools**: tools that
retrieve information (get, list, search). Lower risk and usually safe to pre-authorize"
(`corpus/mistral-docs/vibe/work/safety-and-approvals.md`). Mistral's Connectors API already reads
the field: its tool listing endpoint can "Return a simplified payload with only name, description,
annotations, and a compact inputSchema"
(`corpus/mistral-docs/api/endpoint/beta/connectors.md`). The protocol defines the hints as behaviour
descriptions — "If true, the tool does not modify its environment" for `readOnlyHint`, "If true,
calling the tool repeatedly with the same arguments will have no additional effect on its
environment" for `idempotentHint`, and for `openWorldHint`, "If true, this tool may interact with an
'open world' of external entities. If false, the tool's domain of interaction is closed"
(https://modelcontextprotocol.io/specification/2026-07-28/schema). A documentation search over a
pinned commit is the closed-world, read-only, idempotent case exactly.

The argument itself is now dropped rather than rejected, and the tool announces what it ignored, but
that only converts a hard failure into an extra round trip. The annotation is what tells the host
the call never needed approval in the first place.

**Expected effect.** Six approval interruptions per two-question session drop toward zero. Every
interruption is a place where a user can decline and the answer is lost, and where a model that
sees an error may abandon the tool.

**How to measure.** Count approval prompts and first-attempt failures per session in hand tests
through the Connector, before and after, on the same two questions. In the blind consumer run,
count `tool_calls[].error` per arm; it is currently zero across 160 server calls, which is why this
defect was invisible until a real host connected (axis 8).

**Caveat.** Annotations are advisory: "NOTE: all properties in `ToolAnnotations` are **hints**. They
are not guaranteed to provide a faithful description of tool behavior" and "clients **MUST**
consider tool annotations to be untrusted unless they come from trusted servers"
(https://modelcontextprotocol.io/specification/2026-07-28/server/tools). A host may still prompt.
The change costs a few tokens and removes one of two possible causes.

## 2. Make the workspace Skill the whole rulebook, and keep it current

**What to change.** The Skill under `skills/mistral-docs/` names the tools `search`, `open`, `read`
and `cite`. Those names no longer exist: the server registers `mistral_docs_search`,
`mistral_docs_open_section`, `mistral_docs_read_page` and `mistral_docs_verify_quotes`. Beyond the
rename, the Skill should carry the rules that Work can never read anywhere else: what the corpus
covers and does not, the never-fabricate rule, the refusal path, the shape of the source block, and
an explicit instruction not to answer a Mistral question from the model's own knowledge even when
the connector was consulted.

Work's Connector page states the gap: custom MCP Connectors "don't yet support all MCP
capabilities", listing dynamic tool discovery, resources and automatic prompt templates
(`corpus/mistral-docs/vibe/work/connectors/mcp-connectors.md`). So the `glossator://guide` resource
never reaches Work, and the server instructions and tool descriptions are the only server-side
channel left. The Skill is the only client-side one, and it is the only place a rule can live
without being paid for on every session, because Work loads Skills progressively: "at session start,
Work loads only each Skill's name and description (~100 tokens each)", then "when a task matches a
Skill's description, Work reads the full `SKILL.md` instructions into context"
(`corpus/mistral-docs/vibe/work/skills.md`). That is the same progressive-disclosure shape Anthropic
describes for Agent Skills, where the frontmatter `description` is what "Claude will use ... when
deciding whether to trigger the skill in response to its current task"
(https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills,
2025-10-16).

The description is the trigger and deserves the prompt engineering: "Write descriptions that
describe **when** to use the Skill, not just what it does"
(`corpus/mistral-docs/vibe/work/skills.md`). A Skill also outranks the workspace preamble — "when a
Skill is active for a task, its instructions take precedence over your custom instructions" — while
custom instructions "don't change how tools execute"
(`corpus/mistral-docs/vibe/work/custom-instructions.md`), so anything procedural belongs in the
Skill and only tone belongs in the instructions.

**Evidence.** On question one the Work session called the connector and then answered from Work's
own knowledge about a GitHub connector, with no visible search result and no citation. On question
two it searched once, opened five sections, wrote a correct and well-structured answer, and never
called the verification tool. The blind consumer, driven by a Skill that prescribes the flow step by
step, called the server on 28 of 28 questions and the verification tool on 27 (D-040a). The
difference between the two is the imperative, not the model.

**Expected effect.** Question one becomes a search-and-cite answer rather than a recalled one, which
is the failure mode the whole product exists to remove. Question two gains verified quotes and a
source block.

**How to measure.** Over a fixed set of Work questions, record three rates: the connector was called
before the answer; the verification tool was called; the answer carries a source block whose links
resolve. Run once with the Skill disabled and once with it enabled. The same three rates already
exist as `mcp_called`, `cite_called` and `links` in the consumer records, so the harness needs no new
fields.

**A limit to state plainly.** Nothing in the corpus lets a Work Skill scope or force a Connector
call. `allowed-tools` is documented only for the coding CLI
(`corpus/mistral-docs/vibe/code/cli/skills.md`), and Work Skills have no equivalent field. The Skill
persuades; it does not bind.

## 3. Ship a paste-ready `CLAUDE.md` block for coding agents

**What to change.** Add a short block to the deployment instructions that a user pastes into their
own `CLAUDE.md`, on the model of the one Anthropic describes for its own agent: "CLAUDE.md files are
naively dropped into context up front, while primitives like glob and grep allow it to navigate its
environment and retrieve files just-in-time"
(https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents). The block is
the up-front half; the tools are the just-in-time half.

Four sentences, no more, because the same page warns that "Context, therefore, must be treated as a
finite resource with diminishing marginal returns" and asks for "the *smallest* *possible* set of
high-signal tokens that maximize the likelihood of some desired outcome":

1. For any question about Mistral models, the API, SDKs, pricing, limits, Studio, Work, Vibe or La
   Plateforme, call `mistral_docs_search` before answering, including when the answer seems known.
2. Quote only text a tool printed, and cite the `url#anchor` exactly as printed; never reconstruct a
   documentation URL.
3. Before showing quotes, pass the draft and its quotes to `mistral_docs_verify_quotes` and drop
   every marker it did not verify.
4. When the search does not find the answer, say the documentation does not cover it rather than
   answering from the model's own knowledge.

**Evidence.** Asked whether Mistral agents can automate GitHub, the Claude Code session answered
from its own knowledge, said no first-party GitHub connector existed, and searched only once the
user named the server. It then found `github_app` documented as one of the five auth methods a
Connector accepts (`corpus/mistral-docs/api/endpoint/beta/connectors.md`), and corrected itself. The
server was attached and idle; the first answer was wrong; one sentence of up-front context is what
separates the two.

**Expected effect.** The first question of a session gets a grounded answer instead of a recalled
one, without the user having to name the server.

**How to measure.** A fixed set of first-turn Mistral questions, asked in fresh sessions with and
without the block, scoring: was a server tool called before the answer, and was the answer correct.
The Work session's question one and the Claude Code session's question one are the seed cases: both
failed the first half.

## 4. Write results a person can read, because Work shows them raw

**What to change.** Work renders every tool result verbatim in the chat: the session displayed the
retrieval variant, the hybrid backend line, scores, byte offsets, chunk ids, the copy-paste
exclusion block and the `next:` hints, in the UI, to a human. Work documents this: every tool call
is shown with "**What outputs** came back"
(`corpus/mistral-docs/vibe/work/safety-and-approvals.md`). The `concise` format removes most of the
apparatus, but what remains — ids and `next:` lines — is addressed to the model and read by the
person.

The shape that serves both is a result whose first lines are the documentation itself, with the
machine handles below a short separator: heading path, quote, link; then the id and the `next:`
line. A reader who stops after the first block has the answer; a model that reads on has its handle.

**Evidence.** The Work transcript records the leak directly. The measured composition of a five-hit
search page before the trim was 34.0% snippet text and 66% apparatus
(`docs/context-surface-audit.md`), so the reader was seeing two lines of machinery for every line of
documentation.

**Expected effect.** A Work user who expands a tool call sees documentation, not a retrieval trace.
This is the difference between a connector that looks like a product and one that looks like a
debugging endpoint.

**How to measure.** Characters of documentation text over total characters, per result kind, from
the recorded consumer transcripts. Today the ratio is measurable per format; the target is a
majority of every result being text the reader could have read on the page.

## 5. Add structured content where a host can render it, and never half of it

**What to change.** Give `mistral_docs_search` and `mistral_docs_verify_quotes` an `outputSchema` and
return `structuredContent` beside the text: for search, a list of `{url, anchor, heading_path,
snippet, chunk_id}` plus the result counts and the continuation handle; for verification,
`{verified, failed, uncovered_markers, sources}`. Text stays primary — and every `note:` line, every
`next:` hint and every clamp announcement is mirrored into the structured payload rather than
existing only in the text.

**Evidence.** The protocol supports it — "**Structured** content is returned as a JSON value in the
`structuredContent` field of a result" — and names the benefits as "Enabling strict schema
validation of responses" and "Guiding clients and LLMs to properly parse and utilize the returned
data" (https://modelcontextprotocol.io/specification/2026-07-28/server/tools). But the same page
requires that "For backwards compatibility, a tool that returns structured content SHOULD also
return the serialized JSON in a TextContent block", so for a text-first consumer the payload is paid
twice.

The mirroring rule is not a precaution. A sibling project's third round of consumer evaluation, run
in August 2026 against a coding-agent client, found that the client rendered the structured payload
and discarded the text block entirely, which made every hint and every announcement in that text
invisible to that whole fleet of consumers. A server whose steering lives only in prose loses all of
it the moment a client prefers the JSON. That project now carries its notes inside the structured
content for exactly this reason.

There is also no evidence Work would use structured content today. The Work documentation defines a
`structuredContent` field only for Studio Workflows published into the chat
(`corpus/mistral-docs/studio/workflows/interacting-with-workflows/conversational_workflows/publish_in_vibe.md`),
never for Connector tools, and the Connector limitations list does not mention it either way. The
Connectors debugger states the contract it checks in terms of text: "Return bounded results with
valid `content` blocks" (`corpus/mistral-docs/studio/connectors/debugger.md`).

**Expected effect.** Nothing visible in Work today; a schema a host can render the day it supports
one; a machine-checkable contract for the harness in axis 8; and, immediately, insurance against a
client that reads JSON and throws the prose away. The verification tool is the better first
candidate because its result is small, so the duplicated text costs little, and its shape — verified,
failed, uncovered — is what a reader most wants drawn.

**How to measure.** Register the tools in Studio's Connectors debugger, whose passing report already
counts "`Tools`", "`Prompts`", "`Resources`" and "`Instructions`: server instructions when the MCP
server returns them" (`corpus/mistral-docs/studio/connectors/debugger.md`), and record whether the
Work rendering changes. Separately, assert in the harness that for every tool the set of hints
present in the text is also present in the structured payload; and read one consumer transcript per
client to see which of the two the client actually kept.

## 6. Budget the session, not the call

**What to change.** Every clamp today is per call: hits per search, chunks per read, characters per
diff. A session has no ceiling. Add a per-session accounting that the server can report — characters
or tokens returned so far — and lower the two ceilings that a single call can still blow through:
the page listing resource, and repeated whole-page reads.

**Evidence.** In the blind consumer run the server returned 708,408 characters over 38 questions,
about 18,600 characters — roughly 5,000 tokens — of tool output per question, from a median of four
calls. One resource read returned 34,676 characters; the page listing has 411 entries and renders to
about 34,900 characters of URLs and titles, so a single read of it costs a small model close to
9,000 tokens for a list it will use one line of. The largest single page read was 36,612 characters.

The cost of that is not linear. "LLMs have an 'attention budget' that they draw on when parsing
large volumes of context", and "as the number of tokens in the context window increases, the model's
ability to accurately recall information from that context decreases"
(https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents). Mistral states
the permanent half of the same cost for its own models: "Tool descriptions are included in the token
count. Long descriptions reduce available context for messages"
(`corpus/mistral-docs/resources/known-limitations.md`), alongside a ceiling of 128 tools per
request.

The remedy the guidance names is retrieval by handle rather than by bulk: agents "maintain
lightweight identifiers (file paths, stored queries, web links, etc.) and use these references to
dynamically load data into context at runtime using tools", which "enables progressive
disclosure—in other words, allows agents to incrementally discover relevant context through
exploration" (same source). The page listing is the opposite: a bulk dump offered as a starting
point. It should become a search over page titles, or a first page with a continuation, rather than
a resource that is read whole.

**Expected effect.** Lower input tokens per question at equal or better correctness. There is
already a hint that the direction is right: the arm with the server ran at a median of 15,735 input
tokens per question against 20,190 for the same model with no server, because targeted retrieval
displaced 180 web searches and fetches with 160 server calls.

**How to measure.** Median and maximum server characters per question, per tool, from the consumer
records; median input tokens per question per arm; correctness held constant by the judge. Those
three already exist in the record schema.

## 7. Make continuation one opaque handle instead of a growing list

**What to change.** Search continues today by echoing every chunk id already seen into a
copy-pasteable exclusion call, which grows linearly: after four rounds it carries twenty ids. Replace
the enumeration with a single opaque continuation token that the server expands, keeping the
exclusion semantics and dropping the transcript of them.

**Evidence.** The pattern being replaced is Mistral's own, and worth keeping in substance:
"`exclude_ids` makes corpus-level pagination possible: the agent can move through new results
instead of cycling over the same chunks"
(`corpus/mistral-docs/studio/search/agentic-search.md`). What is wrong is the encoding, not the
idea. MCP's own list pagination shows the shape: "The **cursor** is an opaque string token,
representing a position in the result set", servers "**SHOULD** provide stable cursors" and "handle
invalid cursors gracefully", and clients "**MUST** treat cursors as opaque tokens"
(https://modelcontextprotocol.io/specification/2026-07-28/server/utilities/pagination). Tool results
are not covered by that mechanism, so the token has to travel in the text and come back as an
argument — which the protocol also describes, in its guidance on state: a server that needs
continuity across calls "should do so by returning an explicit handle from a creation tool and
accepting that handle as an argument on subsequent calls", with handles that are opaque, because
"handles that encode internal structure invite parsing or guessing", and with expiry reported as a
tool error the model can act on
(https://modelcontextprotocol.io/specification/2026-07-28/server/tools).

The measured cost of the current encoding is 17.0% of a five-hit search page spent on the footer and
15.5% on ids and offsets (`docs/context-surface-audit.md`).

**Expected effect.** A search page whose size stops depending on how many searches came before it,
and a continuation the model cannot mistype into a valid-but-wrong call.

**How to measure.** Characters per search result against the round number, from the consumer
transcripts: today it rises, and it should become flat.

## 8. Evaluate against a host that behaves badly, and count what breaks

**What to change.** Four changes to the consumer evaluation.

*Count the errors.* The records carry `tool_calls[].error` and nothing aggregates it. The guidance
asks for exactly this: "we recommend collecting other metrics like the total runtime of individual
tool calls and tasks, the total number of tool calls, the total token consumption, and tool errors"
(https://www.anthropic.com/engineering/writing-tools-for-agents). Across 160 server calls in the
blind run the error count is zero — and a real host produced six failures in one two-question
session. A metric that reads zero when the deployed product is failing is not measuring the thing.

*Add a host-fidelity arm.* The harness is a well-behaved client that sends exactly the arguments in
the schema. Real hosts do not: Work adds `_confirmationReason`, and Mistral's own guidance for
server authors treats malformed and hostile input as the normal case, asking servers to "review tool
metadata for prompt injection" and to "Use `isError` for tool-level failures and JSON-RPC errors for
protocol-level failures" (`corpus/mistral-docs/studio/connectors/debugger.md`). The arm sends
unknown arguments, host-prefixed arguments, ids that were never printed, offsets that match nothing,
and out-of-range clamped values, and asserts that each returns a typed tool error naming the next
call — not a stack trace, and not a protocol error, because the protocol reserves those for what a
model cannot fix: tool execution errors "contain actionable feedback that language models can use to
self-correct and retry with adjusted parameters", and clients "**SHOULD** provide tool execution
errors to language models to enable self-correction"
(https://modelcontextprotocol.io/specification/2026-07-28/server/tools).

*Finish the arms and the consumers.* The recorded run has two arms, `A0` with no tools and `A1` with
the retrieval tools, one consumer, and no judge model set
(`eval/runs/2026-09-09-1905-consumer-eval/config.json`). D-040 specifies three arms and several
consumers; without them there is no basis for telling a capable consumer which arm to use.

*Classify defects by cause as well as severity, and re-run.* Severity is already fixed at three
levels — wrong or unreachable answer, extra calls, friction — and the fixed surface is re-run on
identical questions (D-032). What is missing is the cause, and a sibling project's five rounds of
consumer evaluation settled on five: a protocol bug; a mismatch between what a description promises
and what the payload delivers; an affordance trap, where the surface invites a call that cannot
work; a token-discipline violation; and the case where the consumer erred and the surface caught it,
which is a pass and worth recording as one. The last two categories are the ones a severity scale
alone hides. The transcripts are the input: "Read through your evaluation agents' reasoning and
feedback (or CoT) to identify rough edges. Review the raw transcripts (including tool calls and tool
responses)", and the analysis itself can be delegated — "You can even let agents analyze your
results and improve your tools for you"
(https://www.anthropic.com/engineering/writing-tools-for-agents).

**Evidence.** The two hand sessions found, in twenty minutes, three defects that 98 recorded cells
did not: the host argument, the raw rendering, and the unprompted answer from memory. The tasks that
find defects are the realistic ones — "Prompts should be inspired by real-world uses and be based on
realistic data sources and services" and "Strong evaluation tasks might require multiple tool
calls—potentially dozens" (same source).

**Expected effect.** The next surface defect is found by the harness rather than by the first person
to attach the Connector.

**How to measure.** Defects found per run, by severity, and the fraction found by the harness rather
than by hand. A re-run on byte-identical questions after a fix shows whether the fix held.

## 9. Adopt the surface mechanisms a sibling project already paid for

A sibling project runs a search-shaped MCP server over a private corpus and has taken its tool
surface through five rounds of consumer evaluation with agents from two vendors. Several of its
mechanisms answer defects that are latent here and have no analogue in the current surface. Each is
described by what it does, not by how it is written.

| Mechanism there | What it would mean here |
|---|---|
| A last-resort ceiling on the whole response, applied after every per-item and per-field clamp: whole results are dropped from the tail, at least one always survives, and a closing line says how many were dropped and which parameter to lower | `mistral_docs_read_page` has a per-call character budget; search, section reads and history do not. The 36,612-character page read and the 34,676-character resource read in the blind run are exactly what a final ceiling catches, and it catches the next one without anyone predicting its shape |
| Truncation centred on the matched text, sliding the window so a match near either end still spends the whole budget, with a marker on each cut side | A search snippet today can elide the very phrase the query asked about, and nothing says it did. This is a silent wrong answer, not a formatting complaint |
| A character budget where `0` means "no truncation", and a budget set too small is clamped *up* to a floor, because a window shorter than the truncation marker is worse than none | Gives a consumer a way to ask for the whole chunk without switching the whole result to the detailed format, which currently also restores scores and offsets it did not want |
| Columnar output with a caller-chosen field list, measured at roughly a quarter of the tokens of the same rows rendered as compact JSON, because the field names are written once | The page listing is 411 rows of url, title and kind — about 34,900 characters — and search hits are a table with a snippet attached. Both are shaped for columns |
| A total that does not move with the page size, from a bounded count probe with a floor; and a distinct rendering for a call past the last page that names the last valid offset rather than printing the offset as the total | Counts here are kept over considered from a fixed candidate pool, which is honest but changes with the request; and a call past the end has no rendering at all |
| One deep-link constructor, a small lead offset so the link lands just before the target, and a compact per-line citation under a single base link rather than a full URL per line | A verified quote prints a percent-encoded fragment URL of about 170 characters, twice — once in the verdict line and once under its source entry. One base link per page with a short per-quote suffix is the same navigation at a fraction of the payload |
| The read-only set of tools derived from the annotations rather than configured, so a tool that writes is masked on a public deployment the day it is added | Turns "the public deployment cannot change the corpus" from an environment variable into an invariant, on top of the annotations of axis 1 |
| A curated table of wrong-to-right parameter names resolved against the tool actually called, alongside string similarity, plus the enum's accepted values when the value is wrong too, and a unit hint when a name is right but its meaning is misread | The suggestions here come from string similarity alone. `top_k` to `max_hits` is a rename no fuzzy match will find, and it is the rename that just happened; an offset misread as a page number is the other standing confusion |
| A test that fails when a description exceeds the word budget or drops a required clause | Three descriptions were measured over the 120-word rule the set sets itself. A rule with no test is a preference |
| Verbs consolidated into one tool with a mode argument rather than one tool per verb, on the grounds that every tool is permanent context | Stepping to a neighbouring section is a mode of opening one, not a separate capability; folding it removes a tool description from every session |
| A minimal command-line client that calls one tool, prints the text blocks and the structured payload, and exits with a distinct code for a tool error and a transport failure | Axis 8 requires that no claim about the surface be accepted from a transcript. Reproducing one by hand needs a one-line command that prints the reproduction |

**Evidence.** Two of these were bought with defects rather than designed: the match-centred window
exists because a truncated result came back with the matched phrase cut out of the middle, and the
retry error that forbids reformulating a query exists because an earlier, friendlier wording taught
a consumer to abandon its search. The rule that a claim must be reproduced by hand with the command
printed, and the byte-identical re-run after fixes, are already carried over here (D-032, D-029);
the mechanisms above are the parts that were not.

**Expected effect.** No single one of these changes an answer. Together they remove the classes of
silent failure that a text surface produces: a payload that grows without a ceiling, a snippet that
drops the match, a count that changes meaning with the request, a rejected parameter with no route
to the right one, and a rule that no test enforces.

**How to measure.** Each has its own assertion, and they belong in the harness rather than in a
report: maximum characters returned by any single call; the proportion of search snippets containing
the matched phrase; the printed total held constant across page sizes; the proportion of rejected
parameters whose message names the correct one, measured against a fixed list of plausible wrong
names; and the description budget as a failing test rather than a measurement.

## Guidance dated outside the pinned corpus

The Mistral facts above are quoted from the vendored corpus at commit
`2e094f7bbe1395de4a738a3483def3573143d973`, dated 2026-09-07. Everything else is external and dated.

| Source | Date | Standing |
|---|---|---|
| https://modelcontextprotocol.io/specification/2026-07-28/server/tools and `.../schema` | 2026-07-28 | Current revision. The annotation hints, the `isError` split and the structured-content rules are unchanged from the 2025-06-18 revision the earlier audit quotes. New in this revision and used above: guidance on opaque state handles, and the note that clients aggregating several servers may hit a name collision "for example, two servers each exposing a `search` tool" |
| https://modelcontextprotocol.io/specification/2026-07-28/server/utilities/pagination | 2026-07-28 | Current. Covers list operations only, not tool results, which is why axis 7 carries the handle in the payload |
| https://www.anthropic.com/engineering/code-execution-with-mcp | 2025-11-04 | Consistent with the context-engineering post; its "150,000 tokens to 2,000 tokens" figure is for a tool-definition regime far larger than eight tools and is not claimed here |
| https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills | 2025-10-16 | Consistent with the corpus Skills page: both describe metadata-first discovery, a body loaded on match, and files loaded only as needed |
| https://mistral.ai/news/connectors/ | 2026-05-22 | Consistent with the corpus Connectors pages, including tool filtering by allowlist or blocklist |
| https://mistral.ai/news/vibe-agent/ | 2026-05-28 | Consistent; names Le Chat as the predecessor product |
| https://mistral.ai/news/le-chat-mcp-connectors-memories/ | 2025-09-02 | Outdated. It describes custom MCP connectors as a Le Chat feature, a year before the corpus documents them under Work, and predates the current limitations list. Not relied on |
| https://docs.mistral.ai/vibe/work/skills | live, footer 2026 | Same text as the corpus page, except that the live site says "Vibe Work" where the pinned page says "Work". A naming change with no behavioural content |
| https://docs.mistral.ai/models/best-practices/prompt-engineering | live, undated | Same guidance as the corpus page at `studio/conversations/chat-completion/prompting.md`, at a different path. The pinned path is the one cited above |
| https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview | live, undated | Moved: it redirects to `platform.claude.com`, and the ordered list of techniques it once carried now lives on a separate best-practices page. Nothing above depends on it |

One version fact matters for testing. Mistral's Connectors debugger reports a passing server as
`Protocol 2025-11-25` (`corpus/mistral-docs/studio/connectors/debugger.md`), so a Connector is
exercised against that revision, while the quotations above come from 2026-07-28. The three
mechanisms this rests on — tool annotations, `isError` for tool-level failures, and structured
content beside text — are present and unchanged in both.
