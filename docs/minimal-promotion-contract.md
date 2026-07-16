# Minimal Promotion Contract

## Status and intent

This document defines the consumer-side Minimal Promotion Contract for this repository. The repository receives immutable Minimal Promotion Packages and determines whether bounded formalization is authorized.

This is a documentation-level contract only. It defines deterministic consumer record identity and lifecycle linkage before machine-readable schemas are frozen for Admissibility Review and Promotion Decision records. It does not create schemas, validators, review-record instances, promotion decisions, registries, adapters, synchronization, automation, canonical research objects, canonical fixtures, conformance changes, SYNAPSE changes, or theorem/proof expansion.

The repository reviews submitted packages. It does not reinterpret empirical evidence, reconstruct the producer's claim, rewrite producer package meaning, or convert a package into canonical authority by receipt alone.

## Canonical architecture

The promotion architecture preserves this sequence:

```text
Minimal Promotion Package
        ↓
Admissibility Review
        ↓
Promotion Decision
        ↓
Bounded Formalization
        ↓
Canonical Research Object
        ↓
Canonical Fixture
        ↓
Implementation Conformance
```

The contract preserves these separations:

- **Producer Proposal ≠ Consumer Decision Package Receipt.** Receipt records that an immutable producer package is available for review; it is not a consumer decision.
- **Admissibility ≠ Promotion Authorization.** An admissibility result determines whether promotion review may proceed; it does not authorize bounded formalization.
- **Accepted Promotion ≠ Canonical Research Object.** Acceptance authorizes only the bounded formalization scope stated in the decision. It does not create a canonical research object.
- **Promotion Review ≠ Implementation Conformance.** Promotion review concerns admissibility and bounded authority. It is separate from validating any implementation, adapter, fixture, or executable artifact.
- **Upstream Provenance ≠ Runtime Dependency.** Producer provenance must be preserved locally, but repository-local validation must not require live producer access.

The producer owns the proposal. The consumer owns the review and decision.

## Promotion boundary

A Minimal Promotion Package is admissible input to review only as an immutable proposal for bounded formalization. The promotion boundary separates:

- producer-owned package contents, package identity, package version, evidence references, empirical outcome, limitations, lifecycle records, claims, rationale, and provenance; from
- consumer-owned admissibility findings, promotion decisions, accepted scope, excluded scope, authority effects, local provenance snapshots, and consumer lifecycle records.

Crossing the boundary does not change ownership of the proposal, reclassify empirical evidence as canonical authority, create a shared mutable record, or imply synchronization with the producer repository.

## Consumer record identifier model

Consumer review records use deterministic, repository-scoped identifiers. Identifiers are documentation-level record identities and must not be left as unconstrained strings.

The deterministic identifier pattern is:

```text
saf:<record_type>:<package_id>:<package_version>:<ordinal>
```

where:

- `saf` is the fixed namespace for this repository's consumer records.
- `<record_type>` is exactly `admissibility`, `decision`, `withdrawal`, or `invalidation`.
- `<package_id>` is the producer-owned package identifier copied from the immutable package reference and normalized only for identifier safety by lowercasing and replacing any character outside `[a-z0-9._-]` with `-`.
- `<package_version>` is the producer-owned package version copied from the immutable package reference and normalized by the same identifier-safety rule.
- `<ordinal>` is a zero-padded four-digit decimal sequence allocated append-only within this repository for records of the same `record_type`, `package_id`, and `package_version`, starting at `0001`.

Identifier fields have these semantics:

- `admissibility_id` identifies one Admissibility Review record and must use `record_type = admissibility`.
- `decision_id` identifies one Promotion Decision record and must use `record_type = decision`.
- `prior_record_reference` references the immediately prior consumer record, when a later record supersedes, withdraws, invalidates, or reconsiders it.
- `superseding_record_reference` references the later consumer record that superseded the current record, when known.
- `withdrawal_record_reference` references the consumer withdrawal record that withdrew current effect from the record, when applicable.
- `invalidation_record_reference` references the consumer invalidation record that invalidated the record, when applicable.

