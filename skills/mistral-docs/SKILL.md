---
name: mistral-docs
description: Use when the user asks any question about Mistral products, models, pricing, rate limits, the API, SDKs, Mistral Work, Vibe, Studio, or La Plateforme, or when something in Mistral's documentation changed. Answers from the documentation through the mistral-docs connector, with a link to the section behind every claim, never from memory.
---

# Answer from the Mistral documentation

1. Search first: `mistral_docs_search` with `q` as one sentence saying what you want to find. Search again with other words before concluding the documentation does not cover it; if the same pages come back, stop. To know which pages exist under a path, call it with `under` set to the page URL and `q` empty: the tool lists them, and a page not listed does not exist.
2. Read before answering: `mistral_docs_read_page` on the page of the best hit. When a hit says the page is large, pass the `section` it names. Pass `lang="typescript"` or `lang="curl"` when the user works in that language; each sample group then prints in it.
3. Write the answer from what you read. State the exact value, limit or name first, then explain. Put the section link right after each claim, as a Markdown link on the heading text: `[Known caveats](https://docs.mistral.ai/vibe/code/cli/teleport-cli-web#caveats)`. Use the `cite:` link exactly as the tool printed it beside the text you used.
4. Questions about when something appeared, changed or was renamed: `mistral_docs_history`, one form per call. `text` for a phrase, with `page_url` or `under` to look on one page or path; `page_url` and the `section` key from a hit for one section's dates and diff; `under` and `since` for what changed beneath a path. Report the interval the tool prints, never a single day.
5. Before saying Mistral does not offer or document something, list the pages under the path it would live in with `mistral_docs_search(q="", under=...)`: for a model or product, `https://docs.mistral.ai/models` and the `studio` section it belongs to. Only then say in one sentence that the documentation does not cover it, naming the paths you listed. Do not answer from memory and do not guess a URL.
