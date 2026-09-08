---
url: https://docs.mistral.ai/vibe/code/vs-code-extension/work-with-extension
title: Work with the extension
breadcrumbs: [Vibe, Code, VS Code extension]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/code/vs-code-extension/work-with-extension/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# Work with the extension

Use the VS Code extension when you want Vibe Code in the **same workspace as your files, selections, diffs, and source control**, with no context switch and no extra terminal.

## Open Vibe in VS Code {#open-vibe}

Open the extension from one of these entry points:

- Click the **Mistral Vibe** icon in the activity bar.
- Run **Mistral Vibe: Open Mistral Vibe** from the Command Palette.
- Use the editor title action when it appears for the active file.

The extension keeps the Vibe panel in a VS Code webview and runs the bundled Vibe ACP agent in the background.

## Use editor context {#editor-context}

The extension tracks your **active editor and current selection** so you don't have to copy paths or paste snippets:

| Context | How it works |
|---|---|
| **Active file** | Vibe receives a workspace mention for the active file. |
| **Selected lines** | Vibe receives the file mention with start and end line numbers. |
| **Selected text** | Vibe includes selected text when the selection has enough non-whitespace content and stays under the selection size limit. |

> **Tip**
>
> Highlight the code you want to discuss, then ask Vibe in plain language. The extension attaches the right context for you.

## Send a prompt {#prompt}

Write a focused request in the Vibe panel. Include the expected outcome and any constraints that matter.

Examples:

```text
Explain how authentication is wired in the selected file.
```

```text
Refactor this function to make error handling explicit. Keep the public API unchanged.
```

```text
Review this diff for edge cases before I open a pull request.
```

## Review actions {#review-actions}

When Vibe Code needs permission, the extension shows **approval controls in the webview**. Review the proposed action before approving it. For file changes, use VS Code's diff and source control views to inspect the result before committing or opening a pull request.

For the shared approval model, see [Safety, approvals, and permissions](https://docs.mistral.ai/vibe/code/safety-approvals-permissions).

## Current limits {#limits}

The extension doesn't expose every CLI command or workflow.

| Area | Extension behavior |
|---|---|
| **Slash commands** | Exposes a subset of CLI slash commands. See [Commands and slash commands](https://docs.mistral.ai/vibe/code/vs-code-extension/commands-slash-commands). |
| **CLI install** | Not required for normal extension use. |
| **Programmatic mode** | Not supported from the extension. For unattended runs, install the CLI and use `vibe --prompt`. |
