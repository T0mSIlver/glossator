---
url: https://docs.mistral.ai/admin/security-access/api-keys
title: API keys
breadcrumbs: [Admin, Security & Access]
kind: doc
locale: en
source_path: src/content/en/docs/admin/security-access/api-keys/page.mdx
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
---

# API keys

API keys authenticate your requests to the Mistral API. Each key is scoped to a specific Workspace and grants access to all API endpoints available on your plan.

## Create an API key {#creating-keys}

1. [API keys](https://console.mistral.ai/api-keys).
2. Click **Create new key**.
3. Optionally set a **name** (e.g., "Production pipeline") and an **expiration date**.
4. Click **Create new key**.
5. Copy the key immediately.

> **Warning**
>
> **The full key is shown only once**. After you close the dialog, you can't retrieve it. Store the key securely in a password manager or secrets vault. Don't share it or commit it to version control.

## Use API keys {#using-keys}

Pass the key in the `Authorization` header:

```bash
curl https://api.mistral.ai/v1/chat/completions \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "mistral-medium-latest", "messages": [{"role": "user", "content": "Hello"}]}'
```

Or set it as an environment variable for the SDKs:

```bash
export MISTRAL_API_KEY="your-api-key"
```

## Workspace scoping {#workspace-scoping}

API keys are **scoped to the Workspace** where they were created. Resources created with a key (like datasets, batch jobs, etc.) are visible to all members of that Workspace.

To use different keys for different environments (development, staging, production), create separate [Workspaces](https://docs.mistral.ai/admin/security-access/organization).

## Key management {#key-management}

- **Rotate keys** regularly. Create a new key, update your applications, then delete the old one.
- **Revoke compromised keys** immediately by deleting them from the API keys page.
- **Set expiration dates** so keys automatically stop working after a given date.
- **Usage tracking**: all usage from keys in a Workspace is tracked together and billed to the Organization.

## Plans {#plans}

API keys work in **Free mode** by default, with usage and rate limits suitable for evaluation and prototyping. To raise your limits with pay-as-you-go billing, upgrade to the **Scale plan** in [Subscriptions › Billing](https://admin.mistral.ai/organization/billing).
