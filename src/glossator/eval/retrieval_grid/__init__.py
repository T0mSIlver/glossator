"""Every question through every retrieval configuration, with the record to prove it.

A grid row is a ``RetrievalConfig`` and nothing else, so what the evaluation
measures is exactly what a caller could set. Each row runs the whole dataset, and
each question keeps its ranked hits -- ids, urls, anchors, scores -- so any number
in the report can be traced back to the hits it was computed from (D-023).

Usage:
    python -m glossator.eval.retrieval_grid --dataset eval/dev.jsonl \\
        --grid eval/configs/retrieval-grid.yaml --name dev
"""
