# mined2-041 (single_page, 2 connector calls)

## Question

How many `AGENTS.md` files does the Vibe CLI load, and from where?

## Thinking

The user is asking about the Vibe CLI and specifically how many `AGENTS.md` files it loads and from where. I need to search the Mistral documentation for information about the Vibe CLI and its handling of `AGENTS.md` files. I'll use the mistral_docs_search tool with a query that captures this specific question.

The search returned a relevant result. The first hit is from the Vibe CLI documentation about AGENTS.md support. It mentions that the CLI loads up to two AGENTS.md files: one user-level and one project-level. I should read the full page to get the complete and accurate information about the locations and the loading behavior.

I have now read the relevant section from the Mistral documentation. The information is clear: the Vibe CLI loads **up to two** `AGENTS.md` files. The locations are:
1. User-level: `~/.vibe/AGENTS.md` (or in `$VIBE_HOME` if set)
2. Project-level: The first `AGENTS.md` found by walking up from the current working directory, but only within trusted folders.

I need to present this information clearly and concisely to the user, and include the citation to the documentation as required.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "Vibe CLI AGENTS.md files loaded and their locations"}
```

Result:

```
q: "Vibe CLI AGENTS.md files loaded and their locations"

[1] https://docs.mistral.ai/vibe/code/cli/agents | section: agents-md
    Agents > AGENTS.md support
    The CLI loads up to **two `AGENTS.md` files** into context to follow project-specific agent instructions: 1. **User-level**: `~/.vibe/AGENTS.md` (or in `$VIBE_HOME` if you set it). 2. **Project-level**: starting from the current working directory and walking up parent directories (but only inside [trusted folders](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#trusted-folders)), th …
    cite: https://docs.mistral.ai/vibe/code/cli/agents#agents-md

[2] https://docs.mistral.ai/vibe/code/cli/hooks | section: file-locations
    Hooks > Configuration file locations
    Hooks are declared in `hooks.toml`. The CLI looks in this order: 1. `./.vibe/hooks.toml` in the working directory (**project-level**, loaded first, **trusted folders only**). 2. `~/.vibe/hooks.toml` in your home directory (**user-level**, loaded second). When the same `name` appears in both files, the **project entry wins**. Project-level hooks load only when the working directory is [trusted](htt …
    cite: https://docs.mistral.ai/vibe/code/cli/hooks#file-locations

[3] https://docs.mistral.ai/vibe/code/cli/configuration | section: file-locations
    Configuration > Configuration file locations
    The CLI looks for `config.toml` in this order: 1. `./.vibe/config.toml` in the current working directory (**project-level**). 2. `~/.vibe/config.toml` in your home directory (**user-level**). Project-level configuration takes precedence over user-level configuration. Project configuration is loaded only when the working directory is [trusted](https://docs.mistral.ai/vibe/code/safety-approvals-perm …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#file-locations

[4] https://docs.mistral.ai/vibe/code/cli/skills | section: locations
    Skills > Skill locations
    The CLI discovers skills from several locations, in order: 1. **Custom paths** defined in `config.toml` → `skill_paths = ["/path/to/custom/skills"]` 2. **Project-level** skills in `./.vibe/skills/` or `./.agents/skills/` when the working directory is [trusted](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#trusted-folders). 3. **User-level** skills in `~/.vibe/skills/`.
    cite: https://docs.mistral.ai/vibe/code/cli/skills#locations

[5] https://docs.mistral.ai/vibe/code/cli/agents | section: custom-agents
    Agents > Custom agents
    Create custom agents in `~/.vibe/agents/` (user-level) or `./.vibe/agents/` (project-level) by adding a `.toml` file. Every agent must declare its kind via `agent_type`: - `agent_type = "agent"`: **user-facing**. Selectable via `vibe --agent <name>` or `Shift+Tab`. - `agent_type = "subagent"`: **delegation-only**. Spawned by the model through the `task` tool. Not selectable by the user. Run a cust …
    cite: https://docs.mistral.ai/vibe/code/cli/agents#custom-agents

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
2. **Project-level**: The first `AGENTS.md` found by walking up from the current working directory, but only within [trusted folders](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#trusted-folders).

[AGENTS.md support](https://docs.mistral.ai/vibe/code/cli/agents#agents-md)

