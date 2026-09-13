---
url: https://docs.mistral.ai/getting-started/quickstarts/studio/create-skill
title: Create a Skill in Studio
breadcrumbs: [Getting started, Quickstarts, Studio]
kind: doc
locale: en
source_path: src/content/en/docs/getting-started/quickstarts/studio/create-skill/page.mdx
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
---

# Create a Skill in Studio

Use [Skills](https://console.mistral.ai/build/skills) to package a reusable method, checklist, or procedure that an AI assistant can apply when a task matches.

A Skill is different from a saved Prompt. A Prompt stores reusable text or instructions. A Skill stores when to use a method, the method itself, and optional files such as examples, templates, or reference material.

By the end you will have a Skill with a clear description, instructions, and a test plan.

**Time to complete:** ~10 minutes

## Prerequisites {#prerequisites}

- An active Studio account.
- A repeatable task you want to standardize. Good first candidates are review checklists, report formats, or domain-specific analysis steps.

## Step 1: Open Skills {#step-1}

1. Open [Studio](https://console.mistral.ai).
2. In the sidebar, open `Build` > `Skills`.
3. Click `New Skill`.

## Step 2: Define when the Skill applies {#step-2}

Fill in the Skill details. The description is the most important field because it determines when the assistant loads the Skill.

| Field | Example |
|---|---|
| `Title` | `contract-risk-review` |
| `Description` | `Use when reviewing customer contracts for renewal, liability, or termination risk.` |

Write the description as a condition:

- **Vague**: *"Helps with contracts."*
- **Specific**: *"Use when reviewing customer contracts to identify renewal dates, termination clauses, liability caps, and missing approvals."*

## Step 3: Write the instructions {#step-3}

In the instructions field, write the procedure the Skill follows:

> When given a customer contract:
> 1. Extract renewal date, notice period, termination rights, and liability cap.
> 2. Flag missing approvals or unusual commercial terms.
> 3. Return a summary table with **Risk**, **Evidence**, and **Recommended action**.
>
> Do not invent missing terms. Mark unknown values as `Not found`.

Keep the Skill focused on one job. If you need several unrelated procedures, create separate Skills with separate descriptions.

## Step 4: Add files {#step-4}

Attach files when the Skill needs examples or reference material:

- A checklist in `checklist.md`.
- A preferred output template in `template.md`.
- A sample reviewed contract with comments.

## Step 5: Save and test {#step-5}

1. Click `Create Skill`.
2. Open a supported Studio surface that can use Skills.
3. Run a realistic task that matches the description.
4. Compare the output with your expected format.

## Step 6: Create a new version {#step-6}

Create a new version when you want to change the Skill without overwriting the version that assistants or workflows already use. Studio creates the new version after you save changes.

1. Open the Skill from the `Skills` list.
2. Update the instructions or attached files.
3. Add version notes that explain what changed, such as `Adds liability cap checks` or `Updates the summary table format`.
4. Click `Save`.
5. Confirm the version history shows the new version.

Older versions stay available for review and rollback. Test the new version before promoting it for production use.

## Verify {#verify}

Your Skill is ready if:

- It appears in the Skills list.
- The description explains exactly when the Skill applies.
- The output follows the procedure, format, and constraints you wrote.
- Attached files are relevant and referenced by the instructions.
- The version history shows your original version and the updated version.

## What's next {#whats-next}

- [Create a reusable Prompt](https://docs.mistral.ai/getting-started/quickstarts/studio/create-reusable-prompt)

- [Agents overview](https://docs.mistral.ai/studio-api/agents/introduction)

- [Skills in Vibe Work](https://docs.mistral.ai/vibe/work/skills)
