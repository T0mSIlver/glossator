---
url: https://docs.mistral.ai/studio/workflows/building-workflows/mistral_client
title: Mistral client
breadcrumbs: [Studio, Workflows, Building Workflows]
kind: doc
locale: en
source_path: src/content/en/docs/studio/workflows/building-workflows/mistral_client/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# Mistral client

`get_mistral_client()` returns a standard [Mistral SDK client](https://docs.mistral.ai/getting-started/clients) pre-configured with workflow-aware hooks. It handles authentication, telemetry, and observability metadata automatically.

> **Warning**
>
> Always use `get_mistral_client()` inside activities instead of constructing `Mistral(api_key=...)` directly. A vanilla client does not collect workflow-specific telemetry, does not inject observability metadata, and does not support on-behalf-of credentials.

## Quick start {#quick-start}

```python
# ❌ Don't — misses telemetry, observability metadata, and proper auth
from mistralai import Mistral

client = Mistral(api_key="your_api_key")
```

```python
# ✅ Do — automatically configured for workflows
from mistralai.workflows.client import get_mistral_client

client = get_mistral_client()
```

## What it adds {#what-it-adds}

| Feature | Description |
|---------|-------------|
| **Telemetry** | Collects Mistral API telemetry for your workflow traces |
| **Observability metadata** | Adds workflow metadata with execution and activity IDs for workflow tracing |
| **On-behalf-of credentials** | When `use_executor_credentials=True`, calls the Mistral API as the triggering user instead of the worker |
| **Automatic authentication** | Selects the correct credential for your deployment — API key, Service Account token file, or explicit key |

## Telemetry {#telemetry}

When the workflow's OpenTelemetry provider is enabled, `get_mistral_client()` ensures that Mistral API calls automatically appear in your workflow traces.

If telemetry is disabled in the worker configuration, the wiring is skipped silently. See [Observability](https://docs.mistral.ai/studio/workflows/observability) for more telemetry details.

## Observability metadata {#observability-metadata}

Every outgoing HTTP request gets an `x-metadata` JSON header containing:

| Field | Description |
|-------|-------------|
| `execution_id` | The workflow execution ID |
| `run_id` | The workflow run ID |
| `task_id` | The activity ID |
| `attempt` | The retry attempt number |

This metadata links each API call to the exact workflow execution and activity attempt.

## On-behalf-of credentials {#on-behalf-of-credentials}

In [on-behalf-of workflows](https://docs.mistral.ai/studio/workflows/building-workflows/on_behalf_of), you can call the Mistral API as the triggering user instead of the worker.

## Automatic authentication {#automatic-authentication}

`get_mistral_client()` handles authentication automatically. It selects credentials in the following order:

1. **Explicit `api_key` argument** — if you pass `get_mistral_client(api_key="...")`, that key is used directly.
2. **Service Account token file** — if `MISTRAL_SA_TOKEN_PATH` is set, Service Account authentication is used instead of `MISTRAL_API_KEY`.
3. **`MISTRAL_API_KEY` environment variable** — used as a static API key when neither of the above is set.

In most cases you can call `get_mistral_client()` with no arguments — the correct token is resolved automatically from your environment.

## Using with dependency injection {#using-with-dependency-injection}

`get_mistral_client` works as a `Depends()` provider. The worker initializes it once at startup and reuses the same client across all activity executions:

**Python**

```python
import mistralai.workflows as workflows
from mistralai.workflows.client import get_mistral_client
from mistralai.workflows import Depends

@workflows.activity()
async def summarize(text: str, client = Depends(get_mistral_client)) -> str:
    response = await client.chat.complete_async(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": f"Summarize:\n\n{text}"}],
    )
    return response.choices[0].message.content
```

For more on the `Depends()` pattern and provider lifecycle, see [Dependency injection](https://docs.mistral.ai/studio/workflows/building-workflows/dependency_injection).
