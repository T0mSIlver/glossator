---
url: https://docs.mistral.ai/vibe/work/web-search-open-url
title: Search the web
breadcrumbs: [Vibe, Work]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/work/web-search-open-url/page.mdx
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
---

# Search the web

Work can browse the internet in real time and read specific web pages as part of a task. **Web search** answers questions with up-to-date, sourced information. **Open URL** lets Work read and analyze a page you already have the link to.

> **Info**
>
> **Knowledge cutoff**: every language model is trained on data collected up to a fixed date. After that date, the model has no built-in knowledge of new events, releases, or facts. Web search and Open URL let Work go past that cutoff and answer with **verifiable, up-to-date sources**.

> **Note**
>
> For multi-source, in-depth research with structured cited reports and PDF export, use [Deep Research](https://docs.mistral.ai/vibe/chat-legacy/deep-research) in Chat. Deep Research isn't available in Work.

## Web search {#web-search}

Web search lets Work fetch current information from across the web and use it to answer your prompt.

### Activation {#web-search-activation}

1. Click the `+` icon or type `/` in the chat window.
2. Select `Tools` then enable `Web search`.

When you ask a question that needs current information, Work **searches the web** and weaves the findings into its response. Ask your question naturally.

### Reading the results {#reading-results}

When Work uses web search to answer your question, you'll notice:

- A **globe icon** next to the response, confirming that web data was used.
- **Inline links** pointing back to the original sources.
- A `Sources` button at the bottom of the response that opens a panel listing every reference in one place.

Every **web-sourced response comes with its references** so you can check the underlying material yourself.

### News search {#news-search}

For news queries, Work draws from professional news partners [Agence France-Presse](https://www.afp.com/en) (AFP) and [Associated Press](https://apnews.com/) (AP), so results come from **verified, editorially vetted sources** you can cite with confidence.

When news results are included, you'll see a **news icon** alongside the globe icon. Sources link directly to the original agency reporting, giving you reliable material for briefings or internal updates.

> **Tip**
>
> For quick competitive or market intelligence, try prompts like *"Latest regulatory updates in [your industry]"* or *"Recent funding rounds in [sector]."*

## Open URL {#open-url}

Open URL lets you **bring web content directly into a Work chat**. Instead of copying and pasting text from a webpage, paste the URL and let Work fetch, read, and use the page content as context.

### How to use {#open-url-how-to-use}

1. Ensure **Web Search** is enabled:
    + Click the `+` icon or type `/` in the chat window.
    + Select `Tools`.
    + Enable `Web Search`. Without this, Work cannot browse the web.
2. Paste a URL into the message box, along with your question or instruction.
3. Send the message. Work fetches the page and uses its content to answer.

You'll see a link icon and an `Opened Page` mention in the response, confirming that Work read the page content.

> **Tip**
>
> Open URL also works with links to online files (PDFs, documents). Work fetches the file and answers your question with context.

### Working with multiple URLs {#multiple-urls}

You can paste **several URLs in a single chat**. Work keeps the content from each page in context, so you can ask follow-up questions that reference or compare them.

For example, paste two competitor product pages and ask: *"Compare the feature sets described on these two pages."* Work uses both pages as context to generate a side-by-side comparison.

### Common use cases {#open-url-use-cases}

- **Competitor analysis**: paste a competitor's product page and ask Work to extract features, pricing, or positioning.
- **Documentation review**: share a docs page and ask for a summary, or check it against your own specifications.
- **Article summarization**: drop in a long article and get the key takeaways.
- **Meeting prep**: paste an agenda or briefing document hosted online and ask Work to highlight the most important items.

## Choosing the right tool {#choosing-the-right-tool}

Pick the option that fits your situation:

| You want to... | Use |
|----------------|-----|
| Get a quick, up-to-date answer with sources | **Web search** |
| Analyze a specific page you already have the link to | **Open URL** |
| Get a structured, cited report pulling from many sources | **[Deep Research](https://docs.mistral.ai/vibe/chat-legacy/deep-research)** (Chat legacy only) |
| Search trusted internal documents | **[Libraries](https://docs.mistral.ai/vibe/work/libraries)** |
| Pull live data from a connected tool (Gmail, Drive, Notion...) | **[Connectors](https://docs.mistral.ai/vibe/work/connectors)** |

## Limitations {#limitations}

- Open URL fetches only the single page at the URL you provide. It doesn't crawl the entire site or follow links.
- Pages behind a login or paywall can't be accessed. Download the content and [upload it as a file](https://docs.mistral.ai/vibe/work/files-and-canvas) instead.
- Some highly interactive websites may not load fully, which can result in incomplete content.
- Web search can return outdated or incomplete content depending on what the source page exposes.
