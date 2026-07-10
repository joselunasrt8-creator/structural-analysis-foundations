#!/usr/bin/env python3
"""Validate every canonical fixture against its declared JSON Schema."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from conformance.fixture_schema_validator import format_issues, validate_all


def main() -> int:
    issues = validate_all(REPO_ROOT)
    if issues:
        print(format_issues(issues), file=sys.stderr)
        return 1
    print("canonical fixture schema validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
