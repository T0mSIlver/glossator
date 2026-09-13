---
url: https://docs.mistral.ai/vibe/chat-legacy/code-interpreter
title: Code Interpreter
breadcrumbs: [Vibe, Chat]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/chat-legacy/code-interpreter/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
---

# Code Interpreter

> **Warning**
>
> Code Interpreter is a legacy Chat feature. It remains available in the **Chat** tab, with no public deprecation date.
>
> Vibe Work has a built-in **TypeScript code environment** that covers most data-processing and graphing use cases, including cleaning data, generating charts, and transforming files. Pick Work when TypeScript fits the task. Pick Chat with Code Interpreter when you specifically need Python or a Python-only library.

Code Interpreter lets you **run Python directly inside Vibe**.

Not a developer? No problem. Describe what you want in plain language, and Vibe generates and executes the code for you.

> **Info**
>
> Code runs in a **secure, isolated environment** with no internet access. It cannot reach your system or external services. Common data-analysis packages are preinstalled (pandas, numpy, matplotlib). Uploaded files are available for the current conversation only.

## Common use cases {#use-cases}

Code Interpreter combines the versatility of Vibe with the precision of Python. It's perfect for:

- **Data analysis**: explore CSV, XLSX, or JSON files. Summarize, filter, flag outliers, or clean missing values.
- **Charts and visuals**: generate line charts, bar charts, pie charts, or any Matplotlib visualization from your data.
- **Calculations**: work through formulas, financial models, or unit conversions with verified accuracy.
- **File transformations**: convert formats, merge datasets, or export processed results as downloadable files.

## Activation {#activation}

Code Interpreter must be enabled before Vibe can use it.

1. Select the **Chat** tab in the sidebar.
2. Click the `+` icon or type `/` in the chat window.
3. Select `Tools` then enable `Code Interpreter`.

The tool stays active for the duration of the conversation and subsequent chats.

> **Note**
>
> Code Interpreter usage is **subject to rate limits** based on your plan. For details, visit our [pricing page](https://mistral.ai/pricing).

## Running code {#running-code}

Describe what you want **in plain language** and Vibe writes and executes the Python code for you.

```text
Load this CSV and show the top 5 rows, then plot sales by month.
```

The code runs in the sandbox and returns tables, figures, or files inline. You can follow up to refine results, adjust filters, or ask for explanations of what the code does.

> **Info**
>
> Code Interpreter cannot fetch files directly from URLs. If your data is online, download it locally and upload the file. Alternatively, enable [Web search](https://docs.mistral.ai/vibe/work/web-search-open-url) and ask Vibe to fetch the data before running code.

## Working with files {#working-with-files}

Upload files using the `+` button in the chat toolbar. Supported formats include:

- **Documents**: PDF, Word (`.docx`, `.doc`), PowerPoint (`.pptx`, `.ppt`), ODT, EPUB, RTF
- **Spreadsheets**: Excel (`.xlsx`, `.xls`), CSV, ODS, Numbers
- **Images**: PNG, JPEG, WebP, GIF
- **Text and markup**: TXT, Markdown, RST, LaTeX
- **Data formats**: JSON, JSONL, XML, YAML
- **Code files**: Python, JavaScript/TypeScript, Java, Go, Rust, C/C++, Ruby, PHP, SQL, and many more
- **Email**: EML, MSG

Typical prompts:

- *"Summarize this spreadsheet and flag outliers."*
- *"Clean this CSV, fix missing values, and export a new file."*
- *"Extract all emails from this PDF and give me a CSV."*

> **Note**
>
> For details and advanced workflows, see the [Files and Canvas](https://docs.mistral.ai/vibe/work/files-and-canvas) article.

## Tips for better results {#tips-for-better-results}

- **Be specific.** For charts or tables, specify column names, filters, and the desired output format.
- **Ask for explanations.** Try *"Explain the steps and show the code"* to understand what's happening.
- **Iterate.** Follow up with requests to fine-tune the output (e.g., *"Now add a rolling average and label the axes."*)
- **Prototype with smaller files.** If you hit a limit, upload a sample to test your approach, then scale up.
- **Avoid sharing secrets.** Never share API keys or credentials in the chat or in code.

## Related features {#related-features}

- **[Files and Canvas](https://docs.mistral.ai/vibe/work/files-and-canvas)**: edit and refine code, data, and text, and import documents, spreadsheets, and images into your conversation.
