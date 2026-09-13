---
url: https://docs.mistral.ai/studio/conversations/chat-completion/prompt-registry
title: Using prompts in chat completions
breadcrumbs: [Studio, Conversations, Chat completions]
kind: doc
locale: en
source_path: src/content/en/docs/studio/conversations/chat-completion/prompt-registry/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Using prompts in chat completions

The [Prompt Registry](https://docs.mistral.ai/api/#tag/beta.prompts) lets you store, version, and manage prompts centrally in Studio. This guide shows how to retrieve a stored prompt and use it as the system message in a chat completion.

## Basic usage {#basic-usage}

Fetch the prompt by name or ID, extract its content, and pass it as the system message.

**Python**

**V1**

```python
import os
from mistralai.client import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

prompt = client.beta.prompts.get(prompt_id="coding-assistant")
system_content = prompt.definition.content

response = client.chat.complete(
    model="mistral-large-latest",
    messages=[
        {"role": "system", "content": system_content},
        {"role": "user", "content": "Help me debug this function."},
    ],
)
print(response.choices[0].message.content)
```

**V2**

```python
import os
from mistralai.client import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

prompt = client.beta.prompts.get(prompt_id="coding-assistant")
system_content = prompt.definition.content

response = client.chat.complete(
    model="mistral-large-latest",
    messages=[
        {"role": "system", "content": system_content},
        {"role": "user", "content": "Help me debug this function."},
    ],
)
print(response.choices[0].message.content)
```

**TypeScript**

```typescript
import { Mistral } from '@mistralai/mistralai';

const client = new Mistral({ apiKey: process.env.MISTRAL_API_KEY });

const prompt = await client.beta.prompts.get({ promptId: 'coding-assistant' });
const systemContent = prompt.definition?.content ?? '';

const response = await client.chat.complete({
  model: 'mistral-large-latest',
  messages: [
    { role: 'system', content: systemContent },
    { role: 'user', content: 'Help me debug this function.' },
  ],
});
console.log(response.choices[0].message.content);
```

## Template variables {#template-variables}

Prompts can contain `{{variable}}` placeholders. Replace them before passing the content to the completion.

For example, a prompt stored as:

```text
You are a coding assistant. You specialise in {{language}}.
```

Can be used like this:

**Python**

**V1**

```python
prompt = client.beta.prompts.get(prompt_id="coding-assistant")
system_content = prompt.definition.content.replace("{{language}}", "Python")
```

**V2**

```python
prompt = client.beta.prompts.get(prompt_id="coding-assistant")
system_content = prompt.definition.content.replace("{{language}}", "Python")
```

**TypeScript**

```typescript
const prompt = await client.beta.prompts.get({ promptId: 'coding-assistant' });
const systemContent = (prompt.definition?.content ?? '').replace('{{language}}', 'Python');
```

## Pinning a version {#pinning-a-version}

By default, `get` returns the latest version of a prompt. Pin a specific version or alias to prevent production behavior from changing when a prompt is updated.

**Python**

**V1**

```python
# Pin by version number
prompt = client.beta.prompts.get(prompt_id="coding-assistant", version=3)

# Pin by alias
prompt = client.beta.prompts.get(prompt_id="coding-assistant", alias="production")
```

**V2**

```python
# Pin by version number
prompt = client.beta.prompts.get(prompt_id="coding-assistant", version=3)

# Pin by alias
prompt = client.beta.prompts.get(prompt_id="coding-assistant", alias="production")
```

**TypeScript**

```typescript
// Pin by version number
const prompt = await client.beta.prompts.get({ promptId: 'coding-assistant', version: 3 });

// Pin by alias
const prompt = await client.beta.prompts.get({ promptId: 'coding-assistant', alias: 'production' });
```

> **Tip**
>
> Use named aliases like `production` or `staging` to decouple your code from version numbers. You can update which version an alias points to from Studio without changing your application.
