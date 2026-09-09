# Answer evaluation: search_loop on `sec1024`

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
- Judge models: `glm-5.3`; primary first (answer-judge/v2)
- Index variant: `sec1024`, top_k 8, rerank True (ministral-14b-2512), context budget 6000 tokens
- Non-English questions rendered in English for retrieval: True
- Question reworded into the documentation's vocabulary for retrieval: False
- Dataset: `eval/dev-noisy.jsonl`, sha256 `df892be3ea190383acf69b5df647781f6f093d7f2e76b1ea22ec724da7b3bd68`
- Questions: 105; strategies: 1; records: 105
- Judge prompt hashes: {"judge_citation": "d1565f592953cb68", "judge_system": "3b300bf0bcd8ea7f", "judge_user": "4e976b80283c7257"}

`config.json` holds every other parameter, including the price table the USD
columns were computed with.

## Notes on this run

- Noisy variants of 120 stratified dev questions (eval/dev-noisy.jsonl), one noise kind per question.
- The search loop, whose query reformulation this dataset was built to show.
- The noisy and clean streams ran side by side, and some answers and judgements came back HTTP 429. Those rows were removed from records.jsonl and answered and judged again; every attempt, failed ones included, is still in calls.jsonl.

## Results

105 of 105 answers were judged by the primary judge `glm-5.3`. 0 answer(s) ended in an error and are recorded with it.

### Citations against the gold sources

Whether the answer's verified citations point at the pages the dataset says hold the answer. Unanswerable questions have no gold source, so they are left out of these tables rather than counted as failures. Capability questions also accept a named model's own card, and the last table counts matches that passed only because of that documented relaxation.

**cited_url_match** -- a verified citation names a gold page

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `search_loop` | `ministral-14b-2512` | 0.71 | 0.88 | 0.78 | 0.41 | 0.89 | -- | **0.74** |

**cited_anchor_match** -- a verified citation names the gold section

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `search_loop` | `ministral-14b-2512` | 0.35 | 0.88 | 0.28 | 0.41 | 0.32 | -- | **0.44** |

**gold_relaxed_matches** -- matches accepted through the model-card relaxation

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `search_loop` | `ministral-14b-2512` | 0 | 0 | 0 | 1 | 0 | 0 | **1** |

### Citation verification

Whether the quotes the model wrote are in the sources it named. A fabricated rejection is a sentence that is not in the source at all; a cosmetic one is a quote too short to be evidence. The two are reported apart because averaging them hides both (D-027a). Distinct sources are counted beside the citations because an answer that cites `[1]` five times looks well cited and is not.

**citation_verification_rate** -- verified citations over emitted citations

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `search_loop` | `ministral-14b-2512` | 0.83 | 0.87 | 0.89 | 0.74 | 0.82 | 0.94 | **0.85** |

**unverified_citations_per_answer** -- rejected citations per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `search_loop` | `ministral-14b-2512` | 0.65 | 0.71 | 0.56 | 1.06 | 0.47 | 0.18 | **0.60** |

**fabricated_per_answer** -- fabricated rejections per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `search_loop` | `ministral-14b-2512` | 0.65 | 0.71 | 0.56 | 1.06 | 0.47 | 0.18 | **0.60** |

**cosmetic_per_answer** -- cosmetic rejections per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `search_loop` | `ministral-14b-2512` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

**distinct_sources_cited** -- different sources cited per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `search_loop` | `ministral-14b-2512` | 2.24 | 3.76 | 1.83 | 2.76 | 1.53 | 2.53 | **2.42** |

**unmatched_markers_per_answer** -- `[n]` markers with no citation behind them

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `search_loop` | `ministral-14b-2512` | 0.18 | 0.12 | 0.06 | 0.12 | 0.11 | 0.18 | **0.12** |

### Refusal

`insufficient_evidence` should be set on exactly the questions the documentation cannot answer. This table scores both directions: a refused answerable question is as wrong as an answered unanswerable one.

**refusal_correct** -- the refusal flag matches the question

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `search_loop` | `ministral-14b-2512` | 0.94 | 0.88 | 0.83 | 0.82 | 0.95 | 0.41 | **0.81** |

### Judged quality

The primary judge's verdicts (D-021), reported beside the deterministic numbers and never merged into them. Correctness scores correct as 1, partial as 0.5, wrong as 0. Groundedness is the fraction of the answer's factual claims the cited passages support. Citation relevance is the fraction of citations that support the sentence they are attached to.

