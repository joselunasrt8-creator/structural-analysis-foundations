#!/usr/bin/env python3
"""Deterministically validate repository-owned consumer promotion records.

This validator is deliberately local and read-only.  It validates consumer
records and their relationships; it never validates, fetches, or executes a
producer package.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATHS = {
    "admissibility": Path("schemas/admissibility_review.schema.json"),
    "decision": Path("schemas/promotion_decision.schema.json"),
}
SUPPORTED_SCHEMA_VERSIONS = {"admissibility": {"v1"}, "decision": {"v1"}}
DISCOVERY_DIRECTORIES = (
    Path("promotion-records/admissibility"),
    Path("promotion-records/decisions"),
)
IDENTIFIER_RE = re.compile(r"^saf:(admissibility|decision):([a-z2-7]+):([0-9]{4})$")
EXCLUDED_EFFECTS = {
    "canonical_research_object_publication",
    "canonical_fixture_creation",
    "theorem_validation",
    "implementation_conformance_claim",
    "producer_evidence_mutation",
    "automation_creation",
    "cross_repository_synchronization",
}


@dataclass(frozen=True)
class Record:
    path: Path
    display_path: str
    kind: str
    value: dict[str, Any]

    @property
    def identifier(self) -> Any:
        return self.value.get("admissibility_id" if self.kind == "admissibility" else "decision_id")


def package_identity_token(package_id: str, package_version: str) -> str:
    """Return the contract-defined lowercase, unpadded RFC 4648 Base32 token."""
    framed = f"{len(package_id.encode('utf-8'))}:{package_id}{len(package_version.encode('utf-8'))}:{package_version}"
    return base64.b32encode(framed.encode("utf-8")).decode("ascii").rstrip("=").lower()


def _display_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def discover_paths(root: Path) -> list[Path]:
    """Discover only regular, non-symlink records in the bounded canonical layout."""
    paths: list[Path] = []
    for relative in DISCOVERY_DIRECTORIES:
        directory = root / relative
        if _has_symlink_component(directory, root) or not directory.is_dir():
            continue
        paths.extend(path for path in directory.glob("*.json") if path.is_file() and not _has_symlink_component(path, root))
    return sorted(set(paths), key=lambda path: path.relative_to(root).as_posix())


def _has_symlink_component(path: Path, root: Path) -> bool:
    """Return whether a repository-relative path traverses any symlink."""
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def _discovery_boundary_errors(root: Path) -> list[str]:
    errors: list[str] = []
    for relative in DISCOVERY_DIRECTORIES:
        current = root
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                errors.append(f"{current.relative_to(root).as_posix()}: canonical record discovery cannot traverse a symlink")
                break
    return errors


def normalize_explicit_paths(root: Path, paths: Iterable[Path]) -> tuple[list[Path], list[str]]:
    normalized: dict[Path, Path] = {}
    errors: list[str] = []
    resolved_root = root.resolve()
    for supplied in paths:
        candidate = supplied if supplied.is_absolute() else Path.cwd() / supplied
        display = _display_path(candidate, root)
        try:
            resolved = candidate.resolve(strict=True)
        except OSError as exc:
            errors.append(f"{display}: cannot read input: {exc.strerror or exc.__class__.__name__}")
            continue
        if resolved_root not in (resolved, *resolved.parents):
            errors.append(f"{display}: input is outside the repository root")
            continue
        if _has_symlink_component(candidate, root) or not resolved.is_file():
            errors.append(f"{display}: input must be a regular non-symlink file")
            continue
        normalized.setdefault(resolved, resolved)
    return sorted(normalized.values(), key=lambda path: _display_path(path, root)), sorted(errors)


def _json_path(parts: Iterable[Any]) -> str:
    result = "$"
    for part in parts:
        result += f"[{part}]" if isinstance(part, int) else f".{part}"
    return result


def _require(condition: bool, errors: list[str], path: str, message: str) -> None:
    if not condition:
        errors.append(f"{path}: {message}")


def _identifier_parts(value: Any) -> tuple[str, str, int] | None:
    if not isinstance(value, str):
        return None
    match = IDENTIFIER_RE.fullmatch(value)
    if not match:
        return None
    return match.group(1), match.group(2), int(match.group(3))


def _not_applicable(value: Any) -> bool:
    return isinstance(value, dict) and value.get("value") == "not_applicable" and bool(value.get("rationale"))


def _meaningful_limitations(snapshot: Any) -> list[str]:
    if not isinstance(snapshot, dict):
        return []
    result: list[str] = []
    for field in ("assumptions", "known_limitations", "not_claimed"):
        items = snapshot.get(field)
        if isinstance(items, list):
            result.extend(item for item in items if isinstance(item, str) and item)
    return result


def _load_schemas(root: Path) -> tuple[dict[str, Draft202012Validator], list[str]]:
    validators: dict[str, Draft202012Validator] = {}
    errors: list[str] = []
    for kind, relative in SCHEMA_PATHS.items():
        path = root / relative
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            validators[kind] = Draft202012Validator(schema, format_checker=FormatChecker())
        except Exception as exc:  # noqa: BLE001 - schema failures become stable validation errors.
            errors.append(f"{relative.as_posix()}: invalid Draft 2020-12 schema: {exc}")
    return validators, sorted(errors)


def _record_kind(value: Any) -> str | None:
    if not isinstance(value, dict):
        return None
    has_review = "admissibility_id" in value
    has_decision = "decision_id" in value
    if has_decision:
        return "decision"
    if has_review:
        return "admissibility"
    return None


def _validate_snapshot(record: Record, errors: list[str]) -> None:
    value = record.value
    snapshot = value.get("provenance_snapshot")
    if not isinstance(snapshot, dict):
        return
    prefix = record.display_path
    package = value.get("package_reference")
    if not isinstance(package, dict):
        return
    comparisons = (
        ("package_version", package.get("package_version")),
        ("package_purpose", value.get("package_purpose")),
        ("reviewed_empirical_outcome", value.get("reviewed_empirical_outcome")),
        ("artifact_references", value.get("reviewed_artifact_references")),
        ("limitations_snapshot", value.get("limitations_snapshot")),
        ("replication_status", value.get("replication_status")),
    )
    for field, expected in comparisons:
        _require(snapshot.get(field) == expected, errors, f"{prefix}:$.provenance_snapshot.{field}", f"must exactly equal $.{field if field not in {'artifact_references'} else 'reviewed_artifact_references'}")
    if package.get("provenance_source_type") == "repository":
        _require(snapshot.get("producer_commit") == package.get("producer_commit"), errors, f"{prefix}:$.provenance_snapshot.producer_commit", "must exactly equal $.package_reference.producer_commit")
    if "producer_lifecycle_record_reference" in package:
        _require(snapshot.get("producer_lifecycle_record_reference") == package["producer_lifecycle_record_reference"], errors, f"{prefix}:$.provenance_snapshot.producer_lifecycle_record_reference", "must preserve the package lifecycle reference")
    hashes = snapshot.get("hashes")
    if isinstance(hashes, list):
        expected_digest = {
            "hash_algorithm": package.get("hash_algorithm"),
            "value": package.get("content_digest"),
            "canonicalization_method": package.get("canonicalization_method"),
        }
        _require(expected_digest in hashes, errors, f"{prefix}:$.provenance_snapshot.hashes", "must contain the locally observed package digest metadata")
    if value.get("admissibility_result") == "admissible_with_limitations":
        _require(bool(_meaningful_limitations(value.get("limitations_snapshot"))), errors, f"{prefix}:$.limitations_snapshot", "must retain at least one meaningful limitation for admissible_with_limitations")


def _validate_identifier(record: Record, errors: list[str]) -> None:
    prefix = record.display_path
    parts = _identifier_parts(record.identifier)
    if parts is None:
        return
    kind, token, ordinal = parts
    package = record.value.get("package_reference")
    if not isinstance(package, dict) or not isinstance(package.get("package_id"), str) or not isinstance(package.get("package_version"), str):
        return
    expected = package_identity_token(package["package_id"], package["package_version"])
    _require(kind == record.kind, errors, f"{prefix}:$", f"identifier record type must be {record.kind}")
    _require(token == expected, errors, f"{prefix}:$", "identifier package token does not match package_reference")
    _require(ordinal != 0, errors, f"{prefix}:$", "identifier ordinal 0000 is prohibited")
    if record.kind == "decision":
        linked = _identifier_parts(record.value.get("admissibility_id"))
        if linked is not None:
            _require(linked[1] == expected, errors, f"{prefix}:$.admissibility_id", "package token does not match package_reference")


def _validate_decision(record: Record, reviews: dict[str, list[Record]], errors: list[str]) -> None:
    value = record.value
    prefix = record.display_path
    admissibility_id = value.get("admissibility_id")
    linked_records = reviews.get(admissibility_id, []) if isinstance(admissibility_id, str) else []
    _require(len(linked_records) == 1, errors, f"{prefix}:$.admissibility_id", "must resolve to exactly one discovered Admissibility Review")
    if len(linked_records) != 1:
        return
    review = linked_records[0].value
    eligible = review.get("admissibility_result") in {"admissible", "admissible_with_limitations"}
    _require(eligible, errors, f"{prefix}:$.admissibility_id", f"linked review result {review.get('admissibility_result')!r} is not eligible for a Promotion Decision")
    _require(value.get("package_reference") == review.get("package_reference"), errors, f"{prefix}:$.package_reference", "must exactly equal the linked Admissibility Review package_reference")
    translation = value.get("translation_record")
    accepted = value.get("decision_result") in {"accepted_for_formalization", "accepted_with_constraints"}
    if accepted and isinstance(translation, dict):
        snapshot = review.get("provenance_snapshot")
        if not isinstance(snapshot, dict):
            snapshot = {}
        _require(translation.get("producer_claim") == snapshot.get("reviewed_claim"), errors, f"{prefix}:$.translation_record.producer_claim", "must exactly preserve the linked review producer claim")
        excluded = translation.get("excluded_formalization_scope")
        if isinstance(excluded, list):
            _require(translation.get("accepted_formalization_scope") not in excluded, errors, f"{prefix}:$.translation_record.accepted_formalization_scope", "must not exactly duplicate an excluded scope item")
        limitations = _meaningful_limitations(review.get("limitations_snapshot"))
        if review.get("admissibility_result") == "admissible_with_limitations":
            decision_limitations = value.get("preserved_limitations")
            translated_limitations = translation.get("preserved_limitations")
            if isinstance(decision_limitations, list):
                _require(all(item in decision_limitations for item in limitations), errors, f"{prefix}:$.preserved_limitations", "must preserve every linked review limitation")
            if isinstance(translated_limitations, list):
                _require(all(item in translated_limitations for item in limitations), errors, f"{prefix}:$.translation_record.preserved_limitations", "must preserve every linked review limitation")
        if value.get("decision_result") == "accepted_with_constraints":
            _require(bool(translation.get("constraints")), errors, f"{prefix}:$.translation_record.constraints", "must be non-empty for accepted_with_constraints")
            _require(bool(translation.get("excluded_formalization_scope")), errors, f"{prefix}:$.translation_record.excluded_formalization_scope", "must be non-empty for accepted_with_constraints")
            _require(bool(translation.get("preserved_limitations")), errors, f"{prefix}:$.translation_record.preserved_limitations", "must be non-empty for accepted_with_constraints")
    excluded_effects = value.get("excluded_effects")
    if isinstance(excluded_effects, list) and all(isinstance(effect, str) for effect in excluded_effects):
        _require(set(excluded_effects) == EXCLUDED_EFFECTS, errors, f"{prefix}:$.excluded_effects", "must contain exactly the mandatory excluded-effect set")
    if eligible:
        allowed = _allowed_decision_results(review.get("reviewed_empirical_outcome"), review.get("package_purpose"))
        if allowed is not None:
            _require(value.get("decision_result") in allowed, errors, f"{prefix}:$.decision_result", "is incompatible with the linked review outcome and package purpose")


def _allowed_decision_results(outcome: Any, purpose: Any) -> set[str] | None:
    """Return the decision-result row defined by the normative compatibility matrix."""
    nonaccepted = {"rejected", "deferred"}
    if outcome == "supports" and purpose in {"candidate_invariant_review", "bounded_formal_question", "vocabulary_alignment", "model_obligation"}:
        return nonaccepted | {"accepted_for_formalization", "accepted_with_constraints"}
    if outcome == "indeterminate" and purpose in {"indeterminate_evidence_review", "bounded_formal_question", "vocabulary_alignment", "model_obligation"}:
        return nonaccepted | {"accepted_with_constraints"}
    if outcome == "violates" and purpose == "counterexample_review":
        return nonaccepted | {"accepted_for_formalization", "accepted_with_constraints"}
    if outcome == "violates" and purpose == "candidate_invariant_review":
        return nonaccepted | {"accepted_with_constraints"}
    return None


def _validate_lifecycle(record: Record, by_id: dict[str, list[Record]], errors: list[str]) -> None:
    value = record.value
    prefix = record.display_path
    current = _identifier_parts(record.identifier)
    if current is None:
        return
    lifecycle = value.get("record_lifecycle")
    known_fields = ("superseding_record_reference", "withdrawal_record_reference", "invalidation_record_reference")
    if lifecycle == "active":
        for field in known_fields:
            _require(not isinstance(value.get(field), str), errors, f"{prefix}:$.{field}", "active records cannot contain a known lifecycle-action reference")
    prior = value.get("prior_record_reference")
    if isinstance(prior, str):
        targets = by_id.get(prior, [])
        _require(len(targets) == 1, errors, f"{prefix}:$.prior_record_reference", "must resolve to exactly one discovered record")
        if len(targets) == 1:
            target = targets[0]
            target_parts = _identifier_parts(target.identifier)
            _require(target.kind == record.kind, errors, f"{prefix}:$.prior_record_reference", "must reference the same record type")
            if target_parts is not None and target_parts[1] == current[1]:
                _require(target_parts[2] == current[2] - 1, errors, f"{prefix}:$.prior_record_reference", "must reference the immediately preceding ordinal")
            else:
                _require(_is_cross_version_lineage(record, target), errors, f"{prefix}:$.prior_record_reference", "cross-token linkage must preserve the producer package_id and change package_version")
    for field in known_fields:
        reference = value.get(field)
        if not isinstance(reference, str):
            continue
        targets = by_id.get(reference, [])
        _require(len(targets) == 1, errors, f"{prefix}:$.{field}", "must resolve to exactly one discovered record")
        if len(targets) != 1:
            continue
        target = targets[0]
        target_parts = _identifier_parts(target.identifier)
        _require(target.kind == record.kind, errors, f"{prefix}:$.{field}", "must reference the same record type")
        if target_parts is not None and target_parts[1] == current[1]:
            _require(target_parts[2] == current[2] + 1, errors, f"{prefix}:$.{field}", "must reference the immediately following ordinal")
        else:
            _require(_is_cross_version_lineage(record, target), errors, f"{prefix}:$.{field}", "cross-token linkage must preserve the producer package_id and change package_version")
        _require(target.value.get("prior_record_reference") == record.identifier, errors, f"{prefix}:$.{field}", "target record must link back through prior_record_reference")
        expected_lifecycle = {
            "withdrawal_record_reference": "withdrawn",
            "invalidation_record_reference": "invalidated",
        }.get(field)
        if expected_lifecycle is not None:
            _require(target.value.get("record_lifecycle") == expected_lifecycle, errors, f"{prefix}:$.{field}", f"target record lifecycle must be {expected_lifecycle}")
    if lifecycle == "superseded":
        reference = value.get("superseding_record_reference")
        _require(isinstance(reference, str) or _not_applicable(reference), errors, f"{prefix}:$.superseding_record_reference", "must be a known later record or rationale-bearing not_applicable")


def _is_cross_version_lineage(record: Record, target: Record) -> bool:
    if record.kind != target.kind:
        return False
    package = record.value.get("package_reference")
    target_package = target.value.get("package_reference")
    return (
        isinstance(package, dict)
        and isinstance(target_package, dict)
        and isinstance(package.get("package_id"), str)
        and package.get("package_id") == target_package.get("package_id")
        and isinstance(package.get("package_version"), str)
        and isinstance(target_package.get("package_version"), str)
        and package.get("package_version") != target_package.get("package_version")
    )


def _validate_sequences(records: list[Record], errors: list[str]) -> None:
    sequences: dict[tuple[str, str], list[tuple[int, Record]]] = {}
    for record in records:
        parts = _identifier_parts(record.identifier)
        if parts is not None:
            sequences.setdefault((parts[0], parts[1]), []).append((parts[2], record))
    for (kind, token), entries in sorted(sequences.items()):
        ordered = sorted(entries, key=lambda entry: (entry[0], entry[1].display_path))
        ordinals = [ordinal for ordinal, _ in ordered]
        if ordinals and ordinals[0] != 1:
            errors.append(f"{ordered[0][1].display_path}:$: {kind} sequence {token!r} must begin at ordinal 0001")
        expected = list(range(1, len(ordinals) + 1))
        if len(set(ordinals)) == len(ordinals) and ordinals != expected:
            errors.append(f"{ordered[0][1].display_path}:$: {kind} sequence {token!r} ordinals must be allocated contiguously from 0001")


def validate(root: Path, explicit_paths: Iterable[Path] | None = None) -> tuple[int, list[str]]:
    """Validate a discovered or explicit set and return (record count, errors)."""
    root = root.resolve()
    discovered = discover_paths(root)
    path_errors = _discovery_boundary_errors(root)
    if explicit_paths is not None:
        explicit, explicit_errors = normalize_explicit_paths(root, explicit_paths)
        path_errors.extend(explicit_errors)
        paths = sorted({path.resolve(): path.resolve() for path in [*discovered, *explicit]}.values(), key=lambda path: _display_path(path, root))
    else:
        paths = discovered
    validators, errors = _load_schemas(root)
    errors.extend(path_errors)
    records: list[Record] = []
    for path in paths:
        display = _display_path(path, root)
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{display}: invalid JSON: {exc}")
            continue
        kind = _record_kind(value)
        if kind is None:
            errors.append(f"{display}: $: cannot determine consumer record type")
            continue
        record = Record(path, display, kind, value)
        records.append(record)
        validator = validators.get(kind)
        if validator is not None:
            for failure in sorted(validator.iter_errors(value), key=lambda item: (_json_path(item.absolute_path), item.message)):
                errors.append(f"{display}:{_json_path(failure.absolute_path)}: schema: {failure.message}")
        if value.get("schema_version") not in SUPPORTED_SCHEMA_VERSIONS[kind]:
            errors.append(f"{display}:$.schema_version: unsupported {kind} schema version {value.get('schema_version')!r}")
        _validate_identifier(record, errors)
        if kind == "admissibility":
            _validate_snapshot(record, errors)

    by_id: dict[str, list[Record]] = {}
    reviews: dict[str, list[Record]] = {}
    for record in records:
        if isinstance(record.identifier, str):
            by_id.setdefault(record.identifier, []).append(record)
            if record.kind == "admissibility":
                reviews.setdefault(record.identifier, []).append(record)
    for identifier, duplicates in by_id.items():
        if len(duplicates) > 1:
            for record in duplicates:
                errors.append(f"{record.display_path}:$: duplicate consumer identifier {identifier!r}")
    _validate_sequences(records, errors)
    for record in records:
        if record.kind == "decision":
            _validate_decision(record, reviews, errors)
        _validate_lifecycle(record, by_id, errors)
    return len(records), sorted(set(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate local Admissibility Review and Promotion Decision records.")
    parser.add_argument("paths", nargs="*", type=Path, help="explicit repository-local record paths (default: bounded discovery)")
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    args = parser.parse_args(argv)
    count, errors = validate(args.root, args.paths if args.paths else None)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"promotion record validation failed: {len(errors)} error(s), {count} record(s)")
        return 1
    print(f"promotion record validation passed: {count} record(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
