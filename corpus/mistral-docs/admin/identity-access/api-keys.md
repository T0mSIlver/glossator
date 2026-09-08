---
url: https://docs.mistral.ai/admin/identity-access/api-keys
title: API keys
breadcrumbs: [Admin, Access and permissions]
kind: doc
locale: en
source_path: src/content/en/docs/admin/identity-access/api-keys/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# API keys

API keys authenticate requests to the Mistral API and other Mistral tools. In Admin, Organization Admins can create, review, rotate, and delete API keys across Workspaces.

Developers can create and manage their own API keys from their User Profile modal in Studio. Vibe-only users usually do not need API keys unless they also use Studio, the API, Vibe Code, or another developer tool.

## API key types {#key-types}

API keys can be associated with different product areas:

| Type | Use |
| --- | --- |
| **Studio** | Standard API keys for Mistral API usage. |
| **Vibe** | Keys used by Vibe Code. |
| **Mistral Code** | Legacy keys for earlier Mistral Code usage. |

## Create an API key as an admin {#create-key-admin}

1. Open [Admin Panel > API > API Keys](https://admin.mistral.ai/plateforme/api-keys).
2. Select `Create new key`.
3. Optionally enter a `Key name`.
4. Select the `Workspace` the key belongs to.
5. Set an `Expiration` date. If an [API key expiration policy](https://docs.mistral.ai/admin/identity-access/api-key-policy) applies to the selected Workspace, the date picker only offers dates within the allowed range and the non-expiring option is unavailable. If no policy applies, choose any future date or leave the key non-expiring.
6. Choose the `Connector access scope`.
7. Select `Create new key`.
8. Copy the key immediately.

After you create a key, you cannot change its Workspace, Connector access scope, or expiration date. To change those settings, create a new key and delete the old one.

> **Warning**
>
> API keys are confidential and are not shared within your Organization. The full key is shown only once. After you close the dialog, you cannot retrieve it. Store it in a password manager or secrets vault. Do not share it or commit it to version control.

## Manage API keys {#manage-keys}

Open [Admin Panel > API > API Keys](https://admin.mistral.ai/plateforme/api-keys) to review API keys across the Organization.

The key list shows:

- active and expired keys;
- key type;
- Workspace;
- last used date;
- expiration date.

From the key list, admins can:

- rotate a key by creating a new key and deleting the old one;
- delete a key;
- identify unused or expired keys.

## API key expiration policy {#expiration-policy}

An API key expiration policy sets the maximum validity period for newly created API keys. Policies are off by default. Existing keys, including non-expiring keys, keep working until they are revoked or reach their original expiry.

Organization Admins can set an Organization-wide maximum. Workspace Admins can set a stricter Workspace maximum, but they cannot exceed the Organization maximum. Server-side checks enforce active policies for API and UI creation paths.

For policy behavior and hierarchy, see [API key expiration policy](https://docs.mistral.ai/admin/identity-access/api-key-policy).

## Manage your own API keys {#user-profile-keys}

Admins and developers can manage their own API keys from the User Profile modal:

- In Studio, open [Studio > API keys](https://console.mistral.ai/home?profile_dialog=api-keys).
- Or open your user profile menu and select `API Keys`.

Use this flow for keys you own. Use the Admin Panel flow when you need to manage keys across the Organization.

> **Tip**
>
> Admins can also review API keys from a member's `User Details` panel. The `API Keys` tab shows the member's keys, their type, the Workspace each key belongs to, when each key was last used, and when each key expires. See [User management](https://docs.mistral.ai/admin/identity-access/user-management#api-keys).

## API key scope {#api-key-scope}

API keys are scoped to the Workspace where they were created. Requests made with a key use that Workspace's quota, rate limits, and resources.

To use different keys for different environments, such as development, staging, and production, create separate [Workspaces](https://docs.mistral.ai/admin/workspaces/your-first-workspace) and create a dedicated API key in each Workspace.

Connector access scope controls which Workspace Connectors the key can use.

| Scope | Access |
| --- | --- |
| **Shared connectors only** | Access only Connectors shared with the Workspace, not private Connectors. |
| **Private and shared connectors** | Access both private Connectors owned by the key creator and Connectors shared with the Workspace. |

The default scope is `Shared connectors only`. Use it for automation. Choose `Private and shared connectors` only when the application needs private Connectors owned by the key creator.

For Connector administration, see [Connectors](https://docs.mistral.ai/admin/identity-access/connectors).

> **Note**
>
> API keys are not scoped to plans. You cannot create a Free mode API key or a pay-as-you-go API key. Each key automatically uses your Organization's Mistral plan and pay-as-you-go settings. See [Subscriptions](https://docs.mistral.ai/admin/billing-usage/subscriptions).
