# mined2-043 (single_page, 4 connector calls)

## Question

My skills are not loading even though the files look right — where does the CLI look for them and how do the enable and disable lists interact?

## Thinking

The user is asking about CLI behavior regarding skills: where it looks for them and how enable/disable lists interact. This is a specific technical question about Mistral's CLI configuration. I need to search the documentation for information about skill loading, file locations, and enable/disable list interactions.

Let me start by searching for documentation about the CLI and skills configuration.

The search returned several relevant hits. Let me examine the most relevant ones:

1. Hit [1] from `https://docs.mistral.ai/vibe/code/cli/skills#filtering` - This seems to directly address the enable/disable lists interaction
2. Hit [2] from `https://docs.mistral.ai/vibe/code/cli/configuration#skills` - This also mentions skill_paths, enabled_skills, and disabled_skills
3. Hit [4] from `https://docs.mistral.ai/vibe/code/cli/skills#locations` - This should tell us where the CLI looks for skills

I need to read these pages to get the complete information. Let me start with the skills page since it has multiple relevant sections.

Good, I have the skills page. Now let me also read the configuration page to get the complete picture about how enabled_skills and disabled_skills interact.

Perfect! Now I have all the information I need. Let me also check the trusted folders information since it was mentioned in the search results and might be relevant for project-level skills loading.

Now I have all the necessary information. Let me synthesize this into a clear, actionable answer for the user.

The user's question has two parts:
1. Where does the CLI look for skills?
2. How do the enable and disable lists interact?

From the documentation:
- **Locations**: The CLI discovers skills from:
  1. Custom paths in `config.toml` → `skill_paths = ["/path/to/custom/skills"]`
  2. Project-level: `./.vibe/skills/` or `./.agents/skills/` (when working directory is trusted)
  3. User-level: `~/.vibe/skills/`

- **Filtering interaction**:
  - If `enabled_skills` is set and non-empty, it acts as an allow-list: only skills matching patterns in this list are available
  - If `enabled_skills` is empty or not set, all discovered skills are available EXCEPT those matching patterns in `disabled_skills`
  - Both lists support exact names, glob patterns, and regex with `re:` prefix

I should also mention the trust folder requirement for project-level skills since that could be why skills aren't loading.

Let me structure the answer clearly with the locations first, then the interaction logic, and finally some troubleshooting tips.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "CLI skills loading enable disable lists path", "max_hits": 10}
```

Result:

```
q: "CLI skills loading enable disable lists path"

[1] https://docs.mistral.ai/vibe/code/cli/skills | section: filtering
    Skills > Enable, disable, or filter skills
    Use patterns to control which skills load: ```toml enabled_skills = ["code-review", "test-*"] disabled_skills = ["experimental-*"] ``` Skill filters support **exact names**, **glob patterns**, and **regex** with the `re:` prefix, just like tool filters. If `enabled_skills` is non-empty, it acts as an allow-list; otherwise every discovered skill is available minus those matched by `disabled_skills` …
    cite: https://docs.mistral.ai/vibe/code/cli/skills#filtering

[2] https://docs.mistral.ai/vibe/code/cli/configuration | section: skills
    Configuration > Common configuration sections > Skills
    Enable, disable, or add skill paths: ```toml skill_paths = ["/path/to/custom/skills"] enabled_skills = ["code-review", "test-*"] disabled_skills = ["experimental-*"] ``` `enabled_skills` and `disabled_skills` interact as follows: - If `enabled_skills` is **set and non-empty**, only skills whose name matches a pattern in that list are available. - Otherwise, every discovered skill is available, min …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#skills

[3] https://docs.mistral.ai/vibe/code/safety-approvals-permissions | section: enable-disable-tools
    Safety, approvals, and permissions > Per-tool permissions > Enable or disable tools
    Toggle tools globally using exact names, globs, or regex patterns: ```toml # Only allow read-only and search tools enabled_tools = ["read_file", "grep", "task"] # Or disable a specific class of tools disabled_tools = ["bash"] ```
    cite: https://docs.mistral.ai/vibe/code/safety-approvals-permissions#enable-disable-tools

