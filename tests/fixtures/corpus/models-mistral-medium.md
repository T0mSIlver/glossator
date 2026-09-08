---
url: https://docs.mistral.ai/models/mistral-medium
title: Mistral Medium 3.5
breadcrumbs:
  - Models
  - Mistral Medium 3.5
kind: model
locale: en
source_path: src/schema/models/models/mistral-medium.ts
source_commit: 2e094f7
---

# Mistral Medium 3.5

Mistral Medium 3.5 is the frontier model for general use: the best quality per
euro in the catalogue for reasoning, instruction following and long-context work.
Released 2026-04-28.

## At a glance {#at-a-glance}

| Property | Value |
| --- | --- |
| API name | `mistral-medium-latest` |
| Versioned name | `mistral-medium-2604` |
| Context window | 128,000 tokens |
| Max output | 8,192 tokens |
| Input price | 1.50 USD per million tokens |
| Output price | 7.50 USD per million tokens |
| Knowledge cutoff | 2026-02 |
| Licence | Proprietary, API only |

## Capabilities {#capabilities}

Function calling, structured outputs, document Q&A, vision, reasoning, and
prompt caching are all supported. The model accepts image parts in user messages
and PDF document parts through the document Q&A path.

Reasoning is emitted as a separate segment before the answer, so a client that
renders the raw content stream must skip it or show it as a distinct block.

## When to choose it {#when-to-choose-it}

Choose Mistral Medium 3.5 when answer quality is the constraint: multi-step
reasoning, careful instruction following, grounded answers over retrieved
documents. It is the default for anything user-facing.

Choose Mistral Small 4 when the task is simple classification, extraction or
routing and volume is high; at a tenth of the input price the quality difference
on those tasks is usually not measurable.

Choose Ministral 3 8B when latency dominates and the task is narrow.

## Limits {#limits}

The 128k context window is shared between prompt and completion. A request whose
prompt fills the window returns `finish_reason: "model_length"` without producing
useful output, so budget the completion explicitly with `max_tokens`.

Rate limits are per workspace and published in the console. A 429 carries a
`Retry-After` header; honour it rather than retrying immediately.
