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
- Consumers: claude-sonnet-low, codex-gpt-luna-low.
- Judge: zai:glm-5.3 (answer-judge/v2); citation passages shown to the judge are the verified
  quotes themselves, since a consumer answer keeps no served context.

## Notes

- The answer arm, and every search that asked for the reranker, ran against Ministral 3 14B Reasoning on the local server from 01:10 on 2026-09-10, with the sampling its model card asks for.
- The A0 and A1 cells were collected before that swap: on the A1 searches where the consumer asked for the reranker, the reranker was the instruct model.

## Cells

| cell | n | correctness | refusal | links resolve | on gold | mcp called | rerank asked | cite verified | tool calls | bad params | p50 s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| claude-sonnet-low / A0 | 30 | 0.50 | 0.70 | 0.35 | 0.48 | 0.00 | 0.00 | 0.00 | 3.93 | 0.00 | 22.14 |
| claude-sonnet-low / A1 | 30 | 0.77 | 0.80 | 0.92 | 0.83 | 1.00 | 0.23 | 0.93 | 5.23 | 0.00 | 21.49 |
| claude-sonnet-low / A2 | 30 | 0.78 | 0.80 | 0.90 | 0.78 | 1.00 | 0.00 | 0.00 | 2.33 | 0.00 | 74.37 |
| codex-gpt-luna-low / A0 | 30 | 0.58 | 0.80 | 0.86 | 0.87 | 0.00 | 0.00 | 0.00 | 2.03 | 0.00 | 14.68 |
| codex-gpt-luna-low / A1 | 30 | 0.52 | 0.80 | 0.85 | 0.78 | 0.00 | 0.00 | 0.00 | 2.20 | 0.00 | 13.58 |
| codex-gpt-luna-low / A2 | 30 | 0.58 | 0.83 | 0.81 | 0.74 | 0.00 | 0.00 | 0.00 | 2.23 | 0.00 | 14.58 |

Correctness is the blind judge's 1 / 0.5 / 0 mean where judged, else `--`.
`rerank asked` is the share of cells where the consumer asked search to
rerank: search ranks with the index alone otherwise, so the retrieval arm
spends no generation except on those cells.
`links resolve` is the share of answer URLs landing on a corpus page;
`on gold` the share of answerable answers naming a gold page. Refusal is a
heuristic over the answer text (declines for lack of documentation).

## Fragments

1 of 1 sampled fragment links found their text on the live page (seed 0).

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
- `records-a2-set-aside.jsonl`: answer-arm rows this run does not report,
  collected while the server could not reach its model or against a
  model since replaced. Their cells were collected again.
