"""Deterministic Draft 2020-12 validation for canonical fixture contracts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker, SchemaError
from jsonschema.exceptions import ValidationError

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
    fixture_name = _display_path(fixture_path, repo_root)
    declared = fixture_data.get("schema_path")
    if not isinstance(declared, str) or not declared:
        raise SchemaValidationFailure([
            ValidationIssue(fixture_name, "<undeclared>", "$", "required", "fixture must declare schema_path")
        ])
    if Path(declared).is_absolute():
        raise SchemaValidationFailure([
            ValidationIssue(fixture_name, declared, "$/schema_path", "repositoryBoundary", "schema_path must be repository-relative")
        ])

    repo_root_resolved = repo_root.resolve()
    candidate = (repo_root_resolved / declared).resolve()
    if not _is_relative_to(candidate, repo_root_resolved):
        raise SchemaValidationFailure([
            ValidationIssue(fixture_name, declared, "$/schema_path", "repositoryBoundary", "schema_path must remain within the repository")
        ])
    if not candidate.exists():
        raise SchemaValidationFailure([
            ValidationIssue(fixture_name, _display_path(candidate, repo_root_resolved), "$/schema_path", "schemaExists", "declared schema file does not exist")
        ])
    if not candidate.is_file():
        raise SchemaValidationFailure([
            ValidationIssue(fixture_name, _display_path(candidate, repo_root_resolved), "$/schema_path", "schemaFile", "declared schema path must be a regular file")
        ])
    return candidate


def validate_all(repo_root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    repo_root = repo_root.resolve()
    for fixture_path in discover_fixtures(repo_root):
        fixture_name = _display_path(fixture_path, repo_root)
        try:
            fixture_data = read_json(fixture_path)
        except Exception as exc:  # pragma: no cover - fixture JSON parsing is covered by existing repository tests.
            issues.append(ValidationIssue(fixture_name, "<unknown>", "$", "fixtureReadable", str(exc)))
            continue
        try:
            schema_path = schema_path_for_fixture(fixture_data, fixture_path, repo_root)
            schema = read_json(schema_path)
        except SchemaValidationFailure as exc:
            issues.extend(exc.issues)
            continue
        except Exception as exc:
            schema_name = str(fixture_data.get("schema_path", "<unknown>"))
            issues.append(ValidationIssue(fixture_name, schema_name, "$/schema_path", "schemaReadable", str(exc)))
            continue
        issues.extend(validate_instance(fixture_data, schema, fixture_name, _display_path(schema_path, repo_root)))
    return sorted_issues(issues)


def validate_instance(instance: Any, schema: dict[str, Any], fixture: str, schema_name: str) -> list[ValidationIssue]:
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        return [ValidationIssue(fixture, schema_name, _json_path(exc.absolute_path), "schema", exc.message)]

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return sorted_issues(_issue_from_error(error, fixture, schema_name) for error in validator.iter_errors(instance))


def format_issues(issues: list[ValidationIssue]) -> str:
    lines = ["canonical fixture schema validation failed:"]
    for issue in sorted_issues(issues):
        lines.append(
            f"- fixture={issue.fixture} schema={issue.schema} path={issue.json_path} "
            f"constraint={issue.constraint} message={issue.message}"
        )
    return "\n".join(lines)


def sorted_issues(issues) -> list[ValidationIssue]:
    return sorted(issues, key=lambda e: (e.fixture, e.schema, e.json_path, e.constraint, e.message))


def _issue_from_error(error: ValidationError, fixture: str, schema_name: str) -> ValidationIssue:
    return ValidationIssue(
        fixture=fixture,
        schema=schema_name,
        json_path=_json_path(error.absolute_path),
        constraint=str(error.validator),
        message=error.message,
    )


def _json_path(tokens) -> str:
    path = "$"
    for token in tokens:
        path += f"/{_escape(str(token))}"
    return path


def _escape(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def _display_path(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False
