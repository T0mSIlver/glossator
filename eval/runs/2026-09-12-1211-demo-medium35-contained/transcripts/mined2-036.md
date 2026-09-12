# mined2-036 (single_page, 2 connector calls)

## Question

Which setting wins when the same option is set in the project config, an environment variable, a command-line flag and my organization's admin config?

## Thinking

The user is asking about the precedence order of configuration settings in Mistral's ecosystem. They want to know which setting takes priority when the same option is defined in multiple places: project config, environment variable, command-line flag, and organization admin config.

I need to search the Mistral documentation for information about configuration precedence or priority. The query should be specific to find the exact documentation about this.

The search returned results pointing to the Mistral documentation about CLI configuration precedence. I can see from the first hit that there's a "precedence" section in the configuration documentation. Let me read that page to get the exact details.

I have the documentation now. The precedence order is clearly stated. From highest to lowest priority:
1. Admin config (organization admin config)
2. Command-line flags
3. Environment variables
4. Project config (./.vibe/config.toml)
5. User config (~/.vibe/config.toml)

The user asked specifically about project config, environment variable, command-line flag, and organization admin config. Based on this list, the order would be:
1. Admin config (highest)
2. Command-line flags
3. Environment variables
4. Project config

So the answer is: **Admin config** wins, as it has the highest priority.

I need to format this clearly and cite the documentation. The user wants to know which setting wins, so I should be direct.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "precedence order of configuration settings: project config, environment variable, command-line flag, organization admin config"}
```

Result:

```
q: "precedence order of configuration settings: project config, environment variable, command-line flag, organization admin config"

[1] https://docs.mistral.ai/vibe/code/cli/configuration | section: precedence
    Configuration > Configuration precedence
    When the same setting is defined in multiple places, the CLI applies them in this order, from **highest to lowest priority**: 1. **Admin config**, when your Organization provides one. See [Admin config](https://docs.mistral.ai/vibe/code/cli/admin-config). 2. **Command-line flags** (for example, `--agent`, `--workdir`). 3. **Environment variables** (for example, `MISTRAL_API_KEY`, `VIBE_HOME`). 4. …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#precedence

[2] https://docs.mistral.ai/vibe/code/cli/admin-config | section: precedence
    Admin config > Precedence
    Admin config is the **highest-priority** layer. It takes precedence over command-line flags, environment variables, and both project and user `config.toml`: ```text admin config > CLI flags > env vars > project config.toml > user config.toml ``` This precedence means the admin-provided values take effect for users by default, without them needing to update their own `config.toml`.
    cite: https://docs.mistral.ai/vibe/code/cli/admin-config#precedence

[3] https://docs.mistral.ai/vibe/code/cli/configuration | section: admin-config
    Configuration > Admin-managed configuration
    Your Organization can distribute a Vibe Code CLI configuration to all users. Admin-managed settings take precedence over command-line flags, environment variables, and the project and user `config.toml` files. When admin config is active: - Admin-managed settings in `/config` appear dim with a `⚿` lock glyph and list `your administrator` as the origin. A legend at the bottom of the screen reads `⚿ …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#admin-config

[4] https://docs.mistral.ai/vibe/code/cli/admin-config | section: admin-config
    Admin config
    Admin config, also called **managed config**, lets Organization and Workspace administrators distribute Vibe Code CLI settings to all users. You define it once in the Admin Panel, and the CLI applies it to users in the Organization or Workspace. Use it to distribute models, providers, MCP servers, and tool policies without requiring users to edit `config.toml`. > **Info** > > Admin config is a **d …
    cite: https://docs.mistral.ai/vibe/code/cli/admin-config

[5] https://docs.mistral.ai/vibe/code/cli/configuration-reference | section: environment-variables
    Configuration reference > Environment variables
    Not `config.toml` keys, but part of the configuration model. They sit at precedence level 3 (env vars). | Variable | Purpose | |---|---| | `VIBE_HOME` | Overrides the `~/.vibe/` home directory for all state (config, prompts, agents, skills, logs) | | `MISTRAL_API_KEY` | Primary Mistral API key | | `<PROVIDER>_API_KEY` | API key referenced by a `[[providers]]` `api_key_env_var` (for example `OPENRO …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration-reference#environment-variables

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/configuration") to read hit 1 on its page
```

### 2. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/configuration", "section": "precedence"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/cli/configuration | "Configuration" | section: precedence

## section: precedence
    Configuration > Configuration precedence
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#precedence
## Configuration precedence {#precedence}

When the same setting is defined in multiple places, the CLI applies them in this order, from **highest to lowest priority**:

1. **Admin config**, when your Organization provides one. See [Admin config](https://docs.mistral.ai/vibe/code/cli/admin-config).
2. **Command-line flags** (for example, `--agent`, `--workdir`).
3. **Environment variables** (for example, `MISTRAL_API_KEY`, `VIBE_HOME`).
4. **Project** `./.vibe/config.toml`.
5. **User** `~/.vibe/config.toml`.

Results: the whole section.
```

## Answer

The **organization's admin config** wins, as it has the highest priority.

The full precedence order for the Vibe Code CLI is:
1. **Admin config** (highest)
2. Command-line flags
3. Environment variables
4. Project config (`./.vibe/config.toml`)
5. User config (`~/.vibe/config.toml`)

[Configuration precedence](https://docs.mistral.ai/vibe/code/cli/configuration#precedence)