Repository-scoped uniqueness is mandatory. Once emitted, an identifier is immutable, must never be reused, and continues to identify the historical record even if the record is superseded, withdrawn, invalidated, or reconsidered. Identifiers encode the record type and producer package identity/version for local intelligibility. They do not encode mutable lifecycle state, admissibility result, decision result, authority effects, reviewer identity, timestamps, downstream canonical objects, or implementation conformance outcomes.

Versioning and supersession never mutate an existing identifier. A new producer package version, consumer supersession, consumer withdrawal, consumer invalidation, or reconsideration receives a new append-only record identifier and links back through the appropriate reference fields.

## Immutable producer-package reference model

Every Admissibility Review and Promotion Decision must contain the same immutable `package_reference` model identifying the exact producer package version reviewed:

| Field | Required | Semantics |
| --- | --- | --- |
| `package_id` | Yes | Producer-owned package identity. The consumer copies it and does not rewrite package meaning. |
| `package_version` | Yes | Producer-owned immutable package version. Package identity remains the pair (`package_id`, `package_version`). |
| `content_reference` | Yes | Immutable producer-supplied location, tag, release artifact, object path, or content address for the reviewed package version. |
| `content_digest` | Yes | Digest of the reviewed package content or package manifest snapshot as observed by the consumer. The digest strengthens identity but does not replace (`package_id`, `package_version`). |
| `hash_algorithm` | Yes | Hash algorithm for `content_digest`, such as `sha256`. |
| `canonicalization_method` | Yes | Producer-declared or consumer-recorded method used to compute the digest, such as canonical JSON, archive digest, or manifest digest. |
| `producer_repository` | Yes | Producer repository identity or URL. It is provenance, not a runtime dependency. |
| `producer_commit` | Yes | Producer commit or immutable source revision associated with the reviewed package version. |
| `producer_lifecycle_record_reference` | Optional | Producer-owned correction, withdrawal, supersession, invalidation, or other lifecycle record referenced by the consumer. |

The consumer preserves a local provenance snapshot containing the package reference, reviewed claim, purpose, empirical outcome, submitted evidence references, limitations, replication status, producer lifecycle references known at review time, and any locally observed digest metadata. This snapshot makes the consumer record locally intelligible without live upstream access.

A digest mismatch is not repaired by the consumer. If detected before review, the package is `inadmissible` or `deferred` because the exact package cannot be established. If detected after a record exists, the consumer appends an invalidation or supersession record and links it through `invalidation_record_reference` or `superseding_record_reference`. Producer correction, withdrawal, or supersession is referenced through `producer_lifecycle_record_reference`; the consumer does not rewrite the original package meaning.

Upstream provenance does not create a live runtime dependency. Repository-local validation must not fetch, clone, import, execute, synchronize with, or otherwise evaluate the producer repository to interpret an already emitted consumer record.

## Admissibility requirements

A Minimal Promotion Package is admissible for review only when it provides, at minimum:

1. A stable package identifier.
2. An immutable package version or content-addressed reference.
3. A producer identity or accountable producing authority.
4. A precise promotion claim.
5. A bounded requested formalization scope.
6. A list of submitted evidence artifacts or references.
7. Provenance for each submitted artifact sufficient to identify origin, version, and custody.
8. Explicit statement of assumptions and known limitations.
9. Explicit statement of what the producer is not claiming.
10. A declared package purpose.
11. A declared empirical outcome classification when the package relies on empirical investigation.
12. A declaration that the submitted package is complete for the requested review state.

Recognized package purposes include:

- `candidate_invariant_review`
- `bounded_formal_question`
- `counterexample_review`
- `vocabulary_alignment`
- `model_obligation`
- `indeterminate_evidence_review`

Admissibility must consider both the empirical outcome and the package purpose. Not every package requests candidate-invariant review, and the consumer must not silently treat bounded questions, counterexamples, vocabulary alignment, model obligations, or indeterminate evidence as supported invariant proposals.

Admissibility does not require the repository to accept the claim as true. It only determines whether review can proceed without reconstructing missing producer intent or mutating the proposal.

