---
url: https://docs.mistral.ai/vibe/work/connectors
title: Connect tools with Connectors
breadcrumbs: [Vibe, Work]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/work/connectors/page.mdx
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
---

# Connect tools with Connectors

Connectors are **secure bridges** between Work and your external tools and data sources. They let Work retrieve, analyze, and act on data from services like Gmail, Google Drive, GitHub, or Notion as part of a task.

Instead of switching between apps, you ask Work: *"Check my Gmail for unread messages about the quarterly report and summarize them"* or *"Find the latest design document in Google Drive and create a brief I can share with my team."* Work decides which Connector to call, asks for authentication if missing, and requests approval before sensitive actions.

## Available Connectors {#available-connectors}

**Featured**

Featured Connectors use a direct OAuth flow. Click `Connect` on the card and authenticate. Administrators can disable specific Connectors for the whole organization on a case-by-case basis.

| Connector | What it does |
|-----------|-------------|
| Atlassian | Connect to Confluence and Jira to search, summarize, and perform project actions. |
| Box | Search, analyze, and get insights from your Box files. |
| GitHub App | Search repositories, review issues, and manage pull requests in GitHub. |
| Gmail | Include your email in your chats. |
| Google Calendar | Include your calendar in your chats. |
| Linear | Search, summarize, and manage your issues and projects in Linear. |
| Notion | Search, summarize, and author content in Notion. |
| Outlook | Read and send emails with Outlook. |
| Outlook Calendar | Manage your Outlook Calendar — search events, schedule and delete meetings, and accept or decline invitations. |
| SharePoint Search API | Search and open SharePoint content via Microsoft Graph API. |
| Slack | Search messages, read channels, send messages, and manage canvases in Slack. |
| Stripe | Access and manage payments, customers, and transactions in Stripe. |

**Knowledge**

Knowledge Connectors **index your team's files** so Work can search them instantly, with your existing permissions replicated. An administrator must configure indexing before users can connect.

| Connector | What it does |
|-----------|-------------|
| Google Drive | Include your team's Google Drive files in your chats. |
| SharePoint Online | Include your team's SharePoint Online files in your chats. |
| SharePoint | Include your team's SharePoint files in your chats. |

For setup instructions (admin indexing, selective sync, ACLs), see our [Knowledge Connectors guide](https://docs.mistral.ai/vibe/work/connectors/knowledge-connectors).

**MCP**

Connect Work to **any service** built on the [Model Context Protocol](https://modelcontextprotocol.io) (MCP). Pick a pre-configured Connector from our directory, or point Work at your own MCP-compatible server. Requires an administrator.

For directory browsing, custom configuration, and security best practices, see our [MCP Connectors guide](https://docs.mistral.ai/vibe/work/connectors/mcp-connectors).

## Connecting a service {#connecting}

To connect a featured Connector:

1. Open the `Connectors` page from the sidebar.
2. Find the Connector card and click `Connect`.
3. Complete the authentication flow (typically OAuth 2.0). Your password is never shared with us.

A green `Connected` indicator confirms the connection. You can disconnect at any time from the same page.

> **Note**
>
> Google Drive and SharePoint (Online) require administrator setup before users can connect, because we index your team's files. See our [Knowledge Connectors](https://docs.mistral.ai/vibe/work/connectors/knowledge-connectors) guide.

## Using Connectors in tasks {#using-connectors}

Once connected, Work can use the Connector automatically when relevant. You can also enable a specific Connector for a task:

1. Click the `+` icon or type `/` in the chat window.
2. Select `Tools` then enable the Connector you want to use.

Then describe the task naturally. Work figures out which Connector to call based on your request.

Typical prompts:

- *"What meetings do I have tomorrow?"*
- *"Find the latest Q3 revenue deck in Google Drive and prepare a one-page summary."*
- *"Create a calendar event for Friday at 2pm with the product team."*
- *"Check my unread emails from the legal team and draft replies for me to review."*

### Approving actions {#approving-actions}

When a Connector performs an action on your behalf (sending an email, creating an event, modifying a file), Work asks for your **approval before executing** it. See [Safety and approvals](https://docs.mistral.ai/vibe/work/safety-and-approvals#approvals) for the full approval flow and the three options (`Continue`, `Always allow`, `Decline`).

You can also pre-authorize specific functions per Connector — see [Per-function Connector permissions](https://docs.mistral.ai/vibe/work/safety-and-approvals#connector-functions).

## Data and privacy {#data-privacy}

How we handle Connector data depends on the type:

- **Featured Connectors** (Gmail, Google Calendar, etc.): data is fetched in real time for your current request. We don't store it on our servers. Disconnecting revokes access immediately.
- **Knowledge Connectors** (Google Drive, SharePoint): files are indexed and stored in our European data centers. See [Knowledge Connectors](https://docs.mistral.ai/vibe/work/connectors/knowledge-connectors#data-privacy) for details.

**Training**: data accessed through Connectors is **never used to train or fine-tune our models**, regardless of your plan. Conversations that reference Connector data are treated as regular user-provided content and follow your plan's [data policies](https://mistral.ai/terms#privacy-policy).

For more details, see our [trust center](https://trust.mistral.ai/).
