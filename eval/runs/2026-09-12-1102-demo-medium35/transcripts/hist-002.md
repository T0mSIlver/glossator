# hist-002 (history, 2 connector calls)

## Question

Since when does Mistral's documentation have a model page for Z.ai GLM 5.2?

## Thinking

The user is asking about when Mistral's documentation added a model page for Z.ai GLM 5.2. I need to check the documentation history to find when this specific page was added. I should use the mistral_docs_history tool to track this. I'll search for the exact phrase "Z.ai GLM 5.2" in the documentation history.

I got an error because I provided both text and under parameters. The tool requires exactly one of these. Let me try with just the text parameter to search for the phrase "Z.ai GLM 5.2" across all documentation.

The history tool returned that the phrase "Z.ai GLM 5.2" first appeared on 2026-08-15 at the URL https://docs.mistral.ai/models/zai-glm-5-2. This means the model page was added on August 15, 2026. The user asked "Since when" which means they want the first appearance date. I should provide this date clearly.

## Tool calls

### 1. mistral_docs_history

```json
{"text": "Z.ai GLM 5.2", "under": "https://docs.mistral.ai"}
```

Result:

```
Error executing tool mistral_docs_ca30_mistral_docs_history: error: E_BAD_PARAM
history takes exactly one of text, page_url or under.
next: mistral_docs_history(text="phrase"), mistral_docs_history(page_url="url", section="key") or mistral_docs_history(under="path", since="date").
```

### 2. mistral_docs_history

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

The Mistral documentation has had a model page for **Z.ai GLM 5.2** since **August 15, 2026** ([model page](https://docs.mistral.ai/models/zai-glm-5-2)).

