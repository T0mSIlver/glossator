---
url: https://docs.mistral.ai/admin/workspaces/workspaces-in-studio
title: Workspaces in Studio
breadcrumbs: [Admin, Configure Workspaces]
kind: doc
locale: en
source_path: src/content/en/docs/admin/workspaces/workspaces-in-studio/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Workspaces in Studio

Studio uses the active Workspace as the context for what a developer can see, create, and monitor. Switching Workspace changes the API keys, playground state, resources, usage, limits, and observability data available to that user.

This guide explains how Workspace selection affects Studio users and what admins can configure from the Admin Panel.

## What changes for Studio users {#user-impact}

Everything in Studio is Workspace-scoped.

Workspace scope affects:

- **API keys**: users see and create keys for the active Workspace only.
- **Playground**: test requests run in the active Workspace context.
- **Agents**: agent definitions belong to the Workspace where they were created.
- **Batches**: batch jobs and their results are scoped to the Workspace.
- **Document AI**: document processing resources are scoped to the Workspace.
- **Workflows**: workflow resources belong to the active Workspace.
- **Audio**: transcription and speech resources are scoped to the Workspace.
- **Observability**: Campaigns, Judges, datasets, traces, token usage, and error metrics are scoped to the Workspace.
- **Prompts and Skills**: saved prompts and skills belong to the Workspace where they were created.
- **Files and Libraries**: uploaded files and Libraries are scoped to the Workspace.
- **Connectors**: Connector access and tools can be managed per Workspace.
- **Vibe Code CLI settings and keys**: settings and keys are scoped to the Workspace.

## Switch Workspace in Studio {#switch-workspace}

Users switch Workspace from the Organization or Workspace selector in the Studio header. After they select another Workspace, Studio updates API keys, playground state, resources, usage, and observability views for that Workspace.

## Admin settings for Studio {#admin-settings}

Organization admins configure Studio-related Workspace settings from [Admin Panel > Administration > Workspaces](https://admin.mistral.ai/organization/workspaces). Open a Workspace to manage its members, usage, spending limit, API key creation setting, and Connector access.

### API key creation {#api-key-creation}

Use **API Key Creation** to allow or prevent users from creating API keys in a Workspace.

> **Info**
>
> Keys created in a Workspace use that Workspace's quota, limits, and resources.

### Usage and limits {#usage-and-limits}

Each Workspace has its own usage and limits. Admins can:

- view Workspace usage from the Workspace detail view;
- set a monthly spending limit for API and Vibe consumption;
- use a cap that is lower than or equal to the Organization spending limit.

> **Warning**
>
> If a Workspace reaches its monthly spending limit, API access for that Workspace is suspended until the next month begins or the limit is increased.

A Workspace spending limit cannot exceed the Organization spending limit. If a recent payment fails, access can be affected until the payment is processed again.

For setup details, see [Usage and limits by Workspace](https://docs.mistral.ai/admin/workspaces/usage-limits).

### Connectors {#connectors}

Admins can manage the Connectors and Connector tools available in Studio and Vibe for each Workspace. See [Connectors](https://docs.mistral.ai/admin/identity-access/connectors).

## Next steps {#next-steps}

- Learn how [Workspaces affect Vibe](https://docs.mistral.ai/admin/workspaces/workspaces-in-vibe).
- Review [Workspace roles and permissions](https://docs.mistral.ai/admin/identity-access/roles-permissions).
- Set [usage and limits by Workspace](https://docs.mistral.ai/admin/workspaces/usage-limits).
