---
url: https://docs.mistral.ai/studio-api/conversations/structured-output/custom
title: Custom
breadcrumbs: [Studio, Conversations, Structured Outputs]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/conversations/structured-output/custom/page.mdx
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
---

# Custom Structured Outputs

Custom Structured Outputs allow you to ensure the model provides an answer in a very specific JSON format by supplying a clear JSON schema. This approach allows the model to consistently deliver responses with the correct typing and keywords.

## Usage {#usage}

### Generate and Use custom Structured Outputs

Here is an example of how to achieve this using the Mistral AI client and Pydantic/Zod/JSON Schemas:

### Define the Data Model {#define-the-data-model}

First, define the structure of the output using a Pydantic, Zod or a JSON Schema:

**Python**

```python
from pydantic import BaseModel

class Book(BaseModel):
    name: str
    authors: list[str]
```

**TypeScript**

```typescript
import { z } from 'zod';

const Book = z.object({
  name: z.string(),
  authors: z.array(z.string()),
});
```

**curl json schema**

```json
{
  "type": "json_schema",
  "json_schema": {
    "schema": {
      "properties": {
        "name": {
          "title": "Name",
          "type": "string"
        },
        "authors": {
          "items": {
            "type": "string"
          },
          "title": "Authors",
          "type": "array"
        }
      },
      "required": [
        "name",
        "authors"
      ],
      "title": "Book",
      "type": "object",
      "additionalProperties": false
    },
    "name": "book",
    "strict": true
  }
}
```

### Start the completion {#start-the-completion}

Next, make a request and ensure the response adheres to the defined structure using `response_format` set to the corresponding model:

**Python**

**V1**

```python
import os
from mistralai.client import Mistral

api_key = os.environ["MISTRAL_API_KEY"]
model = "ministral-8b-latest"

client = Mistral(api_key=api_key)

chat_response = client.chat.parse(
    model=model,
    messages=[
        {
            "role": "system",
            "content": "Extract the books information."
        },
        {
            "role": "user",
            "content": "I recently read 'To Kill a Mockingbird' by Harper Lee."
        },
    ],
    response_format=Book,
    max_tokens=256,
    temperature=0
)
```

**V2**

```python
import os
from mistralai.client import Mistral

api_key = os.environ["MISTRAL_API_KEY"]
model = "ministral-8b-latest"

client = Mistral(api_key=api_key)

chat_response = client.chat.parse(
    model=model,
    messages=[
        {
            "role": "system",
            "content": "Extract the books information."
        },
        {
            "role": "user",
            "content": "I recently read 'To Kill a Mockingbird' by Harper Lee."
        },
    ],
    response_format=Book,
    max_tokens=256,
    temperature=0
)
```

**TypeScript**

```typescript
import { Mistral } from '@mistralai/mistralai';

const apiKey = process.env.MISTRAL_API_KEY;

const client = new Mistral({ apiKey: apiKey });

const chatResponse = await client.chat.parse({
  model: 'ministral-8b-latest',
  messages: [
    {
      role: 'system',
      content: 'Extract the books information.',
    },
    {
      role: 'user',
      content: "I recently read 'To Kill a Mockingbird' by Harper Lee.",
    },
  ],
  responseFormat: Book,
  maxTokens: 256,
  temperature: 0,
});
```

**cURL**

```bash
curl --location "https://api.mistral.ai/v1/chat/completions" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
    "model": "ministral-8b-latest",
    "messages": [
     {
        "role": "system",
        "content": "Extract the books information."
      },
     {
        "role": "user",
        "content": "I recently read To Kill a Mockingbird by Harper Lee."
      }
    ],
    "response_format": {
      "type": "json_schema",
      "json_schema": {
        "schema": {
          "properties": {
            "name": {
              "title": "Name",
              "type": "string"
            },
            "authors": {
              "items": {
                "type": "string"
              },
              "title": "Authors",
              "type": "array"
            }
          },
          "required": ["name", "authors"],
          "title": "Book",
          "type": "object",
          "additionalProperties": false
        },
        "name": "book",
        "strict": true
      }
    },
    "max_tokens": 256,
    "temperature": 0
  }'
```

**Output**

```json
{
  "id": "feaa11fd78fc4e6584d233c045ffe138",
  "created": 1757442515,
  "model": "ministral-8b-latest",
  "usage": {
    "prompt_tokens": 23,
    "total_tokens": 47,
    "completion_tokens": 24
  },
  "object": "chat.completion",
  "choices": [
    {
      "index": 0,
      "finish_reason": "stop",
      "message": {
        "role": "assistant",
        "tool_calls": null,
        "content": "{\n  \"name\": \"To Kill a Mockingbird\",\n  \"authors\": [\"Harper Lee\"]\n}"
      }
    }
  ]
}
```

In this example, the `Book` class defines the structure of the output, ensuring that the model's response adheres to the specified format.

There are two types of possible outputs that are easily accessible via our SDK.

**Raw JSON Output**

Corresponds to the raw structured JSON output of the model.

**Python**

```python
# Accessed with `chat_response.choices[0].message.content`:
print(chat_response.choices[0].message.content)
# {
#   "authors": ["Harper Lee"],
#   "name": "To Kill a Mockingbird"
# }
```

**TypeScript**

```typescript
// Accessed with `chatResponse.choices[0].message.content`:
console.log(chatResponse.choices[0].message.content);
// {
//   "authors": ["Harper Lee"],
//   "name": "To Kill a Mockingbird"
// }
```

**Parsed Output**

Corresponds to the parsed json object initialized from the `response_format` parameter and the `content` field of the response.
It corresponds to the same object as the defined pydantic/zod model.

**Python**

```python
# converted into a Pydantic object with `chat_response.choices[0].message.parsed`. In this case, it is a `Book` instance:
print(chat_response.choices[0].message.parsed)
# name='To Kill a Mockingbird' authors=['Harper Lee']
```

**TypeScript**

```typescript
// converted into a TypeScript object with `chatResponse.choices[0].message.parsed`. In this case, it is a `Book` object:
console.log(chatResponse.choices[0].message.parsed);
// { name: 'To Kill a Mockingbird', authors: [ 'Harper Lee' ] }
```

> **Note**
>
> To better guide the model, the following is being always prepended to the System Prompt when using this method:
>
> ```
> Your output should be an instance of a JSON object following this schema: {{ json_schema }}
> ```
>
> However, it is recommended to add more explanations and iterate on your system prompt to better clarify the expected schema and behavior.

## FAQ {#faq}

### Which models support custom Structured Outputs? {#which-models-support-custom-structured-outputs}

All currently available models except for `codestral-mamba` are supported.
