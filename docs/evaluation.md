# Evaluation

Every number names the model that produced it; run names are directories under
[`../eval/runs/`](../eval/runs/). `D-0xx` is a `DECISIONS.md` entry. The full
stage-by-stage table is [`eval-status.md`](eval-status.md).

## The story in one page

The shipped retrieval was chosen by a grid, not by taste: 294 generated
development questions through 13 configurations of chunking, ranking weights
and reranker ([`2026-09-09-0136-dev-grid-v2`](../eval/runs/2026-09-09-0136-dev-grid-v2/),
D-034). Section chunks with `mistral-embed` at 1,024 dimensions and vector-heavy
hybrid weights in Vespa won; a listwise reranker over 20 candidates (Ministral 3
14B in the run) took page recall@1 from 0.60 to 0.71. Whole-page chunks cannot
deep-link at all: section recall 0.

Six question sets cover what users actually do. 294 generated questions
(`dev.jsonl`, written by GLM 5.3 Flash) tune the system; a stratified 60 of them
held out from tuning and 85 questions mined from real GitHub issues by people
who had the SDK and still failed report it; 83 more mined from Vibe CLI, client-ts
and Stack Overflow issues await hand validation; 36 French translations and 105
deliberately degraded questions measure language and noise. The 85 mined
questions are the set the results lead with, because these are the questions
users actually had (D-038, D-038b).

With Ministral 3 14B generating and GLM 5.3 judging blind, the shipped
generated-answer path scores 0.93 judged correctness on the tuned 60
([`dev60-rerank`](../eval/runs/2026-09-09-0312-dev60-rerank/)), 0.84 on the
fresh 60 ([`fresh60-shipped`](../eval/runs/2026-09-09-1211-fresh60-shipped/))
and 0.76 on the 85 mined ([`mined-shipped`](../eval/runs/2026-09-09-1253-mined-shipped/)).
On badly worded questions it falls to 0.68
([`noisy-single`](../eval/runs/2026-09-09-1228-noisy-single/)); on French
questions rendered in English for retrieval it reaches 0.94
([`devfr-translated`](../eval/runs/2026-09-09-0420-devfr-translated/)).

Judging is calibrated, not assumed. GLM 5.3 is the primary judge; GLM 5.3 Flash
agrees at weighted kappa 0.87, Qwen 3.8 27B on the local server at 0.72, and
Ministral 3 14B is the strict outlier (D-021a, D-021c). Against 40 hand
labels by the author the primary judge agrees on 35, and every disagreement is in the
strict direction, so every correctness number here is a floor, not an average
(D-021b).

The failure analysis explains the gap between the sets: over 575 answers
(Ministral 3 14B, verdicts by GLM 5.3) generation causes 47% of failures,
retrieval misses 1 to 3% on well-formed questions and 12% on badly worded ones,
and context misses are zero everywhere. 53 of the 77 generation failures quoted
the gold section verbatim and still answered short: the model read the right
passage and stopped one parameter early
([`failure-analysis`](../eval/runs/2026-09-09-2028-failure-analysis/), D-042).

The generator is therefore not the ceiling. Mistral Medium 3.5 was measured by
replaying the recorded prompts of the four reporting runs through an
OpenAI-compatible gateway, so retrieval and context stayed byte-identical and
only the generator changed: correctness moved by at most four points, inside the
interval (0.93 to 0.91, 0.84 to 0.84, 0.76 to 0.80, GLM 5.3 blind), while
fabricated quotes halved and answers shortened by a third
([`2026-09-10-1615-medium35-replay-*`](../eval/runs/2026-09-10-1615-medium35-replay-mined-shipped/),
D-017b).

The MCP surface was evaluated with blind consumers, not proxies: 30 questions,
judged blind by GLM 5.3 ([`consumer-eval-v2`](../eval/runs/consumer-eval-v2/),
D-040b). Claude Sonnet at low effort answers 0.50 with no tools and 0.77 with
the retrieval tools, its links resolving 0.92 of the time instead of 0.35; the
server-side answer arm reaches 0.78 at three times the latency with a second
model in the loop. GPT luna, which carries its own web search, never called the
server in 60 cells: with nothing naming the server, a consumer with a competing
tool keeps its habit.

The time axis runs the same pipeline over eight biweekly snapshots of the docs
repository since 1 June 2026 ([`snapshot-labels`](../eval/runs/2026-09-09-1929-snapshot-labels/),
D-041a). The first thing it caught is a site-wide rename: 300 of 357 moved
sections are the same content under `/studio-api/...` before 15 August 2026 and
`/studio/...` after -- every method keyed on URLs, including gold links, lived
through it once. On the snapshot evaluation (local Ministral 3 14B Reasoning
generating, GLM 5.3 judging) correctness holds at 0.76 to 0.82 on questions the
snapshot answers ([`snapshot-eval`](../eval/runs/2026-09-09-1949-snapshot-eval/)).

