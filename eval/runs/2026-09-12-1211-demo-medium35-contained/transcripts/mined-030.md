# mined-030 (api_reference, 6 connector calls)

## Question

Which event types can a streamed conversation emit?

## Thinking

The user is asking about event types for streamed conversations. This is likely a technical question about Mistral's API or SDK. I need to search the Mistral documentation for information about streaming conversations and their event types. I'll use the mistral_docs_search tool with a query that matches the user's question.

The search returned a result about consuming streaming events with a section on event types. This seems relevant. I should read the full page to get the complete list of event types. Let me fetch the page at the URL from the search result.

I've retrieved the page about core concepts and events. Now I need to extract the specific event types for streamed conversations. The documentation shows a table of event types. Let me also check if there are any other relevant pages about chat-specific events. I'll search for "le_chat" or "conversation" event types to see if there's a more specific list for chat streaming.

I've found information about le Chat events, but these seem to be audit log events rather than real-time streaming events. The user is likely asking about the event types emitted during a live chat streaming session, not audit logs. Let me search more specifically for streaming conversation events in the context of chat or messaging.

The search results are still pointing to workflow events and audit logs. Let me try a different approach and search for "streaming conversation" specifically, as the user mentioned "streamed conversation" which might be a specific feature.

I found a page about "Streaming Events" which seems more relevant. Let me read this page to understand the event types for streaming conversations.

Now I have comprehensive information about streaming events. The documentation shows that for streamed conversations (in the context of workflows and activities), there are specific event types. The user asked about "streamed conversation" - in Mistral's ecosystem, this likely refers to the streaming events from workflows and activities, particularly for chat applications. 

Based on the documentation I've gathered:
1. There are workflow execution events (started, completed, failed, canceled, continued as new, task timed out, task failed)
2. There are activity task events (started, completed, retrying, failed)
3. There are custom task events (started, in-progress, completed, failed, timed out, canceled) for long-running activities

The most relevant answer for a streamed conversation would be the combination of workflow, activity, and custom task events. I should present these clearly, organized by category, and include the citations as shown in the documentation.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "event types emitted by a streamed conversation"}
```

Result:

```
q: "event types emitted by a streamed conversation"

