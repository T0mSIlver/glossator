# Work proxy evaluation

A Conversations-API agent stood in for a Mistral Work session: model
`mistral-medium-3-5` at `reasoning_effort: high`, the
mistral-docs Skill body plus the Work custom instructions as its
instructions, and the `mistral_docs` Connector as its only tool. One
unstored conversation per question; the consumer `judge` and `score`
subcommands read this directory unchanged.

## Protocol

- Questions: 30 rows from `eval/demo.jsonl` (sha256 739c1066cb64).
- Consumer: `work-proxy-mistral-medium-3-5-high` (arm A1), the same record shape as
  the blind consumer runs, so the metrics are comparable.
- Agent: `ag_01a09ae0be0f716db2c45d4462dfb5b4` on Connector `mistral_docs_ca30`,
- deleted after the run.
- Timeout 300 s per question;
429 and 5xx retried with backoff; other failures are error rows.

## Cells

| cell | n | correctness | refusal | links resolve | on gold | mcp called | rerank asked | cite verified | tool calls | bad params | p50 s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| work-proxy-mistral-medium-3-5-high / A1 | 30 | 0.60 | 0.83 | 0.96 | 0.72 | 1.00 | 0.00 | 0.00 | 5.43 | 0.00 | 18.55 |

## Size

| questions | input tokens / question (mean) | (p50) | output tokens / question | tool results | chars / tool result | chars / question |
|---:|---:|---:|---:|---:|---:|---:|
| 30 | 7,358 | 4,950 | 1,098 | 163 | 4,309 | 23,411 |

Input tokens include the Connector's tool results as the API counts them;
characters are what the tools printed, before tokenization.

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
