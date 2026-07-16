# Minimal Promotion Contract

## Status and intent

This document defines the consumer-side Minimal Promotion Contract for this repository. The repository receives immutable Promotion Packages and determines whether bounded formalization is authorized.

The repository reviews submitted packages. It does not reinterpret empirical evidence, reconstruct the producer's claim, or convert a package into canonical authority by receipt alone.

## Architectural invariants

The contract preserves the following invariants:

- **Empirical Evidence ≠ Canonical Authority.** Evidence may support a proposal, but evidence does not itself authorize canonicalization or formalization.
- **Promotion Package ≠ Promotion Decision.** A submitted package is a producer-owned proposal. The repository's decision is a separate consumer-owned record.
- **Accepted Promotion ≠ Canonical Research Object.** Acceptance authorizes only the bounded formalization scope stated in the decision. It does not create a canonical research object.
- **Promotion Review ≠ Implementation Conformance.** Promotion review concerns admissibility and bounded authority. It is separate from validating any implementation, adapter, fixture, or executable artifact.

The producer owns the proposal. The consumer owns the decision.

## Promotion boundary

A Promotion Package is admissible input to review only as an immutable proposal for bounded formalization. The promotion boundary separates:

- producer-owned empirical material, claims, identifiers, rationale, and package provenance; from
- consumer-owned admissibility findings, promotion decisions, accepted scope, exclusions, and review records.

Crossing the boundary does not change ownership of the proposal, reclassify empirical evidence as canonical authority, or imply implementation conformance.

## Admissibility requirements

A Promotion Package is admissible for review only when it provides, at minimum:

1. A stable package identifier.
2. An immutable package version or content-addressed reference.
3. A producer identity or accountable producing authority.
4. A precise promotion claim.
5. A bounded requested formalization scope.
6. A list of submitted evidence artifacts or references.
7. Provenance for each submitted artifact sufficient to identify origin, version, and custody.
8. Explicit statement of assumptions and known limitations.
9. Explicit statement of what the producer is not claiming.
10. A declaration that the submitted package is complete for the requested review state.

Admissibility does not require the repository to accept the claim as true. It only determines whether review can proceed without reconstructing missing producer intent or mutating the proposal.

## Admissibility review process

Admissibility review is a bounded consumer-side process:

1. Confirm that the package reference is immutable.
2. Confirm that required package fields are present and internally identifiable.
3. Confirm that the requested formalization scope is bounded.
4. Confirm that provenance is recorded for submitted evidence artifacts.
5. Confirm that exclusions and limitations are stated by the producer.
6. Determine whether review can proceed without reinterpretation, supplementation, or repair of empirical evidence.
7. Record an admissibility result before any promotion decision is made.

The reviewer may reject or defer a package for missing, mutable, ambiguous, or unbounded material. The reviewer must not repair the package by inventing claims, normalizing evidence into new authority, or broadening the requested scope.

## Admissibility result states

Admissibility review produces exactly one of these result states:

- **Admissible.** The package is sufficiently bounded, immutable, and provenance-bearing for promotion review.
- **Deferred.** Review cannot proceed until the producer supplies a new immutable package version or clarifies bounded producer-owned material.
- **Rejected as inadmissible.** The package is outside the promotion boundary, mutable, unbounded, missing required provenance, or dependent on consumer reinterpretation of empirical evidence.

An admissibility result is not a promotion decision.

## Promotion decision states

After an admissible package is reviewed, the repository records exactly one promotion decision state:

- **Accepted.** Bounded formalization is authorized only for the accepted scope recorded in the decision.
- **Accepted with constraints.** Bounded formalization is authorized subject to explicit consumer-side constraints, exclusions, or preconditions recorded in the decision.
- **Rejected.** Bounded formalization is not authorized for the submitted package version.
- **Superseded.** A prior decision is retained for provenance but no longer governs current review because a later immutable package version or later decision has replaced it.
- **Withdrawn from consideration.** The package is no longer under active review because the producer withdrew it or the consumer closed review without a substantive promotion decision.

A promotion decision does not itself create schemas, validators, registries, adapters, automation, canonical research objects, fixtures, theorems, or SYNAPSE changes.

## Decision authority

The repository, acting as consumer, has authority to:

