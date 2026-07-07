# Research Object ID Policy

This repository uses stable, human-readable IDs for canonical research objects.
Phase 1 introduces only a minimal canonical foundation: manifests, seed objects, source provenance, structured dependencies, validation metadata, export placeholders, and a local validator.

## ID format

Every research object ID MUST have the form:

```text
<kind>.<domain>.<slug>
```

- `kind` identifies the object category, such as `definition`, `theorem`, `concept`, `claim`, or `interface`.
- `domain` identifies the local research domain vocabulary.
- `slug` is a lowercase, hyphenated stable name for the object.

Paper identifiers MUST use the scalable form `paper-<number>-<slug>`, for example `paper-4-example-extension`.

The object's `id` field MUST equal the concatenation of its `kind`, `domain`, and `slug` fields.

## Stability rules

- IDs are stable references, not display titles.
- Titles and summaries may be edited without changing IDs.
- An ID should change only when the referenced research object changes identity.
- Deprecated objects should remain addressable and use `lifecycle_status: deprecated` rather than being silently reused for a different object.

## Phase 1 boundaries

Phase 1 does not define graph exports, JSON-LD, LLM export formats, proof-assistant bridges, or graph database support. Those integrations require later explicit phases.

## Local validation

Run the lightweight validator from the repository root:

```sh
python tools/validate_research_objects.py
```

The validator checks that paper manifests parse, referenced files exist, seed objects validate against `schemas/research-object.schema.json`, source anchors exist, source line ranges are ordered and in bounds, dependency targets resolve to existing objects, and stable IDs match `<kind>.<domain>.<slug>`.
