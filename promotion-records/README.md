# Consumer Promotion Records

This directory contains repository-owned Admissibility Review and Promotion Decision records governed by the [Minimal Promotion Contract](../docs/minimal-promotion-contract.md). The executable schemas and semantic validator remain the existing repository authorities; these instances do not define another contract, schema, or validator.

## B2 v1.0 boundary

The consumer boundary for the canonical B2 Minimal Promotion Package is represented by:

1. The [immutable producer snapshot](../promotion-packages/snapshots/b2-minimal-promotion-package-v1.0/releases/b2-minimal-promotion-package-v1.0/b2-governance-cohort-indeterminate-evidence-review-v1.0.json).
2. The [consumer Admissibility Review](admissibility/b2-governance-cohort-indeterminate-evidence-review-v1.0.json).
3. The [consumer Promotion Decision](decisions/b2-governance-cohort-indeterminate-evidence-review-v1.0.json).

The producer package satisfied the contract's minimum producer disclosures as follows:

| Contract requirement | Producer field or binding |
| --- | --- |
| Stable package identifier | `package_id` |
| Immutable package version or content address | `package_version`, `package_content_digest`, `producer_commit` |
| Accountable producer | `producer_repository`, `producer_commit` |
| Precise promotion claim | `candidate_claim` |
| Bounded requested scope | `proposed_foundation_repository`, `proposed_foundation_surface` |
| Submitted evidence references | `source_artifact_refs_and_hashes` |
| Artifact origin, version, and custody | Per-artifact path, source commit, lineage role, and digest |
| Assumptions and known limitations | Frozen registration/rule references and `known_limitations` |
| Producer non-claims | `excluded_claims`, `non_authority_statement` |
| Declared purpose | `package_purpose = indeterminate_evidence_review` |
| Empirical outcome | `cohort_outcome = indeterminate` |
| Complete requested review state | Canonical schema/version binding and `package_status = current` |

The Admissibility Review is `admissible_with_limitations`. The Promotion Decision is `accepted_with_constraints`, which is permitted by the contract for an `indeterminate` outcome with `indeterminate_evidence_review` purpose. Its sole authorized effect is `bounded_formalization` of the producer's stated foundation surface.

The decision explicitly excludes candidate-invariant authority, theorem or proof authority, implementation or conformance authority, and execution or runtime authority. It also preserves the producer's limitations, missing measurements, uncertainty, exclusions, and non-claims. The exact producer representation remains available in the immutable snapshot; the consumer records do not rewrite it.

Validate the repository-owned records with:

```sh
python3 tools/validate_promotion_records.py
```
