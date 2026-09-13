---
url: https://docs.mistral.ai/robots
title: Mistral AI Crawlers
breadcrumbs: []
kind: doc
locale: en
source_path: src/content/en/docs/robots/page.mdx
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
---

# Mistral AI Crawlers

Mistral uses web crawlers, also known as robots, and user agents to run product tasks automatically or when a user requests them. To help webmasters manage how their sites and content interact with AI, Mistral uses specific `robots.txt` tags.

## MistralAI-User {#mistralai-user}

`MistralAI-User` is for **user actions in Vibe**. When users ask Vibe a question, it may **visit a web page** to help answer and **include a link to the source in its response**.

`MistralAI-User` governs which sites these user requests can be made to. It is **not used for crawling the web in any automatic fashion, nor to crawl content for generative AI training**.

For more information about Mistral policy for web crawlers used for generative AI training, see the [Mistral Legal Center](https://legal.mistral.ai/).

### Crawler info {#mistralai-user-info}

Full user-agent string:
- `Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; MistralAI-User/1.0; +https://docs.mistral.ai/robots)`

All published IP addresses:
- https://mistral.ai/mistralai-user-ips.json

## MistralAI-Index {#mistralai-index}

`MistralAI-Index` is for **automated crawling** of the web for **indexing purposes only**. It indexes content for Mistral search, which helps answer user questions in Vibe.

Content crawled by `MistralAI-Index` is **not used for generative AI training of any kind**.

For more information about Mistral policy for web crawlers used for generative AI training, see the [Mistral Legal Center](https://legal.mistral.ai/).

### Crawler info {#mistralai-index-info}

Full user-agent string:
- `Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; MistralAI-Index/1.0; +https://docs.mistral.ai/robots)`

All published IP addresses:
- https://mistral.ai/mistralai-index-ips.json
