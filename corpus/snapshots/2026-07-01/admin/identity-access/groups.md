---
url: https://docs.mistral.ai/admin/identity-access/groups
title: Groups
breadcrumbs: [Admin, Access and permissions]
kind: doc
locale: en
source_path: src/content/en/docs/admin/identity-access/groups/page.mdx
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
---

# User groups

A user group is a named collection of users that you manage and assign together. Instead of granting Workspace access one user at a time, you assign a group to a Workspace once, and every member gains access with the role you choose.

You can create and manage groups from [Admin Panel > Administration > Groups](https://admin.mistral.ai/organization/groups) or with the [Admin API](https://docs.mistral.ai/admin/admin-api/manage-groups-roles).

## How user groups work {#how-it-works}

- A group bundles users under a single name and description.
- You add or remove members by their user ID.
- You assign a group to a Workspace with a role. Every current member of the group is provisioned into that Workspace with that role.
- A group can be assigned to more than one Workspace, and a user can belong to more than one group.

## Groups, Workspaces, and roles {#groups-Workspaces-roles}

User groups sit alongside the existing access model:

- **Organization**: the top-level account that users belong to.
- **Workspace**: an isolated environment with its own members, API keys, and usage. Each member has a Workspace role.
- **User group**: a convenience layer for assigning many users to a Workspace at once, with a chosen role.

When you provision a group to a Workspace, you set the Workspace role applied to its members. See [Your first Workspace](https://docs.mistral.ai/admin/workspaces/your-first-workspace) for how Workspace roles work, and [Roles and permissions](https://docs.mistral.ai/admin/identity-access/roles-permissions) for role names and API fields.

## Externally managed groups {#externally-managed-groups}

If your Organization uses an identity provider with SSO or SCIM provisioning, some groups and members can be externally managed. Your identity provider is the source of truth for their identity, membership, or lifecycle.

Externally managed users and groups cannot be edited directly in Mistral for fields owned by the identity provider. Manage those fields in your identity provider, then let the next sync update Mistral.

## Typical workflow {#typical-workflow}

1. Create a group.
2. Add members to the group.
3. Assign the group to a Workspace with a role.

For the corresponding API calls, see [Manage groups and roles](https://docs.mistral.ai/admin/admin-api/manage-groups-roles) and [User provisioning](https://docs.mistral.ai/admin/admin-api/user-provisioning).

## Next steps {#next-steps}

- [User provisioning](https://docs.mistral.ai/admin/admin-api/user-provisioning)

- [Admin API](https://docs.mistral.ai/admin/admin-api/overview)
