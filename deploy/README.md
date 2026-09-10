# Deploying glossator

One command from this repository puts the MCP server on a Linux host you reach
over SSH. A Cloudflare tunnel gives it an HTTPS hostname, and Mistral Work
registers that hostname as a custom MCP Connector.

The host needs docker with the compose plugin and an SSH account in the `docker`
group. This machine needs `ssh` and `rsync`. The script checks all of that first
and names anything missing.

## Two modes

| Mode | What runs on the host | When |
|---|---|---|
| `remote-index` | the MCP server alone, against `VESPA_ENDPOINT` elsewhere | an index already exists on the LAN; nothing is embedded or ingested |
| `full` | Vespa, the schema migrations, ingestion, the MCP server, optionally the API | the host owns its index |

`full` syncs `~/.cache/glossator/embeddings` to the host and mounts it into the
ingestion job, so a chunk whose text is already cached costs nothing. It refuses
to start when the host's docker filesystem is 80% full or more: Vespa blocks
external feeds above that mark, and re-indexing a page deletes its chunks before
writing the replacements, so a blocked feed empties the index (`DECISIONS.md`
D-025b). Ingestion also feeds and removes one probe document before it deletes
anything.

## Configure

```bash
cp deploy/.env.deploy.example deploy/.env.deploy
$EDITOR deploy/.env.deploy
```

`MISTRAL_API_KEY` and `GLOSSATOR_MCP_TOKEN` are required; compose refuses to
start without them rather than publishing an open server through a tunnel.
Generate the token with `openssl rand -hex 32`. The file is copied to the host
with mode 600 and is never baked into an image. It is git-ignored, like `.env`.

For `remote-index`, point `VESPA_ENDPOINT` at the Vespa that already serves the
shipped schemas, for example `http://192.168.1.98:18080`. For `full`, leave it
empty and the MCP server reaches the `vespa` service over the compose network.

## Deploy

```bash
make deploy HOST=lxc-glossator                 # remote-index
make deploy HOST=lxc-glossator MODE=full       # Vespa, migrations, ingestion
make deploy-check HOST=lxc-glossator           # health and token checks only
```

`deploy/deploy.sh --help` lists `--with-api`, `--skip-ingest`, `--skip-build`,
`--remote-dir` and `--print-plan`. Re-running redeploys: the sync, the build and
`compose up` are idempotent, and the ingestion re-embeds only what the cache
does not already hold.

The script ends by printing the health JSON, the result of an unauthenticated
and an authenticated MCP call, and the exact `curl` commands that reproduce
both.

## Manual steps for the tunnel

These are the steps to do by hand, in order, on the deployment host.

1. **Install cloudflared** and log in. `cloudflared login` opens a browser and
   writes `~/.cloudflared/cert.pem`.

   ```bash
   curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
     -o /usr/local/bin/cloudflared
   chmod +x /usr/local/bin/cloudflared
   cloudflared login
   ```

2. **Create the tunnel.** The command prints a tunnel ID and writes a
   credentials file under `~/.cloudflared/`.

   ```bash
   cloudflared tunnel create glossator
   ```

3. **Route the hostname to it.** Use a hostname on a zone in your Cloudflare
   account; this creates the DNS record.

   ```bash
   cloudflared tunnel route dns glossator glossator.example.com
   ```

4. **Place the credentials and the config.**

   ```bash
   sudo mkdir -p /etc/cloudflared
   sudo cp ~/.cloudflared/<TUNNEL-ID>.json /etc/cloudflared/
   sudo cp ~/glossator/deploy/cloudflared/config.yml /etc/cloudflared/config.yml
   sudo $EDITOR /etc/cloudflared/config.yml   # replace <TUNNEL-ID> and <HOSTNAME>
   ```

5. **Enable the unit.**

   ```bash
   sudo cp ~/glossator/deploy/cloudflared/cloudflared.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now cloudflared
   systemctl status cloudflared
   ```

6. **Check the hostname from outside.** `GET /health` carries no token.

   ```bash
   curl -s https://glossator.example.com/health
   ```

7. Put the hostname in `deploy/.env.deploy` as `GLOSSATOR_PUBLIC_HOSTNAME` and
   redeploy, so the script prints the real URLs instead of a placeholder.

## Register the Connector in Mistral Work

The Connector URL is the tunnel hostname plus `/mcp`, for example
`https://glossator.example.com/mcp`. From the documentation page on MCP
Connectors, in its exact words:

> 1. Open the `Connectors` page.
> 2. Click `+ Add Connector` and switch to the `Custom MCP Connector` tab.
> 3. Fill in the required fields:
>    - **Connector name**: a unique identifier (no spaces or special characters).
>    - **Server URL**: the full URL of your MCP-compatible server.
>    - **Description** (optional): a short explanation of what this Connector does.
> 4. Click `Connect`. The platform detects the server's authentication method automatically.
> 5. Complete the authentication flow if prompted.

On authentication, the same page:

> Our platform auto-detects the authentication method when you provide the server URL:
>
> - **No authentication**: for publicly accessible or trusted internal servers.
> - **HTTP Bearer Token / Basic Auth**: for servers that require credentials in the `Authorization` header.
> - **OAuth 2.1** (with dynamic client registration): for servers using standard OAuth 2.1 delegated access. You'll be guided through the consent flow.

