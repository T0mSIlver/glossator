# mined2-010 (single_page, 2 connector calls)

## Question

Mistral announced a model called Devstral 2 but the API lists `devstral-2512`, `devstral-latest`, `devstral-medium-latest` and more — which identifier is Devstral 2?

## Thinking

The user is asking about Mistral's Devstral 2 model and its API identifier. They've noticed that the API lists several model identifiers like `devstral-2512`, `devstral-latest`, `devstral-medium-latest`, and they want to know which one corresponds to Devstral 2.

I need to search the Mistral documentation to find information about Devstral 2 and its model identifiers. I'll start with a search query that combines the model name and the identifiers mentioned.

The search results show that there's a page for "Devstral 2" at `https://docs.mistral.ai/models/devstral-2-25-12`. The first hit indicates that Devstral 2 has API names including `devstral-2512`, `devstral-latest`, and `devstral-medium-latest`. This directly answers the user's question.

Let me read the full page to confirm this information and provide a complete answer.

The user asks which API identifier corresponds to the "Devstral 2" model. Based on the Mistral documentation I retrieved:

From the search results and the page content, I can see that:
- The model "Devstral 2" has a documentation page at `https://docs.mistral.ai/models/devstral-2-25-12`
- In the Overview section, it explicitly lists the API names as: `devstral-2512`, `devstral-latest`, `devstral-medium-latest`
- The slug is `devstral-2-25-12`
- The version is 25.12

So all three identifiers (`devstral-2512`, `devstral-latest`, `devstral-medium-latest`) refer to the same Devstral 2 model. The primary identifier appears to be `devstral-2512` based on the version number.

The answer is clear: all three identifiers point to Devstral 2, with `devstral-2512` being the most specific one tied to version 25.12.

I should provide a direct, clear answer and cite the documentation.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "Devstral 2 model identifier devstral-2512 devstral-latest devstral-medium-latest"}
```

Result:

```
q: "Devstral 2 model identifier devstral-2512 devstral-latest devstral-medium-latest"

[1] https://docs.mistral.ai/models/devstral-2-25-12 | section: overview
    Devstral 2 > Overview
    | Field | Value | | --- | --- | | API names | `devstral-2512`, `devstral-latest`, `devstral-medium-latest` | | Slug | `devstral-2-25-12` | | Status | Deprecated | | Release date | 2025-12-09 | | Version | 25.12 | | Type | Open | | Class | Specialist | | Context length | 256k | | Legacy | yes |
    cite: https://docs.mistral.ai/models/devstral-2-25-12

[2] https://docs.mistral.ai/models/devstral-small-2-25-12 | section: overview
    Devstral Small 2 > Overview
    | Field | Value | | --- | --- | | API names | `labs-devstral-small-2512`, `devstral-small-latest` | | Slug | `devstral-small-2-25-12` | | Status | Deprecated | | Release date | 2025-12-09 | | Version | 25.12 | | Type | Labs | | Class | Specialist | | Context length | 256k | | Legacy | yes |
    cite: https://docs.mistral.ai/models/devstral-small-2-25-12

