---
url: https://docs.mistral.ai/admin/identity-access/workload-identity
title: Workload identity federation
breadcrumbs: [Admin, Access and permissions]
kind: doc
locale: en
source_path: src/content/en/docs/admin/identity-access/workload-identity/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Workload identity federation

Workload identity federation lets a workload authenticate as a [service account](https://docs.mistral.ai/admin/identity-access/service-accounts) using a token that its own infrastructure signs and rotates. The platform trusts the issuer, verifies the token, and resolves it to the service account. Nothing long-lived is stored in the workload's environment.

This is the recommended way to authenticate a workflow worker running in your own Kubernetes cluster. For a workload that cannot present an issuer-signed token, give the service account an [API key](https://docs.mistral.ai/admin/identity-access/service-accounts#add-api-key) instead.

## How setup works {#how-setup-works}

Setup runs in the following order.

1. An **organization admin** [registers your cluster as a trusted issuer](https://docs.mistral.ai/admin/identity-access/workload-identity#register-trusted-issuer), once per external OIDC provider or Kubernetes cluster.
2. A **workspace admin** [creates the service account](https://docs.mistral.ai/admin/identity-access/service-accounts#create-service-account) in Mistral.
3. You [create the matching Kubernetes service account](https://docs.mistral.ai/admin/identity-access/workload-identity#set-up-k8s-sa) in your cluster. This is the workload's identity.
4. The workspace admin [adds a workload identity credential](https://docs.mistral.ai/admin/identity-access/workload-identity#add-credential), proving your workload owns that identity.
5. You [deploy the worker](https://docs.mistral.ai/admin/identity-access/workload-identity#deploy-worker) with a projected token so it authenticates automatically.

> **Note**
>
> A single trusted issuer can validate tokens for multiple credentials, and a single service account can be authorized by multiple credentials.

## Key concepts {#key-concepts}

| Concept | What it is | Who manages it |
| --- | --- | --- |
| **Trusted issuer** | A pre-approved OIDC issuer, typically one Kubernetes cluster, whose signed tokens the platform trusts. | Organization admin |
| **Subject** | The workload's identifier inside that issuer, for example `system:serviceaccount:<namespace>:<name>`. | You, in your cluster |
| **Credential** | The link that lets a workload with a given subject authenticate as a service account. | Workspace admin |
| **Proof of ownership** | A freshly signed token that proves you control the subject before the credential is created. | Workspace admin |

## Register a trusted issuer {#register-trusted-issuer}

An organization admin registers each cluster that will run your workloads. Do this once per cluster.

1. Open [Admin Console > Organization > Trusted issuers](https://admin.mistral.ai).
2. Click **Register new trusted issuer**.
3. Fill in the following fields.
4. Click **Register**.

| Field | Required | Notes |
| --- | --- | --- |
| **Name** | Yes | A human-readable label, for example `gcp-production`. |
| **Issuer URL** | Yes | The cluster's OIDC issuer URL, the expected `iss` claim on its tokens. |
| **JWKS URI** | No | Where the platform fetches signing keys. Leave empty to discover it automatically through OIDC. Most clusters need no value here. |

> **Warning**
>
> An issuer URL can be registered **once per organization**. Registering the same issuer URL again returns an error.

## Set up the Kubernetes service account {#set-up-k8s-sa}

Create a Kubernetes service account for the workload. This is the identity the workload presents, and it must exist before you add the credential.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: example-worker
  namespace: workflows
# subject -> system:serviceaccount:workflows:example-worker
```

## Add a workload identity credential {#add-credential}

The credential records which subject can authenticate as the service account. You do not type the subject in: the platform reads it from a token that the trusted issuer signed for that workload, which is what proves you control it.

1. Open the service account and click **Add new authentication**.
2. In the **Add credential** dialog, choose **Workload identity federation**.
3. Select a **Trusted issuer** from the ones your organization has registered.
4. Click **Create registration**. The platform generates a one-time **Audience** of the form `mistral-auth:<nonce>`. Copy it.
5. Mint a token for your workload carrying that audience. Expand **Using Kubernetes?** to copy a ready-made command, then replace the service account name and namespace:

```bash
kubectl create token example-worker -n workflows \
  --audience="mistral-auth:<nonce>" \
  --duration=10m
```

6. Paste the result into **Proof token**.
7. Optionally set an **Expiration**. Leave it empty for a credential that never expires.
8. Click **Create credential**.

The platform verifies the issuer's signature and matches the audience against the registration. The credential's subject is taken from the verified token, so it always reflects the workload that actually produced the proof.

> **Note**
>
> The audience is random and unguessable, and it is used only once, to register the credential. Only someone who can run the workload can mint a token stamped with it. At runtime the worker authenticates with the `api-gateway` audience instead.

> **Warning**
>
> The token you mint is short-lived. Mint it and submit it within its validity window, or the platform rejects it.

## Deploy the worker {#deploy-worker}

Run the worker as the Kubernetes service account you created, and give it a **projected service account token**: a JWT the cluster signs and the kubelet rotates on disk before it expires. At runtime the token uses the `api-gateway` audience.

Point the worker at the token file with `MISTRAL_SA_TOKEN_PATH`, and do not set an API key: its presence takes precedence over the service account token.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: example-worker
  namespace: workflows
spec:
  replicas: 1
  selector:
    matchLabels: { app: example-worker }
  template:
    metadata:
      labels: { app: example-worker }
    spec:
      serviceAccountName: example-worker
      containers:
        - name: worker
          image: <your-worker-image>
          env:
            - name: MISTRAL_SA_TOKEN_PATH
              value: /var/run/secrets/mistral-sa/token
            - name: MISTRAL_CLIENT_SERVER_URL
              value: https://api.mistral.ai
          volumeMounts:
            - name: mistral-sa-token
              mountPath: /var/run/secrets/mistral-sa
              readOnly: true
      volumes:
        - name: mistral-sa-token
          projected:
            sources:
              - serviceAccountToken:
                  path: token
                  expirationSeconds: 600
                  audience: api-gateway
```

## Manage and rotate {#manage-rotate}

A service account's **Credentials** list shows its workload identity credentials, with the subject, the trusted issuer, and the expiry.

- **Rotate** a credential by adding a new one and deleting the old one. Both can stay active during the overlap, so the worker keeps authenticating throughout.
- **Delete** a credential to stop that workload from authenticating as the service account.

Rotating a workload identity credential does not change the service account itself, so a [hardened deployment](https://docs.mistral.ai/studio/workflows/managing-workflows-in-production/hardened_deployments) that trusts the service account needs no update.

## Related {#related}

- [Service accounts](https://docs.mistral.ai/admin/identity-access/service-accounts)

- [Roles and permissions](https://docs.mistral.ai/admin/identity-access/roles-permissions)

- [Hardened deployments](https://docs.mistral.ai/studio/workflows/managing-workflows-in-production/hardened_deployments)

- [Audit log reference](https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference)