**correctness** -- correctness against the reference answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `search_loop` | `ministral-14b-2512` | 0.79 | 0.65 | 0.81 | 0.76 | 0.84 | 0.59 | **0.74** |

**groundedness** -- claims supported by the cited passages

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `search_loop` | `ministral-14b-2512` | 0.83 | 0.84 | 0.84 | 0.77 | 0.88 | 0.72 | **0.82** |

**citation_relevance** -- citations that support their sentence

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `search_loop` | `ministral-14b-2512` | 0.98 | 0.92 | 0.94 | 0.89 | 0.95 | 0.93 | **0.94** |

### Effort

What each strategy spent to get there.

**latency_p50_s** -- median seconds per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `search_loop` | `ministral-14b-2512` | 35.2 | 42.7 | 31.2 | 31.6 | 29.3 | 44.2 | **36.4** |

**latency_p95_s** -- 95th percentile seconds per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `search_loop` | `ministral-14b-2512` | 72.3 | 69.3 | 44.8 | 61.3 | 56.7 | 56.7 | **56.7** |

**tokens_in** -- prompt tokens per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `search_loop` | `ministral-14b-2512` | 12948 | 18674 | 16199 | 12717 | 18625 | 21266 | **16769** |

**tokens_out** -- completion tokens per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `search_loop` | `ministral-14b-2512` | 690 | 1000 | 691 | 721 | 561 | 603 | **708** |

**usd** -- USD per question, at this run's price table

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `search_loop` | `ministral-14b-2512` | 0.00205 | 0.00295 | 0.00265 | 0.00202 | 0.00288 | 0.00328 | **0.00264** |

**reference_usd** -- USD per question at mistral-medium-2604 prices

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `search_loop` | `ministral-14b-2512` | 0.0246 | 0.0355 | 0.0295 | 0.0245 | 0.0321 | 0.0364 | **0.0305** |

**tool_calls** -- tool calls per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `search_loop` | `ministral-14b-2512` | 3.65 | 5.59 | 4.33 | 3.24 | 4.79 | 6.59 | **4.70** |

**rounds** -- rounds per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `search_loop` | `ministral-14b-2512` | 2.29 | 3.24 | 3.17 | 2.29 | 3.37 | 3.41 | **2.97** |

## Agreement

Correctness is ordinal: wrong is 0, partial is 0.5, and correct is 1. Kappa uses quadratic weights. Exact agreement requires the same label.

### Judge pairs

| first judge | second judge | answers | quadratic-weighted kappa | exact agreement |
|---|---|---:|---:|---:|
| -- | -- | 0 | -- | -- |

### Krippendorff's alpha

| raters | ordinal alpha | pairwise exact agreement |
|---|---:|---:|
| configured judges | -- | -- |

### Judge means

| judge | answers | mean correctness | human-labeled answers |
|---|---:|---:|---:|
| `zai:glm-5.3` | 105 | 0.74 | -- |

## Cost and latency

The run made 105 answers over 105 questions:
1760737 prompt and 74338 completion tokens,
0.2773 USD at this run's price table and
3.1986 USD at mistral-medium-2604 prices. Median
answer latency was 36.4 s, 95th
percentile 56.7 s.

Judging spent 305285 prompt and 34380 completion tokens over 105 call(s) (10980 of them reasoning tokens, with thinking disabled), at a mean of 10.8 s per judgement and 0 verdict(s) that did not validate. The z.ai coding plan bills nothing against the Mistral budget (D-020); the same judging on mistral-medium-2604 would have cost 0.7158 USD.

## Winner per metric

- `cited_url_match`: **search_loop**
- `cited_anchor_match`: **search_loop**
- `citation_verification_rate`: **search_loop**
- `unverified_citations_per_answer`: **search_loop**
- `refusal_correct`: **search_loop**
- `correctness`: **search_loop**
- `groundedness`: **search_loop**
- `citation_relevance`: **search_loop**
- `latency_p50_s`: **search_loop**
- `usd`: **search_loop**
- `reference_usd`: **search_loop**

`search_loop` wins on quality and on cost, so there is no trade-off to make in this run.

## Figures

`figures/` is regenerated from `metrics.json` by `make eval-report run=eval/runs/2026-09-09-1344-noisy-loop`.

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