[3] https://docs.mistral.ai/models/devstral-2-25-12 | section: weights
    Devstral 2 > Weights
    - Weights, 123B parameters, license Modified MIT, context 256k — [weights](https://huggingface.co/mistralai/Devstral-2-123B-Instruct-2512)
    cite: https://docs.mistral.ai/models/devstral-2-25-12

[4] https://docs.mistral.ai/models/devstral-small-2-25-12 | section: weights
    Devstral Small 2 > Weights
    - Weights, 24B parameters, license Apache 2.0, context 256k — [weights](https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512)
    cite: https://docs.mistral.ai/models/devstral-small-2-25-12

[5] https://docs.mistral.ai/models | section: all-models
    Model capability matrix > All models
    | Model | API names | Status | Context | Release date | | --- | --- | --- | --- | --- | | [Codestral](https://docs.mistral.ai/models/codestral-24-05) | `codestral-2405` | Retired | 32k | 2024-05-29 | | [Codestral](https://docs.mistral.ai/models/codestral-25-01) | `codestral-2501` | Retired | 128k | 2025-01-13 | | [Codestral](https://docs.mistral.ai/models/codestral-25-08) | `codestral-2508`, `code …
    cite: https://docs.mistral.ai/models
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/models", section="all-models") reads this section

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/models/devstral-2-25-12") to read hit 1 on its page
```

### 2. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/models/devstral-2-25-12"}
```

Result:

```
page: https://docs.mistral.ai/models/devstral-2-25-12 | "Devstral 2"

## section: devstral-2
    Devstral 2
    cite: https://docs.mistral.ai/models/devstral-2-25-12
# Devstral 2

Our frontier code agents model for solving software engineering tasks; excels at using tools to explore codebases, editing multiple files and power software engineering agents.

## section: overview
    Devstral 2 > Overview
    cite: https://docs.mistral.ai/models/devstral-2-25-12
## Overview

| Field | Value |
| --- | --- |
| API names | `devstral-2512`, `devstral-latest`, `devstral-medium-latest` |
| Slug | `devstral-2-25-12` |
| Status | Deprecated |
| Release date | 2025-12-09 |
| Version | 25.12 |
| Type | Open |
| Class | Specialist |
| Context length | 256k |
| Legacy | yes |

## section: modalities
    Devstral 2 > Modalities
    cite: https://docs.mistral.ai/models/devstral-2-25-12
## Modalities

- Input: Text
- Output: Text

## section: features
    Devstral 2 > Features
    cite: https://docs.mistral.ai/models/devstral-2-25-12
## Features

- [Structured Outputs](https://docs.mistral.ai/studio/conversations/structured-output) (`structured-outputs`)
- [Function Calling](https://docs.mistral.ai/studio/conversations/function-calling) (`function-calling`)
- [Document QnA](https://docs.mistral.ai/studio/document-processing/document_qna) (`document-qna`)
- [Prefix](https://docs.mistral.ai/studio/conversations/chat-completion#other-useful-features) (`prefix`)
- [Chat Completions](https://docs.mistral.ai/studio/conversations/chat-completion) (`chat-completions`)
- [Batching](https://docs.mistral.ai/studio/batch-processing) (`batching`)

## section: pricing
    Devstral 2 > Pricing
    cite: https://docs.mistral.ai/models/devstral-2-25-12
## Pricing

- Input: 0.4 USD/M Tokens (0.35 EUR/M Tokens)
- Output: 2.0 USD/M Tokens (1.75 EUR/M Tokens)

## section: weights
    Devstral 2 > Weights
    cite: https://docs.mistral.ai/models/devstral-2-25-12
## Weights

- Weights, 123B parameters, license Modified MIT, context 256k — [weights](https://huggingface.co/mistralai/Devstral-2-123B-Instruct-2512)

## section: lifecycle
    Devstral 2 > Lifecycle
    cite: https://docs.mistral.ai/models/devstral-2-25-12
## Lifecycle

- Deprecation date: 2026-05-22
- Retirement date: 2026-07-31
- Replacement: Mistral Medium 3.5

## section: links
    Devstral 2 > Links
    cite: https://docs.mistral.ai/models/devstral-2-25-12
## Links

- [Blog post](https://mistral.ai/news/devstral-2-vibe-cli)
- [Playground](https://console.mistral.ai/build/playground)

## section: capability-matrix
    Devstral 2 > Capability matrix
    cite: https://docs.mistral.ai/models/devstral-2-25-12#:~:text=See%20the%20model
## Capability matrix

See the [model capability matrix](https://docs.mistral.ai/models) for every model that shares these features.

Results: 9 sections, the whole page.
```

## Answer

The model **Devstral 2** is identified in the API by the following names:
- `devstral-2512`
- `devstral-latest`
- `devstral-medium-latest`

All three identifiers refer to the same Devstral 2 model (version 25.12).

[Devstral 2 > Overview](https://docs.mistral.ai/models/devstral-2-25-12)

