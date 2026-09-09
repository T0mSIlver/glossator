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
answer and the cited passages verbatim. It sees no URL, page identifier, or strategy.

## Configuration

- Generation model: `ministral-14b-2512`
- Judge models: `zai:glm-5.3`, `zai:glm-5.3-flash`, `mistral:ministral-14b-2512`; primary first (answer-judge/v2)
- Index variant: `sec1024`, top_k 8, rerank True (ministral-14b-2512), context budget 6000 tokens
- Non-English questions rendered in English for retrieval: unknown
- Question reworded into the documentation's vocabulary for retrieval: unknown
- Dataset: `eval/dev.jsonl`, sha256 `acf3c2e148f1aa4036565ac03dd7a3a7e9bef5d0717529976ce9422b68b35490`
- Questions: 60; strategies: 2; records: 120
- Judge prompt hashes: {"judge_citation": "d1565f592953cb68", "judge_system": "3b300bf0bcd8ea7f", "judge_user": "4e976b80283c7257"}

`config.json` holds every other parameter, including the price table the USD
columns were computed with.

## Notes on this run

- Same 60 questions as dev60-baseline and dev60-anchors, on the shipped retrieval: section chunks at 1024 dimensions, vector-heavy weights, listwise reranker on (D-034); Ministral 14B generates and reranks because Medium 3.5 and Small 4 are rate-limited to zero on this key (D-017a).

## Results

120 of 120 answers were judged by the primary judge `zai:glm-5.3`. 0 answer(s) ended in an error and are recorded with it.

### Citations against the gold sources

Whether the answer's verified citations point at the pages the dataset says hold the answer. Unanswerable questions have no gold source, so they are left out of these tables rather than counted as failures. Capability questions also accept a named model's own card, and the last table counts matches that passed only because of that documented relaxation.

**cited_url_match** -- a verified citation names a gold page

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.90 | 0.80 | 0.70 | 0.70 | 1.00 | -- | **0.82** |
| `search_loop` | `ministral-14b-2512` | 0.70 | 0.90 | 0.90 | 0.70 | 0.90 | -- | **0.82** |

**cited_anchor_match** -- a verified citation names the gold section

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.40 | 0.80 | 0.70 | 0.70 | 0.50 | -- | **0.62** |
| `search_loop` | `ministral-14b-2512` | 0.00 | 0.90 | 0.60 | 0.70 | 0.50 | -- | **0.54** |

**gold_relaxed_matches** -- matches accepted through the model-card relaxation

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0 | 0 | 0 | 1 | 0 | 0 | **1** |
| `search_loop` | `ministral-14b-2512` | 0 | 0 | 0 | 1 | 0 | 0 | **1** |

### Citation verification

Whether the quotes the model wrote are in the sources it named. A fabricated rejection is a sentence that is not in the source at all; a cosmetic one is a quote too short to be evidence. The two are reported apart because averaging them hides both (D-027a). Distinct sources are counted beside the citations because an answer that cites `[1]` five times looks well cited and is not.

**citation_verification_rate** -- verified citations over emitted citations

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.74 | 0.76 | 0.97 | 0.85 | 0.93 | 0.92 | **0.86** |
| `search_loop` | `ministral-14b-2512` | 0.79 | 0.89 | 0.91 | 0.83 | 0.82 | 0.87 | **0.86** |

**unverified_citations_per_answer** -- rejected citations per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.90 | 0.80 | 0.10 | 0.30 | 0.20 | 0.10 | **0.40** |
| `search_loop` | `ministral-14b-2512` | 0.60 | 0.50 | 0.40 | 0.50 | 0.50 | 0.20 | **0.45** |

**fabricated_per_answer** -- fabricated rejections per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.90 | 0.80 | 0.10 | 0.30 | 0.20 | 0.10 | **0.40** |
| `search_loop` | `ministral-14b-2512` | 0.60 | 0.50 | 0.40 | 0.50 | 0.50 | 0.20 | **0.45** |

**cosmetic_per_answer** -- cosmetic rejections per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| `search_loop` | `ministral-14b-2512` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

**distinct_sources_cited** -- different sources cited per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.30 | 2.50 | 1.50 | 1.70 | 2.00 | 1.00 | **1.67** |
| `search_loop` | `ministral-14b-2512` | 1.10 | 3.30 | 1.60 | 2.50 | 1.40 | 1.20 | **1.85** |

**unmatched_markers_per_answer** -- `[n]` markers with no citation behind them

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.10 | 0.00 | 0.50 | 0.00 | 0.00 | 1.20 | **0.30** |
| `search_loop` | `ministral-14b-2512` | 0.00 | 0.30 | 0.00 | 0.00 | 0.00 | 0.40 | **0.12** |

### Refusal

`insufficient_evidence` should be set on exactly the questions the documentation cannot answer. This table scores both directions: a refused answerable question is as wrong as an answered unanswerable one.

**refusal_correct** -- the refusal flag matches the question

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.90 | 1.00 | 0.90 | 0.90 | 1.00 | 0.80 | **0.92** |
| `search_loop` | `ministral-14b-2512` | 0.90 | 0.90 | 1.00 | 1.00 | 0.90 | 0.70 | **0.90** |

### Judged quality

The primary judge's verdicts (D-021), reported beside the deterministic numbers and never merged into them. Correctness scores correct as 1, partial as 0.5, wrong as 0. Groundedness is the fraction of the answer's factual claims the cited passages support. Citation relevance is the fraction of citations that support the sentence they are attached to.

