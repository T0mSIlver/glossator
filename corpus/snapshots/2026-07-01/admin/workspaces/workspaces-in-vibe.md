---
url: https://docs.mistral.ai/admin/workspaces/workspaces-in-vibe
title: Workspaces in Vibe
breadcrumbs: [Admin, Configure Workspaces]
kind: doc
locale: en
source_path: src/content/en/docs/admin/workspaces/workspaces-in-vibe/page.mdx
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
---

# Workspaces in Vibe

Vibe uses the active Workspace as the context for what a user can see and do. Switching Workspace changes the conversations, projects, tools, Connectors, feature settings, and policies available to that user.

This guide explains how Workspace selection affects Vibe users and what admins can configure from the Admin Panel.

## What changes for Vibe users {#user-impact}

Everything in Vibe is Workspace-scoped.

Workspace scope affects:

- **Conversation history**: chats and artifacts belong to the Workspace where they were created.
- **Projects**: project definitions and their related conversations are scoped to the Workspace.
- **Skills and agents**: users see the skills and agents available in the active Workspace.
- **Scheduled tasks**: schedules run in the Workspace where they were created.
- **Connector authentications**: users connect third-party services in a Workspace context.
- **Custom instructions**: instructions can vary by Workspace.

## Switch Workspace in Vibe {#switch-workspace}

Users switch Workspace by selecting their Organization name in the bottom-left corner of Vibe. The switcher shows the current Workspace, other Workspaces in the same Organization, and other Organizations they belong to.

Switching Workspace resets the active context across open tabs. For the full user-facing guide, see [Switch Organization or Workspace](https://docs.mistral.ai/vibe/work/switch-organization-workspace).

## Admin settings for Vibe {#admin-settings}

Organization admins configure Vibe-related Workspace settings from [Admin Panel > Administration > Workspaces](https://admin.mistral.ai/organization/workspaces).

### Feature toggles {#feature-toggles}

In the Workspace settings, admins can enable or disable Vibe capabilities for a Workspace.

- Work mode
- Agents
- Canvas
- Code Interpreter
- Deep Research
- Image Generation
- Memories
- Thinking Mode
- Web Search

> **Warning**
>
> Disabling a feature removes it from Vibe for all members of that Workspace. Use this when a Workspace needs stricter controls, for example for sensitive internal work.

### Chat retention policy {#retention-policy}

Use **Chat Retention Policy** to automatically delete Workspace chats and their artifacts after 30, 90, 180, or 365 days, or never.

> **Info**
>
> You can select only values that are stricter than [Admin Panel > Vibe > Privacy](https://admin.mistral.ai/vibe/privacy).

### Conversation tracing {#conversation-tracing}

Use **Conversation tracing** to collect traces, token usage, and error metrics from conversations in a Workspace. Data is available in [Observability](https://docs.mistral.ai/studio-api/observability) within Studio.

### Connectors {#connectors}

Admins can manage the Connectors and Connector tools available in Vibe and Studio for each Workspace. See [Connectors](https://docs.mistral.ai/admin/identity-access/connectors).

### Member access {#member-access}

Admins control which members can access a Workspace and which Workspace roles they receive. See [Roles and permissions](https://docs.mistral.ai/admin/identity-access/roles-permissions) for role details.

## Next steps {#next-steps}

- Learn how [Workspaces affect Studio](https://docs.mistral.ai/admin/workspaces/workspaces-in-studio).
- Review [Workspace roles and permissions](https://docs.mistral.ai/admin/identity-access/roles-permissions).
- Set [usage and limits by Workspace](https://docs.mistral.ai/admin/workspaces/usage-limits).
