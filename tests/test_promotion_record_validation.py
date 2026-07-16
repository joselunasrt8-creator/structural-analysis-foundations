from __future__ import annotations

import copy
import json
import shutil
import socket
import subprocess
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from tools.validate_promotion_records import ROOT, discover_paths, main, package_identity_token, validate


FIXTURES = ROOT / "tests" / "fixtures" / "promotion_records"


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def repository(tmp_path: Path) -> Path:
    root = tmp_path / "repository"
    (root / "schemas").mkdir(parents=True)
    for name in ("admissibility_review.schema.json", "promotion_decision.schema.json"):
        shutil.copyfile(ROOT / "schemas" / name, root / "schemas" / name)
    return root


def write(root: Path, relative: str, value: dict) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return path


def validate_values(tmp_path: Path, *named_values: tuple[str, dict]) -> tuple[int, list[str]]:
    root = repository(tmp_path)
    paths = [write(root, name, value) for name, value in named_values]
    return validate(root, paths)


def assert_error(errors: list[str], fragment: str) -> None:
    assert any(fragment in error for error in errors), "\n".join(errors)


def linked_pair(*, limited: bool = False, decision_name: str = "valid_accepted_decision.json") -> tuple[dict, dict]:
    review = load("valid_limited_review.json" if limited else "valid_admissible_review.json")
    decision = load(decision_name)
    return review, decision


def set_ordinal(record: dict, field: str, ordinal: int) -> None:
    record[field] = record[field][:-4] + f"{ordinal:04d}"


