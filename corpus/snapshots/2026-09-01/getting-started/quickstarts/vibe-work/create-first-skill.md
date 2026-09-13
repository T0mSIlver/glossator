---
url: https://docs.mistral.ai/getting-started/quickstarts/vibe-work/create-first-skill
title: Create your first Skill
breadcrumbs: [Getting started, Quickstarts, Vibe Work]
kind: doc
locale: en
source_path: src/content/en/docs/getting-started/quickstarts/vibe-work/create-first-skill/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Create your first Skill

Package a repeatable method into a **Skill** so [Work](https://chat.mistral.ai/work) applies the same procedure, format, and tone every time the task matches.

Skills follow the open [Agent Skills](https://agentskills.io/home) standard. Each Skill is a folder with a `SKILL.md` file (instructions + metadata) and optional files (templates, references, examples). Work loads only the relevant Skills into context via **progressive disclosure**, so you can have many enabled without bloat.

**Time to complete:** ~10 minutes

## Prerequisites {#prerequisites}

- A Mistral account with Vibe Work access. Workspace admins can force-enable or disable Skills at the workspace level.
- A repeatable task you handle often. Good first candidates: a meeting summary template, a code-review checklist, a weekly-report format.

## First, try a built-in Skill {#try-built-in}

Before building your own, see what a Skill does in practice. Vibe Work ships with [built-in Skills](https://docs.mistral.ai/vibe/work/skills#built-in-skills) you can invoke immediately. Try `/deep-research`:

> `/deep-research` What are the main approaches to long-context LLMs in 2026?

Work plans the search, runs multiple web queries, synthesizes the sources, and returns a structured brief with citations in [Canvas](https://docs.mistral.ai/vibe/work/files-and-canvas). That's a Skill in action: one trigger, a packaged procedure, a consistent output format.

Now create your own to capture a procedure you reuse.

## Step 1: Open the Skills view {#step-1}

1. Open [chat.mistral.ai](https://chat.mistral.ai/work) and switch to the **Work** tab.
2. In the left sidebar, open `Context` > `Skills`.
3. Click **New Skill**.

You'll see three sections: **Built-in** (shipped with Vibe Work), **Personal** (only you see them), and **Workspace** (shared with your team).

> **Tip**
>
> **Recommended path: let Work draft a Skill from a real task.** Run a task where you refine an approach you want to reuse, then ask Work *"turn this into a Skill"*. Work generates a `SKILL.md` draft, lists the contents, and proposes it for review. It captures the patterns that actually worked, including details you wouldn't think to write down from scratch. See [Skills](https://docs.mistral.ai/vibe/work/skills#create-from-chat) for the full flow.

## Step 2: Fill in the Skill form {#step-2}

The form has three fields. The **description** is the most important: it tells Work *when* to activate the Skill.

| Field | Example |
|---|---|
| **Title** | `Meeting summary` |
| **Description** | `Use when the user pastes meeting notes or a transcript and asks for a summary. Produces an executive summary, action items with owners, and open questions.` |
| **`SKILL.md`** | The full instructions Work follows when the Skill activates (see step 3). |

Write the description as a trigger condition:

- **Vague**: *"Helps with meetings."*
- **Specific**: *"Use when reviewing customer-call transcripts to extract objections and next steps."*

The specific version is what makes Work pick the Skill up reliably at discovery.

## Step 3: Write the `SKILL.md` instructions {#step-3}

In the `SKILL.md` field, write the procedure Work should follow. Be explicit about format, tone, and what to avoid:

> When given meeting notes or a transcript, produce:
> 1. A one-paragraph executive summary (max 80 words).
> 2. A bulleted list of action items with owners and due dates if available.
> 3. A list of open questions.
>
> Tone: professional, concise. Don't invent information that isn't in the source. If owners or dates are missing, mark them as `[TBD]`.

Keep instructions tight. If a step needs an example, attach a sample file or template alongside the Skill (templates, references, brand guidelines, sample outputs). Supporting files are subject to a file-count limit, so keep references focused and use progressive disclosure for larger methods. See [Structure large Skills with progressive disclosure](https://agentskills.io/skill-creation/best-practices#structure-large-skills-with-progressive-disclosure) for guidance.

## Step 4: Create and test {#step-4}

1. Click **Create Skill** to register it.
2. Start a new Work task and paste a real example of the source material (meeting notes, transcript, etc.).
3. Watch the todos panel: if the description matches, Work picks the Skill up automatically. You can also invoke it explicitly with `/{skill-name}` or by mentioning it in your prompt.
4. Compare the output to your expected format. Iterate on the `SKILL.md` if anything is off.

## Step 5: Share with your team (optional) {#step-5}

If the Skill is useful beyond your own work, share it with the workspace:

1. From the Skills view, open the Skill.
2. Click **Share**.
3. Choose whether to keep the Skill private or share it with the entire workspace.
4. Workspace admins can also **force-enable** specific Skills for everyone in the workspace.

## Verify {#verify}

Your Skill is working if:

- It appears in the Skills view under the correct scope (Personal or Workspace).
- Work activates it automatically on matching tasks (you'll see it referenced in the todos).
- The output follows your format, tone, and constraints consistently across different inputs.

## What's next {#whats-next}

- [Skills reference](https://docs.mistral.ai/vibe/work/skills) — Full doc: progressive disclosure, file bundling, edits, sharing.

- [Custom instructions](https://docs.mistral.ai/vibe/work/custom-instructions) — Set persistent preferences that apply across tasks.

- [Safety and approvals](https://docs.mistral.ai/vibe/work/safety-and-approvals) — How Skills interact with Connector approvals and workspace controls.

- [All Vibe Work quickstarts](https://docs.mistral.ai/#quickstarts)
