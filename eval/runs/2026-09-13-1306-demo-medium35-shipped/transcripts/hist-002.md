# hist-002 (history, 3 connector calls)

## Question

Since when does Mistral's documentation have a model page for Z.ai GLM 5.2?

## Thinking

The user is asking about when Mistral's documentation started having a model page for Z.ai GLM 5.2. This is a historical question about documentation changes. I need to use the mistral_docs_history tool to track when this specific model page appeared.

Let me search for information about Z.ai GLM 5.2 in the Mistral documentation first to see if such a page exists, and then I can track its history.

The search results show that there is indeed a model page for Z.ai GLM 5.2 at https://docs.mistral.ai/models/zai-glm-5-2. Now I need to find out when this page was added to the documentation. I'll use the mistral_docs_history tool to track the creation date of this specific page.

I got an error. The tool requires the `under` parameter when using `since`. Let me try a different approach - I'll track the page directly without the `since` parameter to see its full history.

Perfect! The history tool shows that the page was:
- Absent at 2026-06-01
- Absent through 2026-08-01
- Added between 2026-08-01 and 2026-08-15
- Same through 2026-09-07

So the model page for Z.ai GLM 5.2 was added to Mistral's documentation between August 1, 2026, and August 15, 2026. The release date shown in the search results was 2026-08-06, which falls within this interval.

The answer should be the interval: between 2026-08-01 and 2026-08-15.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "Z.ai GLM 5.2 model page", "max_hits": 5}
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

### 2. mistral_docs_history

```json
{"page_url": "https://docs.mistral.ai/models/zai-glm-5-2", "since": "2026-01-01"}
```

Result:

```
Error executing tool mistral_docs_ca30_mistral_docs_history: error: E_BAD_PARAM
since requires under.
next: mistral_docs_history(under="path", since="date").
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

The model page for **Z.ai GLM 5.2** was added to Mistral's documentation **between August 1, 2026, and August 15, 2026** (first appearing in the snapshot interval after 2026-08-01).

*Source: [Documentation history for /models/zai-glm-5-2](https://docs.mistral.ai/models/zai-glm-5-2)*

