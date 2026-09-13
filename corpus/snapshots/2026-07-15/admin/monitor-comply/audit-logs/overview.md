---
url: https://docs.mistral.ai/admin/monitor-comply/audit-logs/overview
title: Overview
breadcrumbs: [Admin, Monitor and comply, Audit logs]
kind: doc
locale: en
source_path: src/content/en/docs/admin/monitor-comply/audit-logs/overview/page.mdx
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
---

# Audit logs

Audit logs provide a **chronological record of actions** performed within your Organization across Studio and Vibe. They let administrators track user activity, API key usage, and security events.

Available on **Enterprise** plans. Enabled by default for all Workspaces.

## Access audit logs {#accessing}

Open [Admin Panel > Administration > Audit Logs](https://admin.mistral.ai/audit-logs).

> **Info**
>
> No setup is needed. Audit logs are enabled automatically on Enterprise plans.

## What gets logged {#what-is-logged}

Audit logs capture actions performed by both users and API keys. Each log entry includes:

- **Timestamp** (`CreatedAt`): when the event occurred.
- **Actor**: who performed the action (human user, API key, or system).
- **Event**: the specific action (e.g., `batch_job.create`, `le_chat.conversation.deleted`).
- **Target**: the resource affected (e.g., batch job, conversation, API key).
- **Metadata**: additional context about the actor, event, and target.

**Logged activities** include:

- Authentication events (sign-ins, SSO flows)
- API usage and key management (creation, deletion)
- Organization and Workspace changes
- User management actions (invitations, role changes, removals)
- Settings modifications
- Vibe interactions (conversation creation, deletion)

## Search and filter {#search-and-filter}

Use the filter controls above the log table to narrow results:

1. Filter by **Actor** (human, API key), **Event** type, or **Target** resource.
2. Combine multiple filters to find specific activities (e.g., all conversation deletions by a specific user).
3. Customize visible columns by clicking **Columns** and toggling fields on or off.

The table updates automatically as you apply filters.

## Use cases {#use-cases}

- **Security monitoring**: detect unauthorized access or unusual activity patterns.
- **Incident investigation**: trace the sequence of actions leading to an issue.
- **Compliance**: maintain records for regulatory requirements.

## Limitations {#limitations}

- Log export is not supported.
- Audit logs are only available on Enterprise plans.
