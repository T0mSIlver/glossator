---
url: https://docs.mistral.ai/studio/connectors/debugger
title: Debug Connectors
breadcrumbs: [Studio, Connectors]
kind: doc
locale: en
source_path: src/content/en/docs/studio/connectors/debugger/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Debug Connectors

The Connectors Debugger helps you test an MCP Connector server before you use it with Studio. Use it to check server reachability, authentication setup, tool discovery, and validation errors from Studio.

> **Info**
>
> The Connectors Debugger is in **Public Preview**. Validation coverage and error details can change as we add more MCP compatibility checks.

## Before you start {#before-you-start}

You need access to Studio and the MCP Connector server URL you want to test.

If the server requires authentication, prepare one of the following:

- A static HTTP header, such as `Authorization: Bearer <token>`.
- OAuth2 client credentials for the Connector server.

If your Connector uses OAuth2, configure this redirect URI in your OAuth application:

```text
https://console.mistral.ai/build/connectors/debugger/oauth-callback
```

> **Info**
>
> Credentials configured in the Debugger **aren't stored**. They last only for the current session.

## Open the Connectors Debugger {#open-debugger}

1. Open [Studio](https://console.mistral.ai/).
2. In the left menu, click `Connectors`.
3. Click `Debugger` in the top-right corner.

Alternatively, use the direct URL: [Studio > Connectors > Debugger](https://console.mistral.ai/build/connectors/debugger)

## Configure the Connector test {#configure-test}

1. In the Connector URL field, enter the MCP server URL.
2. If the server requires credentials, click the settings icon next to `Run diagnostic`:
    + In `Credentials`, select `Custom header` or `OAuth 2.0`.
    + For a custom header, set `Header name` to `Authorization` and `Header value` to `Bearer <token>`.
    + For OAuth, enter `Client ID` and `Client Secret`.
3. Click `Run diagnostic`.

> **Caution**
>
> **Only test Connector servers you trust**. The Debugger sends the configured headers or credentials to the server address you provide.

## Run a diagnostic {#run-validation}

The Debugger runs the diagnostic and generates a report on the right side of the window. If you need to repeat the test after changing the URL or credentials, click `Run again`.

When a step fails, the report explains which step failed and includes troubleshooting details. Depending on the failure, the report can include:

- `Likely cause`
- `Suggested fix`
- `Raw response`
- `Copy as curl`
- `Headers`
- `Body`
- A JSON report for the failed step

For example, if the server responds with HTML instead of an MCP JSON-RPC response, the report can show `The server responded but does not appear to be an MCP server` as the likely cause and `Verify the URL points to an MCP server, not a regular web page or REST API` as the suggested fix.

A failed step report can look like this:

```json
{
  "step": "transport_detection",
  "status": "error",
  "duration": 259,
  "data": {
    "attempt": {
      "request": {
        "method": "POST",
        "url": "https://chaos-mcp.example.com/"
      },
      "response": {
        "status": 200,
        "headers": {
          "content-type": "text/html; charset=utf-8"
        },
        "body": "<!DOCTYPE html><html lang=\"en\">..."
      }
    }
  },
  "error": {
    "type": "not_mcp_server"
  }
}
```

## Review a successful test {#successful-test}

When all checks pass, the final report shows that the MCP server is ready. The report includes the MCP protocol version, a `View official docs` link, summary metrics, instructions when available, and discovered MCP content.

A successful report can include:

- `MCP server ready`
- `Protocol 2025-11-25`
- `View official docs`
- `Tools`: the number of tools discovered
- `Prompts`: the number of prompts discovered
- `Resources`: the number of resources discovered
- `Duration`: how long the validation took
- `Checks`: the number of checks that passed, such as `3/3`
- `Instructions`: server instructions when the MCP server returns them

The `Tools` section lists discovered tools. You can use `Search...` to filter them and select `Interactive` to inspect them. For example, a test server might return tools named `echo`, `add`, and `current_time`. Selecting `echo` shows `Echo back the provided message.` as the description and shows the input schema:

```json
{
  "type": "object",
  "properties": {
    "message": {
      "description": "Text to echo",
      "type": "string"
    }
  },
  "required": ["message"]
}
```

## Troubleshoot typical MCP errors {#typical-errors}

Use the generated report first. It shows the failed step and the most specific `Likely cause` and `Suggested fix` available. The cases below explain common MCP server issues that can appear in the report.

### The response starts with HTML or isn't valid JSON-RPC. What should I check? {#the-response-starts-with-html-or-isnt-valid-json-rpc-what-should-i-check}

The URL probably points to a web page, login wall, or REST endpoint instead of the MCP endpoint.

Use the Streamable HTTP MCP endpoint URL, such as a path ending in `/mcp`. Confirm that the endpoint returns JSON-RPC 2.0 responses.

### The detail panel mentions malformed JSON, an empty body, or invalid JSON-RPC. How do I fix it? {#the-detail-panel-mentions-malformed-json-an-empty-body-or-invalid-json-rpc-how-do-i-fix-it}

The server response can't be parsed as a valid JSON-RPC 2.0 message.

Return a complete JSON body with `jsonrpc`, `id`, and either `result` or `error`. Remove HTML, byte order marks, debug banners, and empty `200` responses.

### The response has the wrong content type or a gzip error. What does that mean? {#the-response-has-the-wrong-content-type-or-a-gzip-error-what-does-that-mean}

The server headers don't match the body.

Set the expected JSON or event stream content type for your MCP transport. Only set `Content-Encoding: gzip` when the body is gzip encoded.

### The request times out, hangs, returns 500, or returns 429. What should I do? {#the-request-times-out-hangs-returns-500-or-returns-429-what-should-i-do}

The server may be slow, unavailable, rate limited, or unstable under retry.

Check server logs, timeout settings, retry behavior, and rate limits. Return `Retry-After` for `429` responses and make initialization fast.

### Authentication doesn't start after a 401. What is missing? {#authentication-doesnt-start-after-a-401-what-is-missing}

The server may not be returning a usable authentication challenge.

Include a valid `WWW-Authenticate` header and make protected resource metadata available when discovery is required.

### Discovery or token exchange fails. What should I verify? {#discovery-or-token-exchange-fails-what-should-i-verify}

The metadata, authorization, or token endpoint may be missing or rejecting the Debugger request.

Check the issuer metadata, client registration settings, `Client ID`, `Client Secret`, scopes, token endpoint, and redirect URI.

### The token is rejected immediately after consent. What causes this? {#the-token-is-rejected-immediately-after-consent-what-causes-this}

The MCP server may not accept the issued token, or the token may lack required scopes.

Validate issuer, audience, expiry, scopes, and token signature on the server side. Make sure the same authorization server protects the MCP endpoint.

### Browser-based validation fails with a CORS error. How do I fix it? {#browser-based-validation-fails-with-a-cors-error-how-do-i-fix-it}

The MCP server may not allow the Studio origin or required MCP headers.

Add CORS headers for the Studio origin. Allow `Authorization`, `Content-Type`, `Accept`, `Mcp-Session-Id`, and `Mcp-Protocol-Version` where relevant.

### Session resume fails or the client reinitializes repeatedly. What should I check? {#session-resume-fails-or-the-client-reinitializes-repeatedly-what-should-i-check}

The server may not return or preserve `Mcp-Session-Id`.

Return `Mcp-Session-Id` when required and keep session state available for subsequent requests.

### Initialize MCP fails because of capabilities, protocol version, or serverInfo. What should I return? {#initialize-mcp-fails-because-of-capabilities-protocol-version-or-serverinfo-what-should-i-return}

The `initialize` response may not match the MCP schema or may advertise unsupported protocol metadata.

Return a valid `initialize` result with supported protocol version, capabilities, and a correctly shaped `serverInfo` object.

### Tool discovery fails or the discovered tools look wrong. What should I review? {#tool-discovery-fails-or-the-discovered-tools-look-wrong-what-should-i-review}

Tool names, descriptions, or `inputSchema` values may be invalid, duplicated, too large, or unsafe.

Use unique tool names, concise descriptions, valid JSON Schema input definitions, and review tool metadata for prompt injection.

### Tool calls hang, return huge payloads, return isError, or return malformed content. What should I change? {#tool-calls-hang-return-huge-payloads-return-iserror-or-return-malformed-content-what-should-i-change}

The `tools/call` implementation may not return the expected MCP result shape or may not handle errors consistently.

Return bounded results with valid `content` blocks. Use `isError` for tool-level failures and JSON-RPC errors for protocol-level failures. Add timeouts around slow downstream calls.

## Next steps after a successful test {#next-steps}

After the Debugger validates your Connector server, use the report to confirm compatibility with Studio. The Connector creation flow isn't in scope for this release.
