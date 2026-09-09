# Blind consumer evaluation

Weak models at low reasoning answer Mistral documentation questions over
glossator's MCP server, without being told they are evaluated. Three arms
per consumer: A0 answers from memory, A1 uses retrieval tools plus `cite`,
A2 asks the server for the answer. Shell tools stay available in every
arm, so the comparison is between whole agents.

## Protocol

- Questions: 30 fixed rows (20 stratified from eval/mined.jsonl and 10 from eval/dev-fresh60.jsonl, seed 0), identical in every arm and for every consumer.
- The prompt is one fixed sentence plus the question; nothing says
  evaluation and nothing names the tools.
- Consumers: claude-sonnet-low.
- Judge: not yet run (answer-judge/v2); citation passages shown to the judge are the verified
  quotes themselves, since a consumer answer keeps no served context.

## Cells

| cell | n | correctness | refusal | links resolve | on gold | mcp called | rerank asked | cite verified | tool calls | bad params | p50 s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| claude-sonnet-low / A0 | 30 | -- | 0.70 | 0.35 | 0.48 | 0.00 | 0.00 | 0.00 | 3.93 | 0.00 | 22.14 |
| claude-sonnet-low / A1 | 30 | -- | 0.80 | 0.92 | 0.83 | 1.00 | 0.23 | 0.93 | 5.23 | 0.00 | 21.49 |
| claude-sonnet-low / A2 | 2 | -- | 1.00 | 0.78 | 0.50 | 1.00 | 0.00 | 0.00 | 2.00 | 0.00 | 51.79 |

Correctness is the blind judge's 1 / 0.5 / 0 mean where judged, else `--`.
`rerank asked` is the share of cells where the consumer asked search to
rerank: search ranks with the index alone otherwise, so the retrieval arm
spends no generation except on those cells.
`links resolve` is the share of answer URLs landing on a corpus page;
`on gold` the share of answerable answers naming a gold page. Refusal is a
heuristic over the answer text (declines for lack of documentation).

## Fragments

0 of 1 sampled fragment links found their text on the live page (seed 0).

## Files

- `records.jsonl`: one row per consumer, arm, question, with the answer
  text and the extracted links.
- `metrics.json`: the cells above in machine form.
- `defects.md`: every wrong turn with transcript path and severity.
- `samples.md`: ten questions with the three arms side by side.
- `figures/`: regenerated SVG charts.
- `transcripts/<consumer>/<arm>/<question>.jsonl`: the harness event
  stream behind every row, copied out of the consumer's scratch
  directory at collection time; each record names its own under
  `transcript`.
- `calls.jsonl`: the judge's calls, verbatim. The consumers' own model
  calls are their harnesses', not this server's.
- `records-a2-upstream-outage.jsonl`: rows collected while the answer server
  could not reach its model. They are out of the metrics, and the
  cells behind them are collected again once it can.
