# Immutable Producer Package Snapshots

This directory contains byte-for-byte repository-local snapshots of producer-owned Minimal Promotion Packages. A snapshot preserves upstream provenance without creating a live producer dependency or changing ownership, meaning, lifecycle, or authority.

Snapshot contents are immutable. Corrections, withdrawals, and supersessions must be represented by new producer packages and append-only consumer records; they must not rewrite an existing snapshot.

## B2 Minimal Promotion Package v1.0

The `b2-minimal-promotion-package-v1.0/` directory preserves both supplied producer inputs without modification. Its internal `releases/` layout intentionally matches the unchanged path in `SHA256SUMS`.

Verify the byte-level package digest from the snapshot root:

```sh
cd promotion-packages/snapshots/b2-minimal-promotion-package-v1.0
sha256sum -c SHA256SUMS
```

The expected package-file digest is:

```text
26a0aaa66568277936c38db638eb7b6d00679528e24c2b29886e311561929ada
```

The producer-embedded canonical-content digest was independently recomputed using the declared deterministic JSON method, with `package_content_digest.digest` represented as an empty string. The recomputed value exactly matches the embedded value:

```text
4fb1e08a8a0489d6715ab30e9c52ee96d269d7dd7c1d7b918d38f10800832cca
```

These integrity results establish the reviewed package bytes. They do not establish admissibility, promotion, formal truth, implementation conformance, or execution authority.
