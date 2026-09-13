---
url: https://docs.mistral.ai/vibe/work/switch-organization-workspace
title: Switch Organization or Workspace
breadcrumbs: [Vibe, Work]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/work/switch-organization-workspace/page.mdx
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
---

# Switch Organization or Workspace

Your Mistral account belongs to one or more **Organizations**, and each Organization contains one or more **Workspaces**. A Workspace is an **isolation boundary**: use it to keep resources separate between departments, projects, or environments. It is not a team-management container.

> **Info**
>
> Workspaces are shared across Vibe, Studio, and the Admin Panel: the same Workspace entity is visible in all three. In Vibe Work, switching Workspace changes which scope you're working in. See [Organizations and Workspaces](https://docs.mistral.ai/admin/workspaces/organization-vs-workspaces) for the admin view.

## Switch from the sidebar {#switcher}

Click your **Organization name** in the bottom-left corner of the Vibe app, next to your initials. The popover shows:

- Your current **Workspace** (named **Default Workspace** if the Organization has only one).
- Other Workspaces in the same Organization.
- Other Organizations you belong to.

Pick a Workspace to switch directly. Pick an Organization to land on its default Workspace.

> **Note**
>
> If your account only has access to one Workspace, the switcher is hidden. Nothing to do.

> **Warning**
>
> Switching Workspace switches **all open tabs** (single session per user). Open separate browser profiles if you need to work in two Workspaces at once.

## Everything is scoped per Workspace {#scoped}

When you switch Workspace, your view in Vibe Work resets. The following resources stay where you created them and **are not shared across Workspaces**:

- Chat history
- [Projects](https://docs.mistral.ai/vibe/work/projects)
- [Skills](https://docs.mistral.ai/vibe/work/skills) (personal and Workspace-published)
- [Scheduled tasks](https://docs.mistral.ai/vibe/work/scheduled-tasks)
- [Custom instructions](https://docs.mistral.ai/vibe/work/custom-instructions)
- Connector authentications

If you need any other resource in another Workspace, you have to recreate it there.

> **Info**
>
> [Libraries](https://docs.mistral.ai/vibe/work/libraries) are also scoped per Workspace by default, but your Organization admin can allow Org-level sharing so a Library is visible across all Workspaces in the Organization.

## Workspace-level admin settings {#admin-config}

Some Vibe Work behavior is configured per Workspace by Organization Admins:

- **Available tools**: which Vibe Work tools and Connectors are enabled.
- **User access and roles**: who can join the Workspace and at what role.
- **Usage metrics**: per-Workspace usage tracking.

If a feature is missing or behaves differently between Workspaces, this is usually why. Reach out to your Organization admin to adjust settings, or see [Organizations and Workspaces](https://docs.mistral.ai/admin/workspaces/organization-vs-workspaces) for the configuration details.

> **Tip**
>
> More granular sharing of individual resources with specific users or groups, without requiring a Workspace switch, is on the roadmap.
