from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import ValidationError
from jsonschema.validators import validator_for

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas" / "promotion_decision.schema.json").read_text(encoding="utf-8"))
Validator = validator_for(SCHEMA)
Validator.check_schema(SCHEMA)
VALIDATOR = Validator(SCHEMA)

EXCLUDED_EFFECTS = [
    "canonical_research_object_publication",
    "canonical_fixture_creation",
    "implementation_conformance_claim",
    "producer_evidence_mutation",
    "schema_creation",
    "validator_creation",
    "automation_creation",
    "cross_repository_synchronization",
]


def not_applicable(rationale: str = "not applicable for this decision") -> dict[str, str]:
    return {"value": "not_applicable", "rationale": rationale}


def package_reference(source_type: str = "repository") -> dict[str, str]:
    base = {
        "package_id": "B2.Package",
        "package_version": "v1.0",
        "provenance_source_type": source_type,
        "content_reference": "immutable reference",
        "content_digest": "abcdef",
        "hash_algorithm": "sha256",
        "canonicalization_method": "canonical JSON manifest digest",
    }
    if source_type == "repository":
        return {**base, "producer_repository": "https://example.invalid/repo", "producer_commit": "abcdef"}
    if source_type in {"release_artifact", "archive", "object_store"}:
        return {**base, "producer_artifact_locator": "artifact://example", "producer_artifact_revision": "v1"}
    if source_type == "content_address":
        return {**base, "content_address": "sha256:abcdef"}
    raise ValueError(source_type)


def translation_record() -> dict:
    return {
        "producer_claim": "Producer-owned claim under review.",
        "accepted_formalization_scope": "Bounded accepted scope.",
        "excluded_formalization_scope": ["No canonical object publication."],
        "translation_rationale": "The accepted scope is bounded and does not broaden producer evidence.",
        "assumptions": ["Producer package remains immutable."],
        "constraints": ["No implementation conformance claim."],
        "permitted_evidence_references": ["artifact:1"],
        "preserved_limitations": ["Indeterminate empirical outcome is preserved."],
        "non_authorized_downstream_effects": ["No canonical fixture creation."],
    }


def base_record(*, result: str = "accepted_for_formalization", lifecycle: str = "active") -> dict:
    record = {
        "schema_version": "v1",
        "decision_id": "saf:decision:geyduqrsfzigcy3lmftwknb2oyys4ma:0001",
        "admissibility_id": "saf:admissibility:geyduqrsfzigcy3lmftwknb2oyys4ma:0001",
        "package_reference": package_reference(),
        "decision_result": result,
        "record_lifecycle": lifecycle,
        "decision_rationale": "The decision preserves the documented promotion boundary.",
        "decision_timestamp": "2026-07-16T00:00:00Z",
        "decision_authority": {"authority_id": "consumer-decision", "authority_type": "repository"},
        "translation_record_status": "provided",
        "authorized_effects": ["bounded_formalization"],
        "excluded_effects": list(EXCLUDED_EFFECTS),
        "preserved_limitations": ["Known limitations remain non-canonical."],
        "reconsideration_conditions": ["Producer submits a new immutable package."],
        "prior_record_reference": not_applicable("initial decision record"),
        "superseding_record_reference": not_applicable("no superseding record is known"),
        "translation_record": translation_record(),
    }
    if result in {"rejected", "deferred"}:
        record.pop("translation_record")
        record["translation_record_status"] = not_applicable("no accepted translation scope exists")
    return record


def assert_valid(instance: dict) -> None:
    VALIDATOR.validate(instance)


def assert_invalid(instance: dict) -> None:
    with pytest.raises(ValidationError):
        VALIDATOR.validate(instance)


def test_schema_is_draft_2020_12_valid() -> None:
    Validator.check_schema(SCHEMA)


def test_decision_id_rejects_0000_and_accepts_0001() -> None:
    assert_valid(base_record())
    record = base_record()
    record["decision_id"] = "saf:decision:geyduqrsfzigcy3lmftwknb2oyys4ma:0000"
    assert_invalid(record)


@pytest.mark.parametrize("result", ["accepted_for_formalization", "accepted_with_constraints"])
def test_accepted_decision_without_translation_record_fails(result: str) -> None:
    record = base_record(result=result)
    record.pop("translation_record")
    assert_invalid(record)


def test_accepted_with_constraints_without_constraints_fails() -> None:
    record = base_record(result="accepted_with_constraints")
    record["translation_record"].pop("constraints")
    assert_invalid(record)


