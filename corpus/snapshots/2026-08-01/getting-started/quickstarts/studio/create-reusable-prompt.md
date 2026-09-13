---
url: https://docs.mistral.ai/getting-started/quickstarts/studio/create-reusable-prompt
title: Create a reusable Prompt
breadcrumbs: [Getting started, Quickstarts, Studio]
kind: doc
locale: en
source_path: src/content/en/docs/getting-started/quickstarts/studio/create-reusable-prompt/page.mdx
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
---

# Create a reusable Prompt

Use [Prompts](https://console.mistral.ai/build/prompts) to save prompt templates you can reuse privately or share with your workspace in Studio and in applications that reference shared prompt definitions.

- **Reusable instructions**: store system instructions, task templates, and output formats in one place.
- **Versioning**: update a Prompt without losing earlier versions.

By the end you will have a saved Prompt ready to test, reuse, and share when needed.

**Time to complete:** ~5 minutes

## Prerequisites {#prerequisites}

- An active Studio account.
- A prompt you want to reuse. Good first candidates are support tone guidelines, extraction instructions, or a structured summary format.

## Step 1: Open Prompts {#step-1}

1. Open [Studio](https://console.mistral.ai).
2. In the sidebar, open `Build` > `Prompts`.
3. Click `New prompt`.

## Step 2: Add the Prompt details {#step-2}

Give the Prompt a clear title and description so teammates know when to use it.

| Field | Example |
|---|---|
| `Title` | `Support tone` |
| `Description` | `Tone and response structure for customer support replies.` |

Keep the description task-oriented. Explain the use case instead of restating the title.

## Step 3: Write the template {#step-3}

Add the prompt text. Keep the instructions specific enough that another teammate can reuse the Prompt without extra context:

> You are a customer support assistant. Acknowledge the issue, answer clearly, and propose the next action. Use a calm, concise tone for enterprise administrators.

## Step 4: Save and test {#step-4}

1. Click `Save` or `Create prompt`.
2. Open the saved Prompt and review its first version.
3. Test it in a supported Studio surface, such as the `Playground`, before using it in an application.

## Step 5: Choose visibility {#step-5}

From the Prompt details page, click `Share` to choose who can use the Prompt:

- Keep it private if only you should access it.
- Share it with the entire workspace if teammates should be able to find and reuse it.

You can update this visibility later from the same `Share` button.

## Step 6: Create a new version {#step-6}

Create a new version when you want to change the Prompt without overwriting the version that teammates or applications already use. Studio creates the new version after you save changes.

1. Open the Prompt from the `Prompts` list.
2. Update the prompt text.
3. Add version notes that explain what changed, such as `Shorter support replies` or `Adds escalation guidance`.
4. Click `Save`.
5. Confirm the version history shows the new version.

Older versions stay available for review and rollback. Test the new version before promoting it for production use.

If your workspace uses aliases, promote the tested version to an alias such as `stable`.

## Verify {#verify}

Your Prompt is ready if:

- It appears in the Prompts list with the right title and description.
- A test run produces the expected tone, structure, and constraints.
- Its visibility is correct: private to you or shared with the workspace.
- The version history shows your original version and the updated version.

## What's next {#whats-next}

- [Create a Skill in Studio](https://docs.mistral.ai/getting-started/quickstarts/studio/create-skill)

- [Test a model in the API playground](https://docs.mistral.ai/getting-started/quickstarts/studio/test-model-playground)

- [Prompt engineering guide](https://docs.mistral.ai/models/best-practices/prompt-engineering)
