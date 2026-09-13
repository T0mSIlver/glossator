"""Command line: perturb a stratified subset of a dataset."""

from __future__ import annotations

import argparse
import asyncio
import json

from dotenv import load_dotenv

from glossator.eval.perturb.run import run


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Rewrite an evaluation subset into badly worded variants"
    )
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--n", type=int, default=120)
    parser.add_argument("--provider", choices=["zai", "mistral"], default="zai")
    parser.add_argument("--model", default="glm-5.3")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--concurrency", type=int, default=4)
    print(json.dumps(asyncio.run(run(parser.parse_args())), ensure_ascii=False))
