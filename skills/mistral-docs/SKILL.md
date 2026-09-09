---
name: mistral-docs
description: Use when the user asks any question about Mistral products, models, pricing, rate limits, the API, SDKs, Mistral Work, Vibe, Studio, or La Plateforme. Answers from the Mistral documentation through the mistral-docs connector with verified quotes, never from memory.
---

# Answer from the Mistral documentation

1. Search first with the mistral-docs connector (`mistral_docs_search`, two or three distinctive words).
2. Read the sections you rely on (`mistral_docs_open_section` on a promising hit, `mistral_docs_read_page` for a range).
3. Write the answer with `[n]` markers and verbatim quotes from the hits.
4. Call `mistral_docs_verify_quotes` with the draft and the quotes. Drop every marker it did not verify.
5. Paste its Sources block under the answer.
6. Never answer from memory. When the documentation does not answer, say so.
