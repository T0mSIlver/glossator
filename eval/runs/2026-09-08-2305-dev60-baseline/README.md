# Answer evaluation: single_pass, search_loop, outline on `sec1024`

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
- Index variant: `sec1024`, top_k 8, context budget 6000 tokens
- Dataset: `eval/dev.jsonl`, sha256 `acf3c2e148f1aa4036565ac03dd7a3a7e9bef5d0717529976ce9422b68b35490`
- Questions: 60; strategies: 3; records: 180
- Judge prompt hashes: {"judge_citation": "4603459ac6e543de", "judge_system": "b8150fdcba16ff47", "judge_user": "5bbdcd0c47bf9a06"}

`config.json` holds every other parameter, including the price table the USD
columns were computed with.

## Notes on this run

- Baseline: shipped retrieval defaults (no reranker, no floors), Ministral 14B because Medium 3.5 is rate-limited to zero on this key (D-017a).

## Results

180 of 180 answers were judged by `glm-5.3` with thinking disabled. 0 answer(s) ended in an error and are recorded with it.

### Citations against the gold sources

Whether the answer's verified citations point at the pages the dataset says hold the answer. Unanswerable questions have no gold source, so they are left out of these two tables rather than counted as failures.

**cited_url_match** -- a verified citation names a gold page

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.80 | 1.00 | 0.70 | 0.10 | 0.90 | -- | **0.70** |
| `search_loop` | `ministral-14b-2512` | 0.80 | 1.00 | 0.70 | 0.50 | 0.90 | -- | **0.78** |
| `outline` | `ministral-14b-2512` | 0.80 | 0.40 | 0.00 | 0.50 | 0.40 | -- | **0.42** |

**cited_anchor_match** -- a verified citation names the gold section

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.30 | 1.00 | 0.60 | 0.10 | 0.50 | -- | **0.50** |
| `search_loop` | `ministral-14b-2512` | 0.30 | 1.00 | 0.10 | 0.50 | 0.10 | -- | **0.40** |
| `outline` | `ministral-14b-2512` | 0.00 | 0.40 | 0.00 | 0.50 | 0.00 | -- | **0.18** |

### Citation verification

Whether the quotes the model wrote are in the sources it named. A fabricated rejection is a sentence that is not in the source at all; a cosmetic one is a quote too short to be evidence. The two are reported apart because averaging them hides both (D-027a). Distinct sources are counted beside the citations because an answer that cites `[1]` five times looks well cited and is not.

**citation_verification_rate** -- verified citations over emitted citations

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.83 | 0.83 | 0.89 | 0.79 | 0.93 | 1.00 | **0.86** |
| `search_loop` | `ministral-14b-2512` | 0.89 | 0.74 | 0.90 | 0.78 | 0.75 | 1.00 | **0.82** |
| `outline` | `ministral-14b-2512` | 0.89 | 0.89 | 1.00 | 0.80 | 0.86 | 1.00 | **0.89** |

**unverified_citations_per_answer** -- rejected citations per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.50 | 1.00 | 0.30 | 0.40 | 0.20 | 0.00 | **0.40** |
| `search_loop` | `ministral-14b-2512` | 0.30 | 1.50 | 0.40 | 0.50 | 0.60 | 0.00 | **0.55** |
| `outline` | `ministral-14b-2512` | 0.30 | 0.40 | 0.00 | 0.30 | 0.40 | 0.00 | **0.23** |

**fabricated_per_answer** -- fabricated rejections per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.50 | 1.00 | 0.30 | 0.40 | 0.20 | 0.00 | **0.40** |
| `search_loop` | `ministral-14b-2512` | 0.30 | 1.50 | 0.40 | 0.50 | 0.60 | 0.00 | **0.55** |
| `outline` | `ministral-14b-2512` | 0.30 | 0.40 | 0.00 | 0.30 | 0.40 | 0.00 | **0.23** |

**cosmetic_per_answer** -- cosmetic rejections per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| `search_loop` | `ministral-14b-2512` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| `outline` | `ministral-14b-2512` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

