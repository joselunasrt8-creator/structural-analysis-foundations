#!/usr/bin/env python3
"""Validate Phase 1 research-object manifests and seed objects.

The validator is dependency-free and local-filesystem only. The JSON Schema file
is the authority for patterns, enums, required object fields, and allowed object
fields; this script applies that schema contract plus repository-specific checks
that JSON Schema alone cannot prove here, such as manifest references, source
anchors, line ranges, unique IDs, and resolved dependency targets.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def parse_manifest(path: Path) -> dict[str, Any]:
    """Parse the repository's deliberately small manifest YAML subset."""
    data: dict[str, Any] = {}
    current_list: str | None = None
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].rstrip()
        if not line:
            continue
        if line.startswith("  - "):
            if current_list is None:
                raise ValueError(f"{path}:{line_no}: list item without list key")
            data[current_list].append(line[4:].strip())
            continue
        if line.startswith(" "):
            raise ValueError(f"{path}:{line_no}: unsupported indentation")
        if ":" not in line:
            raise ValueError(f"{path}:{line_no}: expected key: value")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"{path}:{line_no}: empty key")
        if value:
            data[key] = int(value) if value.isdigit() else value
            current_list = None
        else:
            data[key] = []
            current_list = key
    return data


def require(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def compile_pattern(schema: dict[str, Any], field: str) -> re.Pattern[str]:
    return re.compile(schema["properties"][field]["pattern"])


def enum_values(schema: dict[str, Any], field: str) -> set[str]:
    return set(schema["properties"][field]["enum"])


def nested_enum_values(schema: dict[str, Any], *path: str) -> set[str]:
    node: dict[str, Any] = schema
    for key in path:
        node = node[key]
    return set(node["enum"])


def validate_source(source: Any, obj_path: Path, paper_dir: Path, errors: list[str]) -> None:
    require(isinstance(source, dict), errors, f"{obj_path}: provenance.source must be an object")
    if not isinstance(source, dict):
        return

    source_file = source.get("file")
    anchor = source.get("anchor")
    require(isinstance(source_file, str) and bool(source_file), errors, f"{obj_path}: invalid provenance.source.file")
    require(isinstance(anchor, str) and bool(anchor), errors, f"{obj_path}: invalid provenance.source.anchor")

    source_path = paper_dir / source_file if isinstance(source_file, str) else None
    if source_path is not None:
        require(source_path.is_file(), errors, f"{obj_path}: missing source file {source_file}")

    lines = source.get("lines")
    if lines is not None:
        valid_lines = isinstance(lines, list) and len(lines) == 2 and all(isinstance(i, int) and i > 0 for i in lines)
        require(valid_lines, errors, f"{obj_path}: invalid provenance.source.lines")
        if valid_lines:
            start, end = lines
            require(start <= end, errors, f"{obj_path}: source line range must be ordered")
            if source_path is not None and source_path.is_file():
                line_count = len(source_path.read_text(encoding="utf-8").splitlines())
                require(end <= line_count, errors, f"{obj_path}: source line range exceeds {source_file} length")

    if isinstance(anchor, str) and source_path is not None and source_path.is_file():
        text = source_path.read_text(encoding="utf-8")
        require(f"\\label{{{anchor}}}" in text or anchor in text, errors, f"{obj_path}: source anchor {anchor!r} not found in {source_file}")


def validate_object(
    obj: dict[str, Any],
    obj_path: Path,
    paper_dir: Path,
    schema: dict[str, Any],
    errors: list[str],
) -> None:
    id_re = compile_pattern(schema, "id")
    token_re = compile_pattern(schema, "domain")
    paper_re = compile_pattern(schema, "paper")
    version_re = compile_pattern(schema, "version")
    kinds = enum_values(schema, "kind")
    lifecycle_statuses = enum_values(schema, "lifecycle_status")
    maturities = enum_values(schema, "maturity")
    validation_statuses = nested_enum_values(schema, "properties", "validation", "properties", "status")
    dependency_relations = nested_enum_values(schema, "properties", "dependencies", "items", "properties", "relation")

    for key in schema.get("required", []):
        require(key in obj, errors, f"{obj_path}: missing required field {key!r}")

    allowed = set(schema.get("properties", {}))
    for key in obj:
        require(key in allowed, errors, f"{obj_path}: unsupported field {key!r}")

    object_id = obj.get("id")
    kind = obj.get("kind")
    domain = obj.get("domain")
    slug = obj.get("slug")
    require(isinstance(object_id, str) and bool(id_re.fullmatch(object_id)), errors, f"{obj_path}: invalid id")
    require(kind in kinds, errors, f"{obj_path}: invalid kind")
    require(isinstance(domain, str) and bool(token_re.fullmatch(domain)), errors, f"{obj_path}: invalid domain")
    require(isinstance(slug, str) and bool(token_re.fullmatch(slug)), errors, f"{obj_path}: invalid slug")
    if isinstance(kind, str) and isinstance(domain, str) and isinstance(slug, str):
        require(object_id == f"{kind}.{domain}.{slug}", errors, f"{obj_path}: id does not match <kind>.<domain>.<slug>")

    require(isinstance(obj.get("version"), str) and bool(version_re.fullmatch(obj["version"])), errors, f"{obj_path}: invalid version")
    require(isinstance(obj.get("title"), str) and bool(obj["title"]), errors, f"{obj_path}: invalid title")
    require(isinstance(obj.get("paper"), str) and bool(paper_re.fullmatch(obj["paper"])), errors, f"{obj_path}: invalid paper")
    require(isinstance(obj.get("canonical_statement"), str) and bool(obj["canonical_statement"]), errors, f"{obj_path}: invalid canonical_statement")
    require(obj.get("lifecycle_status") in lifecycle_statuses, errors, f"{obj_path}: invalid lifecycle_status")
    require(obj.get("maturity") in maturities, errors, f"{obj_path}: invalid maturity")

    provenance = obj.get("provenance")
    require(isinstance(provenance, dict), errors, f"{obj_path}: provenance must be an object")
    if isinstance(provenance, dict):
        validate_source(provenance.get("source"), obj_path, paper_dir, errors)

    dependencies = obj.get("dependencies")
    require(isinstance(dependencies, list), errors, f"{obj_path}: dependencies must be a list")
    if isinstance(dependencies, list):
        seen_deps: set[tuple[str, str]] = set()
        for dep in dependencies:
            require(isinstance(dep, dict), errors, f"{obj_path}: dependency entries must be objects")
            if not isinstance(dep, dict):
                continue
            dep_id = dep.get("id")
            relation = dep.get("relation")
            require(isinstance(dep_id, str) and bool(id_re.fullmatch(dep_id)), errors, f"{obj_path}: invalid dependency id {dep_id!r}")
            require(relation in dependency_relations, errors, f"{obj_path}: invalid dependency relation {relation!r}")
            if isinstance(dep_id, str) and isinstance(relation, str):
                require((dep_id, relation) not in seen_deps, errors, f"{obj_path}: duplicate dependency {dep_id} ({relation})")
                seen_deps.add((dep_id, relation))

    validation = obj.get("validation")
    require(isinstance(validation, dict), errors, f"{obj_path}: validation must be an object")
    if isinstance(validation, dict):
        require(validation.get("status") in validation_statuses, errors, f"{obj_path}: invalid validation.status")

    require(isinstance(obj.get("exports"), dict), errors, f"{obj_path}: exports must be an object")


def discover_manifests(root: Path) -> list[Path]:
    return sorted(path for path in root.glob("paper-*/paper.yml") if path.is_file())


def validate(root: Path) -> tuple[int, int, list[str]]:
    errors: list[str] = []
    schema_path = root / "schemas" / "research-object.schema.json"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - report validation failure cleanly.
        return 0, 0, [f"schema is not valid JSON: {exc}"]

    manifests = discover_manifests(root)
    require(bool(manifests), errors, "no paper manifests found")

    objects_by_id: dict[str, Path] = {}
    dependency_edges: list[tuple[Path, str]] = []
    valid_object_count = 0

    for manifest_path in manifests:
        try:
            manifest = parse_manifest(manifest_path)
        except Exception as exc:  # noqa: BLE001 - report parser failure cleanly.
            errors.append(str(exc))
            continue

        paper_dir = manifest_path.parent
        paper_id = manifest.get("paper")
        require(paper_id == paper_dir.name, errors, f"{manifest_path.relative_to(root)}: paper must match directory name")
        for key in ("paper", "title", "manifest_version", "files", "research_objects"):
            require(key in manifest, errors, f"{manifest_path.relative_to(root)}: missing {key}")
        for list_key in ("files", "research_objects"):
            require(isinstance(manifest.get(list_key), list), errors, f"{manifest_path.relative_to(root)}: {list_key} must be a list")
        for rel in manifest.get("files", []):
            require((paper_dir / rel).is_file(), errors, f"{manifest_path.relative_to(root)}: missing file reference {rel}")
        for rel in manifest.get("research_objects", []):
            obj_path = paper_dir / rel
            if not obj_path.is_file():
                errors.append(f"{manifest_path.relative_to(root)}: missing research object {rel}")
                continue
            try:
                obj = json.loads(obj_path.read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001 - report validation failure cleanly.
                errors.append(f"{obj_path.relative_to(root)}: invalid JSON: {exc}")
                continue
            rel_obj_path = obj_path.relative_to(root)
            validate_object(obj, rel_obj_path, paper_dir, schema, errors)
            require(obj.get("paper") == paper_id, errors, f"{rel_obj_path}: paper does not match manifest")
            if isinstance(obj.get("id"), str):
                require(obj["id"] not in objects_by_id, errors, f"{rel_obj_path}: duplicate id {obj['id']}")
                objects_by_id.setdefault(obj["id"], rel_obj_path)
            if isinstance(obj.get("dependencies"), list):
                for dep in obj["dependencies"]:
                    if isinstance(dep, dict) and isinstance(dep.get("id"), str):
                        dependency_edges.append((rel_obj_path, dep["id"]))
            valid_object_count += 1

    for from_path, dep_id in dependency_edges:
        require(dep_id in objects_by_id, errors, f"{from_path}: unresolved dependency target {dep_id}")

    return len(manifests), valid_object_count, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate research-object manifests and seed objects.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="repository root to validate")
    args = parser.parse_args()

    manifest_count, object_count, errors = validate(args.root.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Validated {manifest_count} manifests and {object_count} research objects.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
