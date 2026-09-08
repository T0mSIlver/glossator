# Dataset generation run

This run asked glm-5.3-flash to generate documentation questions from corpus/mistral-docs. It measures how many valid questions of each type the generators produce, and what they cost.

## Question

Does this generator configuration produce standalone questions whose assigned sources are all necessary for the answer, in the numbers the development set needs?

## Configuration

`config.json` records every parameter and prompt hash.

- Provider: zai
- Model: glm-5.3-flash
- Thinking: disabled
- Seed: 0
- Prompt version: v1
- Corpus commit: 2e094f7bbe1395de4a738a3483def3573143d973
- Requested questions: 12
- Dataset: eval/dev-smoke.jsonl

## Results

The run processed 24 candidates, kept 12, and dropped 12.

- api_reference: 2 asked, 4 candidates, 2 kept, 2 dropped
- capability: 2 asked, 4 candidates, 2 kept, 2 dropped
- cross_page: 2 asked, 4 candidates, 2 kept, 2 dropped
- post_cutoff: 2 asked, 4 candidates, 2 kept, 2 dropped
- single_page: 2 asked, 4 candidates, 2 kept, 2 dropped
- unanswerable: 2 asked, 4 candidates, 2 kept, 2 dropped

Dropped candidates by reason:

- gold condition failed: 1
- not about the documented product: 2
- provider_error: 1
- surplus, the type was already filled: 9

## Calls and usage

The provider handled 66 calls, of which 0 were cache hits and 3 returned an error that was retried or recorded.

- closed_book: 4 calls, 294 prompt + 351 completion tokens
- corpus_check: 4 calls, 6689 prompt + 309 completion tokens
- filter: 24 calls, 34765 prompt + 2519 completion tokens
- generation: 24 calls, 28803 prompt + 2660 completion tokens
- page_alone: 10 calls, 8133 prompt + 617 completion tokens

Total tokens: 78684 prompt, 6456 completion, 1563 reasoning. Paid for in this run (uncached): 78684 prompt, 6456 completion, 1563 reasoning.

## Figures

`figures/` holds the charts, regenerated from `metrics.json` by `make eval-report run=<dir>`.

- `figures/accepted-by-type.svg`: accepted against dropped, per question type
- `figures/drop-reasons.svg`: how many candidates each drop reason accounts for
- `figures/tokens-by-call-kind.svg`: tokens spent on generating against checking

## Conclusion

The run asked for 12 questions and accepted 12 of 24 candidates. Every question type was filled. The largest drop reasons were surplus, the type was already filled (9), not about the documented product (2), gold condition failed (1). 78684 prompt and 6456 completion tokens were paid for at 0.00 USD against the Mistral budget (z.ai coding plan, not billed to the Mistral budget). The dataset feeds the retrieval and answer evaluations in D-016.