Every run is a committed directory with its questions, retrieval hits, prompts,
raw model responses, citations, token usage, latency and errors, so any number
above can be traced to the model output that produced it (D-023). Recorded spend
is a lower bound for runs before 2026-09-09: reranker calls made before D-023b
and all embeddings are absent from their ledgers.

## In depth

### Answer evaluation

The answer evaluator runs each question through the selected strategies. Code
checks source matches, quote verification, refusal behaviour, usage, latency, and
cost. A blinded model judge scores correctness, groundedness, and citation
relevance.

```bash
make eval-answers dataset=eval/dev.jsonl name=answers-dev
make eval-answers dataset=tests/fixtures/answer-questions.jsonl \
  name=answers-fixture strategies=single_pass variant=sec128 limit=4
```

Three runs over the same 60 stratified development questions decided the
shipped strategy (`DECISIONS.md` D-033, D-033a, D-035). Answers were generated by
`ministral-14b-2512` and judged blind by `glm-5.3`; Mistral Medium 3.5, the
shipped generator, was measured on the same prompts by replay (D-017b, above).

| Run | Retrieval | Strategy | Correctness | Groundedness | Correct refusal | Gold URL cited | Gold anchor cited | Median latency | Prompt tokens | USD per question at Medium 3.5 prices |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `dev60-baseline` | migration weights, no reranker | `single_pass` | 0.81 | 0.75 | 0.82 | 0.70 | 0.50 | 3.0 s | 1.9k | 0.005 |
| `dev60-baseline` | migration weights, no reranker | `search_loop` | 0.93 | 0.81 | 0.88 | 0.78 | 0.40 | 7.4 s | 16.0k | 0.028 |
| `dev60-baseline` | migration weights, no reranker | `outline` | 0.65 | 0.65 | 0.72 | 0.42 | 0.18 | 3.7 s | 8.9k | 0.016 |
| `dev60-anchors` | same, after the anchor fallback | `single_pass` | 0.83 | 0.79 | 0.87 | 0.76 | 0.58 | 3.0 s | 2.0k | 0.005 |
| `dev60-rerank` | **shipped**: vector-heavy weights, reranker on | **`single_pass`** | **0.93** | 0.82 | **0.92** | 0.82 | **0.62** | 7.2 s | 2.0k | 0.005 |
| `dev60-rerank` | shipped | `search_loop` | 0.95 | 0.85 | 0.90 | 0.82 | 0.54 | 20.7 s | 14.8k | 0.026 |

Reranked single-pass retrieval closed most of the gap to the search loop, which
remains available as the thorough mode of `ask`.

Questions in another language are rendered in English for retrieval and answered
in their own language (`DECISIONS.md` D-008b). On 36 French questions
(`../eval/dev-fr.jsonl`) over the English corpus this took cited-URL match from 0.47
to 0.80 and correctness from 0.75 to 0.94, against 0.82 and 0.93 for the same
questions in English; the runs are
[`2026-09-09-0401-devfr-shipped`](../eval/runs/2026-09-09-0401-devfr-shipped/) and
[`2026-09-09-0420-devfr-translated`](../eval/runs/2026-09-09-0420-devfr-translated/).

Generated questions are well worded by construction, so they say little about
badly worded ones. `../eval/dev-noisy.jsonl` is the same 120 development questions
degraded into typos, bare keywords, vague wording, a wrong product term, or a
request buried in a user's context, with the gold sources and reference answers
unchanged. Noise costs the shipped single pass 19 points of correctness (0.87 to
0.68 on the same questions) and the search loop 16 (0.90 to 0.74), so the loop's
lead widens from 3 points to 6 at three times the latency and seven times the
prompt tokens. Rewording the question into the documentation's vocabulary before
retrieval (`AnswerConfig.rewrite_for_retrieval`, off by default, `--rewrite` on
the CLI and the answer eval) recovers 4 of the 19 points for a quarter of a
second and 275 prompt tokens, and costs 5 points on clean questions. The runs are
`../eval/runs/*-noisy-*/` and `../eval/runs/*-clean-*/`.

Recorded spend is a lower bound for runs made before 2026-09-09: their answer
evaluations built the search engine without a call recorder, so the listwise
reranker's calls are absent from their `calls.jsonl` and from their totals, and
embeddings are not priced per run at all. The console figure is the number of
record for spend. Runs from that date on share one recorder between the engine
and the answer model, so reranker calls land beside generation calls.

The stage-by-stage table of every shipped choice with its evidence is in
[`eval-status.md`](eval-status.md).
