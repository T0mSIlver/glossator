---
url: https://docs.mistral.ai/vibe/code/vibe-code-web/get-started
title: Get started
breadcrumbs: [Vibe, Code, Vibe Code Web]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/code/vibe-code-web/get-started/page.mdx
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
---

# Get started with Vibe Code Web

Vibe Code Web is the **control plane for remote coding agents**. Start a coding task from the web, supervise the agent as it works, and review the branch or pull request it produces.

Same engine under the hood as the [Vibe CLI](https://docs.mistral.ai/vibe/code/cli/install-setup), but running in a **managed cloud sandbox** you reach **from any browser**.

> **Info**
>
> Vibe Code Web is rolling out progressively across all plans. See [Limits and lifecycle](https://docs.mistral.ai/vibe/code/vibe-code-web/limits-and-lifecycle) for quotas, model behavior, and session limits.

## What you can do {#what-you-can-do}

With Vibe Code Web you can:

- Create projects from one or more GitHub repositories under the same GitHub owner.
- Start remote coding sessions from the web.
- Send a prompt to a cloud session from the Vibe CLI, or teleport an active CLI session to the web.
- Run agents in managed cloud sandboxes.
- Produce GitHub branches and pull requests.
- Review final code in GitHub.

It fits tasks that:

- Run remotely without local files, services, or secrets.
- Take long enough that you don't want to keep your machine open.
- End with a branch or pull request for review.

> **Tip**
>
> Prefer the [CLI](https://docs.mistral.ai/vibe/code/cli/install-setup) or [VS Code extension](https://docs.mistral.ai/vibe/code/vs-code-extension/install-authenticate) when the task depends on local files, local secrets, unsupported runtimes, or direct access to your machine.

## Core concepts {#core-concepts}

Vibe Code Web organizes work around three entities: **projects**, **repositories**, and **sessions**. A project pins one or more GitHub repositories from the same owner, and each session is one run of the agent against that project.

**Project**

A **project** is a scoped workspace, listed in the Vibe Code Web sidebar. It includes one or more GitHub repositories from the same GitHub owner (user or organization). Sessions you run from the project share that repository scope.

At launch, project setup is limited to selecting one or more repositories from the same GitHub owner and giving the project a name.

See [Projects](https://docs.mistral.ai/vibe/code/vibe-code-web/projects) for creation, edits, deletion, and session management.

**Repository**

A **repository** is a GitHub repository the agent clones into the sandbox, reads, edits, commits to, and opens pull requests against. A project can include one or more repositories, but they must all belong to the **same GitHub owner**. To work across owners, create separate projects.

See [GitHub repositories and permissions](https://docs.mistral.ai/vibe/code/vibe-code-web/github-repositories-permissions) for the App install, token model, attribution, and access management.

**Session**

A **session** is one run of the agent against a project. It follows the same flow:

1. **Spawn.** Create a session from the web, or send one from the CLI. Provide a focused prompt.
2. **Run.** The agent works remotely in an isolated sandbox: clone, plan, edit, run commands and tests.
3. **Follow.** Inspect commands and file changes as the agent works.
4. **Review.** Open the resulting branch or pull request in GitHub for code review, comments, required checks, and merge decisions.

Past sessions can be inspected, but once the sandbox is deprovisioned, a session cannot be resumed.

See [Sessions](https://docs.mistral.ai/vibe/code/vibe-code-web/sessions) for the full runbook and [Limits and lifecycle](https://docs.mistral.ai/vibe/code/vibe-code-web/limits-and-lifecycle) for states and timeouts.

## Quickstart {#quickstart}

You can start a Vibe Code Web session from the web or from the Vibe CLI.

**Web**

1. Open Vibe Code Web from the **Code** tab in Vibe.
2. Create a project and connect one or more GitHub repositories from the same owner. See [Projects](https://docs.mistral.ai/vibe/code/vibe-code-web/projects).
3. Click **New session** and enter a focused prompt. Name the file, failing test, stack trace, or expected behavior when you can.
4. Watch the agent clone the repository, inspect the code, and run commands.
5. Open the resulting branch or pull request in GitHub for review and merge.

> **Tip**
>
> Start with a small, well-scoped task. Mention the file, function, or failing test when you know it.

**CLI**

From the [Vibe CLI](https://docs.mistral.ai/vibe/code/cli/install-setup), prefix a prompt with `&` to send the task to a cloud session instead of running it locally:

```bash
vibe
& fix the failing auth tests
```

The CLI returns a web URL where you can follow the session. The task runs in the cloud, not on your laptop.

Requirements:

- Vibe CLI installed (upgrade with `uv tool upgrade mistral-vibe`).
- A Mistral account with access to Vibe Code Web.
- The [Mistral GitHub App](https://github.com/apps/mistralai/installations/new) installed on the target repository.

> **Tip**
>
> Already in a local CLI session? Run `/teleport` inside the session to move it to the cloud, with history and branch state preserved. See [Teleport from CLI to web](https://docs.mistral.ai/vibe/code/cli/teleport-cli-web).

## Next steps {#next}

- [Projects](https://docs.mistral.ai/vibe/code/vibe-code-web/projects) — Create, manage, and delete projects. Add repositories and manage session history.

- [Sessions](https://docs.mistral.ai/vibe/code/vibe-code-web/sessions) — Lifecycle, agent loop, branch and PR output.

- [GitHub repositories and permissions](https://docs.mistral.ai/vibe/code/vibe-code-web/github-repositories-permissions) — Connect GitHub, grant repository access, and review authorship and scopes.

- [Sandbox environment](https://docs.mistral.ai/vibe/code/vibe-code-web/sandbox-environment) — Cloud image, available tools, and what you can configure today.

- [Security](https://docs.mistral.ai/vibe/code/vibe-code-web/security) — Prompt-injection risk and data handling.

- [Limits and lifecycle](https://docs.mistral.ai/vibe/code/vibe-code-web/limits-and-lifecycle) — Session lifecycle, sandbox behavior, and what persists.
