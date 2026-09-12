# hist-002 (history, 3 connector calls)

## Question

Since when does Mistral's documentation have a model page for Z.ai GLM 5.2?

## Thinking

The user wants to know when the Mistral documentation added a model page for Z.ai GLM 5.2. I need to search the Mistral documentation for this specific model page and track its history. I'll use the mistral_docs_history tool to find when this page was introduced.

I need to correct my approach. The error indicates I can only use one of the parameters. Let me first search for the model page to find its URL, then use the history tool properly.

I found the model page at https://docs.mistral.ai/models/zai-glm-5-2. Now I need to check when this page was added to the documentation. I'll use the history tool with the page URL to track its creation date.

The history tool shows the page was added between 2026-08-01 and 2026-08-15. The model page itself shows a release date of 2026-08-06. Combining these, the documentation page was added shortly after the model's release. I should provide a precise answer based on this information.

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

### 2. mistral_docs_search

```json
{"q": "Z.ai GLM 5.2 model page"}
```

Result:

```
q: "Z.ai GLM 5.2 model page"

[1] https://docs.mistral.ai/models/zai-glm-5-2 | section: links
    Z.ai GLM 5.2 > Links
    - [Blog post](https://z.ai/blog/glm-5.2)
    cite: https://docs.mistral.ai/models/zai-glm-5-2

[2] https://docs.mistral.ai/models/zai-glm-5-2 | section: overview
    Z.ai GLM 5.2 > Overview
    | Field | Value | | --- | --- | | API names | `zai-glm-5-2` | | Slug | `zai-glm-5-2` | | Status | PublicPreview | | Release date | 2026-08-06 | | Version | 5.2 | | Type | Open | | Class | Generalist | | Context length | 1M | | Output token limit | 128k | | Legacy | no |
    cite: https://docs.mistral.ai/models/zai-glm-5-2

[3] https://docs.mistral.ai/models/zai-glm-5-2 | section: capability-matrix
    Z.ai GLM 5.2 > Capability matrix
    See the [model capability matrix](https://docs.mistral.ai/models) for every model that shares these features.
    cite: https://docs.mistral.ai/models/zai-glm-5-2

[4] https://docs.mistral.ai/models/zai-glm-5-2 | section: modalities
    Z.ai GLM 5.2 > Modalities
    - Input: Text - Output: Reasoning, Text
    cite: https://docs.mistral.ai/models/zai-glm-5-2

[5] https://docs.mistral.ai/models/zai-glm-5-2 | section: pricing
    Z.ai GLM 5.2 > Pricing
    - Input: Input: 1.4 USD/M Tokens (1.19 EUR/M Tokens); Cached input: 0.14 USD/M Tokens (0.119 EUR/M Tokens) - Output: Output: 4.4 USD/M Tokens (3.74 EUR/M Tokens)
    cite: https://docs.mistral.ai/models/zai-glm-5-2

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/models/zai-glm-5-2") to read hit 1 on its page
```

### 3. mistral_docs_history

```json
{"page_url": "https://docs.mistral.ai/models/zai-glm-5-2"}
```

Result:

```
history page: https://docs.mistral.ai/models/zai-glm-5-2
absent at 2026-06-01
absent through 2026-08-01
added between 2026-08-01 and 2026-08-15 | https://docs.mistral.ai/models/zai-glm-5-2
same through 2026-09-07 | https://docs.mistral.ai/models/zai-glm-5-2
Results: 8 of 8 stored snapshots
```

## Answer

The Mistral documentation page for **Z.ai GLM 5.2** was added between **August 1, 2026, and August 15, 2026**, as it was absent in the snapshot from August 1, 2026, but present by August 15, 2026. The model's release date is listed as **2026-08-06** in the documentation itself.

[Z.ai GLM 5.2 model page](https://docs.mistral.ai/models/zai-glm-5-2)

