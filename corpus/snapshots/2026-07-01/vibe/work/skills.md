---
url: https://docs.mistral.ai/vibe/work/skills
title: Reuse work with Skills
breadcrumbs: [Vibe, Work]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/work/skills/page.mdx
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
---

# Reuse work with Skills

Skills are **reusable instructions and resources** that give Work specialized capabilities for specific tasks. Use them when a task has a known method, checklist, template, output format, or domain-specific procedure: package an approach once and Work applies it whenever the task matches, with the same tone, format, and procedure every time.

> **Info**
>
> Skills follow the open [Agent Skills](https://agentskills.io/home) standard, originally developed by Anthropic and now adopted across multiple agentic clients. Each Skill is a folder containing a `SKILL.md` file (instructions + metadata) and any extra files Work should use alongside it (references, templates, examples, data).

## How Skills work {#how-skills-work}

Work loads Skills through **progressive disclosure** in three stages:

1. **Discovery**: at session start, Work loads only each Skill's name and description (~100 tokens each), just enough to know when it might be relevant.
2. **Activation**: when a task matches a Skill's description, Work reads the full `SKILL.md` instructions into context.
3. **Execution**: Work follows the instructions, optionally loading referenced files or running examples as needed.

This means you can have many Skills enabled without overloading context: only the relevant ones expand into full instructions.

> **Tip**
>
> The Skill's **description** is what determines when it activates. Write descriptions that describe **when** to use the Skill, not just what it does (for example, *"Use when reviewing customer contracts for renewal risks"* rather than *"Helps with contracts"*).

## Built-in Skills {#built-in-skills}

Vibe Work ships with a set of **built-in Skills** covering common productivity tasks. They appear in your Skills list alongside personal and workspace ones, activate automatically when a task matches, and can be invoked explicitly with `/{skill-name}`. Disable any you don't need from `Context` > `Skills`.

| Skill | Triggers on |
|---|---|
| `challenge-my-thinking` | Pressure-test a plan, devil's advocate, "what am I missing", risk review. |
| `data-analysis` | Inspect, clean, transform, or aggregate data (`.csv`, `.json`, tables, metrics, anomalies). |
| `deep-research` | Thorough research, source-backed synthesis, market or technical landscape analysis. |
| `doc-coauthoring` | Co-author proposals, technical specs, decision docs, RFCs. |
| `document-review` | Review documents for completeness, compliance, consistency, or quality. |
| `internal-comms` | Status reports, leadership updates, 3P updates, FAQs, incident reports. |
| `meeting-prep` | Prepare for upcoming meetings, brief on calendar items. |
| `research-synthesis` | Synthesize multiple sources, notes, or files into a structured brief. |
| `skill-creator` | Create, update, or delete Skills (loaded before any Skill edit). |
| `stakeholder-translator` | Reframe content for a different audience (exec, engineering, leadership). |
| `structured-extraction` | Extract structured data (tables, JSON) from emails, PDFs, or free-text. |
| `vibe-work-onboarding` | Walk through Vibe Work capabilities for first-time users. |

### Example: `/deep-research` {#example-deep-research}

To see a built-in Skill in action, trigger `deep-research` explicitly:

> `/deep-research` What are the main approaches to long-context LLMs in 2026?

Work plans the search, runs multiple web queries, synthesizes the sources, and returns a structured brief with citations, opened in [Canvas](https://docs.mistral.ai/vibe/work/files-and-canvas).

## Personal and workspace Skills {#personal-vs-workspace}

Open the sidebar and go to `Context` > `Skills` to see your Skills, organized in two more sections:

- **Personal**: Skills you've created for your own use. Only you see them.
- **Workspace**: Skills shared across your workspace. Anyone in the workspace can use them.

Toggle each Skill on or off individually to control which ones load into Work's context.

> **Note**
>
> Workspace admins can **force-enable** specific Skills for the whole workspace (for example, a finance team's domain Skills). Force-enabled Skills are always active and can't be disabled by individual users.

## Using Skills in a task {#using-skills}

Once a Skill is enabled, Work uses it automatically when the task matches its description. You can also invoke a Skill explicitly:

- **Slash command**: type `/` in the chat window and pick a Skill from the list, or type `/{skill-name}` directly.
- **Natural reference**: mention the Skill by name in your prompt (for example, *"Use the contract-review Skill on this PDF"*).

When a Skill is active in a task, Work surfaces it in the chat so you know which one is being applied.

## Creating a Skill {#creating-skills}

There are two ways to create a Skill: build it manually in the editor, or have Work create one for you from a chat.

### Create from the editor {#create-from-ui}

1. Open `Context` > `Skills` in the sidebar.
2. Click `New Skill`.
3. Fill in the form:
   - **Title**: a short, descriptive name (for example, `Brand voice copywriting`).
   - **Description**: when Work should use this Skill. This text is what Work reads at discovery to decide whether to activate the Skill, so make it specific.
   - **SKILL.md**: the full instructions Work follows when the Skill activates. Write them as you would brief a colleague: tone, format, steps, examples.
4. (Optional) Add **files or folders** alongside the Skill (reference documents, templates, brand guidelines, sample outputs, datasets). Work loads them as needed when the Skill activates.
5. Click `Create Skill`.

### Create a Skill from a task (recommended) {#create-from-chat}

The fastest way to build a Skill is to let Work draft it for you from a real task:

1. Run a task where you refine an approach you'd like to reuse (a writing style, a review checklist, a research method).
2. Ask Work to *"turn this into a Skill"* or *"save this as a Skill"*.
3. Work generates a `SKILL.md` draft, lists the contents, and proposes it for review.
4. Edit if needed, then save.

> **Tip**
>
> Skills built from real usage capture the actual patterns that worked, including details you wouldn't think to write down from scratch. Iterate in a task, save when satisfied, then refine over time.

## Editing and managing Skills {#managing-skills}

From the `Context` > `Skills` page, you can:

- **Edit** a Skill's title, description, `SKILL.md`, or attached files.
- **Disable** a Skill without deleting it.
- **Delete** a personal Skill (workspace Skills require the appropriate permission).
- **Publish** a personal Skill to your workspace so teammates can use it.

When you edit a Skill, your changes take effect in new chats from that point on. Active chats keep the previous version until you start a new one.

## Best practices {#best-practices}

- **Build Skills from real tasks.** See [Create a Skill from a task](https://docs.mistral.ai/vibe/work/skills#create-from-chat) above. It's the highest-leverage way to start.
- **Write descriptions as triggers.** The description tells Work **when** to activate the Skill. *"Use when..."* phrasing beats *"This Skill helps with..."* every time.
- **Keep Skills focused.** One Skill per job. If a Skill grows into many unrelated procedures, split it.
- **Avoid near-duplicates.** Two Skills with overlapping descriptions confuse Work and inflate context. Edit the existing Skill rather than saving a slight variant.
- **Bundle supporting files.** Templates, brand guides, sample outputs, or reference data live next to the `SKILL.md` and load when the Skill activates. Supporting files are subject to a file-count limit; for larger methods, use [progressive disclosure](https://agentskills.io/skill-creation/best-practices#structure-large-skills-with-progressive-disclosure).
- **Iterate.** Run the Skill on real tasks, note what's missing, edit, and improve.
