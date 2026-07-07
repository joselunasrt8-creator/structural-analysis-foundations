"""Deterministic data models for conformance fixtures, evidence, and results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

SemanticResult = Literal["PASS", "DRIFT", "FAIL", "UNKNOWN"]


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
    implementation_version: str
    research_object_id: str
    fixture_id: str
    execution_timestamp: str
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


@dataclass(frozen=True)
class ConformanceResult:
    status: SemanticResult
    fixture_id: str
    research_object_id: str
    repository: str
    explanation: str
    diagnostics: list[dict[str, Any]]
    evidence_path: str
    report_path: str
