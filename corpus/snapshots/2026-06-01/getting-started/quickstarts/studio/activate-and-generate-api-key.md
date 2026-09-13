---
url: https://docs.mistral.ai/getting-started/quickstarts/studio/activate-and-generate-api-key
title: Activate Studio and generate an API key
breadcrumbs: [Getting started, Quickstarts, Studio]
kind: doc
locale: en
source_path: src/content/en/docs/getting-started/quickstarts/studio/activate-and-generate-api-key/page.mdx
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
---

# Activate Studio and generate an API key

Set up your [Studio](https://console.mistral.ai) account and create an API key you can use to call Mistral models.

- **Free mode**: API access is enabled by default with no credit card required. Usage and rate limits apply.
- **Secure key management**: set expiration dates and rotate keys regularly

By the end you will have a working API key ready to use in your first request.

**Time to complete:** ~5 minutes

## Prerequisites {#prerequisites}

- A [Mistral account](https://console.mistral.ai).

## Step 1: Generate an API key {#step-1}

1. Open the [Studio console](https://console.mistral.ai).
2. Navigate to **API Keys** in the left sidebar.
3. Click **Create new key**.

![Click Create new key](https://docs.mistral.ai/assets/quickstarts/studio/new-key-button.png)

4. Add a **Name** to identify the key (for example, "First test key").
5. Set an **Expiration** date. Regular rotation improves security.

![Configure the API key with optional name and expiration date](https://docs.mistral.ai/assets/quickstarts/studio/new-key-modal.png)

6. Click **Create new key**.
7. Copy the key immediately and store it in a secure location (password manager or secrets vault).

> **Warning**
>
> The full key appears only once. You cannot retrieve it after closing the confirmation dialog.

## Verify {#verify}

You have completed the setup:

1. You are in Free mode with limited usage and rate limits.
2. You have an API key stored securely.

Test the key with a quick `curl` request:

```bash
curl https://api.mistral.ai/v1/chat/completions \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-small-latest",
    "messages": [{"role": "user", "content": "Hello, Mistral!"}]
  }'
```

A successful response confirms your key is working.

## What's next {#whats-next}

- [Test a model in the API playground](https://docs.mistral.ai/getting-started/quickstarts/studio/test-model-playground)

- [Studio overview](https://docs.mistral.ai/studio-api/overview)
