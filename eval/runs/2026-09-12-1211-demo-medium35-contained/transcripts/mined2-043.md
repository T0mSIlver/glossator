# mined2-043 (single_page, 3 connector calls)

## Question

My skills are not loading even though the files look right — where does the CLI look for them and how do the enable and disable lists interact?

## Thinking

The user is asking about CLI behavior related to skills: where it looks for skill files, and how the enable/disable lists interact. This is a specific technical question about Mistral's CLI configuration. I need to search the documentation for information about:
1. Where the CLI looks for skills files (file paths, directories)
2. How the enable and disable lists work together
3. The interaction between these configuration options

I should use the mistral_docs_search tool to find relevant sections in the documentation. The query should be specific to CLI, skills, and configuration.

The search returned several relevant hits. Hit 1 and 3 seem most directly relevant to the user's question. Hit 1 is about filtering skills with enable/disable lists, and hit 3 is about the skills configuration section. Hit 5 is about skill locations, which also seems very relevant.

I need to read the full page for the skills documentation to get complete information about:
1. Where skills are discovered from (file locations)
2. How enabled_skills and disabled_skills interact

Let me read the skills page first.

The skills page gives me good information about:
- Skill format (directories with SKILL.md)
- Skill locations: custom paths in config.toml, project-level (./.vibe/skills/ or ./.agents/skills/), user-level (~/.vibe/skills/)
- Filtering: enabled_skills and disabled_skills patterns

But I need more details about how the enable/disable lists interact. The configuration page (hit 3) might have more details. Let me read that.

Now I have all the information I need to answer the user's question. Let me summarize:

**Where the CLI looks for skills:**
1. Custom paths defined in config.toml via `skill_paths`
2. Project-level: `./.vibe/skills/` or `./.agents/skills/` (when working directory is trusted)
3. User-level: `~/.vibe/skills/`

**How enable/disable lists interact:**
- If `enabled_skills` is set and non-empty: only skills matching those patterns are loaded (allow-list)
- If `enabled_skills` is empty or not set: all discovered skills are loaded EXCEPT those matching `disabled_skills` patterns

The user mentioned their skills aren't loading even though the files look right. This could be because:
1. The files aren't in the right location
2. The working directory isn't trusted (for project-level skills)
3. The enable/disable lists are filtering them out

I should provide a clear, structured answer with the locations and the interaction logic, and include the relevant documentation links.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "CLI skills loading enable disable lists file location", "max_hits": 10}
```

Result:

```
q: "CLI skills loading enable disable lists file location"

[1] https://docs.mistral.ai/vibe/code/cli/skills | section: filtering
    Skills > Enable, disable, or filter skills
    Use patterns to control which skills load: ```toml enabled_skills = ["code-review", "test-*"] disabled_skills = ["experimental-*"] ``` Skill filters support **exact names**, **glob patterns**, and **regex** with the `re:` prefix, just like tool filters. If `enabled_skills` is non-empty, it acts as an allow-list; otherwise every discovered skill is available minus those matched by `disabled_skills` …
    cite: https://docs.mistral.ai/vibe/code/cli/skills#filtering

[2] https://docs.mistral.ai/vibe/code/safety-approvals-permissions | section: enable-disable-tools
    Safety, approvals, and permissions > Per-tool permissions > Enable or disable tools
    Toggle tools globally using exact names, globs, or regex patterns: ```toml # Only allow read-only and search tools enabled_tools = ["read_file", "grep", "task"] # Or disable a specific class of tools disabled_tools = ["bash"] ```
    cite: https://docs.mistral.ai/vibe/code/safety-approvals-permissions#enable-disable-tools

[3] https://docs.mistral.ai/vibe/code/cli/configuration | section: skills
    Configuration > Common configuration sections > Skills
    Enable, disable, or add skill paths: ```toml skill_paths = ["/path/to/custom/skills"] enabled_skills = ["code-review", "test-*"] disabled_skills = ["experimental-*"] ``` `enabled_skills` and `disabled_skills` interact as follows: - If `enabled_skills` is **set and non-empty**, only skills whose name matches a pattern in that list are available. - Otherwise, every discovered skill is available, min …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#skills

[4] https://docs.mistral.ai/vibe/code/cli/skills | section: stay-in-control
    Skills > Stay in control
    - **Review a skill before enabling it** if it can call write-capable tools. - Prefer **narrow `allowed-tools` lists** over disabling tools elsewhere. - Keep project-specific skills in `./.vibe/skills/` so collaborators can review them in code review.
    cite: https://docs.mistral.ai/vibe/code/cli/skills#stay-in-control

