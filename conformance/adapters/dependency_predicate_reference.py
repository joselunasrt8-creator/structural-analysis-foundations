"""Reference-only adapter for validating the dependency predicate harness path."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from conformance.adapter_api import RepositoryAdapter
from conformance.jsonutil import read_json, write_json
from conformance.models import CanonicalEvidence, CanonicalFixture
from conformance.schema_validation import EvidenceSchemaError, validate_evidence_file


class DependencyPredicateReferenceAdapter(RepositoryAdapter):
    """Execute the local reference command.

    This adapter validates harness mechanics. It is not evidence that an external
    dependency-algebra repository conforms.
    """

    def __init__(self, config: dict):
        self.config = config
        self.schema_failure: str | None = None

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
        (artifact_dir / "command.txt").write_text(" ".join(command) + "\n", encoding="utf-8")
        if completed.returncode != 0:
            raise RuntimeError(f"reference adapter command failed with exit code {completed.returncode}")
        return raw_output

    def capture_evidence(self, raw_artifact: Path) -> dict:
        try:
            return validate_evidence_file(raw_artifact)
        except EvidenceSchemaError as exc:
            self.schema_failure = str(exc)
            raw = read_json(raw_artifact) if raw_artifact.exists() else {}
            raw["schema_failure"] = True
            raw.setdefault("diagnostics", []).append({"code": "SCHEMA_FAILURE", "level": "error", "message": str(exc)})
            return raw

    def normalize_output(self, raw_evidence: dict, fixture: CanonicalFixture) -> CanonicalEvidence:
        return CanonicalEvidence(
            repository=raw_evidence.get("repository", "dependency-predicate-reference"),
            repository_url=raw_evidence.get("repository_url", "local://conformance/tools/dependency_algebra_reference.py"),
            commit_sha=raw_evidence.get("commit_sha", "unknown"),
            branch=raw_evidence.get("branch", "unknown"),
            implementation_version=raw_evidence.get("implementation_version", "unknown"),
            research_object_id=raw_evidence.get("research_object_id", fixture.research_object_id),
            fixture_id=raw_evidence.get("fixture_id", fixture.fixture_id),
            observed_execution_timestamp=raw_evidence.get("observed_execution_timestamp", "unknown"),
            canonical_projection_timestamp=raw_evidence.get("canonical_projection_timestamp", fixture.deterministic_timestamp),
            semantic_result=raw_evidence.get("semantic_result", "FAIL" if self.schema_failure else "UNKNOWN"),
            diagnostics=raw_evidence.get("diagnostics", []),
            generated_artifacts=raw_evidence.get("generated_artifacts", []),
            structural_metrics=raw_evidence.get("structural_metrics", {}),
            provenance=raw_evidence.get("provenance", {}),
            dependency_relations=raw_evidence.get("dependency_relations", []),
            structural_invariants=raw_evidence.get("structural_invariants", {}),
            canonical_outputs=raw_evidence.get("canonical_outputs", {}),
            required_diagnostics=raw_evidence.get("required_diagnostics", []),
            proof_obligations=raw_evidence.get("proof_obligations", {}),
            execution_failure=False,
            schema_failure=bool(self.schema_failure or raw_evidence.get("schema_failure", False)),
            run_mode="reference",
        )


def create_adapter(config: dict) -> DependencyPredicateReferenceAdapter:
    return DependencyPredicateReferenceAdapter(config)
