# Research-object lifecycle and authority

Research-object maturity, editorial lifecycle, and canonical authority are separate axes. No value on one axis silently changes another.

## Maturity transitions

- **`seed`** records an identified statement and source pointer for later work. It may be incomplete, has not been checked as a faithful extraction, and is not canonical.
- **`extracted`** requires a reviewer or author to check the statement against the cited source, confirm the anchor or line range, and record all known research-object dependencies. Extraction establishes traceability, not correctness or authority.
- **`verified`** requires an extracted object, a successful recorded validation of its stated contract, at least one repository evidence artifact, and a recorded review that assesses that evidence. Verification is necessary but not sufficient for canonical authority.

Transitions are monotonic for one object version: `seed` to `extracted` to `verified`. If meaning changes, create a new version and repeat the applicable checks rather than retaining inherited maturity.

## Editorial lifecycle

- **`draft`** is still being prepared. A draft may be a `seed` or `extracted` object, but cannot claim canonical authority.
- **`reviewed`** has a recorded review and must be at least `extracted`. Review does not by itself make an object canonical.
- **`published`** is a reviewed version released by the repository. A published canonical object must also be `verified`; publication alone does not grant authority.
- **`deprecated`** identifies a version that must not make a current canonical claim.

Thus maturity describes the strength of the object record, while lifecycle describes editorial handling.

## Canonical authority

Canonical status is explicit in `authority_status`; it is not derived from maturity or lifecycle. This prevents a mechanical validation, review event, or publication event from silently granting research authority.

`authority_status: canonical` is permitted only when all of the following are recorded:

1. `maturity` is `verified`;
2. `lifecycle_status` is `reviewed` or `published`;
3. `validation.status` is `validated`;
4. `review_reference` identifies an existing repository review artifact; and
5. `evidence_references` contains at least one existing repository evidence artifact.

All other records use `authority_status: noncanonical`. In particular, every `seed` is noncanonical. References demonstrate that the prerequisites were recorded; they do not allow the validator to invent or broaden the review's authority.
