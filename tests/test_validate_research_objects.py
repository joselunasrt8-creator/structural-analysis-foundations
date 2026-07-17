#!/usr/bin/env python3
"""Negative tests for the Phase 1 research-object validator."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import validate_research_objects as validator  # noqa: E402


class ResearchObjectValidatorNegativeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "schemas").mkdir()
        shutil.copy2(ROOT / "schemas" / "research-object.schema.json", self.root / "schemas" / "research-object.schema.json")
        self.paper = self.root / "paper-1-example"
        (self.paper / "research-objects").mkdir(parents=True)
        (self.paper / "README.md").write_text("# Example\n", encoding="utf-8")
        (self.paper / "references.bib").write_text("", encoding="utf-8")
        (self.paper / "pdf").mkdir()
        (self.paper / "pdf" / "paper.pdf").write_text("placeholder\n", encoding="utf-8")
        (self.paper / "main.tex").write_text(
            "\\begin{definition}\n\\label{def:example}\nExample.\n\\end{definition}\n",
            encoding="utf-8",
        )
        self.object_rel = "research-objects/definition.example.example.json"
        self.obj = {
            "id": "definition.example.example",
            "kind": "definition",
            "domain": "example",
            "slug": "example",
            "version": "v1",
            "title": "Example",
            "paper": "paper-1-example",
            "canonical_statement": "Example canonical statement.",
            "provenance": {"source": {"file": "main.tex", "anchor": "def:example", "lines": [1, 4]}},
            "dependencies": [],
            "validation": {"status": "not_validated"},
            "exports": {},
            "lifecycle_status": "draft",
            "maturity": "seed",
            "authority_status": "noncanonical",
        }
        self.write_object(self.object_rel, self.obj)
        self.write_manifest(["README.md", "main.tex", "references.bib", "pdf/paper.pdf"], [self.object_rel])

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write_manifest(self, files: list[str], objects: list[str], paper: str = "paper-1-example") -> None:
        body = [f"paper: {paper}", "title: Example", "manifest_version: 1", "files:"]
        body.extend(f"  - {item}" for item in files)
        body.append("research_objects:")
        body.extend(f"  - {item}" for item in objects)
        (self.paper / "paper.yml").write_text("\n".join(body) + "\n", encoding="utf-8")

    def write_object(self, rel: str, obj: dict) -> None:
        path = self.paper / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")

    def assert_invalid_contains(self, expected: str) -> None:
        _manifest_count, _object_count, errors = validator.validate(self.root)
        self.assertTrue(errors, "fixture unexpectedly validated successfully")
        self.assertTrue(any(expected in error for error in errors), f"expected {expected!r} in errors: {errors}")

    def test_duplicate_object_id_is_rejected(self) -> None:
        duplicate = dict(self.obj)
        duplicate["slug"] = "duplicate"
        self.write_object("research-objects/definition.example.duplicate.json", duplicate)
        self.write_manifest(["README.md", "main.tex", "references.bib", "pdf/paper.pdf"], [self.object_rel, "research-objects/definition.example.duplicate.json"])
        self.assert_invalid_contains("duplicate id definition.example.example")

    def test_malformed_id_is_rejected(self) -> None:
        self.obj["id"] = "bad-id"
        self.write_object(self.object_rel, self.obj)
        self.assert_invalid_contains("invalid id")

    def test_missing_referenced_file_is_rejected(self) -> None:
        self.write_manifest(["README.md", "missing.tex", "references.bib", "pdf/paper.pdf"], [self.object_rel])
        self.assert_invalid_contains("missing file reference missing.tex")

    def test_nonexistent_source_anchor_is_rejected(self) -> None:
        self.obj["provenance"]["source"]["anchor"] = "def:missing"
        self.write_object(self.object_rel, self.obj)
        self.assert_invalid_contains("source anchor 'def:missing' not found")

    def test_unresolved_dependency_is_rejected(self) -> None:
        self.obj["dependencies"] = [{"id": "definition.example.missing", "relation": "depends_on"}]
        self.write_object(self.object_rel, self.obj)
        self.assert_invalid_contains("unresolved dependency target definition.example.missing")

    def test_invalid_lifecycle_status_is_rejected(self) -> None:
        self.obj["lifecycle_status"] = "canonical"
        self.write_object(self.object_rel, self.obj)
        self.assert_invalid_contains("invalid lifecycle_status")

    def test_canonical_authority_without_transition_evidence_is_rejected(self) -> None:
        self.obj["authority_status"] = "canonical"
        self.write_object(self.object_rel, self.obj)
        self.assert_invalid_contains("canonical authority requires maturity 'verified'")
        self.assert_invalid_contains("canonical authority requires at least one evidence_reference")

    def test_canonical_authority_with_review_and_evidence_is_accepted(self) -> None:
        (self.root / "reviews").mkdir()
        (self.root / "reviews" / "example.md").write_text("# Accepted review\n", encoding="utf-8")
        (self.root / "evidence").mkdir()
        (self.root / "evidence" / "example.txt").write_text("validated result\n", encoding="utf-8")
        self.obj.update(
            {
                "authority_status": "canonical",
                "maturity": "verified",
                "lifecycle_status": "reviewed",
                "validation": {"status": "validated"},
                "review_reference": {"file": "reviews/example.md", "anchor": "Accepted review"},
                "evidence_references": [{"file": "evidence/example.txt"}],
            }
        )
        self.write_object(self.object_rel, self.obj)
        _manifest_count, _object_count, errors = validator.validate(self.root)
        self.assertEqual([], errors)

    def test_canonical_evidence_must_be_repository_contained(self) -> None:
        self.obj.update(
            {
                "authority_status": "canonical",
                "maturity": "verified",
                "lifecycle_status": "reviewed",
                "validation": {"status": "validated"},
                "review_reference": {"file": "../outside-review.md"},
                "evidence_references": [{"file": "/tmp/outside-evidence.txt"}],
            }
        )
        self.write_object(self.object_rel, self.obj)
        self.assert_invalid_contains("review_reference.file must be repository-relative and contained")
        self.assert_invalid_contains("evidence_references[0].file must be repository-relative and contained")

    def test_paper_object_mismatch_is_rejected(self) -> None:
        self.obj["paper"] = "paper-2-example"
        self.write_object(self.object_rel, self.obj)
        self.assert_invalid_contains("paper does not match manifest")


if __name__ == "__main__":
    unittest.main()
