# hist-004 (history, 7 connector calls)

## Question

Since when do the custom vector store docs describe partial updates through the PatchableIndex protocol?

## Thinking

The user is asking about when the custom vector store documentation started describing partial updates through the PatchableIndex protocol. This is a specific question about the history of Mistral's documentation. I need to search for information about PatchableIndex and its documentation history.

I should use the mistral_docs_history tool to track when this appeared in the documentation. Let me search for "PatchableIndex" in the documentation history.

I got an error because I provided both text and under parameters. The tool requires exactly one of these. Let me try with just the text parameter to find when "PatchableIndex protocol" first appeared in the documentation.

The phrase "PatchableIndex protocol" is not found in any stored snapshot. Let me try a broader search. Maybe the documentation uses slightly different terminology. Let me search for just "PatchableIndex" without "protocol".

Good! The phrase "PatchableIndex" first appears on 2026-09-07 in the changelog at https://docs.mistral.ai/studio/search/search-toolkit/changelog. This suggests that the feature was introduced or documented around that date. However, the user specifically asked about "custom vector store docs" and "partial updates through the PatchableIndex protocol". Let me check the actual vector store documentation to see if there's more context.

The path https://docs.mistral.ai/api/vector-stores doesn't exist at this commit. Let me try a broader search under the API documentation to find where vector store docs are located.

The search didn't find relevant results under /api. The changelog mentioned earlier is at /studio/search/search-toolkit/changelog. Let me search for vector store related documentation more broadly. Maybe the custom vector store docs are under a different path.

Perfect! I found the relevant documentation. The search result shows that the custom vector stores documentation at https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores has a section "partial-updates" that describes the PatchableIndex protocol. Now I need to find out when this section was added. Let me check the history of this specific page.

Excellent! The history shows that the "partial-updates" section was added between 2026-09-01 and 2026-09-07. This means the documentation describing partial updates through the PatchableIndex protocol in the custom vector store docs first appeared during that timeframe. Since the earlier history check showed that "PatchableIndex" first appeared on 2026-09-07 in the changelog, it's likely that the documentation was added on or around September 7, 2026.

The answer is: The custom vector store docs have described partial updates through the PatchableIndex protocol since **September 7, 2026** (or more precisely, between September 1 and September 7, 2026).

## Tool calls

### 1. mistral_docs_history

```json
{"text": "PatchableIndex protocol", "under": "https://docs.mistral.ai/api/vector-stores"}
```

Result:

```
Error executing tool mistral_docs_ca30_mistral_docs_history: error: E_BAD_PARAM
history takes exactly one of text, page_url or under.
next: mistral_docs_history(text="phrase"), mistral_docs_history(page_url="url", section="key") or mistral_docs_history(under="path", since="date").
```

### 2. mistral_docs_history

```json
{"text": "PatchableIndex protocol"}
```

Result:

```
history text: "PatchableIndex protocol"
Results: the phrase is absent from every stored snapshot.
```

### 3. mistral_docs_history

```json
{"text": "PatchableIndex"}
```

Result:

```
history text: "PatchableIndex"
first stored date with the phrase: 2026-09-07 | https://docs.mistral.ai/studio/search/search-toolkit/changelog
last stored date with the phrase: 2026-09-07 | https://docs.mistral.ai/studio/search/search-toolkit/changelog
Results: present in 1 of 8 stored snapshots
```

### 4. mistral_docs_search

```json
{"q": "PatchableIndex protocol partial updates", "under": "https://docs.mistral.ai/api/vector-stores"}
```

Result:

```
pages under https://docs.mistral.ai/api/vector-stores

Results: no page under https://docs.mistral.ai/api/vector-stores at this commit.
next: mistral_docs_search(under="https://docs.mistral.ai/api") lists the pages that do exist there.
```

### 5. mistral_docs_search

```json
{"q": "PatchableIndex protocol partial updates", "under": "https://docs.mistral.ai/api"}
```

Result:

