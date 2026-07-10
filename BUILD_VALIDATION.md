# Build Validation Status

Date: 2026-07-06

## Intent

Validate independent LaTeX builds for all three paper directories without modifying manuscript content or overwriting canonical PDFs.

## Scope

Paper directories checked:

- `paper-1-dependency/`
- `paper-2-canonical-structural-analysis/`
- `paper-3-foundations-structural-analysis/`

Required command per paper:

```sh
latexmk -pdf main.tex
```

## Preserved invariants

- Manuscript content was not modified.
- Canonical PDFs under each `pdf/` directory were not overwritten.
- Validation was attempted against the checked-out repository state.

## Environment result

The current Codex environment does not include a LaTeX build toolchain:

- `latexmk` is unavailable.
- `pdflatex` is unavailable.
- `xelatex` is unavailable.
- `lualatex` is unavailable.

An attempted package-manager install path was blocked by the execution environment: `apt-get update && apt-get install -y latexmk` failed because configured Ubuntu package repositories returned HTTP 403 responses through the proxy.

## Per-paper validation

| Paper directory | `main.tex` | `references.bib` | Canonical PDF under `pdf/` | Build command | Result |
| --- | --- | --- | --- | --- | --- |
| `paper-1-dependency/` | Present | Present | `pdf/paper1.pdf` present | `latexmk -pdf main.tex` | Blocked: `latexmk: command not found` |
| `paper-2-canonical-structural-analysis/` | Present | Present | `pdf/paper2.pdf` present | `latexmk -pdf main.tex` | Blocked: `latexmk: command not found` |
| `paper-3-foundations-structural-analysis/` | Present | Present | `pdf/paper3.pdf` present | `latexmk -pdf main.tex` | Blocked: `latexmk: command not found` |

## Unvalidated items

Because no LaTeX engine was available, the following checks remain unresolved:

- Bibliography resolution.
- Repeated compilation for labels and citations.
- Generated PDF production.
- Generated PDF comparison against checked-in canonical PDFs.

## Remaining blocker

The remaining blocker is environmental LaTeX tooling availability, not repository structure. Re-run this validation in an environment with `latexmk` and a complete TeX distribution installed.

## Research object validation

Phase 1 research-object metadata can be validated without changing paper builds:

```sh
python tools/validate_research_objects.py
python tools/validate_canonical_fixtures.py
```

`python tools/validate_canonical_fixtures.py` validates every canonical fixture discovered under `conformance/fixtures/*.fixture.json` against its declared `schema_path` and reports deterministic fixture, schema, JSON path, constraint, and message fields on failure.

This command validates the schema JSON, paper manifests, manifest file references, seed research objects, source anchors, line ranges, dependency targets, and stable object IDs.

Validator rejection behavior is covered by local negative tests:

```sh
python -m unittest tests/test_validate_research_objects.py
```
