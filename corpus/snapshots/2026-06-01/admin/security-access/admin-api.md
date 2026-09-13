---
url: https://docs.mistral.ai/admin/security-access/admin-api
title: Admin API
breadcrumbs: [Admin, Security & Access]
kind: doc
locale: en
source_path: src/content/en/docs/admin/security-access/admin-api/page.mdx
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
---

# Admin API

The Admin API provides programmatic access to organization management tasks that are otherwise available through the [Admin Panel](https://admin.mistral.ai).

## Capabilities {#capabilities}

Use the Admin API to automate:

- Organization and Workspace management
- User invitations and role assignments
- Seat provisioning and access control
- Billing and usage queries

## Authentication {#authentication}

Admin API requests require an API key that belongs to a user with the **Admin** role in the Organization. Standard API keys with Member or Billing roles don't have access to administrative endpoints.

## API reference {#reference}

See the [API reference](https://docs.mistral.ai/api) for endpoint documentation.