[1] https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events | section: event-types
    Consuming Streaming Events > Event types
    The SDK uses typed event responses discriminated by `event_type`. Each event is a Pydantic model (e.g. `WorkflowExecutionCompletedResponse`, `CustomTaskInProgressResponse`) with fields like `event_id`, `event_timestamp`, `workflow_exec_id`, `workflow_name`, and type-specific `attributes`. For the canonical list of workflow and activity event types, see [Core Concepts > Events > Event types](https: …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events#event-types

[2] https://docs.mistral.ai/studio/workflows/getting-started/core_concepts/events | section: event-types
    Events > Event types
    | Type | Emitted when | |------|-------------| | `WORKFLOW_EXECUTION_STARTED` | A workflow execution begins | | `WORKFLOW_EXECUTION_COMPLETED` | A workflow finishes successfully | | `WORKFLOW_EXECUTION_FAILED` | A workflow ends with an unhandled error | | `WORKFLOW_EXECUTION_CANCELED` | A workflow is canceled | | `WORKFLOW_EXECUTION_CONTINUED_AS_NEW` | A workflow resets its history | | `WORKFLOW_T …
    cite: https://docs.mistral.ai/studio/workflows/getting-started/core_concepts/events#event-types

[3] https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference | section: le-chat-events
    Audit logs reference > Event types > le Chat events
    | Event type | Meaning | |---|---| | `le_chat.conversation.created` | Records when a le Chat conversation is created. | | `le_chat.conversation.deleted` | Records when a le Chat conversation is deleted. | | `le_chat.conversation_batch.deleted` | Records when le Chat conversation batch is deleted. | | `le_chat.conversation.public_sharing.enabled` | Records when le Chat conversation public sharing i …
    cite: https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference

[4] https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference | section: event-types
    Audit logs reference > Event types
    Each `event_type` names the action recorded in the audit log. Deprecated events can still appear for older logs.
    cite: https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference#:~:text=Each%20event_type%20names

[5] https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events | section: example-event
    Consuming Streaming Events > Event types > Example Event
    ```json { "stream": "token", "broker_sequence": 1, "timestamp": "2025-01-15T10:30:00Z", "data": { "event_type": "WORKFLOW_EXECUTION_STARTED", "event_id": "evt_abc123", "event_timestamp": 1736938200000000000, "workflow_name": "my-workflow", "workflow_exec_id": "abc123", "root_workflow_exec_id": "abc123", "parent_workflow_exec_id": null, "workflow_run_id": "run_456", "attributes": {} }, "workflow_co …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events#example-event

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events") to read hit 1 on its page
```

### 2. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/workflows/getting-started/core_concepts/events", "section": "event-types"}
```

Result:

```
page: https://docs.mistral.ai/studio/workflows/getting-started/core_concepts/events | "Events" | section: event-types

## section: event-types
    Events > Event types
    cite: https://docs.mistral.ai/studio/workflows/getting-started/core_concepts/events#event-types
## Event types {#event-types}

| Type | Emitted when |
|------|-------------|
| `WORKFLOW_EXECUTION_STARTED` | A workflow execution begins |
| `WORKFLOW_EXECUTION_COMPLETED` | A workflow finishes successfully |
| `WORKFLOW_EXECUTION_FAILED` | A workflow ends with an unhandled error |
| `WORKFLOW_EXECUTION_CANCELED` | A workflow is canceled |
| `WORKFLOW_EXECUTION_CONTINUED_AS_NEW` | A workflow resets its history |
| `WORKFLOW_TASK_TIMED_OUT` | A workflow task exceeds its time limit |
| `WORKFLOW_TASK_FAILED` | A workflow task encounters an error |
| `ACTIVITY_TASK_STARTED` | An activity begins |
| `ACTIVITY_TASK_COMPLETED` | An activity finishes successfully |
| `ACTIVITY_TASK_RETRYING` | An activity is being retried |
| `ACTIVITY_TASK_FAILED` | An activity fails |

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/workflows/getting-started/core_concepts/events", section="history-limits") for the section after it
```

### 3. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference", "section": "le-chat-events"}
```

Result:

```
page: https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference | "Audit logs reference" | section: le-chat-events

## section: le-chat-events
    Audit logs reference > Event types > le Chat events
    cite: https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference
### le Chat events

| Event type | Meaning |
|---|---|
| `le_chat.conversation.created` | Records when a le Chat conversation is created. |
| `le_chat.conversation.deleted` | Records when a le Chat conversation is deleted. |
| `le_chat.conversation_batch.deleted` | Records when le Chat conversation batch is deleted. |
| `le_chat.conversation.public_sharing.enabled` | Records when le Chat conversation public sharing is enabled. |
| `le_chat.conversation.public_sharing.disabled` | Records when le Chat conversation public sharing is disabled. |
| `le_chat.flash_answers.enabled` | Records when le Chat flash answers is enabled. |
| `le_chat.flash_answers.disabled` | Records when le Chat flash answers is disabled. |
| `le_chat.localisation_sharing.enabled` | Records when le Chat localisation sharing is enabled. |
| `le_chat.localisation_sharing.disabled` | Records when le Chat localisation sharing is disabled. |
| `le_chat.memories.enabled` | Records when le Chat memories is enabled. |
| `le_chat.memories.disabled` | Records when le Chat memories is disabled. |
| `le_chat.data.training_enabled` | Records when le Chat data training is enabled. |
| `le_chat.data.training_disabled` | Records when le Chat data training is disabled. |
| `le_chat.actions.external_link` | Records when a user opens an external link from le Chat actions. |

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference", section="studio-events") for the section after it
```

### 4. mistral_docs_search

```json
{"q": "streamed conversation event types chat"}
```

Result:

```
q: "streamed conversation event types chat"

[1] https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference | section: le-chat-events
    Audit logs reference > Event types > le Chat events
    | Event type | Meaning | |---|---| | `le_chat.conversation.created` | Records when a le Chat conversation is created. | | `le_chat.conversation.deleted` | Records when a le Chat conversation is deleted. | | `le_chat.conversation_batch.deleted` | Records when le Chat conversation batch is deleted. | | `le_chat.conversation.public_sharing.enabled` | Records when le Chat conversation public sharing i …
    cite: https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference

[2] https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events | section: event-types
    Consuming Streaming Events > Event types
    The SDK uses typed event responses discriminated by `event_type`. Each event is a Pydantic model (e.g. `WorkflowExecutionCompletedResponse`, `CustomTaskInProgressResponse`) with fields like `event_id`, `event_timestamp`, `workflow_exec_id`, `workflow_name`, and type-specific `attributes`. For the canonical list of workflow and activity event types, see [Core Concepts > Events > Event types](https: …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events#event-types

[3] https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference | section: event-types
    Audit logs reference > Event types
    Each `event_type` names the action recorded in the audit log. Deprecated events can still appear for older logs.
    cite: https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference#:~:text=Each%20event_type%20names

[4] https://docs.mistral.ai/studio/workflows/getting-started/core_concepts/events | section: event-types
    Events > Event types
    | Type | Emitted when | |------|-------------| | `WORKFLOW_EXECUTION_STARTED` | A workflow execution begins | | `WORKFLOW_EXECUTION_COMPLETED` | A workflow finishes successfully | | `WORKFLOW_EXECUTION_FAILED` | A workflow ends with an unhandled error | | `WORKFLOW_EXECUTION_CANCELED` | A workflow is canceled | | `WORKFLOW_EXECUTION_CONTINUED_AS_NEW` | A workflow resets its history | | `WORKFLOW_T …
    cite: https://docs.mistral.ai/studio/workflows/getting-started/core_concepts/events#event-types

[5] https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events | section: example-event
    Consuming Streaming Events > Event types > Example Event
    ```json { "stream": "token", "broker_sequence": 1, "timestamp": "2025-01-15T10:30:00Z", "data": { "event_type": "WORKFLOW_EXECUTION_STARTED", "event_id": "evt_abc123", "event_timestamp": 1736938200000000000, "workflow_name": "my-workflow", "workflow_exec_id": "abc123", "root_workflow_exec_id": "abc123", "parent_workflow_exec_id": null, "workflow_run_id": "run_456", "attributes": {} }, "workflow_co …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events#example-event

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference") to read hit 1 on its page
```

### 5. mistral_docs_search

```json
{"q": "streaming conversation events"}
```

Result:

```
q: "streaming conversation events"

[1] https://docs.mistral.ai/studio/workflows/building-workflows/streaming | section: streaming-events
    Streaming Events
    Stream events in real-time from your workflows and activities to power live UIs, progress indicators, and token-by-token LLM responses. This page covers how to **publish** streaming events from workflow code. To **consume** them from a client, see [Consuming Streaming Events](https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events).
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/streaming

[2] https://docs.mistral.ai/studio/workflows/building-workflows/streaming | section: consume-events
    Streaming Events > Quick start > 2. Consume Events
    See [Consuming Streaming Events](https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events) for details on subscribing to events.
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/streaming#consume-events

[3] https://docs.mistral.ai/studio/workflows/building-workflows/streaming | section: whats-next
    Streaming Events > What's next
    → [Consume events from a client](https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events): subscribe to the stream you just published, with the SDK or the raw HTTP endpoint.
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/streaming#whats-next

[4] https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events | section: event-types
    Consuming Streaming Events > Event types
    The SDK uses typed event responses discriminated by `event_type`. Each event is a Pydantic model (e.g. `WorkflowExecutionCompletedResponse`, `CustomTaskInProgressResponse`) with fields like `event_id`, `event_timestamp`, `workflow_exec_id`, `workflow_name`, and type-specific `attributes`. For the canonical list of workflow and activity event types, see [Core Concepts > Events > Event types](https: …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events#event-types

[5] https://docs.mistral.ai/studio/workflows/building-workflows/streaming | section: token-streaming-llm
    Streaming Events > Publishing Patterns > Token Streaming (LLM)
    The most common pattern: stream tokens as they're generated: **Python** ```python @workflows.activity() async def chat_activity(messages: list) -> dict: initial_state = {"tokens": []} async with Task(type="token-stream", state=initial_state) as task: async for chunk in llm.stream(messages): token = chunk.choices[0].delta.content if token: await task.update_state({"tokens": task.state["tokens"] + [ …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/streaming#token-streaming-llm

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/workflows/building-workflows/streaming") to read hit 1 on its page
```

### 6. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events", "section": "event-types"}
```

Result:

```
page: https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events | "Consuming Streaming Events" | section: event-types

## section: event-types
    Consuming Streaming Events > Event types
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events#event-types
## Event types {#event-types}

The SDK uses typed event responses discriminated by `event_type`. Each event is a Pydantic model
(e.g. `WorkflowExecutionCompletedResponse`, `CustomTaskInProgressResponse`) with fields like
`event_id`, `event_timestamp`, `workflow_exec_id`, `workflow_name`, and type-specific `attributes`.

For the canonical list of workflow and activity event types, see [Core Concepts > Events > Event types](https://docs.mistral.ai/studio/workflows/getting-started/core_concepts/events#event-types). The streaming API additionally surfaces **`CUSTOM_TASK_*`** events emitted from inside activities (started, in-progress, completed, failed, timed out, canceled). Use these to publish progress updates from long-running activities; see [Streaming](https://docs.mistral.ai/studio/workflows/building-workflows/streaming) for how to publish them.

For convenience, here are the event types you'll encounter most often when streaming:

For convenience, here are the event types you'll encounter most often when streaming:

| Event Type                            | Description                    |
| ------------------------------------- | ------------------------------ |
| `WORKFLOW_EXECUTION_STARTED`          | Workflow started               |
| `WORKFLOW_EXECUTION_COMPLETED`        | Workflow finished successfully |
| `WORKFLOW_EXECUTION_FAILED`           | Workflow failed                |
| `WORKFLOW_EXECUTION_CANCELED`         | Workflow was canceled          |
| `WORKFLOW_EXECUTION_CONTINUED_AS_NEW` | Workflow continued as new      |
| `WORKFLOW_TASK_TIMED_OUT`             | Workflow task timed out        |
| `WORKFLOW_TASK_FAILED`                | Workflow task failed           |
| `CUSTOM_TASK_STARTED`                 | Custom task started            |
| `CUSTOM_TASK_IN_PROGRESS`             | Custom task progress update    |
| `CUSTOM_TASK_COMPLETED`               | Custom task completed          |
| `CUSTOM_TASK_FAILED`                  | Custom task failed             |
| `CUSTOM_TASK_TIMED_OUT`               | Custom task timed out          |
| `CUSTOM_TASK_CANCELED`                | Custom task canceled           |
| `ACTIVITY_TASK_STARTED`               | Activity started               |
| `ACTIVITY_TASK_COMPLETED`             | Activity finished              |
| `ACTIVITY_TASK_RETRYING`              | Activity is retrying           |
| `ACTIVITY_TASK_FAILED`                | Activity failed                |

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events", section="example-event") for the section after it
```

## Answer

A **streamed conversation** in Mistral Studio (workflows/activities) can emit the following event types:

### Workflow Execution Events
| Event Type | Description |
|------------|-------------|
| `WORKFLOW_EXECUTION_STARTED` | Workflow started |
| `WORKFLOW_EXECUTION_COMPLETED` | Workflow finished successfully |
| `WORKFLOW_EXECUTION_FAILED` | Workflow failed |
| `WORKFLOW_EXECUTION_CANCELED` | Workflow was canceled |
| `WORKFLOW_EXECUTION_CONTINUED_AS_NEW` | Workflow continued as new |
| `WORKFLOW_TASK_TIMED_OUT` | Workflow task timed out |
| `WORKFLOW_TASK_FAILED` | Workflow task failed |

### Activity Task Events
| Event Type | Description |
|------------|-------------|
| `ACTIVITY_TASK_STARTED` | Activity started |
| `ACTIVITY_TASK_COMPLETED` | Activity finished |
| `ACTIVITY_TASK_RETRYING` | Activity is retrying |
| `ACTIVITY_TASK_FAILED` | Activity failed |

### Custom Task Events (for long-running activities)
| Event Type | Description |
|------------|-------------|
| `CUSTOM_TASK_STARTED` | Custom task started |
| `CUSTOM_TASK_IN_PROGRESS` | Custom task progress update |
| `CUSTOM_TASK_COMPLETED` | Custom task completed |
| `CUSTOM_TASK_FAILED` | Custom task failed |
| `CUSTOM_TASK_TIMED_OUT` | Custom task timed out |
| `CUSTOM_TASK_CANCELED` | Custom task canceled |

---
Each event is a typed Pydantic model with fields like `event_id`, `event_timestamp`, `workflow_exec_id`, `workflow_name`, and type-specific `attributes`.
[Consuming Streaming Events > Event types](https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events#event-types)
[Core Concepts > Events > Event types](https://docs.mistral.ai/studio/workflows/getting-started/core_concepts/events#event-types)