**distinct_sources_cited** -- different sources cited per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.20 | 3.60 | 1.80 | 1.50 | 1.50 | 0.60 | **1.70** |
| `search_loop` | `ministral-14b-2512` | 1.20 | 3.30 | 2.00 | 1.80 | 1.20 | 1.10 | **1.77** |
| `outline` | `ministral-14b-2512` | 0.90 | 1.70 | 0.60 | 1.10 | 0.90 | 0.60 | **0.97** |

**unmatched_markers_per_answer** -- `[n]` markers with no citation behind them

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00 | 0.00 | 0.40 | 0.40 | 0.00 | 0.80 | **0.27** |
| `search_loop` | `ministral-14b-2512` | 0.00 | 0.20 | 0.20 | 0.00 | 0.00 | 1.00 | **0.23** |
| `outline` | `ministral-14b-2512` | 0.20 | 0.60 | 0.20 | 0.00 | 0.40 | 1.00 | **0.40** |

### Refusal

`insufficient_evidence` should be set on exactly the questions the documentation cannot answer. This table scores both directions: a refused answerable question is as wrong as an answered unanswerable one.

**refusal_correct** -- the refusal flag matches the question

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 1.00 | 0.60 | 0.60 | 0.90 | 0.80 | **0.82** |
| `search_loop` | `ministral-14b-2512` | 0.90 | 1.00 | 0.90 | 0.80 | 1.00 | 0.70 | **0.88** |
| `outline` | `ministral-14b-2512` | 0.80 | 0.70 | 0.30 | 0.80 | 0.80 | 0.90 | **0.72** |

### Judged quality

GLM's verdicts (D-021), reported beside the deterministic numbers and never merged into them. Correctness scores correct as 1, partial as 0.5, wrong as 0. Groundedness is the fraction of the answer's factual claims the cited passages support. Citation relevance is the fraction of citations that support the sentence they are attached to.

**correctness** -- correctness against the reference answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.90 | 0.65 | 0.60 | 0.80 | 1.00 | 0.90 | **0.81** |
| `search_loop` | `ministral-14b-2512` | 1.00 | 0.95 | 0.95 | 0.80 | 0.95 | 0.95 | **0.93** |
| `outline` | `ministral-14b-2512` | 0.75 | 0.60 | 0.15 | 1.00 | 0.60 | 0.80 | **0.65** |

**groundedness** -- claims supported by the cited passages

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.96 | 0.82 | 0.68 | 0.53 | 0.90 | 0.61 | **0.75** |
| `search_loop` | `ministral-14b-2512` | 0.87 | 0.86 | 0.88 | 0.61 | 0.90 | 0.75 | **0.81** |
| `outline` | `ministral-14b-2512` | 0.76 | 0.70 | 0.35 | 0.80 | 0.75 | 0.40 | **0.65** |

**citation_relevance** -- citations that support their sentence

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 0.91 | 0.81 | 0.77 | 0.90 | 1.00 | **0.89** |
| `search_loop` | `ministral-14b-2512` | 1.00 | 0.88 | 0.84 | 0.73 | 1.00 | 1.00 | **0.91** |
| `outline` | `ministral-14b-2512` | 0.91 | 0.88 | 0.96 | 0.89 | 0.75 | 0.62 | **0.85** |

### Effort

What each strategy spent to get there.

**latency_p50_s** -- median seconds per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 3.2 | 6.6 | 4.2 | 2.2 | 3.2 | 2.0 | **3.0** |
| `search_loop` | `ministral-14b-2512` | 5.6 | 11.6 | 7.6 | 6.1 | 6.7 | 7.3 | **7.4** |
| `outline` | `ministral-14b-2512` | 3.3 | 7.3 | 2.6 | 3.1 | 4.8 | 2.6 | **3.7** |

