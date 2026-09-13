---
url: https://docs.mistral.ai/vibe/work/files-and-canvas
title: Work with Files and Canvas
breadcrumbs: [Vibe, Work]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/work/files-and-canvas/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
---

# Work with Files and Canvas

**Files** bring source material into a task. **Canvas** is the built-in editor where Work produces, previews, and refines outputs.

Together, they let you go from a raw upload (CSV, PDF, screenshot, document) to a polished, editable deliverable without leaving the chat interface.

> **Info**
>
> Files and Canvas are available on **all plans** with no setup required. Usage limits apply based on your plan. See our [pricing page](https://mistral.ai/pricing) for details.

## Files: bring source material into a task {#files}

Upload documents, images, and spreadsheets directly into a chat. Work reads the content and uses it as context, so you can ask questions, extract information, and get answers based on your data.

### How to upload {#how-to-upload}

Two ways to get files into a chat:

- **Drag and drop**: drag one or more files into the chat window.
- **`+` button**: click the `+` icon in the chat toolbar then select `Upload Files` and select files from your device.

You can upload multiple files at once (or even a folder). Work keeps them in context for the full chat, so you can ask follow-up questions without re-uploading.

> **Tip**
>
> Use descriptive filenames. They make it easier to reference specific files when you have several in the same chat.

### Supported formats {#supported-formats}

| Category | Formats |
|----------|---------|
| **Documents** | PDF, Word (`.docx`, `.doc`), PowerPoint (`.pptx`, `.ppt`), ODT, EPUB, RTF |
| **Spreadsheets** | Excel (`.xlsx`, `.xls`), CSV, ODS, Numbers |
| **Images** | PNG, JPEG, WebP, GIF |
| **Text and markup** | TXT, Markdown, RST, LaTeX |
| **Data formats** | JSON, JSONL, XML, YAML |
| **Code files** | Python, JavaScript/TypeScript, Java, Go, Rust, C/C++, Ruby, PHP, SQL, and more |
| **Email** | EML, MSG |

### Querying text documents {#querying-documents}

Upload a PDF, Word file, or presentation and ask Work to focus on what matters to you. Answers come directly from the uploaded content, not from general knowledge.

Typical prompts:

- *"Summarize this annual report with a focus on financial risks."*
- *"Extract all dates, parties, and obligations from this contract."*
- *"List the key security findings in this audit report."*
- *"Compare slide 3 and slide 7 and list the differences."*

Follow up to go deeper. Work remembers uploaded files throughout the chat, so you can refine, drill into specifics, or ask for translations without re-uploading.

### Analyzing images {#analyzing-images}

Work can interpret photos, diagrams, screenshots, and scanned pages. Upload an image with the `+` button and ask your question.

- **Text extraction**: *"Extract all the text from this scanned invoice."* Works with handwritten notes, printed forms, and photographed whiteboards.
- **Diagram interpretation**: *"Describe the architecture shown in this diagram."*
- **Screenshot analysis**: *"What error is shown in this screenshot?"*

> **Note**
>
> For heavier document processing needs (structured extraction from scanned PDFs, multi-page forms, or handwritten content in bulk), check Studio's [Document AI](https://docs.mistral.ai/studio/document-processing/overview) features.

### Analyzing spreadsheets {#analyzing-spreadsheets}

For tabular files like CSV or Excel, Work can answer questions, summarize, and extract data directly from the upload.

Typical prompts:

- *"Show me all sales from the North region."*
- *"What's the average deal size by quarter?"*
- *"List the top 10 customers by revenue."*

> **Note**
>
> For Python-based data analysis (custom statistics, charts, transformations), use [Code Interpreter](https://docs.mistral.ai/vibe/chat-legacy/code-interpreter) in Chat.

## Canvas: review, edit, and iterate on Work's output {#canvas}

Canvas is the built-in editor where Work produces and refines text, data, code, and presentations. You go from a raw upload to a polished deliverable without leaving the chat.

### Activation {#activation}

1. Click the `+` icon or type `/` in the chat window.
2. Select `Tools` then enable `Canvas`.

Once activated, Canvas **opens automatically** when Work determines it would be useful. You can also **trigger it manually** by typing `/canvas` in the message box or asking Work to *"open in Canvas"* in your prompt.

Typical prompts that open Canvas:

- *"Create a presentation outline for our Q3 results."*
- *"Analyze the attached CSV and show it as a table."*
- *"Write a Python script to parse JSON logs."*

### Canvas features {#canvas-features}

**Editing**

Work directly in the Canvas like you would in any editor.

- **Direct editing**: click anywhere to edit text, code, or data by hand. Fix a typo, rename a column, or rewrite a paragraph.
- **Multiple Canvases**: open several Canvases in one chat. Each one appears as a tab, so you can switch between a data table and a draft report without losing context.
- **Version control**: use the navigation arrows to move between versions. Toggle the change-tracking view to see exactly what changed. Restore any previous version at any time.

**AI assistance**

Let Work refine, translate, or transform your content.

- **Inline prompts**: select a passage to reveal the `Ask Work` field. Type a request (*"make this more concise"*, *"translate to French"*) and Work applies the change to the selection only.
- **Quick actions**: click the sparkle icon for context-aware shortcuts like translate, optimize, or visualize. Available actions depend on the content type.
- **Preview mode**: click the eye icon to toggle between raw content and rendered output. Supports HTML, React components, [Mermaid](https://mermaid.js.org/) diagrams (text-based charts and flowcharts), and [Marp](https://marp.app/) presentations (text-based slides).

**Export and sharing**

Get your work out of Canvas and into your tools.

- **Export**: save Canvas output as a file. For example, export a slide deck as PowerPoint or a table as a CSV/Excel file.
- **Share**: distribute the full chat, including Canvas content.
- **Copy**: transfer raw Canvas content to your clipboard.

## Common use cases {#use-cases}

- **Quarterly reports**: upload financial data, generate tables and summaries, export as slides.
- **Project briefs**: draft structured documents with inline AI editing.
- **Contract review**: extract clauses, parties, dates, and obligations from PDF uploads.
- **Data exploration**: query CSVs and spreadsheets with direct editing.
- **Image and screenshot analysis**: extract text, interpret diagrams, debug error screens.
- **Presentations**: build and preview Marp slide decks without leaving Work.
- **Code prototyping**: write and iterate on Python scripts or React components.
- **Email and content drafts**: compose, refine, and translate written content with inline prompts.

## Worked example: from data to slides {#practical-workflow}

Files and Canvas shine when chained together. Here's a typical sequence for turning a raw upload into a shareable deliverable.

### Upload and explore your data {#upload-explore}

Import a CSV or spreadsheet using the `+` button and select `Upload Files`, then ask:

```text
Analyze the attached CSV and open it in Canvas.
```

Canvas displays your data as an editable table. Click into cells to fix headers, rename columns, or remove empty rows.

> **Tip**
>
> If Canvas opens in the wrong format, ask *"Show this as a table"* and it will switch.

### Generate a written summary {#generate-summary}

Once your data looks right, ask Canvas to produce a text summary:

```text
Transform this table into a concise executive summary.
```

Canvas drafts a write-up based on your data. You can edit the result directly or use inline prompts to refine specific sections.

### Create a slide deck {#create-slides}

Turn your analysis into presentation-ready slides:

```text
Create slide-ready bullet points with the key insights and recommendations.
```

Canvas generates slides using [Marp](https://marp.app/) syntax, a text-based format for presentations. Click the **eye icon** to preview the rendered deck.

When the slides look good, use the export button to save the deck as a PowerPoint file for final adjustments in your preferred tool.

## Tips for better results {#tips}

- **Be specific.** Tell Work what to focus on: *"Summarize this contract for a compliance officer"* gives better results than *"Summarize this file."*
- **Use action verbs.** Summarize, extract, compare, explain, highlight, list, convert.
- **Reference files explicitly.** When you have several uploads, mention the filename: *"In `AnnualReport_2024.pdf`, page 14, extract the revenue breakdown."*
- **Iterate.** Follow up with requests to refine, translate, or reformat the output.
- **Verify before sharing.** Treat generated content as a draft. Check facts, numbers, and citations against the source.