@pytest.mark.parametrize("name", ["admissibility_review.schema.json", "promotion_decision.schema.json"])
def test_schemas_meta_validate(name: str) -> None:
    Draft202012Validator.check_schema(json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8")))


def test_identifier_derivation_examples() -> None:
    assert package_identity_token("B2.Package", "v1.0") == "geyduqrsfzigcy3lmftwknb2oyys4ma"
    assert package_identity_token("pkg:Alpha/β", "Release 2026-07-16") == "gezdu4dlm45ec3dqnbqs7tvsge4duutfnrswc43feazdamrwfuydoljrgy"


@pytest.mark.parametrize(
    ("review_name", "decision_name"),
    [
        ("valid_admissible_review.json", "valid_accepted_decision.json"),
        ("valid_limited_review.json", "valid_constrained_decision.json"),
        ("valid_admissible_review.json", "valid_rejected_decision.json"),
        ("valid_admissible_review.json", "valid_deferred_decision.json"),
    ],
)
def test_positive_review_and_decision_fixtures_pass(tmp_path: Path, review_name: str, decision_name: str) -> None:
    count, errors = validate_values(tmp_path, ("review.json", load(review_name)), ("decision.json", load(decision_name)))
    assert count == 2
    assert errors == []


@pytest.mark.parametrize(
    ("mutation", "fragment"),
    [
        (lambda review: review.pop("review_authority"), "schema:"),
        (lambda review: review.__setitem__("schema_version", "v2"), "unsupported admissibility schema version"),
        (lambda review: review.__setitem__("admissibility_id", review["admissibility_id"].replace("geydu", "geydv")), "identifier package token"),
        (lambda review: review.__setitem__("admissibility_id", review["admissibility_id"][:-4] + "0000"), "0000"),
        (lambda review: review["provenance_snapshot"].__setitem__("package_version", "v2"), "must exactly equal $.package_version"),
        (lambda review: review.__setitem__("record_lifecycle", "admissible"), "schema:"),
        (lambda review: (review.__setitem__("reviewed_empirical_outcome", "indeterminate"), review["provenance_snapshot"].__setitem__("reviewed_empirical_outcome", "indeterminate")), "schema:"),
    ],
)
def test_invalid_admissibility_mutations_fail(tmp_path: Path, mutation, fragment: str) -> None:
    review = load("valid_admissible_review.json")
    mutation(review)
    _, errors = validate_values(tmp_path, ("review.json", review))
    assert_error(errors, fragment)


def test_duplicate_identifier_fails_but_duplicate_path_is_deduplicated(tmp_path: Path) -> None:
    review = load("valid_admissible_review.json")
    _, errors = validate_values(tmp_path, ("a.json", review), ("b.json", review))
    assert_error(errors, "duplicate consumer identifier")
    root = repository(tmp_path / "second")
    path = write(root, "one.json", review)
    count, errors = validate(root, [path, path, path.parent / "." / path.name])
    assert (count, errors) == (1, [])


def test_package_reference_and_link_eligibility_failures(tmp_path: Path) -> None:
    review, decision = linked_pair()
    decision["package_reference"]["content_digest"] = "different"
    _, errors = validate_values(tmp_path, ("review.json", review), ("decision.json", decision))
    assert_error(errors, "must exactly equal the linked")

    _, errors = validate_values(tmp_path / "missing", ("decision.json", load("valid_accepted_decision.json")))
    assert_error(errors, "exactly one discovered Admissibility Review")


@pytest.mark.parametrize("result", ["inadmissible", "deferred"])
def test_ineligible_review_blocks_decision(tmp_path: Path, result: str) -> None:
    review, decision = linked_pair()
    review["admissibility_result"] = result
    _, errors = validate_values(tmp_path, ("review.json", review), ("decision.json", decision))
    assert_error(errors, "is not eligible")


@pytest.mark.parametrize(
    ("mutation", "fragment"),
    [
        (lambda decision: decision.pop("translation_record"), "schema:"),
        (lambda decision: decision["translation_record"].__setitem__("producer_claim", "Broadened claim"), "must exactly preserve"),
        (lambda decision: decision.__setitem__("authorized_effects", []), "schema:"),
        (lambda decision: decision["excluded_effects"].remove("theorem_validation"), "mandatory excluded-effect set"),
        (lambda decision: decision.__setitem__("record_lifecycle", "accepted_for_formalization"), "schema:"),
    ],
)
def test_invalid_decision_mutations_fail(tmp_path: Path, mutation, fragment: str) -> None:
    review, decision = linked_pair()
    mutation(decision)
    _, errors = validate_values(tmp_path, ("review.json", review), ("decision.json", decision))
    assert_error(errors, fragment)


def test_malformed_excluded_effects_returns_errors_without_traceback(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = repository(tmp_path)
    review, decision = linked_pair()
    decision["excluded_effects"] = [{}]
    review_path = write(root, "review.json", review)
    decision_path = write(root, "decision.json", decision)
    assert main(["--root", str(root), str(review_path), str(decision_path)]) == 1
    output = capsys.readouterr().out
    assert "schema:" in output
    assert "Traceback" not in output


@pytest.mark.parametrize(("fixture", "field"), [("valid_admissible_review.json", "review_timestamp"), ("valid_accepted_decision.json", "decision_timestamp")])
def test_invalid_timestamps_fail_format_validation(tmp_path: Path, fixture: str, field: str) -> None:
    value = load(fixture)
    value[field] = "not-a-date-time"
    _, errors = validate_values(tmp_path, ("record.json", value))
    assert_error(errors, "is not a 'date-time'")


def test_constrained_decision_requires_constraints_exclusions_and_limitations(tmp_path: Path) -> None:
    for field in ("constraints", "excluded_formalization_scope"):
        review, decision = linked_pair(limited=True, decision_name="valid_constrained_decision.json")
        decision["translation_record"][field] = []
        _, errors = validate_values(tmp_path / field, ("review.json", review), ("decision.json", decision))
        assert_error(errors, "must be non-empty")
    review, decision = linked_pair(limited=True, decision_name="valid_constrained_decision.json")
    decision["preserved_limitations"] = []
    decision["translation_record"]["preserved_limitations"] = []
    _, errors = validate_values(tmp_path / "limitations", ("review.json", review), ("decision.json", decision))
    assert_error(errors, "must preserve every linked review limitation")


@pytest.mark.parametrize("result", ["rejected", "deferred"])
def test_nonaccepted_decisions_cannot_authorize_bounded_formalization(tmp_path: Path, result: str) -> None:
    review = load("valid_admissible_review.json")
    decision = load(f"valid_{result}_decision.json")
    decision["authorized_effects"] = ["bounded_formalization"]
    _, errors = validate_values(tmp_path, ("review.json", review), ("decision.json", decision))
    assert_error(errors, "schema:")


def lifecycle_pair(kind: str, action: str) -> tuple[dict, dict]:
    if kind == "admissibility":
        earlier = load("valid_admissible_review.json")
        id_field = "admissibility_id"
    else:
        earlier = load("valid_rejected_decision.json")
        id_field = "decision_id"
    later = copy.deepcopy(earlier)
    set_ordinal(later, id_field, 2)
    later["prior_record_reference"] = earlier[id_field]
    if action == "superseded":
        earlier["record_lifecycle"] = "superseded"
        earlier["superseding_record_reference"] = later[id_field]
    elif action == "withdrawn":
        earlier[f"{action[:-1]}al_record_reference"] = later[id_field]
        later["record_lifecycle"] = action
        later["superseding_record_reference"] = {"value": "not_applicable", "rationale": "withdrawal is not supersession"}
        if kind == "decision":
            later["withdrawal_record_reference"] = later[id_field]  # removed below; schema needs link on withdrawn record
            later["withdrawal_reason"] = "Package withdrawn."
    else:
        earlier["invalidation_record_reference"] = later[id_field]
        later["record_lifecycle"] = action
        later["superseding_record_reference"] = {"value": "not_applicable", "rationale": "invalidation is not supersession"}
        if kind == "decision":
            later["invalidation_record_reference"] = later[id_field]
            later["invalidity_reason"] = "Digest invalid."
    return earlier, later


def test_valid_superseded_lineage_and_unknown_later_representation(tmp_path: Path) -> None:
    earlier, later = lifecycle_pair("admissibility", "superseded")
    _, errors = validate_values(tmp_path, ("earlier.json", earlier), ("later.json", later))
    assert errors == []
    earlier["superseding_record_reference"] = {"value": "not_applicable", "rationale": "later identifier unknown"}
    _, errors = validate_values(tmp_path / "unknown", ("earlier.json", earlier))
    assert errors == []


def test_withdrawal_and_invalidation_linkage_and_later_ordinals(tmp_path: Path) -> None:
    for action, field in (("withdrawn", "withdrawal_record_reference"), ("invalidated", "invalidation_record_reference")):
        for target_lifecycle in ("active", "superseded"):
            earlier = load("valid_admissible_review.json")
            later = copy.deepcopy(earlier)
            set_ordinal(later, "admissibility_id", 2)
            later["record_lifecycle"] = target_lifecycle
            earlier["record_lifecycle"] = action
            earlier[field] = later["admissibility_id"]
            _, errors = validate_values(tmp_path / action / target_lifecycle, ("earlier.json", earlier), ("later.json", later))
            assert_error(errors, f"target record lifecycle must be {action}")


def test_cross_type_prior_backward_and_wrong_token_links_fail(tmp_path: Path) -> None:
    review, decision = linked_pair(decision_name="valid_rejected_decision.json")
    decision["prior_record_reference"] = review["admissibility_id"]
    _, errors = validate_values(tmp_path, ("review.json", review), ("decision.json", decision))
    assert_error(errors, "same record type")
    first, second = lifecycle_pair("admissibility", "superseded")
    set_ordinal(first, "admissibility_id", 3)
    second["prior_record_reference"] = first["admissibility_id"]
    _, errors = validate_values(tmp_path / "backward", ("first.json", first), ("second.json", second))
    assert_error(errors, "immediately following ordinal")


def test_missing_withdrawal_and_invalidation_records_fail(tmp_path: Path) -> None:
    for lifecycle, field in (("withdrawn", "withdrawal_record_reference"), ("invalidated", "invalidation_record_reference")):
        review = load("valid_admissible_review.json")
        review["record_lifecycle"] = lifecycle
        review[field] = review["admissibility_id"][:-4] + "0002"
        _, errors = validate_values(tmp_path / lifecycle, ("review.json", review))
        assert_error(errors, "exactly one discovered record")


def test_active_record_with_known_superseding_reference_fails(tmp_path: Path) -> None:
    review = load("valid_admissible_review.json")
    review["superseding_record_reference"] = review["admissibility_id"][:-4] + "0002"
    _, errors = validate_values(tmp_path, ("review.json", review))
    assert_error(errors, "active records cannot contain")


def test_lifecycle_link_with_different_package_token_fails(tmp_path: Path) -> None:
    earlier = load("valid_admissible_review.json")
    later = copy.deepcopy(earlier)
    later["package_reference"]["package_id"] = "Other.Package"
    token = package_identity_token("Other.Package", later["package_reference"]["package_version"])
    later["admissibility_id"] = f"saf:admissibility:{token}:0001"
    later["prior_record_reference"] = earlier["admissibility_id"]
    earlier["record_lifecycle"] = "superseded"
    earlier["superseding_record_reference"] = later["admissibility_id"]
    _, errors = validate_values(tmp_path, ("earlier.json", earlier), ("later.json", later))
    assert_error(errors, "cross-token linkage must preserve")


def test_cross_version_supersession_is_allowed_for_same_package_id(tmp_path: Path) -> None:
    earlier = load("valid_admissible_review.json")
    later = copy.deepcopy(earlier)
    later["package_reference"]["package_version"] = "v2.0"
    later["provenance_snapshot"]["package_version"] = "v2.0"
    token = package_identity_token("B2.Package", "v2.0")
    later["admissibility_id"] = f"saf:admissibility:{token}:0001"
    later["prior_record_reference"] = earlier["admissibility_id"]
    earlier["record_lifecycle"] = "superseded"
    earlier["superseding_record_reference"] = later["admissibility_id"]
    _, errors = validate_values(tmp_path, ("earlier.json", earlier), ("later.json", later))
    assert errors == []


def test_sequence_allocation_and_immediate_prior_are_enforced(tmp_path: Path) -> None:
    first = load("valid_admissible_review.json")
    set_ordinal(first, "admissibility_id", 42)
    _, errors = validate_values(tmp_path / "start", ("first.json", first))
    assert_error(errors, "must begin at ordinal 0001")

    first = load("valid_admissible_review.json")
    third = copy.deepcopy(first)
    set_ordinal(third, "admissibility_id", 3)
    third["prior_record_reference"] = first["admissibility_id"]
    first["record_lifecycle"] = "superseded"
    first["superseding_record_reference"] = third["admissibility_id"]
    _, errors = validate_values(tmp_path / "gap", ("first.json", first), ("third.json", third))
    assert_error(errors, "immediately preceding ordinal")
    assert_error(errors, "allocated contiguously")

    first, second = lifecycle_pair("admissibility", "superseded")
    _, errors = validate_values(tmp_path / "valid", ("first.json", first), ("second.json", second))
    assert errors == []


MATRIX_CONTEXTS = [
    ("supports", "candidate_invariant_review", {"accepted_for_formalization", "accepted_with_constraints", "rejected", "deferred"}),
    ("supports", "bounded_formal_question", {"accepted_for_formalization", "accepted_with_constraints", "rejected", "deferred"}),
    ("supports", "vocabulary_alignment", {"accepted_for_formalization", "accepted_with_constraints", "rejected", "deferred"}),
    ("supports", "model_obligation", {"accepted_for_formalization", "accepted_with_constraints", "rejected", "deferred"}),
    ("indeterminate", "indeterminate_evidence_review", {"accepted_with_constraints", "rejected", "deferred"}),
    ("indeterminate", "bounded_formal_question", {"accepted_with_constraints", "rejected", "deferred"}),
    ("indeterminate", "vocabulary_alignment", {"accepted_with_constraints", "rejected", "deferred"}),
    ("indeterminate", "model_obligation", {"accepted_with_constraints", "rejected", "deferred"}),
    ("violates", "counterexample_review", {"accepted_for_formalization", "accepted_with_constraints", "rejected", "deferred"}),
    ("violates", "candidate_invariant_review", {"accepted_with_constraints", "rejected", "deferred"}),
]


@pytest.mark.parametrize(("outcome", "purpose", "allowed"), MATRIX_CONTEXTS)
@pytest.mark.parametrize("result", ["accepted_for_formalization", "accepted_with_constraints", "rejected", "deferred"])
def test_complete_decision_compatibility_matrix(tmp_path: Path, outcome: str, purpose: str, allowed: set[str], result: str) -> None:
    limited = outcome == "violates" and purpose == "candidate_invariant_review"
    review = load("valid_limited_review.json" if limited else "valid_admissible_review.json")
    review["reviewed_empirical_outcome"] = outcome
    review["package_purpose"] = purpose
    review["provenance_snapshot"]["reviewed_empirical_outcome"] = outcome
    review["provenance_snapshot"]["package_purpose"] = purpose
    fixture = {
        "accepted_for_formalization": "valid_accepted_decision.json",
        "accepted_with_constraints": "valid_constrained_decision.json",
        "rejected": "valid_rejected_decision.json",
        "deferred": "valid_deferred_decision.json",
    }[result]
    decision = load(fixture)
    if limited:
        limitation = review["limitations_snapshot"]["known_limitations"][0]
        decision["preserved_limitations"] = [limitation]
        if "translation_record" in decision:
            decision["translation_record"]["preserved_limitations"] = [limitation]
    _, errors = validate_values(tmp_path, ("review.json", review), ("decision.json", decision))
    matrix_errors = [error for error in errors if "incompatible with the linked review" in error]
    assert (not matrix_errors) == (result in allowed)
    if result in allowed:
        assert errors == []


def test_explicit_paths_are_combined_with_discovered_records(tmp_path: Path) -> None:
    root = repository(tmp_path)
    canonical = write(root, "promotion-records/admissibility/canonical.json", load("valid_admissible_review.json"))
    explicit = write(root, "scratch/explicit.json", load("valid_admissible_review.json"))
    count, errors = validate(root, [explicit])
    assert canonical != explicit
    assert count == 2
    assert_error(errors, "duplicate consumer identifier")


def test_discovery_is_bounded_sorted_and_ignores_symlinks(tmp_path: Path) -> None:
    root = repository(tmp_path)
    a = write(root, "promotion-records/admissibility/z.json", load("valid_admissible_review.json"))
    b = write(root, "promotion-records/decisions/a.json", load("valid_rejected_decision.json"))
    write(root, "unbounded/ignored.json", load("valid_admissible_review.json"))
    (a.parent / "link.json").symlink_to(a)
    assert discover_paths(root) == [a, b]


def test_symlinked_discovery_directory_is_rejected_without_traversal(tmp_path: Path) -> None:
    root = repository(tmp_path)
    outside = tmp_path / "outside"
    write(outside, "escaped.json", load("valid_admissible_review.json"))
    (root / "promotion-records").mkdir()
    (root / "promotion-records" / "admissibility").symlink_to(outside, target_is_directory=True)
    count, errors = validate(root)
    assert count == 0
    assert_error(errors, "canonical record discovery cannot traverse a symlink")


def test_validation_is_read_only_deterministic_and_has_no_external_access(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    review, decision = linked_pair()
    root = repository(tmp_path)
    paths = [write(root, "review.json", review), write(root, "decision.json", decision)]
    before = {path: path.read_bytes() for path in paths}
    monkeypatch.setattr(socket, "create_connection", lambda *args, **kwargs: pytest.fail("network access attempted"))
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: pytest.fail("subprocess access attempted"))
    first = validate(root, paths)
    second = validate(root, list(reversed(paths)))
    assert first == second == (2, [])
    assert {path: path.read_bytes() for path in paths} == before
