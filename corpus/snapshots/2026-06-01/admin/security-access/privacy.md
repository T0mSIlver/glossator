---
url: https://docs.mistral.ai/admin/security-access/privacy
title: Privacy
breadcrumbs: [Admin, Security & Access]
kind: doc
locale: en
source_path: src/content/en/docs/admin/security-access/privacy/page.mdx
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
---

# Privacy

We provide controls for managing how your data is handled across Vibe and the API. This page covers data usage policies, training opt-out, and GDPR rights.

## Data usage {#data-usage}

- **Vibe (Free plan)**: conversations may be used to improve our models. You can opt out at any time from the Admin Panel.
- **Vibe (Pro, Team, Enterprise)**: conversations aren't used for model training by default.
- **API**: data sent through the API isn't used for model training.
- **Connectors**: data accessed through Connectors is fetched on-demand and not stored permanently. Connector data isn't used for training.
- **Libraries**: uploaded documents are stored securely and not used for training.

## Training opt-out {#opt-out}

To opt out of data usage for model improvement:

1. Open [Privacy](https://admin.mistral.ai).
2. Disable data sharing for model training.

The change applies immediately to your Organization.

## GDPR rights {#gdpr}

Under GDPR, you have the following rights:

| Right | Description |
|-------|-------------|
| **Access** | Obtain copies of your personal data |
| **Rectification** | Correct inaccurate personal information |
| **Erasure** | Delete your account and associated data |
| **Data portability** | Request your data in a transferable format |
| **Object** | Opt out of certain processing activities |
| **Restriction** | Request limitations on data processing |

To exercise these rights, use our [dedicated contact form](https://help.mistral.ai). Use the email address associated with your account and specify which data or activities concern you.

For account data changes, use the Admin Panel directly. For data export, download from Vibe or Studio.

> **Warning**
>
> Account deletion is permanent and irreversible. All prompts, outputs, and personal data are removed and can't be recovered.

## Legal resources {#legal}

For terms of service, privacy policies, and data processing agreements, see the Legal and Trust Center on [mistral.ai](https://mistral.ai).
