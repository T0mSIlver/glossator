---
url: https://docs.mistral.ai/studio/workflows/getting-started/installation
title: Installation
breadcrumbs: [Studio, Workflows, Getting Started]
kind: doc
locale: en
source_path: src/content/en/docs/studio/workflows/getting-started/installation/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Installation

This guide will walk you through setting up Workflows and verifying your installation.

## Prerequisites {#prerequisites}

Before installing the Workflows SDK, ensure you have:

1. [Python](https://www.python.org/downloads/) 3.12 or later installed on your machine.
2. [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager installed (`uvx` ships with `uv`).

## Install Workflows {#install-workflows}

Install the Workflows package from PyPI using uv:

```bash
uv add mistralai-workflows
```

This will create a virtual environment (if one doesn't exist) and install Workflows along with its core dependencies.

### Installing with Optional Dependencies {#installing-with-optional-dependencies}

The Mistral plugin provides native integration with Mistral's AI models and services, including [durable agents](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents), [tool calling](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#built-in-tools), and [multi-agent handoffs](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#multi-agent-handoffs):

```bash
uv add "mistralai-workflows[mistralai]"
```

For [payload offloading](https://docs.mistral.ai/studio/workflows/building-workflows/payload_offloading) and direct cloud storage access from activities, install the extra for your provider:

```bash
# AWS S3 support
uv add "mistralai-workflows[s3]"

# Azure Blob Storage support
uv add "mistralai-workflows[azure]"

# Google Cloud Storage support
uv add "mistralai-workflows[gcs]"

# All storage providers
uv add "mistralai-workflows[storage]"
```

## Verify Installation {#verify-installation}

To verify your installation was successful, run the following command:

```bash
uv run python -c "import mistralai.workflows; print('Workflows is installed successfully!')"
```
