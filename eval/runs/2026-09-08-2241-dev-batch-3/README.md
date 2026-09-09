# Dataset generation run

This run asked glm-5.3-flash to generate documentation questions from corpus/mistral-docs. It measures how many valid questions of each type the generators produce, and what they cost.

## Question

Does this generator configuration produce standalone questions whose assigned sources are all necessary for the answer, in the numbers the development set needs?

## Configuration

`config.json` records every parameter and prompt hash.

- Provider: zai
- Model: glm-5.3-flash
- Thinking: disabled
- Seed: 3
- Prompt version: v1
- Corpus commit: 2e094f7bbe1395de4a738a3483def3573143d973
- Requested questions: 96
- Dataset: eval/dev-batch-3.jsonl

## Results

The run processed 192 candidates, kept 96, and dropped 96.

- api_reference: 16 asked, 32 candidates, 16 kept, 16 dropped
- capability: 16 asked, 32 candidates, 16 kept, 16 dropped
- cross_page: 16 asked, 32 candidates, 16 kept, 16 dropped
- post_cutoff: 16 asked, 32 candidates, 16 kept, 16 dropped
- single_page: 16 asked, 32 candidates, 16 kept, 16 dropped
- unanswerable: 16 asked, 32 candidates, 16 kept, 16 dropped

Dropped candidates by reason:

- answerable from one page alone: 8
- answerable from title alone: 9
- does not require every gold source: 7
- duplicate question: 3
- gold condition failed: 2
- names another vendor's product: 1
- not about the documented product: 6
- surplus, the type was already filled: 59
- the corpus answers it after all: 8

## Calls and usage

The provider handled 515 calls, of which 0 were cache hits and 3 returned an error that was retried or recorded.

- closed_book: 32 calls, 2436 prompt + 3714 completion tokens
- corpus_check: 32 calls, 44564 prompt + 2278 completion tokens
- filter: 192 calls, 280615 prompt + 19515 completion tokens
- generation: 192 calls, 229357 prompt + 22486 completion tokens
- page_alone: 67 calls, 99577 prompt + 6018 completion tokens

Total tokens: 656549 prompt, 54011 completion, 13046 reasoning. Paid for in this run (uncached): 656549 prompt, 54011 completion, 13046 reasoning.

## Figures

`figures/` holds the charts, regenerated from `metrics.json` by `make eval-report run=<dir>`.

- `figures/accepted-by-type.svg`: accepted against dropped, per question type
- `figures/drop-reasons.svg`: how many candidates each drop reason accounts for
- `figures/tokens-by-call-kind.svg`: tokens spent on generating against checking

## Conclusion

The run asked for 96 questions and accepted 96 of 192 candidates. Every question type was filled. The largest drop reasons were surplus, the type was already filled (59), answerable from title alone (9), answerable from one page alone (8). 656549 prompt and 54011 completion tokens were paid for at 0.00 USD against the Mistral budget (z.ai coding plan, not billed to the Mistral budget). The dataset feeds the retrieval and answer evaluations in D-016.