- decide whether a package is admissible;
- decide whether bounded formalization is authorized;
- define accepted and excluded formalization scope;
- record constraints on any accepted promotion;
- preserve review provenance and lifecycle state; and
- reject, defer, supersede, or close review.

The producer retains authority over the contents, intended claim, and submitted evidence of the Promotion Package. The consumer must not mutate those producer-owned contents when making a decision.

## Authority effects

A promotion decision has only the effects explicitly recorded in the consumer-side decision:

- It may authorize bounded formalization work in this repository.
- It may constrain the permissible interpretation of the accepted scope.
- It may exclude specific claims, evidence uses, implementation implications, or canonical lifecycle effects.
- It may provide a provenance anchor for later documentation or review.

A promotion decision does not:

- convert empirical evidence into canonical authority;
- make a Promotion Package a canonical research object;
- certify implementation conformance;
- validate executable behavior;
- require downstream automation; or
- override canonical lifecycle requirements.

## Accepted formalization scope

Accepted formalization scope must be recorded as a bounded statement of what may be formalized. It may include:

- the specific claim or concept authorized for formal treatment;
- the package version from which the authorization derives;
- the assumptions under which formalization may proceed;
- the evidence references that may be cited as producer-supplied context;
- the constraints that preserve the distinction between evidence, proposal, decision, and canonical authority; and
- the review record that authorized the work.

Accepted scope is interpreted narrowly. Anything not explicitly accepted remains outside the authorization.

## Excluded formalization scope

Unless explicitly authorized by a later decision, accepted promotion excludes:

- creation of canonical research objects;
- creation of schemas, validators, registries, adapters, fixtures, automation, theorems, or SYNAPSE changes;
- implementation conformance claims;
- new empirical claims not present in the submitted package;
- reinterpretation, repair, or extension of producer evidence;
- expansion from a bounded concept into repository-wide architecture; and
- any claim that acceptance confers canonical lifecycle status.

## Immutable provenance requirements

Every review record must preserve immutable provenance sufficient to identify:

- the exact Promotion Package version reviewed;
- the producer or producing authority;
- the package identifier and content reference;
- the submitted evidence references as supplied by the producer;
- the admissibility result;
- the promotion decision state, if any;
- the accepted and excluded scope, if any;
- the decision date or review record timestamp; and
- the consumer-side reviewer or decision authority when recorded by repository process.

If the reviewed package cannot be identified immutably, it is not admissible.

## Reconsideration conditions

A prior decision may be reconsidered only when one of the following conditions is recorded:

- the producer submits a new immutable package version;
- material provenance for the reviewed package is shown to be incorrect or incomplete;
- the prior decision exceeded its recorded authority or scope;
- the accepted scope is found to conflict with repository architectural invariants;
- a later repository decision supersedes the prior decision; or
- the producer withdraws the package from further consideration.

Reconsideration does not mutate the original package or erase the prior review record. It creates a new consumer-side review record linked to the prior state.

## Record lifecycle

Promotion records follow this lifecycle:

1. **Received.** An immutable package reference is recorded for possible review.
2. **Admissibility reviewed.** The repository records `Admissible`, `Deferred`, or `Rejected as inadmissible`.
3. **Promotion reviewed.** If admissible, the repository records a promotion decision state.
4. **Active or closed.** Accepted decisions remain active only for their recorded scope. Rejected, withdrawn, deferred, and inadmissible records remain closed or pending according to their state.
5. **Superseded when applicable.** Later package versions or decisions may supersede earlier records without deleting them.

Records are append-only in meaning: later records may supersede or correct authority, but they do not rewrite the submitted package or silently alter the historical decision.

## Separation from canonical lifecycle

Promotion review is upstream of, and separate from, any canonical lifecycle. An accepted promotion may authorize bounded formalization work, but it does not establish a canonical research object or satisfy canonical object requirements.

Any later canonical lifecycle must independently define its object identity, scientific meaning, invariants, evidence contract, reproducibility requirements, schemas, fixtures, and validation process according to the repository's canonical research-object standards.

## Separation from implementation conformance

Promotion review is not implementation conformance. It does not validate code, adapters, fixtures, schema validation, algorithms, execution traces, or runtime behavior.

Implementation conformance, if later pursued, must be evaluated by the repository's conformance process against the relevant canonical object or formal specification. An accepted promotion can be cited as authorization for bounded formalization, but it cannot be cited as proof that an implementation conforms.
