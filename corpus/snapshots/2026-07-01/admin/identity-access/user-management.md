---
url: https://docs.mistral.ai/admin/identity-access/user-management
title: User management
breadcrumbs: [Admin, Access and permissions]
kind: doc
locale: en
source_path: src/content/en/docs/admin/identity-access/user-management/page.mdx
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
---

# User management

Use the Members page to manage who belongs to your Organization, which Organization role they have, which product seats they use, and which Workspaces and groups they belong to.

> **Info**
>
> To invite members to Vibe, your Organization needs a Team or Enterprise plan. To invite members for Studio and API access, your Organization needs a Scale plan. You need an Organization admin role to manage members.

## Open the Members page {#open-members}

Open [Admin Panel > Administration > Members](https://admin.mistral.ai/organization/members).

The Members page has two lists:

- **Active Users**: members who already belong to the Organization.
- **Invited Users**: pending invitations, including expired invitations.

Use search to find members by last name or email. In **Active Users**, filter by Organization role: **Admin**, **Member**, or **Billing**.

## Invite members {#invite-members}

Invite members manually when your Organization **does not use SSO**.

> **Info**
>
> If [SAML SSO](https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso) is enabled, users join through your configured identity provider instead.

To invite members:

1. Open [Admin Panel > Administration > Members](https://admin.mistral.ai/organization/members).
2. Click **Invite members**.
3. Enter one or more email addresses.
4. Choose the Organization role for the invitees.
5. Assign product seats if needed.
6. Send the invitations.

Invitees receive an email with instructions to join. Use **Invited Users** to track pending and expired invitations.

For each invitation, you can:

- resend the invitation if it expired;
- revoke the invitation to prevent the invitee from joining.

## Manage members {#manage-members}

Use **Active Users** for quick member changes. From the member list, you can:

- change the member's Organization role;
- turn Vibe seats on or off;
- turn Mistral Code seats on or off.

For more settings, click a member in **Active Users** to open **User Details**. The details panel lets you review the member profile, subscriptions, Workspaces, groups, and API keys.

### Review the profile {#user-profile}

The **Profile** tab shows:

- email address;
- first name and last name;
- user ID;
- whether the profile is externally managed by SSO or SCIM.

> **Note**
>
> If a profile is externally managed, name and email are synced from your identity provider and cannot be edited in the Admin Panel.

### Manage Organization roles {#organization-roles}

Organization roles control what a member can do at the Organization level.

| Role | Access |
| --- | --- |
| **Admin** | Full Organization administration. |
| **Billing** | Billing, subscriptions, invoices, payment methods, and usage information. |
| **Member** | Product access and personal profile settings. |

For the complete role model, see [Roles and permissions](https://docs.mistral.ai/admin/identity-access/roles-permissions).

### Manage seats and subscriptions {#seats-and-subscriptions}

Use **Subscriptions** in **User Details** to review and manage the member's product seats.

Seats can include:

- API Plan;
- Vibe;
- Mistral Code.

When SAML SSO is enabled, Organization admins can turn on **automatic seat assignment** from [Admin Panel > Administration > Access](https://admin.mistral.ai/organization/access).

> **Info**
>
> With automatic seat assignment, users who first sign in through SSO receive a seat when they have access to the Organization and seats are available.

### Manage Workspace access {#workspace-access}

The **Workspaces** tab in **User Details** lists the Workspaces the member belongs to and their Workspace role in each one.

From this tab, you can:

- add the member to an existing Workspace;
- change the member's Workspace role;
- remove the member from a Workspace;
- review Workspace membership.

> **Note**
>
> You can add a member only to a Workspace that already exists. You cannot remove a member from the default Workspace.

Workspace roles are separate from Organization roles. For example, an Organization **Billing** member can still be a **Workspace Contributor** in a Workspace. See [Roles and permissions](https://docs.mistral.ai/admin/identity-access/roles-permissions) for Workspace role details.

### Manage groups {#groups}

The **Groups** tab in **User Details** shows the groups the member belongs to.

Use it to add the member to groups or review group membership. Groups help you assign Workspace access and roles to multiple users at once. See [Groups](https://docs.mistral.ai/admin/identity-access/groups).

### Review member API keys {#api-keys}

The **API Keys** tab in **User Details** shows the member's API keys and the Workspace each key belongs to.

API keys are Workspace-scoped. See [API keys](https://docs.mistral.ai/admin/identity-access/api-keys) for key management details.

## Remove a member {#remove-members}

Remove a member when they no longer need access to the Organization.

1. Open [Admin Panel > Administration > Members](https://admin.mistral.ai/organization/members).
2. Find the member in **Active Users**.
3. Open the member row or user details.
4. Click **Remove user** and confirm.

Removing a member removes their Organization access and Workspace memberships. Resources they created can remain available to other Organization members.

> **Warning**
>
> You cannot remove the last Organization admin. At least one Organization admin must remain.
