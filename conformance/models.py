"""Deterministic data models for conformance fixtures, evidence, and results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

SemanticResult = Literal["PASS", "DRIFT", "FAIL", "UNKNOWN", "UNOBSERVED"]
ResultStatus = Literal[
    "REFERENCE_PASS",
    "REFERENCE_FAIL",
    "CONFORMANCE_PASS",
    "CONFORMANCE_DRIFT",
    "CONFORMANCE_FAIL",
    "UNOBSERVED",
]
RunMode = Literal["reference", "external"]


@dataclass(frozen=True)
class CanonicalFixture:
    fixture_id: str
    research_object_id: str
    research_object_path: str
    description: str
    input: dict[str, Any]
    expected_semantics: dict[str, Any]
    adapter: dict[str, Any]
    deterministic_timestamp: str


@dataclass(frozen=True)
class CanonicalEvidence:
    repository: str
    repository_url: str
    commit_sha: str
    branch: str
    implementation_version: str
    research_object_id: str
    fixture_id: str
    observed_execution_timestamp: str
    canonical_projection_timestamp: str
    semantic_result: SemanticResult
    diagnostics: list[dict[str, Any]]
    generated_artifacts: list[dict[str, Any]]
    structural_metrics: dict[str, Any]
    provenance: dict[str, Any]
    dependency_relations: list[dict[str, Any]] = field(default_factory=list)
    structural_invariants: dict[str, Any] = field(default_factory=dict)
    canonical_outputs: dict[str, Any] = field(default_factory=dict)
    required_diagnostics: list[dict[str, Any]] = field(default_factory=list)
    proof_obligations: dict[str, Any] = field(default_factory=dict)
    execution_failure: bool = False
    schema_failure: bool = False
    run_mode: RunMode = "external"


@dataclass(frozen=True)
class ReplayResult:
    run_a_evidence_path: str
    run_b_evidence_path: str
    run_a_canonical_evidence_hash: str
    run_b_canonical_evidence_hash: str
    deterministic: bool
    explanation: str


@dataclass(frozen=True)
class ConformanceResult:
    status: ResultStatus
    fixture_id: str
    research_object_id: str
    repository: str
    explanation: str
    diagnostics: list[dict[str, Any]]
    evidence_path: str
    report_path: str
    fixture_hash: str
    evidence_hash: str
    replay: ReplayResult
