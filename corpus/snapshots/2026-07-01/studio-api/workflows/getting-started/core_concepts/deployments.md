---
url: https://docs.mistral.ai/studio-api/workflows/getting-started/core_concepts/deployments
title: Deployments
breadcrumbs: [Studio, Workflows, Getting Started, Core concepts]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/workflows/getting-started/core_concepts/deployments/page.mdx
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
---

# Deployments

A **deployment** is a named group of [workers](https://docs.mistral.ai/studio-api/workflows/getting-started/core_concepts/workers) that owns a set of workflow definitions and receives all executions for those definitions. Workers join a deployment by setting the `DEPLOYMENT_NAME` environment variable at startup. See [Workers > Starting a worker](https://docs.mistral.ai/studio-api/workflows/getting-started/core_concepts/workers#starting-a-worker) for the launch command.

All workers running under the same `DEPLOYMENT_NAME` form a single deployment. They share identical workflow definitions and collectively receive all executions routed to that deployment.

> **Tip**
>
> Set `DEPLOYMENT_NAME` per environment (for example, `invoice-service-staging` or `invoice-service-prod`) so staging and production workers never compete for the same executions.

## Why deployments? {#why-deployments}

Deployments give you four key capabilities:

- **Worker isolation**: In a shared workspace, each deployment exclusively receives executions for its registered workflows. Multiple teams can run workers simultaneously without interfering with each other.
- **Automatic routing**: When a single active deployment owns a workflow, executions route to it automatically. No manual configuration needed.
- **Horizontal scaling**: Run multiple workers under the same `DEPLOYMENT_NAME` to increase throughput. The platform distributes tasks across all of them automatically.
- **Lifecycle tracking**: A deployment is considered active as long as at least one of its workers has [heartbeated](https://docs.mistral.ai/studio-api/workflows/getting-started/core_concepts/activities#long-running-activities-heartbeats) within the liveness window. Inactive deployments are excluded from routing.
- **Access control**: Restrict workflow registration to specific API keys with [hardened deployments](https://docs.mistral.ai/studio-api/workflows/managing-workflows-in-production/hardened_deployments).

> **Tip**
>
> For a complete guide covering execution routing, conflict detection, and the Deployments API, see [Managing Deployments](https://docs.mistral.ai/studio-api/workflows/managing-workflows-in-production/deployments).
