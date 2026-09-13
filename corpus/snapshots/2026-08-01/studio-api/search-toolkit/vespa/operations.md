---
url: https://docs.mistral.ai/studio-api/search-toolkit/vespa/operations
title: Deploy and operate
breadcrumbs: [Studio, Search Toolkit, Manage and deploy Vespa applications]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/search-toolkit/vespa/operations/page.mdx
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
---

# Deploy and operate

Production deployment and operation of Vespa applications.

## VespaClientConfig {#vespaclientconfig}

Configure the search backend with connection settings, timeouts, and retry policies:

```python
from mistralai.search.toolkit.plugins.vespa import VespaClientConfig
from vespa_app import app

collection_name = "my_collection"
config = VespaClientConfig(
    endpoint="http://localhost:8080",
    # Advanced options
    timeout=30,              # Request timeout in seconds
    max_retries=3,          # Retry failed requests
    verify_ssl=True,        # Verify TLS certificates
)

vector_store = app.get_search_index(config, collection_name=collection_name)
```

**Connection parameters**:

| Parameter | Purpose | Default |
|-----------|---------|---------|
| `endpoint` | Vespa query endpoint URL | Required |
| `timeout` | Request timeout in seconds | 30 |
| `max_retries` | Automatic retry attempts on failure | 3 |
| `verify_ssl` | Verify TLS certificates | True |

**TLS/SSL configuration** (production):

```python
from mistralai.search.toolkit.plugins.vespa import VespaClientConfig
from vespa_app import app

config = VespaClientConfig(
    endpoint="https://vespa.example.com:8080",
    verify_ssl=True,
    # Custom CA certificate
    ca_cert_path="/path/to/ca-bundle.pem",
)

vector_store = app.get_search_index(config, collection_name="my_collection")
```

## Health Checks and Readiness {#health-checks-and-readiness}

Before ingesting or querying, ensure Vespa is ready:

```python
import asyncio
from mistralai.search.toolkit.plugins.vespa import VespaClientConfig
from vespa_app import app

async def wait_for_vespa(endpoint: str, max_attempts=30):
    """Wait for Vespa to be ready for operations."""
    for attempt in range(max_attempts):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{endpoint}/ApplicationStatus",
                    timeout=5
                ) as resp:
                    if resp.status == 200:
                        print("Vespa is ready")
                        return True
        except Exception as e:
            print(f"Attempt {attempt + 1}: {e}")
        await asyncio.sleep(2)

    raise RuntimeError("Vespa failed to become ready")

# Usage
endpoint = "http://localhost:8080"
await wait_for_vespa(endpoint)
config = VespaClientConfig(endpoint=endpoint)
vector_store = app.get_search_index(config, collection_name="my_collection")
```

**Health check endpoints**:

```bash
# Application status
curl http://localhost:8080/ApplicationStatus

# Document count in collection
curl "http://localhost:8080/search/?yql=select%20*%20from%20my_collection%20limit%201"
```

## Production Deployment {#production-deployment}

For production environments, follow these guidelines:

**Cluster setup**:
- Deploy at least 3 Vespa nodes for redundancy
- Distribute nodes across availability zones
- Use a load balancer with health checks in front of query endpoints

**Network configuration**:
- Use private networks for inter-node communication
- Expose query endpoint through a reverse proxy (nginx, Cloudflare, etc.)
- Implement rate limiting and DDoS protection

**Configuration example** (distributed setup):

```python
from mistralai.search.toolkit.plugins.vespa import VespaClientConfig
from vespa_app import app

# Load balancer endpoint (single entry point)
config = VespaClientConfig(
    endpoint="https://vespa-lb.example.com",
    timeout=30,
    max_retries=3,
    verify_ssl=True,
)

vector_store = app.get_search_index(config, collection_name="my_collection")
```

**Monitoring**:
- Track ingestion latency and throughput
- Monitor query latency and error rates
- Set alerts on health check failures
- Monitor disk usage and index size growth

## See Also {#see-also}

- **[Local Development](https://docs.mistral.ai/studio-api/search-toolkit/vespa/local-development)** — Local setup guide
- **[Manage with Migrations](https://docs.mistral.ai/studio-api/search-toolkit/vespa/migrations)** — Create and evolve schemas
- **[Vespa official docs](https://docs.vespa.ai)** — Advanced configuration and operations
