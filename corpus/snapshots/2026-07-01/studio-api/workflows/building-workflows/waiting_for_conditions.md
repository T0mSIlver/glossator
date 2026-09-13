---
url: https://docs.mistral.ai/studio-api/workflows/building-workflows/waiting_for_conditions
title: Waiting for Conditions
breadcrumbs: [Studio, Workflows, Building Workflows]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/workflows/building-workflows/waiting_for_conditions/page.mdx
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
---

# Waiting for Conditions

Workflows can pause execution until a specific condition is met, enabling event-driven patterns like human-in-the-loop and approval flows.

The condition predicate is typically flipped by a [signal](https://docs.mistral.ai/studio-api/workflows/interacting-with-workflows/signals) sent from outside the workflow (an API call, another service, a UI action). The workflow stays suspended at no compute cost until the predicate becomes `True` or the timeout fires.

> **Tip**
>
> **Building a chat-style interaction?** Use [`wait_for_input()`](https://docs.mistral.ai/studio-api/workflows/interacting-with-workflows/conversational_workflows) from `InteractiveWorkflow` instead. It's a built-in primitive for prompting the user and waiting for a reply — no signal definition or custom predicate needed, with built-in support for structured forms, confirmations, and timeouts.

## Common patterns {#common-patterns}

The same `wait_condition` primitive supports several recurring use cases:

- **Approval flows** — wait for a human to approve or reject (signal-driven). See the example below.
- **External callback** — wait for a third-party webhook or job to mark the workflow as ready to proceed.
- **Polling-with-backoff (rare)** — wait for an in-workflow flag flipped by another coroutine; usually better expressed as an activity that does the polling itself.

If your case is HITL-heavy, also see [Signals](https://docs.mistral.ai/studio-api/workflows/interacting-with-workflows/signals) for how to define and send the trigger.

## Basic usage {#basic-usage}

Use `workflow.wait_condition()` to block until a predicate returns `True`:

**Python**

```python
from datetime import timedelta
from mistralai.workflows import workflow

await workflow.wait_condition(
    lambda: self.ready,
    timeout=timedelta(minutes=5)
)
```

## Example: approval flow {#example-approval-flow}

Combine with signals to implement a human-in-the-loop pattern:

**Python**

```python
import asyncio
import mistralai.workflows as workflows
from mistralai.workflows import workflow
from datetime import timedelta

@workflows.workflow.define(name="approval_workflow")
class ApprovalWorkflow:
    def __init__(self):
        self.approved = False

    @workflows.workflow.signal(name="approve")
    async def approve(self) -> None:
        self.approved = True

    @workflows.workflow.entrypoint
    async def run(self, request_id: str) -> str:
        try:
            # Wait up to 24 hours for the `approve` signal to flip self.approved
            await workflow.wait_condition(
                lambda: self.approved,
                timeout=timedelta(hours=24),
            )
        except asyncio.TimeoutError:
            return f"Request {request_id} timed out"

        return f"Request {request_id} approved"
```

## Timeout behavior {#timeout-behavior}

When a timeout is specified, `wait_condition` raises `asyncio.TimeoutError` if the condition is not met within the duration. Handle this to implement timeout logic:

**Python**

```python
import asyncio

try:
    await workflow.wait_condition(
        lambda: self.ready,
        timeout=timedelta(minutes=30)
    )
except asyncio.TimeoutError:
    # Handle timeout
    return "Operation timed out"
```
