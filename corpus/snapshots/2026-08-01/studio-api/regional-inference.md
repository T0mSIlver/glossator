---
url: https://docs.mistral.ai/studio-api/regional-inference
title: Regional Inference
breadcrumbs: [Studio]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/regional-inference/page.mdx
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
---

# Regional Inference

Regional inference routes your API requests to models hosted in a specific geographic region. Inference occurs within that region, and processed data doesn't leave it. If you don't specify a region, the API uses the global Mistral endpoint.

## Region groups {#region-groups}

Use a regional endpoint when your application needs requests processed in a specific geographic region. Each region group maps to a dedicated base URL and can include several data centers in that geography.

| Region group | Base URL | Availability | Geography |
|---|---|---|---|
| `eu` | [`api.eu.mistral.ai`](https://api.eu.mistral.ai) | Available | Multiple data centers in EU/EFTA countries |
| `us` | [`api.us.mistral.ai`](https://api.us.mistral.ai) | Coming soon | Multiple data centers in the United States |

## How to use a regional endpoint {#use-regional-endpoint}

### SDK version ≥ 2.70 {#python-sdk-version}

Use the `server` parameter when initializing the client to specify the region:

**Python**

```python
import os
from mistralai.client import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"], server="eu")
response = client.chat.complete(
    model="mistral-medium-latest",
    messages=[{"role": "user", "content": "What is Mistral AI?"}],
)
print(response.choices[0].message.content)
```

**TypeScript**

```typescript
import { Mistral } from "@mistralai/mistralai";

const mistral = new Mistral({
  apiKey: process.env.MISTRAL_API_KEY,
  server: "eu",
});

async function main() {
  const response = await mistral.chat.complete({
    model: "mistral-medium-latest",
    messages: [
      { role: "user", content: "What is the best French cheese?" },
    ],
  });

  console.log(response.choices?.[0]?.message?.content);
}

main();
```

### Older SDK versions {#older-sdk-versions}

If using an older SDK, use the `server_url` parameter instead:

```python
from mistralai.client import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"], server_url="https://api.eu.mistral.ai/")
list_models_response = client.models.list()
print(list_models_response)
```

### Using curl {#curl}

```bash
curl https://api.eu.mistral.ai/v1/chat/completions \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-large-latest",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Available models {#available-models}

Regional endpoints only serve models hosted in that region. Use `models.list` against the regional base URL to see which models are available.

```python
import os
from mistralai.client import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"], server="eu")
models = client.models.list()
for model in models.data:
    print(model.id)
```

## Pricing {#pricing}

Regional inference is billed at **1.1× standard list pricing** (a 10% upcharge) for input tokens, output tokens, cached reads, and cache writes.

## Limitations {#limitations}

- Not all [Tool calls](https://docs.mistral.ai/studio-api/agents/agent-tools) are currently supported. [Function Calling](https://docs.mistral.ai/studio-api/agents/agent-tools/function-calling) is the only supported regional tool.
- **Stateful features** (Agents, Batch, Files API) are not available on regional endpoints.
- Available models vary by region.
