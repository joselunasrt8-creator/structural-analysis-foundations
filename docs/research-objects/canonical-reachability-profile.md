# Canonical Research Object: Reachability Profile

## Purpose

The **Reachability Profile** is a canonical research object for measuring which targets are structurally reachable from which roots in a canonical structural object under a declared workload. It demonstrates that a canonical research object is a stable scientific artifact that can support multiple independent analyses without coupling the artifact to an implementation, optimizer, programming language, or execution environment.

This object sits in the architecture as:

```text
Real System
  ↓
Canonical Structural Object
  ↓
Canonical Research Object: Reachability Profile
  ↓
Specific Analysis or Implementation
```

The research object fixes the meaning of the observation and the evidence that must be produced. Implementations only realize that meaning.

## Inputs

A realization of the Reachability Profile consumes a canonical structural object and a workload descriptor.

Required input fields are:

- `canonical_structural_object`: a language-independent structural object with stable node identities and directed structural relations.
- `workload.roots`: a finite, ordered set of root node identifiers.
- `workload.targets`: a finite, ordered set of target node identifiers.
- `canonicalization`: the deterministic ordering and identity rules used to project equivalent representations to the same canonical input.

Optional input fields are allowed only when they do not change the mathematical meaning of reachability. Optional fields must be reported in provenance if they affect diagnostics or measurement coverage.

## Outputs

A realization emits a canonical profile containing:

- `reachable_pairs`: ordered root-target pairs for which a directed path exists.
- `unreachable_pairs`: ordered root-target pairs for which no directed path exists.
- `root_coverage`: the number of reachable targets for each root.
- `target_coverage`: the number of roots that can reach each target.
- `structural_measurements`: node count, edge count, root count, target count, reachable pair count, unreachable pair count, and reachability density.

The output is a structural observation, not an implementation trace. Runtime-specific details such as traversal algorithm, memory layout, queue discipline, or cache behavior are diagnostics only and cannot change the canonical output.

## Preconditions

A conforming realization must verify that:

1. Every root and target identifier is present in the canonical structural object.
2. Node identifiers are unique after canonicalization.
3. Structural relations reference only declared nodes.
4. The canonicalization rules produce a deterministic ordering of nodes, edges, roots, targets, and emitted pairs.
5. The workload is finite.

If any precondition fails, the realization must emit failing evidence rather than silently repairing the input.

## Postconditions

After successful realization:

1. Every ordered pair in `workload.roots × workload.targets` appears exactly once in either `reachable_pairs` or `unreachable_pairs`.
2. `reachable_pair_count + unreachable_pair_count = root_count × target_count`.
3. `root_coverage[root]` equals the number of reachable pairs whose first element is `root`.
4. `target_coverage[target]` equals the number of reachable pairs whose second element is `target`.
5. `reachability_density = reachable_pair_count / (root_count × target_count)` when the denominator is nonzero.
6. Evidence includes enough provenance to replay the same canonical input and compare the same canonical output.

## Canonical Schema

The canonical schema is documented in [`schemas/canonical-reachability-profile.schema.json`](../../schemas/canonical-reachability-profile.schema.json). The schema is intentionally independent of programming language, implementation strategy, optimization choices, and execution environment.

The schema separates:

- `input`: canonical structural object and workload.
- `expected_semantics`: canonical output and invariant expectations.
- `evidence_contract`: the canonical evidence envelope that future adapters must emit, plus the semantic projection fields that this fixture constrains.
- `reproducibility`: deterministic timestamp, canonical ordering, and hash fields.

## Structural Invariants

### Mathematical invariants

These properties must hold across every realization:

- Reachability is evaluated over directed structural relations in the canonical structural object.
- The observed pair universe is exactly `roots × targets`.
- Reachability classification is total and exclusive: a pair is either reachable or unreachable, never both and never omitted.
- Structural measurements are derived from canonical input and canonical output, not from implementation traces.
- Equivalent canonical inputs produce identical canonical outputs and identical invariant-verification results.

### Implementation details

The following are explicitly non-canonical:

- traversal algorithm choice;
- recursion versus iteration;
- data structure layout;
- parallel or sequential execution;
- memoization or caching;
- file format used internally by an implementation.

Implementation details may appear in diagnostics, but they cannot alter canonical semantics.

### Diagnostics

Diagnostics are evidence about realization quality, not additional scientific claims. A successful realization should emit at least:

- `REACHABILITY_PROFILE_EVALUATED` when the profile has been computed.
- `REACHABILITY_INVARIANTS_VERIFIED` when the mathematical invariants have been checked.
- `CANONICAL_ORDERING_CONFIRMED` when emitted pairs and measurement keys follow canonical ordering.

Failures should emit deterministic diagnostic codes identifying the failed precondition, postcondition, schema check, or replay check.

## Evidence Contract

The Reachability Profile fixture defines expected semantics; it is not itself a complete canonical evidence envelope. A repository adapter that realizes this research object must emit evidence conforming to `conformance/schemas/evidence.schema.json`. That adapter-produced envelope supplies execution provenance such as repository identity, repository URL, commit SHA, branch, implementation version, timestamps, semantic result, diagnostics, generated artifacts, and other required envelope fields.

The fixture constrains the semantic projection of that evidence through these fields:

- `canonical_outputs`: reachable pairs, unreachable pairs, root coverage, target coverage, and reachability density.
- `structural_metrics`: node count, edge count, root count, target count, pair counts, and density.
- `structural_invariants`: invariant-verification records proving total classification, exclusive classification, coverage consistency, and density consistency.
- `required_diagnostics`: deterministic diagnostic records that must be present in adapter-produced evidence.

This boundary preserves the distinction:

```text
Canonical fixture
  → defines expected semantics
Repository adapter
  → produces canonical evidence envelope
```

Evidence may include implementation-specific diagnostic extensions only inside fields intended for extension. Such extensions must not be required to interpret the canonical output.

## Reproducibility Requirements

A conforming realization must be reproducible under these rules:

1. Canonical input serialization is deterministic.
2. Node, edge, root, target, pair, and diagnostic ordering is deterministic.
3. Evidence comparison excludes observed wall-clock time and includes a deterministic canonical projection timestamp.
4. Fixture hash, canonical input hash, and canonical evidence hash are stable across replay.
5. A repeated realization of the same fixture either produces the same canonical evidence or reports deterministic drift.

## Deterministic Fixture

The fixture [`conformance/fixtures/canonical-reachability-profile.fixture.json`](../../conformance/fixtures/canonical-reachability-profile.fixture.json) defines a directed structure with roots `r1`, `r2` and targets `t1`, `t2`. The expected profile contains two reachable pairs and two unreachable pairs, yielding a reachability density of `0.5`.

The fixture is language-independent and intentionally contains no executable adapter binding. Future implementations can bind an adapter to this fixture while preserving the same canonical semantics and evidence contract.
