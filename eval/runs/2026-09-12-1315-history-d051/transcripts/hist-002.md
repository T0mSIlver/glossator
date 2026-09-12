# hist-002 (history, 1 connector calls)

## Question

Since when does Mistral's documentation have a model page for Z.ai GLM 5.2?

## Thinking

The user is asking about when a specific model page (Z.ai GLM 5.2) appeared in Mistral's documentation. This is a historical question about documentation changes. I need to use the mistral_docs_history tool to track when this page was added or changed.

I should search for the phrase "Z.ai GLM 5.2" in the documentation history. Since this is about a model page, it's likely under the models section of the documentation. I'll use the text parameter to search for this exact phrase.

Let me call the history tool with text="Z.ai GLM 5.2" to find when this first appeared.

The user asks: "Since when does Mistral's documentation have a model page for Z.ai GLM 5.2?"

I used the `mistral_docs_history` tool to search for the phrase "Z.ai GLM 5.2" in the documentation history.

The tool returned:
- first stored date with the phrase: 2026-08-15 | https://docs.mistral.ai/models/zai-glm-5-2
- last stored date with the phrase: 2026-09-07 | https://docs.mistral.ai/models/zai-glm-5-2
- Results: present in 3 of 8 stored snapshots

This means the model page for Z.ai GLM 5.2 first appeared in Mistral's documentation on August 15, 2026.

I should provide a clear, direct answer with the date and the source.

## Tool calls

### 1. mistral_docs_history

```json
{"text": "Z.ai GLM 5.2"}
```

Result:

```
history text: "Z.ai GLM 5.2"
first stored date with the phrase: 2026-08-15 | https://docs.mistral.ai/models/zai-glm-5-2
last stored date with the phrase: 2026-09-07 | https://docs.mistral.ai/models/zai-glm-5-2
Results: present in 3 of 8 stored snapshots
```

## Answer

Mistral's documentation has had a model page for **Z.ai GLM 5.2** since **August 15, 2026** ([model page](https://docs.mistral.ai/models/zai-glm-5-2)).

