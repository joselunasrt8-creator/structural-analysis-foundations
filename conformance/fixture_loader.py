"""Canonical fixture loading and validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .jsonutil import read_json
from .models import CanonicalFixture

_REQUIRED = {
    "fixture_id",
    "research_object_id",
    "research_object_path",
    "description",
    "input",
    "expected_semantics",
    "adapter",
    "deterministic_timestamp",
}


def load_fixture(path: Path, repo_root: Path) -> CanonicalFixture:
    data = read_json(path)
    missing = sorted(_REQUIRED - data.keys())
    if missing:
        raise ValueError(f"fixture {path} missing required keys: {', '.join(missing)}")

    research_object_path = repo_root / data["research_object_path"]
    research_object = read_json(research_object_path)
    if research_object.get("id") != data["research_object_id"]:
        raise ValueError(
            f"fixture {data['fixture_id']} targets {data['research_object_id']} but research object contains {research_object.get('id')}"
        )

    return CanonicalFixture(**{key: data[key] for key in _REQUIRED})
