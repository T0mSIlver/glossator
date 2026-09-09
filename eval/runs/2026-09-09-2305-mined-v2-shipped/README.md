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

- Generation model: `llamacpp/ministral3-14b`
- Generation server: `http://192.168.1.183:8080` -- a local server, not the Mistral API. Every judged number, latency and token count in this run describes that server; none of it is comparable with an API run of the same configuration. Chat calls were sent with `reasoning_effort=low`.
- Answer-config overrides: none (the shipped configuration)
- Judge models: `zai:glm-5.3`; primary first (answer-judge/v2)
- Index variant: `sec1024`, top_k 8, rerank True (llamacpp/ministral3-14b), context budget 6000 tokens
- Search loop caps: round_cap 4, searches_per_round 4, tool_result_chars 600, response_format json_schema
- Non-English questions rendered in English for retrieval: True
- Question reworded into the documentation's vocabulary for retrieval: False
- Dataset: `eval/mined-v2.jsonl`, sha256 `1e19ef8f8f12dc7e923c4e196bf3111c386c92e46992d2a3dac8b9600fdfecb2`
- Questions: 83; strategies: 1; records: 83
- Judge prompt hashes: {"judge_citation": "d1565f592953cb68", "judge_system": "3b300bf0bcd8ea7f", "judge_user": "4e976b80283c7257"}

`config.json` holds every other parameter, including the price table the USD
columns were computed with.

## Notes on this run

- Second mined set on the shipped configuration, generated on the local llama.cpp server with Ministral 3 14B Reasoning at the model card's settings: temperature 1.0, top_p 0.95, reasoning effort low, thinking always on with token headroom.

## Results

83 of 83 answers were judged by the primary judge `zai:glm-5.3`. 0 answer(s) ended in an error and are recorded with it.

### Citations against the gold sources

Whether the answer's verified citations point at the pages the dataset says hold the answer. Unanswerable questions have no gold source, so they are left out of these tables rather than counted as failures. Capability questions also accept a named model's own card, and the last table counts matches that passed only because of that documented relaxation.

**cited_url_match** -- a verified citation names a gold page

| strategy | model | single_page | cross_page | api_reference | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `llamacpp/ministral3-14b` | 0.58 | 0.64 | 0.25 | -- | **0.57** |

**cited_anchor_match** -- a verified citation names the gold section

| strategy | model | single_page | cross_page | api_reference | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `llamacpp/ministral3-14b` | 0.42 | 0.27 | 0.25 | -- | **0.39** |

**gold_relaxed_matches** -- matches accepted through the model-card relaxation

| strategy | model | single_page | cross_page | api_reference | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `llamacpp/ministral3-14b` | 0 | 0 | 0 | 0 | **0** |

### Citation verification

Whether the quotes the model wrote are in the sources it named. A fabricated rejection is a sentence that is not in the source at all; a cosmetic one is a quote too short to be evidence. The two are reported apart because averaging them hides both (D-027a). Distinct sources are counted beside the citations because an answer that cites `[1]` five times looks well cited and is not.

**citation_verification_rate** -- verified citations over emitted citations

| strategy | model | single_page | cross_page | api_reference | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `llamacpp/ministral3-14b` | 0.85 | 0.69 | 0.86 | 0.86 | **0.83** |

**unverified_citations_per_answer** -- rejected citations per answer

| strategy | model | single_page | cross_page | api_reference | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `llamacpp/ministral3-14b` | 0.40 | 0.82 | 0.25 | 0.15 | **0.41** |

**fabricated_per_answer** -- fabricated rejections per answer

| strategy | model | single_page | cross_page | api_reference | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `llamacpp/ministral3-14b` | 0.40 | 0.82 | 0.25 | 0.15 | **0.41** |

**cosmetic_per_answer** -- cosmetic rejections per answer

| strategy | model | single_page | cross_page | api_reference | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `llamacpp/ministral3-14b` | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

**distinct_sources_cited** -- different sources cited per answer

| strategy | model | single_page | cross_page | api_reference | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `llamacpp/ministral3-14b` | 1.82 | 1.64 | 1.50 | 0.85 | **1.63** |

**unmatched_markers_per_answer** -- `[n]` markers with no citation behind them

| strategy | model | single_page | cross_page | api_reference | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `llamacpp/ministral3-14b` | 0.05 | 0.18 | 0.00 | 0.00 | **0.06** |

