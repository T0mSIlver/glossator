# Answer evaluation: single_pass on `sec128`

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
- Index variant: `sec128`, top_k 8, context budget 6000 tokens
- Dataset: `tests/fixtures/answer-questions.jsonl`, sha256 `ef184ab31296f7caf57659e5ef6f24bd591e5841089c67c09d031d535cde5a7a`
- Questions: 4; strategies: 1; records: 4
- Judge prompt hashes: {"judge_citation": "4603459ac6e543de", "judge_system": "b8150fdcba16ff47", "judge_user": "5bbdcd0c47bf9a06"}

`config.json` holds every other parameter, including the price table the USD
columns were computed with.

## Notes on this run

- The sec128 schema holds the whole vendored corpus as well as the nine fixture pages, because both were ingested into it. The fixture pages replaced the real pages that share their URL, but every other real page still competes for retrieval, so a fixture question can be answered from a real page whose URL is not in the gold set. This run proves the pipeline; it does not measure answer quality.
- Run on the fixture dataset with --limit 4, so each question type below has exactly one question in it. Nothing here is a sample size.

## Results

4 of 4 answers were judged by `glm-5.3` with thinking disabled. 0 answer(s) ended in an error and are recorded with it.

### Citations against the gold sources

Whether the answer's verified citations point at the pages the dataset says hold the answer. Unanswerable questions have no gold source, so they are left out of these two tables rather than counted as failures.

**cited_url_match** -- a verified citation names a gold page

| strategy | model | single_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 1.00 | 0.00 | -- | **0.67** |

**cited_anchor_match** -- a verified citation names the gold section

| strategy | model | single_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00 | 1.00 | 0.00 | -- | **0.33** |

### Citation verification

Whether the quotes the model wrote are in the sources it named. A fabricated rejection is a sentence that is not in the source at all; a cosmetic one is a quote too short to be evidence. The two are reported apart because averaging them hides both (D-027a). Distinct sources are counted beside the citations because an answer that cites `[1]` five times looks well cited and is not.

**citation_verification_rate** -- verified citations over emitted citations

| strategy | model | single_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 1.00 | 1.00 | -- | **1.00** |

**unverified_citations_per_answer** -- rejected citations per answer

| strategy | model | single_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

**fabricated_per_answer** -- fabricated rejections per answer

| strategy | model | single_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

**cosmetic_per_answer** -- cosmetic rejections per answer

| strategy | model | single_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

**distinct_sources_cited** -- different sources cited per answer

| strategy | model | single_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 1.00 | 1.00 | 0.00 | **0.75** |

**unmatched_markers_per_answer** -- `[n]` markers with no citation behind them

| strategy | model | single_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00 | 0.00 | 0.00 | 6.00 | **1.50** |

### Refusal

`insufficient_evidence` should be set on exactly the questions the documentation cannot answer. This table scores both directions: a refused answerable question is as wrong as an answered unanswerable one.

**refusal_correct** -- the refusal flag matches the question

| strategy | model | single_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 1.00 | 1.00 | 1.00 | **1.00** |

### Judged quality

GLM's verdicts (D-021), reported beside the deterministic numbers and never merged into them. Correctness scores correct as 1, partial as 0.5, wrong as 0. Groundedness is the fraction of the answer's factual claims the cited passages support. Citation relevance is the fraction of citations that support the sentence they are attached to.

**correctness** -- correctness against the reference answer

| strategy | model | single_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 0.50 | 1.00 | 1.00 | **0.88** |

**groundedness** -- claims supported by the cited passages

| strategy | model | single_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 1.00 | 1.00 | -- | **1.00** |

**citation_relevance** -- citations that support their sentence

| strategy | model | single_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 1.00 | 1.00 | -- | **1.00** |

### Effort

What each strategy spent to get there.

**latency_p50_s** -- median seconds per answer

| strategy | model | single_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 2.0 | 3.6 | 4.3 | 1.2 | **2.0** |

**latency_p95_s** -- 95th percentile seconds per answer

| strategy | model | single_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 2.0 | 3.6 | 4.3 | 1.2 | **4.3** |

**tokens_in** -- prompt tokens per answer

| strategy | model | single_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 4665 | 1961 | 2585 | 1799 | **2752** |

**tokens_out** -- completion tokens per answer

| strategy | model | single_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 131 | 241 | 265 | 71 | **177** |

**usd** -- USD per question, at this run's price table

| strategy | model | single_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00000 | 0.00000 | 0.00000 | 0.00000 | **0.00000** |

**reference_usd** -- USD per question at mistral-medium-2604 prices

| strategy | model | single_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.0080 | 0.0047 | 0.0059 | 0.0032 | **0.0055** |

**tool_calls** -- tool calls per answer

| strategy | model | single_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

**rounds** -- rounds per answer

| strategy | model | single_page | api_reference | capability | unanswerable | all |
|---|---|---|---|---|---|---|
| `single_pass` | `ministral-14b-2512` | 1.00 | 1.00 | 1.00 | 1.00 | **1.00** |

## Cost and latency

The run made 4 answers over 4 questions:
11010 prompt and 708 completion tokens,
0.0000 USD at this run's price table and
0.0218 USD at mistral-medium-2604 prices. Median
answer latency was 2.0 s, 95th
percentile 4.3 s.

`ministral-14b-2512` has no published price, so the USD column of this run is zero by construction. The row beside it prices the same recorded tokens at mistral-medium-2604 rates (D-017), which is what the shipped configuration would have cost.

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

`figures/` is regenerated from `metrics.json` by `make eval-report run=eval/runs/2026-09-08-2255-answers-fixture`.

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
