---
url: https://docs.mistral.ai/models
title: Model capability matrix
breadcrumbs:
  - Models
kind: model
locale: en
source_path: src/schema/models/models/*.ts
source_commit: 2e094f7
---

# Model capability matrix

Which model supports which feature, derived from the model catalogue. A blank cell
means the feature is not available on that model, not that it is untested.

## Text models {#text-models}

| Model | Context | Function calling | Structured outputs | Document Q&A | Vision | Reasoning |
| --- | --- | --- | --- | --- | --- | --- |
| [`mistral-medium-latest`](https://docs.mistral.ai/models/mistral-medium) | 128k | yes | yes | yes | yes | yes |
| `mistral-large-latest` | 128k | yes | yes | yes | yes | yes |
| `mistral-small-latest` | 128k | yes | yes | yes | yes | |
| `ministral-8b-latest` | 128k | yes | yes | yes | | |
| `ministral-3b-latest` | 128k | yes | yes | | | |
| `magistral-medium-latest` | 40k | yes | yes | yes | yes | yes |
| `magistral-small-latest` | 40k | yes | yes | yes | yes | yes |
| `pixtral-large-latest` | 128k | yes | yes | yes | yes | |
| `pixtral-12b` | 128k | yes | yes | yes | yes | |
| `open-mistral-nemo` | 128k | yes | yes | | | |
| `mistral-saba-latest` | 32k | yes | yes | | | |
| `devstral-medium-latest` | 256k | yes | yes | | | |
| `devstral-small-latest` | 256k | yes | yes | | | |

## Code models {#code-models}

| Model | Context | Fill in the middle | Function calling | Structured outputs |
| --- | --- | --- | --- | --- |
| `codestral-latest` | 256k | yes | yes | yes |
| `codestral-mamba-latest` | 256k | yes | | |
| `devstral-medium-latest` | 256k | | yes | yes |

## Embedding and specialised models {#embedding-and-specialised-models}

| Model | Purpose | Dimensions | Max input |
| --- | --- | --- | --- |
| `mistral-embed` | Text embeddings | 1024 | 8192 |
| `mistral-embed-dim256-2510` | Text embeddings | 256 | 8192 |
| `mistral-embed-dim128-2510` | Text embeddings | 128 | 8192 |
| `codestral-embed` | Code embeddings | 1536 | 8192 |
| `mistral-ocr-latest` | Document OCR | -- | -- |
| `mistral-moderation-latest` | Content moderation | -- | 8192 |

## Reading the matrix {#reading-the-matrix}

**Function calling** means the model accepts a `tools` array and may answer with
`tool_calls`. **Structured outputs** means it accepts a JSON schema in
`response_format` and is constrained to it. **Document Q&A** means it accepts
document parts in a user message. **Vision** means it accepts image parts.
**Reasoning** means the model emits a separate thinking segment before its answer.

Availability changes with each release. The matrix is generated from the catalogue
at the commit recorded in this page's frontmatter, so treat an old copy as a
snapshot rather than as current fact.
