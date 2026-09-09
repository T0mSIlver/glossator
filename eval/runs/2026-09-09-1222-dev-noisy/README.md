# Perturb run

Status: complete.

## Configuration

- dataset: eval/dev.jsonl
- figures: ['kept-by-kind.svg', 'drop-reasons.svg']
- kind: perturb
- model: glm-5.3
- n: 120
- noise_kinds: ['typos', 'keywords', 'vague', 'wrong_term', 'chatty']
- prompt_version: perturb-v1
- provider: zai
- seed: 0
- source_questions: [dev-008, dev-175, dev-290, dev-115, dev-153, dev-230, ... 114 more, see config.json]
- thinking: disabled

## Records

- rows: 120, kept: 105
- dataset: eval/dev-noisy.jsonl

- chatty: 24 candidates, 18 kept, 6 dropped
- keywords: 24 candidates, 24 kept, 0 dropped
- typos: 24 candidates, 24 kept, 0 dropped
- vague: 24 candidates, 24 kept, 0 dropped
- wrong_term: 24 candidates, 15 kept, 9 dropped

Dropped by reason:

- provider_error: ProviderCallError: HTTP 429 from zai: {"error":{"code":"1302","message":"Rate limit reached for requests"}}: 1
- the variant adds a fact the question did not carry: 5
- the variant asks something else: 7
- the variant is the question it came from: 2

## Calls

- filter: 122 calls, 60912 prompt + 8239 completion tokens
- perturb:chatty: 24 calls, 7620 prompt + 1855 completion tokens
- perturb:keywords: 24 calls, 7257 prompt + 517 completion tokens
- perturb:vague: 24 calls, 7575 prompt + 1250 completion tokens
- perturb:wrong_term: 24 calls, 9253 prompt + 1714 completion tokens

- total: 218 calls (9 cached), 92617 prompt + 13575 completion tokens (1356 reasoning); uncached 88765 + 13065; estimated 0.0000 USD against the Mistral budget

## Figures

- `figures/kept-by-kind.svg`
- `figures/drop-reasons.svg`

Every call is in `calls.jsonl` and every row in `records.jsonl`.
