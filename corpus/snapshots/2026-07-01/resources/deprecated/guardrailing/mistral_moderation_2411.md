---
url: https://docs.mistral.ai/resources/deprecated/guardrailing/mistral_moderation_2411
title: Mistral Moderation 2411
breadcrumbs: [Resources, Deprecated features, Moderation & Guardrailing]
kind: doc
locale: en
source_path: src/content/en/docs/resources/deprecated/guardrailing/mistral_moderation_2411/page.mdx
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
---

# Mistral Moderation 2411

> **Warning**
>
> **Deprecated**: `mistral-moderation-2411` is deprecated. Migrate to [`mistral-moderation-2603`](https://docs.mistral.ai/studio-api/safety-moderation) and update any `moderation_llm_v1` guardrail configs to `moderation_llm_v2`.

## Model {#model}

`mistral-moderation-2411` has been superseded by `mistral-moderation-2603`, which introduces updated policy categories (`Dangerous`, `Criminal`, `Jailbreaking`).

## Policy Categories {#policy-categories}

| Category | Description |
| --- | --- |
| Sexual | Material that explicitly depicts, describes, or promotes sexual activities, nudity, or sexual services. |
| Hate and Discrimination | Content expressing prejudice or hostility against individuals or groups based on protected characteristics. |
| Violence and Threats | Content that describes, glorifies, incites, or threatens physical violence against individuals or groups. |
| Dangerous and Criminal Content | Content that promotes illegal activities or extremely hazardous behaviors. *(Legacy — replaced by separate `Dangerous` and `Criminal` categories in `mistral-moderation-2603`.)* |
| Self-Harm | Content that promotes or encourages deliberate self-injury, suicide, or eating disorders. |
| Health | Content that contains or tries to elicit detailed or tailored medical advice. |
| Financial | Content that contains or tries to elicit detailed or tailored financial advice. |
| Law | Content that contains or tries to elicit detailed or tailored legal advice. |
| PII | Content that requests or shares personal identifying information. |

## Custom Guardrails (moderation_llm_v1) {#custom-guardrails}

The `moderation_llm_v1` guardrail config is backed by `mistral-moderation-2411`. It is deprecated — use `moderation_llm_v2` instead.

```json
{
  "block_on_error": true,
  "moderation_llm_v1": {
    "custom_category_thresholds": {
      "sexual": 0.1,
      "selfharm": 0.1
    },
    "ignore_other_categories": false,
    "action": "block"
  }
}
```

A blocked request returns `403` with:

```json
{
  "error": {
    "message": "Content blocked by guardrail",
    "status": 403
  },
  "guardrails": {
    "results": {
      "moderation_llm_v1": {
        "model_name": "mistral-moderation-2411",
        "decisions": {
          "sexual": { "threshold": 0.1, "score": 0.3, "violated": true },
          "selfharm": { "threshold": 0.1, "score": 0.05, "violated": false }
        },
        "violated": true,
        "action": "block"
      }
    }
  }
}
```
