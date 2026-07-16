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

- **Producer Proposal ≠ Consumer Decision.** A producer package is a producer-owned proposal; it is not a consumer-owned review or decision.
- **Package Receipt ≠ Admissibility.** Receipt records that an immutable producer package is available for possible review; it is not an admissibility result.
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
saf:<record_type>:<package_identity_token>:<ordinal>
```

where:

- `saf` is the fixed namespace for this repository's consumer records.
- `<record_type>` is exactly `admissibility` or `decision`.
- `<package_identity_token>` is `base32url_no_padding(UTF-8(byte_length(package_id) + ":" + package_id + byte_length(package_version) + ":" + package_version))`, where `package_id` and `package_version` are the exact producer-owned strings stored in `package_reference`, each `byte_length` is the decimal UTF-8 byte length of the following value, the encoded byte sequence uses the RFC 4648 base32 alphabet `a-z2-7`, padding `=` is omitted, and letters are emitted lowercase for identifier readability.
- `<ordinal>` is a zero-padded four-digit decimal sequence allocated append-only within this repository for records of the same `record_type` and `package_identity_token`, starting at `0001`.

This encoding preserves case and character distinctions by encoding the exact UTF-8 bytes of the length-prefixed ordered pair. It is injective because the byte lengths delimit each value unambiguously, the base32 representation is reversible after restoring omitted padding, and no lossy normalization or character replacement is applied. The token remains repository-local and deterministic, does not depend on hashes alone, and does not replace the original `package_id` or `package_version` stored in `package_reference`.

Examples:

| `package_id` | `package_version` | `package_identity_token` | Example identifier |
| --- | --- | --- | --- |
| `B2.Package` | `v1.0` | `geyduqrsfzigcy3lmftwknb2oyys4ma` | `saf:admissibility:geyduqrsfzigcy3lmftwknb2oyys4ma:0001` |
| `pkg:Alpha/β` | `Release 2026-07-16` | `gezdu4dlm45ec3dqnbqs7tvsge4duutfnrswc43feazdamrwfuydoljrgy` | `saf:decision:gezdu4dlm45ec3dqnbqs7tvsge4duutfnrswc43feazdamrwfuydoljrgy:0001` |

Identifier fields have these semantics:

- `admissibility_id` identifies one Admissibility Review record and must use `record_type = admissibility`.
- `decision_id` identifies one Promotion Decision record and must use `record_type = decision`.
- `prior_record_reference` references the immediately prior consumer record, when a later record supersedes, withdraws, invalidates, or reconsiders it.
- `superseding_record_reference` references the later consumer record that superseded the current record, when known.
- `withdrawal_record_reference` references the append-only Admissibility Review or Promotion Decision record version that changed the affected record lifecycle to `withdrawn`, when applicable.
- `invalidation_record_reference` references the append-only Admissibility Review or Promotion Decision record version that changed the affected record lifecycle to `invalidated`, when applicable.

Repository-scoped uniqueness is mandatory. Once emitted, an identifier is immutable, must never be reused, and continues to identify the historical record even if the record is superseded, withdrawn, invalidated, or reconsidered. Identifiers encode the record type and exact producer package identity/version token for local intelligibility. They do not encode mutable lifecycle state, admissibility result, decision result, authority effects, reviewer identity, timestamps, downstream canonical objects, or implementation conformance outcomes.

Versioning and supersession never mutate an existing identifier. A new producer package version, consumer supersession, consumer withdrawal, consumer invalidation, or reconsideration receives a new append-only `admissibility` or `decision` record identifier and links back through the appropriate reference fields.

## Immutable producer-package reference model

Every Admissibility Review and Promotion Decision must contain the same immutable `package_reference` model identifying the exact producer package version reviewed. The model supports repository and non-repository packages without weakening immutability.

Common fields required for every package reference are:

| Field | Required | Semantics |
| --- | --- | --- |
| `package_id` | Yes | Producer-owned package identity. The consumer copies it and does not rewrite package meaning. |
| `package_version` | Yes | Producer-owned immutable package version. Package identity remains the pair (`package_id`, `package_version`). |
| `provenance_source_type` | Yes | Exactly one of `repository`, `release_artifact`, `archive`, `object_store`, or `content_address`. |
| `content_reference` | Yes | Immutable producer-supplied location, release artifact, archive object, object-store key/version, or content address for the reviewed package version. Mutable URLs, floating branch names, and moving tags are insufficient. |
| `content_digest` | Yes | Digest of the reviewed package content or package manifest snapshot as observed by the consumer. The digest strengthens identity and provenance but does not replace (`package_id`, `package_version`). |
| `hash_algorithm` | Yes | Hash algorithm for `content_digest`, such as `sha256`. |
| `canonicalization_method` | Yes | Producer-declared or consumer-recorded method used to compute the digest, such as canonical JSON, archive digest, or manifest digest. |
| `producer_lifecycle_record_reference` | Optional | Producer-owned correction, withdrawal, supersession, invalidation, or other lifecycle record referenced by the consumer. Required when such a producer lifecycle record is part of the reviewed package context. |

The provenance union is deterministic and mutually exclusive:

| `provenance_source_type` | Additional required fields | Prohibited branch fields |
| --- | --- | --- |
| `repository` | `producer_repository`, `producer_commit` | `producer_artifact_locator`, `producer_artifact_revision`, `content_address` as the primary provenance branch |
| `release_artifact` | `producer_artifact_locator`, `producer_artifact_revision` | `producer_repository`, `producer_commit`, `content_address` as the primary provenance branch |
| `archive` | `producer_artifact_locator`, `producer_artifact_revision` | `producer_repository`, `producer_commit`, `content_address` as the primary provenance branch |
| `object_store` | `producer_artifact_locator`, `producer_artifact_revision` | `producer_repository`, `producer_commit`, `content_address` as the primary provenance branch |
| `content_address` | `content_address` | `producer_repository`, `producer_commit`, `producer_artifact_locator`, `producer_artifact_revision` as the primary provenance branch |

Every package must have exactly one immutable provenance source. Repository provenance requires a repository identity and immutable commit. Non-repository provenance requires an immutable artifact locator and revision object, or a content address when `provenance_source_type = content_address`. The content digest remains mandatory in all branches and strengthens provenance; it does not replace package identity or the selected provenance source.

A Promotion Decision repeats `package_reference`, and `PromotionDecision.package_reference` must equal the linked `AdmissibilityReview.package_reference` across the full immutable reference: `package_id`, `package_version`, `provenance_source_type`, `content_reference`, `content_digest`, `hash_algorithm`, `canonicalization_method`, repository fields when `repository` is selected, non-repository artifact locator/revision or content address when a non-repository branch is selected, and `producer_lifecycle_record_reference` when applicable. A Promotion Decision must not authorize bounded formalization for any package other than the exact package admitted. If the producer package changes, a new Admissibility Review is required.

The consumer preserves a local provenance snapshot containing the package reference, reviewed claim, purpose, empirical outcome, submitted evidence references, limitations, replication status, producer lifecycle references known at review time, and any locally observed digest metadata. This snapshot makes the consumer record locally intelligible without live upstream access.

A digest mismatch is not repaired by the consumer. If detected before review, the package is `inadmissible` or `deferred` because the exact package cannot be established. If detected after a record exists, the consumer appends a new `admissibility` or `decision` record version with lifecycle `invalidated` or `superseded` and links it through `invalidation_record_reference` or `superseding_record_reference`. Producer correction, withdrawal, or supersession is referenced through `producer_lifecycle_record_reference`; the consumer does not rewrite the original package meaning.

Upstream provenance does not create a live runtime dependency. Repository-local validation must not fetch, clone, import, execute, synchronize with, or otherwise evaluate the producer repository, artifact locator, object store, archive location, or content-address provider to interpret an already emitted consumer record.

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
- `withdrawal_record_reference`
- `invalidation_record_reference`
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

The admissibility result and the record lifecycle are independent axes. For example, an `inadmissible` record may be `active` until superseded, and an `admissible` record may later become `superseded` or `invalidated` without changing the historical result. `withdrawal_record_reference` and `invalidation_record_reference` are absent when no withdrawal or invalidation applies, required when `record_lifecycle` is `withdrawn` or `invalidated`, must reference a later append-only Admissibility Review record, and must not reference a separate third schema type.

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

A Promotion Decision record is the minimum consumer record that determines whether bounded formalization is authorized for one admitted package reference. It must link to exactly one Admissibility Review record through `admissibility_id`. A Promotion Decision may exist only when the linked Admissibility Review result is `admissible` or `admissible_with_limitations`. A linked result of `inadmissible` or `deferred` prohibits a Promotion Decision; deferred admissibility requires producer clarification, correction, or a new immutable package before promotion review may proceed.

A Promotion Decision record must include:

- `decision_id`
- `admissibility_id`
- `package_reference`
- `decision_result`
- `record_lifecycle`
- `decision_rationale`
- `decision_timestamp`
- `decision_authority`
- `translation_record` (required only for `accepted_for_formalization` and `accepted_with_constraints`; absent otherwise)
- `translation_record_status`
- `authorized_effects`
- `excluded_effects`
- `preserved_limitations`
- `reconsideration_conditions`
- `prior_record_reference`
- `superseding_record_reference`
- `withdrawal_record_reference`
- `invalidation_record_reference`
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

The promotion decision result and decision-record lifecycle are independent axes. A rejected or deferred decision may be active as the current decision for a package version; an accepted decision may later be superseded, withdrawn, or invalidated without altering the historical result. `withdrawal_record_reference` and `invalidation_record_reference` are absent when no withdrawal or invalidation applies, required when `record_lifecycle` is `withdrawn` or `invalidated`, must reference a later append-only Promotion Decision record, and must not reference a separate third schema type. `package_reference` must exactly equal the linked Admissibility Review package reference.

## Translation record

`translation_record` is conditional on `decision_result` and must not force placeholder accepted-scope data into rejected or deferred decisions. The deterministic convention is:

| `decision_result` | `translation_record` convention | Additional requirements |
| --- | --- | --- |
| `accepted_for_formalization` | Required | Must define accepted and excluded scope. |
| `accepted_with_constraints` | Required | Must define accepted scope, constraints, preserved limitations, and exclusions. |
| `rejected` | Prohibited; use `translation_record_status = not_applicable` | `decision_rationale` records why no accepted scope exists. |
| `deferred` | Prohibited; use `translation_record_status = not_applicable` | `decision_rationale` records what producer clarification, correction, or new immutable package is needed. |

Every required translation record must include:

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

When a producer package is withdrawn, existing consumer records remain historically traceable but no longer provide current authority unless the consumer records a narrow reason that historical bounded formalization remains valid without reliance on the withdrawn package. The usual consumer action is to append a new version of the affected Admissibility Review or Promotion Decision record with lifecycle `withdrawn` and link the affected record through `withdrawal_record_reference`.

When a producer package is superseded, an existing consumer review or decision may remain active only against the exact superseded package version and exact accepted scope recorded in its package reference. It does not automatically apply to the newer package. If current work should follow the newer package, a new Admissibility Review and any allowed Promotion Decision must be emitted and linked by prior/superseding references.

When a producer package is invalidated or found internally inconsistent, the consumer must reconsider any active review or decision depending on the invalidated basis. If the basis of the consumer record is incorrect, the consumer appends a new version of the affected Admissibility Review or Promotion Decision record with lifecycle `invalidated` and links it through `invalidation_record_reference`. If a narrower historically accurate decision can remain active under constraints, that constrained effect must be documented in a new superseding record rather than by editing the old one.

Required linkage rules:

- A superseding record must point to the prior record with `prior_record_reference`.
- A superseded record must point forward with `superseding_record_reference` when the later record is known.
- A withdrawal action must create or reference a new append-only version of the affected Admissibility Review or Promotion Decision record with lifecycle `withdrawn` and populate `withdrawal_record_reference` on affected records when known.
- An invalidation action must create or reference a new append-only version of the affected Admissibility Review or Promotion Decision record with lifecycle `invalidated` and populate `invalidation_record_reference` on affected records when known.
- Withdrawal and invalidation are not independent third or fourth document types and do not require separate future schemas under this contract.
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

Allowed relationships across empirical outcome, package purpose, admissibility result, and decision result are constrained as follows. In every row, `inadmissible` or `deferred` admissibility means no Promotion Decision; only `admissible` or `admissible_with_limitations` may proceed to promotion review.

| Empirical outcome | Package purpose | Allowed admissibility result | Allowed decision result when admissible |
| --- | --- | --- | --- |
| `supports` | `candidate_invariant_review` within registered scope | `admissible`, `admissible_with_limitations`, or `deferred`; `inadmissible` if identity, provenance, or scope fails | May permit `accepted_for_formalization` or `accepted_with_constraints` for bounded candidate-invariant review; may also be `rejected` or `deferred` |
| `supports` | `bounded_formal_question` | `admissible`, `admissible_with_limitations`, or `deferred`; `inadmissible` if identity, provenance, or scope fails | May permit bounded formalization for the bounded question only; no candidate-invariant authority is implied |
| `supports` | `vocabulary_alignment` | `admissible`, `admissible_with_limitations`, or `deferred`; `inadmissible` if identity, provenance, or scope fails | May permit vocabulary-alignment formalization only; no candidate-invariant authority is implied |
| `supports` | `model_obligation` | `admissible`, `admissible_with_limitations`, or `deferred`; `inadmissible` if identity, provenance, or scope fails | May permit model-obligation formalization only; no theorem-validation or implementation-conformance authority is implied |
| `indeterminate` | `indeterminate_evidence_review` | `admissible`, `admissible_with_limitations`, or `deferred`; `inadmissible` if identity, provenance, or scope fails | May permit `accepted_with_constraints` for indeterminate-evidence review, bounded formal question, vocabulary alignment, or model obligation; must not become supported candidate-invariant authority |
| `indeterminate` | `bounded_formal_question`, `vocabulary_alignment`, or `model_obligation` | `admissible`, `admissible_with_limitations`, or `deferred`; `inadmissible` if identity, provenance, or scope fails | May permit bounded formalization only for the stated secondary purpose; must not become supported candidate-invariant authority |
| `violates` | `counterexample_review` | `admissible`, `admissible_with_limitations`, or `deferred`; `inadmissible` if identity, provenance, or scope fails | May permit counterexample review or bounded formal question; must not become supported candidate-invariant authority |
| `violates` | `candidate_invariant_review` | Usually `inadmissible`, `admissible_with_limitations`, or `deferred` depending on whether review is reframed explicitly by producer-owned purpose | Must not be accepted as supported candidate-invariant authority; any acceptance requires explicit counterexample or bounded-question scope |
| Any outcome | Any purpose | `inadmissible` or `deferred` | No Promotion Decision |

Additional matrix rules:

- `accepted_for_formalization` requires a translation record.
- `accepted_with_constraints` requires a translation record, constraints, preserved limitations, and exclusions.
- `rejected` and decision-level `deferred` prohibit `translation_record` and require `translation_record_status = not_applicable` with rationale in `decision_rationale`.
- `inadmissible` or `deferred` Admissibility Review results always mean no Promotion Decision for that Admissibility Review.

## B2 constraint

The canonical B2 empirical outcome is `indeterminate`. Any future B2 consumer record must preserve `package_purpose = indeterminate_evidence_review` or another explicitly allowed bounded secondary purpose such as `bounded_formal_question`, `vocabulary_alignment`, or `model_obligation`.

A B2 consumer record must not convert B2 into `candidate_invariant_review`, supported invariant evidence, or supported invariant authority.

## Downstream references

References to later Canonical Research Objects or Canonical Fixtures are optional, append-only, non-authoritative downstream links. They must not be required fields in the initial Promotion Decision record. They must not imply that acceptance created those objects, completed canonical review, or satisfied implementation conformance.

## Repository independence

The contract aligns consumer package-reference semantics with producer-owned Minimal Promotion Package identity and provenance. The producer retains ownership over package contents, package identity, package version, evidence references, empirical outcome, limitations, and producer lifecycle records. The consumer retains ownership over admissibility findings, promotion decisions, accepted scope, excluded scope, authority effects, and consumer lifecycle records.

No shared mutable record or cross-repository synchronization contract is created. Consumer records preserve enough local provenance to be historically traceable and locally intelligible without live upstream access.

## Documentation audit for schema readiness

1. Record identifier encoding is collision-safe because `package_identity_token` is a reversible base32 encoding of the exact UTF-8 length-prefixed ordered pair (`package_id`, `package_version`), with no lossy normalization.
2. `admissibility_id` and `decision_id` remain immutable and repository-scoped.
3. Withdrawal and invalidation links appear in both minimum record models.
4. Withdrawal and invalidation remain append-only versions of the same primary record types and not separate schema families.
5. `translation_record` is required only for `accepted_for_formalization` and `accepted_with_constraints`; it is prohibited for `rejected` and `deferred` decisions under `translation_record_status = not_applicable`.
6. Deferred admissibility blocks Promotion Decisions until producer clarification, correction, or a new immutable package permits a new admissibility result.
7. `PromotionDecision.package_reference` must exactly match the linked `AdmissibilityReview.package_reference`; changed packages require a new Admissibility Review.
8. Repository and non-repository immutable provenance are both representable through the mutually exclusive `provenance_source_type` union.
9. Mutable provenance remains prohibited; mutable URLs, floating branch names, and moving tags are insufficient.
10. Supported secondary-purpose packages are covered by the compatibility matrix for `bounded_formal_question`, `vocabulary_alignment`, and `model_obligation`.
11. B2 remains `indeterminate`.
12. B2 cannot become supported candidate-invariant authority.
13. Result state, lifecycle state, process event, and authority effect remain separate axes.
14. Future Issues #39 and #40 can encode the contract without redesign because identifiers, provenance union, package-reference equality, decision eligibility, translation conditionality, lifecycle linkage, and matrix rules are specified at documentation level.