[5] https://docs.mistral.ai/vibe/code/cli/skills | section: locations
    Skills > Skill locations
    The CLI discovers skills from several locations, in order: 1. **Custom paths** defined in `config.toml` → `skill_paths = ["/path/to/custom/skills"]` 2. **Project-level** skills in `./.vibe/skills/` or `./.agents/skills/` when the working directory is [trusted](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#trusted-folders). 3. **User-level** skills in `~/.vibe/skills/`.
    cite: https://docs.mistral.ai/vibe/code/cli/skills#locations

[6] https://docs.mistral.ai/studio/search/search-toolkit/ingestion/loaders | section: batch-loading
    File loaders > Batch loading
    Load multiple files with concurrency control: ```python import asyncio from mistralai.search.toolkit.ingestion.loaders import FileLoader from mistralai.search.toolkit.plugins.storage.s3 import S3FileLoader async def load_files_batch( loader: FileLoader, paths: list[str], max_concurrent: int = 10, ) -> list: """Load multiple files concurrently with semaphore.""" semaphore = asyncio.Semaphore(max_co …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/ingestion/loaders#batch-loading

[7] https://docs.mistral.ai/vibe/code/cli/work-with-cli | section: trust-folders
    Work with the CLI > Trust folders
    The CLI checks whether the current working directory is trusted before loading project-level configuration, skills, or agent files. The first time you run the CLI in **interactive mode** from a new directory that contains trustable files, it asks you to confirm the folder. Trust enforcement applies in **both** interactive and programmatic modes, but the confirmation prompt only appears interactive …
    cite: https://docs.mistral.ai/vibe/code/cli/work-with-cli#trust-folders

[8] https://docs.mistral.ai/vibe/code/cli/skills | section: skill-format
    Skills > Skill format
    A skill is a **directory containing a `SKILL.md` file**. The file starts with YAML frontmatter and continues with the skill instructions in Markdown. ```markdown --- name: code-review description: Perform automated code reviews. license: MIT compatibility: Python 3.12+ user-invocable: true allowed-tools: - read_file - grep - ask_user_question --- # Code review skill This skill helps analyze code q …
    cite: https://docs.mistral.ai/vibe/code/cli/skills#skill-format

[9] https://docs.mistral.ai/vibe/code/cli/skills | section: slash-commands
    Skills > Custom slash commands
    Skills are the recommended way to add your own slash commands. Set `user-invocable: true` in the frontmatter and the skill name becomes available with `/skill-name` autocompletion in the CLI prompt, and in the [VS Code extension](https://docs.mistral.ai/vibe/code/vs-code-extension/commands-slash-commands#slash-commands) slash picker too. Pair custom skills with `allowed-tools` to keep their access …
    cite: https://docs.mistral.ai/vibe/code/cli/skills#slash-commands

[10] https://docs.mistral.ai/vibe/code/cli/configuration-reference | section: top-level
    Configuration reference > Top-level keys
    | Key | Type | Default | Description | |---|---|---|---| | `default_agent` | string | | Default interactive agent, for example `"plan"`. Ignored in programmatic mode, which falls back to `auto-approve`. See [Agents](https://docs.mistral.ai/vibe/code/cli/agents) | | `active_model` | string | | Model alias currently in use. Set to a `[[models]]` `alias` or a built-in model ID | | `log_interactions` …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration-reference#top-level

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

## Answer

The CLI looks for skills in these locations, **in order**:

1. **Custom paths** defined in `config.toml` via `skill_paths = ["/path/to/custom/skills"]`
2. **Project-level** skills in `./.vibe/skills/` or `./.agents/skills/` (only when the current working directory is [trusted](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#trusted-folders))
3. **User-level** skills in `~/.vibe/skills/`
   *[Skill locations](https://docs.mistral.ai/vibe/code/cli/skills#locations)*

---

**How `enabled_skills` and `disabled_skills` interact**:

- If **`enabled_skills` is set and non-empty**, it acts as an **allow-list**: only skills whose names match the listed patterns (exact, glob, or regex with `re:` prefix) are loaded.
- If **`enabled_skills` is empty or not set**, all discovered skills are loaded **except** those whose names match any pattern in `disabled_skills`.
   *[Enable, disable, or filter skills](https://docs.mistral.ai/vibe/code/cli/skills#filtering)* and *[Configuration > Skills](https://docs.mistral.ai/vibe/code/cli/configuration#skills)*

---

**Checklist if skills aren’t loading**:
- Verify the skill directories contain a valid `SKILL.md` file.
- Confirm the working directory is trusted (for project-level skills).
- Ensure your `config.toml` paths and filter lists are correct for the intended behavior.

