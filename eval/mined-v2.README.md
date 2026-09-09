# eval/mined-v2.jsonl

A second set of questions mined from real failures, from sources the first mined set
(`eval/mined.README.md`) did not reach: public question-and-answer sites, and the Mistral
repositories the first pass skipped. Each row starts from a moment where someone could not
use a Mistral product the documentation describes; the question keeps the person's wording
where there was any, and the gold sources were found by reading `corpus/mistral-docs/`.

The evidence itself is not committed. `.agent-runs/mined-v2/stumbles.jsonl` holds one row
per stumble with the verbatim excerpt and the question, issue or session it came from, and
`.agent-runs/mined-v2/mined-v2-validation.md` puts the excerpt, the question and the gold
link on one line each for review. Every question carries its stumble's identifier and
reference in `generator`, so a row can always be traced back to that evidence.

- Questions: 83 (single_page 55, unanswerable 13, cross_page 11, api_reference 4);
  languages: {'en': 83}
- sha256: `1e19ef8f8f12dc7e923c4e196bf3111c386c92e46992d2a3dac8b9600fdfecb2`
- Sources: `github_issue` 55, `transcript` 10, `stack_overflow` 9, `hacker_news` 9
- Issues by repository: `mistralai/mistral-vibe` 31, `mistralai/client-ts` 20,
  `mistralai/mistral-inference` 3, `mistralai/mistral-finetune` 1
- Product areas: vibe 30, document_ai 10, agents 7, structured_output 5, deployment 4,
  errors 3, fine_tuning 3, models 3, security 3, platform 3, and two each of
  chat_completions, sdk, rate_limits, audio, workflows, plus tokenization and admin
- Corpus: `corpus/mistral-docs`, validated with `validate_against_corpus`; zero issues

Thirteen questions are `unanswerable`: the stumble was real, the corpus does not cover it,
and the reference answer says what is missing — the crawler's per-request page cap, a Code
Interpreter execution timeout, the `x-ratelimit-*` response headers, HTTP 411, an MCP tool
ceiling, `AGENTS.md` includes, the chat template `mistral-common` builds, and others.

The shape of this set differs from the first: the Vibe products (CLI, VS Code extension,
Vibe Code Web, admin config) are 30 of 83 questions, because the CLI repository is where
users write down what they could not find, and the first pass had a single Vibe question.

## Where the Stack Overflow questions came from

The public Stack Exchange API, no key, honouring the `backoff` field:

```bash
curl "https://api.stackexchange.com/2.3/search/advanced?site=stackoverflow\
&tagged=<tag>&fromdate=$(date -d 2025-01-01 +%s)&sort=creation&order=desc\
&filter=withbody&pagesize=100&page=<n>"
```

Only two of the candidate tags exist on Stack Overflow: `mistral-ai` (12 questions) and
`mistral-7b` (62); `mistral` and `mistralai` return nothing. The sweep also ran
`title=mistral` and full-text `q=` searches for "mistral api", "mistral ocr",
"mistral agents", "la plateforme mistral" and "mistral fine-tune", and fetched the answers
of the qualifying questions with `questions/<ids>/answers`. That is 26 distinct questions
since 2025-01-01, of which 9 have a Mistral product the corpus documents as their subject;
the rest are local inference of open weights with `transformers`, `trl`, Ollama or vLLM.

## Where the Hacker News questions came from

The Algolia HN API, `search_by_date`, comments and Ask HN / Show HN threads since
2025-01-01:

```bash
curl "https://hn.algolia.com/api/v1/search_by_date?query=<query>&tags=<comment|ask_hn>\
&numericFilters=created_at_i><epoch>&hitsPerPage=100&page=<n>"
```

Queries: "mistral api", "mistral ocr", "la plateforme", "mistral agents api",
"mistral fine-tuning", "mistral le chat", "mistral codestral", "mistral embed",
"mistral vibe", "mistral studio". 1,629 hits, filtered to the 156 that mention Mistral, ask
a question and name a platform term, of which 9 are usable. Hacker News is a thin source:
most matches are opinion about the company, model comparisons, or a product launch
mentioned in passing.

## Where the issues came from

Non-pull-request issues, open and closed, cached under `.agent-runs/github/`:

```bash
gh api --paginate \
  "repos/<owner>/<repo>/issues?state=all&per_page=100&since=<since>&sort=created&direction=desc" \
  --jq '.[]' > .agent-runs/github/<owner>_<repo>.json
```

`mistralai/mistral-inference` and `mistralai/mistral-finetune` from 2025-01-01 (19 and 5
non-PR issues created in range; both are largely local-GPU build failures and unrelated
posts), `mistralai/client-ts` from 2025-01-01 (52), and `mistralai/mistral-vibe` — the Vibe
CLI repository, found by listing `orgs/mistralai/repos` — from 2026-01-01 (309). The same
listing shows `mistralai/client-ts` exists and has issues enabled. Re-running the four
repositories the first pass read with `since=2026-09-08` returns no new non-pull-request
issue, so that part of the sweep contributed nothing.

Kept were issues where a user could not find or understand something the current
documentation covers; dropped were defect reports about the tools themselves, feature
requests, and posts unrelated to any Mistral product.

## Where the sessions came from

The consumer-evaluation transcripts under `eval/runs/consumer-eval-v2/transcripts/` and the
scratch root `/home/dev/.local/share/glossator-mcp-eval/`, which hold the same sessions.
The questions put to those agents came from the existing sets; what is mined here is what
each agent went looking for next and where it misread what it found — the queries it wrote
for itself, and the sentences in which it declared something undocumented. Both were
extracted mechanically from the recorded events rather than by reading transcripts:

```bash
python3 .agent-runs/mined-v2/consumer_queries.py eval/runs/consumer-eval-v2/transcripts
python3 .agent-runs/mined-v2/consumer_probe.py  eval/runs/consumer-eval-v2/transcripts
```

Claude Code transcripts under `/home/dev/.claude/projects/` newer than 2026-09-09 12:00
were listed (82 files across 20 directories) and searched with fixed-string patterns and
match caps. They yielded nothing: the sessions on this repository are the evaluation
pipeline's own work, and the Mistral-product text in them is the first mined set's own
evidence rather than a new stumble; the other recent projects run open weights locally with
third-party tooling.

## Duplicates dropped

Eight candidates were dropped as duplicates of `eval/mined.jsonl` — same fact, same page:
the npm supply-chain advisory versions (mined-037), querying a model deployed on Azure AI
(mined-038), the batch job's endpoint enum (mined-046), where the Vibe CLI finds skills
(mined-047), the OCR `pages` parameter and its zero-based numbering (mined-054), the model
capability matrix (mined-040), an `llms.txt` for the documentation (mined-078), and local
token counting before a request (mined-049). Two further candidates were dropped for having
no evidence behind the question once written, and one for asking a question the corpus
answers only through the same page and anchor an existing row already uses.

## Constraints observed

No excerpt names a person, carries a handle or an email address, or reproduces session
content beyond the failure itself. Session references in this dataset are run-relative
paths; `.agent-runs/mined-v2/stumbles.jsonl` resolves each one to its recorded events.

## Regenerating

The gold sources are hand-verified, so there is no regeneration command; the guard is
`tests/eval/test_datasets.py`, which validates every dataset under `eval/` against the
vendored corpus and fails if a gold URL or anchor stops resolving.
