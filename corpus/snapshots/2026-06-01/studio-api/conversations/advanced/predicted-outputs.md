---
url: https://docs.mistral.ai/studio-api/conversations/advanced/predicted-outputs
title: Predicted outputs
breadcrumbs: [Studio, Conversations, Advanced]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/conversations/advanced/predicted-outputs/page.mdx
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
---

# Predicted Outputs

Predicted Outputs **optimizes response time** by leveraging known or predictable content.
This approach minimizes latency while maintaining high output quality. In tasks such as editing large texts, modifying code, or generating template-based responses, significant portions of the output are often predetermined. By predefining these expected parts with Predicted Outputs, **models can allocate more computational resources to the unpredictable elements, improving overall efficiency.**

## Usage Example {#usage-example}

### Code Modification

**Predicted Outputs shine in scenarios where you need to regenerate text documents or code files with minor modifications.** The key parameter introduced is the `prediction` parameter, which enables users to define predicted outputs. For example, imagine you want your model to update the model used in a chat request. You can include the code snippet you'd like to modify as both the user prompt and the predicted output.

> **Tip**
>
> Before continuing, we recommend reading the [Chat Completions](https://docs.mistral.ai/studio-api/conversations/chat-completion) documentation to learn more about the chat completions API and how to use it before proceeding.

**Python**

**V1**

```python
import os
from mistralai import Mistral

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-2411"

client = Mistral(api_key=api_key)

code = """
response = client.chat.complete(
model="open-mistral-7b",
messages=[
{"role": "user", "content": "Summarize this document."}
]
)
"""

prompt = "Change the model name from open-mistral-7b to open-mistral-nemo. Respond only with code, no explanation, no formatting."

chat_response = client.chat.complete(
  model= model,
  messages = [
    {
      "role": "user",
      "content": prompt,
    },
    {
      "role": "user",
      "content": code
    },
  ],
  prediction = {
    "type": "content",
    "content": code
  }
)
````

**V2**

```python
import os
from mistralai.client import Mistral

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-2411"

client = Mistral(api_key=api_key)

code = """
response = client.chat.complete(
model="open-mistral-7b",
messages=[
{"role": "user", "content": "Summarize this document."}
]
)
"""

prompt = "Change the model name from open-mistral-7b to open-mistral-nemo. Respond only with code, no explanation, no formatting."

chat_response = client.chat.complete(
  model= model,
  messages = [
    {
      "role": "user",
      "content": prompt,
    },
    {
      "role": "user",
      "content": code
    },
  ],
  prediction = {
    "type": "content",
    "content": code
  }
)
````

**TypeScript**

```typescript
import { Mistral } from '@mistralai/mistralai';

const apiKey = process.env.MISTRAL_API_KEY;

const client = new Mistral({apiKey: apiKey});

const code = `
response = client.chat.complete(
    model="open-mistral-7b",
    messages=[
        {"role": "user", "content": "Summarize this document."}
    ]
)
`.trim();

const prompt = `Change the model name from open-mistral-7b to open-mistral-nemo. Respond only with code, no explanation, no formatting.`;

const chatResponse = await client.chat.complete({
    model: "mistral-large-2411",
    messages: [
        {
            role: 'user',
            content: prompt
        },
        {
            role: "user",
            content: code
        },
    ],
    prediction: {
        type: "content",
        content: code
    },
});
````

**cURL**

```bash
curl --location "https://api.mistral.ai/v1/chat/completions" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
    "model": "mistral-large-2411",
    "messages": [
        {"role": "user", "content": "Change the model name from open-mistral-7b to open-mistral-nemo. Respond only with code, no explanation, no formatting."},
        {"role": "user", "content": "$CODE"}
    ],
    "prediction": {
        "type": "content",
        "content": "$CODE"
    }
  }'
```

**Output**

```json
{
  "id": "987f971cf1d24d0cbf88a50e2c850546",
  "created": 1756812876,
  "model": "mistral-large-2411",
  "usage": {
    "prompt_tokens": 153,
    "total_tokens": 270,
    "completion_tokens": 117
  },
  "object": "chat.completion",
  "choices": [
    {
      "index": 0,
      "finish_reason": "stop",
      "message": {
        "role": "assistant",
        "tool_calls": null,
        "content": "```python\nresponse = client.chat.complete(\nmodel=\"open-mistral-nemo\",\nmessages=[\n{\"role\": \"user\", \"content\": \"Summarize this document.\"}\n]\n)\n```"
      }
    }
  ]
}
```

## FAQ {#faq}

### Which model supports predicted outputs? {#which-model-supports-predicted-outputs}

As of now, `codestral-latest` and `mistral-large-2411` support predicted outputs.

### How does predicted outputs affect pricing? {#how-does-predicted-outputs-affect-pricing}

Currently, predicted outputs do not impact pricing.

### Which parameters are not supported when using Predicted Outputs? {#which-parameters-are-not-supported-when-using-predicted-outputs}

`n` (number of completions to return for each request) is not supported when using predicted outputs.

### Does the Position of Certain Sentences or Words in the Prediction Matter? {#does-the-position-of-certain-sentences-or-words-in-the-prediction-matter}

No, the placement of sentences or words in your prediction does not affect its effectiveness. Predictions can appear anywhere within the generated response and still help reduce the API's output latency.
