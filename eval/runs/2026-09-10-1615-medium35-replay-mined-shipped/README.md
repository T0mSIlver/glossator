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

- Generation model: `mistral-medium-2604`
- Generation server: the Mistral API (`https://api.mistral.ai`)
- Answer-config overrides: none (the shipped configuration)
- Judge models: `zai:glm-5.3`, `zai:glm-5.3-flash`; primary first (answer-judge/v2)
- Index variant: `sec1024`, top_k 8, rerank True (ministral-14b-2512), context budget 6000 tokens
- Search loop caps: round_cap 4, searches_per_round 4, tool_result_chars 600, response_format unknown
- Non-English questions rendered in English for retrieval: True
- Question reworded into the documentation's vocabulary for retrieval: unknown
- Dataset: `eval/mined.jsonl`, sha256 `a276e09f853024f2647dad9d7f7c4c8c34e1754dafdf6a6dc4fbb994dfd5b2a2`
- Questions: 84; strategies: 1; records: 84
- Judge prompt hashes: {"judge_citation": "d1565f592953cb68", "judge_system": "3b300bf0bcd8ea7f", "judge_user": "4e976b80283c7257"}

`config.json` holds every other parameter, including the price table the USD
columns were computed with.

## Notes on this run

- Generation replayed on mistral-medium-2604 from the recorded prompts of `2026-09-09-1253-mined-shipped`; retrieval, reranking and context are that run's, unchanged.
- Completions produced on 2026-09-10 by Mistral Medium 3.5 (endpoint model name Mistral-Medium-3.5-128B) through an OpenAI-compatible gateway with json_schema output, temperature 0.2, 1,600 completion tokens; reranking stayed as the source run recorded it.
- 1 replayed answer(s) not scored because the source record ended in an error and has no trace: mined-006.

## Results

84 of 84 answers were judged by the primary judge `zai:glm-5.3`. 0 answer(s) ended in an error and are recorded with it.

### Citations against the gold sources

Whether the answer's verified citations point at the pages the dataset says hold the answer. Unanswerable questions have no gold source, so they are left out of these tables rather than counted as failures. Capability questions also accept a named model's own card, and the last table counts matches that passed only because of that documented relaxation.

**cited_url_match** -- a verified citation names a gold page

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `mistral-medium-2604` | 0.88 | 0.50 | 0.82 | 1.00 | -- | **0.85** |

**cited_anchor_match** -- a verified citation names the gold section

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `mistral-medium-2604` | 0.54 | 0.25 | 0.82 | 1.00 | -- | **0.57** |

**gold_relaxed_matches** -- matches accepted through the model-card relaxation

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `mistral-medium-2604` | 0 | 0 | 0 | 0 | 0 | **0** |

### Citation verification

Whether the quotes the model wrote are in the sources it named. A fabricated rejection is a sentence that is not in the source at all; a cosmetic one is a quote too short to be evidence. The two are reported apart because averaging them hides both (D-027a). Distinct sources are counted beside the citations because an answer that cites `[1]` five times looks well cited and is not.

**citation_verification_rate** -- verified citations over emitted citations

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `mistral-medium-2604` | 0.92 | 0.90 | 1.00 | 1.00 | 0.80 | **0.92** |

**unverified_citations_per_answer** -- rejected citations per answer

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `mistral-medium-2604` | 0.20 | 0.25 | 0.00 | 0.00 | 0.11 | **0.17** |

**fabricated_per_answer** -- fabricated rejections per answer

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `mistral-medium-2604` | 0.20 | 0.25 | 0.00 | 0.00 | 0.11 | **0.17** |

**cosmetic_per_answer** -- cosmetic rejections per answer

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `mistral-medium-2604` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

**distinct_sources_cited** -- different sources cited per answer

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `mistral-medium-2604` | 1.75 | 1.25 | 1.27 | 1.00 | 0.44 | **1.51** |

**unmatched_markers_per_answer** -- `[n]` markers with no citation behind them

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `mistral-medium-2604` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

### Refusal

