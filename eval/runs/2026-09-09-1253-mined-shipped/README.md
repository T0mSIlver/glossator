# Answer evaluation: single_pass, search_loop on `sec1024`

**What this measures.** Which way of gathering evidence produces the best cited
answer, and what each one costs. Every question of the dataset is run through
each strategy against the same index, and every answer is scored twice: once by
code that can be re-run without a model, and once by a judge.

The deterministic checks are the primary numbers (D-016). They ask whether a
verified citation landed on a page the dataset names as gold, whether the quotes
the model wrote survive the verifier, whether the answer refused exactly the
questions the documentation cannot answer, and what the run spent. None of them
depends on a model's opinion, so none of them moves when a judge is swapped.

The judge answers what code cannot: whether the answer is *right*, whether its
claims are actually in the passages it cites, and whether each citation supports
the sentence it hangs on. It is shown the question, the reference answer, the
gold URLs, the answer and the cited passages verbatim -- and never which strategy
wrote the answer, so it cannot prefer one.

## Configuration

- Generation model: `ministral-14b-2512`
- Judge model: `glm-5.3` (answer-judge/v1)
- Index variant: `sec1024`, top_k 8, rerank True (ministral-14b-2512), context budget 6000 tokens
- Non-English questions rendered in English for retrieval: True
- Dataset: `eval/mined.jsonl`, sha256 `a276e09f853024f2647dad9d7f7c4c8c34e1754dafdf6a6dc4fbb994dfd5b2a2`
- Questions: 85; strategies: 2; records: 170
- Judge prompt hashes: {"judge_citation": "4603459ac6e543de", "judge_system": "b8150fdcba16ff47", "judge_user": "5bbdcd0c47bf9a06"}

`config.json` holds every other parameter, including the price table the USD
columns were computed with.

## Notes on this run

- The 85 questions mined from GitHub issues and agent sessions (D-038), never used for tuning, on the shipped configuration (S1024 · W-vec · R).

## Results

163 of 170 answers were judged by `glm-5.3` with thinking disabled. 7 answer(s) ended in an error and are recorded with it.

### Citations against the gold sources

Whether the answer's verified citations point at the pages the dataset says hold the answer. Unanswerable questions have no gold source, so they are left out of these tables rather than counted as failures. Capability questions also accept a named model's own card, and the last table counts matches that passed only because of that documented relaxation.

**cited_url_match** -- a verified citation names a gold page

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.88 | 1.00 | 0.73 | 0.00 | -- | **0.86** |
| `search_loop` | `ministral-14b-2512` | 0.85 | 0.50 | 0.45 | 1.00 | -- | **0.78** |

**cited_anchor_match** -- a verified citation names the gold section

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.55 | 0.50 | 0.73 | 0.00 | -- | **0.57** |
| `search_loop` | `ministral-14b-2512` | 0.40 | 0.25 | 0.36 | 1.00 | -- | **0.39** |

**gold_relaxed_matches** -- matches accepted through the model-card relaxation

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0 | 0 | 0 | 0 | 0 | **0** |
| `search_loop` | `ministral-14b-2512` | 0 | 0 | 0 | 0 | 0 | **0** |

### Citation verification

Whether the quotes the model wrote are in the sources it named. A fabricated rejection is a sentence that is not in the source at all; a cosmetic one is a quote too short to be evidence. The two are reported apart because averaging them hides both (D-027a). Distinct sources are counted beside the citations because an answer that cites `[1]` five times looks well cited and is not.

**citation_verification_rate** -- verified citations over emitted citations

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.86 | 0.74 | 0.86 | 0.00 | 0.91 | **0.85** |
| `search_loop` | `ministral-14b-2512` | 0.81 | 0.68 | 0.75 | 1.00 | 0.80 | **0.80** |

**unverified_citations_per_answer** -- rejected citations per answer

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.60 | 1.50 | 0.45 | 1.00 | 0.22 | **0.59** |
| `search_loop` | `ministral-14b-2512` | 0.83 | 1.50 | 0.73 | 0.00 | 0.67 | **0.82** |

**fabricated_per_answer** -- fabricated rejections per answer

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.60 | 1.50 | 0.45 | 1.00 | 0.22 | **0.59** |
| `search_loop` | `ministral-14b-2512` | 0.83 | 1.50 | 0.73 | 0.00 | 0.67 | **0.82** |

**cosmetic_per_answer** -- cosmetic rejections per answer

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| `search_loop` | `ministral-14b-2512` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

**distinct_sources_cited** -- different sources cited per answer

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.98 | 2.50 | 1.82 | 0.00 | 2.11 | **1.98** |
| `search_loop` | `ministral-14b-2512` | 2.02 | 2.50 | 1.36 | 3.00 | 2.44 | **2.01** |

**unmatched_markers_per_answer** -- `[n]` markers with no citation behind them

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.12 | 0.00 | 0.00 | 0.00 | 0.78 | **0.16** |
| `search_loop` | `ministral-14b-2512` | 0.12 | 0.00 | 0.00 | 0.00 | 0.44 | **0.13** |

### Refusal

`insufficient_evidence` should be set on exactly the questions the documentation cannot answer. This table scores both directions: a refused answerable question is as wrong as an answered unanswerable one.

**refusal_correct** -- the refusal flag matches the question

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.97 | 0.75 | 1.00 | 0.00 | 0.67 | **0.92** |
| `search_loop` | `ministral-14b-2512` | 1.00 | 1.00 | 1.00 | 1.00 | 0.33 | **0.93** |

### Judged quality

GLM's verdicts (D-021), reported beside the deterministic numbers and never merged into them. Correctness scores correct as 1, partial as 0.5, wrong as 0. Groundedness is the fraction of the answer's factual claims the cited passages support. Citation relevance is the fraction of citations that support the sentence they are attached to.

