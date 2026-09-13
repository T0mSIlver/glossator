---
url: https://docs.mistral.ai/studio-api/conversations/advanced/prompt-caching
title: Prompt caching
breadcrumbs: [Studio, Conversations, Advanced]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/conversations/advanced/prompt-caching/page.mdx
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
---

# Prompt caching

Prompt caching lets you reuse previously computed prompt tokens when requests share the same prefix, meaning the same beginning of the prompt. Cached prompt tokens are billed at 10% of the standard input token price, and cache hits can reduce response latency by reusing part of the previous prompt computation.

> **Info**
>
> `prompt_cache_key` increases the chance of a cache hit, but it **doesn't guarantee one**. A cache hit happens when the API finds a compatible cached prefix for the request.

## When to use prompt caching {#when-to-use-prompt-caching}

Use `prompt_cache_key` for multi-turn conversations, repeated system prompts, or workloads that send similar context across requests, such as:

- Multi-turn chat sessions that resend the conversation history.
- Applications that reuse the same system prompt or developer instructions.
- Fill-in-the-middle requests that reuse a long prompt prefix.
- Agent completion requests that reuse the same context across turns.

> **Tip**
>
> Prompt caching is less useful for short prompts, unrelated requests, or requests that change the first part of the prompt on every call.

## Enable prompt caching in your requests {#use-prompt-cache-key}

Set the same `prompt_cache_key` on requests that are likely to share a prefix. Use a stable application-level identifier, such as a conversation ID, session ID, or workflow ID.

Don't include secrets, API keys, or sensitive user data in `prompt_cache_key`.

```bash
curl https://api.mistral.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -d '{
    "model": "mistral-large-latest",
    "prompt_cache_key": "support-session-42",
    "messages": [
      {
        "role": "system",
        "content": "You are a support assistant. Answer with concise troubleshooting steps."
      },
      {
        "role": "user",
        "content": "My API request returns a 401 error. What should I check?"
      }
    ]
  }'
```

For the next turn in the same conversation, keep the same `prompt_cache_key` and preserve the shared prompt prefix in the request body:

```json
{
  "model": "mistral-large-latest",
  "prompt_cache_key": "support-session-42",
  "messages": [
    {
      "role": "system",
      "content": "You are a support assistant. Answer with concise troubleshooting steps."
    },
    {
      "role": "user",
      "content": "My API request returns a 401 error. What should I check?"
    },
    {
      "role": "assistant",
      "content": "Check that your API key is present, valid, and sent in the Authorization header."
    },
    {
      "role": "user",
      "content": "How do I verify that the header is correct?"
    }
  ]
}
```

## Check cached tokens {#check-cached-tokens}

Completion responses report cached prompt tokens in `usage.prompt_tokens_details.cached_tokens`.

```json
{
  "id": "a4db7c530548494f8ff9986bcd2a7737",
  "created": 1773840064,
  "model": "mistral-large-latest",
  "usage": {
    "prompt_tokens": 1013,
    "total_tokens": 1043,
    "completion_tokens": 30,
    "prompt_tokens_details": {
      "cached_tokens": 1008
    }
  },
  "object": "chat.completion",
  "choices": []
}
```

In this response, `prompt_tokens` contains all prompt tokens. The billable uncached input tokens are `prompt_tokens - cached_tokens`.

For this example, billing includes:

- `5` uncached input tokens billed at the standard input token price.
- `1008` cached input tokens billed at 10% of the standard input token price.
- `30` completion tokens billed at the output token price.

If the API doesn't serve tokens from cache, `cached_tokens` is `0` or omitted.

> **Info**
>
> Cache blocks contain 64 tokens. Because of this block size:
>
> - `cached_tokens` is a multiple of 64.
> - Prompts with fewer than 64 prompt tokens do not have cache hits.
> - Longer shared prefixes can reuse more cached tokens.

## Track billing {#track-billing}

Cached tokens are billed at 10% of the standard input token price. To review cached token usage, open [Usage](https://admin.mistral.ai/organization/usage) in Admin and check per model usage.
