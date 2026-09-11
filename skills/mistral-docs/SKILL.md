---
name: mistral-docs
description: Use when the user asks any question about Mistral products, models, pricing, rate limits, the API, SDKs, Mistral Work, Vibe, Studio, or La Plateforme, or when something in Mistral's documentation changed. Answers from the documentation through the mistral-docs connector, with a link to the section behind every claim, never from memory.
---

# Answer from the Mistral documentation

1. Search first: `mistral_docs_search` with `q` as one sentence saying what you want to find. Search again with other words before concluding the documentation does not cover it; if the same pages come back, stop. To know which pages exist under a path, call it with `under` set to the page URL and `q` empty: the tool lists them, and a page not listed does not exist.
2. Read before answering: `mistral_docs_read_page` on the page of the best hit. When a hit says the page is large, pass the `section` it names.
3. Write the answer from what you read. State the exact value, limit or name first, then explain. Put the section link right after each claim, as a Markdown link on the heading text: `[Known caveats](https://docs.mistral.ai/vibe/code/cli/teleport-cli-web#caveats)`. Use the `cite:` link exactly as the tool printed it beside the text you used.
4. Questions about when something appeared, changed or was renamed, or what a `-latest` alias pointed to on a date: `mistral_docs_history` with the phrase, the section URL, or the question.
5. When the documentation does not answer the question, say so in one sentence. Do not answer from memory and do not guess a URL.
