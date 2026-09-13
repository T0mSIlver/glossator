---
url: https://docs.mistral.ai/robots
title: Mistral AI Crawlers
breadcrumbs: []
kind: doc
locale: en
source_path: src/content/en/docs/robots/page.mdx
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
---

# Mistral AI Crawlers

## Mistral AI Crawlers

Mistral AI employs web crawlers, aka "robots", and user agents to execute tasks for its products, either automatically or upon user request. To facilitate webmasters in managing how their sites and content interact with AI, Mistral AI utilizes specific robots.txt tags.

## MistralAI-User {#mistralai-user}

`MistralAI-User` is for **user actions in Vibe**. When users ask Vibe a question, it may **visit a web page** to help answer and **include a link to the source in its response**.

`MistralAI-User` governs which sites these user requests can be made to. It is **not used for crawling the web in any automatic fashion, nor to crawl content for generative AI training**.

For more information about Mistral AI's policy with regard to web crawlers employed for generative AI training, please refer to the [Mistral AI Legal Center](https://legal.mistral.ai/).

### Crawler Info {#mistralai-user-info}

Full user-agent string:
- `Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; MistralAI-User/1.0; +https://docs.mistral.ai/robots)`

All published IP addresses:
- https://mistral.ai/mistralai-user-ips.json

## MistralAI-Index {#mistralai-index}

`MistralAI-Index` is for **automated crawling** of the web for **indexing purposes only**. This is used to **index content** for Mistral AI's search engine, which is used to help answer user questions in Vibe.

Content crawled by `MistralAI-Index` is **not used for generative AI training of any kind**.

For more information about Mistral AI's policy with regard to web crawlers employed for generative AI training, please refer to the [Mistral AI Legal Center](https://legal.mistral.ai/).

### Crawler Info {#mistralai-index-info}

Full user-agent string:
- `Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; MistralAI-Index/1.0; +https://docs.mistral.ai/robots)`

All published IP addresses:
- https://mistral.ai/mistralai-index-ips.json
