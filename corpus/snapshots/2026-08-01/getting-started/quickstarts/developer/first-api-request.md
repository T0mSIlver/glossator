---
url: https://docs.mistral.ai/getting-started/quickstarts/developer/first-api-request
title: Send your first API request
breadcrumbs: [Getting started, Quickstarts, Developer]
kind: doc
locale: en
source_path: src/content/en/docs/getting-started/quickstarts/developer/first-api-request/page.mdx
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
---

# Send your first API request

Create an API key, install the SDK, and send a chat completion request.

- Install the Python or TypeScript SDK
- Send a request to a Mistral model
- Print the model's response

Everything here is the foundation for the agent and RAG quickstarts that follow.

**Time to complete:** ~5 minutes

## Prerequisites {#prerequisites}

- Python 3.9+ **or** Node.js 18+ installed on your machine.
- A Mistral AI account. [Create account](https://console.mistral.ai)
- A Mistral API key. Studio is enabled in Free mode by default, with no credit card required. Follow the [Activate Studio and generate an API key](https://docs.mistral.ai/getting-started/quickstarts/studio/activate-and-generate-api-key) quickstart if you don't have one yet.

## Step 1: Get your API key {#step-1}

1. Open [API keys](https://console.mistral.ai/api-keys).
2. Click **Create new key**.
3. Give the key a name (for example, `quickstart`) and click **Create**.
4. Copy the key to your clipboard. The key appears only once; if you lose it, generate a new one.
5. Set the key as an environment variable in your terminal:

**macOS / Linux**

```bash
export MISTRAL_API_KEY="your_api_key_here"
```

**Windows (PowerShell)**

```powershell
$env:MISTRAL_API_KEY="your_api_key_here"
```

## Step 2: Install the SDK {#step-2}

**Python**

```bash
pip install mistralai
```

**TypeScript**

```bash
npm install @mistralai/mistralai
```

## Step 3: Send your first request {#step-3}

Create a file and add the following code:

**Python**

```python
# quickstart.py
import os
from mistralai.client import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

response = client.chat.complete(
    model="mistral-large-latest",
    messages=[
        {"role": "user", "content": "What is Mistral AI?"}
    ],
)

print(response.choices[0].message.content)
```

**TypeScript**

```typescript
// quickstart.ts
import { Mistral } from '@mistralai/mistralai';

const client = new Mistral({ apiKey: process.env.MISTRAL_API_KEY });

const response = await client.chat.complete({
  model: 'mistral-large-latest',
  messages: [
    { role: 'user', content: 'What is Mistral AI?' }
  ],
});

console.log(response.choices[0].message.content);
```

**cURL**

```bash
curl https://api.mistral.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -d '{
    "model": "mistral-large-latest",
    "messages": [
      {"role": "user", "content": "What is Mistral AI?"}
    ]
  }'
```

## Step 4: Run it {#step-4}

**Python**

```bash
python quickstart.py
```

**TypeScript**

```bash
npx tsx quickstart.ts
```

## Verify {#verify}

The terminal prints a short description of Mistral AI. If it doesn't, check the error table below.

| Error | Cause | Fix |
| --- | --- | --- |
| `401 Unauthorized` | API key is incorrect or not set | Run `echo $MISTRAL_API_KEY` to confirm the variable is set |
| `402 Payment Required` | No payment method on account | Add one at [Subscriptions > Billing](https://admin.mistral.ai/organization/billing) |
| `429 Too Many Requests` | Rate limit hit | Wait and retry with exponential backoff |

## What's next {#whats-next}

- [Build an agent with tools](https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent)

- [RAG with document search](https://docs.mistral.ai/getting-started/quickstarts/developer/rag-document-search)
