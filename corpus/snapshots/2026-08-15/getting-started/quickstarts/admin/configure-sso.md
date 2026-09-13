---
url: https://docs.mistral.ai/getting-started/quickstarts/admin/configure-sso
title: Configure SSO and domain verification
breadcrumbs: [Getting started, Quickstarts, Admin]
kind: doc
locale: en
source_path: src/content/en/docs/getting-started/quickstarts/admin/configure-sso/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
---

# Configure SSO and domain verification

Verify your company domain and connect your corporate identity provider to your Mistral organization.

- Add a DNS record to prove domain ownership
- Enable email-domain authentication for automatic team onboarding
- Configure SAML SSO with your IdP (Okta, Azure AD, or similar)

Once complete, team members sign in with their corporate credentials instead of separate passwords.

**Time to complete:** ~20 minutes

## Prerequisites {#prerequisites}

- An **Enterprise plan** (SAML SSO requires Enterprise; domain verification works on Team+)
- Admin role in your Mistral organization
- Access to your company's DNS records (for domain verification)
- Access to your identity provider admin console (Okta, Azure AD, Ping Identity, or similar)

## Step 1: Verify your domain {#step-1}

Domain verification proves you own your company's email domain. This enables email-domain authentication and SSO.

1. Navigate to **Administration › Settings** in the [Admin panel](https://admin.mistral.ai).
2. Under **Domain verification**, click **Add domain**.
3. Enter your domain: for example, `acme.com`.
4. We generate a DNS TXT record. Copy the record value.
5. Add the TXT record to your domain's DNS configuration:

```
Type:  TXT
Name:  _mistral-verification
Value: mistral-verify=abc123xyz...
```

6. Click **Verify**. DNS propagation can take up to 48 hours but typically finishes within 15 minutes.

You can confirm the TXT record is live before clicking Verify by running: `dig TXT _mistral-verification.acme.com`

## Step 2: Enable email-domain authentication (optional) {#step-2}

Once your domain is verified, you can allow anyone with a matching email address to automatically join your organization: no individual invitations needed.

1. Navigate to **Administration › Settings** in the [Admin panel](https://admin.mistral.ai).
2. Under **Email domain authentication**, toggle it **on**.
3. Select the default role for auto-joined users: **Member** (recommended).

When enabled, any user who signs up with an `@acme.com` email is automatically added to your organization as a Member.

Only enable this if you want all employees with your domain email to have automatic access. If you prefer manual control, skip this step and invite users individually.

## Step 3: Configure SAML SSO {#step-3}

SAML SSO lets team members sign in through your corporate identity provider instead of a separate password.

1. Navigate to **Administration › Settings** in the [Admin panel](https://admin.mistral.ai).
2. Under **SAML SSO**, click **Configure**.
3. We provide two values to enter in your IdP:

| Field | Value |
| --- | --- |
| **ACS URL** (Assertion Consumer Service) | Provided by Mistral: copy from the settings page |
| **Entity ID** (Audience URI) | Provided by Mistral: copy from the settings page |

4. In your IdP (Okta, Azure AD, etc.), create a new SAML application and paste the ACS URL and Entity ID.
5. Configure attribute mapping in your IdP:

| IdP attribute | Mistral attribute |
| --- | --- |
| Email | Name ID (email format) |
| First name | `firstName` |
| Last name | `lastName` |

6. Copy the **IdP metadata URL** (or download the metadata XML) from your IdP.
7. Back in the settings page, paste the metadata URL and click **Save**.

## Step 4: Test SSO login {#step-4}

1. Open a private/incognito browser window.
2. Open [Vibe](https://chat.mistral.ai) or [Studio](https://console.mistral.ai).
3. Click **Sign in with SSO** and enter your company email.
4. Your IdP login page opens.
5. After authenticating, you land in your Mistral dashboard with your organization selected.

If the login fails, verify the ACS URL and Entity ID match exactly between Mistral and your IdP. Check that the Name ID format is set to **email**.

## Verify {#verify}

Your SSO is configured correctly if:

- The domain shows **Verified** in Organization Settings
- Team members can sign in via your IdP without a separate Mistral password
- New users who sign in via SSO are automatically added to your organization
- User names (first and last) appear correctly from the IdP attribute mapping

## What's next {#whats-next}

- [Manage workspaces and API keys](https://docs.mistral.ai/getting-started/quickstarts/admin/manage-workspaces)

- [All admin quickstarts](https://docs.mistral.ai/#quickstarts)
