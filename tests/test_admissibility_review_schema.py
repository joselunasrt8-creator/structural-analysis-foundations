from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import ValidationError
from jsonschema.validators import validator_for

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas" / "admissibility_review.schema.json").read_text(encoding="utf-8"))
Validator = validator_for(SCHEMA)
Validator.check_schema(SCHEMA)
VALIDATOR = Validator(SCHEMA)

PACKAGE_PURPOSES = [
    "candidate_invariant_review",
    "bounded_formal_question",
    "counterexample_review",
    "vocabulary_alignment",
    "model_obligation",
    "indeterminate_evidence_review",
]
EMPIRICAL_OUTCOMES = ["supports", "indeterminate", "violates"]

ADMISSIBLE_PAIRS = {
    ("supports", "candidate_invariant_review"),
    ("supports", "bounded_formal_question"),
    ("supports", "vocabulary_alignment"),
    ("supports", "model_obligation"),
    ("indeterminate", "indeterminate_evidence_review"),
    ("indeterminate", "bounded_formal_question"),
    ("indeterminate", "vocabulary_alignment"),
    ("indeterminate", "model_obligation"),
    ("violates", "counterexample_review"),
}
ADMISSIBLE_WITH_LIMITATIONS_PAIRS = ADMISSIBLE_PAIRS | {("violates", "candidate_invariant_review")}

NORMATIVE_REQUIRED_FIELDS = [
    "schema_version",
    "admissibility_id",
    "package_reference",
    "reviewed_empirical_outcome",
    "package_purpose",
    "provenance_snapshot",
    "reviewed_artifact_references",
    "limitations_snapshot",
    "replication_status",
    "admissibility_result",
    "record_lifecycle",
    "review_timestamp",
    "review_authority",
    "admissibility_rationale",
    "reconsideration_conditions",
    "prior_record_reference",
    "superseding_record_reference",
]


def not_applicable(rationale: str = "not applicable for this review") -> dict[str, str]:
    return {"value": "not_applicable", "rationale": rationale}


def package_reference() -> dict[str, str]:
    return {
        "package_id": "B2.Package",
        "package_version": "v1.0",
        "provenance_source_type": "repository",
        "content_reference": "https://example.invalid/repo@abcdef",
        "content_digest": "abcdef",
        "hash_algorithm": "sha256",
        "canonicalization_method": "canonical JSON manifest digest",
        "producer_repository": "https://example.invalid/repo",
        "producer_commit": "abcdef",
    }


def base_record(
    *,
    outcome: str = "supports",
    purpose: str = "candidate_invariant_review",
    result: str = "admissible",
    lifecycle: str = "active",
) -> dict:
    limitations = {"assumptions": [], "known_limitations": [], "not_claimed": []}
    return {
        "schema_version": "v1",
        "admissibility_id": "saf:admissibility:geyduqrsfzigcy3lmftwknb2oyys4ma:0001",
        "package_reference": package_reference(),
        "reviewed_empirical_outcome": outcome,
        "package_purpose": purpose,
        "provenance_snapshot": {
            "reviewed_claim": "Producer-owned claim under review.",
            "requested_formalization_scope": "Bounded requested scope supplied by the producer.",
            "package_purpose": purpose,
            "reviewed_empirical_outcome": outcome,
            "artifact_references": [],
            "producer_commit": "abcdef",
            "package_version": "v1.0",
            "investigation_reference": not_applicable("no separate investigation reference"),
            "retained_classification_reference": not_applicable("no retained classification reference"),
            "cohort_conclusion_reference": not_applicable("no cohort conclusion reference"),
            "replication_status": "not_attempted",
            "limitations_snapshot": limitations,
        },
        "reviewed_artifact_references": [],
        "limitations_snapshot": limitations,
        "replication_status": "not_attempted",
        "admissibility_result": result,
        "record_lifecycle": lifecycle,
        "review_timestamp": "2026-07-16T00:00:00Z",
        "review_authority": {"authority_id": "consumer-review", "authority_type": "repository"},
        "admissibility_rationale": "The package is identifiable and bounded for this review state.",
        "reconsideration_conditions": [],
        "prior_record_reference": not_applicable("initial review record"),
        "superseding_record_reference": not_applicable("no superseding record is known"),
    }


def assert_valid(instance: dict) -> None:
    VALIDATOR.validate(instance)


def assert_invalid(instance: dict) -> None:
    with pytest.raises(ValidationError):
        VALIDATOR.validate(instance)


def test_schema_is_draft_2020_12_valid() -> None:
    Validator.check_schema(SCHEMA)


