# Citation fragment resolvability

The check sampled 60 verified citations from `records.jsonl` with
seed 0. It fetched each cited documentation page once, reduced the
HTML to visible text, and searched for the decoded text fragment without regard to
case or whitespace runs. Range directives pass only when both ends occur in order.

49 of 60 sampled fragments were present
(81.7%). 2 absent fragment(s)
came from tab-labelled source text. The live HTML omits non-default tab panels even
though a browser can render them after selecting the tab (D-003). After excluding
those citations, 49 of 58 fragments were found
(84.5%).

## Failures

| reason | citations |
|---|---:|
| text absent | 11 |

## Question types

| type | checked | found | tab exclusions | found in eligible HTML |
|---|---:|---:|---:|---:|
| api_reference | 7 | 3 | 1 | 50.0% |
| capability | 7 | 5 | 0 | 71.4% |
| cross_page | 14 | 13 | 0 | 92.9% |
| post_cutoff | 9 | 6 | 1 | 75.0% |
| single_page | 13 | 12 | 0 | 92.3% |
| unanswerable | 10 | 10 | 0 | 100.0% |

## Files

`results.jsonl` has one row per sampled citation. `metrics.json` contains these
counts. `pages/` caches the HTTP responses, so repeating the command reads no
documentation pages from the network. This check calls no model, so it has no
`calls.jsonl`.
