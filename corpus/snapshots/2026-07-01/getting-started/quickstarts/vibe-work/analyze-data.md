---
url: https://docs.mistral.ai/getting-started/quickstarts/vibe-work/analyze-data
title: Analyze a dataset
breadcrumbs: [Getting started, Quickstarts, Vibe Work]
kind: doc
locale: en
source_path: src/content/en/docs/getting-started/quickstarts/vibe-work/analyze-data/page.mdx
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
---

# Analyze a dataset

Upload a spreadsheet to [Work](https://chat.mistral.ai/work) and ask questions about it in plain language. Work picks the right tools (file reader, built-in code sandbox, Canvas) to compute summaries, generate charts, and run follow-up analyses. You write no code.

**Time to complete:** ~10 minutes

## Prerequisites {#prerequisites}

- A Mistral account (Free plan is enough to try, paid plans recommended for heavier datasets).
- A data file to analyze (CSV, XLSX, or JSON).

## Step 1: Upload your data {#step-1}

1. Open [chat.mistral.ai](https://chat.mistral.ai/work) and switch to the **Work** tab.
2. In the chat toolbar, click the `+` icon, then select `Upload Files` and pick your data file (for example `sales-q4-2025.csv`).
3. Work shows a preview of the file. Confirm it looks correct.

For best results, use files with clear column headers. Work reads them to understand the schema before running anything.

## Step 2: Ask a question about your data {#step-2}

Type a question in plain language. Work writes and runs code in a sandbox and returns tables, charts, and explanations directly in **[Canvas](https://docs.mistral.ai/vibe/work/files-and-canvas)**, a side panel that opens automatically when Work needs to display a document, a chart, or a long output you can edit. You can also ask for it explicitly with phrases like *"open this in Canvas"* or *"visualize this file"*.

**Try one of these:**

> Summarize this dataset. How many rows and columns are there? What are the key statistics per column?

> Show me monthly revenue trends as a line chart.

> What are the top 5 products by total sales? Display as a bar chart.

> Calculate the correlation between marketing spend and revenue, and explain the result.

Work shows the code it ran alongside the result, so you can verify the logic.

## Step 3: Refine and export {#step-3}

Build on previous results by asking follow-up questions. Work keeps the data in context across the conversation.

1. **Refine a chart**: *"Make the chart wider and add data labels."*
2. **Filter data**: *"Show only rows where region is Europe."*
3. **Compare periods**: *"Compare Q3 vs Q4 revenue by product category."*

To save your work, use the **Export** button in Canvas to download tables as CSV/Excel or charts as image files. You can also copy tables directly from the Canvas view, or ask Work to *"open this in Canvas"* to turn the analysis into an editable document.

## Verify {#verify}

Your analysis is working if:

- Work correctly identifies column names and data types.
- Generated charts match the data in your file.
- Follow-up questions reference the same dataset without re-upload.
- Statistical results (mean, median, correlation) match what you expect.

If a column is misinterpreted, clarify it explicitly: *"The 'Date' column is in DD/MM/YYYY format."*

## What's next {#whats-next}

- [Create your first Skill](https://docs.mistral.ai/getting-started/quickstarts/vibe-work/create-first-skill)

- [Files and Canvas](https://docs.mistral.ai/vibe/work/files-and-canvas)

- [Choose Chat, Work, or Code](https://docs.mistral.ai/vibe/choose-chat-work-code) — When to pick Code Interpreter (Python) over Work's built-in code env.

- [All Vibe Work quickstarts](https://docs.mistral.ai/#quickstarts)
