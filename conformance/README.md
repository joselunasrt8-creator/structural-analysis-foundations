# SYNAPSE Phase 2 Conformance Harness

This module is the deterministic bridge from published research objects to implementation evidence. Papers define semantics; implementations are hypotheses; the harness decides whether observed evidence conforms.

## Current Phase 2 Boundary

This PR completes the first stage only:

```text
Research Specification
  ↓
Reference Implementation
  ↓
Harness Validation
```

It also adds the external adapter boundary needed for the next stage:

```text
External Repository Adapter
  ↓
Observed Evidence
  ↓
Semantic Comparison
  ↓
Deterministic Conformance
```

A reference result validates the harness mechanics. It is not external repository conformance. A conformance `PASS` is reserved for an independently executed implementation preserving the semantics defined by the canonical research object.

## Topology

```mermaid
flowchart TD
  A[Research Paper] --> B[Canonical Research Object]
  B --> C[Canonical Fixture]
  C --> D[Conformance Harness]
  D --> R[Reference Adapter]
  R --> HV[Harness Validation]
  D --> E[External Repository Adapter]
  E --> F[Implementation Execution]
  F --> G[Observed Evidence]
  G --> H[Semantic Comparator]
  H --> I{REFERENCE_PASS / REFERENCE_FAIL / CONFORMANCE_PASS / CONFORMANCE_DRIFT / CONFORMANCE_FAIL / UNOBSERVED}
```

## Components

- `fixture_loader.py` loads canonical fixtures and verifies the fixture targets the stated research object.
- `adapter_api.py` defines the repository adapter plugin contract.
- `models.py` defines canonical fixture, evidence, replay, and result objects.
- `engine.py` orchestrates fixture loading, two-pass replay execution, evidence capture, hash generation, comparison, and reporting.
- `comparator.py` compares semantics rather than formatting, ordering, or serialization details.
- `reporter.py` writes deterministic result artifacts.
- `adapters/dependency_predicate_reference.py` is the local reference adapter for validating the harness path.
- `adapters/dependency_algebra_external.py` is the external adapter boundary for an actual `dependency-algebra` implementation. It returns `UNOBSERVED` when the implementation is unavailable.
- `fixtures/dependency-predicate.fixture.json` is the reference fixture for Paper 1's Dependency Predicate research object.
- `fixtures/dependency-predicate.external.fixture.json` is the external fixture for dependency-algebra observation.
- `schemas/evidence.schema.json` documents the canonical evidence envelope.

## Adapter Contract

Every repository adapter must implement:

1. Load canonical fixture.
2. Execute implementation.
3. Capture evidence.
4. Validate raw evidence against `schemas/evidence.schema.json`.
5. Normalize output.
6. Return a canonical evidence object.

Core harness code must not contain repository-specific execution details. Implementation details belong in adapter plugins and fixture adapter configuration.

## Evidence and Provenance

Every evidence artifact must include repository identity, repository URL, commit SHA, branch, implementation version, command executed, tool version, fixture hash, canonical input hash, canonical evidence hash, environment metadata, and working tree cleanliness when available.

The schema intentionally permits extension inside `diagnostics`, `generated_artifacts`, semantic maps, and `provenance` so future adapters can carry implementation-specific proof details without changing core harness identity fields.

## Replay Determinism

Every fixture is executed twice:

- `run-a/evidence.json`
- `run-b/evidence.json`
- `replay.json`

The harness compares canonical evidence hashes. Observed runtime timestamps are preserved as reality in `observed_execution_timestamp`; deterministic comparison uses `canonical_projection_timestamp` and a canonical projection that excludes the observed runtime timestamp.

## Deterministic Execution

Validate the reference harness path:

```bash
python -m conformance --fixture conformance/fixtures/dependency-predicate.fixture.json
```

Observe the external adapter boundary:

```bash
python -m conformance --fixture conformance/fixtures/dependency-predicate.external.fixture.json
```

If `dependency-algebra` is unavailable, the external path reports `UNOBSERVED`, never `PASS`.

The command writes deterministic artifacts under `conformance/artifacts/<fixture-id>/<adapter-name>/`:

- `run-a/evidence.json`
- `run-b/evidence.json`
- `evidence.json`
- `report.json`
- `replay.json`
- `fixture.sha256`
- `evidence.sha256`
- `report.sha256`
