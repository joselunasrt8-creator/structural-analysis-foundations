"""Conformance engine orchestration."""

from __future__ import annotations

import importlib
from dataclasses import replace
from pathlib import Path

from .adapter_api import RepositoryAdapter
from .comparator import compare_semantics
from .fixture_loader import load_fixture
from .jsonutil import canonical_hash, file_hash, to_plain, write_json, write_text
from .models import CanonicalEvidence, ReplayResult
from .reporter import write_report


def _load_adapter(adapter_name: str, config: dict) -> RepositoryAdapter:
    module = importlib.import_module(f"conformance.adapters.{adapter_name}")
    return module.create_adapter(config)


def _normalize_replay_paths(value):
    if isinstance(value, dict):
        return {key: ("<observed-runtime>" if key == "timestamp" else _normalize_replay_paths(item)) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_replay_paths(item) for item in value]
    if isinstance(value, str):
        return value.replace("/run-a/", "/<run>/").replace("/run-b/", "/<run>/")
    return value


def canonical_evidence_projection(evidence: CanonicalEvidence) -> dict:
    projected = _normalize_replay_paths(to_plain(evidence))
    projected["observed_execution_timestamp"] = "<observed-runtime>"
    projected["provenance"].pop("canonical_evidence_hash", None)
    return projected


def _run_once(adapter: RepositoryAdapter, fixture, artifact_dir: Path, label: str) -> tuple[CanonicalEvidence, str, Path]:
    run_dir = artifact_dir / label
    evidence = adapter.run(fixture, run_dir)
    evidence_hash = canonical_hash(canonical_evidence_projection(evidence))
    provenance = dict(evidence.provenance)
    provenance["canonical_evidence_hash"] = evidence_hash
    evidence = replace(evidence, provenance=provenance)
    evidence_path = run_dir / "evidence.json"
    write_json(evidence_path, evidence)
    write_text(run_dir / "evidence.sha256", evidence_hash)
    return evidence, evidence_hash, evidence_path


def run_conformance(repo_root: Path, fixture_path: Path, artifact_root: Path) -> int:
    fixture = load_fixture(fixture_path, repo_root)
    fixture_hash = canonical_hash(fixture)
    artifact_dir = artifact_root / fixture.fixture_id / fixture.adapter["name"]
    adapter_name = fixture.adapter["name"].replace("-", "_")
    adapter_config = dict(fixture.adapter)
    adapter_config.setdefault("repository_path", str(repo_root))
    adapter = _load_adapter(adapter_name, adapter_config)

    evidence_a, hash_a, path_a = _run_once(adapter, fixture, artifact_dir, "run-a")
    evidence_b, hash_b, path_b = _run_once(adapter, fixture, artifact_dir, "run-b")
    replay = ReplayResult(
        str(path_a),
        str(path_b),
        hash_a,
        hash_b,
        hash_a == hash_b,
        "canonical evidence hashes match" if hash_a == hash_b else "canonical evidence hashes differ across replay",
    )
    replay_path = artifact_dir / "replay.json"
    write_json(replay_path, replay)
    write_text(artifact_dir / "fixture.sha256", fixture_hash)
    evidence_path = artifact_dir / "evidence.json"
    report_path = artifact_dir / "report.json"
    write_json(evidence_path, evidence_a)
    write_text(artifact_dir / "evidence.sha256", hash_a)
    result = compare_semantics(fixture, evidence_a, str(evidence_path), str(report_path), fixture_hash, hash_a, replay)
    write_report(result, report_path)
    write_text(artifact_dir / "report.sha256", file_hash(report_path))
    print(result.explanation)
    print(f"evidence={evidence_path}")
    print(f"report={report_path}")
    print(f"replay={replay_path}")
    return 0 if result.status in {"REFERENCE_PASS", "CONFORMANCE_PASS", "UNOBSERVED"} else 1
