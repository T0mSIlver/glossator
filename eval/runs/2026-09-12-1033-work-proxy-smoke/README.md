# Work proxy evaluation

A Conversations-API agent stood in for a Mistral Work session: model
`mistral-small-latest` at `reasoning_effort: none`, the
mistral-docs Skill body plus the Work custom instructions as its
instructions, and the `mistral_docs` Connector as its only tool. One
unstored conversation per question; the consumer `judge` and `score`
subcommands read this directory unchanged.

## Protocol

- Questions: 2 rows from `eval/dev-smoke.jsonl` (sha256 c769d857e66c).
- Consumer: `work-proxy-mistral-small-latest-none` (arm A1), the same record shape as
  the blind consumer runs, so the metrics are comparable.
- Agent: `ag_01a0952f46dd725bb50c2f18f59e765c` on Connector `01a09051-8f79-73fa-a42b-c144932140c3`,
- deleted after the run.
- Timeout 300 s per question;
429 and 5xx retried with backoff; other failures are error rows.

## Cells

| cell | n | correctness | refusal | links resolve | on gold | mcp called | rerank asked | cite verified | tool calls | bad params | p50 s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| work-proxy-mistral-small-latest-none / A1 | 2 | -- | 1.00 | 1.00 | 0.50 | 1.00 | 0.00 | 0.00 | 3.50 | 0.00 | 6.56 |

Correctness is the blind judge's 1 / 0.5 / 0 mean where judged, else `--`.
Run `python -m glossator.eval.consumer judge --run <dir>` and then `score`
to fill it in; `score` also writes `metrics.json`, `figures/`, `defects.md`
and `samples.md` from the same records.

## Files

- `config.json`: the agent, model, effort, Connector and dataset behind
  the run, with the agent id and its deletion outcome.
- `questions.jsonl`: the question rows the run read.
- `records.jsonl`: one consumer record per question, the same shape as
  the blind consumer runs.
- `calls.jsonl`: every conversation response verbatim, one JSON object
  per question.
- `transcripts/<question_id>.md`: question, thinking, tool calls with
  arguments and results, and the answer.
- `README.md`: this file.
