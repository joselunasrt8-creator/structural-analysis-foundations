"""Semantic comparator for canonical evidence."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .models import CanonicalEvidence, CanonicalFixture, ConformanceResult, ReplayResult


def _canonicalize(value: Any) -> Any:
    if isinstance(value, dict):
        return tuple((key, _canonicalize(val)) for key, val in sorted(value.items()))
    if isinstance(value, list):
        return tuple(sorted((_canonicalize(item) for item in value), key=repr))
    return value


def _equivalent(expected: Any, observed: Any) -> bool:
    return _canonicalize(expected) == _canonicalize(observed)


def _status(run_mode: str, terminal: str) -> str:
    if terminal == "UNOBSERVED":
        return "UNOBSERVED"
    if run_mode == "reference":
        return "REFERENCE_PASS" if terminal == "PASS" else "REFERENCE_FAIL"
    return {
        "PASS": "CONFORMANCE_PASS",
        "DRIFT": "CONFORMANCE_DRIFT",
        "FAIL": "CONFORMANCE_FAIL",
        "UNKNOWN": "UNOBSERVED",
    }[terminal]


def compare_semantics(
    fixture: CanonicalFixture,
    evidence: CanonicalEvidence,
    evidence_path: str,
    report_path: str,
    fixture_hash: str,
    evidence_hash: str,
    replay: ReplayResult,
) -> ConformanceResult:
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
    should_compare_semantics = evidence.semantic_result not in {"UNOBSERVED", "UNKNOWN", "FAIL"} and not evidence.execution_failure and not evidence.schema_failure
    if should_compare_semantics:
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
        terminal = "FAIL"
    elif evidence.execution_failure:
        diagnostics.append({"check": "execution", "result": "FAIL", "explanation": "implementation execution failed"})
        terminal = "FAIL"
    elif evidence.schema_failure:
        diagnostics.append({"check": "schema", "result": "FAIL", "explanation": "raw evidence schema validation failed"})
        terminal = "FAIL"
    elif not replay.deterministic:
        diagnostics.append({"check": "replay", "result": "FAIL", "explanation": replay.explanation})
        terminal = "FAIL"
    elif evidence.semantic_result == "UNOBSERVED":
        diagnostics.append({"check": "observation", "result": "UNOBSERVED", "explanation": "external implementation was not observed"})
        terminal = "UNOBSERVED"
    elif evidence.semantic_result == "UNKNOWN":
        diagnostics.append({"check": "adapter_result", "result": "UNKNOWN", "explanation": "adapter could not establish implementation semantics"})
        terminal = "UNKNOWN"
    elif evidence.semantic_result == "FAIL":
        diagnostics.append({"check": "adapter_result", "result": "FAIL", "explanation": "implementation reported semantic failure"})
        terminal = "FAIL"
    elif mismatches:
        terminal = "DRIFT"
    else:
        terminal = "PASS"

    status = _status(evidence.run_mode, terminal)
    summary = Counter(item["result"] for item in diagnostics)
    explanation = f"{status}: {summary.get('PASS', 0)} semantic checks passed; {len(mismatches)} drift checks; replay deterministic={replay.deterministic}."
    return ConformanceResult(status, fixture.fixture_id, fixture.research_object_id, evidence.repository, explanation, diagnostics, evidence_path, report_path, fixture_hash, evidence_hash, replay)
