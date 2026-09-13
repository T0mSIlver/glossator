# mined-030 (api_reference, 3 connector calls)

## Question

Which event types can a streamed conversation emit?

## Thinking

The user is asking about event types that a streamed conversation can emit. This is a specific technical question about Mistral's API or SDK. I need to search the documentation for information about streaming conversations and their event types. Let me use the mistral_docs_search tool to find relevant information.

The search returned results about workflow events and audit logs, but the user specifically asked about "streamed conversation" event types. The first result mentions "Consuming Streaming Events > Event types" which seems most relevant. Let me read the full page to get the complete list of event types.

The first page I read only contains workflow execution event types, but the user asked about "streamed conversation" event types. The search results also mentioned a page about "Consuming Streaming Events" which might be more relevant. Let me read that page to see if it contains the specific event types for streamed conversations.

Now I have the information from the "Consuming Streaming Events" page. This page lists both workflow/activity event types and custom task event types that are emitted during streaming. The user asked about "streamed conversation" event types, and this appears to be the relevant information. Let me compile the complete list from the documentation.

The documentation shows two categories:
1. Core workflow and activity event types (WORKFLOW_EXECUTION_*, ACTIVITY_TASK_*)
2. Custom task event types (CUSTOM_TASK_*) that are specifically surfaced by the streaming API

I should present this information clearly, organized by category, and include the citation to the documentation source.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "streamed conversation event types", "max_hits": 5}
```

Result:

```
q: "streamed conversation event types"

[1] https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events | section: event-types
    Consuming Streaming Events > Event types
    The SDK uses typed event responses discriminated by `event_type`. Each event is a Pydantic model (e.g. `WorkflowExecutionCompletedResponse`, `CustomTaskInProgressResponse`) with fields like `event_id`, `event_timestamp`, `workflow_exec_id`, `workflow_name`, and type-specific `attributes`. For the canonical list of workflow and activity event types, see [Core Concepts > Events > Event types](https: …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events#event-types

[2] https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference | section: le-chat-events
    Audit logs reference > Event types > le Chat events
    | Event type | Meaning | |---|---| | `le_chat.conversation.created` | Records when a le Chat conversation is created. | | `le_chat.conversation.deleted` | Records when a le Chat conversation is deleted. | | `le_chat.conversation_batch.deleted` | Records when le Chat conversation batch is deleted. | | `le_chat.conversation.public_sharing.enabled` | Records when le Chat conversation public sharing i …
    cite: https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference

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

For a **streamed conversation**, the following event types can be emitted:

### Core Workflow & Activity Events
| Event Type | Description |
|------------|-------------|
| `WORKFLOW_EXECUTION_STARTED` | Workflow execution begins |
| `WORKFLOW_EXECUTION_COMPLETED` | Workflow finishes successfully |
| `WORKFLOW_EXECUTION_FAILED` | Workflow ends with an unhandled error |
| `WORKFLOW_EXECUTION_CANCELED` | Workflow is canceled |
| `WORKFLOW_EXECUTION_CONTINUED_AS_NEW` | Workflow resets its history |
| `WORKFLOW_TASK_TIMED_OUT` | Workflow task exceeds its time limit |
| `WORKFLOW_TASK_FAILED` | Workflow task encounters an error |
| `ACTIVITY_TASK_STARTED` | Activity begins |
| `ACTIVITY_TASK_COMPLETED` | Activity finishes successfully |
| `ACTIVITY_TASK_RETRYING` | Activity is being retried |
| `ACTIVITY_TASK_FAILED` | Activity fails |

### Custom Task Events (Streaming-Specific)
| Event Type | Description |
|------------|-------------|
| `CUSTOM_TASK_STARTED` | Custom task started |
| `CUSTOM_TASK_IN_PROGRESS` | Custom task progress update |
| `CUSTOM_TASK_COMPLETED` | Custom task completed |
| `CUSTOM_TASK_FAILED` | Custom task failed |
| `CUSTOM_TASK_TIMED_OUT` | Custom task timed out |
| `CUSTOM_TASK_CANCELED` | Custom task canceled |

[Event types](https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events#event-types)

