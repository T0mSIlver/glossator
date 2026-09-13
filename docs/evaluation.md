# Evaluation

Five questions decide whether the tool ships. Each has a number, a set, a model that produced it and a judge. `D-0xx` is the `DECISIONS.md` entry that took the decision. Run directories live under [`../eval/runs/`](../eval/runs/), one per run, with every model call recorded. The stage-by-stage table of every shipped choice is [`eval-status.md`](eval-status.md).

| Question | Number | Set | Produced by | Judged by | Entry |
|---|---|---|---|---|---|
| Does search return the section that states the fact? | section recall@1 0.73, 0.87 with the reranker | 294 generated questions | `mistral-embed`, Ministral 3 14B reranking | code | D-034 |
| Is the generated answer right, with a link that lands? | correctness 0.84 on held-out questions, 0.76 on real ones | 60 held-out, 85 mined | Ministral 3 14B | GLM 5.3, blind | D-035a, D-038 |
| Is a stronger generator better? | correctness unchanged within the interval, fabricated quotes halved | the same 288 prompts | Medium 3.5 on Mistral's API | GLM 5.3, blind | D-017c |
| Does an agent do as well with the tools as with a served answer? | 0.77 with the tools, 0.78 with the served answer at three times the latency | 30 questions | Claude Sonnet, low effort | GLM 5.3, blind | D-040b |
| Does it hold where it runs? | correctness 0.60, history rows 0.80, unanswerable rows 0.40 | 30 questions | Medium 3.5 through the Work Connector and the Skill | GLM 5.3, blind | D-049b |

## The question sets

Nothing reported was tuned on. `dev.jsonl` tuned retrieval and the answer prompt; the reporting sets are the held-out slice and the mined questions.

| Set | Count | Source | Role |
|---|---:|---|---|
| `dev.jsonl` | 294 | written by GLM 5.3 Flash from one page each, six question types | tuning only |
| `dev-fresh60.jsonl` | 60 | a balanced slice of `dev.jsonl` never used for tuning | held-out reporting |
| `mined.jsonl` | 85 | GitHub issues on the SDK and docs repositories, and agent transcripts, each checked by hand against the corpus | reporting on real questions |
| `demo.jsonl` | 30 | 25 mined questions on agents, MCP and the Vibe CLI, 5 written for the history tool | the Work measurement |

Secondary sets, used once each: 36 French translations (D-008b), 105 badly worded rewrites (D-035b), 84 more mined questions not yet checked by hand (D-038b).

## How a number is produced

Code checks what code can check: whether a cited URL and anchor is the expected one, whether every quoted span exists in the chunk it names, whether a link resolves on the live page. A model judges correctness, groundedness and citation relevance without seeing which configuration produced the answer.

The judge is GLM 5.3, chosen so that a Mistral model does not grade Mistral answers. Four judges were compared: GLM 5.3 Flash agrees with it at weighted kappa 0.87 over 492 answers, a local Qwen at 0.72, Ministral 3 14B is stricter than both (D-021a, D-021c). Against 40 answers labelled by hand, GLM 5.3 agreed on 35 and never accepted an answer the reader rejected, so judged correctness is a floor (D-021b).

Sixty questions give an interval of about ±0.09, thirty about ±0.17. Only larger gaps are read as differences.

## Retrieval

A grid ran the 294 tuning questions through 13 configurations: page chunks against section chunks, 128 against 1,024 embedding dimensions, four ranking weight sets, and a listwise reranker on or off (`2026-09-09-0136-dev-grid-v2`, D-034).

Section chunks with anchors won because page chunks cannot return a section link at all. Vector-heavy weights won over the starter's, whose phase-one vector weight was zero (D-012). The reranker was the largest single gain, section recall@1 0.732 to 0.873, and it stays in the answer path only: it is 91% of a search's latency and an agent reads several hits anyway (D-015b). 128 dimensions were not worse without the reranker, and 1,024 ships because the reranker was only run on 1,024.

## The answer path

`POST /ask` retrieves, reranks, assembles context, generates a structured answer with one marker per claim, verifies every quoted span, and refuses when nothing verifies.

