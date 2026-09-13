---
url: https://docs.mistral.ai/studio/workflows/building-workflows/on_behalf_of
title: On-behalf-of workflows
breadcrumbs: [Studio, Workflows, Building Workflows]
kind: doc
locale: en
source_path: src/content/en/docs/studio/workflows/building-workflows/on_behalf_of/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
---

# On-behalf-of workflows

> **Warning**
>
> On-behalf-of workflows require a [hardened deployment](https://docs.mistral.ai/studio/workflows/managing-workflows-in-production/hardened_deployments). They cannot be registered in a non-hardened deployment.

Some workflows need to act **as the user who triggered them** — for example, accessing the user's connectors, querying resources scoped to their workspace, or calling the Mistral API with their identity. On-behalf-of (OBO) mode makes this possible.

When a workflow is marked as OBO, the platform captures the triggering user's identity at execution time and makes it available to the worker. The worker can then obtain short-lived credentials that represent that user, without ever seeing their API key or session token.

## How it works {#how-it-works}

At execution time, the platform attaches the triggering user's identity to the execution context. When an activity requests user credentials, the SDK:

1. Retrieves the execution token from the current workflow context.
2. Exchanges it with the platform for a short-lived JWT representing the triggering user.
3. Injects the JWT into the `Authorization` header of every outgoing request.
4. Caches and refreshes the JWT automatically.

From the activity's perspective, the client behaves like a normal Mistral client — the identity swap is transparent.

## Enabling OBO mode {#enabling-obo-mode}

Set `on_behalf_of=True` on the workflow definition:

**Python**

```python
import mistralai.workflows as workflows

@workflows.workflow.define(name="user_report", on_behalf_of=True)
class UserReportWorkflow:
    @workflows.workflow.entrypoint
    async def run(self, report_type: str) -> dict:
        ...
```

## Using user credentials in activities {#using-user-credentials-in-activities}

Inside an activity, create a Mistral client with `use_executor_credentials=True`:

**Python**

```python
from datetime import timedelta

import mistralai.workflows as workflows
from mistralai.workflows.client import get_mistral_client

@workflows.workflow.define(name="user_search", on_behalf_of=True)
class UserSearchWorkflow:
    @workflows.workflow.entrypoint
    async def run(self, query: str) -> str:
        return await search_with_user_identity(query)

@workflows.activity(start_to_close_timeout=timedelta(seconds=30))
async def search_with_user_identity(query: str) -> str:
    client = get_mistral_client(use_executor_credentials=True)
    response = await client.chat.complete_async(
        model="mistral-medium-latest",
        messages=[{"role": "user", "content": query}],
    )
    return response.choices[0].message.content
```

## Mixing worker and user credentials {#mixing-worker-and-user-credentials}

You can call the Mistral API **as the worker** within an OBO workflow — for example, to ensure requests are rate-limited against the worker's workspace rather than the user's. Create a second client with `use_executor_credentials=False` (the default):

**Python**

```python
@workflows.activity(start_to_close_timeout=timedelta(seconds=30))
async def my_activity(query: str) -> str:
    # Calls the API as the triggering user
    user_client = get_mistral_client(use_executor_credentials=True)

    # Calls the API as the worker (uses the worker's own API key)
    worker_client = get_mistral_client(use_executor_credentials=False)
    ...
```

This lets you choose the right identity on a per-call basis within the same activity.

## Constraints {#constraints}

> **Warning**
>
> `on_behalf_of=True` **cannot** be combined with `schedules`. Scheduled executions have no triggering user, so the identity context would be undefined. This is enforced at both decorator time and registration time.

- The caller must have a full user identity. Executions triggered by API keys without `user_id` / `organization_id` headers are rejected.
- The identity JWT is short-lived and scoped to the execution. If the execution ends, the JWT can no longer be refreshed.
