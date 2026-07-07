"""Deterministic reference command for the dependency predicate harness.

The command intentionally lives outside the core harness. It validates the first
bounded harness path and must not be treated as external repository conformance.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

from conformance.jsonutil import canonical_hash


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


def git_value(args: list[str], default: str) -> str:
    completed = subprocess.run(["git", *args], check=False, text=True, capture_output=True)
    return completed.stdout.strip() if completed.returncode == 0 and completed.stdout.strip() else default


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
    command = [sys.executable, "-m", "conformance.tools.dependency_algebra_reference", "--fixture", args.fixture, "--output", args.output]
    observed = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    status = git_value(["status", "--porcelain"], "unknown")
    output = {
        "repository": "dependency-predicate-reference",
        "repository_url": git_value(["config", "--get", "remote.origin.url"], "local://structural-analysis-foundations"),
        "commit_sha": git_value(["rev-parse", "HEAD"], "unknown"),
        "branch": git_value(["rev-parse", "--abbrev-ref", "HEAD"], "unknown"),
        "implementation_version": "reference-command-v2",
        "research_object_id": fixture["research_object_id"],
        "fixture_id": fixture["fixture_id"],
        "observed_execution_timestamp": observed,
        "canonical_projection_timestamp": fixture["deterministic_timestamp"],
        "semantic_result": "PASS" if dependency_holds else "FAIL",
        "dependency_relations": [{"candidate_set": candidate, "predicate": "removal_eliminates_root_to_target_reachability", "holds": dependency_holds}],
        "structural_invariants": {"reachable_before_removal": before, "reachable_after_removal": after, "removed_components": candidate},
        "canonical_outputs": {"is_dependency": dependency_holds},
        "required_diagnostics": [{"code": "DEPENDENCY_PREDICATE_EVALUATED", "level": "info"}],
        "proof_obligations": {"root_to_target_reachability_eliminated": dependency_holds},
        "diagnostics": [{"code": "REFERENCE_EXECUTION", "level": "info", "message": "deterministic dependency predicate reference evaluation completed"}],
        "generated_artifacts": [],
        "structural_metrics": {"node_count": len(graph["nodes"]), "edge_count": len(graph["edges"]), "candidate_set_size": len(candidate)},
        "provenance": {
            "command_executed": command,
            "tool_version": "conformance-0.1.0",
            "fixture_hash": canonical_hash(fixture),
            "canonical_input_hash": canonical_hash(fixture["input"]),
            "canonical_evidence_hash": "computed-after-normalization",
            "environment_metadata": {"python": sys.version.split()[0]},
            "working_tree_clean": status == "",
        },
        "execution_failure": False,
        "schema_failure": False,
        "run_mode": "reference",
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
