"""CLI: build the Mistral docs corpus and check it against the live site."""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

import structlog

from . import PINNED_REF
from .build import BuildError, build_corpus, format_summary
from .check import format_report, run_live_check
from .openapi import OPENAPI_URL
from .routes import fetch_search_docs
from .source import DEFAULT_CACHE_DIR, fetch_docs_repo, use_existing_checkout

DEFAULT_OUT_DIR = Path("corpus/mistral-docs")


class _Stderr:
    """Write to whatever `sys.stderr` is at call time.

    Binding the stream object once would keep writing to a stream the host has since
    replaced or closed, which turns a log line into an unrelated crash.
    """

    def write(self, text: str) -> int:
        return sys.stderr.write(text)

    def flush(self) -> None:
        sys.stderr.flush()


def _configure_logging(verbose: bool) -> None:
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.DEBUG if verbose else logging.INFO
        ),
        logger_factory=structlog.PrintLoggerFactory(_Stderr()),  # type: ignore[arg-type]
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="glossator.corpus.mistral_docs")
    parser.add_argument("-v", "--verbose", action="store_true")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="build the normalized corpus")
    build.add_argument("--ref", default=PINNED_REF, help="docs repo commit, tag or branch")
    build.add_argument("--out", type=Path, default=DEFAULT_OUT_DIR)
    build.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    build.add_argument(
        "--checkout",
        type=Path,
        help="use this existing docs working tree instead of cloning",
    )
    build.add_argument(
        "--search-docs",
        type=Path,
        help="local search-docs-en.json; fetched from the site when omitted",
    )
    build.add_argument(
        "--no-search-docs",
        action="store_true",
        help="skip the breadcrumb cross-check instead of fetching the site's index",
    )
    build.add_argument("--openapi-url", default=OPENAPI_URL)
    build.add_argument("--openapi-file", type=Path, help="use a local spec instead of fetching")
    build.add_argument("--refresh-openapi", action="store_true", help="ignore the cached spec")

    check = subparsers.add_parser("check", help="check the built corpus")
    check.add_argument("--corpus", type=Path, default=DEFAULT_OUT_DIR)
    check.add_argument("--live", action="store_true", help="check against docs.mistral.ai")
    check.add_argument("--no-anchors", action="store_true", help="check URLs only")
    check.add_argument("--concurrency", type=int, default=8)
    return parser


def _search_docs_path(args: argparse.Namespace) -> Path | None:
    if args.no_search_docs:
        return None
    if args.search_docs is not None:
        return Path(args.search_docs)
    return fetch_search_docs(args.cache_dir.parent / "search-docs", refresh=args.refresh_openapi)


def _run_build(args: argparse.Namespace) -> int:
    if args.checkout is not None:
        checkout = use_existing_checkout(args.checkout, args.ref)
    else:
        checkout = fetch_docs_repo(args.ref, cache_dir=args.cache_dir)
    try:
        summary = build_corpus(
            checkout,
            out_dir=args.out,
            cache_dir=args.cache_dir.parent / "openapi",
            search_docs=_search_docs_path(args),
            openapi_offline=args.openapi_file,
            openapi_url=args.openapi_url,
            refresh_openapi=args.refresh_openapi,
        )
    except BuildError as error:
        print(f"build failed: {error}")
        return 1
    print(format_summary(summary))
    return 1 if summary.residue_pages or summary.breadcrumb_mismatches else 0


def _run_check(args: argparse.Namespace) -> int:
    if not args.live:
        print("check requires --live; there is nothing to verify offline")
        return 2
    report = asyncio.run(
        run_live_check(
            args.corpus,
            check_anchors=not args.no_anchors,
            concurrency=args.concurrency,
        )
    )
    print(format_report(report))
    return 0 if report.passed else 1


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    _configure_logging(args.verbose)
    if args.command == "build":
        return _run_build(args)
    return _run_check(args)


if __name__ == "__main__":
    raise SystemExit(main())
