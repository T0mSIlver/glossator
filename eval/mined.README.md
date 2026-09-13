# eval/mined.jsonl

Questions mined from real failures rather than written from a page. Each row starts from
a moment where someone could not use a Mistral product the documentation describes: an
issue on a public Mistral repository, or a coding-agent session on this machine that hit a
tool error, retried with different arguments, or said out loud what it had assumed. The
question keeps the person's wording where there was any; the gold sources were found by
reading `corpus/mistral-docs/`.

The evidence itself is not committed. `.agent-runs/stumbles.jsonl` holds one row per
stumble with the verbatim excerpt and the file or issue it came from, and
`.agent-runs/mined-validation.md` puts the excerpt, the question and the gold link on one
line each for review. Every question carries its stumble's identifier and reference in
`generator`, so a row can always be traced back to that evidence.

- Questions: 85 (single_page 60, api_reference 11, unanswerable 9, cross_page 4,
  capability 1); languages: {'en': 85}
- sha256: `a276e09f853024f2647dad9d7f7c4c8c34e1754dafdf6a6dc4fbb994dfd5b2a2`
- Sources: `github_issue` 54, `transcript` 31
- Issues by repository: `mistralai/client-python` 38, `mistralai/platform-docs-public` 10,
  `mistralai/cookbook` 4, `mistralai/mistral-common` 2
- Product areas: search_toolkit 29, document_ai 15, agents 6, audio 4, batch 3,
  chat_completions 3, structured_output 3, reasoning 3, rate_limits 3, function_calling 2,
  errors 2, sdk 2, deployment 2, and one each of platform, citations, prompt_caching,
  security, models, fine_tuning, vibe, tokenization
- Corpus: `corpus/mistral-docs`, validated with `validate_against_corpus`; zero issues

Nine questions are `unanswerable`: the stumble was real, the corpus does not cover it, and
the reference answer says what is missing. They are as much a part of the mining result as
the answerable ones, because they name the gaps a client's users fall into.

## Where the issues came from

Non-pull-request issues, open and closed, on `mistralai/client-python`,
`mistralai/client-js`, `mistralai/platform-docs-public`, `mistralai/cookbook` and
`mistralai/mistral-common`, cached under `.agent-runs/github/`:

```bash
gh api --paginate \
  "repos/<owner>/<repo>/issues?state=all&per_page=100&since=2025-03-01T00:00:00Z&sort=created&direction=desc" \
  --jq '.[]' > .agent-runs/github/<owner>_<repo>.json
```

`since` filters on last activity, so the fetch returns 272 non-PR issues of which 234 were
created inside the last eighteen months; only those were read. `mistralai/client-js` has
issues disabled and returned nothing. Kept were issues where a user could not find or
understand something the current documentation covers; dropped were SDK defect reports,
feature requests, and the ~110 automated `[Stale Cookbook]` rows that dominate the cookbook
repository by count.

## Where the sessions came from

`.local/transcripts/{claude,codex,opencode}/` (76 MB), searched with fixed-string patterns
and match caps, never a recursive grep:

```bash
rg -F -c --max-count N '<pattern>' .local/transcripts -g '*.json*'
```

Patterns that produced stumbles: `has no attribute`, `unexpected keyword`, `TypeError`,
`AttributeError`, `ValidationError`, `NotFound`, `429`, `x-ratelimit`, `SDKError`,
`embedding_dimensions`, `deprecated`, `exclude_ids`, `set_app_name`, `mistral-vespa`,
`docs.mistral.ai`, `the docs say`, `not documented`, `undocumented`. Matching regions were
read with a windowed extractor rather than by opening whole files: each match prints ±350
characters around the hit, and the excerpt in `.agent-runs/stumbles.jsonl` is trimmed from
that window to the part that shows the failure.

`~/.claude/projects/` was listed (159 directories) and the five whose paths or
first lines mention Mistral were searched. None held a usable stumble against a Mistral
product: the matches were either an unrelated application that merely depends on the SDK,
or a repository-setup session. Nothing from them is in this dataset.

## Constraints observed

No excerpt names a person, carries a handle or an email address, or reproduces session
content beyond the failure itself. Transcript references in this dataset are opaque session
identifiers; `.agent-runs/stumbles.jsonl` resolves each one to its file and line.

## Regenerating

The gold sources are hand-verified, so there is no regeneration command; the guard is
`tests/eval/test_datasets.py`, which validates every dataset under `eval/` against the
vendored corpus and fails if a gold URL or anchor stops resolving.
