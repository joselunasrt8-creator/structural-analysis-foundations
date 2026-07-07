"""CLI for the canonical conformance harness."""

from __future__ import annotations

import argparse
from pathlib import Path

from .engine import run_conformance


def main() -> int:
    parser = argparse.ArgumentParser(description="Run canonical research-object conformance.")
    parser.add_argument("--fixture", default="conformance/fixtures/dependency-predicate.fixture.json")
    parser.add_argument("--artifacts", default="conformance/artifacts")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    return run_conformance(repo_root, repo_root / args.fixture, repo_root / args.artifacts)


if __name__ == "__main__":
    raise SystemExit(main())