## Admissibility Review record model

An Admissibility Review record is the minimum consumer record that determines whether promotion review may proceed for one immutable package reference. It must include:

- `admissibility_id`
- `package_reference`
- `package_purpose`
- `reviewed_empirical_outcome`
- `reviewed_artifact_references`
- `provenance_snapshot`
- `limitations_snapshot`
- `replication_status`
- `admissibility_result`
- `record_lifecycle`
- `admissibility_rationale`
- `review_timestamp`
- `review_authority`
- `prior_record_reference`
- `superseding_record_reference`
- `reconsideration_conditions`

`admissibility_result` is exactly one of:

- `admissible`
- `admissible_with_limitations`
- `inadmissible`
- `deferred`

`record_lifecycle` is exactly one of:

- `active`
- `superseded`
- `withdrawn`
- `invalidated`

The admissibility result and the record lifecycle are independent axes. For example, an `inadmissible` record may be `active` until superseded, and an `admissible` record may later become `superseded` or `invalidated` without changing the historical result.

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

## Promotion Decision record model

A Promotion Decision record is the minimum consumer record that determines whether bounded formalization is authorized for one admissible package reference. It must link to exactly one Admissibility Review record through `admissibility_id`. A package with an `inadmissible` Admissibility Review must not receive a Promotion Decision.

A Promotion Decision record must include:

- `decision_id`
- `admissibility_id`
- `package_reference`
- `decision_result`
- `record_lifecycle`
- `decision_rationale`
- `decision_timestamp`
- `decision_authority`
- `translation_record`
- `authorized_effects`
- `excluded_effects`
- `preserved_limitations`
- `reconsideration_conditions`
- `prior_record_reference`
- `superseding_record_reference`
- `withdrawal_reason`
- `invalidity_reason`

`decision_result` is exactly one of:

- `accepted_for_formalization`
- `accepted_with_constraints`
- `rejected`
- `deferred`

`record_lifecycle` is exactly one of:

- `active`
- `superseded`
- `withdrawn`
- `invalidated`

The promotion decision result and decision-record lifecycle are independent axes. A rejected or deferred decision may be active as the current decision for a package version; an accepted decision may later be superseded, withdrawn, or invalidated without altering the historical result.

## Translation record

Every `accepted_for_formalization` or `accepted_with_constraints` decision must include a translation record. `accepted_with_constraints` additionally requires explicit constraints and exclusions. The translation record must include:

- `producer_claim`
- `accepted_formalization_scope`
- `excluded_formalization_scope`
- `translation_rationale`
- `assumptions`
- `constraints`
- `permitted_evidence_references`
- `preserved_limitations`
- `non_authorized_downstream_effects`

Producer Claim ≠ Accepted Formalization Scope. A narrower accepted scope must be explicit in `accepted_formalization_scope`, `excluded_formalization_scope`, and `translation_rationale`. The consumer must not silently strengthen, reinterpret, generalize, repair, or broaden the producer claim.

## Authority effects

`authorized_effects` and `excluded_effects` use finite documentation-level values.

The only minimum authorized effect defined by this contract is:

- `bounded_formalization`

The following effects are explicitly excluded unless a later, separate architecture layer independently authorizes them:

- `canonical_research_object_publication`
- `canonical_fixture_creation`
- `theorem_validation`
- `implementation_conformance_claim`
- `automation_creation`
- `producer_evidence_mutation`
- `cross_repository_synchronization`

Acceptance authorizes bounded work, not canonical completion. A promotion decision does not convert empirical evidence into canonical authority, make a Minimal Promotion Package a canonical research object, certify implementation conformance, validate executable behavior, require downstream automation, mutate producer evidence, synchronize repositories, or override canonical lifecycle requirements.

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

## Lifecycle linkage and reconsideration

Consumer records are append-only in meaning. Later records may supersede, withdraw, invalidate, or reconsider authority, but they do not erase earlier consumer records and do not rewrite the submitted producer package.

