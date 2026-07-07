"""External dependency-algebra adapter.

This adapter never substitutes the local reference implementation. If no external
repository executable/CLI/package is available, it returns UNOBSERVED evidence.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from conformance.adapter_api import RepositoryAdapter
from conformance.jsonutil import canonical_hash, read_json, write_json
from conformance.models import CanonicalEvidence, CanonicalFixture
from conformance.schema_validation import EvidenceSchemaError, validate_evidence_file


class DependencyAlgebraExternalAdapter(RepositoryAdapter):
    def __init__(self, config: dict):
        self.config = config
        self.execution_failure: str | None = None
        self.schema_failure: str | None = None
        self.command: list[str] = []

    def load_canonical_fixture(self, fixture: CanonicalFixture) -> CanonicalFixture:
        return fixture

    def _resolve_command(self) -> list[str] | None:
        if "cli" in self.config:
            cli = self.config["cli"]
            executable = shutil.which(cli[0]) if isinstance(cli, list) and cli else shutil.which(str(cli))
            if executable:
                return [executable, *cli[1:]] if isinstance(cli, list) else [executable]
        if "executable" in self.config:
            executable = Path(self.config["executable"])
            if executable.exists() and os.access(executable, os.X_OK):
                return [str(executable)]
        if "python_package" in self.config:
            package = self.config["python_package"]
            found = subprocess.run([sys.executable, "-c", f"import {package}"], check=False, capture_output=True, text=True)
            if found.returncode == 0:
                return [sys.executable, "-m", package]
        return None

    def execute_implementation(self, fixture: CanonicalFixture, artifact_dir: Path) -> Path:
        fixture_input = artifact_dir / "fixture.json"
        raw_output = artifact_dir / "raw-evidence.json"
        write_json(fixture_input, fixture)
        base_command = self._resolve_command()
        if base_command is None:
            self.execution_failure = "dependency-algebra external implementation unavailable"
            self._write_unobserved(raw_output, fixture)
            return raw_output
        self.command = [*base_command, "--fixture", str(fixture_input), "--output", str(raw_output)]
        completed = subprocess.run(self.command, cwd=self.config.get("repository_path"), check=False, text=True, capture_output=True)
        (artifact_dir / "execution.stdout").write_text(completed.stdout, encoding="utf-8")
        (artifact_dir / "execution.stderr").write_text(completed.stderr, encoding="utf-8")
        (artifact_dir / "command.txt").write_text(" ".join(self.command) + "\n", encoding="utf-8")
        if completed.returncode != 0:
            self.execution_failure = f"external adapter command failed with exit code {completed.returncode}"
            self._write_unobserved(raw_output, fixture)
        return raw_output

    def _write_unobserved(self, raw_output: Path, fixture: CanonicalFixture) -> None:
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        raw = {
            "repository": "dependency-algebra",
            "repository_url": self.config.get("repository_url", "UNOBSERVED"),
            "commit_sha": self.config.get("commit_sha", "UNOBSERVED"),
            "branch": self.config.get("branch", "UNOBSERVED"),
            "implementation_version": self.config.get("implementation_version", "UNOBSERVED"),
            "research_object_id": fixture.research_object_id,
            "fixture_id": fixture.fixture_id,
            "observed_execution_timestamp": now,
            "canonical_projection_timestamp": fixture.deterministic_timestamp,
            "semantic_result": "UNOBSERVED",
            "diagnostics": [{"code": "UNOBSERVED", "level": "warning", "message": self.execution_failure or "external implementation unavailable"}],
            "generated_artifacts": [],
            "structural_metrics": {},
            "provenance": {
                "command_executed": self.command,
                "tool_version": "conformance-0.1.0",
                "fixture_hash": canonical_hash(fixture),
                "canonical_input_hash": canonical_hash(fixture.input),
                "environment_metadata": {"python": sys.version.split()[0]},
                "working_tree_clean": self.config.get("working_tree_clean", "unknown"),
            },
            "dependency_relations": [],
            "structural_invariants": {},
            "canonical_outputs": {},
            "required_diagnostics": [],
            "proof_obligations": {},
            "execution_failure": False,
            "schema_failure": False,
            "run_mode": "external",
        }
        write_json(raw_output, raw)

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
            repository=raw_evidence.get("repository", "dependency-algebra"),
            repository_url=raw_evidence.get("repository_url", "UNOBSERVED"),
            commit_sha=raw_evidence.get("commit_sha", "UNOBSERVED"),
            branch=raw_evidence.get("branch", "UNOBSERVED"),
            implementation_version=raw_evidence.get("implementation_version", "UNOBSERVED"),
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
            execution_failure=bool(raw_evidence.get("execution_failure", False)),
            schema_failure=bool(self.schema_failure or raw_evidence.get("schema_failure", False)),
            run_mode="external",
        )


def create_adapter(config: dict) -> DependencyAlgebraExternalAdapter:
    return DependencyAlgebraExternalAdapter(config)
