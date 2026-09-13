---
url: https://docs.mistral.ai/studio/workflows/building-workflows/encryption
title: Encryption
breadcrumbs: [Studio, Workflows, Building Workflows]
kind: doc
locale: en
source_path: src/content/en/docs/studio/workflows/building-workflows/encryption/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Encryption

Encrypt all payloads (workflow inputs, activity I/O, signal data) before they leave your worker. The platform stores ciphertext, and only your workers can decrypt.

| Mode | Workflow input | Activity I/O | Stored in our database |
|------|----------------|---------------|------------------|
| Default | cleartext | cleartext | yes (cleartext) |
| Encryption | ciphertext | ciphertext | yes (ciphertext) |

> **Info**
>
> Encryption can be combined with [payload offloading](https://docs.mistral.ai/studio/workflows/building-workflows/payload_offloading) and [compression](https://docs.mistral.ai/studio/workflows/building-workflows/compression). Payloads are compressed and offloaded before encryption runs last, so the orchestrator only ever sees an encrypted reference.

## Prerequisites {#prerequisites}

Install the encryption extra:

```bash
uv add "mistralai[workflow-payload-encryption]"
```

This pulls in `cryptography`, which the SDK uses for AES-GCM encryption.

## Generate a key {#generate-key}

Generate a 256-bit AES-GCM key:

**Python**

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

key = AESGCM.generate_key(bit_length=256)
print(key.hex())
```

Store the key in your secret manager. Anyone with this key can read your workflow data.

## Configure your workers {#configure-workers}

Two modes are available:

- `full`: encrypt every payload.
- `partial`: encrypt only fields typed as `EncryptedStrField`.

**Full encryption**

```bash
TEMPORAL_PAYLOAD_ENCRYPTION__MODE=full
TEMPORAL_PAYLOAD_ENCRYPTION__MAIN_KEY=<your_hex_key>
```

**Partial encryption**

```bash
TEMPORAL_PAYLOAD_ENCRYPTION__MODE=partial
TEMPORAL_PAYLOAD_ENCRYPTION__MAIN_KEY=<your_hex_key>
```

```python
from mistralai.extra.workflows.encoding import EncryptedStrField

class PIIPayload(BaseModel):
    user_id: str                  # cleartext
    ssn: EncryptedStrField        # encrypted
```

Encrypted payloads appear as `<encrypted>` in execution traces and the Studio UI.

## Key rotation {#key-rotation}

To rotate without downtime, follow these steps:

+ **Generate a new key** using the method shown earlier.
+ **Promote the new key** and keep the old one as a secondary so workers can still decrypt in-flight executions:

    ```bash
    TEMPORAL_PAYLOAD_ENCRYPTION__MAIN_KEY=<new_key>
    TEMPORAL_PAYLOAD_ENCRYPTION__SECONDARY_KEY=<old_key>
    ```

+ **Wait** for workflows started before the rotation to finish. The wait depends on your retention plus workflow duration (default is 30 days).
+ **Remove the old key** by unsetting `SECONDARY_KEY`.
