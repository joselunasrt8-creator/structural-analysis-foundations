from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from conformance.fixture_schema_validator import validate_all, validate_instance
from conformance.jsonutil import read_json

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = "conformance/fixtures/canonical-reachability-profile.fixture.json"
SCHEMA = "schemas/canonical-reachability-profile.schema.json"


class CanonicalFixtureSchemaValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = read_json(ROOT / FIXTURE)
        self.schema = read_json(ROOT / SCHEMA)

    def _issues_for(self, data: dict, schema: dict | None = None):
        return validate_instance(data, schema or self.schema, FIXTURE, SCHEMA)

    def assertHasIssue(self, issues, path: str, constraint: str) -> None:
        self.assertTrue(
            any(issue.json_path == path and issue.constraint == constraint for issue in issues),
            f"expected {constraint} at {path}, got {issues!r}",
        )

    def _repo_with_fixture(
        self, root: Path, fixture: dict, schema: dict | None = None, schema_name: str = "schemas/test.schema.json"
    ) -> Path:
        (root / "conformance" / "fixtures").mkdir(parents=True)
        (root / "schemas").mkdir()
        fixture = copy.deepcopy(fixture)
        fixture["schema_path"] = schema_name
        (root / "conformance" / "fixtures" / "test.fixture.json").write_text(
            json.dumps(fixture, indent=2, sort_keys=True), encoding="utf-8"
        )
        if schema is not None:
            (root / schema_name).parent.mkdir(parents=True, exist_ok=True)
            (root / schema_name).write_text(json.dumps(schema, indent=2, sort_keys=True), encoding="utf-8")
        return root

    def test_registered_repository_fixtures_validate(self) -> None:
        self.assertEqual(validate_all(ROOT), [])

    def test_missing_required_field_fails(self) -> None:
        data = copy.deepcopy(self.fixture)
        del data["expected_semantics"]["canonical_outputs"]
        self.assertHasIssue(self._issues_for(data), "$/expected_semantics", "required")

    def test_invalid_research_object_id_fails(self) -> None:
        data = copy.deepcopy(self.fixture)
        data["research_object_id"] = "bad.id"
        self.assertHasIssue(self._issues_for(data), "$/research_object_id", "const")

    def test_malformed_pair_fails(self) -> None:
        data = copy.deepcopy(self.fixture)
        data["expected_semantics"]["canonical_outputs"]["reachable_pairs"][0] = ["r1"]
        self.assertHasIssue(self._issues_for(data), "$/expected_semantics/canonical_outputs/reachable_pairs/0", "minItems")

    def test_incomplete_invariant_set_fails(self) -> None:
        data = copy.deepcopy(self.fixture)
        del data["expected_semantics"]["structural_invariants"]["density_consistent"]
        self.assertHasIssue(self._issues_for(data), "$/expected_semantics/structural_invariants", "required")

    def test_unknown_property_fails(self) -> None:
        data = copy.deepcopy(self.fixture)
        data["unexpected"] = True
        self.assertHasIssue(self._issues_for(data), "$", "additionalProperties")

    def test_empty_workload_fails(self) -> None:
        data = copy.deepcopy(self.fixture)
        data["input"]["workload"]["roots"] = []
        self.assertHasIssue(self._issues_for(data), "$/input/workload/roots", "minItems")

    def test_invalid_date_time_fails(self) -> None:
        data = copy.deepcopy(self.fixture)
        data["deterministic_timestamp"] = "not-a-date"
        self.assertHasIssue(self._issues_for(data), "$/deterministic_timestamp", "format")

    def test_missing_schema_file_reports_controlled_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._repo_with_fixture(Path(directory), self.fixture, schema=None, schema_name="schemas/missing.schema.json")
            issues = validate_all(root)
        self.assertHasIssue(issues, "$/schema_path", "schemaExists")

    def test_absolute_schema_path_reports_boundary_failure(self) -> None:
        data = copy.deepcopy(self.fixture)
        data["schema_path"] = "/tmp/outside.schema.json"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "conformance" / "fixtures").mkdir(parents=True)
            (root / "conformance" / "fixtures" / "test.fixture.json").write_text(json.dumps(data), encoding="utf-8")
            issues = validate_all(root)
        self.assertHasIssue(issues, "$/schema_path", "repositoryBoundary")

    def test_schema_path_traversal_reports_boundary_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._repo_with_fixture(Path(directory), self.fixture, schema=None, schema_name="../outside.schema.json")
            issues = validate_all(root)
        self.assertHasIssue(issues, "$/schema_path", "repositoryBoundary")

    def test_malformed_schema_reports_schema_failure(self) -> None:
        schema = copy.deepcopy(self.schema)
        schema["type"] = 7
        self.assertHasIssue(self._issues_for(self.fixture, schema=schema), "$/type", "schema")


if __name__ == "__main__":
    unittest.main()
