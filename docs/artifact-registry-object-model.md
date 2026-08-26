# Canonical Artifact Registry Object Model

## Status and boundary

This document is the normative Artifact contract for SYNAPSE. The JSON Schema at
`schemas/artifact.schema.json` is its machine-readable representation. This change defines records and
validation only: it does not define a database, graph store, registry service, API, synchronization,
user interface, deployment, or an authority-granting workflow.

An **Artifact** is an immutable, content-addressed record of a bounded product. Existing research-object
IDs remain the identity of research meaning; an Artifact wraps an exact version/representation without
replacing that identity or its lifecycle and authority rules.

## Canonical object

Every Artifact contains:

| Field | Contract |
| --- | --- |
| `schema_version` | Contract version, currently `1.0.0`. |
| `artifact_id` | Stable logical identity: `artifact:<type>:<lowercase-slug>`. |
| `artifact_type` | `repository_snapshot`, `observation`, `evidence_record`, `model_object`, `analysis_result`, `decision_reference`, `validation_record`, `authorization_record`, or `execution_record`. |
| `version` | Positive, monotonically allocated integer for this `artifact_id`. |
| `producer` | Stable producer identity, kind (`human`, `software`, or `organization`), and producer version when software is used. |
| `inputs`, `outputs` | Exact immutable Artifact references; outputs describe separately registered products and never embed mutable objects. |
| `provenance` | Origin locator/revision, production method, reproducibility parameters, environment, and production time. |
| `content_hash` | SHA-256 over the canonical payload bytes, expressed as `sha256:<64 lowercase hex>`. The envelope hash is not self-referential. |
| `lifecycle_state` | Editorial/availability state. |
| `validity` | Independent confidence/validity assertion, its basis, assessor, and time. |
| `supersession` | Immediate prior/later version references, without deletion or mutation. |
| `relationships` | Typed, directed statements from this artifact to exact target versions. |
| `payload` | Artifact-specific content. For this v1 contract its canonical serialization is UTF-8 JSON with object keys sorted lexicographically, no insignificant whitespace, and JSON separators `,` and `:`. |

An Artifact reference is the triple `artifact_id`, `version`, and `content_hash`. Consumers MUST reject an
unversioned reference or a digest mismatch. References are exact; they do not mean “latest.”

## Identity, versions, and immutability

1. `(artifact_id, version)` identifies exactly one payload and one `content_hash`; the triple is globally
   unambiguous within a SYNAPSE exchange boundary.
2. `artifact_id` is stable for the same logical artifact. A semantic identity change requires a new ID.
3. Version 1 starts an identity. Any payload, provenance, producer, input/output, relationship, lifecycle,
   validity, or lineage change creates the next integer version. Published historical envelopes are never
   edited or reused.
4. A new version explicitly links its immediate predecessor with `supersedes`; the predecessor may later
   be represented by a new envelope version that records `superseded_by`. History remains addressable.
5. Titles, locations, lifecycle labels, validity findings, and relationship assertions are not encoded in
   identity. They therefore cannot silently retarget an ID.
6. Hashing covers only the canonical `payload` serialization defined above. Envelope integrity/signatures may be layered later but are not
   invented by this contract. Reproduction compares both payload hash and all declared production inputs.

## Provenance and lineage

`provenance.origin` identifies where the producer obtained or created the payload; repository origins name
an immutable commit/revision, while non-repository origins name an immutable release or source revision.
`method` identifies the bounded procedure. `parameters` and `environment` contain replay-relevant values.
`produced_at` records history and MUST NOT be replaced with validation or ingestion time.

`inputs` answers which exact artifacts participated in production. `derived_from` records intellectual or
data derivation even when a target was not a direct execution input. `produced_by` connects a product to an
execution record; `producer` identifies the responsible agent. These fields are complementary, not aliases.
A reproducible chain has immutable references, resolvable origin revisions, a method, replay parameters,
environment, producer version when applicable, and matching hashes. This contract records those facts; it
does not promise that external sources remain available.

