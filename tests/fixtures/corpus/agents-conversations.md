---
url: https://docs.mistral.ai/agents/conversations
title: Conversations
breadcrumbs:
  - Agents
  - Conversations
kind: doc
locale: en
source_path: src/content/en/docs/agents/conversations/page.mdx
source_commit: 2e094f7
---

# Conversations

The Conversations API holds the state of a multi-turn exchange server-side. You
append an input and receive the outputs it produced; you do not resend the history
on every turn.

## Starting a conversation

```python
# Step 1: start the conversation. The agent id fixes the model, instructions
# and tools for every turn that follows.
conversation = client.beta.conversations.start(
    agent_id="ag_01hz...",
    inputs="Which of our models support function calling?",
)

# Step 2: append a turn. Only the new input is sent; the server already has
# everything before it.
# Note that conversation_id, not agent_id, identifies the thread.
follow_up = client.beta.conversations.append(
    conversation_id=conversation.conversation_id,
    inputs="And which of those also support vision?",
)
```

The lines beginning with `#` above are Python comments inside a fenced block, not
document headings. A chunker that splits on `#` without tracking fences cuts this
example into pieces.

## Outputs

A conversation response carries an `outputs` array rather than `choices`. Each
entry has a `type`: `message.output` for text the model produced,
`function.call` for a tool call it wants you to run, and `tool.execution` for a
built-in tool the server ran itself.

Read the array in order. The last `message.output` is the answer; anything before
it is the work that produced it.

## Built-in tools

An agent can be given connectors that run on Mistral's side: web search, code
execution, image generation, and document library retrieval. These appear in the
output as `tool.execution` entries and need no loop on your part.

Your own functions still round-trip through your application, exactly as in the
chat completions API.

## Streaming

`start_stream` and `append_stream` return the same outputs as server-sent events.
Each event names the output index it belongs to, so a client rendering several
outputs can place deltas without buffering the whole response.

## Choosing between the APIs

Use chat completions when you already keep conversation state, when you need exact
control over every message sent, or when you are porting code written against an
OpenAI-compatible endpoint.

Use conversations when the state is a nuisance rather than a feature: the server
keeps it, the wire payload stays small on long threads, and built-in tools become
available without an execution loop of your own.
