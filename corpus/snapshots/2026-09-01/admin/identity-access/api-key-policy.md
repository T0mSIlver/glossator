---
url: https://docs.mistral.ai/admin/identity-access/api-key-policy
title: API key expiration policy
breadcrumbs: [Admin, Access and permissions]
kind: doc
locale: en
source_path: src/content/en/docs/admin/identity-access/api-key-policy/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
hidden: true
---

# API key expiration policy

This page is for Organization Admins and Workspace Admins who need to understand API key expiration policies. Use it to confirm what the policy controls, how Organization and Workspace limits interact, and what happens to existing API keys.

> **Info**
>
> API key expiration policies are **off by default**. An Organization Admin must enable a policy before key creation is restricted.

## What the policy controls {#policy-scope}

An API key expiration policy sets a maximum validity period, in days, for newly created API keys. When a policy is active, new API keys cannot be created beyond the configured limit.

> **Note**
>
> The policy applies only when a key is created. Existing keys, including keys without an expiration date, are not modified, shortened, revoked, or expired by a policy change.

Policy checks run on the server side for every creation path, including the `Admin Panel`, Studio, and the API. Client-side controls, such as the date picker, guide users, but server-side validation is the source of enforcement.

## Set or change a policy {#configure-policy}

Organization Admins can set the Organization policy from [Admin Panel > API > API Keys](https://admin.mistral.ai/organization/api-keys). Select `Edit` next to `API key expiration policy`, choose the maximum validity period, then select `Save`.

Workspace Admins can set a Workspace policy from [Admin Panel > Administration > Workspaces](https://admin.mistral.ai/organization/workspaces). Open the Workspace, go to the `API keys` tab, then set a Workspace maximum.

Managing a policy requires the `Manage API key policy` permission at the corresponding Organization or Workspace level.

## How Organization and Workspace limits interact {#policy-hierarchy}

The Organization policy sets the ceiling. Workspace Admins can set a stricter, shorter maximum for their Workspace, but they cannot set a maximum that exceeds the Organization limit.

For example, if the Organization maximum is 90 days, a Workspace Admin can set a Workspace maximum of 30 or 60 days, but not 120 days. If only the Organization policy is set, Workspaces inherit that maximum.

> **Tip**
>
> When both levels have a policy, the **shorter maximum** applies to newly created API keys.

## What happens to existing keys {#existing-keys}

Existing keys are not affected. A policy applies only to newly created keys, so current integrations keep working unless you revoke a key or the key reaches its original expiration date.

There is no remediation deadline for existing keys that do not match a new policy. To bring an existing key under the policy, create a replacement key with a compliant expiration date, migrate your integration, then revoke the old key.

## How policy changes are logged {#audit-logs}

Policy creations, updates, and removals are recorded in the Enterprise Audit Log with before and after values and the admin who made the change. See [Audit logs](https://docs.mistral.ai/admin/monitor-comply/audit-logs/overview).

## Common questions {#faq}

### Is the policy enabled by default? {#default-state}

No. The policy is off by default. An Organization Admin must enable it before new API keys need to follow a maximum validity period.

### Who can configure the policy? {#policy-owners}

Organization Admins can set or change the Organization policy. Workspace Admins can set a Workspace policy that is equal to or stricter than the Organization maximum.

### What happens if I create a key without an expiration date? {#missing-expiration}

If a policy is active, the key is created with the latest expiration date allowed by the policy. For example, if the maximum is 90 days, a key created without an expiration date expires in 90 days.

If no policy applies, you can create a key without an expiration date.

### What happens if I set an expiration date beyond the maximum? {#expiration-too-late}

The key is created with the latest expiration date allowed by the policy. Choose a date within the configured maximum validity period if you need the key to expire sooner.

### Does the policy apply to API-created keys and UI-created keys? {#creation-paths}

Yes. Policy checks run on the server side for every creation path, including the `Admin Panel`, Studio, and the API.

### What changes in the date picker? {#date-picker}

When a policy is active, the date picker only allows dates within the allowed range. Dates beyond the maximum are disabled, and the non-expiring option is unavailable.

### What happens if the Organization limit is lower than a Workspace limit? {#workspace-limit-above-org-limit}

The Organization maximum becomes the effective ceiling for newly created API keys. Workspace Admins can still set stricter limits, but they cannot exceed the Organization maximum.

### Can I set different limits for different products? {#product-specific-limits}

No. The policy applies uniformly across products within the Organization or Workspace, including Studio and Vibe Code keys.

### Why is the expiration date different from what I requested? {#expiration-clamped}

Check whether an Organization Admin has set an Organization policy. If the requested expiration is missing or beyond the maximum, we set the key to the latest allowed expiration date. Workspace Admins may not have visibility into Organization-level settings.

### Why can't I set a Workspace limit higher than the Organization limit? {#workspace-limit-blocked}

The Organization policy is the ceiling. Workspace limits can be stricter, but they cannot exceed the Organization maximum. Contact your Organization Admin if you need a higher limit.
