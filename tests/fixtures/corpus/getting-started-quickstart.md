---
url: https://docs.mistral.ai/getting-started/quickstart
title: Quickstart
breadcrumbs:
  - Getting started
  - Quickstart
kind: doc
locale: en
source_path: src/content/en/docs/getting-started/quickstart/page.mdx
source_commit: 2e094f7
---

# Quickstart

Get your first request to the Mistral AI platform working in under five minutes.
You need a Mistral account and an API key.

## Create an API key {#create-an-api-key}

Sign in to the console, open **API Keys**, and create a key. Keys are shown once;
store the value in a secret manager rather than in source control.

Export the key in your shell so the SDKs pick it up automatically:

```bash
export MISTRAL_API_KEY="your-key-here"
```

## Install a client {#install-a-client}

The Python and TypeScript clients are the supported entry points. Both wrap the
same REST API, so anything described in the API reference is reachable from either.

```bash
pip install mistralai
```

```bash
npm install @mistralai/mistralai
```

## Make your first request {#make-your-first-request}

The chat completions endpoint takes a list of messages and returns one or more
choices. The `model` field selects which model answers.

```python
from mistralai import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
response = client.chat.complete(
    model="mistral-medium-latest",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
)
print(response.choices[0].message.content)
```

The response carries a `usage` object with `prompt_tokens`, `completion_tokens`
and `total_tokens`. Those are the numbers your bill is computed from, so log them
from the start rather than adding the instrumentation later.

## Stream a response {#stream-a-response}

Streaming returns server-sent events as the model produces them, which is what
you want for anything a person is waiting on. The first token typically arrives in
a fraction of the time the full completion takes.

```python
stream = client.chat.stream(
    model="mistral-medium-latest",
    messages=[{"role": "user", "content": "Write a haiku about latency."}],
)
for chunk in stream:
    print(chunk.data.choices[0].delta.content, end="")
```

Every streamed chunk has the same shape as a non-streamed choice, except that the
content arrives on `delta` instead of `message`. The final event carries the usage
totals for the whole completion.

## Next steps {#next-steps}

- Read the [function calling guide](https://docs.mistral.ai/capabilities/function-calling) to let a model call your code.
- Read the [embeddings guide](https://docs.mistral.ai/capabilities/embeddings) to build search over your own documents.
- Browse the [model catalogue](https://docs.mistral.ai/models) to pick a model for your latency and cost budget.
