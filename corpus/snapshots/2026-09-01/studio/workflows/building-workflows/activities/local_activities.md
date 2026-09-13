---
url: https://docs.mistral.ai/studio/workflows/building-workflows/activities/local_activities
title: Local activities
breadcrumbs: [Studio, Workflows, Building Workflows, Activities]
kind: doc
locale: en
source_path: src/content/en/docs/studio/workflows/building-workflows/activities/local_activities/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Local activities

Local activities run directly in the workflow worker process, skipping the regular platform scheduling hop. They're useful for fast operations (under 1 second) where scheduling overhead is significant.

## When to use {#when-to-use}

**Good for:**

- Quick computations, validations, data transformations
- High-volume scenarios where latency matters
- Operations completing in under 1 second

**Avoid for:**

- Long-running operations (more than a few seconds)
- External API calls or I/O-heavy tasks
- Operations needing separate retry isolation or scaling

## Basic usage {#basic-usage}

**Python**

```python
from mistralai.workflows import run_activities_locally

@workflows.activity()
async def validate_email(email: str) -> bool:
    return "@" in email

@workflows.workflow.define(name="user-workflow")
class UserWorkflow:
    @workflows.workflow.entrypoint
    async def execute(self, email: str) -> bool:
        with run_activities_locally():
            result = await validate_email(email)
        return result
```

## Mixed execution {#mixed-execution}

Combine local and remote activities:

**Python**

```python
@workflows.workflow.define(name="mixed-workflow")
class MixedWorkflow:
    @workflows.workflow.entrypoint
    async def execute(self, email: str) -> dict:
        # Fast lookup runs locally
        with run_activities_locally():
            domain = await quick_lookup(email)

        # Slow operation runs as regular activity
        verified = await external_api_call(email)

        return {"domain": domain, "verified": verified}
```

## Performance impact {#performance-impact}

Local activities skip remote scheduling and the worker hop, so they typically run much faster than regular activities. Actual latency depends on infrastructure and workflow load.

| Execution mode   | Latency profile        | Best for                    |
| ---------------- | ---------------------- | --------------------------- |
| Local activity   | Sub-millisecond to ms  | Quick computations, lookups |
| Regular activity | Tens to hundreds of ms | API calls, complex logic    |

## Limitations {#limitations}

> **Warning**
>
> **Worker crash risk**: local activities run in the workflow worker process. If a local activity raises an unexpected error, it can crash the worker, affecting all workflows and activities running on it. Unlike regular activities, there is no process-level isolation. Reserve local activities for code you trust to be exception-safe.

**Bypasses standard scheduling:**

- No deployment-level isolation: local activities share resources with workflows.
- Worker process blocking: slow local activities block the workflow worker.
- No independent scaling: local activities cannot scale separately from the worker.

**Activity settings (partial support):**

Timeouts, retry policies, and dependency injection work the same for local activities. The following parameters **do not apply** because local activities already run in the workflow worker process: `sticky_to_worker`, `rate_limit`, `heartbeat_timeout`.

**Python**

```python
@workflows.activity(
    start_to_close_timeout=timedelta(seconds=5),
    retry_policy_max_attempts=3
)
async def timed_local_activity(data: str) -> str:
    # Timeouts and retry policies apply even when running locally.
    # Rate limiting is NOT supported for local activities.
    return data.upper()
```
