---
url: https://docs.mistral.ai/admin/workspaces/your-first-workspace
title: Your first Workspace
breadcrumbs: [Admin, Configure Workspaces]
kind: doc
locale: en
source_path: src/content/en/docs/admin/workspaces/your-first-workspace/page.mdx
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
---

# Create your first Workspace

A Workspace is a **shared environment** for a team or use case inside your Organization. It scopes the resources, access, usage, and limits that apply to the work done there.

Each Workspace can have its own:

- **Members and roles**: decide who can access the Workspace and what they can do.
- **API keys**: scope API usage to one Workspace.
- **Resources**: keep Vibe and Studio resources, such as prompts, Libraries, and skills, separate by Workspace. You can also configure Connector connections and permissions for each Workspace.

- **Usage and limits**: track consumption and set spending limits per Workspace.
- **Product settings**: enable or disable Vibe capabilities for a specific Workspace.

From a user's perspective, switching Workspace changes the product context they work in. See [Workspaces in Studio](https://docs.mistral.ai/admin/workspaces/workspaces-in-studio) and [Workspaces in Vibe](https://docs.mistral.ai/admin/workspaces/workspaces-in-vibe) for how the selected Workspace affects resources inside each product.

> **Note**
>
> An Organization can have up to **500 active Workspaces**. Workspace names must be unique within an Organization.

## Create a Workspace {#create-workspace}

Every Organization **starts with a default Workspace**. Organization admins can create additional Workspaces when they need more separation.

1. Open [Admin Panel > Administration > Workspaces](https://admin.mistral.ai/organization/workspaces).
2. Click **New Workspace**.
3. Choose an **icon** to represent the Workspace.
4. Enter a **name**. This is the human-friendly label shown in user interfaces and exports.
5. Optionally, enter a **description**.
6. Optionally, add **members** and assign Workspace **roles** to those members. See [Workspace access](https://docs.mistral.ai/admin/workspaces/your-first-workspace#workspace-access) for how roles apply.
7. Click **Create**.

> **Tip**
>
> The creator is automatically assigned the **Workspace Admin** role.

## Workspace access {#workspace-access}

Members belong to the Organization first, then get access to one or more Workspaces. You can add members directly to a Workspace or manage access through [Groups](https://docs.mistral.ai/admin/identity-access/groups).

A member's Workspace role controls what they can do inside one Workspace. Their Organization role controls what they can do across the Organization. The two are independent: for example, an Organization Member can be a Workspace Admin in a specific Workspace.

> **Info**
>
> Organization admins always have full access to every Workspace in the Organization, even when not explicitly added as Workspace members.

For the full list of Workspace roles and their permissions, see [Roles and permissions](https://docs.mistral.ai/admin/identity-access/roles-permissions).

## Archive a Workspace {#archive-workspace}

Archive a Workspace when members no longer need access to it, but you want to keep it in the Organization history.

1. Open [Admin Panel > Administration > Workspaces](https://admin.mistral.ai/organization/workspaces).
2. Find the Workspace in the list.
3. Click the **Archive** icon.
4. Confirm the archive action.

> **Warning**
>
> Archiving a Workspace makes it unavailable to all members. This action cannot be undone. The default Workspace cannot be archived.

## Next steps {#next-steps}

After you create a Workspace, configure it for Studio and Vibe, then set limits and review usage:

- [Workspaces in Studio](https://docs.mistral.ai/admin/workspaces/workspaces-in-studio): understand how Workspace selection affects API keys, developer resources, usage, limits, and Connectors in Studio.
- [Workspaces in Vibe](https://docs.mistral.ai/admin/workspaces/workspaces-in-vibe): understand how Workspace selection affects chats, projects, tools, feature toggles, retention, tracing, and Connectors in Vibe.
- [Usage and limits by Workspace](https://docs.mistral.ai/admin/workspaces/usage-limits): set spending caps and review Workspace usage.
