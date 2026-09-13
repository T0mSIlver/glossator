---
url: https://docs.mistral.ai/resources/error-glossary
title: Error glossary
breadcrumbs: [Resources]
kind: doc
locale: en
source_path: src/content/en/docs/resources/error-glossary/page.mdx
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
---

# Error glossary

This page lists the HTTP status codes returned by the Mistral API, their meanings, and how to resolve them.

## Client errors (4xx) {#client-errors}

### 400: Bad request {#400-bad-request}

The request body is malformed or missing required fields.

**Common causes:**
- Invalid JSON syntax
- Missing the `model` or `messages` field
- Unsupported parameter value (e.g., `temperature` outside 0 to 1 range)

**Resolution:** Check your request body against the [API reference](https://docs.mistral.ai/api). Validate JSON before sending.

### 401: Unauthorized {#401-unauthorized}

The API key is missing, invalid, or expired.

**Common causes:**
- No `Authorization` header
- Incorrect or revoked API key
- Using a key from a different workspace

**Resolution:** Verify your API key in [API keys](https://console.mistral.ai/api-keys). Ensure the header format is `Authorization: Bearer YOUR_API_KEY`.

### 403: Forbidden {#403-forbidden}

Your account does not have permission to access the requested resource.

**Common causes:**
- Accessing a model not available on your subscription tier
- Attempting to delete a base model
- Workspace-level permissions restricting access

**Resolution:** Check your subscription tier and model access. Contact your workspace admin if you believe this is an error.

### 404: Not found {#404-not-found}

The requested resource does not exist.

**Common causes:**
- Invalid model ID or endpoint path
- Referencing a deleted file, job, or conversation
- Typo in the URL

**Resolution:** Verify the resource ID and endpoint path. Use the list endpoints to confirm the resource exists.

### 422: Validation error {#422-validation-error}

The request is well-formed JSON but contains invalid parameter values.

**Common causes:**
- Wrong data type for a field (e.g., string instead of number)
- Enum value not in the allowed set
- Array length exceeding limits

**Resolution:** Check the response body for detailed field-level validation errors. Cross-reference with the API schema.

### 429: Too many requests {#429-too-many-requests}

You have exceeded the rate limit for your subscription tier.

**Common causes:**
- Too many requests per second
- Token-per-minute quota exceeded
- Concurrent request limit reached

**Resolution:** Implement exponential backoff. Check the `Retry-After` response header. For sustained high throughput, use [batch processing](https://docs.mistral.ai/studio-api/batch-processing) or upgrade your plan.

## Server errors (5xx) {#server-errors}

### 500: Internal server error {#500-internal-server-error}

An unexpected error occurred on the server side.

**Resolution:** Retry the request after a brief delay. If the error persists, check [status.mistral.ai](https://status.mistral.ai) or email [support@mistral.ai](mailto:support@mistral.ai).

### 502: Bad gateway {#502-bad-gateway}

The server received an invalid response from an upstream service.

**Resolution:** Wait 30 to 60 seconds and retry. This is typically transient.

### 503: Service unavailable {#503-service-unavailable}

The service is temporarily overloaded or under maintenance.

**Resolution:** Retry with exponential backoff. Check [status.mistral.ai](https://status.mistral.ai) for ongoing incidents.

### 504: Gateway timeout {#504-gateway-timeout}

The request took too long to process.

**Common causes:**
- Very long prompts or high `max_tokens` values
- Server under heavy load

**Resolution:** Reduce input size or `max_tokens`. If using streaming, ensure your client handles the connection properly. Retry after a brief delay.

## Error response format {#error-response-format}

All errors return a JSON body with this structure:

```json
{
  "object": "error",
  "message": "A human-readable description of the error.",
  "type": "invalid_request_error",
  "param": "model",
  "code": "unknown_model"
}
```

| Field | Description |
|-------|-------------|
| `message` | Human-readable error description |
| `type` | Error category (`invalid_request_error`, `authentication_error`, `rate_limit_error`, `server_error`) |
| `param` | The parameter that caused the error (if applicable) |
| `code` | Machine-readable error code (if applicable) |

## Recommended retry strategy {#retry-strategy}

For transient errors (429, 500, 502, 503, 504), implement exponential backoff:

```python
import time
import random
from mistralai.client import Mistral

client = Mistral(api_key="YOUR_API_KEY")

def call_with_retry(func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait)
```

> **Tip**
>
> The official Python and TypeScript SDKs include built-in retry logic with exponential backoff. Use the SDKs to avoid implementing this yourself.
