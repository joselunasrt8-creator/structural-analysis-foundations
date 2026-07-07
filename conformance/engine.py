"""Conformance engine orchestration."""

from __future__ import annotations

import importlib
from pathlib import Path

from .adapter_api import RepositoryAdapter
from .comparator import compare_semantics
from .fixture_loader import load_fixture
from .jsonutil import write_json
from .reporter import write_report


def _load_adapter(adapter_name: str, config: dict) -> RepositoryAdapter:
    module = importlib.import_module(f"conformance.adapters.{adapter_name}")
    return module.create_adapter(config)


def run_conformance(repo_root: Path, fixture_path: Path, artifact_root: Path) -> int:
    fixture = load_fixture(fixture_path, repo_root)
    artifact_dir = artifact_root / fixture.fixture_id
    adapter_name = fixture.adapter["name"].replace("-", "_")
    adapter = _load_adapter(adapter_name, fixture.adapter)
    evidence = adapter.run(fixture, artifact_dir)
    evidence_path = artifact_dir / "evidence.json"
    report_path = artifact_dir / "report.json"
    write_json(evidence_path, evidence)
    result = compare_semantics(fixture, evidence, str(evidence_path), str(report_path))
    write_report(result, report_path)
    print(result.explanation)
    print(f"evidence={evidence_path}")
    print(f"report={report_path}")
    return 0 if result.status == "PASS" else 1
