# Surface defects

Every wrong turn a consumer took, with the transcript path, a severity,
and a proposed fix in prose. Fixes to the server belong in their own change.

## 1. mined-052 (claude-sonnet-low / A1)

- Observation: mcp__mistral-docs__mistral_docs_verify_quotes returned 1 validation error for call[mistral_docs_verify_quotes]
- Transcript: `transcripts/claude-sonnet-low/A1/mined-052.jsonl`
- Severity: friction
- Proposed fix: Check whether the typed error and its next hint led the consumer to a working call within two turns; if not, sharpen the hint.
