---
url: https://docs.mistral.ai/admin/set-up-organization/enterprise-accounts
title: Enterprise Accounts and Backoffice
breadcrumbs: [Admin, Set up your Organization]
kind: doc
locale: en
source_path: src/content/en/docs/admin/set-up-organization/enterprise-accounts/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
---

# Enterprise Accounts and Backoffice

Enterprise Accounts sit above Organizations. They let existing Organization admins create and manage linked Organizations from Backoffice.

[Backoffice](https://backoffice.mistral.ai/) is where Enterprise Account admins manage the Enterprise Account layer. [Admin Panel](https://admin.mistral.ai/) remains the place to administer one Organization.

## How Enterprise Accounts fit into Admin {#admin-hierarchy}

The Admin hierarchy has three layers:

1. **Enterprise Account**: the top-level account that links one or more Organizations.
2. **Organization**: the account that contains members, Workspaces, billing, access settings, and policies.
3. **Workspace**: a shared environment inside an Organization for product usage, resources, access, and limits.

![Admin hierarchy: Enterprise Account links one or more Organizations, and each Organization contains one or more Workspaces.](https://docs.mistral.ai/img/admin_enterprise_hierarchy.svg)

Backoffice manages the Enterprise Account and the Organizations under it. The Admin Panel manages one Organization at a time. Workspaces still organize teams, environments, products, and budgets inside one Organization.

## When you need an Enterprise Account {#when-you-need-an-enterprise-account}

Enterprise Accounts are available to admins of an existing linked Organization. Use them to generate Admin API keys, or when your company needs more than one Organization.

> **Note**
>
> To get initial Backoffice access, contact your Mistral account team. A Mistral team member needs to create the first Enterprise Account for your company.

Create separate Organizations when different groups need their own:

- Organization settings;
- members and access model;
- Workspaces;
- Admin API keys;
- usage, billing, or operational boundaries.

> **Note**
>
> You don't need multiple Organizations to access Backoffice. Enterprise Account access also doesn't replace Organization roles.

## Manage an Enterprise Account {#manage-enterprise-account}

Use Backoffice to manage Enterprise Account members, linked Organizations, and Admin API keys from one place.

### Open Backoffice {#open-backoffice}

Open [backoffice.mistral.ai](https://backoffice.mistral.ai/).

You need Enterprise Account admin access to use Backoffice. Existing Enterprise Account admins can add other existing Organization admins to the Enterprise Account.

> **Warning**
>
> If you try to add a user who is not an Organization admin in a linked Organization, the invitation fails.

The left navigation includes:

- **Enterprise Account Members**;
- **Organizations**;
- **API Keys**.

### Manage members {#enterprise-account-members}

Use **Enterprise Account Members** to review and manage people who can access the Enterprise Account in Backoffice. Enterprise Account members must already be admins of a linked Organization.

The member list shows:

- name and email;
- account ID;
- Organizations associated with the member;
- last login;
- available actions.

You can add a new member from this page. Pending invitations appear in the list with an **Invite pending** status.

### Manage Organizations {#organizations}

Use **Organizations** to review the Organizations linked to the Enterprise Account. The list shows each Organization name, Organization ID, member count, and available actions.

You can create an Organization from this page.

> **Note**
>
> Enterprise Account admins can see linked Organizations, but they cannot administer every linked Organization by default. Use **Promote to admin** to promote the current Enterprise Account admin to Organization admin on the selected Organization.

### Manage Admin API keys {#admin-api-keys}

Use **API Keys** to create and review Admin API keys for the Organizations under the Enterprise Account.

Admin API keys are scoped to one Organization. A key can administer only the Organization selected when you create it. Admin API keys can have an expiration date or no expiration date.

The key list shows:

- key name;
- Organization;
- masked key value;
- creation date;
- last used date;
- expiration date;
- available actions.

To create an Admin API key:

1. Open **API Keys** in Backoffice.
2. Click **Create Key**.
3. Enter a **Name**.
4. Select the **Organization** the key belongs to.
5. Optionally set an **Expiration** date.
6. Create the key and copy it immediately.

> **Warning**
>
> The full Admin API key is only shown at creation. If you lose it, you'll need to create a new one.

## Next steps {#next-steps}

- [Authentication and Admin API keys](https://docs.mistral.ai/admin/admin-api/authentication)

- [Create your Organization](https://docs.mistral.ai/admin/set-up-organization/create-organization)

- [Create your first Workspace](https://docs.mistral.ai/admin/workspaces/your-first-workspace)
