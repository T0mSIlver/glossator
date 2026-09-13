---
url: https://docs.mistral.ai/vibe/chat-legacy/deep-research
title: Deep Research
breadcrumbs: [Vibe, Chat]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/chat-legacy/deep-research/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
---

# Deep Research

> **Warning**
>
> Deep Research is a legacy Chat feature. It remains available in the **Chat** tab, with no public deprecation date.
>
> Vibe Work covers the same use case with the [`/deep-research` Skill](https://docs.mistral.ai/vibe/work/skills) and [Canvas](https://docs.mistral.ai/vibe/work/files-and-canvas). The Chat implementation doesn't work with Connectors and is no longer actively developed.

Deep Research automates **multi-step web research** in Vibe. It breaks down your question, searches multiple sources, evaluates findings, and generates a structured report with citations, **reducing hours of manual work to minutes**.

You can use it for competitive landscape analysis, regulatory reviews, industry trend reports, or any question that benefits from pulling together information across multiple sources.

## How it works {#how-it-works}

Deep Research follows a three-stage process:

1. It creates a **search plan** based on your question.
2. It **browses the web**, gathering information from multiple sources.
3. It synthesizes everything into a structured, cited **report**.

Your question can be open-ended (*"What are the latest trends in enterprise AI adoption?"*) or specific (*"Generate a report on renewable energy regulations in the EU for 2024-2025."*).

If your query is too broad, Vibe will ask you to **add more context** before starting.

## Starting a research task {#starting-a-research-task}

1. Select the **Chat** tab in the sidebar.
2. Select the `Research` option (`Fast` is the default) below the message box.
3. Type your question and send it.

> **Note**
>
> When you enable Research mode, Libraries, Connectors, and Agents are temporarily disabled. They become available again once you switch back to standard chat.

## Reviewing and editing the search plan {#reviewing-the-search-plan}

Before searching, Vibe proposes a step-by-step research plan. You have full control over this plan:

- Click `Edit` to add, remove, or reorder steps.
- Reply in the chat to suggest changes in natural language.
- Click `Start research` when the plan looks right.

Editing the plan lets you steer the research toward the sources and angles that matter most for your use case.

## Tracking progress {#tracking-progress}

Research runs **as a background task**. A progress widget shows live updates, search summaries, and reasoning **as Vibe works through each step**.

You don't need to wait. You can open other conversations and come back when the research is done. To stop a research task early, click `Cancel` in the progress widget and confirm.

## Working with results {#working-with-results}

When research finishes, the report appears in your conversation. It includes:

- **Summary**: a concise overview of the key findings at the top.
- **Full report**: detailed analysis with supporting arguments, data, and inline citations.
- **Sources**: a list of all sources used, so you can verify findings or dig deeper.

You can export and share your report:

- Click `Save as PDF` to download a formatted version for sharing, printing, or archiving.
- Share reports with colleagues using the standard conversation sharing feature.

## Tips for better results {#tips}

- **Be specific in your query.** *"Market trends for residential solar in Western Europe, 2023-2025"* produces a more focused report than *"Tell me about solar energy."*
- **Edit the search plan.** Adding or removing steps helps you get exactly the depth and scope you need.
- **Use detailed briefs for complex topics.** Include the region, time frame, industry, or angle you care about. The more context you provide, the more relevant the report.

## Related features {#related-features}

- **[Web search and Open URL](https://docs.mistral.ai/vibe/work/web-search-open-url)**: quick, single-step lookups for current information.
- **[Files and Canvas](https://docs.mistral.ai/vibe/work/files-and-canvas)**: refine and iterate on research outputs in an editor.
