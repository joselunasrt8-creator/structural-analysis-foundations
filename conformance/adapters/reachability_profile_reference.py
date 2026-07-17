"""Bounded reference realization of the canonical reachability profile."""

from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Any

from conformance.adapter_api import RepositoryAdapter
from conformance.jsonutil import canonical_hash, read_json, write_json
from conformance.models import CanonicalEvidence, CanonicalFixture
from conformance.schema_validation import validate_evidence_file


def _require_identifiers(value: Any, field: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or (nonempty and not value):
        raise ValueError(f"{field} must be a{' non-empty' if nonempty else ''} list")
    if any(not isinstance(item, str) or not item for item in value):
        raise ValueError(f"{field} must contain non-empty string identifiers")
    if len(value) != len(set(value)):
        raise ValueError(f"{field} must not contain duplicate identifiers")
    return sorted(value)


def realize_reachability_profile(fixture_input: dict[str, Any]) -> dict[str, Any]:
    """Validate and evaluate the fixture's finite directed structural object."""
    if not isinstance(fixture_input, dict):
        raise ValueError("input must be an object")
    structural_object = fixture_input.get("canonical_structural_object")
    workload = fixture_input.get("workload")
    if not isinstance(structural_object, dict) or not isinstance(workload, dict):
        raise ValueError("input must contain canonical_structural_object and workload objects")

    nodes = _require_identifiers(structural_object.get("nodes"), "nodes")
    roots = _require_identifiers(workload.get("roots"), "roots", nonempty=True)
    targets = _require_identifiers(workload.get("targets"), "targets", nonempty=True)
    relations_value = structural_object.get("relations")
    if not isinstance(relations_value, list):
        raise ValueError("relations must be a list")
    relations: list[tuple[str, str]] = []
    for index, relation in enumerate(relations_value):
        if (
            not isinstance(relation, list)
            or len(relation) != 2
            or any(not isinstance(item, str) or not item for item in relation)
        ):
            raise ValueError(f"relations[{index}] must be a pair of non-empty string identifiers")
        relations.append((relation[0], relation[1]))
    relations.sort()
    if len(relations) != len(set(relations)):
        raise ValueError("relations must not contain duplicate pairs")

    node_set = set(nodes)
    referenced = set(roots) | set(targets) | {item for relation in relations for item in relation}
    unknown = sorted(referenced - node_set)
    if unknown:
        raise ValueError(f"all workload and relation identifiers must be nodes; unknown: {', '.join(unknown)}")

    adjacency = {node: [] for node in nodes}
    for source, target in relations:
        adjacency[source].append(target)

    reachable_pairs: list[list[str]] = []
    unreachable_pairs: list[list[str]] = []
    for root in roots:
        visited = {root}
        queue = deque([root])
        while queue:
            for successor in adjacency[queue.popleft()]:
                if successor not in visited:
                    visited.add(successor)
                    queue.append(successor)
        for target in targets:
            (reachable_pairs if target in visited else unreachable_pairs).append([root, target])

    universe_count = len(roots) * len(targets)
    reachable_count = len(reachable_pairs)
    density = reachable_count / universe_count
    root_coverage = {root: sum(pair[0] == root for pair in reachable_pairs) for root in roots}
    target_coverage = {target: sum(pair[1] == target for pair in reachable_pairs) for target in targets}
    outputs = {
        "reachability_density": density,
        "reachable_pairs": reachable_pairs,
        "root_coverage": root_coverage,
        "target_coverage": target_coverage,
        "unreachable_pairs": unreachable_pairs,
    }
    metrics = {
        "node_count": len(nodes),
        "pair_universe_count": universe_count,
        "reachability_density": density,
        "reachable_pair_count": reachable_count,
        "relation_count": len(relations),
        "root_count": len(roots),
        "target_count": len(targets),
        "unreachable_pair_count": len(unreachable_pairs),
    }
    invariants = {
        "coverage_counts_consistent": sum(root_coverage.values()) == reachable_count == sum(target_coverage.values()),
        "density_consistent": density == reachable_count / universe_count,
        "exclusive_classification": not ({tuple(pair) for pair in reachable_pairs} & {tuple(pair) for pair in unreachable_pairs}),
        "pair_universe_complete": reachable_count + len(unreachable_pairs) == universe_count,
    }
    diagnostics = [
        {"code": "CANONICAL_ORDERING_CONFIRMED", "level": "info"},
        {"code": "REACHABILITY_INVARIANTS_VERIFIED", "level": "info"},
        {"code": "REACHABILITY_PROFILE_EVALUATED", "level": "info"},
    ]
    return {"canonical_outputs": outputs, "structural_metrics": metrics, "structural_invariants": invariants, "required_diagnostics": diagnostics}


class ReachabilityProfileReferenceAdapter(RepositoryAdapter):
    """Evaluate only the finite canonical object carried by the fixture."""

    def __init__(self, config: dict[str, Any]):
        self.config = config

    def load_canonical_fixture(self, fixture: CanonicalFixture) -> CanonicalFixture:
        realize_reachability_profile(fixture.input)
        return fixture

    def execute_implementation(self, fixture: CanonicalFixture, artifact_dir: Path) -> Path:
        result = realize_reachability_profile(fixture.input)
        raw_path = artifact_dir / "raw-evidence.json"
        raw = {
            "branch": "local",
            "canonical_outputs": result["canonical_outputs"],
            "canonical_projection_timestamp": fixture.deterministic_timestamp,
            "commit_sha": "repository-worktree",
            "diagnostics": result["required_diagnostics"],
            "fixture_id": fixture.fixture_id,
            "generated_artifacts": [],
            "implementation_version": "reachability-profile-reference-v1",
            "observed_execution_timestamp": fixture.deterministic_timestamp,
            "provenance": {"canonical_input_hash": canonical_hash(fixture.input), "tool_version": "conformance-0.1.0"},
            "repository": "structural-analysis-foundations",
            "repository_url": "local://conformance/adapters/reachability_profile_reference.py",
            "required_diagnostics": result["required_diagnostics"],
            "research_object_id": fixture.research_object_id,
            "run_mode": "reference",
            "semantic_result": "PASS" if all(result["structural_invariants"].values()) else "FAIL",
            "structural_invariants": result["structural_invariants"],
            "structural_metrics": result["structural_metrics"],
        }
        write_json(raw_path, raw)
        return raw_path

    def capture_evidence(self, raw_artifact: Path) -> dict:
        return validate_evidence_file(raw_artifact)

    def normalize_output(self, raw_evidence: dict, fixture: CanonicalFixture) -> CanonicalEvidence:
        return CanonicalEvidence(**raw_evidence)


def create_adapter(config: dict[str, Any]) -> ReachabilityProfileReferenceAdapter:
    return ReachabilityProfileReferenceAdapter(config)
