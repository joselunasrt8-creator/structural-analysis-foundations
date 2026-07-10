from __future__ import annotations

import copy
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

    def _issues_for(self, data: dict):
        return validate_instance(data, self.schema, FIXTURE, SCHEMA)

    def assertHasIssue(self, issues, path: str, constraint: str) -> None:
        self.assertTrue(
            any(issue.json_path == path and issue.constraint == constraint for issue in issues),
            f"expected {constraint} at {path}, got {issues!r}",
        )

    def test_registered_repository_fixtures_validate(self) -> None:
        self.assertEqual(validate_all(ROOT), [])

    def test_missing_required_field_fails(self) -> None:
        data = copy.deepcopy(self.fixture)
        del data["expected_semantics"]["canonical_outputs"]
        self.assertHasIssue(self._issues_for(data), "$/expected_semantics/canonical_outputs", "required")

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
        self.assertHasIssue(self._issues_for(data), "$/expected_semantics/structural_invariants/density_consistent", "required")

    def test_unknown_property_fails(self) -> None:
        data = copy.deepcopy(self.fixture)
        data["unexpected"] = True
        self.assertHasIssue(self._issues_for(data), "$/unexpected", "additionalProperties")

    def test_empty_workload_fails(self) -> None:
        data = copy.deepcopy(self.fixture)
        data["input"]["workload"]["roots"] = []
        self.assertHasIssue(self._issues_for(data), "$/input/workload/roots", "minItems")


if __name__ == "__main__":
    unittest.main()
