---
url: https://docs.mistral.ai/admin/monitor-comply/zero-data-retention
title: Zero data retention
breadcrumbs: [Admin, Monitor and comply]
kind: doc
locale: en
source_path: src/content/en/docs/admin/monitor-comply/zero-data-retention/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# Zero data retention

Zero data retention (ZDR) controls whether supported API inputs and outputs are retained after Mistral returns a response. Use this guide to understand what ZDR covers, what it excludes, and how to request it for your Organization.

> **Info**
>
> **ZDR is available on paid plans for supported stateless API calls.** It gives eligible Organizations stricter control over whether API inputs and outputs are retained after processing.

## What zero data retention covers {#what-zdr-covers}

When ZDR is enabled, Mistral **does not store or log inputs and outputs for supported API requests** longer than required to generate the output.

ZDR applies to **stateless API calls**. A stateless API call does not need to store your input or output after the request completes for the endpoint to work.

## Supported API endpoints {#supported-endpoints}

ZDR applies to the following stateless API endpoints:

| Endpoint | Coverage |
|----------|----------|
| `/v1/chat/completions` | Chat completions |
| `/v1/fim/completions` | Fill-in-the-middle completions |
| `/v1/embeddings` | Embeddings |
| `/v1/moderations` | Text moderation |
| `/v1/chat/moderations` | Chat moderation |
| `/v1/classifications` | Text classification |
| `/v1/chat/classifications` | Chat classification |
| `/v1/ocr` | OCR |
| `/v1/audio/speech` | Speech generation |
| `/v1/audio/transcriptions` | Speech transcription |

ZDR applies to supported endpoints across models, **except Labs models**.

## What zero data retention does not cover {#what-zdr-does-not-cover}

ZDR **does not apply to stateful APIs or products**. These services must store data to work, for example to show history, maintain application state, process files, or retrieve documents later.

ZDR does not apply to:

- Agents
- Batch processing files
- Conversations
- Libraries
- `/v1/files`
- Vibe Work
- Chat

For example, the Files API stores uploaded files and is **outside the scope of ZDR**. Vibe Work and Chat store conversation data so you can access previous work and conversation history.

## How ZDR applies to Vibe CLI {#vibe-cli}

Vibe CLI runs on your machine and calls stateless APIs. If ZDR is enabled for your Organization on a paid plan, Vibe CLI API calls follow the ZDR rules of the **underlying API endpoint**.

## How ZDR differs from training opt-out {#training-opt-out}

ZDR and training opt-out are **separate controls**.

| Control | What it controls |
|---------|------------------|
| ZDR | Whether supported API inputs and outputs are retained after processing. |
| Training opt-out | Whether eligible data can be used to improve Mistral models. |

**You do not need ZDR to opt out of model training.** To manage training preferences, see [Privacy and data controls](https://docs.mistral.ai/admin/monitor-comply/privacy-data-controls).

## Request zero data retention {#request-zdr}

To request ZDR, contact support through the [ZDR Help Center article](https://help.mistral.ai/en/articles/347612-can-i-activate-zero-data-retention-zdr) or [contact Mistral support](https://help.mistral.ai/en/articles/347458-how-do-i-contact-support).

Include enough detail about your legitimate reason for requesting ZDR. **We review each request and may approve or deny it.**

## Check whether ZDR is active {#check-zdr-status}

After your request is approved, **ZDR appears in your Admin privacy settings**.

Open [Admin Panel > API > Privacy](https://admin.mistral.ai/plateforme/privacy).

If ZDR does not appear in your privacy settings, your request has not been processed yet. If your request is rejected, you receive an email.

## Related resources {#related-resources}

- [Privacy and data controls](https://docs.mistral.ai/admin/monitor-comply/privacy-data-controls)
- [ZDR Help Center article](https://help.mistral.ai/en/articles/347612-can-i-activate-zero-data-retention-zdr)
- [Trust Center](https://trust.mistral.ai/)
- [Legal Center](https://legal.mistral.ai/)
