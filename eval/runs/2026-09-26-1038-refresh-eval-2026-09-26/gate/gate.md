# Refresh gate: pass

Candidate `2026-09-26-1038-refresh-eval-2026-09-26@2026-09-26` against baseline `2026-09-26-1038-refresh-eval-2026-09-26@2026-09-07`. Paired on 50 answerable and 10 refusal-expected questions present in both snapshots. A signal regresses when the questions that got worse outnumber the questions that got better by more than max(4, 5% of the population).

| signal | population | worse | better | net loss | threshold | baseline | candidate | verdict |
|---|---|---|---|---|---|---|---|---|
| retrieved | 50 | 0 | 0 | 0 | 4 | 1.00 | 1.00 | ok |
| cited | 50 | 2 | 3 | -1 | 4 | 0.92 | 0.94 | ok |
| refused | 10 | 0 | 0 | 0 | 4 | 0.90 | 0.90 | ok |
| correct | 50 | 2 | 4 | -2 | 4 | 0.84 | 0.86 | ok |

## cited

Worse:

- `dev-040`: True → False
- `dev-061`: True → False

Better:

- `dev-072`: False → True
- `dev-076`: False → True
- `dev-262`: False → True

## correct

Worse:

- `dev-061`: correct → partial
- `dev-125`: partial → wrong

Better:

- `dev-033`: partial → correct
- `dev-059`: partial → correct
- `dev-076`: partial → correct
- `dev-151`: wrong → partial
