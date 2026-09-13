---
url: https://docs.mistral.ai/studio-api/audio/speech_to_text/realtime_transcription/client_auth
title: Client authentication
breadcrumbs: [Studio, Audio, Speech to Text, Realtime]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/audio/speech_to_text/realtime_transcription/client_auth/page.mdx
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
---

# Client authentication

Browser clients cannot store long-lived API keys safely and cannot set `Authorization` headers on WebSocket connections. To support browser-based realtime transcription, Mistral provides **short-lived realtime tokens** (`rt_*`) that your server mints on behalf of the client.

## How it works {#how-it-works}

1. Your backend calls `POST /v1/client/sessions` using your API key to mint a short-lived token scoped to a specific model.
2. Your backend passes the token to the browser, for example in a REST response.
3. The browser opens the WebSocket connection using the token in the `Sec-WebSocket-Protocol` header.

![Client authentication flow: the browser asks your server for a token, your server mints an rt_* token with the Mistral API, returns it to the browser, and the browser opens the realtime transcription WebSocket using Sec-WebSocket-Protocol.](https://docs.mistral.ai/img/audio_realtime_client_auth_flow.svg)

## Step 1: Mint a token (server-side) {#mint-token}

Call `POST /v1/client/sessions` from your backend with your API key. Pass the model the client will use.

```bash
curl https://api.mistral.ai/v1/client/sessions \
  -X POST \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "purpose": "realtime",
    "model": "voxtral-mini-transcribe-realtime-2602"
  }'
```

**`201` response**

```json
{
  "object": "client.session",
  "purpose": "realtime",
  "expires_at": "2026-07-03T10:01:00Z",
  "client_secret": {
    "value": "rt_...",
    "expires_at": "2026-07-03T10:01:00Z"
  }
}
```

Return `client_secret.value` to the browser. Do not expose your API key.

> **Note**
>
> Tokens expire after approximately 60 seconds. Mint a fresh token close to when the client needs to connect, not on page load.

## Step 2: Connect from the browser (client-side) {#connect-browser}

Open the WebSocket using the token in `Sec-WebSocket-Protocol`. Browsers cannot set `Authorization` headers on WebSocket connections, so this header is the only supported transport for `rt_*` tokens.

```typescript
const token = await fetchTokenFromYourBackend(); // "rt_..."
const model = "voxtral-mini-transcribe-realtime-2602";

const ws = new WebSocket(
  `wss://api.mistral.ai/v1/audio/transcriptions/realtime?model=${model}`,
  ["realtime", token] // passed as Sec-WebSocket-Protocol
);
```

## Token properties {#token-properties}

| Property | Value |
|---|---|
| Prefix | `rt_` |
| Lifetime | ~60 seconds (configurable) |
| Scope | Single model (specified at mint time) |
| Reusable | Yes, until expiry |

A token minted for model A is rejected if used with model B.