| Set | Correctness | Correct refusal | Reference URL cited | Run |
|---|---:|---:|---:|---|
| tuned 60 | 0.93 | 0.92 | 0.82 | `2026-09-09-0312-dev60-rerank` |
| held-out 60 | 0.84 | 0.87 | 0.84 | `2026-09-09-1211-fresh60-shipped` |
| mined 85 | 0.76 | 0.92 | 0.86 | `2026-09-09-1253-mined-shipped` |

Ministral 3 14B generated these, because the key had no Medium 3.5 quota until 12 September. Replaying the same 288 prompts on Medium 3.5 through Mistral's API moved correctness by −3, −2, −3 and +1 points on the four sets, all inside the interval, and halved fabricated quotes per answer, 0.40 to 0.59 down to 0.17 to 0.19 (D-017c). The generator is not the ceiling.

The failure analysis over 575 answers puts 82 of 177 failures on generation, 55 of them with the right passage quoted; retrieval misses are 1% to 3% on well-written questions and context assembly lost nothing (D-042). [`failure-classes.md`](failure-classes.md) names the four classes still failing, with question ids and the fix for each.

Two smaller findings decided defaults. A single pass over reranked retrieval scores within two points of a search loop at a third of the latency and a fifth of the cost, so single pass is the default (D-035). Rendering a French question in English for retrieval raises correctness on 36 French questions from 0.75 to 0.94 (D-008b). Badly worded questions cost 19 points; a query rewrite recovers 4 and loses 5 on clean questions, so it stays off (D-035b).

## The agent path

Two agents answered the same 30 questions blind, with no mention of the server in their prompts (`consumer-eval-v2`, D-040b). Sonnet at low effort scored 0.50 from memory, 0.77 with search and read, and 0.78 when it asked the server for a finished answer, at 74 seconds against 21. Its links resolved 0.92 of the time with the tools against 0.35 without. GPT, which carries its own web search, never called the server in 60 cells: a consumer with a competing habit needs to be told the server exists, which is what the Work Skill does. This run decided that the agent writes the answer and the served answer stays as the API baseline (D-044).

The Work measurement drives the same server-side loop Work runs: Medium 3.5 at high reasoning, the Skill as instructions, the Connector as the only tool, one conversation per question (D-049). Three runs on `demo.jsonl`:

| Run | Correctness | History rows | Unanswerable rows | Characters per read | Entry |
|---|---:|---:|---:|---:|---|
| first, 12 Sep | 0.60 | 0.80 | 0.20 | 7,374 | D-049a |
| reads contained | 0.62 | 0.90 | 0.30 | 4,735 | D-050a |
| shipped server, 13 Sep | 0.60 | 0.80 | 0.40 | 5,410 | D-049b |

The history rows answer through the tool in one or two calls. The unanswerable rows are where the model fills a gap the documentation leaves; the stop rules in the Skill halved the searches on those questions and the listing form gives the model a proof of absence (D-044a, D-046).

## The time axis

Eight snapshots of the documentation repository, one every two weeks from 1 June 2026, are labelled for which questions each can answer (`2026-09-09-1929-snapshot-labels`, D-041a). The labels found the August rename of `/studio-api` to `/studio`: 300 sections moved unchanged. The history tool reads those snapshots and a precomputed changelog; the five history rows of the demo set are answered as a bound between two dates, never a day (D-048).

## Not measured

Mistral Small 4 is the shipped reranker default and has never run in an evaluation; every reranker number names Ministral 3 14B. No consumer arm had grep over the docs repository. The 84 second-pass mined questions are not checked by hand. Whether a text-fragment link survives a click from Work is open (D-047c).

## Reproduce

```bash
make eval-retrieval dataset=eval/dev.jsonl name=grid          # the retrieval grid
make eval-answers dataset=eval/dev-fresh60.jsonl name=fresh    # the answer path
make failures runs="eval/runs/<run> ..."                       # the failure analysis
uv run python -m glossator.eval.work_proxy run --dataset eval/demo.jsonl --name demo   # the Work measurement
```

A run directory holds the questions, every retrieved hit, every prompt and response, the citations, token usage, latency, cost and a README with its tables (D-023). Ledgers before 9 September omit the reranker's calls and embeddings, so their totals are a lower bound (D-023b).