def test_identifier_0000_fails_and_0001_passes_syntactically() -> None:
    record = base_record()
    assert_valid(record)
    invalid = copy.deepcopy(record)
    invalid["admissibility_id"] = "saf:admissibility:geyduqrsfzigcy3lmftwknb2oyys4ma:0000"
    assert_invalid(invalid)


def test_withdrawn_and_invalidated_lifecycles_require_matching_links() -> None:
    withdrawn = base_record(lifecycle="withdrawn")
    assert_invalid(withdrawn)
    withdrawn["withdrawal_record_reference"] = "saf:admissibility:geyduqrsfzigcy3lmftwknb2oyys4ma:0002"
    assert_valid(withdrawn)

    invalidated = base_record(lifecycle="invalidated")
    assert_invalid(invalidated)
    invalidated["invalidation_record_reference"] = "saf:admissibility:geyduqrsfzigcy3lmftwknb2oyys4ma:0002"
    assert_valid(invalidated)


def test_active_records_prohibit_withdrawal_and_invalidation_links() -> None:
    for field in ["withdrawal_record_reference", "invalidation_record_reference"]:
        record = base_record(lifecycle="active")
        record[field] = "saf:admissibility:geyduqrsfzigcy3lmftwknb2oyys4ma:0002"
        assert_invalid(record)


def test_documentation_conformant_package_reference_needs_no_extra_digest_object() -> None:
    record = base_record()
    assert "digest" not in record["package_reference"]
    assert_valid(record)


def test_every_allowed_outcome_purpose_result_matrix_row_passes() -> None:
    for outcome, purpose in ADMISSIBLE_PAIRS:
        assert_valid(base_record(outcome=outcome, purpose=purpose, result="admissible"))
    for outcome, purpose in ADMISSIBLE_WITH_LIMITATIONS_PAIRS:
        assert_valid(base_record(outcome=outcome, purpose=purpose, result="admissible_with_limitations"))
    for outcome in EMPIRICAL_OUTCOMES:
        for purpose in PACKAGE_PURPOSES:
            assert_valid(base_record(outcome=outcome, purpose=purpose, result="inadmissible"))
            assert_valid(base_record(outcome=outcome, purpose=purpose, result="deferred"))


@pytest.mark.parametrize(
    ("outcome", "purpose", "result"),
    [
        ("supports", "counterexample_review", "admissible"),
        ("supports", "indeterminate_evidence_review", "admissible"),
        ("indeterminate", "candidate_invariant_review", "admissible"),
        ("indeterminate", "counterexample_review", "admissible"),
        ("violates", "candidate_invariant_review", "admissible"),
        ("violates", "bounded_formal_question", "admissible_with_limitations"),
    ],
)
def test_representative_prohibited_matrix_rows_fail(outcome: str, purpose: str, result: str) -> None:
    assert_invalid(base_record(outcome=outcome, purpose=purpose, result=result))


def test_provenance_snapshot_cannot_independently_identify_a_different_package() -> None:
    record = base_record()
    record["provenance_snapshot"]["package_reference"] = {
        **package_reference(),
        "package_id": "Different.Package",
    }
    assert_invalid(record)


def test_only_normative_admissibility_review_fields_are_required() -> None:
    assert SCHEMA["required"] == NORMATIVE_REQUIRED_FIELDS
    for non_model_field in [
        "producer_identity",
        "producer_repository",
        "producer_commit",
        "submitted_evidence",
        "review_rationale",
    ]:
        assert non_model_field not in SCHEMA["required"]
        assert non_model_field not in SCHEMA["properties"]


def test_result_and_lifecycle_remain_independent_axes() -> None:
    for result in ["admissible", "admissible_with_limitations", "inadmissible", "deferred"]:
        assert_valid(base_record(result=result, lifecycle="active"))
        superseded = base_record(result=result, lifecycle="superseded")
        assert_valid(superseded)
        withdrawn = base_record(result=result, lifecycle="withdrawn")
        withdrawn["withdrawal_record_reference"] = "saf:admissibility:geyduqrsfzigcy3lmftwknb2oyys4ma:0002"
        assert_valid(withdrawn)
        invalidated = base_record(result=result, lifecycle="invalidated")
        invalidated["invalidation_record_reference"] = "saf:admissibility:geyduqrsfzigcy3lmftwknb2oyys4ma:0002"
        assert_valid(invalidated)


def test_no_promotion_decision_schema_properties_are_introduced() -> None:
    forbidden_schema_properties = {
        "decision_id",
        "decision_result",
        "decision_rationale",
        "decision_timestamp",
        "decision_authority",
        "translation_record",
        "authorized_effects",
        "excluded_effects",
    }
    assert forbidden_schema_properties.isdisjoint(SCHEMA["properties"])
    assert "decisionRecordReference" not in SCHEMA["$defs"]
