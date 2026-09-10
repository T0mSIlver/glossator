# Corpus page sizes in Mistral Medium 3.5 tokens

## What this measures

Every page of the vendored corpus (`corpus/mistral-docs`, commit `2e094f7bbe13`) is counted with the tokenizer Mistral Medium 3.5 tokenizes requests with: model id `mistral-medium-2604`, the `tekken.json` of `mistralai/Mistral-Medium-3.5-128B` loaded through `MistralTokenizer.from_hf_hub`. What is counted is the page body -- the markdown after the frontmatter, which is what `read_page` merges its chunks back into. Chunk counts are the shipped `sec1024` section chunking's, whose own budgets are counted with tokenizer v1 (D-010a), so chunk counts and token counts in the same row come from two tokenizers on purpose: the chunk count describes the index, the token count the model.

The answer layer's `count_mistral_tokens` (`glossator/answer/context.py`) loads `MistralTokenizer.v1()`, an older model's sentencepiece tokenizer pinned there so context budgets stay comparable with the chunker's. It is **not** the Medium 3.5 tokenizer; this run does not reuse it.

## Distribution of page tokens

| pages | min | p50 | p75 | p90 | p95 | p99 | max | mean |
|---|---|---|---|---|---|---|---|---|
| 411 | 5 | 942 | 1,639 | 3,327 | 5,629 | 15,719 | 57,179 | 1,863 |

The corpus totals 765,646 tokens across its 411 pages, 3.0 times Mistral Medium 3.5's 256k context.

## Share of pages under a threshold

| under (tokens) | pages | share |
|---|---|---|
| 2,000 | 328 | 79.81% |
| 4,000 | 377 | 91.73% |
| 8,000 | 399 | 97.08% |
| 16,000 | 407 | 99.03% |
| 32,000 | 409 | 99.51% |

## The ten largest pages

| # | page | kind | tokens | characters | chunks |
|---|---|---|---|---|---|
| 1 | `https://docs.mistral.ai/studio/batch-processing` | doc | 57,179 | 190,913 | 101 |
| 2 | `https://docs.mistral.ai/studio/document-processing/basic_ocr` | doc | 44,457 | 112,290 | 80 |
| 3 | `https://docs.mistral.ai/studio/audio/speech_to_text/offline_transcription` | doc | 25,690 | 101,141 | 50 |
| 4 | `https://docs.mistral.ai/resources/deprecated/native-reasoning` | doc | 22,347 | 86,409 | 31 |
| 5 | `https://docs.mistral.ai/studio/document-processing/annotations` | doc | 15,964 | 59,965 | 37 |
| 6 | `https://docs.mistral.ai/studio/agents/agents-api` | doc | 13,519 | 45,226 | 29 |
| 7 | `https://docs.mistral.ai/models` | model | 13,462 | 32,356 | 18 |
| 8 | `https://docs.mistral.ai/resources/deprecated/customization` | doc | 9,273 | 43,971 | 44 |
| 9 | `https://docs.mistral.ai/studio/conversations/function-calling` | doc | 9,137 | 38,556 | 24 |
| 10 | `https://docs.mistral.ai/studio/audio/speech_to_text/realtime_transcription` | doc | 8,880 | 39,008 | 28 |

## Totals per kind

| kind | pages | tokens | token share | characters | chunks |
|---|---|---|---|---|---|
| api | 49 | 72,844 | 9.51% | 287,113 | 996 |
| doc | 296 | 650,801 | 85.00% | 2,522,445 | 2,890 |
| model | 66 | 42,001 | 5.49% | 122,084 | 554 |

## Pages per single read-page call

| budget (tokens) | pages fitting whole | share of corpus | median-sized pages per call |
|---|---|---|---|
| 8,000 | 399 | 97.08% | 8 |
| 16,000 | 407 | 99.03% | 16 |

## Conclusion

At an 8,000-token budget a single `read_page` call holds the typical page with room to spare -- nearly the whole corpus fits whole in one call, and the budget covers several pages of median size -- so per-page calls almost never need to paginate, and the calls that do are the long tail in the table above. At a 16,000-token budget the corpus but a handful of pages fits in one call, so a multi-page read is a matter of choosing which pages, not of splitting them. The pages that overflow either budget are the batch, OCR and transcription pages at the top of the table, and the surface reads those by section: a search hit on one of them names the section to pass to read_page.

## Figure

- `figures/page-tokens.svg`: histogram of page token counts, log x-axis, reference lines at the marker budgets

## Reproduce

The tokenizer file is downloaded from the Hugging Face Hub on first run and cached there, which is why the command needs `huggingface_hub`.

```
uv run --with huggingface_hub python -m glossator.eval.corpus_stats --corpus corpus/mistral-docs --out eval/corpus-stats
```
