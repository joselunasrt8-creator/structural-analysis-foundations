"""Deterministic Draft 2020-12 validation for canonical fixture contracts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json
import re

from .jsonutil import read_json


@dataclass(frozen=True)
class ValidationIssue:
    fixture: str
    schema: str
    json_path: str
    constraint: str
    message: str


class SchemaValidationFailure(ValueError):
    def __init__(self, issues: list[ValidationIssue]) -> None:
        self.issues = issues
        super().__init__(format_issues(issues))


def discover_fixtures(repo_root: Path) -> list[Path]:
    fixtures_root = repo_root / "conformance" / "fixtures"
    return sorted(fixtures_root.glob("*.fixture.json"), key=lambda p: p.as_posix())


def schema_path_for_fixture(fixture_data: dict[str, Any], fixture_path: Path, repo_root: Path) -> Path:
    declared = fixture_data.get("schema_path")
    if not isinstance(declared, str) or not declared:
        raise SchemaValidationFailure([
            ValidationIssue(_rel(fixture_path, repo_root), "<undeclared>", "$", "required", "fixture must declare schema_path")
        ])
    return repo_root / declared


def validate_all(repo_root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for fixture_path in discover_fixtures(repo_root):
        fixture_data = read_json(fixture_path)
        try:
            schema_path = schema_path_for_fixture(fixture_data, fixture_path, repo_root)
        except SchemaValidationFailure as exc:
            issues.extend(exc.issues)
            continue
        schema = read_json(schema_path)
        issues.extend(validate_instance(fixture_data, schema, _rel(fixture_path, repo_root), _rel(schema_path, repo_root)))
    return sorted(issues, key=lambda e: (e.fixture, e.schema, e.json_path, e.constraint, e.message))


def validate_instance(instance: Any, schema: dict[str, Any], fixture: str, schema_name: str) -> list[ValidationIssue]:
    return list(_validate(instance, schema, schema, fixture, schema_name, "$"))


def format_issues(issues: list[ValidationIssue]) -> str:
    lines = ["canonical fixture schema validation failed:"]
    for issue in sorted(issues, key=lambda e: (e.fixture, e.schema, e.json_path, e.constraint, e.message)):
        lines.append(f"- fixture={issue.fixture} schema={issue.schema} path={issue.json_path} constraint={issue.constraint} message={issue.message}")
    return "\n".join(lines)


def _validate(instance: Any, schema: dict[str, Any], root: dict[str, Any], fixture: str, schema_name: str, path: str):
    if "$ref" in schema:
        schema = _resolve_ref(root, schema["$ref"])
    if "const" in schema and instance != schema["const"]:
        yield _issue(fixture, schema_name, path, "const", f"expected constant {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        yield _issue(fixture, schema_name, path, "enum", f"value must be one of {schema['enum']!r}")
    if "type" in schema and not _matches_type(instance, schema["type"]):
        yield _issue(fixture, schema_name, path, "type", f"value must be {schema['type']}")
        return
    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            yield _issue(fixture, schema_name, path, "minLength", f"string length must be at least {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            yield _issue(fixture, schema_name, path, "pattern", f"string does not match pattern {schema['pattern']}")
        return
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            yield _issue(fixture, schema_name, path, "minimum", f"number must be >= {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            yield _issue(fixture, schema_name, path, "maximum", f"number must be <= {schema['maximum']}")
        return
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            yield _issue(fixture, schema_name, path, "minItems", f"array must contain at least {schema['minItems']} items")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            yield _issue(fixture, schema_name, path, "maxItems", f"array must contain at most {schema['maxItems']} items")
        if schema.get("uniqueItems") and len({json.dumps(v, sort_keys=True, separators=(',', ':')) for v in instance}) != len(instance):
            yield _issue(fixture, schema_name, path, "uniqueItems", "array items must be unique")
        prefix = schema.get("prefixItems", [])
        for index, subschema in enumerate(prefix):
            if index < len(instance):
                yield from _validate(instance[index], subschema, root, fixture, schema_name, f"{path}/{index}")
        item_schema = schema.get("items")
        if item_schema is False and len(instance) > len(prefix):
            yield _issue(fixture, schema_name, path, "items", "additional array items are not allowed")
        elif isinstance(item_schema, dict):
            start = len(prefix) if prefix else 0
            for index in range(start, len(instance)):
                yield from _validate(instance[index], item_schema, root, fixture, schema_name, f"{path}/{index}")
        return
    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in sorted(required):
            if key not in instance:
                yield _issue(fixture, schema_name, f"{path}/{_escape(key)}", "required", f"required property {key!r} is missing")
        properties = schema.get("properties", {})
        allowed = set(properties)
        for key in sorted(instance):
            if key in properties:
                yield from _validate(instance[key], properties[key], root, fixture, schema_name, f"{path}/{_escape(key)}")
            elif schema.get("additionalProperties") is False:
                yield _issue(fixture, schema_name, f"{path}/{_escape(key)}", "additionalProperties", f"unexpected property {key!r}")
            elif isinstance(schema.get("additionalProperties"), dict):
                yield from _validate(instance[key], schema["additionalProperties"], root, fixture, schema_name, f"{path}/{_escape(key)}")


def _resolve_ref(root: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValueError(f"unsupported schema reference {ref}")
    node: Any = root
    for token in ref[2:].split("/"):
        node = node[token.replace("~1", "/").replace("~0", "~")]
    return node


def _matches_type(value: Any, type_name: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "boolean": isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
    }[type_name]


def _escape(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def _rel(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def _issue(fixture: str, schema: str, path: str, constraint: str, message: str) -> ValidationIssue:
    return ValidationIssue(fixture, schema, path, constraint, message)
