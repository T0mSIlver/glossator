# Surface defects

Every wrong turn a consumer took, with the transcript path, a severity,
and a proposed fix in prose. Fixes to the server belong in their own change.

## 1. mined2-070 (claude-haiku-low / A1)

- Observation: mcp__mistral-docs__mistral_docs_read_page rejected with E_BAD_PARAM: error: E_BAD_PARAM
- Transcript: `transcripts/claude-haiku-low/A1/mined2-070.jsonl`
- Severity: extra-calls
- Proposed fix: Read the transcript turn: if the parameter name came from the tool description, rename the description's wording; if it came from the guide, fix the guide.

## 2. mined2-023 (claude-haiku-low / A1)

- Observation: mcp__mistral-docs__mistral_docs_read_page rejected with E_BAD_PARAM: error: E_BAD_PARAM
- Transcript: `transcripts/claude-haiku-low/A1/mined2-023.jsonl`
- Severity: extra-calls
- Proposed fix: Read the transcript turn: if the parameter name came from the tool description, rename the description's wording; if it came from the guide, fix the guide.
