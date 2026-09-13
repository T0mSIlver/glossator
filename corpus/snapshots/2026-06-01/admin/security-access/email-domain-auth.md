---
url: https://docs.mistral.ai/admin/security-access/email-domain-auth
title: Email domain authentication
breadcrumbs: [Admin, Security & Access]
kind: doc
locale: en
source_path: src/content/en/docs/admin/security-access/email-domain-auth/page.mdx
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
---

# Email domain authentication

*Available on **Team** plans and above*

Email domain authentication controls how new users join your Organization. When enabled, anyone who signs up or logs in with an **email address matching your verified domain** is automatically added to your Organization.

## How it works {#how-it-works}

- Users signing up or logging in with an email matching your verified domain are **automatically added** to your Organization.
- Users still **create and manage their own credentials** (email and password). This feature controls Organization membership, not authentication.
- For single sign-on authentication **without separate credentials**, use [SSO](https://docs.mistral.ai/admin/security-access/sso) instead (Enterprise plans).

## Prerequisites {#prerequisites}

You need to **verify ownership of your domain** before enabling this feature. Domain verification uses a DNS TXT record. See [domain verification](https://docs.mistral.ai/admin/security-access/sso#domain-verification) for the full setup steps.

## Enable email domain authentication {#enabling}

1. Open [Access](https://admin.mistral.ai) settings.
2. In the **Authentication** section, click **Activate email domain authentication**.
3. Confirm by clicking **Enable email domain authentication** in the dialog.

The Access page updates to show the feature is active.

## Disable email domain authentication {#disabling}

You can disable email domain authentication at any time from the **Access** settings page.

- New users with matching domain emails won't be auto-added anymore.
- Existing members aren't affected.
- You'll need to manually invite new users unless [SSO](https://docs.mistral.ai/admin/security-access/sso) is configured.

> **Caution**
>
> If you re-enable the feature later, you'll need to go through the setup process again.
