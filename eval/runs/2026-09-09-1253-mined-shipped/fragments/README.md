# Citation fragment resolvability

The check sampled 60 verified citations from `records.jsonl` with
seed 0, reading the links stored under `fragment_url`.
It fetched each cited documentation page once, reduced the HTML to its visible text
block by block (paragraphs, list items, cells, headings, code blocks), and searched
for the decoded text fragment inside one block, without regard to case or whitespace
runs: a browser does not match a phrase across a block boundary (D-036c). A range
directive passes when each end sits inside one block and the end follows the start.
A miss that the page's text would contain with its blocks joined is counted as
`across blocks`.

51 of 60 sampled fragments were present
(85.0%). 2 absent fragment(s)
came from tab-labelled source text. The live HTML omits non-default tab panels even
though a browser can render them after selecting the tab (D-003). After excluding
those citations, 51 of 58 fragments were found
(87.9%).

## Failures

| reason | citations |
|---|---:|
| text absent | 9 |

## Question types

| type | checked | found | tab exclusions | found in eligible HTML |
|---|---:|---:|---:|---:|
| api_reference | 4 | 4 | 0 | 100.0% |
| cross_page | 5 | 4 | 0 | 80.0% |
| single_page | 46 | 39 | 1 | 86.7% |
| unanswerable | 5 | 4 | 1 | 100.0% |

## Files

`results.jsonl` has one row per sampled citation. `metrics.json` contains these
counts. `pages/` caches the HTTP responses, so repeating the command reads no
documentation pages from the network. This check calls no model, so it has no
`calls.jsonl`.
