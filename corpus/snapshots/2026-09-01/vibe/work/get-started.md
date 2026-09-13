---
url: https://docs.mistral.ai/vibe/work/get-started
title: Get started with Work
breadcrumbs: [Vibe, Work]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/work/get-started/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Get started with Work

**Vibe Work** is Vibe's productivity mode for delegating complex, multi-step tasks across your apps and tools.

Describe the outcome you want **in natural language**: Work gathers context, breaks the task into steps, calls the right tools, and asks for approval before sensitive actions.

This guide shows how to start a task in Work, give it the right context, follow its progress, and review the result.

## Open Work {#open-work}

1. Open [Work](https://chat.mistral.ai/work).
2. If the sidebar is closed, click the drawer icon or press `Cmd+Shift+B` on macOS or `Ctrl+Shift+B` on Windows and Linux.
3. In the sidebar, select **Work** from the mode selector.
4. Start your task.

Vibe remembers the last tab you selected. If **Chat** or **Code** opens by default, select **Work** in the sidebar before starting the task.

> **Tip**
>
> Not sure which mode to use? See [Choose Chat, Work, or Code](https://docs.mistral.ai/vibe/choose-chat-work-code).

## Start a task {#start-a-task}

Start with the outcome you want. Work reasons through the request, breaks it into smaller steps, and calls tools when needed.

> **Info**
>
> **You stay in control: **Work shows progress and asks for confirmation before sensitive actions. See [Safety and approvals](https://docs.mistral.ai/vibe/work/safety-and-approvals) for more info.

A good first prompt includes:

- the result you want
- the source material or tools Work should consider
- the audience for the output
- any constraints, such as length, tone, format, or deadline

Try prompts such as:

- `Research this topic and create a one-page brief I can share with my team.`
- `Summarize this PDF and extract owners, deadlines, and action items.`
- `Compare these two documents and highlight the main differences.`
- `Create a draft response based on this source material.`

> **Note**
>
> Use **Chat** if you want a quick turn-based conversation, or to use legacy features such as [Agents](https://docs.mistral.ai/vibe/chat-legacy/agents), [Think mode](https://docs.mistral.ai/vibe/chat-legacy/think-mode), [Code Interpreter](https://docs.mistral.ai/vibe/chat-legacy/code-interpreter), or [Memories](https://docs.mistral.ai/vibe/chat-legacy/memories). For Deep Research, use the [Deep Research Skill](https://docs.mistral.ai/vibe/work/skills) in Work.

## Give Work the right context {#give-work-context}

Work selects the right tools and context from your prompt automatically. You can also point it to a specific source when you want full control.

Work draws on the following capabilities:

- [Connectors](https://docs.mistral.ai/vibe/work/connectors): connect tools such as email, calendar, Slack, Notion, GitHub, Google Drive, or SharePoint so Work can use approved external data.
- [Libraries](https://docs.mistral.ai/vibe/work/libraries): use curated document collections that are already uploaded and indexed.
- [Skills](https://docs.mistral.ai/vibe/work/skills): apply repeatable methods, checklists, or templates to a task.
- [Files and Canvas](https://docs.mistral.ai/vibe/work/files-and-canvas): upload documents, spreadsheets, presentations, PDFs, or images for Work to read, summarize, extract, or turn into reviewable outputs.
- [Web search and Open URL](https://docs.mistral.ai/vibe/work/web-search-open-url): use public information or ask Work to read a specific web page.

> **Note**
>
> Work can ask you to connect or authenticate a missing tool during a task. Your organization settings can also affect which tools are available.

## Follow the todos and progress {#follow-progress}

For longer tasks, Work displays a live **todos panel** in the right-hand panel as it works, and may ask you **follow-up questions** when your prompt is ambiguous. It also shows progress, tool calls, and intermediate outputs while it works.

Use these checkpoints to stay in control:

- Watch the todos as they appear to see what Work is doing.
- Approve or deny sensitive actions when prompted.
- Stop the task with the **stop** button (the black square) if Work goes the wrong direction.
- Redirect with a follow-up message if Work chooses the wrong source or approach.

> **Note**
>
> Work asks for approval before sensitive actions such as sending email, posting messages, creating calendar events, deleting issues, or changing data in external tools.
>
> For more detail, see [Safety and approvals](https://docs.mistral.ai/vibe/work/safety-and-approvals).

## Review the result before using it {#review-result}

Treat Work outputs as drafts until you review them. Before you use or share the result:

- Read the final summary.
- Review generated content in [Canvas](https://docs.mistral.ai/vibe/work/files-and-canvas) or files.
- Check facts, tables, dates, names, owners, and source references.
- Verify extracted information against the original file or source when accuracy matters.
- Ask Work to revise the output if the audience, tone, structure, or facts are wrong.
- Approve, edit, share, or reuse the result only after review.

## Make repeated work easier {#repeated-work}

After your first tasks, use Vibe settings and reusable context to reduce repeated instructions:

| Use case | Feature |
|---|---|
| Stable preferences such as tone, format, language, or recurring constraints | [Custom instructions](https://docs.mistral.ai/vibe/work/custom-instructions) |
| Related work around the same team, customer, initiative, or topic | [Projects](https://docs.mistral.ai/vibe/work/projects) |
| Repeatable procedures and task-specific guidance | [Skills](https://docs.mistral.ai/vibe/work/skills) |
| Predefined processes (when your workspace supports them) | [Workflows](https://docs.mistral.ai/vibe/work/workflows) |
| Run a prompt on a schedule (one-off, daily, weekly, monthly, yearly) | [Schedule tasks](https://docs.mistral.ai/vibe/work/scheduled-tasks) |
