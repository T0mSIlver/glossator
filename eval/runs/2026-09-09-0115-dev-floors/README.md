# Score floor calibration

## What this measures

Every query -- 294 questions from `eval/dev.jsonl` and 15 hand-written junk questions from cooking, veterinary medicine, astronomy and sport -- was searched against `sec1024` at top-50, and the cosine similarity of each returned hit was read back. The question is whether an absolute similarity floor exists that a real question always clears and a junk question never does (D-030). Without one, a k-nearest-neighbour index has no way to return nothing, and an unanswerable question gets a confident wrong answer.

Three populations, not two. **real** is an answerable dataset question. **junk** is a question about another subject entirely. **unanswerable** is the dataset's own unanswerable type: written in this corpus's vocabulary, and not answered by it. Only `real` sets the floor -- a floor fitted to accept a question the corpus cannot answer would accept everything -- and `unanswerable` is measured against the proposal instead.

The numbers describe the documents that variant's schema actually held when the run happened. The lexical-footing column below was computed against `corpus/mistral-docs`, which is the corpus the vocabulary was read from and need not be the whole of what is indexed.

## Distributions

| population | depth | n | min | p10 | median | p90 | max |
|---|---|---|---|---|---|---|---|
| real | 1 | 244 | 0.6959 | 0.8167 | 0.8654 | 0.8999 | 0.9270 |
| real | 5 | 244 | 0.6610 | 0.7859 | 0.8243 | 0.8555 | 0.8838 |
| real | 20 | 244 | 0.6000 | 0.7353 | 0.7788 | 0.8136 | 0.8404 |
| real | 50 | 244 | 0.5083 | 0.6434 | 0.6835 | 0.7263 | 0.7781 |
| junk | 1 | 15 | 0.5464 | 0.5592 | 0.6086 | 0.6690 | 0.6789 |
| junk | 5 | 15 | 0.5258 | 0.5462 | 0.5794 | 0.6424 | 0.6577 |
| junk | 20 | 15 | 0.5053 | 0.5246 | 0.5465 | 0.6100 | 0.6335 |
| junk | 50 | 15 | 0.4568 | 0.4642 | 0.4975 | 0.5500 | 0.5844 |
| unanswerable | 1 | 50 | 0.7232 | 0.7941 | 0.8247 | 0.8529 | 0.8706 |
| unanswerable | 5 | 50 | 0.7158 | 0.7580 | 0.7919 | 0.8137 | 0.8397 |
| unanswerable | 20 | 50 | 0.6798 | 0.7264 | 0.7506 | 0.7847 | 0.7982 |
| unanswerable | 50 | 50 | 0.6178 | 0.6324 | 0.6702 | 0.6946 | 0.7077 |

## Lexical footing

0 of 15 junk queries and 0 of 244 real queries have no content word anywhere in the corpus. That gate is independent of the similarity floor and is what makes a genuinely empty result reachable.

## Proposal

**A corridor of 0.0170 exists** between the worst real question's best hit (0.6959) and the best junk question's (0.6789).

- `similarity_floor`: **0.687**, the midpoint of the corridor
- `similarity_margin`: **0.114**, the largest best-to-fifth spread over 244 real questions, so the margin never cuts a real question below five hits

## Unanswerable questions

50 of 50 unanswerable questions still clear the proposed floor of 0.687. They are the case the floor exists for, so this is the number to watch: a floor most of them clear separates junk from documentation and not answerable from unanswerable, and the lexical-footing gate cannot help here either, because these questions are written in the corpus's own words.

## Figures

- `figures/similarity-by-depth.svg`: median similarity at each depth, one line per population

## Decision

These numbers are what D-030's `similarity_floor` and `similarity_margin` are set from. They are not set from a fixture corpus: eight pages produce a similarity distribution that says nothing about four hundred.
