# Canonical Fixture Schema Validation

Canonical fixture schema validation is a repository-level correctness check. It validates each canonical research-object fixture against the JSON Schema declared by that fixture before adapter conformance is evaluated.

## Validation workflow

Run:

```bash
python tools/validate_canonical_fixtures.py
```

The command discovers canonical fixtures, loads each fixture's declared schema, validates the fixture with deterministic Draft 2020-12 checks, and exits non-zero when any schema violation is found. Failure output is sorted and reports the fixture, schema, JSON path, violated constraint, and validation message.

## Fixture discovery

Fixtures are discovered from `conformance/fixtures/*.fixture.json`. A new canonical fixture participates automatically when it is added to that directory and declares its schema with `schema_path`.

## Schema discovery

Each fixture declares its schema using a repository-relative `schema_path`. The validator does not rely on a hard-coded fixture-to-schema mapping. This preserves the canonical flow:

```text
Canonical Research Object
  -> Canonical Fixture
  -> Declared Canonical Schema
  -> Deterministic Validation
  -> Continuous Integration
```

## Developer workflow

When adding or changing a canonical research object fixture:

1. Add or update the canonical fixture under `conformance/fixtures/`.
2. Declare the fixture schema in the fixture's `schema_path` field.
3. Keep fixtures as semantic specifications; do not add adapter execution semantics to the schema validation path.
4. Run `python tools/validate_canonical_fixtures.py`.
5. Run the relevant conformance harness only after the fixture schema contract passes.

## CI behavior

The GitHub Actions conformance workflow runs fixture schema validation before adapter conformance steps. Any invalid canonical fixture fails CI, preventing adapter evidence from becoming a substitute for the canonical fixture contract.

## Architectural boundary

Schema validation checks fixture shape and declared canonical semantics only. It does not execute adapters, produce evidence envelopes, change comparator behavior, or alter runtime execution paths. Adapters remain evidence producers, while fixtures remain implementation-independent semantic specifications.
