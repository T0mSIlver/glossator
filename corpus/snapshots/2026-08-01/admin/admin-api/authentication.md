---
url: https://docs.mistral.ai/admin/admin-api/authentication
title: Authentication
breadcrumbs: [Admin, Admin API]
kind: doc
locale: en
source_path: src/content/en/docs/admin/admin-api/authentication/page.mdx
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
---

# Authentication and Admin API keys

Admin API requests authenticate with a dedicated **Admin API key**. Learn how those keys work and how to call the API.

## Admin API keys {#admin-api-keys}

An Admin API key is created and managed in the **Backoffice** ([backoffice.mistral.ai](https://backoffice.mistral.ai)). Each key is tied to a **single Organization** and grants access to that Organization's admin endpoints. Keys are managed from the Enterprise Account Backoffice for convenience, but their scope is always one Organization. For the Backoffice model, see [Enterprise Accounts and Backoffice](https://docs.mistral.ai/admin/set-up-organization/enterprise-accounts).

> **Warning**
>
> A user's standard API key never grants admin access, regardless of the user's role. Admin endpoints require an Admin API key **created in the Backoffice**. This is different from the regular [API keys](https://docs.mistral.ai/admin/identity-access/api-keys) used for the inference API.

## Create an Admin API key {#create-key}

1. Open the [Backoffice](https://backoffice.mistral.ai) and go to **API keys**.
2. Click **Create key**.
3. Choose a name, select the Organization the key belongs to, and optionally set an expiration date.
4. Copy the key and store it securely.

> **Warning**
>
> The key is only shown at creation. If you lose it, you'll need to create a new one.

## Make a request {#make-a-request}

Send Admin API requests to the Admin API base URL and pass your Admin API key in the `x-api-key` header.

- **Base URL**: `https://api.mistral.ai/v1/admin`
- **Authentication header**: `x-api-key: <ADMIN_API_KEY>`

Set the key as an environment variable before you make requests:

```bash
export ADMIN_API_KEY="your-admin-api-key"
```

Then call an endpoint. For example, list users in the Organization tied to the key:

```bash
curl "https://api.mistral.ai/v1/admin/users?page=1&page_size=50" \
  -H "x-api-key: $ADMIN_API_KEY"
```

For requests with a JSON body, also include the `Content-Type` header:

```bash
curl -X POST https://api.mistral.ai/v1/admin/users-invite \
  -H "x-api-key: $ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email": "ada@example.com"}'
```

See the [Admin API reference](https://docs.mistral.ai/admin/admin-api/api-reference) for available endpoints, parameters, and response fields.

## Next steps {#next-steps}

- [User provisioning](https://docs.mistral.ai/admin/admin-api/user-provisioning)

- [Manage users](https://docs.mistral.ai/admin/admin-api/manage-users)

- [API reference](https://docs.mistral.ai/admin/admin-api/api-reference)
