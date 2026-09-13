---
url: https://docs.mistral.ai/admin/set-up-organization/create-organization
title: Create your Organization
breadcrumbs: [Admin, Set up your Organization]
kind: doc
locale: en
source_path: src/content/en/docs/admin/set-up-organization/create-organization/page.mdx
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
---

# Create your Organization

When you sign up for Mistral, an Organization is created automatically. To create another Organization, for example to separate a personal account from a company account, follow these steps.

## Create an Organization {#create}

1. Click your Organization name in the top-left corner of Studio.
2. Click **Add** in the Organizations section.
3. Enter a name for the Organization.
4. Accept the terms of service.
5. Click **Create Organization**.

The new Organization starts with you as the sole Admin and a default Workspace.

## View Organization details {#view-Organization-details}

After your Organization exists, use the **Your Organization** page to check the Organization name, Organization ID, and number of active members.

1. Open [Admin Panel > Administration > Organization](https://admin.mistral.ai/Organization).
2. Review **Active members** to see how many active members belong to the Organization.
3. Check your **Organization ID**.
4. Review or update the **Organization name**.

> **Tip**
>
> Keep your Organization ID handy. You need it to automate administration with the [Admin API](https://docs.mistral.ai/admin/admin-api/overview) or to help [support](https://help.mistral.ai/en/articles/347458-how-do-i-contact-support) identify your Organization.

## Delete an Organization {#delete-organization}

The **Danger zone** in the Organization settings lets you permanently delete an Organization.

> **Danger**
>
> Deleting an Organization is permanent. It deletes the Organization and its resources, data, Workspaces, API keys, settings, usage history, and other Organization-scoped content. It **does not delete the user accounts** that were members of the Organization.

1. Open [Admin Panel > Administration > Organization](https://admin.mistral.ai/organization).
2. Go to the **Danger zone** section.
3. Click **Delete Organization**.
4. Confirm the deletion.

## Next steps {#next-steps}

After creating your Organization, you can:

- [Set up billing](https://docs.mistral.ai/admin/billing-usage/billing): add a payment method to activate API access beyond the free tier.
- [Verify your domain](https://docs.mistral.ai/admin/set-up-Organization/verify-domain): required to enable email domain authentication or SSO.
- [Invite members](https://docs.mistral.ai/admin/identity-access/user-management): add users and assign roles.
