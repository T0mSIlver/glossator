---
url: https://docs.mistral.ai/studio-api/workflows/getting-started/core_concepts/events
title: Events
breadcrumbs: [Studio, Workflows, Getting Started, Core concepts]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/workflows/getting-started/core_concepts/events/page.mdx
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
---

# Events

Every significant action in a workflow's lifetime produces an **event**: the workflow started, an activity was scheduled, an activity completed, a signal was received, the workflow finished. These events are recorded in order, forming an append-only log called the **execution history**.

## Why events matter {#why-events-matter}

The execution history is what makes durable execution possible. It is the source of truth for a workflow's state. When a worker needs to resume a workflow (after a crash, a restart, or a task reassignment), it replays the execution history from the beginning.

During replay, workflow code runs again from the top, but completed activities are not re-executed: their results are read back from the history. The workflow arrives back at exactly the point where it was interrupted, with no recovery code on your part.

Reliable replay depends on workflow code being deterministic. See [Workflows > Determinism](https://docs.mistral.ai/studio-api/workflows/getting-started/core_concepts/workflows#determinism) for the constraint and how the SDK enforces it.

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

## History limits {#history-limits}

Each execution history is bounded: **51,200 events** or **50MB**, whichever comes first. For workflows that run for a very long time or process very large volumes of work, the platform provides a mechanism called [**continue-as-new**](https://docs.mistral.ai/studio-api/workflows/building-workflows/continue_as_new), which allows a workflow to carry its essential state forward into a fresh history without interrupting its execution.

> **Note**
>
> The events described here are **execution history events**: the internal record of workflow progress used for durability and replay. The platform also supports **streaming events** that can be consumed in real time by external systems. These are a separate concept covered in [Streaming](https://docs.mistral.ai/studio-api/workflows/building-workflows/streaming).
