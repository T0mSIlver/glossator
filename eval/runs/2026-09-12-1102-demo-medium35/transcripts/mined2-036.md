# mined2-036 (single_page, 3 connector calls)

## Question

Which setting wins when the same option is set in the project config, an environment variable, a command-line flag and my organization's admin config?

## Thinking

The user is asking about the precedence order of configuration settings for Mistral's tools. They want to know which setting takes priority when the same option is set in multiple places: project config, environment variable, command-line flag, and organization's admin config.

I need to search the Mistral documentation to find information about configuration precedence. Let me use the mistral_docs_search tool to look for this information.

The search returned results showing that there is a precedence order documented. Let me read the configuration page to get the full details.

The user wants to know which configuration source wins when the same option is set in multiple places. Based on the search results, I can see there's a precedence order documented in the Mistral CLI configuration documentation.

From the search results:
- Hit 1 shows the precedence order: Admin config > CLI flags > Environment variables > Project config > User config
- Hit 2 explicitly states: "Admin config is the **highest-priority** layer. It takes precedence over command-line flags, environment variables, and both project and user `config.toml`"

So the order from highest to lowest priority is:
1. Admin config (organization's admin config)
2. Command-line flags
3. Environment variables
4. Project config
5. User config

The user specifically asked about: project config, environment variable, command-line flag, and organization's admin config.

According to the documentation, the precedence is:
**Admin config > Command-line flags > Environment variables > Project config**

Therefore, the **organization's admin config** wins over all the others. If the admin config sets an option, it will override the command-line flag, environment variable, and project config.

Let me verify this by reading the admin-config page as well to be thorough.

The user is asking about the precedence order of configuration settings in Mistral's CLI. They want to know which setting wins when the same option is set in:
1. Project config
2. Environment variable
3. Command-line flag
4. Organization's admin config

From the search results and the pages I've read, I can see that Mistral's documentation clearly defines the precedence order for Vibe Code CLI configuration:

From the configuration page (hit 1):
"When the same setting is defined in multiple places, the CLI applies them in this order, from **highest to lowest priority**:
1. **Admin config**, when your Organization provides one.
2. **Command-line flags** (for example, `--agent`, `--workdir`).
3. **Environment variables** (for example, `MISTRAL_API_KEY`, `VIBE_HOME`).
4. **Project** `./.vibe/config.toml`.
5. **User** `~/.vibe/config.toml`."

From the admin-config page (hit 2):
"Admin config is the **highest-priority** layer. It takes precedence over command-line flags, environment variables, and both project and user `config.toml`:
```text
admin config  >  CLI flags  >  env vars  >  project config.toml  >  user config.toml
```"

So the order is clear:
1. Admin config (highest priority)
2. Command-line flags
3. Environment variables
4. Project config
5. User config (lowest priority)

The user specifically asks about: project config, environment variable, command-line flag, and organization's admin config.

According to the documentation, the **organization's admin config** has the highest priority and wins over all the others.

The answer should be: **Your organization's admin config** wins.

I should format this clearly and include the citation links as shown in the documentation.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "precedence order for configuration settings: project config, environment variable, command-line flag, organization admin config"}
```

Result:

```
q: "precedence order for configuration settings: project config, environment variable, command-line flag, organization admin config"

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

### 3. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/admin-config", "section": "precedence"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/cli/admin-config | "Admin config" | section: precedence

## section: precedence
    Admin config > Precedence
    cite: https://docs.mistral.ai/vibe/code/cli/admin-config#precedence
## Precedence {#precedence}

Admin config is the **highest-priority** layer. It takes precedence over command-line flags, environment variables, and both project and user `config.toml`:

```text
admin config  >  CLI flags  >  env vars  >  project config.toml  >  user config.toml
```

This precedence means the admin-provided values take effect for users by default, without them needing to update their own `config.toml`.

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/admin-config", section="what-can-be-set") for the section after it
```

## Answer

The **organization's admin config** wins. It has the highest priority and overrides command-line flags, environment variables, and project config.

The full precedence order is:
**Admin config > CLI flags > Environment variables > Project config > User config**
[Configuration precedence](https://docs.mistral.ai/vibe/code/cli/configuration#precedence)
[Admin config precedence](https://docs.mistral.ai/vibe/code/cli/admin-config#precedence)

