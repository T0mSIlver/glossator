---
url: https://docs.mistral.ai/inference/priority-tier
title: Priority Tier
breadcrumbs: [Inference]
kind: doc
locale: en
source_path: src/content/en/docs/inference/priority-tier/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Priority Tier

Priority Tier gives eligible API requests priority queueing for workloads that need more predictable access to shared infrastructure. This page is for enterprise administrators who plan API capacity and developers who add Priority Tier routing to completion requests.

> **Info**
>
> Priority Tier requires account setup with Mistral. Contact your account executive or Mistral contact to configure model-specific Priority Tier rate limits for your organization.

## How Priority Tier works {#how-priority-tier-works}

Priority Tier routes eligible API requests through a priority queue before Standard Tier traffic during periods of high load. It is intended for real-time and business-critical workloads that need predictable access to hosted Mistral models.

Priority Tier availability depends on all of the following:

- Your organization has an active Priority Tier entitlement.
- The request uses a model configured for Priority Tier.
- The request is within your custom Priority Tier rate limits for that model.
- Priority Tier capacity is available for the model and deployment region.

If a request is not eligible for Priority Tier, it can still run as Standard Tier traffic depending on the `service_tier` value you send.

## Compare service tiers {#compare-service-tiers}

| Feature | Batch | Standard Tier | Priority Tier |
|---|---|---|---|
| Use case | Asynchronous processing for workloads that do not need real-time responses | Standard model processing | Real-time and business-critical workloads |
| Latency | Queued for asynchronous processing | Seconds to minutes | Seconds |
| Routing | Batch queue | Best-effort routing | Priority queue |
| Rate limits | Batch processing limits | Usage-based or custom standard limits | Custom Priority Tier limits by model |
| Bursting | Requests are queued and processed over a 24-hour period | Standard rate-limit behavior | Falls back to Standard Tier when Priority Tier limits are exceeded |
| Availability | Global | Global or regional, depending on endpoint and model | Global or regional, depending on account setup, model, and capacity |
| Uptime SLA | Not available | Not available | 99.5% |
| Reliability | High | High to medium | High |

## Request Priority Tier {#request-priority-tier}

Set the `service_tier` request parameter on supported completion requests.

| Value | Behavior |
|---|---|
| `auto` | Uses Priority Tier when your request is eligible. Falls back to Standard Tier when Priority Tier is not available. |
| `standard_only` | Uses Standard Tier and does not consume Priority Tier limits. |

If you omit `service_tier`, the request defaults to `standard_only`.

> **Tip**
>
> Set `service_tier` to `auto` only for requests that should use Priority Tier when it is available. Leave it unset or use `standard_only` for standard traffic.

### Send a Priority Tier request {#send-priority-tier-request}

**cURL**

```bash
curl https://api.mistral.ai/v1/chat/completions \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-medium-latest",
    "service_tier": "auto",
    "messages": [
      {"role": "user", "content": "What is the capital of France?"}
    ]
  }'
```

**Python**

```python
import os
from mistralai import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

response = client.chat.complete(
    model="mistral-medium-latest",
    service_tier="auto",
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?",
        }
    ],
)

print(response.choices[0].message.content)
print(response.usage.service_tier)
```

**TypeScript**

```typescript
import { Mistral } from "@mistralai/mistralai";

const mistral = new Mistral({
  apiKey: process.env.MISTRAL_API_KEY,
});

const response = await mistral.chat.complete({
  model: "mistral-medium-latest",
  serviceTier: "auto",
  messages: [
    { role: "user", content: "What is the capital of France?" },
  ],
});

console.log(response.choices?.[0]?.message?.content);
console.log(response.usage?.serviceTier);
```

The REST API uses `service_tier`. SDK field names may differ by language and version. If your SDK does not accept the field shown here, update to the latest SDK or send the REST request directly.

## Check which tier served a request {#check-served-tier}