**correctness** -- correctness against the reference answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 0.85 | 0.85 | 0.95 | 1.00 | 0.90 | **0.93** |
| `search_loop` | `ministral-14b-2512` | 1.00 | 0.95 | 0.95 | 0.85 | 1.00 | 0.90 | **0.94** |

**groundedness** -- claims supported by the cited passages

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.85 | 0.83 | 0.80 | 0.71 | 0.94 | 0.77 | **0.82** |
| `search_loop` | `ministral-14b-2512` | 0.84 | 0.84 | 0.93 | 0.83 | 0.85 | 0.68 | **0.83** |

**citation_relevance** -- citations that support their sentence

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 0.78 | 0.91 | 0.94 | 1.00 | 1.00 | **0.93** |
| `search_loop` | `ministral-14b-2512` | 1.00 | 0.92 | 1.00 | 0.97 | 1.00 | 1.00 | **0.98** |

### Effort

What each strategy spent to get there.

**latency_p50_s** -- median seconds per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 7.3 | 7.6 | 7.6 | 6.5 | 7.9 | 6.8 | **7.2** |
| `search_loop` | `ministral-14b-2512` | 17.0 | 27.8 | 16.3 | 9.4 | 20.3 | 27.8 | **20.7** |

**latency_p95_s** -- 95th percentile seconds per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 20.4 | 12.0 | 10.9 | 44.0 | 12.4 | 8.3 | **12.0** |
| `search_loop` | `ministral-14b-2512` | 29.5 | 110.7 | 47.4 | 24.4 | 37.2 | 46.2 | **46.0** |

**tokens_in** -- prompt tokens per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1751 | 1839 | 2553 | 1888 | 2318 | 1658 | **2001** |
| `search_loop` | `ministral-14b-2512` | 8596 | 19337 | 13877 | 8221 | 14388 | 24141 | **14760** |

**tokens_out** -- completion tokens per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 284 | 481 | 365 | 204 | 353 | 184 | **312** |
| `search_loop` | `ministral-14b-2512` | 406 | 848 | 603 | 401 | 495 | 496 | **542** |

**usd** -- USD per question, at this run's price table

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00031 | 0.00035 | 0.00044 | 0.00031 | 0.00040 | 0.00028 | **0.00035** |
| `search_loop` | `ministral-14b-2512` | 0.00135 | 0.00303 | 0.00217 | 0.00129 | 0.00223 | 0.00370 | **0.00230** |

**reference_usd** -- USD per question at mistral-medium-2604 prices

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.0048 | 0.0064 | 0.0066 | 0.0044 | 0.0061 | 0.0039 | **0.0053** |
| `search_loop` | `ministral-14b-2512` | 0.0159 | 0.0354 | 0.0253 | 0.0153 | 0.0253 | 0.0399 | **0.0262** |

**tool_calls** -- tool calls per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| `search_loop` | `ministral-14b-2512` | 1.70 | 6.00 | 3.50 | 1.30 | 3.10 | 8.80 | **4.07** |

**rounds** -- rounds per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | **1.00** |
| `search_loop` | `ministral-14b-2512` | 1.80 | 3.30 | 2.70 | 1.70 | 2.90 | 4.00 | **2.73** |

## Agreement

Correctness is ordinal: wrong is 0, partial is 0.5, and correct is 1. Kappa uses quadratic weights. Exact agreement requires the same label.

### Judge pairs

| first judge | second judge | answers | quadratic-weighted kappa | exact agreement |
|---|---|---:|---:|---:|
| `zai:glm-5.3` | `zai:glm-5.3-flash` | 120 | 0.62 | 0.90 |
| `zai:glm-5.3` | `mistral:ministral-14b-2512` | 120 | 0.44 | 0.79 |
| `zai:glm-5.3-flash` | `mistral:ministral-14b-2512` | 120 | 0.42 | 0.78 |

### Krippendorff's alpha

| raters | ordinal alpha | pairwise exact agreement |
|---|---:|---:|
| configured judges | 0.42 | 0.82 |

### Judge means

| judge | answers | mean correctness | human-labeled answers |
|---|---:|---:|---:|
| `zai:glm-5.3` | 120 | 0.93 | -- |
| `zai:glm-5.3-flash` | 120 | 0.94 | -- |
| `mistral:ministral-14b-2512` | 120 | 0.85 | -- |

## Cost and latency

The run made 120 answers over 60 questions:
1005667 prompt and 51215 completion tokens,
0.1585 USD at this run's price table and
1.8926 USD at mistral-medium-2604 prices. Median
answer latency was 9.4 s, 95th
percentile 40.9 s.

Judging spent 762726 prompt and 79378 completion tokens over 360 call(s) (9958 of them reasoning tokens, with thinking disabled), at a mean of 8.7 s per judgement and 0 verdict(s) that did not validate. The z.ai coding plan bills nothing against the Mistral budget (D-020); the same judging on mistral-medium-2604 would have cost 1.7394 USD.

## Winner per metric

- `cited_url_match`: **single_pass**
- `cited_anchor_match`: **single_pass**
- `citation_verification_rate`: **search_loop**
- `unverified_citations_per_answer`: **single_pass**
- `refusal_correct`: **single_pass**
- `correctness`: **search_loop**
- `groundedness`: **search_loop**
- `citation_relevance`: **search_loop**
- `latency_p50_s`: **single_pass**
- `usd`: **single_pass**
- `reference_usd`: **single_pass**

`search_loop` answers best and `single_pass` is cheapest: the better answers cost 7.4x the prompt tokens of the cheaper strategy.

## Figures

`figures/` is regenerated from `metrics.json` by `make eval-report run=eval/runs/2026-09-09-0312-dev60-rerank`.

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
