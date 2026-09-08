---
url: https://docs.mistral.ai/admin/set-up-organization/verify-domain
title: Verify your domain
breadcrumbs: [Admin, Set up your Organization]
kind: doc
locale: en
source_path: src/content/en/docs/admin/set-up-organization/verify-domain/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# Verify your domain

Domain verification proves that you control one or more email domains. It is required before enabling [Email domain authentication](https://docs.mistral.ai/admin/set-up-organization/sign-in-method/email-domain-authentication), [SAML SSO](https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso), and other enterprise access features.

## Verify a domain {#verify}

1. Open [Admin Panel > Administration > Access](https://admin.mistral.ai/organization/access).
2. Click **Add Domain** in the **Domain Ownership** section.
3. Enter your domain (for example, `yourcompany.com`) and click **Add domain**.
4. Click **Verify domain** and copy the DNS TXT record provided.
5. In your DNS provider or domain registrar, add a new TXT record:
   - **Type**: `TXT`
   - **Host/Name**: `@` or your domain (exact format depends on your provider)
   - **Value**: paste the verification code (e.g., `mistral-domain-verification=xxxxxx`)
6. Save the record and wait for DNS propagation. This usually takes 10 minutes to 24 hours.

The Admin Panel updates the domain status to `Verified` once propagation completes. You can add and verify more domains from the same **Domain Ownership** section. To check propagation manually:

```bash
nslookup -type=TXT yourcompany.com
```

> **Caution**
>
> Keep every verified domain's DNS TXT record active. Removing a record can break Email Domain Authentication, SSO, or other enterprise access features for that domain.

## Next steps {#next-steps}

Once your domain is verified:

- Enable [Email domain authentication](https://docs.mistral.ai/admin/set-up-organization/sign-in-method/email-domain-authentication) to automatically add users with matching email addresses.
- Set up [SAML SSO](https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso) to authenticate through your identity provider (Enterprise plans).
