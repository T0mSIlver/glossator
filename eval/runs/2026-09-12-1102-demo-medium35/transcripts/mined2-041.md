# mined2-041 (single_page, 2 connector calls)

## Question

How many `AGENTS.md` files does the Vibe CLI load, and from where?

## Thinking

The user is asking about how many `AGENTS.md` files the Vibe CLI loads and their locations. I need to search the Mistral documentation for information about Vibe CLI and AGENTS.md files. Let me start by searching for relevant documentation.

The search returned a relevant result. The first hit from `https://docs.mistral.ai/vibe/code/cli/agents` with section `agents-md` seems to directly answer the question. It mentions "The CLI loads up to **two `AGENTS.md` files**" and describes their locations: user-level and project-level. Let me read the full page to get the complete details.

The user asks: "How many `AGENTS.md` files does the Vibe CLI load, and from where?"

From the documentation I just read, I can see:

1. The CLI loads **up to two `AGENTS.md` files**
2. The locations are:
   - User-level: `~/.vibe/AGENTS.md` (or in `$VIBE_HOME` if set)
   - Project-level: starting from the current working directory and walking up parent directories (but only inside trusted folders), the first `AGENTS.md` found is loaded

The answer is clear and directly from the documentation. I should format it properly with the exact information and include the citation link.

The answer should be:
- Number: up to two
- Locations: 
  1. User-level: `~/.vibe/AGENTS.md` (or `$VIBE_HOME/AGENTS.md`)
  2. Project-level: first `AGENTS.md` found when walking up from current working directory (only inside trusted folders)

I need to include the citation as a markdown link. The citation from the tool was: `cite: https://docs.mistral.ai/vibe/code/cli/agents#agents-md`

Let me format this as a clear, direct answer.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "Vibe CLI loads AGENTS.md files number and location"}
```

Result:

```
q: "Vibe CLI loads AGENTS.md files number and location"

[1] https://docs.mistral.ai/vibe/code/cli/agents | section: agents-md
    Agents > AGENTS.md support
    The CLI loads up to **two `AGENTS.md` files** into context to follow project-specific agent instructions: 1. **User-level**: `~/.vibe/AGENTS.md` (or in `$VIBE_HOME` if you set it). 2. **Project-level**: starting from the current working directory and walking up parent directories (but only inside [trusted folders](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#trusted-folders)), th …
    cite: https://docs.mistral.ai/vibe/code/cli/agents#agents-md

[2] https://docs.mistral.ai/vibe/code/cli/agents | section: custom-agents
    Agents > Custom agents
    Create custom agents in `~/.vibe/agents/` (user-level) or `./.vibe/agents/` (project-level) by adding a `.toml` file. Every agent must declare its kind via `agent_type`: - `agent_type = "agent"`: **user-facing**. Selectable via `vibe --agent <name>` or `Shift+Tab`. - `agent_type = "subagent"`: **delegation-only**. Spawned by the model through the `task` tool. Not selectable by the user. Run a cust …
    cite: https://docs.mistral.ai/vibe/code/cli/agents#custom-agents

[3] https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli | section: verify
    Install the Vibe CLI and send your first prompt > Verify
    You've completed the setup if: 1. `vibe --version` returns a version number. 2. You're signed in (or your API key is registered). 3. The CLI responds to prompts with context-aware answers.
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli#verify

[4] https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli | section: step-3
    Install the Vibe CLI and send your first prompt > Step 3: Send your first prompt
    Type a request directly in the prompt. For example: > List the files in this directory and explain what each one does. The CLI reads your project context and responds with relevant information. It can also generate code, edit files, and run shell commands when you approve. ![Sending a query to the Vibe CLI](https://docs.mistral.ai/assets/quickstarts/vibe/query.png) To run a shell command directly …
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli#step-3

[5] https://docs.mistral.ai/vibe/code/cli/api-keys-profiles | section: env-file
    API keys and profiles > Give the API key to the CLI > 3. `.env` file
    You can also edit `~/.vibe/.env` directly: ```bash MISTRAL_API_KEY=your_mistral_api_key ``` The CLI loads `~/.vibe/.env` automatically on startup. > **Note** > > The `.env` file is for **credentials only**. General CLI configuration belongs in `config.toml`. See [Configuration](https://docs.mistral.ai/vibe/code/cli/configuration).
    cite: https://docs.mistral.ai/vibe/code/cli/api-keys-profiles#env-file

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

1. **User-level**: `~/.vibe/AGENTS.md` (or `$VIBE_HOME/AGENTS.md` if `$VIBE_HOME` is set)
2. **Project-level**: the first `AGENTS.md` found by walking up from the current working directory, but only if it is inside a [trusted folder](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#trusted-folders)

[AGENTS.md support](https://docs.mistral.ai/vibe/code/cli/agents#agents-md)

