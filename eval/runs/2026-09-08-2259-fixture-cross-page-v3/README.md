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
- Dataset: No dataset was written

## Results

The run processed 61 candidates, kept 8, and dropped 53.

- cross_page: 60 candidates, 7 kept, 53 dropped
- single_page: 1 candidate, 1 kept, 0 dropped

Dropped candidates by reason:

- answerable from page A alone: 33
- answerable from page B alone: 16
- answerable from title alone: 28
- does not require every gold source: 16

The provider handled 247 calls, including 0 cache hits. Recorded usage was 200962 prompt tokens, 28104 completion tokens, and 8834 reasoning tokens.

## Conclusion

Status: failed. Accepted 7 of 10 required cross-page candidates. No dataset was written.