### Refusal

`insufficient_evidence` should be set on exactly the questions the documentation cannot answer. This table scores both directions: a refused answerable question is as wrong as an answered unanswerable one.

**refusal_correct** -- the refusal flag matches the question

| strategy | model | single_page | cross_page | api_reference | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `llamacpp/ministral3-14b` | 0.82 | 0.64 | 0.75 | 0.77 | **0.78** |

### Judged quality

The primary judge's verdicts (D-021), reported beside the deterministic numbers and never merged into them. Correctness scores correct as 1, partial as 0.5, wrong as 0. Groundedness is the fraction of the answer's factual claims the cited passages support. Citation relevance is the fraction of citations that support the sentence they are attached to.

**correctness** -- correctness against the reference answer

| strategy | model | single_page | cross_page | api_reference | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `llamacpp/ministral3-14b` | 0.66 | 0.45 | 0.25 | 0.85 | **0.64** |

**groundedness** -- claims supported by the cited passages

| strategy | model | single_page | cross_page | api_reference | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `llamacpp/ministral3-14b` | 0.75 | 0.64 | 0.87 | 0.39 | **0.71** |

**citation_relevance** -- citations that support their sentence

| strategy | model | single_page | cross_page | api_reference | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `llamacpp/ministral3-14b` | 0.94 | 0.97 | 1.00 | 0.70 | **0.93** |

### Effort

What each strategy spent to get there.

**latency_p50_s** -- median seconds per answer

| strategy | model | single_page | cross_page | api_reference | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `llamacpp/ministral3-14b` | 29.3 | 30.3 | 26.7 | 22.4 | **29.0** |

**latency_p95_s** -- 95th percentile seconds per answer

| strategy | model | single_page | cross_page | api_reference | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `llamacpp/ministral3-14b` | 63.3 | 41.3 | 44.5 | 53.9 | **58.2** |

**tokens_in** -- prompt tokens per answer

| strategy | model | single_page | cross_page | api_reference | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `llamacpp/ministral3-14b` | 2309 | 2386 | 2356 | 2790 | **2397** |

**tokens_out** -- completion tokens per answer

| strategy | model | single_page | cross_page | api_reference | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `llamacpp/ministral3-14b` | 448 | 363 | 265 | 187 | **387** |

**usd** -- USD per question, at this run's price table

| strategy | model | single_page | cross_page | api_reference | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `llamacpp/ministral3-14b` | 0.00041 | 0.00041 | 0.00039 | 0.00045 | **0.00042** |

**reference_usd** -- USD per question at mistral-medium-2604 prices

| strategy | model | single_page | cross_page | api_reference | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `llamacpp/ministral3-14b` | 0.0068 | 0.0063 | 0.0055 | 0.0056 | **0.0065** |

**tool_calls** -- tool calls per answer

| strategy | model | single_page | cross_page | api_reference | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `llamacpp/ministral3-14b` | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

**rounds** -- rounds per answer

| strategy | model | single_page | cross_page | api_reference | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `llamacpp/ministral3-14b` | 1.00 | 1.00 | 1.00 | 1.00 | **1.00** |

**round_cap_hit** -- share of answers that ran out of rounds

| strategy | model | single_page | cross_page | api_reference | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `llamacpp/ministral3-14b` | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
| `zai:glm-5.3` | 83 | 0.64 | -- |

## Cost and latency

The run made 83 answers over 83 questions:
198950 prompt and 32111 completion tokens,
0.0347 USD at this run's price table and
0.5393 USD at mistral-medium-2604 prices. Median
answer latency was 29.0 s, 95th
percentile 58.2 s.

`llamacpp/ministral3-14b` is a local-server alias for Ministral 3 14B: costs use the published Ministral 3 API rate applied to a local run, not API tokens.

Judging spent 170626 prompt and 22933 completion tokens over 83 call(s) (7290 of them reasoning tokens, with thinking disabled), at a mean of 5.0 s per judgement and 0 verdict(s) that did not validate. The z.ai coding plan bills nothing against the Mistral budget (D-020); the same judging on mistral-medium-2604 would have cost 0.4279 USD.

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

`figures/` is regenerated from `metrics.json` by `make eval-report run=eval/runs/2026-09-09-2305-mined-v2-shipped`.

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