glossator is the second case: give it the `GLOSSATOR_MCP_TOKEN` value when Work
asks for the bearer token.

Then pre-authorize the functions you use, again in the page's words:

> 1. Go to `Connectors` and select the `My Connectors` tab.
> 2. Click the Connector card to open its details.
> 3. Open the `Functions` tab.
> 4. Toggle `Always allow` for each function you want to pre-authorize.

> **Tip**
>
> Pre-authorize read functions you use frequently to reduce approval prompts. Keep write functions on manual approval until you're confident in the Connector's behavior.

Every glossator tool is a read function; the server exposes nothing that writes,
and every tool declares it (`readOnlyHint`, `idempotentHint`, no open world), so
a host does not have to assume the worst and confirm each call.
Pre-authorize all three (`mistral_docs_search`, `mistral_docs_read_page`,
`mistral_docs_history`). Name the Connector `mistral_docs` and describe it as
"Searches docs.mistral.ai at a pinned commit and shows what changed.".

`skills/mistral-docs/` in this repository is the workspace Skill that tells Work
when to reach for the Connector.

The same page lists what custom MCP Connectors do not support yet: dynamic tool
discovery, **resources**, and automatic prompt templates. The three glossator
resources (`glossator://guide`, `glossator://index`, `glossator://context`) are
therefore unreadable from Work, and the shared rules reach the model through the
tool descriptions and the workspace Skill instead. Clients that do support
resources, such as Claude Code, read them normally.

## Test the deployment

**Connectors Debugger.** From the Debug Connectors page, in its exact words:

> 1. Open [Studio](https://console.mistral.ai/).
> 2. In the left menu, click `Connectors`.
> 3. Click `Debugger` in the top-right corner.

> 1. In the Connector URL field, enter the MCP server URL.
> 2. If the server requires credentials, click the settings icon next to `Run diagnostic`:
>     + In `Credentials`, select `Custom header` or `OAuth 2.0`.
>     + For a custom header, set `Header name` to `Authorization` and `Header value` to `Bearer <token>`.
>     + For OAuth, enter `Client ID` and `Client Secret`.
> 3. Click `Run diagnostic`.

The URL is `https://glossator.example.com/mcp`, the credential is a custom
header, and the header value is `Bearer` followed by `GLOSSATOR_MCP_TOKEN`.
Credentials entered there are not stored and last only for that session.

**curl**, from the troubleshooting section of the Connectors page:

```bash
curl -I https://glossator.example.com/mcp
curl -H "Authorization: Bearer YOUR_API_KEY" https://glossator.example.com/mcp
curl -X POST https://glossator.example.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{}}}'
```

The last one answers `401` here, because that request carries no token; add
`-H "Authorization: Bearer <token>"` and `-H "Accept: application/json,
text/event-stream"` for a `200` with the server's capabilities.

**Claude Code.** Verified against `claude mcp add --help`:

```bash
claude mcp add --transport http mistral-docs https://glossator.example.com/mcp \
  --header "Authorization: Bearer <token>"
claude mcp list
```

Then ask a question that needs the documentation and watch for a
`mistral_docs_search` call. `claude mcp remove mistral-docs` undoes it.

## What each variable does

`deploy/.env.deploy.example` lists every variable with a comment. The ones that
change per deployment:

| Variable | Meaning |
|---|---|
| `MISTRAL_API_KEY` | embeddings, and generation unless a chat server is set |
| `GLOSSATOR_MCP_TOKEN` | the bearer token every MCP request must carry |
| `GLOSSATOR_MCP_TOOLS` | comma-separated subset of the three tools to register; blank means all |
| `VESPA_ENDPOINT` | the index to serve; blank in full mode |
| `GLOSSATOR_VARIANT` | `page128`, `sec128` or `sec1024` |
| `GLOSSATOR_PUBLIC_HOSTNAME` | the tunnel hostname, used in the printed commands and the Connector URL |
| `GLOSSATOR_CHAT_SERVER_URL` | optional local generation server for the API's `POST /ask` |
| `MCP_PORT`, `API_PORT`, `VESPA_QUERY_PORT` | published ports on the host |
| `MCP_BIND_ADDRESS` | `127.0.0.1` so only the tunnel reaches the server |

## Troubleshooting

**`/health` reports `degraded`.** The body says which half failed: `chunks:
null` means Vespa is unreachable or the schema is empty, and
`embedding_probe.passed: false` means the embedding model did not place the five
fixed probe pairs correctly (D-031). A server in that state still answers, but
its answers are not trustworthy.

**Ingestion aborts with a write-probe message.** Vespa rejected a one-document
feed. Almost always disk: free space and run the deploy again. Nothing was
deleted.

**Work says "MCP connection requires additional information or is invalid".**
Check the path is `/mcp`, that the hostname resolves over HTTPS with a valid
certificate, and that the token matches. `make deploy-check HOST=...` answers
the last one from inside the container.

**The tunnel is up but every call is 502.** The MCP container is not listening
on 127.0.0.1:8000 on the host. `docker compose -f deploy/compose.yaml ps` and
`... logs mcp` on the host say why.