**correctness** -- correctness against the reference answer

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.81 | 0.62 | 0.82 | 1.00 | 0.67 | **0.79** |
| `search_loop` | `ministral-14b-2512` | 0.87 | 0.83 | 0.94 | 0.50 | 0.69 | **0.85** |

**groundedness** -- claims supported by the cited passages

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.91 | 0.88 | 0.96 | 0.00 | 0.65 | **0.88** |
| `search_loop` | `ministral-14b-2512` | 0.87 | 0.78 | 0.77 | 1.00 | 0.68 | **0.84** |

**citation_relevance** -- citations that support their sentence

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.95 | 0.88 | 1.00 | -- | 0.86 | **0.94** |
| `search_loop` | `ministral-14b-2512` | 0.97 | 0.67 | 0.92 | 1.00 | 0.75 | **0.93** |

### Effort

What each strategy spent to get there.

**latency_p50_s** -- median seconds per answer

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 12.9 | 11.4 | 10.3 | 8.5 | 10.8 | **12.0** |
| `search_loop` | `ministral-14b-2512` | 38.0 | 17.9 | 25.2 | 36.8 | 44.4 | **36.8** |

**latency_p95_s** -- 95th percentile seconds per answer

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 24.7 | 14.2 | 32.4 | 8.5 | 24.5 | **24.7** |
| `search_loop` | `ministral-14b-2512` | 66.1 | 83.1 | 48.6 | 36.8 | 67.9 | **66.7** |

**tokens_in** -- prompt tokens per answer

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 2525 | 2523 | 3330 | 1495 | 2423 | **2606** |
| `search_loop` | `ministral-14b-2512` | 17568 | 10543 | 16493 | 12316 | 21308 | **17433** |

**tokens_out** -- completion tokens per answer

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 562 | 562 | 566 | 185 | 292 | **530** |
| `search_loop` | `ministral-14b-2512` | 828 | 684 | 428 | 525 | 644 | **746** |

**usd** -- USD per question, at this run's price table

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | **0.00000** |
| `search_loop` | `ministral-14b-2512` | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | **0.00000** |

**reference_usd** -- USD per question at mistral-medium-2604 prices

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.0080 | 0.0080 | 0.0092 | 0.0036 | 0.0058 | **0.0079** |
| `search_loop` | `ministral-14b-2512` | 0.0326 | 0.0209 | 0.0280 | 0.0224 | 0.0368 | **0.0317** |

**tool_calls** -- tool calls per answer

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| `search_loop` | `ministral-14b-2512` | 4.72 | 2.00 | 4.00 | 3.00 | 5.33 | **4.54** |

**rounds** -- rounds per answer

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.98 | 1.00 | 1.00 | 1.00 | 1.00 | **0.99** |
| `search_loop` | `ministral-14b-2512` | 2.90 | 1.50 | 2.82 | 2.00 | 3.33 | **2.86** |

## Cost and latency

The run made 170 answers over 85 questions:
1703290 prompt and 108467 completion tokens,
0.0000 USD at this run's price table and
3.3684 USD at mistral-medium-2604 prices. Median
answer latency was 17.9 s, 95th
percentile 58.1 s.

`ministral-14b-2512` has no published price, so the USD column of this run is zero by construction. The row beside it prices the same recorded tokens at mistral-medium-2604 rates (D-017), which is what the shipped configuration would have cost.

Judging spent 798718 prompt and 47938 completion tokens over 163 call(s) (12689 of them reasoning tokens, with thinking disabled), at a mean of 9.8 s per judgement and 0 verdict(s) that did not validate. The z.ai coding plan bills nothing against the Mistral budget (D-020); the same judging on mistral-medium-2604 would have cost 1.5576 USD.

## Winner per metric

- `cited_url_match`: **single_pass**
- `cited_anchor_match`: **single_pass**
- `citation_verification_rate`: **single_pass**
- `unverified_citations_per_answer`: **single_pass**
- `refusal_correct`: **search_loop**
- `correctness`: **search_loop**
- `groundedness`: **single_pass**
- `citation_relevance`: **single_pass**
- `latency_p50_s`: **single_pass**
- `usd`: **single_pass**
- `reference_usd`: **single_pass**

`search_loop` answers best and `single_pass` is cheapest: the better answers cost 6.7x the prompt tokens of the cheaper strategy.

## Figures

`figures/` is regenerated from `metrics.json` by `make eval-report run=eval/runs/2026-09-09-1253-mined-shipped`.

- `citation-match.svg`: gold URL and gold anchor match, per strategy
- `verification-rate.svg`: verified, fabricated and cosmetic citations, per strategy
- `correctness.svg`: correct, partial and wrong, per strategy
- `groundedness.svg`: groundedness and citation relevance, per strategy
- `latency-vs-correctness.svg`: what the better answers cost in seconds
- `cost-per-question.svg`: USD per question at mistral-medium-2604 prices

## Files

- `config.json` -- every parameter, including the judge prompt hashes and the price table.
- `calls.jsonl` -- every model call, verbatim. `source` is `answer` for the serving
  path's calls and `judge` for the judge's.
- `records.jsonl` -- one line per (question, strategy): the answer, its verified and
  rejected citations, the whole trace including the context the model saw, the judge's
  input and raw output, usage, latency and cost. These rows are also the run's
  checkpoint: re-running with the same name skips the pairs already in them.
- `metrics.json` -- every number in the tables above.

## What it feeds

D-016 (which deterministic checks and which judged ones the answer eval reports),
D-027 (which strategy the shipped `ask` defaults to) and D-017a (the generation
model column, so this run and a Mistral Medium 3.5 re-run stay comparable).