[4] https://docs.mistral.ai/vibe/code/cli/skills | section: locations
    Skills > Skill locations
    The CLI discovers skills from several locations, in order: 1. **Custom paths** defined in `config.toml` → `skill_paths = ["/path/to/custom/skills"]` 2. **Project-level** skills in `./.vibe/skills/` or `./.agents/skills/` when the working directory is [trusted](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#trusted-folders). 3. **User-level** skills in `~/.vibe/skills/`.
    cite: https://docs.mistral.ai/vibe/code/cli/skills#locations

[5] https://docs.mistral.ai/vibe/code/cli/skills | section: stay-in-control
    Skills > Stay in control
    - **Review a skill before enabling it** if it can call write-capable tools. - Prefer **narrow `allowed-tools` lists** over disabling tools elsewhere. - Keep project-specific skills in `./.vibe/skills/` so collaborators can review them in code review.
    cite: https://docs.mistral.ai/vibe/code/cli/skills#stay-in-control

[6] https://docs.mistral.ai/vibe/code/cli/work-with-cli | section: trust-folders
    Work with the CLI > Trust folders
    The CLI checks whether the current working directory is trusted before loading project-level configuration, skills, or agent files. The first time you run the CLI in **interactive mode** from a new directory that contains trustable files, it asks you to confirm the folder. Trust enforcement applies in **both** interactive and programmatic modes, but the confirmation prompt only appears interactive …
    cite: https://docs.mistral.ai/vibe/code/cli/work-with-cli#trust-folders

[7] https://docs.mistral.ai/studio/search/search-toolkit/ingestion/loaders | section: batch-loading
    File loaders > Batch loading
    Load multiple files with concurrency control: ```python import asyncio from mistralai.search.toolkit.ingestion.loaders import FileLoader from mistralai.search.toolkit.plugins.storage.s3 import S3FileLoader async def load_files_batch( loader: FileLoader, paths: list[str], max_concurrent: int = 10, ) -> list: """Load multiple files concurrently with semaphore.""" semaphore = asyncio.Semaphore(max_co …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/ingestion/loaders#batch-loading

[8] https://docs.mistral.ai/vibe/code/cli/skills | section: slash-commands
    Skills > Custom slash commands
    Skills are the recommended way to add your own slash commands. Set `user-invocable: true` in the frontmatter and the skill name becomes available with `/skill-name` autocompletion in the CLI prompt, and in the [VS Code extension](https://docs.mistral.ai/vibe/code/vs-code-extension/commands-slash-commands#slash-commands) slash picker too. Pair custom skills with `allowed-tools` to keep their access …
    cite: https://docs.mistral.ai/vibe/code/cli/skills#slash-commands

[9] https://docs.mistral.ai/vibe/code/cli/configuration-reference | section: top-level
    Configuration reference > Top-level keys
    | Key | Type | Default | Description | |---|---|---|---| | `default_agent` | string | | Default interactive agent, for example `"plan"`. Ignored in programmatic mode, which falls back to `auto-approve`. See [Agents](https://docs.mistral.ai/vibe/code/cli/agents) | | `active_model` | string | | Model alias currently in use. Set to a `[[models]]` `alias` or a built-in model ID | | `log_interactions` …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration-reference#top-level

[10] https://docs.mistral.ai/vibe/code/cli/offline-models | section: run-offline
    Using offline models > Run fully offline
    If you chose offline models for privacy reasons, you may also want to **disable telemetry and any background network calls**. Set the following in `~/.vibe/config.toml`: ```toml enable_telemetry = false enable_auto_update = false ``` With these settings and a local provider configured above, the CLI does not contact `mistral.ai` or any other external service. Skills, MCP servers, and connectors th …
    cite: https://docs.mistral.ai/vibe/code/cli/offline-models#run-offline

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/skills") to read hit 1 on its page
```

### 2. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/skills"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/cli/skills | "Skills"

## section: skills
    Skills
    cite: https://docs.mistral.ai/vibe/code/cli/skills
# Skills

Skills are **reusable instruction sets** that extend Vibe Code with new workflows, custom slash commands, and scoped tool sets. Vibe follows the [Agent Skills specification](https://agentskills.io/specification), so skills you write here are portable to other agents that adopt the same spec.

## section: skill-format
    Skills > Skill format
    cite: https://docs.mistral.ai/vibe/code/cli/skills#skill-format
## Skill format {#skill-format}

A skill is a **directory containing a `SKILL.md` file**. The file starts with YAML frontmatter and continues with the skill instructions in Markdown.

```markdown
---
name: code-review
description: Perform automated code reviews.
license: MIT
compatibility: Python 3.12+
user-invocable: true
allowed-tools:
  - read_file
  - grep
  - ask_user_question
---

# Code review skill

This skill helps analyze code quality and suggest improvements.
```

Common frontmatter fields:

- **`name`**: used to invoke the skill.
- **`description`**: shown in the skill list.
- **`user-invocable`**: when `true`, exposes the skill as a slash command in the CLI and the VS Code extension.
- **`allowed-tools`**: restricts which tools the skill can call.

## section: locations
    Skills > Skill locations
    cite: https://docs.mistral.ai/vibe/code/cli/skills#locations
## Skill locations {#locations}

The CLI discovers skills from several locations, in order:

1. **Custom paths** defined in `config.toml` → `skill_paths = ["/path/to/custom/skills"]`
2. **Project-level** skills in `./.vibe/skills/` or `./.agents/skills/` when the working directory is [trusted](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#trusted-folders).
3. **User-level** skills in `~/.vibe/skills/`.

## section: filtering
    Skills > Enable, disable, or filter skills
    cite: https://docs.mistral.ai/vibe/code/cli/skills#filtering
## Enable, disable, or filter skills {#filtering}

Use patterns to control which skills load:

```toml
enabled_skills = ["code-review", "test-*"]
disabled_skills = ["experimental-*"]
```

Skill filters support **exact names**, **glob patterns**, and **regex** with the `re:` prefix, just like tool filters. If `enabled_skills` is non-empty, it acts as an allow-list; otherwise every discovered skill is available minus those matched by `disabled_skills`.

## section: slash-commands
    Skills > Custom slash commands
    cite: https://docs.mistral.ai/vibe/code/cli/skills#slash-commands
## Custom slash commands {#slash-commands}

Skills are the recommended way to add your own slash commands. Set `user-invocable: true` in the frontmatter and the skill name becomes available with `/skill-name` autocompletion in the CLI prompt, and in the [VS Code extension](https://docs.mistral.ai/vibe/code/vs-code-extension/commands-slash-commands#slash-commands) slash picker too.

Pair custom skills with `allowed-tools` to keep their access scoped to what the workflow needs.

## section: stay-in-control
    Skills > Stay in control
    cite: https://docs.mistral.ai/vibe/code/cli/skills#stay-in-control
## Stay in control {#stay-in-control}

- **Review a skill before enabling it** if it can call write-capable tools.
- Prefer **narrow `allowed-tools` lists** over disabling tools elsewhere.
- Keep project-specific skills in `./.vibe/skills/` so collaborators can review them in code review.

Results: 6 sections, the whole page.
```

### 3. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/configuration", "section": "skills"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/cli/configuration | "Configuration" | section: skills

## section: skills
    Configuration > Common configuration sections > Skills
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#skills
### Skills {#skills}

Enable, disable, or add skill paths:

```toml
skill_paths = ["/path/to/custom/skills"]
enabled_skills = ["code-review", "test-*"]
disabled_skills = ["experimental-*"]
```

`enabled_skills` and `disabled_skills` interact as follows:

- If `enabled_skills` is **set and non-empty**, only skills whose name matches a pattern in that list are available.
- Otherwise, every discovered skill is available, minus any skill whose name matches a pattern in `disabled_skills`.

See [Skills](https://docs.mistral.ai/vibe/code/cli/skills).

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/configuration", section="tool-permissions") for the section after it
```

### 4. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/work-with-cli", "section": "trust-folders"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/cli/work-with-cli | "Work with the CLI" | section: trust-folders

## section: trust-folders
    Work with the CLI > Trust folders
    cite: https://docs.mistral.ai/vibe/code/cli/work-with-cli#trust-folders
## Trust folders {#trust-folders}

The CLI checks whether the current working directory is trusted before loading project-level configuration, skills, or agent files. The first time you run the CLI in **interactive mode** from a new directory that contains trustable files, it asks you to confirm the folder.

Trust enforcement applies in **both** interactive and programmatic modes, but the confirmation prompt only appears interactively. In programmatic mode, use `vibe --trust` to grant temporary trust for the current invocation only.

Trusted folders are remembered in `~/.vibe/trusted_folders.toml`.

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/work-with-cli", section="resume") for the section after it
```

## Answer

The CLI looks for skills in these locations, in order:

1. **Custom paths** you add in `config.toml` → `skill_paths = ["/path/to/custom/skills"]`
2. **Project-level** folders `./.vibe/skills/` or `./.agents/skills/` — but **only if the current working directory is trusted**
3. **User-level** folder `~/.vibe/skills/`
   *[Skill locations](https://docs.mistral.ai/vibe/code/cli/skills#locations)*

---

**How `enabled_skills` and `disabled_skills` interact:**

- If `enabled_skills` is **set and non-empty**, it acts as an **allow-list**: only skills whose name matches a pattern in that list will load.
- If `enabled_skills` is **empty or not set**, **all discovered skills load** except those whose name matches any pattern in `disabled_skills`.
- Both lists support exact names, glob patterns (e.g., `test-*`), and regex with the `re:` prefix.

Example:
```toml
enabled_skills = ["code-review", "test-*"]   # only these load
disabled_skills = ["experimental-*"]         # ignored if enabled_skills is non-empty
```
*[Skills > Enable, disable, or filter skills](https://docs.mistral.ai/vibe/code/cli/skills#filtering)*
*[Configuration > Skills](https://docs.mistral.ai/vibe/code/cli/configuration#skills)*

---

**If your skills still don’t load:**
- Make sure the working directory is **trusted** (the CLI prompts for this in interactive mode; in programmatic mode, use `vibe --trust`).
  *[Work with the CLI > Trust folders](https://docs.mistral.ai/vibe/code/cli/work-with-cli#trust-folders)*