```
q: "PatchableIndex protocol partial updates" | under: https://docs.mistral.ai/api

[1] https://docs.mistral.ai/api/endpoint/workflows/executions | section: operation-update_workflow_execution_v1_workflows_executions_execution_id_updates_post
    Workflows Executions API > Update Workflow Execution
    `POST /v1/workflows/executions/{execution_id}/updates` - Operation id: `update_workflow_execution_v1_workflows_executions__execution_id__updates_post` - Tag: workflows/executions
    cite: https://docs.mistral.ai/api/endpoint/workflows/executions#operation-update_workflow_execution_v1_workflows_executions_execution_id_updates_post

[2] https://docs.mistral.ai/api/endpoint/workflows/executions | section: operation-reset_workflow_v1_workflows_executions_execution_id_reset_post/request-body
    Workflows Executions API > Reset Workflow > Request body
    `application/json` (required), schema `ResetInvocationBody` - `event_id` (integer, required) — The event ID to reset the workflow execution to - `reason` (string or null, optional) — Reason for resetting the workflow execution - `exclude_signals` (boolean, optional) — Whether to exclude signals that happened after the reset point - `exclude_updates` (boolean, optional) — Whether to exclude updates …
    cite: https://docs.mistral.ai/api/endpoint/workflows/executions#operation-reset_workflow_v1_workflows_executions_execution_id_reset_post

[3] https://docs.mistral.ai/api/endpoint/workflows/schedules | section: operation-update_schedule_v1_workflows_schedules_schedule_id_patch/request-body
    Workflows Schedules API > Update Schedule > Request body
    `application/json` (required), schema `WorkflowScheduleUpdateRequest` - `schedule` (PartialScheduleDefinition, required) — Partial schedule definition to update. Unset fields preserve existing values. - `input` (Input, optional) — Input to provide to the workflow when starting it. - `calendars` (array of ScheduleCalendar, optional) — Calendar-based specification of times. - `second` (array of Sche …
    cite: https://docs.mistral.ai/api/endpoint/workflows/schedules#operation-update_schedule_v1_workflows_schedules_schedule_id_patch

Results: 3 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/api/endpoint/workflows/executions") to read hit 1 on its page
```

### 6. mistral_docs_search

```json
{"q": "custom vector store PatchableIndex partial updates"}
```

Result:

```
q: "custom vector store PatchableIndex partial updates"

[1] https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores | section: partial-updates
    Custom vector stores > Optional partial updates
    A backend can also expose partial updates without a full re-index by implementing the optional `PatchableIndex` protocol. This protocol can change one metadata value or one chunk's embedding without chunking and indexing the full document again. Implement `patch_chunk` and `patch_document`: ```python from mistralai.search.toolkit.search import PatchableIndex class MyVectorStore(VectorStoreIndex): …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores#partial-updates

[2] https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores | section: custom-vector-stores
    Custom vector stores
    Implement a custom storage backend by subclassing `VectorStoreIndex` (or `KeywordStoreIndex` for keyword search) and implementing its three methods: ```python from mistralai.search.toolkit.context import IngestContext, RetrievalContext from mistralai.search.toolkit.search import VectorStoreIndex, VectorSearchQuery, SearchResult from mistralai.search.toolkit.document import Document class MyVectorS …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores

[3] https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores | section: agentic-operations
    Custom vector stores > Optional agentic operations
    Beyond indexing and search, a backend can expose positional navigation by implementing the optional, `@runtime_checkable` `NavigableIndex` protocol. A store that doesn't implement the protocol doesn't advertise the capability, and callers gate access with `isinstance`.
    cite: https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores#agentic-operations

[4] https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores | section: agentic-operations/navigableindex
    Custom vector stores > Optional agentic operations > `NavigableIndex`
    These methods provide positional navigation over a chunk-per-document index. An agent can move to adjacent chunks, read a span, fetch a chunk by ID, and search within a source. In agentic `open` and `navigate` loops, the model keeps only an opaque `chunk_id` from a search result, and the server resolves its position. ```python from mistralai.search.toolkit.search import NavigableIndex, NavigationD …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores#agentic-operations

[5] https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores | section: see-also
    Custom vector stores > See also
    - **[Search index](https://docs.mistral.ai/studio/search/search-toolkit/search-index)**: the built-in backends. - **[Vespa](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa)** and **[Postgres](https://docs.mistral.ai/studio/search/search-toolkit/search-index/postgres)**: the built-in implementations, useful as reference for your own.
    cite: https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores#see-also

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores") to read hit 1 on its page
```

### 7. mistral_docs_history

```json
{"page_url": "https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores", "section": "partial-updates"}
```

Result:

```
history page: https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores | section: partial-updates
absent at 2026-06-01
absent through 2026-09-01
added between 2026-09-01 and 2026-09-07 | https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores#partial-updates
Results: 8 of 8 stored snapshots
```

## Answer

The **custom vector store documentation** first describes partial updates through the **`PatchableIndex` protocol** in the section [`partial-updates`](https://docs.mistral.ai/studio/search/search-toolkit/search-index/custom-vector-stores#partial-updates). This section was **added between September 1, 2026, and September 7, 2026**.

Thus, the documentation has included this feature **since September 7, 2026**.

