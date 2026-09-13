---
url: https://docs.mistral.ai/getting-started/quickstarts/studio/test-model-playground
title: Test a model in the API playground
breadcrumbs: [Getting started, Quickstarts, Studio]
kind: doc
locale: en
source_path: src/content/en/docs/getting-started/quickstarts/studio/test-model-playground/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
---

# Test a model in the API playground

Use the [Studio](https://console.mistral.ai) playground to send prompts to Mistral models, adjust generation parameters, and compare outputs, all without writing code.

- **Interactive testing**: type a prompt and get a response in seconds
- **Model comparison**: switch between models to see how outputs differ
- **Parameter tuning**: adjust temperature, max tokens, and other settings in real time

By the end you will know how to evaluate models and parameters before integrating them into your application.

**Time to complete:** ~5 minutes

## Prerequisites {#prerequisites}

- An active Studio account. Free mode is enabled by default with usage and rate limits.

## Step 1: Open the playground {#step-1}

1. Go to [Studio](https://console.mistral.ai).
2. Click **Playground** in the left sidebar.

The playground opens with a chat interface where you can interact with any available model.

## Step 2: Select a model and send a prompt {#step-2}

1. Open the **Model** dropdown at the top of the playground.
2. Select a model (for example, `mistral-small-latest` for fast responses or `mistral-large-latest` for higher quality).
3. Type a prompt in the input field:

> Explain the difference between supervised and unsupervised learning in three sentences.

4. Click **Send** (or press Enter).

The response appears in the chat panel. Review the output for quality, accuracy, and style.

## Step 3: Adjust parameters and compare outputs {#step-3}

The right sidebar exposes generation parameters. Change them to see how they affect the output.

1. **Temperature**: controls randomness. Lower values (0.1) produce more deterministic outputs. Higher values (0.9) increase creativity.
2. **Max tokens**: limits response length. Set this to control cost and verbosity.
3. **Top P**: an alternative to temperature for controlling diversity.

Try this experiment:

1. Set **Temperature** to `0.1` and send the same prompt.
2. Set **Temperature** to `0.9` and send it again.
3. Compare the two responses. The low-temperature response is more focused and consistent. The high-temperature response shows more variation.

Switch to a different model from the dropdown and send the same prompt to compare how models handle the same task.

## Verify {#verify}

You have used the playground to:

1. Send a prompt to a Mistral model.
2. Adjust temperature and observe the effect on output.
3. Compare responses across different models.

You now understand how model selection and parameters affect generation quality, which helps you make informed choices when building your application.

## What's next {#whats-next}

- [Create a reusable Prompt](https://docs.mistral.ai/getting-started/quickstarts/studio/create-reusable-prompt)

- [Create a Skill in Studio](https://docs.mistral.ai/getting-started/quickstarts/studio/create-skill)

- [Send your first API request](https://docs.mistral.ai/getting-started/quickstarts/developer/first-api-request)

- [Studio overview](https://docs.mistral.ai/studio)
