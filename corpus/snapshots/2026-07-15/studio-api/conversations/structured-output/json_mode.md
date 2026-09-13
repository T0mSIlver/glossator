---
url: https://docs.mistral.ai/studio-api/conversations/structured-output/json_mode
title: JSON Mode
breadcrumbs: [Studio, Conversations, Structured Outputs]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/conversations/structured-output/json_mode/page.mdx
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
---

# JSON Mode

Users have the option to set `response_format` to `{"type": "json_object"}` to enable JSON mode.

This mode ensures that the model's response is formatted as a valid JSON object regardless of the content of the prompt, however we still recommend to explicitly ask the model to return a JSON object and the format.

## Usage {#usage}

### How to generate JSON consistently

Below is an example of how to use JSON mode with the Mistral API.

**Python**

**V1**

```python
import os
from mistralai.client import Mistral

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

client = Mistral(api_key=api_key)
messages = [
    {
        "role": "user",
        "content": "What is the best French meal? Return the name and the ingredients in short JSON object.",
    }
]
chat_response = client.chat.complete(
      model = model,
      messages = messages,
      response_format = {
          "type": "json_object",
      }
)
```

**V2**

```python
import os
from mistralai.client import Mistral

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

client = Mistral(api_key=api_key)
messages = [
    {
        "role": "user",
        "content": "What is the best French meal? Return the name and the ingredients in short JSON object.",
    }
]
chat_response = client.chat.complete(
      model = model,
      messages = messages,
      response_format = {
          "type": "json_object",
      }
)
```

**TypeScript**

```typescript
import { Mistral } from "mistralai";

const apiKey = process.env.MISTRAL_API_KEY;

const mistral = new Mistral({apiKey: apiKey});

const chatResponse = await mistral.chat.complete({
model: "mistral-large-latest",
messages: [{role: 'user', content: 'What is the best French meal? Return the name and the ingredients in JSON format.'}],
responseFormat: {type: 'json_object'},
}
);
```

**cURL**

```bash
curl --location "https://api.mistral.ai/v1/chat/completions" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
    "model": "mistral-large-latest",
    "messages": [
     {
        "role": "user",
        "content": "What is the best French cheese? Return the product and produce location in JSON format"
      }
    ],
    "response_format": {"type": "json_object"}
  }'
```

**Output**

```json
{
  "id": "25e3f46176674414a76a173bb9294529",
  "object": "chat.completion",
  "model": "mistral-large-2512",
  "usage": {
    "prompt_tokens": 21,
    "completion_tokens": 107,
    "total_tokens": 128
  },
  "created": 1764347485,
  "choices": [
    {
      "index": 0,
      "message": {
        "content": "{\n  \"meal\": \"Boeuf Bourguignon\",\n  \"ingredients\": [\n    \"beef\",\n    \"red wine (Burgundy)\",\n    \"onions\",\n    \"carrots\",\n    \"garlic\",\n    \"mushrooms\",\n    \"bacon\",\n    \"beef stock\",\n    \"tomato paste\",\n    \"thyme\",\n    \"bay leaf\",\n    \"butter\",\n    \"flour\",\n    \"salt\",\n    \"pepper\"\n  ]\n}",
        "tool_calls": null,
        "prefix": false,
        "role": "assistant"
      },
      "finish_reason": "stop"
    }
  ]
}
```

The output will always be enforced to be valid JSON, and the `content` field will be a stringified JSON object. In this case:

```json
{
  "meal": "Boeuf Bourguignon",
  "ingredients": [
    "beef",
    "red wine (Burgundy)",
    "onions",
    "carrots",
    "garlic",
    "mushrooms",
    "bacon",
    "beef stock",
    "tomato paste",
    "thyme",
    "bay leaf",
    "butter",
    "flour",
    "salt",
    "pepper"
  ]
}
```

## FAQ {#faq}

### Which models support JSON Mode? {#which-models-support-json-mode}

All currently available models except for `codestral-mamba` are supported.
