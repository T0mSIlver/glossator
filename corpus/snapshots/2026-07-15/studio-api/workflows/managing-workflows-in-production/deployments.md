---
url: https://docs.mistral.ai/studio-api/workflows/managing-workflows-in-production/deployments
title: Deployments
breadcrumbs: [Studio, Workflows, Managing Workflows in Production]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/workflows/managing-workflows-in-production/deployments/page.mdx
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
---

# Deployments

A deployment is a named group of workers that owns a set of workflow definitions and receives all executions for those definitions. It enables worker isolation in shared workspaces and automatic execution routing.

## Setting DEPLOYMENT_NAME {#setting-deployment_name}

`DEPLOYMENT_NAME` is **required** at worker startup. The worker fails immediately at boot if it is not set.

```bash
DEPLOYMENT_NAME=invoice-service MISTRAL_API_KEY=your-key uv run python worker.py
```

Valid characters: alphanumeric, hyphens, underscores (max 128 characters).

`WORKER_NAME` identifies the individual worker process and is visible in the console and API. It defaults to `socket.gethostname()`.

## Worker Isolation {#worker-isolation}

In a shared workspace, multiple developers can run workers simultaneously without interfering. Each deployment only receives executions for the workflow definitions it registered.

```bash
# Developer A
DEPLOYMENT_NAME=alice MISTRAL_API_KEY=shared-key uv run python worker.py

# Developer B
DEPLOYMENT_NAME=bob MISTRAL_API_KEY=shared-key uv run python worker.py
```

Alice's runs land on Alice's workers. Bob's runs land on Bob's workers.

## Execution Routing {#execution-routing}

When only one active deployment owns a workflow, executions route automatically — no extra configuration needed:

```python
execution = await client.execute_workflow(
    workflow_identifier="invoice_processor",
    input_data=InputData(invoice_id="INV-001"),
)
```

When two active deployments register the same workflow name, the platform cannot route automatically and returns `409 Conflict`:

```json
{
  "code": "AMBIGUOUS_WORKFLOW",
  "deployments": ["alice", "bob"]
}
```

Resolve by passing `deployment_name` explicitly:

```python
execution = await client.execute_workflow(
    workflow_identifier="invoice_processor",
    deployment_name="alice",
    input_data=InputData(invoice_id="INV-001"),
)
```

## Conflict Detection {#conflict-detection}

When a worker registers a workflow name already owned by a different active deployment, the platform warns immediately. Registration is not blocked — the warning is returned in the registration response and appears in worker logs:

```json
{
  "warnings": [
    "Workflow 'invoice_processor' is also registered by active deployment 'bob'"
  ]
}
```

The conflict resolves automatically when one of the deployments becomes inactive (its workers stop).

Multiple workers in the **same** deployment registering the same definitions is horizontal scaling — no warning is produced.

> **Tip**
>
> To restrict which API keys can register workflows in a deployment, see [Hardened deployments](https://docs.mistral.ai/studio-api/workflows/managing-workflows-in-production/hardened_deployments).

## Deployment Lifecycle {#deployment-lifecycle}

A deployment is **active** while at least one of its workers has heartbeated within the liveness window. Workers heartbeat every ~10 seconds automatically. When all workers stop, the deployment becomes **inactive** after the liveness window lapses (50 seconds in production, configurable).

Inactive deployments do not receive executions and are not counted as conflicting when checking for ambiguity.

## Horizontal Scaling {#horizontal-scaling}

Run multiple workers under the same `DEPLOYMENT_NAME` to increase throughput. Executions are distributed across all active workers in the deployment.

For production, deploy workers as a Kubernetes `Deployment` or `StatefulSet` with replicas pointing at the same `DEPLOYMENT_NAME`. The platform load-balances tasks automatically.

## Listing Deployments {#listing-deployments}

List all active deployments in your workspace:

**Python**

```python
from mistralai.client import Mistral

client = Mistral(api_key="your_api_key")

response = client.workflows.deployments.list_deployments()
for deployment in response.deployments:
    print(deployment.name, deployment.is_active)
```

**cURL**

```bash
curl https://api.mistral.ai/v1/workflows/deployments \
  -H "Authorization: Bearer $MISTRAL_API_KEY"
```

**Output**

```json
{
  "deployments": [
    {
      "id": "019d2585-21fc-7063-90ae-31a283c784a1",
      "name": "invoice-service",
      "is_active": true,
      "created_at": "2026-03-25 15:02:55.234755+00:00",
      "updated_at": "2026-04-02 17:42:34.960883+00:00"
    }
  ]
}
```

Pass `workflow_name` to filter by workflow, or `active_only=false` to include inactive deployments.

Inspect a specific deployment and its individual workers:

**Python**

```python
deployment = client.workflows.deployments.get_deployment(name="invoice-service")
print(deployment.name, deployment.is_active)
for worker in deployment.workers:
    print(worker.name, worker.updated_at)
```

**cURL**

```bash
curl https://api.mistral.ai/v1/workflows/deployments/invoice-service \
  -H "Authorization: Bearer $MISTRAL_API_KEY"
```

**Output**

```json
{
  "id": "019d2585-21fc-7063-90ae-31a283c784a1",
  "name": "invoice-service",
  "is_active": true,
  "created_at": "2026-03-25 15:02:55.234755+00:00",
  "updated_at": "2026-04-02 17:42:41.828219+00:00",
  "workers": [
    {
      "name": "my-worker-host",
      "created_at": "2026-03-25 15:15:07.911486+00:00",
      "updated_at": "2026-04-02 15:42:13.679937+00:00"
    }
  ]
}
```
