# Translate run

Status: complete.

## Configuration

- dataset: eval/dev.jsonl
- kind: translate
- model: glm-5.3
- n: 36
- prompt_version: translate-v1
- provider: zai
- seed: 0
- target_language: fr

## Records

- rows: 36, kept: 36
- dataset: eval/dev-fr.jsonl

## Calls

- translate: 36 calls, 10394 prompt + 4051 completion tokens

- total: 36 calls (36 cached), 10394 prompt + 4051 completion tokens (0 reasoning); uncached 0 + 0; estimated 0.0000 USD against the Mistral budget

Every call is in `calls.jsonl` and every row in `records.jsonl`.
