# Mistral documentation through the mistral-docs server

Paste this block into the `CLAUDE.md` of a project that has the `mistral-docs` MCP server
attached (`claude mcp add --transport http mistral-docs https://<host>/mcp --header
"Authorization: Bearer <token>"`). It is the up-front half of the setup; the tools are the
just-in-time half.

```markdown
## Mistral documentation

- For any question about Mistral models, the API, SDKs, pricing, limits, Studio, Work, Vibe
  or La Plateforme, call `mistral_docs_search` before answering, even when the answer seems
  known.
- Quote only text a tool printed, and cite the `url#anchor` exactly as printed; never
  reconstruct a documentation URL.
- Before showing quotes, pass the draft and its quotes to `mistral_docs_verify_quotes` and
  drop every marker it did not verify.
- When the search does not find the answer, say the documentation does not cover it rather
  than answering from memory.
```

Four sentences and no more: this text sits in every prompt of the session, so it has to earn
its place. The same rules, for Mistral Work, live in `SKILL.md` and `custom-instructions.md`
beside this file.
