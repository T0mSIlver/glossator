# Score floor calibration

## What this measures

Every query -- 12 real questions from `tests/fixtures/retrieval-dev.jsonl` and 15 hand-written junk questions from cooking, veterinary medicine, astronomy and sport -- was searched against `sec1024` at top-50, and the cosine similarity of each returned hit was read back. The question is whether an absolute similarity floor exists that a real question always clears and a junk question never does (D-030). Without one, a k-nearest-neighbour index has no way to return nothing, and an unanswerable question gets a confident wrong answer.

The numbers describe the documents that variant's schema actually held when the run happened. The lexical-footing column below was computed against `tests/fixtures/corpus`, which is the corpus the vocabulary was read from and need not be the whole of what is indexed.

## Distributions

| population | depth | n | min | p10 | median | p90 | max |
|---|---|---|---|---|---|---|---|
| real | 1 | 12 | 0.7978 | 0.7979 | 0.8400 | 0.8596 | 0.8625 |
| real | 5 | 12 | 0.7458 | 0.7598 | 0.7989 | 0.8218 | 0.8231 |
| real | 20 | 12 | 0.7054 | 0.7156 | 0.7574 | 0.7811 | 0.7850 |
| real | 50 | 12 | 0.6370 | 0.6375 | 0.6751 | 0.6996 | 0.7001 |
| junk | 1 | 15 | 0.5464 | 0.5592 | 0.6090 | 0.6690 | 0.6751 |
| junk | 5 | 15 | 0.5258 | 0.5443 | 0.5786 | 0.6424 | 0.6548 |
| junk | 20 | 15 | 0.5007 | 0.5254 | 0.5454 | 0.6099 | 0.6383 |
| junk | 50 | 15 | 0.4568 | 0.4664 | 0.4944 | 0.5500 | 0.5844 |

## Lexical footing

5 of 15 junk queries and 0 of 12 real queries have no content word anywhere in the corpus. That gate is independent of the similarity floor and is what makes a genuinely empty result reachable.

## Proposal

**A corridor of 0.1227 exists** between the worst real question's best hit (0.7978) and the best junk question's (0.6751).

- `similarity_floor`: **0.736**, the midpoint of the corridor
- `similarity_margin`: **0.072**, the largest best-to-fifth spread over 12 real questions, so the margin never cuts a real question below five hits

## Figures

- `figures/similarity-by-depth.svg`: median similarity at each depth, one line per population

## Decision

These numbers are what D-030's `similarity_floor` and `similarity_margin` are set from. They are not set from a fixture corpus: eight pages produce a similarity distribution that says nothing about four hundred.
