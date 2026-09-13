---
url: https://docs.mistral.ai/admin/set-up-organization/sign-in-method/email-domain-authentication
title: Email domain authentication
breadcrumbs: [Admin, Set up your Organization, Choose a sign-in method]
kind: doc
locale: en
source_path: src/content/en/docs/admin/set-up-organization/sign-in-method/email-domain-authentication/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Email domain authentication

> **Info**
>
> Email domain authentication is available on Team plans and above.

Email domain authentication, also called discoverable domain authentication, controls how users join your Organization. When enabled, any user with an email address that matches a verified domain can join your Organization from [Join Organization](https://admin.mistral.ai/join).

## How it works {#how-it-works}

- Users with an email address matching a verified domain can join from [Join Organization](https://admin.mistral.ai/join).
- Users still **create and manage their own credentials** (email and password). This feature controls Organization membership, not authentication.
- For single sign-on authentication **without separate credentials**, use [SSO](https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso) instead (Enterprise plans).

## Prerequisites {#prerequisites}

You need to **verify ownership of your domain** before enabling this feature. Domain verification uses a DNS TXT record. See [domain verification](https://docs.mistral.ai/admin/set-up-organization/verify-domain) for the full setup steps.

## Enable email domain authentication {#enabling}

1. Open [Admin Panel > Administration > Access](https://admin.mistral.ai/organization/access) in the Admin Panel.
2. In the **Domain Ownership** section, find the verified domain you want to make discoverable.
3. Turn on **Discoverable** for that domain.

The Admin Panel shows a confirmation message: **Email domain authentication enabled for `domain.com`**.

## Disable email domain authentication {#disabling}

You can disable email domain authentication by turning off **Discoverable** for the domain in the **Domain Ownership** section.

- Users with matching domain emails can no longer join automatically from [Join Organization](https://admin.mistral.ai/join).
- Existing members aren't affected.
- You'll need to manually invite new users unless [SSO](https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso) is configured.

> **Caution**
>
> If you re-enable the feature later, you'll need to go through the setup process again.