## Relationship semantics

Relationships are directed from the containing Artifact (`source`) to `target`. Every relationship has an
independent assertion ID and optional rationale. No edge transfers validity, authority, authorization,
canonical status, or confidence.

| Relationship | Exact meaning |
| --- | --- |
| `produced_by` | Source bytes were emitted by the target `execution_record`; it does not validate the output. |
| `derived_from` | Source content materially transforms or selects target content; it does not endorse the target. |
| `supports` | Source provides evidence tending to increase confidence in a target claim/result, within the stated rationale; it grants no authority. |
| `contradicts` | Source provides evidence incompatible with a target claim/result under the stated scope; it neither invalidates nor supersedes automatically. |
| `supersedes` | Source is the declared replacement for the immediately prior version of the same logical identity; history remains validly addressable. |
| `implements` | Source realizes the contract/meaning described by target; it is a conformance claim, not proof of conformance. |
| `validated_by` | Target `validation_record` assessed source against a named contract; it does not authorize use. |
| `authorized_by` | Target `authorization_record` permits a bounded use of source; it does not establish validity or execution. |
| `executed_as` | Source plan/model/decision was instantiated by target `execution_record`; occurrence is not proof of correctness. |

Target types are constrained by schema for `produced_by`, `validated_by`, `authorized_by`, and `executed_as`.
`supersedes` additionally requires the same `artifact_id`, an older version, and agreement with
`supersession.previous`. All duplicate relationship assertion IDs are invalid.

The following separations are invariants:

- Artifact existence ≠ validity.
- Evidence ≠ authority.
- Validation ≠ authorization.
- Authorization ≠ execution.
- Execution ≠ proof.
- Relationship ≠ inherited legitimacy.

## Lifecycle and validity

Lifecycle is one of `draft`, `active`, `superseded`, `deprecated`, or `withdrawn`. Normal movement is
`draft → active → superseded|deprecated|withdrawn`; terminal historical states remain addressable. A
`superseded` artifact requires `supersession.superseded_by`. A successor does not erase or invalidate its
predecessor. `deprecated` discourages new use; `withdrawn` records producer withdrawal; neither is deletion.

Validity is separately `unassessed`, `valid`, `invalid`, or `indeterminate`, with numeric confidence from
0 to 1. `valid`, `invalid`, and `indeterminate` require a nonempty basis and assessor; `unassessed` has no
assessor and confidence 0. Lifecycle transitions never alter validity, and validity never grants authority.

## Valid and invalid examples

`fixtures/artifact-registry/valid-end-to-end.json` is the canonical compressed chain:

```text
Repository Snapshot → Observation → Evidence Record → Model Object → Analysis Result → Decision Reference
```

It demonstrates exact inputs, derivation and support edges, execution provenance, validation distinct from
authorization, and a final decision reference. `fixtures/artifact-registry/invalid-artifacts.json` contains
named rejected cases: mutable/latest references, malformed hashes, validity without assessment, wrong target
types, cross-identity supersession, lineage disagreement, and duplicate assertion IDs. Invalid fixtures carry
expected deterministic JSON paths and constraints; they are test vectors, never candidate registry entries.

The chain answers what was produced (`artifact_id`, type, version, hash), origin (`provenance`), production
inputs (`inputs`), relations (`relationships`), replacement (`supersession`/`supersedes`), consumption
(a later artifact's `inputs`/`derived_from`), and reproducibility (exact references, method, parameters,
environment, producer version, origin revision, and hashes).

## Validation

Run `python tools/validate_artifact_contract.py`. Schema validation is deterministic. Additional semantic
checks enforce reference hashes, identity/type consistency, unique relationship assertions, supersession
agreement, and expected rejection of every invalid fixture. Passing validation proves conformance of these
records to this contract only; it does not prove payload truth, confer authority, authorize action, or record
execution.
