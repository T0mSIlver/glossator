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
- Consumers: claude-haiku-low.
- Judge: not yet run (answer-judge/v2); citation passages shown to the judge are the verified
  quotes themselves, since a consumer answer keeps no served context.

## Notes

- Haiku 4.5 at low effort through headless claude, as the closest stand-in for Mistral Medium 3.5; the A1 arm reaches the public three-tool server (search with under, read_page, history) over the Cloudflare tunnel; no answer arm, the surface has no answer tool since D-044
- Questions: seed-0 sample of eval/mined-v2.jsonl plus dev-fresh60, so mined2-084 (the Search Toolkit evaluation question of D-044a) is in the set

## Cells

| cell | n | correctness | refusal | links resolve | on gold | mcp called | rerank asked | cite verified | tool calls | bad params | p50 s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| claude-haiku-low / A0 | 30 | -- | 0.77 | 0.44 | 0.43 | 0.00 | 0.00 | 0.00 | 6.30 | 0.00 | 30.71 |
| claude-haiku-low / A1 | 30 | -- | 0.80 | 0.89 | 0.78 | 1.00 | 0.00 | 0.00 | 4.90 | 0.07 | 15.68 |

Correctness is the blind judge's 1 / 0.5 / 0 mean where judged, else `--`.
`rerank asked` is the share of cells where the consumer asked search to
rerank: search ranks with the index alone otherwise, so the retrieval arm
spends no generation except on those cells.
`links resolve` is the share of answer URLs landing on a corpus page;
`on gold` the share of answerable answers naming a gold page. Refusal is a
heuristic over the answer text (declines for lack of documentation).

## Fragments

0 of 0 sampled fragment links found their text on the live page (seed 0).

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