**latency_p95_s** -- 95th percentile seconds per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 6.9 | 11.0 | 5.6 | 11.2 | 7.1 | 2.5 | **7.7** |
| `search_loop` | `ministral-14b-2512` | 11.6 | 19.4 | 11.0 | 13.1 | 17.4 | 11.9 | **15.6** |
| `outline` | `ministral-14b-2512` | 6.5 | 28.5 | 6.0 | 5.0 | 9.7 | 4.7 | **9.7** |

**tokens_in** -- prompt tokens per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1646 | 1877 | 2351 | 1728 | 2145 | 1740 | **1914** |
| `search_loop` | `ministral-14b-2512` | 10427 | 17246 | 17107 | 13219 | 14499 | 23619 | **16019** |
| `outline` | `ministral-14b-2512` | 8448 | 9041 | 8032 | 11114 | 9379 | 7592 | **8934** |

**tokens_out** -- completion tokens per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 274 | 648 | 354 | 218 | 311 | 134 | **323** |
| `search_loop` | `ministral-14b-2512` | 478 | 952 | 661 | 439 | 478 | 511 | **586** |
| `outline` | `ministral-14b-2512` | 326 | 865 | 287 | 257 | 420 | 207 | **394** |

**usd** -- USD per question, at this run's price table

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | **0.00000** |
| `search_loop` | `ministral-14b-2512` | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | **0.00000** |
| `outline` | `ministral-14b-2512` | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | **0.00000** |

**reference_usd** -- USD per question at mistral-medium-2604 prices

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.0045 | 0.0077 | 0.0062 | 0.0042 | 0.0056 | 0.0036 | **0.0053** |
| `search_loop` | `ministral-14b-2512` | 0.0192 | 0.0330 | 0.0306 | 0.0231 | 0.0253 | 0.0393 | **0.0284** |
| `outline` | `ministral-14b-2512` | 0.0151 | 0.0200 | 0.0142 | 0.0186 | 0.0172 | 0.0129 | **0.0164** |

**tool_calls** -- tool calls per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| `search_loop` | `ministral-14b-2512` | 2.60 | 5.60 | 4.30 | 3.50 | 3.40 | 8.70 | **4.68** |
| `outline` | `ministral-14b-2512` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

**rounds** -- rounds per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | **1.00** |
| `search_loop` | `ministral-14b-2512` | 2.20 | 3.00 | 3.40 | 2.90 | 2.90 | 4.00 | **3.07** |
| `outline` | `ministral-14b-2512` | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | **1.00** |

## Cost and latency

The run made 180 answers over 60 questions:
1612093 prompt and 78200 completion tokens,
0.0000 USD at this run's price table and
3.0046 USD at mistral-medium-2604 prices. Median
answer latency was 4.7 s, 95th
percentile 11.9 s.

`ministral-14b-2512` has no published price, so the USD column of this run is zero by construction. The row beside it prices the same recorded tokens at mistral-medium-2604 rates (D-017), which is what the shipped configuration would have cost.

Judging spent 497916 prompt and 45948 completion tokens over 180 call(s) (13516 of them reasoning tokens, with thinking disabled), at a mean of 3.8 s per judgement and 0 verdict(s) that did not validate. The z.ai coding plan bills nothing against the Mistral budget (D-020); the same judging on mistral-medium-2604 would have cost 1.0915 USD.

## Winner per metric

- `cited_url_match`: **search_loop**
- `cited_anchor_match`: **single_pass**
- `citation_verification_rate`: **outline**
- `unverified_citations_per_answer`: **outline**
- `refusal_correct`: **search_loop**
- `correctness`: **search_loop**
- `groundedness`: **search_loop**
- `citation_relevance`: **search_loop**
- `latency_p50_s`: **single_pass**
- `usd`: **single_pass**
- `reference_usd`: **single_pass**

`search_loop` answers best and `single_pass` is cheapest: the better answers cost 8.4x the prompt tokens of the cheaper strategy.

## Figures

`figures/` is regenerated from `metrics.json` by `make eval-report run=eval/runs/2026-09-08-2305-dev60-baseline`.

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
