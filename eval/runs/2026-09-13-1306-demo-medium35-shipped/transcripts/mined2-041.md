# mined2-041 (single_page, 2 connector calls)

## Question

How many `AGENTS.md` files does the Vibe CLI load, and from where?

## Thinking

The user asks about how many `AGENTS.md` files the Vibe CLI loads and from where. This is a specific question about the Vibe CLI's configuration loading behavior. I need to search the Mistral documentation for information about Vibe CLI and AGENTS.md files.

I'll start with a search query that combines the key terms: "Vibe CLI", "AGENTS.md", and "load". This should help me find the relevant documentation section.

The search returned a relevant result: section "agents-md" from the page https://docs.mistral.ai/vibe/code/cli/agents. The snippet indicates that the CLI loads up to two AGENTS.md files: one user-level and one project-level. This looks exactly like what the user is asking for.

To get the complete and accurate information, I should read the full page to confirm the details and ensure I have the complete context.

The documentation page confirms the details. The Vibe CLI loads up to two AGENTS.md files:
1. User-level: `~/.vibe/AGENTS.md` (or `$VIBE_HOME/AGENTS.md` if set)
2. Project-level: The first AGENTS.md found by walking up from the current working directory, but only within trusted folders

This directly answers the user's question. I need to format this clearly, mentioning both the number (up to two) and the locations. I should also include the citation link as shown in the documentation snippet.

The answer should be concise but complete, mentioning both files and their locations.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "Vibe CLI AGENTS.md files load", "max_hits": 5}
```

Result:

```
q: "Vibe CLI AGENTS.md files load"

[1] https://docs.mistral.ai/vibe/code/cli/agents | section: agents-md
    Agents > AGENTS.md support
    The CLI loads up to **two `AGENTS.md` files** into context to follow project-specific agent instructions: 1. **User-level**: `~/.vibe/AGENTS.md` (or in `$VIBE_HOME` if you set it). 2. **Project-level**: starting from the current working directory and walking up parent directories (but only inside [trusted folders](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#trusted-folders)), th …
    cite: https://docs.mistral.ai/vibe/code/cli/agents#agents-md

[2] https://docs.mistral.ai/vibe/code/cli/agents | section: custom-agents
    Agents > Custom agents
    Create custom agents in `~/.vibe/agents/` (user-level) or `./.vibe/agents/` (project-level) by adding a `.toml` file. Every agent must declare its kind via `agent_type`: - `agent_type = "agent"`: **user-facing**. Selectable via `vibe --agent <name>` or `Shift+Tab`. - `agent_type = "subagent"`: **delegation-only**. Spawned by the model through the `task` tool. Not selectable by the user. Run a cust …
    cite: https://docs.mistral.ai/vibe/code/cli/agents#custom-agents

[3] https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli | section: step-3
    Install the Vibe CLI and send your first prompt > Step 3: Send your first prompt
    Type a request directly in the prompt. For example: > List the files in this directory and explain what each one does. The CLI reads your project context and responds with relevant information. It can also generate code, edit files, and run shell commands when you approve. ![Sending a query to the Vibe CLI](https://docs.mistral.ai/assets/quickstarts/vibe/query.png) To run a shell command directly …
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli#step-3

[4] https://docs.mistral.ai/vibe/code/cli/work-with-cli | section: start
    Work with the CLI > Start the CLI in your project
    Navigate to your project root and run: ```bash vibe ``` You can also start with an initial prompt: ```bash vibe "Refactor the main function in cli/main.py to be more modular." ``` The CLI launches a terminal chat interface. From there, you can iterate on coding tasks, reference files, run shell commands, and switch agents without leaving the terminal.
    cite: https://docs.mistral.ai/vibe/code/cli/work-with-cli#start

[5] https://docs.mistral.ai/vibe/code/cli/work-with-cli | section: trust-folders
    Work with the CLI > Trust folders
    The CLI checks whether the current working directory is trusted before loading project-level configuration, skills, or agent files. The first time you run the CLI in **interactive mode** from a new directory that contains trustable files, it asks you to confirm the folder. Trust enforcement applies in **both** interactive and programmatic modes, but the confirmation prompt only appears interactive …
    cite: https://docs.mistral.ai/vibe/code/cli/work-with-cli#trust-folders

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/agents") to read hit 1 on its page
```

### 2. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/agents", "section": "agents-md"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/cli/agents | "Agents" | section: agents-md

## section: agents-md
    Agents > AGENTS.md support
    cite: https://docs.mistral.ai/vibe/code/cli/agents#agents-md
## AGENTS.md support {#agents-md}

The CLI loads up to **two `AGENTS.md` files** into context to follow project-specific agent instructions:

1. **User-level**: `~/.vibe/AGENTS.md` (or in `$VIBE_HOME` if you set it).
2. **Project-level**: starting from the current working directory and walking up parent directories (but only inside [trusted folders](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#trusted-folders)), the first `AGENTS.md` found is loaded.

For example:

```text
/
  dir_1/
    AGENTS.md      <- never loaded: location is not trusted
    dir_2/         <- trusted
      AGENTS.md
      dir_3/
        AGENTS.md  <- loaded
        project/   <- cwd (no AGENTS.md here)
```

Additionally, the CLI will auto-discover new `AGENTS.md` files when reading files in sub-directories.

Results: the whole section.
```

## Answer

The Vibe CLI loads **up to two `AGENTS.md` files**:

1. **User-level**: `~/.vibe/AGENTS.md` (or in `$VIBE_HOME` if set).
2. **Project-level**: The first `AGENTS.md` found by walking up from the current working directory, but **only inside [trusted folders](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#trusted-folders)**.

[AGENTS.md support](https://docs.mistral.ai/vibe/code/cli/agents#agents-md)

