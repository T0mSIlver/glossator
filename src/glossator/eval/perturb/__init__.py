"""Noisy rewordings of an evaluation subset, one kind of noise per question.

Every generated development question was written by a model from the section that
answers it, so it uses the documentation's own words and is well formed by
construction (D-020a). That is the distribution on which the shipped single pass
matched the search loop (D-035), and it is not the distribution a user types in.
This tool builds the other one: the same questions, the same gold sources and the
same reference answers, reworded into what a hurried, vague or mistaken user
would have asked, so the strategy decision can be re-tested out of distribution.

The rewording may not change the answer. A variant that asks something else, or
that carries a fact the original did not, is a different question with the wrong
gold attached, so every variant is checked by a second call and dropped and
recorded when it fails (D-023).

Usage:
    uv run python -m glossator.eval.perturb --dataset eval/dev.jsonl \\
        --out eval/dev-noisy.jsonl --n 120 --seed 0 --provider zai --model glm-5.3 \\
        --name dev-noisy
"""
