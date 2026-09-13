---
url: https://docs.mistral.ai/admin/identity-access/api-keys
title: API keys
breadcrumbs: [Admin, Access and permissions]
kind: doc
locale: en
source_path: src/content/en/docs/admin/identity-access/api-keys/page.mdx
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
---

# API keys

API keys authenticate requests to the Mistral API and other Mistral tools. In Admin, Organization admins can create, review, rotate, and delete API keys across Workspaces.

Developers can create and manage their own API keys from their User Profile modal in Studio. Vibe-only users usually do not need API keys unless they also use Studio, the API, Vibe Code, or another developer tool.

## API key types {#key-types}

API keys can be associated with different product surfaces:

| Type | Use |
| --- | --- |
| **Studio** | Standard API keys for Mistral API usage. |
| **Vibe** | Keys used by Vibe Code. |
| **Mistral Code** | Legacy keys for earlier Mistral Code usage. |

## Create an API key as an admin {#create-key-admin}

1. Open [Admin Panel > API > API Keys](https://admin.mistral.ai/plateforme/api-keys).
2. Click **Create new key**.
3. Optionally enter a **Key name**.
4. Select the **Workspace** the key belongs to.
5. Optionally set an **Expiration** date. Use **No expiration date** for a key that does not expire automatically.
6. Choose the **Connector access scope**.
7. Click **Create new key**.
8. Copy the key immediately.

After you create a key, you **cannot change** its Workspace, Connector access scope, or expiration date. To change those settings, create a new key and delete the old one.

> **Warning**
>
> API keys are confidential and are **not shared** within your Organization. The full key is **shown only once**. After you close the dialog, you cannot retrieve it. Store it in a password manager or secrets vault. Do not share it or commit it to version control.

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

## Manage your own API keys {#user-profile-keys}

Admins and developers can manage their own API keys from the User Profile modal:

- In Studio, open [Studio > API keys](https://console.mistral.ai/home?profile_dialog=api-keys).
- Or open your user profile menu and select **API Keys**.

Use this flow for keys you own. Use the Admin Panel flow when you need to manage keys across the Organization.

> **Tip**
>
> Admins can also review API keys from a member's **User Details** panel. The **API Keys** tab shows the member's keys, their type, the Workspace each key belongs to, when each key was last used, and when each key expires. See [User management](https://docs.mistral.ai/admin/identity-access/user-management#api-keys).

## API key scope {#api-key-scope}

API keys are scoped to the Workspace where they were created. Requests made with a key use that Workspace's quota, rate limits, and resources.

To use different keys for different environments, such as development, staging, and production, create separate [Workspaces](https://docs.mistral.ai/admin/workspaces/your-first-workspace) and create a dedicated API key in each Workspace.

Connector access scope controls which Workspace Connectors the key can use.

| Scope | Access |
| --- | --- |
| **Shared connectors only** | Access only Connectors shared with the Workspace, not private Connectors. |
| **Private and shared connectors** | Access both private Connectors owned by the key creator and Connectors shared with the Workspace. |

The default scope is **Shared connectors only**. Use it for automation. Choose **Private and shared connectors** only when the application needs private Connectors owned by the key creator.

For Connector administration, see [Connectors](https://docs.mistral.ai/admin/identity-access/connectors).

> **Note**
>
> API keys are not scoped to plans. You **cannot** create a free API key or a Scale API key. Each key automatically uses the plan your Organization subscribes to. See [Subscriptions](https://docs.mistral.ai/admin/billing-usage/subscriptions).
