"""Repository adapter contract for implementation-independent conformance."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from .models import CanonicalEvidence, CanonicalFixture


class RepositoryAdapter(ABC):
    """Plugin interface implemented by every repository adapter."""

    @abstractmethod
    def load_canonical_fixture(self, fixture: CanonicalFixture) -> CanonicalFixture:
        """Return the fixture representation consumed by the implementation."""

    @abstractmethod
    def execute_implementation(self, fixture: CanonicalFixture, artifact_dir: Path) -> Path:
        """Execute the implementation and return the raw evidence artifact path."""

    @abstractmethod
    def capture_evidence(self, raw_artifact: Path) -> dict:
        """Capture raw implementation evidence from generated artifacts."""

    @abstractmethod
    def normalize_output(self, raw_evidence: dict, fixture: CanonicalFixture) -> CanonicalEvidence:
        """Normalize raw evidence into the canonical evidence object."""

    def run(self, fixture: CanonicalFixture, artifact_dir: Path) -> CanonicalEvidence:
        loaded = self.load_canonical_fixture(fixture)
        raw_artifact = self.execute_implementation(loaded, artifact_dir)
        raw_evidence = self.capture_evidence(raw_artifact)
        return self.normalize_output(raw_evidence, loaded)
