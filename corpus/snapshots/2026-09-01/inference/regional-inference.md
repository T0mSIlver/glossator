---
url: https://docs.mistral.ai/inference/regional-inference
title: Regional inference
breadcrumbs: [Inference]
kind: doc
locale: en
source_path: src/content/en/docs/inference/regional-inference/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Regional inference

Mistral offers **regional inference** as an optional service through [dedicated API endpoints](https://docs.mistral.ai/inference/regional-inference#supported-regions). It supports processing inference requests by systems located within a chosen geography: currently the European Union or the United States.

Use regional inference when you have **data location requirements** for inference inputs and outputs, or when your users are concentrated in a region and want **lower latency**.

> **Info**
>
> Regional inference is billed at **1.1× standard list pricing** (a 10% upcharge) for input tokens, output tokens, cached reads, and cache writes.

## What is regional inference? {#what-is-regional-inference}

Inference is the execution step where a model processes your input and generates output. On Mistral-hosted endpoints, that execution runs on **GPU infrastructure managed by Mistral**.

Regional inference routes that model execution to infrastructure located **within a selected geography**. The request still uses the Mistral API, but the regional endpoint determines where inference processing happens.

Regional inference helps you:

- Control where inference input and output data is processed.
- Support workloads with specific data location requirements.
- Reduce latency when most users or systems are close to the selected geography.

> **Important**
>
> Regional inference does not provide regional storage for all control-plane data. For example, account configuration, API keys, billing, access management, usage analytics, and other operational metadata may still be handled by Mistral systems outside the selected inference geography.
>
> Additionally, if you do not specify a region, the API uses the global Mistral endpoint. Regional inference does not make the Mistral control plane regional.

## What regions are supported? {#supported-regions}

Mistral distinguishes three endpoints:

| Endpoint | Region | Regional upcharge | Geography | When to use it |
|---|---|---|---|---|
| [`api.mistral.ai`](https://api.mistral.ai) | Global | No | Not region-specific | Use the global endpoint when you do not need a specific inference location. Mistral does not commit to a specific inference location for requests sent to this endpoint. |
| [`api.eu.mistral.ai`](https://api.eu.mistral.ai) | EU | Yes | Multiple data centers in EU and EFTA countries | Use the EU regional endpoint to support inference processing within the European Union. |
| [`api.us.mistral.ai`](https://api.us.mistral.ai) | US | Yes | Multiple data centers in the United States | Use the US regional endpoint to support inference processing within the United States. |

## What is supported by regional inference? {#supported-by-regional-inference}

Use regional endpoints only for workloads whose models, tools, and features are available in the target region. Regional endpoints only serve models hosted in that region.

### Limitations {#regional-inference-limitations}

Regional endpoints have feature limitations. If a workload depends on an unsupported feature, the regional processing guarantees for that workload do not apply.

- Not all [tool calls](https://docs.mistral.ai/studio/agents/agent-tools) are currently supported. [Function calling](https://docs.mistral.ai/studio/agents/agent-tools/function-calling) is the only supported regional tool.
- Stateful features, including Agents, Batch, and the Files API, are not available on regional endpoints.
- Available models vary by region.

> **Note**
>
> Before routing traffic to a regional endpoint, check model availability in [Available models](https://docs.mistral.ai/inference/regional-inference#available-models).

### Available models {#available-models}

Regional endpoints only serve models hosted in that region. Use the same model IDs as the global API, but check availability against the regional endpoint before you send production traffic.

To list available models, call `models.list` against the regional base URL or the SDK `server` value for the region.

**Python**

```python
import os
from mistralai.client import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"], server="eu")
models = client.models.list()

for model in models.data:
    print(model.id)
```

**TypeScript**

```typescript
import { Mistral } from "@mistralai/mistralai";

const mistral = new Mistral({
  apiKey: process.env.MISTRAL_API_KEY,
  server: "eu",
});

async function main() {
  const models = await mistral.models.list();

  for (const model of models.data ?? []) {
    console.log(model.id);
  }
}

main();
```

**cURL**

```bash
curl https://api.eu.mistral.ai/v1/models \
  -H "Authorization: Bearer $MISTRAL_API_KEY"
```

## How to configure regional inference {#configure-regional-inference}

Select a regional endpoint by configuring the SDK client or by sending requests to the regional base URL directly.

### SDK version 2.70 or later {#sdk-version}

Use the `server` parameter when initializing the client to specify the region:

**Python**

```python
import os
from mistralai.client import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"], server="eu")
response = client.chat.complete(
    model="mistral-medium-latest",
    messages=[{"role": "user", "content": "What is Mistral?"}],
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

If you use an older SDK, use the `server_url` parameter instead:

```python
import os
from mistralai.client import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"], server_url="https://api.eu.mistral.ai/")
list_models_response = client.models.list()
print(list_models_response)
```

### Use curl {#curl}

```bash
curl https://api.eu.mistral.ai/v1/chat/completions \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-large-latest",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

### Verify regional processing {#verify-region}

The regional endpoint you call is the source of truth for the requested processing geography. For auditability, log the endpoint hostname, SDK `server` value, model ID, timestamp, and response request identifier **for each regional request**.

If you route traffic through a proxy, gateway, or observability tool, keep request logs that show the target base URL (`api.eu.mistral.ai` or `api.us.mistral.ai`). These logs help you confirm that the request was sent to the expected regional endpoint.

## Regional inference and zero data retention {#zero-data-retention}

Regional inference controls where eligible inference requests are processed. Zero data retention controls whether eligible request and response content is retained after processing. These are separate controls, and you may need both depending on your data handling requirements.

To learn how zero data retention works, see [Zero data retention](https://docs.mistral.ai/admin/monitor-comply/zero-data-retention).
