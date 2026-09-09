# Dataset generation run

This run asked glm-5.3-flash to generate documentation questions from corpus/mistral-docs. It measures how many valid questions of each type the generators produce, and what they cost.

## Question

Does this generator configuration produce standalone questions whose assigned sources are all necessary for the answer, in the numbers the development set needs?

## Configuration

`config.json` records every parameter and prompt hash.

- Provider: zai
- Model: glm-5.3-flash
- Thinking: disabled
- Seed: 1
- Prompt version: v1
- Corpus commit: 2e094f7bbe1395de4a738a3483def3573143d973
- Requested questions: 96
- Dataset: eval/dev-batch-1.jsonl

## Results

The run processed 192 candidates, kept 96, and dropped 96.

- api_reference: 16 asked, 32 candidates, 16 kept, 16 dropped
- capability: 16 asked, 32 candidates, 16 kept, 16 dropped
- cross_page: 16 asked, 32 candidates, 16 kept, 16 dropped
- post_cutoff: 16 asked, 32 candidates, 16 kept, 16 dropped
- single_page: 16 asked, 32 candidates, 16 kept, 16 dropped
- unanswerable: 16 asked, 32 candidates, 16 kept, 16 dropped

Dropped candidates by reason:

- answerable from one page alone: 2
- answerable from title alone: 2
- does not require every gold source: 10
- duplicate question: 3
- gold condition failed: 4
- names another vendor's product: 1
- not about the documented product: 10
- surplus, the type was already filled: 62
- the corpus answers it after all: 7

## Calls and usage

The provider handled 515 calls, of which 0 were cache hits and 3 returned an error that was retried or recorded.

- closed_book: 32 calls, 2458 prompt + 3398 completion tokens
- corpus_check: 32 calls, 46518 prompt + 2274 completion tokens
- filter: 193 calls, 283721 prompt + 21858 completion tokens
- generation: 192 calls, 232626 prompt + 22266 completion tokens
- page_alone: 66 calls, 99652 prompt + 5780 completion tokens

Total tokens: 664975 prompt, 55576 completion, 14599 reasoning. Paid for in this run (uncached): 664975 prompt, 55576 completion, 14599 reasoning.

## Figures

`figures/` holds the charts, regenerated from `metrics.json` by `make eval-report run=<dir>`.

- `figures/accepted-by-type.svg`: accepted against dropped, per question type
- `figures/drop-reasons.svg`: how many candidates each drop reason accounts for
- `figures/tokens-by-call-kind.svg`: tokens spent on generating against checking

## Conclusion

The run asked for 96 questions and accepted 96 of 192 candidates. Every question type was filled. The largest drop reasons were surplus, the type was already filled (62), does not require every gold source (10), not about the documented product (10). 664975 prompt and 55576 completion tokens were paid for at 0.00 USD against the Mistral budget (z.ai coding plan, not billed to the Mistral budget). The dataset feeds the retrieval and answer evaluations in D-016.
