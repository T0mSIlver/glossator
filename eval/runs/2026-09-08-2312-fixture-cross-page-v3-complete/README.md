# Dataset generation run

This run asked glm-5.3-flash to generate documentation questions from tests/fixtures/corpus. It tested whether prompt s2-v3 produces standalone questions supported by their assigned sources.

## Question

Does this generator configuration produce valid questions whose assigned sources are all necessary for the answer?

## Configuration

The run used one provider and prompt configuration. `config.json` records every parameter and prompt hash.

- Provider: zai
- Model: glm-5.3-flash
- Thinking: disabled
- Seed: 0
- Corpus commit: 2e094f7bbe1395de4a738a3483def3573143d973
- Requested questions: 6
- Dataset: eval/runs/2026-09-08-2312-fixture-cross-page-v3-complete/questions.jsonl

## Results

The run processed 9 candidates, kept 6, and dropped 3.

- api_reference: 2 candidates, 1 kept, 1 dropped
- capability: 3 candidates, 1 kept, 2 dropped
- cross_page: 1 candidate, 1 kept, 0 dropped
- post_cutoff: 1 candidate, 1 kept, 0 dropped
- single_page: 1 candidate, 1 kept, 0 dropped
- unanswerable: 1 candidate, 1 kept, 0 dropped

Dropped candidates by reason:

- answerable from title alone: 3

The provider handled 20 calls, including 6 cache hits. Recorded usage was 11157 prompt tokens, 1678 completion tokens, and 288 reasoning tokens.

## Conclusion

Status: complete. The records support the dataset-generation choice in D-020 and the record requirements in D-023.
