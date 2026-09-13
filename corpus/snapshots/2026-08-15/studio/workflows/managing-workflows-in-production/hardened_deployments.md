---
url: https://docs.mistral.ai/studio/workflows/managing-workflows-in-production/hardened_deployments
title: Hardened deployments
breadcrumbs: [Studio, Workflows, Managing Workflows in Production]
kind: doc
locale: en
source_path: src/content/en/docs/studio/workflows/managing-workflows-in-production/hardened_deployments/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
---

# Hardened deployments

A **hardened deployment** is a standard [deployment](https://docs.mistral.ai/studio/workflows/managing-workflows-in-production/deployments) with restricted workflow registration. Only a predefined set of API keys can register workflows in a hardened deployment. A deployment becomes hardened as soon as at least one API key is associated with it.

## The problem {#the-problem}

Workflow execution routing occurs at the deployment level. Multiple workers can register workflows — and even multiple versions of the same workflow — within a single deployment. Once two different workflows are registered under the same name in a deployment, routing becomes **non-deterministic**. There is no way to predict which version will execute for a given input.

This non-determinism poses risks for production environments, where reliability is critical. A misconfigured or accidental re-registration can disrupt deployments and compromise workflow integrity.

[On-behalf-of (OBO) workflows](https://docs.mistral.ai/studio/workflows/building-workflows/on_behalf_of) — which execute under the identity of the triggering user and can access their personal files and connectors — introduce further sensitivity. Unrestricted registration of OBO workflows could expose user resources to unintended or malicious access.

## How hardened deployments work {#how-hardened-deployments-work}

Workspace and organization admins manage hardened deployments through the **Settings** panel in the Mistral console. A deployment becomes hardened when at least one API key is associated with it. From that point, only those registered API keys can register workflows on that deployment.

> **Info**
>
> On-behalf-of workflows **require** a hardened deployment. They cannot be registered in a non-hardened deployment. See [On-behalf-of workflows](https://docs.mistral.ai/studio/workflows/building-workflows/on_behalf_of) for details.

## Benefits {#benefits}

- **Reliable production deployments**: Admins designate a production deployment as hardened, ensuring only trusted API keys can register workflows. This prevents misconfigurations (such as a wrong deployment name) from breaking production workflows.
- **Controlled OBO workflow registration**: OBO workflows cannot be registered in non-hardened deployments, ensuring sensitive workflows are validated by trusted admins before use.
- **Restricted unauthorized registration**: Unless an attacker compromises an admin account, they cannot register malicious OBO workflows in hardened deployments.

## Managing hardened deployments {#managing-hardened-deployments}

Once a deployment is created (upon registration of its first worker), an admin can harden it through the workspace's **Settings** panel under the **Hardened Deployment** section.

Admins can:

- View all current hardened deployments
- Add credentials (API key names and owners) to a deployment
- Remove credentials from a deployment

A deployment can have multiple credentials to support key rotation or multi-worker setups.

> **Tip**
>
> Manage your API keys in the [API keys](https://docs.mistral.ai/admin/identity-access/api-keys) section of the admin panel.

## Registering an OBO workflow {#registering-an-obo-workflow}

Hardening a deployment is a **prerequisite** for registering an OBO workflow. If you attempt to register an OBO workflow in a new deployment, the registration will fail because the deployment is not hardened by default. However, the deployment is still pre-registered during this process.

The worker reports an error containing a link to a pre-configured template in the admin panel. This template lets a workspace admin harden the deployment with the correct credential. Once the admin associates the API key with the deployment, re-registering the worker will succeed.

1. Register the worker with your OBO workflow. The registration fails, but the deployment is created.
2. Open the link from the error message. It leads to the admin panel with a pre-filled hardening template.
3. A workspace admin associates the API key with the deployment.
4. The OBO workflow registers successfully.

> **Warning**
>
> Only a workspace admin can associate an API key with a deployment. If you are not an admin, share the link from the error message with your workspace admin.

> **Tip**
>
> For the code-level details of enabling OBO mode and using user credentials, see [On-behalf-of workflows](https://docs.mistral.ai/studio/workflows/building-workflows/on_behalf_of).
