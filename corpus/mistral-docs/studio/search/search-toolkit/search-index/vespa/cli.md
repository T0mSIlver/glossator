---
url: https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli
title: CLI reference
breadcrumbs: [Studio, Search, Search Toolkit, Search index, Vespa]
kind: doc
locale: en
source_path: src/content/en/docs/studio/search/search-toolkit/search-index/vespa/cli/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# CLI reference

The `mistral-vespa` CLI manages the Vespa application lifecycle, from generating migrations to deployment and testing.

> **Tip**
>
> Run `uv run mistral-vespa --help` for the full list of available commands and flags.

## `generate-migration` {#generate-migration}

Create a timestamped migration stub.

```bash
uv run mistral-vespa generate-migration <name> [--app-dir <path>]
```

| Argument/Flag | Default | Description |
|---|---|---|
| `name` | required | Migration name, used for filename and class stub |
| `--app-dir` | `./vespa_app` | Root directory of the Vespa application |

## `migrate` {#migrate}

Build the application from migrations and deploy it. Supports both single-node (localhost) and Kubernetes deployments.

```bash
uv run mistral-vespa migrate [--app-dir <path>] [flags]
```

| Flag | Default | Description |
|---|---|---|
| `--app-dir` | `./vespa_app` | Root directory of the Vespa application |
| `--dry-run` | `false` | Preview changes without applying them |
| `--config-server` | auto | Config server URL (host:port). Defaults to `http://localhost:19071` for local, or in-cluster service URL for K8s |
| `--query-port` | `8080` | Host-side query port to poll after deploy |

**Kubernetes flags** (deprecated): use `generate-topology` to produce a topology file, then pass it with `--topology-file`.

| Flag | Default | Description |
|---|---|---|
| `--k8s-namespace` | Not applicable | Kubernetes namespace (required with `--k8s-instance`) |
| `--k8s-instance` | Not applicable | Kubernetes instance (required with `--k8s-namespace`) |
| `--k8s-context` | Not applicable | Kubernetes context. Requires `--k8s-namespace`, `--k8s-instance`, and `--config-server` |

**Examples:**

```bash
# Local Docker
uv run mistral-vespa migrate --config-server http://localhost:19071

# Kubernetes (in-cluster, e.g. CI)
uv run mistral-vespa migrate \
  --k8s-namespace my-project \
  --k8s-instance vespa

# Kubernetes (workstation, with kubectl port-forward)
uv run mistral-vespa migrate \
  --k8s-namespace my-project \
  --k8s-instance vespa \
  --k8s-context staging \
  --config-server http://localhost:19071
```

## `generate` {#generate}

Write the application package files to disk from migrations (for inspection or CI validation). Not used for deployment.

```bash
uv run mistral-vespa generate --path <output-dir> [--app-dir <path>]
```

| Flag | Default | Description |
|---|---|---|
| `--path` | required | Directory to write the app package files to |
| `--app-dir` | `./vespa_app` | Root directory of the Vespa application |

**Output structure:**

```text
<output-dir>/
├── schemas/
│   └── <document_type>.sd
└── search/
    └── query-profiles/
        ├── <query_profile_name>.xml
        └── types/root.xml
```

## `bruno` {#bruno}

Generate Bruno API test files from migrations.

```bash
uv run mistral-vespa bruno --query-url <url> --document-url <url> [--app-dir <path>]
```

| Flag | Default | Description |
|---|---|---|
| `--query-url` | required | Vespa query endpoint URL |
| `--document-url` | required | Vespa document/feed endpoint URL |
| `--app-dir` | `./vespa_app` | Root directory of the Vespa application |

## `local up` {#local-up}

Start a local Vespa container via Docker.

```bash
uv run mistral-vespa local up [--query-port <port>] [--config-port <port>] [--name <name>]
```

| Flag | Default | Description |
|---|---|---|
| `--query-port` | `8080` | Host port mapped to Vespa query |
| `--config-port` | `19071` | Host port mapped to Vespa config server |
| `--name` | `vespa` | Docker container name |

## `local down` {#local-down}

Stop the local Vespa container and remove volumes.

```bash
uv run mistral-vespa local down [--name <name>]
```

## `local status` {#local-status}

Check if the local Vespa container is running.

```bash
uv run mistral-vespa local status [--name <name>]
```
