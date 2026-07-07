"""Deterministic reference command for the dependency-algebra adapter contract.

The command intentionally lives outside the core harness. It represents the first
bounded implementation plugin path for Paper 1's dependency predicate.
"""

from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path


def reachable(edges: list[list[str]], roots: list[str], targets: list[str], removed: list[str]) -> bool:
    removed_set = set(removed)
    target_set = set(targets) - removed_set
    adjacency: dict[str, list[str]] = {}
    for source, target in edges:
        if source in removed_set or target in removed_set:
            continue
        adjacency.setdefault(source, []).append(target)
    queue = deque(root for root in roots if root not in removed_set)
    seen = set(queue)
    while queue:
        node = queue.popleft()
        if node in target_set:
            return True
        for nxt in sorted(adjacency.get(node, [])):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    fixture = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
    graph = fixture["input"]["graph"]
    workload = fixture["input"]["workload"]
    candidate = workload["candidate_component_set"]
    before = reachable(graph["edges"], workload["roots"], workload["targets"], [])
    after = reachable(graph["edges"], workload["roots"], workload["targets"], candidate)
    dependency_holds = before and not after
    output = {
        "repository": "dependency-algebra",
        "implementation_version": "reference-command-v1",
        "research_object_id": fixture["research_object_id"],
        "fixture_id": fixture["fixture_id"],
        "execution_timestamp": fixture["deterministic_timestamp"],
        "semantic_result": "PASS" if dependency_holds else "FAIL",
        "dependency_relations": [{"candidate_set": candidate, "predicate": "removal_eliminates_root_to_target_reachability", "holds": dependency_holds}],
        "structural_invariants": {"reachable_before_removal": before, "reachable_after_removal": after, "removed_components": candidate},
        "canonical_outputs": {"is_dependency": dependency_holds},
        "required_diagnostics": [{"code": "DEPENDENCY_PREDICATE_EVALUATED", "level": "info"}],
        "proof_obligations": {"root_to_target_reachability_eliminated": dependency_holds},
        "diagnostics": [{"code": "REFERENCE_EXECUTION", "level": "info", "message": "deterministic dependency predicate evaluation completed"}],
        "generated_artifacts": [],
        "structural_metrics": {"node_count": len(graph["nodes"]), "edge_count": len(graph["edges"]), "candidate_set_size": len(candidate)},
        "provenance": {"command": "conformance.tools.dependency_algebra_reference", "fixture_digest_mode": "canonical-json"},
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
