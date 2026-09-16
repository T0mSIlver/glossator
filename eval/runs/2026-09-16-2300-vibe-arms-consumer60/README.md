# Blind consumer evaluation

Weak models at low reasoning answer Mistral documentation questions over
glossator's MCP server, without being told they are evaluated. Three arms
per consumer: A0 answers from memory, A1 uses retrieval tools plus `cite`,
A2 asks the server for the answer. Shell tools stay available in every
arm, so the comparison is between whole agents.

## Protocol

- Questions: 60 fixed rows (40 stratified from eval/mined.jsonl and 20 from eval/dev-fresh60.jsonl, seed 0), identical in every arm and for every consumer.
- The prompt is one fixed sentence plus the question; nothing says
  evaluation and nothing names the tools.
- Consumers: vibe-medium35-high.
- Judge: zai:glm-5.3 (answer-judge/v2); citation passages shown to the judge are the verified
  quotes themselves, since a consumer answer keeps no served context.

## Notes

- vibe 2.25.4, --legacy-harness, model mistral-vibe-cli-latest (Medium 3.5), thinking high, Vibe plan key (plan_type chat)
- MCP arms call the deployed server https://glossator.tomvaucourt.com/mcp (all three tools, sec1024)
- shell arms run bash through eval/vibe-arms/sandbox-shell: no network, no environment, only the arm directory

## Cells

| cell | n | correctness | refusal | links resolve | on gold | mcp called | rerank asked | cite verified | tool calls | bad params | p50 s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| vibe-medium35-high / V0 | 60 | 0.23 | 0.77 | 0.07 | 0.02 | 0.00 | 0.00 | 0.00 | 2.53 | 0.00 | 7.27 |
| vibe-medium35-high / VA | 60 | 0.60 | 0.83 | 0.91 | 0.67 | 0.00 | 0.00 | 0.00 | 17.72 | 0.00 | 31.61 |
| vibe-medium35-high / VB | 60 | 0.63 | 0.83 | 0.97 | 0.85 | 0.00 | 0.00 | 0.00 | 10.77 | 0.00 | 11.68 |
| vibe-medium35-high / VC | 60 | 0.68 | 0.90 | 0.97 | 0.88 | 1.00 | 0.00 | 0.00 | 4.92 | 0.00 | 12.43 |
| vibe-medium35-high / VD | 60 | 0.64 | 0.83 | 0.97 | 0.81 | 1.00 | 0.00 | 0.00 | 6.27 | 0.00 | 13.18 |

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