`insufficient_evidence` should be set on exactly the questions the documentation cannot answer. This table scores both directions: a refused answerable question is as wrong as an answered unanswerable one.

**refusal_correct** -- the refusal flag matches the question

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `mistral-medium-2604` | 0.98 | 0.75 | 1.00 | 1.00 | 0.67 | **0.94** |

### Judged quality

The primary judge's verdicts (D-021), reported beside the deterministic numbers and never merged into them. Correctness scores correct as 1, partial as 0.5, wrong as 0. Groundedness is the fraction of the answer's factual claims the cited passages support. Citation relevance is the fraction of citations that support the sentence they are attached to.

**correctness** -- correctness against the reference answer

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `mistral-medium-2604` | 0.81 | 0.62 | 0.95 | 0.50 | 0.67 | **0.80** |

**groundedness** -- claims supported by the cited passages

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `mistral-medium-2604` | 0.92 | 1.00 | 0.98 | 1.00 | 0.23 | **0.89** |

**citation_relevance** -- citations that support their sentence

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `mistral-medium-2604` | 0.98 | 1.00 | 1.00 | 1.00 | 0.17 | **0.95** |

### Effort

What each strategy spent to get there.

**latency_p50_s** -- median seconds per answer

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `mistral-medium-2604` | 4.2 | 2.4 | 2.6 | 2.1 | 0.9 | **3.9** |

**latency_p95_s** -- 95th percentile seconds per answer

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `mistral-medium-2604` | 12.4 | 8.1 | 9.3 | 2.1 | 5.0 | **10.2** |

**tokens_in** -- prompt tokens per answer

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `mistral-medium-2604` | 2543 | 2535 | 2831 | 1507 | 2435 | **2557** |

**tokens_out** -- completion tokens per answer

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `mistral-medium-2604` | 373 | 304 | 240 | 158 | 105 | **321** |

**usd** -- USD per question, at this run's price table

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `mistral-medium-2604` | 0.00661 | 0.00608 | 0.00605 | 0.00345 | 0.00444 | **0.00624** |

**reference_usd** -- USD per question at mistral-medium-2604 prices

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `mistral-medium-2604` | 0.0066 | 0.0061 | 0.0060 | 0.0034 | 0.0044 | **0.0062** |

**tool_calls** -- tool calls per answer

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `mistral-medium-2604` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

**rounds** -- rounds per answer

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `mistral-medium-2604` | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | **1.00** |

**round_cap_hit** -- share of answers that ran out of rounds

| strategy | model | single_page | cross_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|---|
| `single_pass` | `mistral-medium-2604` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Agreement

Correctness is ordinal: wrong is 0, partial is 0.5, and correct is 1. Kappa uses quadratic weights. Exact agreement requires the same label.

### Judge pairs

| first judge | second judge | answers | quadratic-weighted kappa | exact agreement |
|---|---|---:|---:|---:|
| `zai:glm-5.3` | `zai:glm-5.3-flash` | 84 | 0.71 | 0.79 |

### Krippendorff's alpha

| raters | ordinal alpha | pairwise exact agreement |
|---|---:|---:|
| configured judges | 0.56 | 0.79 |

### Judge means

| judge | answers | mean correctness | human-labeled answers |
|---|---:|---:|---:|
| `zai:glm-5.3` | 84 | 0.80 | -- |
| `zai:glm-5.3-flash` | 84 | 0.85 | -- |

## Cost and latency

The run made 84 answers over 84 questions:
214749 prompt and 26951 completion tokens,
0.5243 USD at this run's price table and
0.5243 USD at mistral-medium-2604 prices. Median
answer latency was 3.9 s, 95th
percentile 10.2 s.

Judging spent 378130 prompt and 30679 completion tokens over 168 call(s) (4571 of them reasoning tokens, with thinking disabled), at a mean of 8.3 s per judgement and 0 verdict(s) that did not validate. The z.ai coding plan bills nothing against the Mistral budget (D-020); the same judging on mistral-medium-2604 would have cost 0.7973 USD.

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