When a producer package is corrected, the consumer must treat the correction as a new producer-owned lifecycle fact. If the corrected package has a new `package_version`, any new review receives new consumer identifiers and links the earlier record through `prior_record_reference` and the later record through `superseding_record_reference`. The earlier record remains historically valid for what was reviewed, but it must not be used as active authority for the corrected package unless a new active consumer record explicitly permits that constrained use.

When a producer package is withdrawn, existing consumer records remain historically traceable but no longer provide current authority unless the consumer records a narrow reason that historical bounded formalization remains valid without reliance on the withdrawn package. The usual consumer action is to append a withdrawal record, set current effect to `withdrawn`, and link the affected record through `withdrawal_record_reference`.

When a producer package is superseded, an existing consumer review or decision may remain active only against the exact superseded package version and exact accepted scope recorded in its package reference. It does not automatically apply to the newer package. If current work should follow the newer package, a new Admissibility Review and any allowed Promotion Decision must be emitted and linked by prior/superseding references.

When a producer package is invalidated or found internally inconsistent, the consumer must reconsider any active review or decision depending on the invalidated basis. If the basis of the consumer record is incorrect, the consumer appends an invalidation record and links it through `invalidation_record_reference`. If a narrower historically accurate decision can remain active under constraints, that constrained effect must be documented in a new superseding record rather than by editing the old one.

Required linkage rules:

- A superseding record must point to the prior record with `prior_record_reference`.
- A superseded record must point forward with `superseding_record_reference` when the later record is known.
- A withdrawal action must create or reference a consumer withdrawal record and populate `withdrawal_record_reference` on affected records when known.
- An invalidation action must create or reference a consumer invalidation record and populate `invalidation_record_reference` on affected records when known.
- Reconsideration requires a recorded condition and a new append-only consumer record; it never mutates the original identifier.

Reconsideration conditions include:

- the producer submits a corrected or new immutable package version;
- the producer withdraws, supersedes, or invalidates the package;
- material provenance for the reviewed package is shown to be incorrect or incomplete;
- a content digest mismatch is detected;
- the prior decision exceeded its recorded authority or scope;
- the accepted scope conflicts with repository architectural invariants; or
- a later repository decision supersedes the prior decision.

## Status-axis separation

The following axes are distinct and must not be collapsed:

- Admissibility Result
- Admissibility Record Lifecycle
- Promotion Decision Result
- Promotion Decision Lifecycle
- Process Event
- Canonical Research-Object Lifecycle
- Implementation Conformance Outcome

`received`, `admissibility_reviewed`, `promotion_reviewed`, and `decision_recorded` are process events, not lifecycle states. This contract does not introduce a third competing status enum. Lifecycle values remain limited to `active`, `superseded`, `withdrawn`, and `invalidated` for consumer records.

## Outcome-sensitive compatibility matrix

Allowed relationships across empirical outcome, package purpose, admissibility result, and decision result are constrained as follows:

| Empirical outcome | Package purpose | Allowed admissibility result | Allowed decision result |
| --- | --- | --- | --- |
| `supports` | `candidate_invariant_review` within registered scope | `admissible`, `admissible_with_limitations`, or `deferred`; `inadmissible` if identity, provenance, or scope fails | May permit `accepted_for_formalization` or `accepted_with_constraints` for bounded candidate-invariant review; may also be `rejected` or `deferred` |
| `indeterminate` | `indeterminate_evidence_review` | `admissible`, `admissible_with_limitations`, or `deferred`; `inadmissible` if identity, provenance, or scope fails | May permit `accepted_with_constraints` for indeterminate-evidence review, bounded formal question, vocabulary alignment, or model obligation; must not become supported candidate-invariant authority |
| `indeterminate` | `bounded_formal_question`, `vocabulary_alignment`, or `model_obligation` | `admissible`, `admissible_with_limitations`, or `deferred`; `inadmissible` if identity, provenance, or scope fails | May permit bounded formalization only for the stated secondary purpose; must not become supported candidate-invariant authority |
| `violates` | `counterexample_review` | `admissible`, `admissible_with_limitations`, or `deferred`; `inadmissible` if identity, provenance, or scope fails | May permit counterexample review or bounded formal question; must not become supported candidate-invariant authority |
| `violates` | `candidate_invariant_review` | Usually `inadmissible`, `admissible_with_limitations`, or `deferred` depending on whether review is reframed explicitly by producer-owned purpose | Must not be accepted as supported candidate-invariant authority; any acceptance requires explicit counterexample or bounded-question scope |
| Any outcome | Any purpose | `inadmissible` | No Promotion Decision |

