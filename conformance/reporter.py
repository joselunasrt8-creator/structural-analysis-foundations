"""Deterministic conformance result reporting."""

from __future__ import annotations

from pathlib import Path

from .jsonutil import write_json
from .models import ConformanceResult


def write_report(result: ConformanceResult, path: Path) -> None:
    write_json(path, result)
