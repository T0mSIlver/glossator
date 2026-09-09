# Citation fragment resolvability

The check sampled 60 verified citations from `records.jsonl` with
seed 0. It fetched each cited documentation page once, reduced the
HTML to visible text, and searched for the decoded text fragment without regard to
case or whitespace runs. Range directives pass only when both ends occur in order.

50 of 60 sampled fragments were present
(83.3%). 2 absent fragment(s)
came from tab-labelled source text. The live HTML omits non-default tab panels even
though a browser can render them after selecting the tab (D-003). After excluding
those citations, 50 of 58 fragments were found
(86.2%).

## Failures

| reason | citations |
|---|---:|
| text absent | 10 |

## Question types

| type | checked | found | tab exclusions | found in eligible HTML |
|---|---:|---:|---:|---:|
| api_reference | 4 | 4 | 0 | 100.0% |
| cross_page | 5 | 3 | 0 | 60.0% |
| single_page | 46 | 39 | 1 | 86.7% |
| unanswerable | 5 | 4 | 1 | 100.0% |

## Files

`results.jsonl` has one row per sampled citation. `metrics.json` contains these
counts. `pages/` caches the HTTP responses, so repeating the command reads no
documentation pages from the network. This check calls no model, so it has no
`calls.jsonl`.