def test_accepted_with_constraints_without_excluded_scope_fails() -> None:
    record = base_record(result="accepted_with_constraints")
    record["translation_record"].pop("excluded_formalization_scope")
    assert_invalid(record)


@pytest.mark.parametrize("result", ["rejected", "deferred"])
def test_rejected_and_deferred_decisions_containing_translation_record_fail(result: str) -> None:
    record = base_record(result=result)
    record["translation_record"] = translation_record()
    assert_invalid(record)


def test_only_bounded_formalization_is_accepted() -> None:
    record = base_record()
    record["authorized_effects"] = ["bounded_formalization", "implementation_conformance_claim"]
    assert_invalid(record)


def test_undocumented_authority_effects_fail() -> None:
    record = base_record()
    record["excluded_effects"].append("producer_authority_creation")
    assert_invalid(record)


def test_withdrawn_records_require_withdrawal_linkage() -> None:
    record = base_record(lifecycle="withdrawn")
    assert_invalid(record)
    record["withdrawal_record_reference"] = "saf:decision:geyduqrsfzigcy3lmftwknb2oyys4ma:0002"
    record["withdrawal_reason"] = "Producer package was withdrawn."
    assert_valid(record)


def test_invalidated_records_require_invalidation_linkage() -> None:
    record = base_record(lifecycle="invalidated")
    assert_invalid(record)
    record["invalidation_record_reference"] = "saf:decision:geyduqrsfzigcy3lmftwknb2oyys4ma:0002"
    record["invalidity_reason"] = "Content digest was shown incorrect."
    assert_valid(record)


def test_active_records_prohibit_lifecycle_action_links() -> None:
    for field, value in [
        ("withdrawal_record_reference", "saf:decision:geyduqrsfzigcy3lmftwknb2oyys4ma:0002"),
        ("invalidation_record_reference", "saf:decision:geyduqrsfzigcy3lmftwknb2oyys4ma:0002"),
        ("withdrawal_reason", "withdrawn"),
        ("invalidity_reason", "invalid"),
    ]:
        record = base_record(lifecycle="active")
        record[field] = value
        assert_invalid(record)


def test_lifecycle_and_result_remain_independent() -> None:
    for result in ["accepted_for_formalization", "accepted_with_constraints", "rejected", "deferred"]:
        assert_valid(base_record(result=result, lifecycle="active"))
        assert_valid(base_record(result=result, lifecycle="superseded"))
        withdrawn = base_record(result=result, lifecycle="withdrawn")
        withdrawn["withdrawal_record_reference"] = "saf:decision:geyduqrsfzigcy3lmftwknb2oyys4ma:0002"
        withdrawn["withdrawal_reason"] = "Producer package was withdrawn."
        assert_valid(withdrawn)
        invalidated = base_record(result=result, lifecycle="invalidated")
        invalidated["invalidation_record_reference"] = "saf:decision:geyduqrsfzigcy3lmftwknb2oyys4ma:0002"
        invalidated["invalidity_reason"] = "Content digest was shown incorrect."
        assert_valid(invalidated)


@pytest.mark.parametrize("source_type", ["repository", "archive", "object_store"])
def test_documented_provenance_branches_validate(source_type: str) -> None:
    record = base_record()
    record["package_reference"] = package_reference(source_type)
    assert_valid(record)


def test_contradictory_provenance_branches_fail() -> None:
    record = base_record()
    record["package_reference"]["producer_artifact_locator"] = "artifact://example"
    record["package_reference"]["producer_artifact_revision"] = "v1"
    assert_invalid(record)


def test_schema_introduces_no_promotion_decision_authority_beyond_contract() -> None:
    assert SCHEMA["properties"]["decision_result"]["enum"] == [
        "accepted_for_formalization",
        "accepted_with_constraints",
        "rejected",
        "deferred",
    ]
    assert SCHEMA["properties"]["record_lifecycle"]["enum"] == ["active", "superseded", "withdrawn", "invalidated"]
    assert SCHEMA["properties"]["authorized_effects"]["items"] == {"type": "string", "const": "bounded_formalization"}
    for non_model_field in [
        "canonical_research_object",
        "canonical_fixture",
        "implementation_conformance",
        "producer_authority",
        "validator_registry",
        "automation_hook",
    ]:
        assert non_model_field not in SCHEMA["properties"]
