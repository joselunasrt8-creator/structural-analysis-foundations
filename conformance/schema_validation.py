"""Small local validator for the canonical evidence schema.

The schema intentionally allows extension only inside semantic/provenance maps and
artifact/diagnostic arrays so future adapters can add replay data without changing
core harness fields.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .jsonutil import read_json

REQUIRED = {
    "repository": str,
    "repository_url": str,
    "commit_sha": str,
    "branch": str,
    "implementation_version": str,
    "research_object_id": str,
    "fixture_id": str,
    "observed_execution_timestamp": str,
    "canonical_projection_timestamp": str,
    "semantic_result": str,
    "diagnostics": list,
    "generated_artifacts": list,
    "structural_metrics": dict,
    "provenance": dict,
}
OPTIONAL = {
    "dependency_relations": list,
    "structural_invariants": dict,
    "canonical_outputs": dict,
    "required_diagnostics": list,
    "proof_obligations": dict,
    "execution_failure": bool,
    "schema_failure": bool,
    "run_mode": str,
}
SEMANTIC_RESULTS = {"PASS", "DRIFT", "FAIL", "UNKNOWN", "UNOBSERVED"}
RUN_MODES = {"reference", "external"}


class EvidenceSchemaError(ValueError):
    """Raised when raw evidence does not satisfy the canonical evidence schema."""


def validate_evidence_dict(data: dict[str, Any]) -> None:
    allowed = set(REQUIRED) | set(OPTIONAL)
    extra = sorted(set(data) - allowed)
    if extra:
        raise EvidenceSchemaError(f"unexpected evidence fields: {', '.join(extra)}")
    for key, expected_type in REQUIRED.items():
        if key not in data:
            raise EvidenceSchemaError(f"missing required evidence field: {key}")
        if not isinstance(data[key], expected_type):
            raise EvidenceSchemaError(f"evidence field {key} must be {expected_type.__name__}")
    for key, expected_type in OPTIONAL.items():
        if key in data and not isinstance(data[key], expected_type):
            raise EvidenceSchemaError(f"evidence field {key} must be {expected_type.__name__}")
    if data["semantic_result"] not in SEMANTIC_RESULTS:
        raise EvidenceSchemaError(f"invalid semantic_result: {data['semantic_result']}")
    if data.get("run_mode", "external") not in RUN_MODES:
        raise EvidenceSchemaError(f"invalid run_mode: {data.get('run_mode')}")


def validate_evidence_file(path: Path) -> dict[str, Any]:
    data = read_json(path)
    validate_evidence_dict(data)
    return data
