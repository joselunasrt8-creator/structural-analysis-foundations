#!/usr/bin/env python3
"""Validate Phase 1 research-object manifests and seed objects.

This validator is intentionally lightweight and dependency-free. It supports the
small YAML subset used by the paper manifests in this repository and the JSON
Schema subset used by schemas/research-object.schema.json.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "research-object.schema.json"
MANIFESTS = [
    ROOT / "paper-1-dependency" / "paper.yml",
    ROOT / "paper-2-canonical-structural-analysis" / "paper.yml",
    ROOT / "paper-3-foundations-structural-analysis" / "paper.yml",
]
ID_RE = re.compile(r"^[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$")
TOKEN_RE = re.compile(r"^[a-z][a-z0-9-]*$")
PAPER_RE = re.compile(r"^paper-[1-3][a-z0-9-]*$")
KINDS = {"definition", "theorem", "concept", "claim", "interface"}
STATUSES = {"seed", "draft", "canonical", "deprecated"}


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


def validate_object(obj: dict[str, Any], obj_path: Path, schema: dict[str, Any], errors: list[str]) -> None:
    required = schema.get("required", [])
    for key in required:
        require(key in obj, errors, f"{obj_path}: missing required field {key!r}")

    allowed = set(schema.get("properties", {}))
    for key in obj:
        require(key in allowed, errors, f"{obj_path}: unsupported field {key!r}")

    object_id = obj.get("id")
    kind = obj.get("kind")
    domain = obj.get("domain")
    slug = obj.get("slug")
    require(isinstance(object_id, str) and bool(ID_RE.fullmatch(object_id)), errors, f"{obj_path}: invalid id")
    require(kind in KINDS, errors, f"{obj_path}: invalid kind")
    require(isinstance(domain, str) and bool(TOKEN_RE.fullmatch(domain)), errors, f"{obj_path}: invalid domain")
    require(isinstance(slug, str) and bool(TOKEN_RE.fullmatch(slug)), errors, f"{obj_path}: invalid slug")
    if isinstance(kind, str) and isinstance(domain, str) and isinstance(slug, str):
        require(object_id == f"{kind}.{domain}.{slug}", errors, f"{obj_path}: id does not match <kind>.<domain>.<slug>")

    require(isinstance(obj.get("title"), str) and bool(obj["title"]), errors, f"{obj_path}: invalid title")
    require(isinstance(obj.get("paper"), str) and bool(PAPER_RE.fullmatch(obj["paper"])), errors, f"{obj_path}: invalid paper")
    require(obj.get("status") in STATUSES, errors, f"{obj_path}: invalid status")

    source = obj.get("source")
    require(isinstance(source, dict), errors, f"{obj_path}: source must be an object")
    if isinstance(source, dict):
        require(isinstance(source.get("file"), str) and bool(source["file"]), errors, f"{obj_path}: invalid source.file")
        require(isinstance(source.get("anchor"), str) and bool(source["anchor"]), errors, f"{obj_path}: invalid source.anchor")
        if "lines" in source:
            lines = source["lines"]
            require(isinstance(lines, list) and len(lines) == 2 and all(isinstance(i, int) and i > 0 for i in lines), errors, f"{obj_path}: invalid source.lines")

    if "depends_on" in obj:
        deps = obj["depends_on"]
        require(isinstance(deps, list), errors, f"{obj_path}: depends_on must be a list")
        if isinstance(deps, list):
            require(len(deps) == len(set(deps)), errors, f"{obj_path}: duplicate depends_on entries")
            for dep in deps:
                require(isinstance(dep, str) and bool(ID_RE.fullmatch(dep)), errors, f"{obj_path}: invalid depends_on id {dep!r}")


def main() -> int:
    errors: list[str] = []
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - report validation failure cleanly.
        print(f"ERROR: schema is not valid JSON: {exc}", file=sys.stderr)
        return 1

    seen_ids: set[str] = set()
    for manifest_path in MANIFESTS:
        if not manifest_path.exists():
            errors.append(f"missing manifest: {manifest_path.relative_to(ROOT)}")
            continue
        try:
            manifest = parse_manifest(manifest_path)
        except Exception as exc:  # noqa: BLE001 - report parser failure cleanly.
            errors.append(str(exc))
            continue

        paper_dir = manifest_path.parent
        paper_id = manifest.get("paper")
        require(paper_id == paper_dir.name, errors, f"{manifest_path.relative_to(ROOT)}: paper must match directory name")
        for key in ("paper", "title", "manifest_version", "files", "research_objects"):
            require(key in manifest, errors, f"{manifest_path.relative_to(ROOT)}: missing {key}")
        for rel in manifest.get("files", []):
            require((paper_dir / rel).is_file(), errors, f"{manifest_path.relative_to(ROOT)}: missing file reference {rel}")
        for rel in manifest.get("research_objects", []):
            obj_path = paper_dir / rel
            if not obj_path.is_file():
                errors.append(f"{manifest_path.relative_to(ROOT)}: missing research object {rel}")
                continue
            try:
                obj = json.loads(obj_path.read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001 - report validation failure cleanly.
                errors.append(f"{obj_path.relative_to(ROOT)}: invalid JSON: {exc}")
                continue
            validate_object(obj, obj_path.relative_to(ROOT), schema, errors)
            require(obj.get("paper") == paper_id, errors, f"{obj_path.relative_to(ROOT)}: paper does not match manifest")
            source_file = obj.get("source", {}).get("file") if isinstance(obj.get("source"), dict) else None
            if isinstance(source_file, str):
                require((paper_dir / source_file).is_file(), errors, f"{obj_path.relative_to(ROOT)}: missing source file {source_file}")
            if isinstance(obj.get("id"), str):
                require(obj["id"] not in seen_ids, errors, f"{obj_path.relative_to(ROOT)}: duplicate id {obj['id']}")
                seen_ids.add(obj["id"])

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(MANIFESTS)} manifests and {len(seen_ids)} research objects.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
