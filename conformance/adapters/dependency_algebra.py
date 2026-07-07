"""Plugin adapter for dependency-algebra implementations."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from conformance.adapter_api import RepositoryAdapter
from conformance.jsonutil import read_json, write_json
from conformance.models import CanonicalEvidence, CanonicalFixture


class DependencyAlgebraAdapter(RepositoryAdapter):
    def __init__(self, config: dict):
        self.config = config

    def load_canonical_fixture(self, fixture: CanonicalFixture) -> CanonicalFixture:
        return fixture

    def execute_implementation(self, fixture: CanonicalFixture, artifact_dir: Path) -> Path:
        fixture_input = artifact_dir / "fixture.json"
        raw_output = artifact_dir / "raw-evidence.json"
        write_json(fixture_input, fixture)
        command = []
        for part in self.config["command"]:
            if part == "{python}":
                command.append(sys.executable)
            else:
                command.append(part.format(fixture=fixture_input, output=raw_output))
        completed = subprocess.run(command, check=False, text=True, capture_output=True)
        (artifact_dir / "execution.stdout").write_text(completed.stdout, encoding="utf-8")
        (artifact_dir / "execution.stderr").write_text(completed.stderr, encoding="utf-8")
        if completed.returncode != 0:
            raise RuntimeError(f"dependency-algebra adapter command failed with exit code {completed.returncode}")
        return raw_output

    def capture_evidence(self, raw_artifact: Path) -> dict:
        return read_json(raw_artifact)

    def normalize_output(self, raw_evidence: dict, fixture: CanonicalFixture) -> CanonicalEvidence:
        return CanonicalEvidence(
            repository=raw_evidence["repository"],
            implementation_version=raw_evidence["implementation_version"],
            research_object_id=raw_evidence["research_object_id"],
            fixture_id=raw_evidence["fixture_id"],
            execution_timestamp=fixture.deterministic_timestamp,
            semantic_result=raw_evidence.get("semantic_result", "UNKNOWN"),
            diagnostics=raw_evidence.get("diagnostics", []),
            generated_artifacts=raw_evidence.get("generated_artifacts", []),
            structural_metrics=raw_evidence.get("structural_metrics", {}),
            provenance=raw_evidence.get("provenance", {}),
            dependency_relations=raw_evidence.get("dependency_relations", []),
            structural_invariants=raw_evidence.get("structural_invariants", {}),
            canonical_outputs=raw_evidence.get("canonical_outputs", {}),
            required_diagnostics=raw_evidence.get("required_diagnostics", []),
            proof_obligations=raw_evidence.get("proof_obligations", {}),
        )


def create_adapter(config: dict) -> DependencyAlgebraAdapter:
    return DependencyAlgebraAdapter(config)
