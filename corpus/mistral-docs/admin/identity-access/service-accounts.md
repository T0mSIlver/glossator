---
url: https://docs.mistral.ai/admin/identity-access/service-accounts
title: Service accounts
breadcrumbs: [Admin, Access and permissions]
kind: doc
locale: en
source_path: src/content/en/docs/admin/identity-access/service-accounts/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# Service accounts

A service account is a workspace-scoped non-human identity that a workload, such as a workflow worker, uses to authenticate to the Mistral platform. It is a principal in its own right: it has a name, roles, and its own credentials, and it is not tied to any person.

Running a workload under a service account rather than a team member's API key has two advantages:

- the workload keeps working when that person's key is rotated, or when they leave;
- audit logs and hardened deployments name the workload, not a person.

> **Note**
>
> Use a service account for **machine-to-machine** authentication, such as a workflow worker running in your cluster. Use a [personal API key](https://docs.mistral.ai/admin/identity-access/api-keys) for interactive use, scripts, and development.

## How a workload authenticates {#how-authentication-works}

A service account on its own cannot authenticate. It needs at least one credential, and there are two kinds.

| Credential | How it works | When to use it |
| --- | --- | --- |
| **Workload identity federation** | The workload presents a short-lived token signed by a trusted issuer. The platform verifies it using the issuer's public key. No stored secret. | A workload running in a Kubernetes cluster or behind another OIDC issuer. |
| **API key** | A long-lived key owned by the service account. | A worker running outside of Kubernetes. |

Both are managed from the same place: open the service account and click **Add new authentication**. Workload identity federation has its own setup, covered in [Workload identity federation](https://docs.mistral.ai/admin/identity-access/workload-identity). Adding an API key is covered in [Add an API key](https://docs.mistral.ai/admin/identity-access/service-accounts#add-api-key).

## Create a service account {#create-service-account}

A workspace admin creates the service account.

1. Open [Admin Console > Workspace > Service accounts](https://admin.mistral.ai).
2. Click **Create service account**.
3. Enter a **Name** (unique within the workspace) and an optional **Description**.
4. Click **Create**.

| Field | Required | Notes |
| --- | --- | --- |
| **Name** | Yes | A slug, unique within the workspace: a lowercase letter followed by lowercase letters, digits, or hyphens, 2–63 characters (for example `prod-worker`). Mixed-case input is lowercased. It cannot be changed after creation. |
| **Description** | No | Free text to record what the service account is for. Up to 4096 characters. |

## Roles {#roles}

A new service account has no role by default. A workspace admin grants it one or more roles after creating it, and until it holds at least one it cannot act on the platform.

The roles you can assign today include, for example:

- **`workflow_executor`** — programmatic API access without AI Studio or credential management. Lets a worker register and run workflows.
- **Developer** (`dev`) — everything `workflow_executor` allows, plus AI Studio access and credential management.

**In the Admin Console**

Open the service account, go to its **Roles** section, and select one or more roles. Changes apply immediately.

**With the API**

`PUT /v1/service-accounts/<SERVICE_ACCOUNT_ID>/roles` replaces the account's roles with the ones you pass in `role_ids`. This is a full replacement: any role the account holds that is absent from the list is revoked, and an empty array clears every role. Each entry is a role UUID; fetch the assignable roles and their UUIDs from `GET /v1/service-accounts/assignable-roles`.

```bash
curl -X PUT https://api.mistral.ai/v1/service-accounts/<SERVICE_ACCOUNT_ID>/roles \
  -H "Content-Type: application/json" -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"role_ids": ["<ROLE_UUID>"]}'
```

See [Roles and permissions](https://docs.mistral.ai/admin/identity-access/roles-permissions).

## Add an API key {#add-api-key}

An API key owned by a service account authenticates as that service account, and inherits its roles.

1. Open the service account and click **Add new authentication**.
2. In the **Add credential** dialog, choose **API key**.
3. Optionally enter a **Name** to help you identify the key later.
4. Optionally set an **Expiration**. Leave it empty for a key that never expires.
5. Click **Create API key**.

The key is displayed once, on creation. Copy it and store it in your secret manager. You cannot retrieve it afterwards.

| Field | Required | Notes |
| --- | --- | --- |
| **Name** | No | A label to identify the key later. |
| **Expiration** | No | The last day the key is valid. Your organization can enforce a maximum lifetime. |

> **Note**
>
> The key is scoped to the service account's workspace and to shared connectors only. You cannot move it to another workspace.

> **Warning**
>
> An API key is a standing secret: anyone holding it can act as the service account until the key is deleted or expires. Prefer [workload identity federation](https://docs.mistral.ai/admin/identity-access/workload-identity) when your workload can present an issuer-signed token.

## Manage credentials {#manage}

The two credential types are listed in different places.

- **Workload identity credentials** appear in the **Credentials** list on the service account, with their subject, trusted issuer, and expiry. See [Manage and rotate](https://docs.mistral.ai/admin/identity-access/workload-identity#manage-rotate).
- **API keys** appear in the [API keys](https://docs.mistral.ai/admin/identity-access/api-keys) section for the workspace, alongside keys owned by people. The **Principal** column shows the owning service account and a **Service account** badge.

Deleting a service account removes the identity and its credentials, and any workload using them stops authenticating.

## Service accounts and hardened deployments {#hardened-deployments}

A [hardened deployment](https://docs.mistral.ai/studio/workflows/managing-workflows-in-production/hardened_deployments) restricts which principals can register workflows. You can associate a service account with one, and rotating that service account's workload identity credentials then needs no change to the deployment.

An API key is associated separately, as an API key. If your worker authenticates with a service account's API key, add that key to the hardened deployment as well.

## Related {#related}

- [Workload identity federation](https://docs.mistral.ai/admin/identity-access/workload-identity)

- [Roles and permissions](https://docs.mistral.ai/admin/identity-access/roles-permissions)

- [API keys](https://docs.mistral.ai/admin/identity-access/api-keys)

- [Hardened deployments](https://docs.mistral.ai/studio/workflows/managing-workflows-in-production/hardened_deployments)