The response usage object includes the service tier that processed the request. Use this field to confirm Priority Tier usage, detect fallback to Standard Tier, and monitor unexpected downgrades.

Possible response values are:

| Response value | Meaning |
|---|---|
| `priority` | The request was served with Priority Tier. |
| `standard` | The request was served with Standard Tier. |

Example response excerpt:

```json
{
  "model": "mistral-medium-latest",
  "usage": {
    "prompt_tokens": 22,
    "completion_tokens": 70,
    "total_tokens": 92,
    "service_tier": "priority"
  }
}
```

## Before you start {#before-you-start}

Before you send Priority Tier traffic, make sure you have:

- An API key for the organization configured for Priority Tier.
- An active Priority Tier agreement or account setup.
- Custom Priority Tier rate limits configured for each target model.
- A supported SDK version if you use Python or TypeScript.
- Confirmation that your target model is eligible for Priority Tier.

## Get access to Priority Tier {#get-access}

1. Contact your account executive or Mistral contact.
2. Share your target models and expected traffic profile.
3. Wait for Mistral to configure your custom Priority Tier rate limits.
4. Update eligible requests to set `service_tier` to `auto`.
5. Check the served tier in the response usage object.

> **Note**
>
> If you need more Priority Tier capacity, coordinate with Mistral ahead of time. Capacity increases may require advance notice.

## Quotas and limits {#quotas-and-limits}

Priority Tier limits are custom and model-specific. Your configured limits can include requests per minute, tokens per minute, or other limits agreed with Mistral.

When a request with `service_tier` set to `auto` exceeds your configured Priority Tier limits, the request falls back to Standard Tier instead of failing only because Priority Tier capacity is exhausted.

## Billing and pricing {#billing-and-pricing}

Priority Tier is billed as a premium multiplier on top of Standard Tier list pricing. The multiplier is 1.75x standard list pricing, which is a 75% premium on input, output, and cached tokens.

Priority requests retain full eligibility for prompt caching discounts, up to 90% savings on cached input tokens. The 1.75x multiplier applies after the prompt cache discount is applied.

Requests served as Priority Tier traffic are billed according to your Priority Tier terms. Requests that fall back to Standard Tier are handled as Standard Tier traffic.

## FAQ {#faq}

### What happens if I omit service_tier? {#what-happens-if-i-omit-servicetier}

The request uses `standard_only`. It is served as Standard Tier traffic and does not consume Priority Tier limits.

### What happens when I set service_tier to auto? {#what-happens-when-i-set-servicetier-to-auto}

We attempt to serve the request with Priority Tier. If Priority Tier is not available for that request, we serve it as Standard Tier traffic.

### Why did my request return service_tier: standard? {#why-did-my-request-return-servicetier-standard}

The request was served as Standard Tier traffic. Common causes include exceeded Priority Tier limits, a model that is not eligible for Priority Tier, missing entitlement, expired access, or unavailable Priority Tier capacity.

### Can I use Priority Tier on every model? {#can-i-use-priority-tier-on-every-model}

No. Priority Tier availability is model-specific and depends on your account configuration and available capacity.

### Does Priority Tier work with regional inference? {#does-priority-tier-work-with-regional-inference}

Priority Tier can be configured for global or regional API traffic, depending on your agreement, target model, and available capacity. See [Regional Inference](https://docs.mistral.ai/inference/regional-inference) for regional endpoint details.

### How do I increase my Priority Tier limits? {#how-do-i-increase-my-priority-tier-limits}

Contact your account executive or Mistral contact. Capacity increases may require advance notice.

## Related resources {#related-resources}

- [Regional Inference](https://docs.mistral.ai/inference/regional-inference)
- [Batch Processing](https://docs.mistral.ai/studio-api/batch-processing)
- [SDKs](https://docs.mistral.ai/resources/sdks)
- [API reference](https://docs.mistral.ai/api)
