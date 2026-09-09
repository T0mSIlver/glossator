# Answer evaluation: single_pass on `sec1024`

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
- Dataset: `eval/dev-fr.jsonl`, sha256 `f5241bb42ec5cf23b23408fb7b71342f6368ab09f8f23bbd8da80d670f81c73e`
- Questions: 36; strategies: 1; records: 36
- Judge prompt hashes: {"judge_citation": "d1565f592953cb68", "judge_system": "3b300bf0bcd8ea7f", "judge_user": "4e976b80283c7257"}

`config.json` holds every other parameter, including the price table the USD
columns were computed with.

## Notes on this run

- 36 French translations of development questions over the English corpus, shipped retrieval (D-034), single pass; measures D-008 option (a): English index only, the model answers in the question's language.

## Results

36 of 36 answers were judged by the primary judge `zai:glm-5.3`. 0 answer(s) ended in an error and are recorded with it.

### Citations against the gold sources

Whether the answer's verified citations point at the pages the dataset says hold the answer. Unanswerable questions have no gold source, so they are left out of these tables rather than counted as failures. Capability questions also accept a named model's own card, and the last table counts matches that passed only because of that documented relaxation.

**cited_url_match** -- a verified citation names a gold page

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.67 | 0.33 | 0.17 | 0.50 | 0.67 | -- | **0.47** |

**cited_anchor_match** -- a verified citation names the gold section

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.50 | 0.33 | 0.17 | 0.50 | 0.50 | -- | **0.40** |

**gold_relaxed_matches** -- matches accepted through the model-card relaxation

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0 | 0 | 0 | 1 | 0 | 0 | **1** |

### Citation verification

Whether the quotes the model wrote are in the sources it named. A fabricated rejection is a sentence that is not in the source at all; a cosmetic one is a quote too short to be evidence. The two are reported apart because averaging them hides both (D-027a). Distinct sources are counted beside the citations because an answer that cites `[1]` five times looks well cited and is not.

**citation_verification_rate** -- verified citations over emitted citations

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.70 | 0.84 | 0.68 | 0.79 | 0.73 | 1.00 | **0.75** |

**unverified_citations_per_answer** -- rejected citations per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 0.50 | 1.33 | 0.50 | 0.67 | 0.00 | **0.67** |

**fabricated_per_answer** -- fabricated rejections per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 0.50 | 1.33 | 0.50 | 0.67 | 0.00 | **0.67** |

**cosmetic_per_answer** -- cosmetic rejections per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

**distinct_sources_cited** -- different sources cited per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 2.00 | 1.17 | 1.83 | 1.33 | 0.50 | **1.31** |

**unmatched_markers_per_answer** -- `[n]` markers with no citation behind them

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.67 | 0.00 | 0.33 | 0.17 | 0.17 | 1.83 | **0.69** |

### Refusal

`insufficient_evidence` should be set on exactly the questions the documentation cannot answer. This table scores both directions: a refused answerable question is as wrong as an answered unanswerable one.

**refusal_correct** -- the refusal flag matches the question

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.67 | 0.67 | 0.67 | 1.00 | 1.00 | 1.00 | **0.83** |

### Judged quality

The primary judge's verdicts (D-021), reported beside the deterministic numbers and never merged into them. Correctness scores correct as 1, partial as 0.5, wrong as 0. Groundedness is the fraction of the answer's factual claims the cited passages support. Citation relevance is the fraction of citations that support the sentence they are attached to.

**correctness** -- correctness against the reference answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.58 | 0.33 | 0.67 | 0.83 | 0.83 | 1.00 | **0.71** |

**groundedness** -- claims supported by the cited passages

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.70 | 0.65 | 0.67 | 0.80 | 0.76 | 0.88 | **0.74** |

**citation_relevance** -- citations that support their sentence

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 0.88 | 1.00 | 1.00 | 0.89 | 1.00 | **0.95** |

### Effort

What each strategy spent to get there.

**latency_p50_s** -- median seconds per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 7.2 | 11.2 | 12.6 | 7.2 | 8.1 | 5.7 | **8.3** |

**latency_p95_s** -- 95th percentile seconds per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 9.1 | 20.2 | 15.3 | 12.3 | 20.4 | 8.3 | **20.2** |

**tokens_in** -- prompt tokens per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 3609 | 4032 | 3975 | 2268 | 4168 | 4915 | **3828** |

**tokens_out** -- completion tokens per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 266 | 686 | 477 | 290 | 402 | 162 | **381** |

**usd** -- USD per question, at this run's price table

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00058 | 0.00071 | 0.00067 | 0.00038 | 0.00069 | 0.00076 | **0.00063** |

**reference_usd** -- USD per question at mistral-medium-2604 prices

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.0074 | 0.0112 | 0.0095 | 0.0056 | 0.0093 | 0.0086 | **0.0086** |

**tool_calls** -- tool calls per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

**rounds** -- rounds per answer

| strategy | model | single_page | cross_page | api_reference | capability | post_cutoff | unanswerable | all |
|---|---|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | **1.00** |

## Agreement

Correctness is ordinal: wrong is 0, partial is 0.5, and correct is 1. Kappa uses quadratic weights. Exact agreement requires the same label.

### Judge pairs

| first judge | second judge | answers | quadratic-weighted kappa | exact agreement |
|---|---|---:|---:|---:|
| `zai:glm-5.3` | `zai:glm-5.3-flash` | 36 | 0.91 | 0.89 |
| `zai:glm-5.3` | `mistral:ministral-14b-2512` | 36 | 0.51 | 0.75 |
| `zai:glm-5.3-flash` | `mistral:ministral-14b-2512` | 36 | 0.43 | 0.64 |

### Krippendorff's alpha

| raters | ordinal alpha | pairwise exact agreement |
|---|---:|---:|
| configured judges | 0.63 | 0.76 |

### Judge means

| judge | answers | mean correctness | human-labeled answers |
|---|---:|---:|---:|
| `zai:glm-5.3` | 36 | 0.71 | -- |
| `zai:glm-5.3-flash` | 36 | 0.71 | -- |
| `mistral:ministral-14b-2512` | 36 | 0.79 | -- |

## Cost and latency

The run made 36 answers over 36 questions:
137798 prompt and 13704 completion tokens,
0.0227 USD at this run's price table and
0.3095 USD at mistral-medium-2604 prices. Median
answer latency was 8.3 s, 95th
percentile 20.2 s.

Judging spent 199855 prompt and 23592 completion tokens over 108 call(s) (3761 of them reasoning tokens, with thinking disabled), at a mean of 11.3 s per judgement and 0 verdict(s) that did not validate. The z.ai coding plan bills nothing against the Mistral budget (D-020); the same judging on mistral-medium-2604 would have cost 0.4767 USD.

## Winner per metric

- `cited_url_match`: **single_pass**
- `cited_anchor_match`: **single_pass**
- `citation_verification_rate`: **single_pass**
- `unverified_citations_per_answer`: **single_pass**
- `refusal_correct`: **single_pass**
- `correctness`: **single_pass**
- `groundedness`: **single_pass**
- `citation_relevance`: **single_pass**
- `latency_p50_s`: **single_pass**
- `usd`: **single_pass**
- `reference_usd`: **single_pass**

`single_pass` wins on quality and on cost, so there is no trade-off to make in this run.

## Figures

`figures/` is regenerated from `metrics.json` by `make eval-report run=eval/runs/2026-09-09-0401-devfr-shipped`.

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