Additional matrix rules:

- `accepted_for_formalization` requires a translation record.
- `accepted_with_constraints` requires a translation record, constraints, preserved limitations, and exclusions.
- `inadmissible` always means no Promotion Decision for that Admissibility Review.

## B2 constraint

The canonical B2 empirical outcome is `indeterminate`. Any future B2 consumer record must preserve `package_purpose = indeterminate_evidence_review` or another explicitly allowed bounded secondary purpose such as `bounded_formal_question`, `vocabulary_alignment`, or `model_obligation`.

A B2 consumer record must not convert B2 into `candidate_invariant_review`, supported invariant evidence, or supported invariant authority.

## Downstream references

References to later Canonical Research Objects or Canonical Fixtures are optional, append-only, non-authoritative downstream links. They must not be required fields in the initial Promotion Decision record. They must not imply that acceptance created those objects, completed canonical review, or satisfied implementation conformance.

## Repository independence

The contract aligns consumer package-reference semantics with producer-owned Minimal Promotion Package identity and provenance. The producer retains ownership over package contents, package identity, package version, evidence references, empirical outcome, limitations, and producer lifecycle records. The consumer retains ownership over admissibility findings, promotion decisions, accepted scope, excluded scope, authority effects, and consumer lifecycle records.

No shared mutable record or cross-repository synchronization contract is created. Consumer records preserve enough local provenance to be historically traceable and locally intelligible without live upstream access.

## Documentation audit for schema readiness

1. An Admissibility Review is uniquely identified by `admissibility_id` using `saf:admissibility:<package_id>:<package_version>:<ordinal>`.
2. A Promotion Decision is uniquely identified by `decision_id` using `saf:decision:<package_id>:<package_version>:<ordinal>`.
3. The exact producer package object reviewed is identified by the required `package_reference` fields, with identity remaining (`package_id`, `package_version`) and strengthened by `content_digest`, `hash_algorithm`, and `canonicalization_method`.
4. Local provenance remains available through `package_reference`, `provenance_snapshot`, `limitations_snapshot`, reviewed artifact references, empirical outcome, replication status, producer lifecycle references known at review time, timestamps, and consumer authority fields.
5. After producer correction, the consumer emits a new append-only review for the corrected immutable package version when current authority is needed, links prior and superseding records, and preserves the earlier record historically.
6. After producer withdrawal, the consumer appends or references a withdrawal record, links affected records through `withdrawal_record_reference`, and removes current effect unless a new constrained consumer record explicitly preserves narrow historical authority.
7. After producer supersession, earlier consumer records remain historically valid only for the exact superseded package version and do not automatically govern the newer package.
8. An existing decision can remain active against a superseded package only for the exact package version and accepted scope recorded in that decision; it cannot transfer to the superseding package without a new record.
9. Acceptance creates only the finite authorized effect `bounded_formalization` within the accepted scope, assumptions, constraints, and preserved limitations.
10. Acceptance explicitly does not create canonical research-object publication, canonical fixture creation, theorem validation, implementation conformance claims, automation creation, producer evidence mutation, cross-repository synchronization, canonical completion, or runtime authority.
11. Result states, lifecycle states, and process events are fully separated: admissibility result, admissibility lifecycle, decision result, decision lifecycle, process events, canonical research-object lifecycle, and implementation conformance outcome are distinct axes.
12. Separate future schemas can encode the model without architectural redesign because identifiers, package references, record models, translation records, finite authority effects, lifecycle linkage, matrix rules, and downstream non-authority are specified as documentation-level contracts.
