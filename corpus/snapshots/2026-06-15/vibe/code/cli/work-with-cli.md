---
url: https://docs.mistral.ai/vibe/code/cli/work-with-cli
title: Work with the CLI
breadcrumbs: [Vibe, Code, CLI]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/code/cli/work-with-cli/page.mdx
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
---

# Work with the CLI

Once the CLI is installed and your API key is set, you're ready for day-to-day work. The CLI runs in **two modes**: *interactive* for chat and exploration, and *programmatic* for scripting and CI.

## Start the CLI in your project {#start}

Navigate to your project root and run:

```bash
vibe
```

You can also start with an initial prompt:

```bash
vibe "Refactor the main function in cli/main.py to be more modular."
```

The CLI launches a terminal chat interface. From there, you can iterate on coding tasks, reference files, run shell commands, and switch agents without leaving the terminal.

## Interactive mode {#interactive-mode}

Interactive mode is the default. Use it for exploration, multi-step tasks, and any work that benefits from review and follow-up.

### Reference files with `@` {#reference-files}

Prefix a path with `@` to attach a file to your prompt. The CLI provides autocompletion as you type:

```text
> Read the file @src/agent.py and suggest improvements.
```

### Run built-in commands with `/` {#builtin-commands}

Type `/` to open the slash-command picker with autocompletion. Use it for built-in commands like `/help`, `/model`, `/config`, or any command exposed by an installed skill. See [Commands and shortcuts](https://docs.mistral.ai/vibe/code/cli/commands-shortcuts) for the full list.

```text
> /model
```

### Run shell commands with `!` {#shell-commands}

Prefix a command with `!` to run it directly in your shell, bypassing the agent:

```text
> !ls -l
```

### Send a prompt to a cloud session with `&` {#cloud-session}

Prefix a prompt with `&` to run it in a Vibe Code Web sandbox. The CLI returns a link to the cloud session.

```text
> & fix the failing tests
```

See [Teleport from CLI to web](https://docs.mistral.ai/vibe/code/cli/teleport-cli-web) for prerequisites and limits.

### Useful in-session shortcuts {#in-session-shortcuts}

| Shortcut | Action |
|---|---|
| `Shift+Tab` | Cycle through agents (default, plan, accept-edits, auto-approve). |
| `Ctrl+O` | Toggle the tool output view. |
| `Ctrl+G` | Edit the current input in an external editor. |
| `Escape` | Interrupt the current operation. |

See [Commands and shortcuts](https://docs.mistral.ai/vibe/code/cli/commands-shortcuts) for the full list of slash commands and shortcuts.

## Programmatic mode {#programmatic-mode}

Programmatic mode is built for **scripting, CI jobs, and any non-interactive use**. Use the `--prompt` flag to run a single task and exit:

```bash
vibe --prompt "Analyze the codebase" --max-turns 5 --output json
```

Programmatic mode does not start the chat interface and disables interactive tools such as the question prompt. By default, it runs with the `auto-approve` agent.

Useful options:

- `--max-turns N` caps the number of assistant turns. **Recommended** to bound run length.
- `--enabled-tools TOOL` restricts which tools the agent can use. Supports exact names, glob patterns (`bash*`), and regex with the `re:` prefix (`re:^serena_.*$`).
- `--output text|json|streaming` sets the output format.

> **Warning**
>
> The CLI also exposes a `--max-price DOLLARS` flag, but the underlying price values come from the config file and can be missing or outdated. Treat the reported cost as **indicative only**: do not rely on it for hard budget enforcement.

## Choose how the CLI handles approval {#approval}

The CLI ships with several built-in agents. Pick one with `--agent`:

```bash
vibe --agent plan
vibe --agent accept-edits
vibe --agent auto-approve
```

Switch agents mid-session (interactive mode only) with `Shift+Tab`. Set a default interactive agent in `config.toml`:

```toml
default_agent = "plan"
```

See [Agents](https://docs.mistral.ai/vibe/code/cli/agents) for the full list and behavior.

## Review changes before they apply {#review-changes}

For tasks with substantial file edits or shell commands, the CLI:

1. Shows a **preview** of the change or command before running it.
2. **Asks for confirmation**, unless the active agent auto-approves.
3. **Displays the result** after each step.

> **Tip**
>
> Use the `plan` agent when you want a read-only walkthrough before any change is proposed. See [Agents](https://docs.mistral.ai/vibe/code/cli/agents).

## Trust folders {#trust-folders}

The CLI checks whether the current working directory is trusted before loading project-level configuration, skills, or agent files. The first time you run the CLI in **interactive mode** from a new directory that contains trustable files, it asks you to confirm the folder.

Trust enforcement applies in **both** interactive and programmatic modes, but the confirmation prompt only appears interactively. In programmatic mode, use `vibe --trust` to grant temporary trust for the current invocation only.

Trusted folders are remembered in `~/.vibe/trusted_folders.toml`.

## Continue or resume sessions {#resume}

The CLI can pick up where you left off:

- `vibe --continue` (or `-c`) resumes the most recent session.
- `vibe --resume SESSION_ID` resumes a specific session. Partial IDs are supported.
- `/resume` (or `/continue`) inside a session opens a browser of past sessions.

Session continuation requires logging, which is enabled by default. If resume stops working after editing your configuration, make sure logging is still enabled in `~/.vibe/config.toml`:

```toml
log_interactions = true
```
