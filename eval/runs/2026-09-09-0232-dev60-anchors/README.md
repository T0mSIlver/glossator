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
- Index variant: `sec1024`, top_k 8, rerank unknown (off), context budget 6000 tokens
- Non-English questions rendered in English for retrieval: unknown
- Question reworded into the documentation's vocabulary for retrieval: unknown
- Dataset: `eval/dev.jsonl`, sha256 `acf3c2e148f1aa4036565ac03dd7a3a7e9bef5d0717529976ce9422b68b35490`
- Questions: 60; strategies: 2; records: 120
- Judge prompt hashes: {"judge_citation": "d1565f592953cb68", "judge_system": "3b300bf0bcd8ea7f", "judge_user": "4e976b80283c7257"}

`config.json` holds every other parameter, including the price table the USD
columns were computed with.

## Notes on this run

- Same 60 questions as dev60-baseline after the anchor fallback to the nearest anchored heading and the stripping of unmatched markers; outline dropped per D-033.

## Results

120 of 120 answers were judged by the primary judge `zai:glm-5.3`. 0 answer(s) ended in an error and are recorded with it.

### Citations against the gold sources

Whether the answer's verified citations point at the pages the dataset says hold the answer. Unanswerable questions have no gold source, so they are left out of these tables rather than counted as failures. Capability questions also accept a named model's own card, and the last table counts matches that passed only because of that documented relaxation.

**cited_url_match** -- a verified citation names a gold page

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.80 | 1.00 | 0.60 | 0.40 | 1.00 | -- | **0.76** |
| `search_loop` | `ministral-14b-2512` | 0.90 | 1.00 | 0.70 | 0.60 | 0.80 | -- | **0.80** |

**cited_anchor_match** -- a verified citation names the gold section

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.30 | 1.00 | 0.60 | 0.40 | 0.60 | -- | **0.58** |
| `search_loop` | `ministral-14b-2512` | 0.40 | 1.00 | 0.30 | 0.60 | 0.10 | -- | **0.48** |

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
| `single_pass` | `ministral-14b-2512` | 0.85 | 0.90 | 1.00 | 0.62 | 0.87 | 1.00 | **0.89** |
| `search_loop` | `ministral-14b-2512` | 0.81 | 0.91 | 0.95 | 0.76 | 0.84 | 0.92 | **0.87** |

**unverified_citations_per_answer** -- rejected citations per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.40 | 0.50 | 0.00 | 0.50 | 0.30 | 0.00 | **0.28** |
| `search_loop` | `ministral-14b-2512` | 0.70 | 0.40 | 0.20 | 0.40 | 0.40 | 0.10 | **0.37** |

**fabricated_per_answer** -- fabricated rejections per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.40 | 0.50 | 0.00 | 0.50 | 0.30 | 0.00 | **0.28** |
| `search_loop` | `ministral-14b-2512` | 0.70 | 0.40 | 0.20 | 0.40 | 0.40 | 0.10 | **0.37** |

**cosmetic_per_answer** -- cosmetic rejections per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| `search_loop` | `ministral-14b-2512` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

**distinct_sources_cited** -- different sources cited per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.30 | 3.40 | 1.50 | 0.80 | 1.50 | 0.60 | **1.52** |
| `search_loop` | `ministral-14b-2512` | 1.40 | 3.00 | 1.60 | 1.20 | 0.90 | 1.00 | **1.52** |

**unmatched_markers_per_answer** -- `[n]` markers with no citation behind them

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00 | 0.10 | 0.20 | 0.40 | 0.00 | 1.20 | **0.32** |
| `search_loop` | `ministral-14b-2512` | 0.30 | 0.30 | 0.00 | 0.10 | 0.10 | 0.30 | **0.18** |

### Refusal

`insufficient_evidence` should be set on exactly the questions the documentation cannot answer. This table scores both directions: a refused answerable question is as wrong as an answered unanswerable one.

**refusal_correct** -- the refusal flag matches the question

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 1.00 | 0.70 | 0.60 | 1.00 | 0.90 | **0.87** |
| `search_loop` | `ministral-14b-2512` | 1.00 | 1.00 | 0.90 | 0.70 | 0.80 | 0.90 | **0.88** |

### Judged quality

The primary judge's verdicts (D-021), reported beside the deterministic numbers and never merged into them. Correctness scores correct as 1, partial as 0.5, wrong as 0. Groundedness is the fraction of the answer's factual claims the cited passages support. Citation relevance is the fraction of citations that support the sentence they are attached to.

**correctness** -- correctness against the reference answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.95 | 0.65 | 0.50 | 0.95 | 0.95 | 0.90 | **0.82** |
| `search_loop` | `ministral-14b-2512` | 1.00 | 0.85 | 0.90 | 0.90 | 1.00 | 0.95 | **0.93** |

**groundedness** -- claims supported by the cited passages

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 0.83 | 0.70 | 0.57 | 0.99 | 0.61 | **0.79** |
| `search_loop` | `ministral-14b-2512` | 0.84 | 0.86 | 0.87 | 0.63 | 0.80 | 0.85 | **0.81** |

