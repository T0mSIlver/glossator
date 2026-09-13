---
url: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/scaffold-a-project
title: Scaffold a project with Vibe Code
breadcrumbs: [Getting started, Quickstarts, Vibe Code]
kind: doc
locale: en
source_path: src/content/en/docs/getting-started/quickstarts/vibe-code/scaffold-a-project/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Scaffold a project with Vibe Code

Use the [Vibe CLI](https://docs.mistral.ai/vibe/code/overview) to generate a full project from a natural-language description, review every change before it's applied, and run the result.

- **Natural-language scaffolding**: describe what you want and the CLI creates the files.
- **Step-by-step confirmation**: Vibe Code splits large tasks into steps and asks for approval.
- **Full preview**: see every file change before it's written to disk.

By the end you'll have a working project scaffolded from a single prompt.

**Time to complete:** ~10 minutes

## Prerequisites {#prerequisites}

- Vibe CLI installed and configured. If you haven't done that yet, run the [Install the Vibe CLI](https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli) quickstart first.

> **Tip**
>
> Scaffolding is a good use case for the **`plan`** or **`accept-edits`** [agents](https://docs.mistral.ai/vibe/code/cli/agents). `plan` asks Vibe to outline what it will do before generating anything; `accept-edits` lets Vibe write files without prompting per step. The default agent asks for approval on every edit, which is safest for a first run.

## Step 1: Create an empty directory and launch the CLI {#step-1}

Start in a fresh directory so the CLI generates the project from scratch.

```bash
mkdir my-project && cd my-project
vibe
```

The CLI starts with an empty context, ready to scaffold.

> **Note**
>
> If you run `vibe` in an existing project with a `.vibe/` directory, the CLI asks whether you trust the folder before loading any local configuration. See [Trusted folders](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#trusted-folders).

## Step 2: Describe your project {#step-2}

Give the CLI a clear description. Be specific about language, framework, and key features. For example:

> Create a Python Flask API with two endpoints: a `/health` endpoint that returns `{"status": "ok"}` and a `/predict` endpoint that accepts a JSON body with a `"text"` field and returns `{"label": "positive", "score": 0.95}`. Include a `requirements.txt` and a `README`.

Vibe Code breaks the request into steps and begins generating files. Before creating or editing any file, it shows a preview.

![Vibe Code showing a preview of changes and asking for confirmation](https://docs.mistral.ai/assets/quickstarts/vibe/demo.png)

## Step 3: Review and approve changes {#step-3}

For each step, the CLI displays the files it plans to create or modify, the content of each file, and a confirmation prompt. Press one of the [approval keys](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#approval-model):

- **`Enter`**, **`1`**, or **`Y`** to approve this specific edit.
- **`2`** to approve all edits to this file in the current session.
- **`3`** to approve all edits in this directory.
- **`4`** to approve all edits in the working directory.
- **`N`** to reject and send feedback.

After each approved step, the CLI shows the result.

![Vibe Code displaying generated output and completed steps](https://docs.mistral.ai/assets/quickstarts/vibe/results.png)

Continue approving steps until the project is complete.

## Verify {#verify}

Check that the project was created:

```bash
ls -la
```

You should see the files Vibe Code generated (for example, `app.py`, `requirements.txt`, `README.md`).

Ask the CLI to start the server and test the endpoints for you:

> Install the dependencies, start the server, and run a curl against `/health` and `/predict` to verify they work.

Or run it yourself:

```bash
pip install -r requirements.txt
python app.py
```

Test the endpoints:

```bash
curl http://localhost:5000/health
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Mistral is great"}'
```

Both endpoints should return valid JSON responses.

## What's next {#whats-next}

- [Work with the CLI](https://docs.mistral.ai/vibe/code/cli/work-with-cli) — Master `@` file refs, `/` slash commands, `!` shell, `&` cloud send, and `resume`.

- [CLI agents](https://docs.mistral.ai/vibe/code/cli/agents) — Pick the right agent (default, plan, accept-edits, auto-approve).

- [CLI Skills](https://docs.mistral.ai/vibe/code/cli/skills)

- [Choose CLI, VS Code, or web sessions](https://docs.mistral.ai/vibe/code/choose-cli-vscode-web-sessions)
