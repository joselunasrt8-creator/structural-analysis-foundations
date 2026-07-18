from __future__ import annotations

import copy
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from conformance.adapters.dependency_predicate_reference import DependencyPredicateReferenceAdapter
from conformance.adapters.reachability_profile_reference import ReachabilityProfileReferenceAdapter, realize_reachability_profile
from conformance.comparator import compare_semantics
from conformance.engine import canonical_evidence_projection, run_conformance
from conformance.fixture_loader import load_fixture
from conformance.jsonutil import canonical_hash, read_json
from conformance.models import ReplayResult

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "conformance/fixtures/canonical-reachability-profile.fixture.json"


class ReachabilityProfileReferenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = load_fixture(FIXTURE_PATH, ROOT)

    def test_comparator_includes_metrics_and_accepts_reference_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            evidence = ReachabilityProfileReferenceAdapter({}).run(self.fixture, Path(directory))
        replay = ReplayResult("a", "b", "hash", "hash", True, "canonical evidence hashes match")
        result = compare_semantics(self.fixture, evidence, "evidence", "report", "fixture-hash", "evidence-hash", replay)
        self.assertEqual(result.status, "REFERENCE_PASS")
        self.assertEqual(
            [item["check"] for item in result.diagnostics],
            ["dependency_relations", "structural_metrics", "structural_invariants", "canonical_outputs", "required_diagnostics", "proof_obligations"],
        )

        drifted_metrics = dict(evidence.structural_metrics)
        drifted_metrics["reachable_pair_count"] = 3
        drift = compare_semantics(
            self.fixture, replace(evidence, structural_metrics=drifted_metrics), "evidence", "report", "fixture-hash", "evidence-hash", replay
        )
        self.assertEqual(drift.status, "REFERENCE_FAIL")
        self.assertEqual([item["check"] for item in drift.diagnostics if item["result"] == "DRIFT"], ["structural_metrics"])

    def test_two_pass_replay_has_identical_canonical_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifacts = Path(directory)
            self.assertEqual(run_conformance(ROOT, FIXTURE_PATH, artifacts), 0)
            adapter_root = artifacts / self.fixture.fixture_id / "reachability-profile-reference"
            replay = read_json(adapter_root / "replay.json")
            evidence_a = read_json(adapter_root / "run-a/evidence.json")
            evidence_b = read_json(adapter_root / "run-b/evidence.json")
        self.assertTrue(replay["deterministic"])
        self.assertEqual(replay["run_a_canonical_evidence_hash"], replay["run_b_canonical_evidence_hash"])
        evidence_a["provenance"].pop("canonical_evidence_hash")
        evidence_b["provenance"].pop("canonical_evidence_hash")
        adapter = ReachabilityProfileReferenceAdapter({})
        projection_a = canonical_evidence_projection(adapter.normalize_output(evidence_a, self.fixture))
        projection_b = canonical_evidence_projection(adapter.normalize_output(evidence_b, self.fixture))
        self.assertEqual(
            canonical_hash(projection_a),
            canonical_hash(projection_b),
        )

    def test_legacy_reference_without_metric_expectations_still_passes(self) -> None:
        legacy_fixture = load_fixture(ROOT / "conformance/fixtures/dependency-predicate.fixture.json", ROOT)
        with tempfile.TemporaryDirectory() as directory:
            evidence = DependencyPredicateReferenceAdapter(legacy_fixture.adapter).run(legacy_fixture, Path(directory))
        replay = ReplayResult("a", "b", "hash", "hash", True, "canonical evidence hashes match")
        result = compare_semantics(legacy_fixture, evidence, "evidence", "report", "fixture-hash", "evidence-hash", replay)
        self.assertEqual(result.status, "REFERENCE_PASS")
        self.assertNotIn("structural_metrics", [item["check"] for item in result.diagnostics])

    def test_malformed_input_rejects_unknown_relation_endpoint(self) -> None:
        malformed = copy.deepcopy(self.fixture.input)
        malformed["canonical_structural_object"]["relations"].append(["r1", "missing"])
        with self.assertRaisesRegex(ValueError, "unknown: missing"):
            realize_reachability_profile(malformed)

    def test_malformed_input_rejects_duplicate_workload_identifier(self) -> None:
        malformed = copy.deepcopy(self.fixture.input)
        malformed["workload"]["roots"].append("r1")
        with self.assertRaisesRegex(ValueError, "roots must not contain duplicate identifiers"):
            realize_reachability_profile(malformed)


if __name__ == "__main__":
    unittest.main()
