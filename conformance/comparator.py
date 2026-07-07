"""Semantic comparator for canonical evidence."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .models import CanonicalEvidence, CanonicalFixture, ConformanceResult


def _canonicalize(value: Any) -> Any:
    if isinstance(value, dict):
        return tuple((key, _canonicalize(val)) for key, val in sorted(value.items()))
    if isinstance(value, list):
        return tuple(sorted((_canonicalize(item) for item in value), key=repr))
    return value


def _equivalent(expected: Any, observed: Any) -> bool:
    return _canonicalize(expected) == _canonicalize(observed)


def compare_semantics(fixture: CanonicalFixture, evidence: CanonicalEvidence, evidence_path: str, report_path: str) -> ConformanceResult:
    expected = fixture.expected_semantics
    checks = [
        ("dependency_relations", expected.get("dependency_relations", []), evidence.dependency_relations),
        ("structural_invariants", expected.get("structural_invariants", {}), evidence.structural_invariants),
        ("canonical_outputs", expected.get("canonical_outputs", {}), evidence.canonical_outputs),
        ("required_diagnostics", expected.get("required_diagnostics", []), evidence.required_diagnostics),
        ("proof_obligations", expected.get("proof_obligations", {}), evidence.proof_obligations),
    ]
    diagnostics: list[dict[str, Any]] = []
    mismatches = []
    for name, expected_value, observed_value in checks:
        if _equivalent(expected_value, observed_value):
            diagnostics.append({"check": name, "result": "PASS", "explanation": "semantic values are equivalent"})
        else:
            mismatches.append(name)
            diagnostics.append(
                {
                    "check": name,
                    "result": "DRIFT",
                    "explanation": "semantic values differ after canonicalization",
                    "expected": expected_value,
                    "observed": observed_value,
                }
            )

    if evidence.research_object_id != fixture.research_object_id or evidence.fixture_id != fixture.fixture_id:
        diagnostics.append({"check": "identity", "result": "FAIL", "explanation": "evidence identity does not match fixture"})
        status = "FAIL"
    elif evidence.semantic_result == "UNKNOWN":
        diagnostics.append({"check": "adapter_result", "result": "UNKNOWN", "explanation": "adapter could not establish implementation semantics"})
        status = "UNKNOWN"
    elif mismatches:
        status = "DRIFT"
    elif evidence.semantic_result == "FAIL":
        status = "FAIL"
    else:
        status = "PASS"

    summary = Counter(item["result"] for item in diagnostics)
    explanation = f"{status}: {summary.get('PASS', 0)} semantic checks passed; {len(mismatches)} drift checks; deterministic fixture {fixture.fixture_id}."
    return ConformanceResult(status, fixture.fixture_id, fixture.research_object_id, evidence.repository, explanation, diagnostics, evidence_path, report_path)
