---
url: https://docs.mistral.ai/admin/identity-access/connectors
title: Connectors
breadcrumbs: [Admin, Access and permissions]
kind: doc
locale: en
source_path: src/content/en/docs/admin/identity-access/connectors/page.mdx
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
---

# Connectors

Organization admins use Connectors in Admin to connect shared apps, review Connector details, and control which Connector tools are available to users in Vibe and Studio.

Connector administration applies at the Organization and Workspace levels. Use Admin to govern access. Use [Studio Connectors](https://docs.mistral.ai/studio-api/connectors) when you need developer-facing Connector docs, API examples, or the Connector Debugger.

## Open Connectors in Admin {#open-connectors}

1. Open [Admin Panel > Administration > Connectors](https://admin.mistral.ai/organization/connectors).
2. Review the **App Connections** and **All Connectors** sections.

## Connect organization-level apps {#app-connections}

Use **App Connections** to connect services once at the Organization level. Once connected, members can use the app through Mistral without signing in individually.

| App | What it does |
| --- | --- |
| **GitHub** | Search repositories, review issues, and manage pull requests in GitHub. |
| **Slack** | Search messages, read channels, send messages, and manage canvases in Slack. |

To connect an app, click **Connect to GitHub** or **Connect to Slack**, then complete the authorization flow.

## Manage all Connectors {#all-connectors}

**All Connectors** lists the Connectors and tools that can be used in Vibe and Studio. Open a Connector to review its setup and control tool access.

Each Connector page includes three tabs:

- **Overview**: review metadata, visibility, authentication, and available content.
- **Credentials**: review or add credentials for the Connector.
- **Permissions**: choose which tools can be used by the model.

### Review Connector details {#overview-tab}

The **Overview** tab shows basic information about the Connector, including:

| Field | Example |
| --- | --- |
| **Visibility** | Organization |
| **Authentication** | OAuth2 |
| **Origin** | Featured |
| **Capabilities** | Read-only |
| **Connector name** | atlassian |
| **Connector ID** | 0198e70f-57b0-77f6-a752-0a7f5ea2da35 |

If you are not connected, the **Includes** section shows **You're not connected**. Click **Connect** to authenticate and see the tools.

### Manage credentials {#credentials-tab}

The **Credentials** tab lists the credentials available for the Connector. If there are no credentials yet, click **Connect** to start using the Connector.

> **Tip**
>
> Use organization-level app connections for shared bot access. Use Connector credentials when users or Workspaces need a specific account connection.

### Set Connector permissions {#permissions-tab}

The **Permissions** tab controls which tools can be used by the model.

| Permission | Effect |
| --- | --- |
| **Allowed** | All tools are available for users in this Workspace. |
| **Restricted** | Only selected tools are available for users in this Workspace. |
| **Blocked** | The Connector is turned off for users in this Workspace. |

Use **Restricted** when a Connector includes tools that must not be available to every workflow or chat. Use **Blocked** when a Connector must not be used in a Workspace.

## Next steps {#next-steps}

- For API key Connector scopes, see [API keys](https://docs.mistral.ai/admin/identity-access/api-keys#connector-access-scope).
- For developer-facing Connector docs, see [Studio Connectors](https://docs.mistral.ai/studio-api/connectors).
- For Workspace impact, see [Workspaces in Studio](https://docs.mistral.ai/admin/workspaces/workspaces-in-studio) and [Workspaces in Vibe](https://docs.mistral.ai/admin/workspaces/workspaces-in-vibe).
