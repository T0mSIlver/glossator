---
url: https://docs.mistral.ai/admin/user-management-finops/user-management
title: User management
breadcrumbs: [Admin, User Management & Fin Ops]
kind: doc
locale: en
source_path: src/content/en/docs/admin/user-management-finops/user-management/page.mdx
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
---

# User management

Add, manage, and remove users within your Organization. Assign roles to control access
to products and administrative functions, and manage seats to grant access to paid features.

Available on **Team** and **Enterprise** plans. Requires the **Admin** role.

## Invite members {#inviting-members}

1. Open [Members](https://admin.mistral.ai).
2. Click **Invite members**.
3. Enter one or more email addresses (comma-separated).
4. Choose a role (**Admin**, **Billing**, or **Member**) for all invitees.
5. Assign product seats based on your subscription.
6. Send the invitations.

Invitees receive an email with instructions to join. You can resend or revoke
an invitation before it is accepted.

With [email domain authentication](https://docs.mistral.ai/admin/security-access/email-domain-auth) enabled,
users with matching domain emails join automatically on sign-up.

### What invitees experience {#invitation-flow}

When you send an invitation:

1. The invitee receives an email from Mistral with a **Join Organization** link.
2. Clicking the link opens a sign-up or sign-in page. Existing Mistral account holders sign in; new users create an account.
3. After authenticating, the invitee joins the Organization with the role you assigned.
4. Assigned product seats activate immediately -- the invitee can start using Vibe, Mistral Code, or other products.

> **Note**
>
> Invitations expire after **7 days**. If the invitee does not accept in time, resend the invitation from the **Members** panel.

### Re-invite and revoke {#re-inviting}

- **Resend:** Click the resend icon next to a pending invitation. The invitee receives a new email with a fresh link, and the original link is invalidated.
- **Revoke:** Click the revoke icon to cancel a pending invitation. The original link stops working.
- **Re-invite a removed user:** A previously removed user can be re-invited. They rejoin with a fresh role and seat assignment -- no prior permissions carry over.

### Troubleshoot invitations {#troubleshooting-invitations}

| Issue | Cause | Resolution |
|-------|-------|------------|
| Invitee did not receive the email | Incorrect address or spam filter | Verify the email address. Check spam/junk folders. Resend the invitation. |
| Invitation link expired | More than 7 days elapsed | Resend the invitation from the **Members** panel. |
| Invitee gets an error on sign-up | SSO or domain restriction blocking the email domain | Check [SSO](https://docs.mistral.ai/admin/security-access/sso) and domain settings. Contact [support](https://help.mistral.ai) if the issue persists. |
| Removed user still has access | Session not yet invalidated | Access revocation applies on the next authentication. Check [audit logs](https://docs.mistral.ai/admin/security-access/audit-logs) and contact support if the issue persists. |

## Assign seats {#assigning-seats}

Seats control access to paid products (Vibe Team/Enterprise, Mistral Code).

1. Find the user in [Members](https://admin.mistral.ai) (search by name or email).
2. In the product column, set the dropdown to **Active** to grant access, or **Inactive** to revoke it.
3. Changes apply immediately.

The number of available seats appears at the top of each product column. If you need more seats, contact [support](https://help.mistral.ai).

- **Reassignment:** Set a user's seat to **Inactive** to free it, then assign it to another user. Freed seats are available immediately.
- **Role independence:** Product seats are separate from Organization roles. A user with the **Member** role can hold an active Vibe seat, and an **Admin** can have no product seats.
- **Deactivation:** If you deactivate a user's seat, they lose access to that product but keep their Organization membership and role.

## Organization roles {#roles}

| Role | Permissions |
|------|-------------|
| **Admin** | Full control: organization settings, user invitations, security configuration, billing, audit logs |
| **Billing** | Subscriptions, invoices, and payment methods only. Cannot invite users or change organization settings |
| **Member** | Product usage only. Can manage their own profile and preferences |

The system assigns the **Member** role to new users by default. Change roles from the **Members** panel in the Admin Panel. Role changes take effect immediately -- if you demote an **Admin** to **Member**, they lose administrative access on their next page load.

## Workspace roles {#workspace-roles}

Workspace roles are independent from Organization roles. A user with the **Billing** role at the Organization level can be an **Admin** within a specific workspace. See [Organizations and workspaces](https://docs.mistral.ai/admin/security-access/organization) for details.

## Remove members {#removing-members}

To remove a member, click the **Remove** icon next to their name in the **Members** panel and confirm.

- Removal is immediate. The user loses access to the Organization and all its resources.
- Resources they created (agents, libraries, etc.) remain available to other Organization members.
- You cannot remove the last **Admin**. At least one **Admin** must remain in the Organization.
- Removed members can rejoin if re-invited.

## Leave an Organization {#leaving}

Any user can leave an Organization (unless they are the last **Admin**):

1. Go to [Members](https://admin.mistral.ai).
2. Find your own entry.
3. Click the **Remove** icon next to your name and confirm.

Leaving is permanent. You must be re-invited to rejoin.