**citation_relevance** -- citations that support their sentence

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 0.95 | 0.97 | 1.00 | 1.00 | 1.00 | **0.98** |
| `search_loop` | `ministral-14b-2512` | 0.98 | 0.95 | 0.93 | 1.00 | 1.00 | 1.00 | **0.97** |

### Effort

What each strategy spent to get there.

**latency_p50_s** -- median seconds per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 3.5 | 6.5 | 4.0 | 2.1 | 2.6 | 1.9 | **3.0** |
| `search_loop` | `ministral-14b-2512` | 5.9 | 10.5 | 8.7 | 5.7 | 6.3 | 7.3 | **7.3** |

**latency_p95_s** -- 95th percentile seconds per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 6.1 | 10.6 | 7.9 | 3.8 | 4.9 | 2.7 | **9.3** |
| `search_loop` | `ministral-14b-2512` | 12.4 | 25.5 | 12.8 | 8.1 | 11.6 | 10.2 | **14.4** |

**tokens_in** -- prompt tokens per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1670 | 1888 | 2447 | 1749 | 2153 | 1796 | **1951** |
| `search_loop` | `ministral-14b-2512` | 10297 | 19096 | 17430 | 13505 | 16162 | 22060 | **16425** |

**tokens_out** -- completion tokens per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 299 | 636 | 350 | 186 | 263 | 141 | **312** |
| `search_loop` | `ministral-14b-2512` | 462 | 844 | 646 | 367 | 514 | 463 | **549** |

**usd** -- USD per question, at this run's price table

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00030 | 0.00038 | 0.00042 | 0.00029 | 0.00036 | 0.00029 | **0.00034** |
| `search_loop` | `ministral-14b-2512` | 0.00161 | 0.00299 | 0.00271 | 0.00208 | 0.00250 | 0.00338 | **0.00255** |

**reference_usd** -- USD per question at mistral-medium-2604 prices

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.0047 | 0.0076 | 0.0063 | 0.0040 | 0.0052 | 0.0038 | **0.0053** |
| `search_loop` | `ministral-14b-2512` | 0.0189 | 0.0350 | 0.0310 | 0.0230 | 0.0281 | 0.0366 | **0.0288** |

**tool_calls** -- tool calls per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| `search_loop` | `ministral-14b-2512` | 2.60 | 6.00 | 4.30 | 3.50 | 4.00 | 7.70 | **4.68** |

**rounds** -- rounds per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | **1.00** |
| `search_loop` | `ministral-14b-2512` | 2.00 | 3.30 | 3.60 | 3.00 | 3.10 | 3.80 | **3.13** |

## Agreement

Correctness is ordinal: wrong is 0, partial is 0.5, and correct is 1. Kappa uses quadratic weights. Exact agreement requires the same label.

### Judge pairs

| first judge | second judge | answers | quadratic-weighted kappa | exact agreement |
|---|---|---:|---:|---:|
| `zai:glm-5.3` | `zai:glm-5.3-flash` | 120 | 0.82 | 0.90 |
| `zai:glm-5.3` | `mistral:ministral-14b-2512` | 120 | 0.55 | 0.85 |
| `zai:glm-5.3-flash` | `mistral:ministral-14b-2512` | 120 | 0.48 | 0.85 |

### Krippendorff's alpha

| raters | ordinal alpha | pairwise exact agreement |
|---|---:|---:|
| configured judges | 0.66 | 0.87 |

### Judge means

| judge | answers | mean correctness | human-labeled answers |
|---|---:|---:|---:|
| `zai:glm-5.3` | 120 | 0.88 | -- |
| `zai:glm-5.3-flash` | 120 | 0.91 | -- |
| `mistral:ministral-14b-2512` | 120 | 0.90 | -- |

## Cost and latency

The run made 120 answers over 60 questions:
1102528 prompt and 51710 completion tokens,
0.1731 USD at this run's price table and
2.0416 USD at mistral-medium-2604 prices. Median
answer latency was 4.9 s, 95th
percentile 12.1 s.

Judging spent 807895 prompt and 75482 completion tokens over 360 call(s) (8967 of them reasoning tokens, with thinking disabled), at a mean of 8.6 s per judgement and 0 verdict(s) that did not validate. The z.ai coding plan bills nothing against the Mistral budget (D-020); the same judging on mistral-medium-2604 would have cost 1.7780 USD.

## Winner per metric

- `cited_url_match`: **search_loop**
- `cited_anchor_match`: **single_pass**
- `citation_verification_rate`: **single_pass**
- `unverified_citations_per_answer`: **single_pass**
- `refusal_correct`: **search_loop**
- `correctness`: **search_loop**
- `groundedness`: **search_loop**
- `citation_relevance`: **single_pass**
- `latency_p50_s`: **single_pass**
- `usd`: **single_pass**
- `reference_usd`: **single_pass**

`search_loop` answers best and `single_pass` is cheapest: the better answers cost 8.4x the prompt tokens of the cheaper strategy.

## Figures

`figures/` is regenerated from `metrics.json` by `make eval-report run=eval/runs/2026-09-09-0232-dev60-anchors`.

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
