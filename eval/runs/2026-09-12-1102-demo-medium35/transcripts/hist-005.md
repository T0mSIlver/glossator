# hist-005 (history, 1 connector calls)

## Question

Has the Reasoning guide always lived at /studio/conversations/reasoning? If not, where was it before and when did it move?

## Thinking

The user is asking about the history of the Reasoning guide's location in Mistral's documentation. They want to know:
1. If it has always been at /studio/conversations/reasoning
2. If not, where it was before
3. When it moved

I need to use the mistral_docs_history tool to track changes to this specific page or path. I should search for the path "/studio/conversations/reasoning" and see its history. Let me start by checking the history of that specific path.

The history tool shows that the page at `/studio/conversations/reasoning` was moved from `/studio-api/conversations/reasoning` between August 1-15, 2026. This means the Reasoning guide was previously at `/studio-api/conversations/reasoning` and moved to its current location in early August 2026.

Let me verify this by checking if there's any additional information about this move. The result shows:
- The page moved from `/studio-api/conversations/reasoning` to `/studio/conversations/reasoning`
- This happened between August 1-15, 2026

So the answer is: No, it hasn't always been at `/studio/conversations/reasoning`. It was previously at `/studio-api/conversations/reasoning` and moved between August 1-15, 2026.

I should provide a clear, direct answer with the specific information.

## Tool calls

### 1. mistral_docs_history

```json
{"under": "/studio/conversations/reasoning"}
```

Result:

```
history under: https://docs.mistral.ai/studio/conversations/reasoning | since: 2026-06-01
between 2026-06-01 and 2026-06-15: no change
between 2026-06-15 and 2026-07-01: no change
between 2026-07-01 and 2026-07-15: no change
between 2026-07-15 and 2026-08-01: no change
between 2026-08-01 and 2026-08-15: 1 moved
  moved | https://docs.mistral.ai/studio/conversations/reasoning | 9 sections
    from: https://docs.mistral.ai/studio-api/conversations/reasoning
    cite: https://docs.mistral.ai/studio/conversations/reasoning
between 2026-08-15 and 2026-09-01: no change
between 2026-09-01 and 2026-09-07: no change
Results: 1 changes over 7 intervals
```

## Answer

No, the Reasoning guide has not always lived at `/studio/conversations/reasoning`.

It was previously located at **`/studio-api/conversations/reasoning`** and moved to its current location between **August 1–15, 2026**.

[History of the move](https://docs.mistral.ai/studio/conversations/reasoning)

