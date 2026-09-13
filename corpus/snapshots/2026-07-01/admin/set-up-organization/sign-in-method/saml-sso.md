---
url: https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso
title: SAML SSO
breadcrumbs: [Admin, Set up your Organization, Choose a sign-in method]
kind: doc
locale: en
source_path: src/content/en/docs/admin/set-up-organization/sign-in-method/saml-sso/page.mdx
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
---

# Single sign-on (SSO)

SAML single sign-on (SSO) lets members of your Organization **sign in with your corporate identity provider** (IdP). Any user with an email address that matches your verified domain is redirected to your configured IdP to authenticate.

> **Info**
>
> You need an Enterprise plan to configure SAML SSO.

## How SAML SSO works {#how-it-works}

1. A user enters an email address that matches a **verified domain**.
2. Mistral redirects the user to your configured IdP.
3. The IdP authenticates the user with your **corporate credentials and policies**.
4. The user returns to Mistral signed in.
5. On **first sign-in**, Mistral provisions the user account in your Organization.

> **Info**
>
> Organization SSO uses SAML 2.0. OpenID Connect (OIDC) is not supported for Organization SSO.

## Prerequisites {#prerequisites}

Before you configure SSO, make sure you have:

- an Enterprise plan;
- at least one [verified domain](https://docs.mistral.ai/admin/set-up-organization/verify-domain);
- permission to create a SAML 2.0 application in your IdP;
- SAML metadata XML from your IdP.

You also need these attribute mappings:

| Attribute | Value |
| --- | --- |
| User's first name | `firstName` |
| User's last name | `lastName` |
| Name ID format | `EmailAddress` |

## Configure SSO {#configure-sso}

### Start SSO setup in Admin {#start-in-admin}

1. Open [Admin Panel > Administration > Access](https://admin.mistral.ai/organization/access) in the Admin Panel.
2. In **Organization Access**, find **Single Sign-On (SAML SSO)**.
3. Click **Activate SSO**.
4. Keep the SSO configuration modal open while you configure your IdP.

### Create the SAML app in your IdP {#create-saml-app}

1. In your IdP admin console, create a **SAML 2.0 application** for Mistral.
2. Copy the **ACS URL** and **Entity ID** from the Mistral modal into your IdP configuration.
3. Map the user attributes from the [prerequisites](https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso#prerequisites) section.
4. Export or copy the **SAML metadata XML** from your IdP.

### Enable SSO in Admin {#enable-sso}

1. Paste the complete metadata XML into the text box in the Mistral SSO configuration modal.
2. Click **Enable SSO**.

Users with email addresses matching your verified domain are redirected to your IdP for authentication.

## What users experience {#signing-in}

1. The user goes to the Mistral login page.
2. The user enters their work email address.
3. The password field disappears, and the user sees **Continue with [Organization name]**.
4. The user authenticates with their corporate credentials on the IdP login page.
5. The user returns to Mistral signed in.

## Supported identity providers {#supported-idps}

Any compliant SAML IdP can work. The most commonly used providers are:

- **Microsoft Entra ID** (formerly Azure Active Directory)
- **Google Workspace** / Google Identity Platform
- **Okta**

Refer to your IdP's documentation for specific SAML application setup instructions.

## Automatic seat assignment {#automatic-seat-assignment}

You can automatically assign seats to users when they first sign in through SSO, if they have access to your Organization and seats are available.

Automatic seat assignment can apply to:

- Team seats;
- Mistral Code Enterprise seats.

Configure automatic seat assignment from [Admin Panel > Administration > Access](https://admin.mistral.ai/organization/access).

## Disable SSO {#disable-sso}

You can disable SSO at any time from [Admin Panel > Administration > Access](https://admin.mistral.ai/organization/access) in the Admin Panel.

> **Warning**
>
> Disabling SSO means users can no longer sign in through your IdP. They need to set a password through the reset flow or be re-invited. Automatic user provisioning also stops. Consider enabling [Email domain authentication](https://docs.mistral.ai/admin/set-up-organization/sign-in-method/email-domain-authentication) before disabling SSO.

## Troubleshooting {#troubleshooting}

If SSO fails after configuration:

- Verify that the **ACS URL** and **Entity ID** match exactly between Mistral and your IdP.
- Confirm that attribute mappings are case-sensitive (`firstName`, `lastName`).
- Check that **Name ID Format** is set to `EmailAddress`.
- Make sure the metadata XML is complete and correctly pasted.
- Contact [support](https://help.mistral.ai) if issues persist.
