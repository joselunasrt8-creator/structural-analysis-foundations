# Reproducibility Specification

This document is the authoritative repository policy for reproducible research builds in Structural Analysis Foundations. It defines repository-level reproducibility requirements independently of manuscript content.

## Authority and artifact vocabulary

- **Authoritative research object:** an accepted, versioned object that governs research meaning within its declared scope.
- **Human-authored manuscript source:** a paper's `main.tex`, `references.bib`, and paper-local included prose, figures, and appendices. It governs narrative or scholarly content not yet represented by an accepted research object.
- **Generated candidate artifact:** a reproducible review output, including `main.pdf`, logs, auxiliary files, previews, and reports. It is neither authority nor a publication.
- **Immutable release artifact:** a reviewed, committed `pdf/paperN.pdf` produced from an identified source commit. Its bytes are not overwritten after publication; a correction is published as a new release artifact.

For content represented by an accepted research object, precedence is **authoritative research object → human-authored manuscript source → immutable release artifact**. If all three disagree, the research object wins. If no accepted object covers the content, manuscript source wins. In either case, a differing committed PDF is a stale release, not competing authority, and must not be presented as aligned until a new release passes the transition below.

## Reproducibility objective

The repository is reproducible when each paper can be built from its own source tree, with the documented TeX environment and build command, without depending on another paper's files and without replacing immutable release artifacts as a side effect of validation.

Reproducibility in this repository means:

- the source topology is explicit;
- each paper has an independent build boundary;
- continuous integration validates the same build boundary used locally;
- generated build outputs are treated as temporary workflow artifacts; and
- immutable release artifacts are created only through an intentional release action.

## Repository invariants

The repository contains three independent research papers:

1. `paper-1-dependency/`
2. `paper-2-canonical-structural-analysis/`
3. `paper-3-foundations-structural-analysis/`

Each paper must remain independently buildable. A paper is independently buildable when its build can start from that paper's directory and resolve its manuscript, bibliography, appendices, figures, and local inputs from that paper's own source tree.

Each paper owns the following required surfaces:

- `main.tex`
- `references.bib`
- `figures/`
- `appendices/`
- `pdf/paperN.pdf`, where `N` is the paper number

No paper may depend on another paper's source tree. In particular:

- Paper 1 source must not import, include, or reference Paper 2 or Paper 3 source files.
- Paper 2 source must not import, include, or reference Paper 1 or Paper 3 source files.
- Paper 3 source must not import, include, or reference Paper 1 or Paper 2 source files.
- Shared research meaning may be discussed in manuscript prose, but build inputs must remain local to the paper being built.

## Release artifacts

The current immutable PDF release artifacts are:

- `paper-1-dependency/pdf/paper1.pdf`
- `paper-2-canonical-structural-analysis/pdf/paper2.pdf`
- `paper-3-foundations-structural-analysis/pdf/paper3.pdf`

These files are release artifacts, not routine CI outputs. CI must never overwrite them.

Generated PDFs such as `main.pdf` are generated candidate artifacts only. They may be used to inspect a build, debug a pull request, or compare candidate output, but they are not publications. Only an explicit, reviewed release action may add a new `pdf/paperN.pdf` release artifact.

## Build reproducibility

### Required TeX distribution

GitHub Actions validates builds with TeX Live 2025 through the maintained LaTeX action configured in `.github/workflows/latex.yml`. Local reproducers should use TeX Live 2025 when exact CI parity is required.

A newer TeX Live distribution may be useful for local experimentation, but differences introduced by a newer distribution do not redefine the repository's reproducibility baseline. If the CI TeX Live version changes, this document and the workflow should be updated together.

### GitHub Actions workflow

The repository's validation workflow is `.github/workflows/latex.yml`. It runs a matrix build with one job per paper and invokes `latexmk` from inside the corresponding paper directory.

The CI workflow is expected to:

- check out the repository read-only for validation purposes;
- build each paper independently;
- use `latexmk` as the compiler driver;
- pass file-line errors, halt-on-error behavior, and nonstop interaction flags to LaTeX;
- collect build logs and auxiliary outputs for workflow inspection; and
- upload generated outputs as temporary workflow artifacts.

The workflow must not write generated PDFs into any `pdf/paperN.pdf` release-artifact path.

### Expected build command

The canonical per-paper build command is:

```sh
latexmk -pdf -file-line-error -halt-on-error -interaction=nonstopmode main.tex
```

It must be run from the paper directory being validated. For example:

```sh
cd paper-1-dependency
latexmk -pdf -file-line-error -halt-on-error -interaction=nonstopmode main.tex
```

Equivalent local commands are acceptable for authoring, provided they preserve the same paper-local build boundary and do not overwrite immutable PDF release artifacts.

### Bibliography requirements

Each paper owns its own `references.bib`. Bibliography entries required by a paper must be present in that paper's bibliography file or otherwise resolvable from files inside that paper's source tree.

Bibliography reproducibility requires that:

- citations resolve without reading another paper's `references.bib`;
- generated bibliography outputs such as `.bbl` and `.blg` remain build artifacts unless intentionally committed as part of a documented policy change;
- changes to citation keys, bibliography style, or bibliography data are treated as manuscript or editorial changes for the affected paper; and
- bibliography warnings that affect rendered citations or references must be resolved before a build is considered reproducible.

### Deterministic compilation expectations

A reproducible build should be deterministic for repository purposes: repeated builds from the same commit, same paper directory, and same TeX Live baseline should either succeed with materially equivalent rendered output or fail in the same way.

The following expectations apply:

- builds must not require network access during LaTeX compilation;
- builds must not depend on files outside the paper's source tree, except for installed TeX distribution files;
- build scripts must not mutate manuscript sources as a side effect of validation;
- timestamps, object identifiers, compression metadata, or other PDF metadata may vary unless the release process explicitly normalizes them;
- warning-only changes are not acceptable if they change citations, references, labels, figure inclusion, page structure, or mathematical content; and
- generated auxiliary files must be reproducible consequences of source files, not required hidden inputs.

## Repository evolution

Repository changes fall into separate governance classes.

### Research changes

Research changes alter manuscript substance or canonical research artifacts. Examples include:

- edits to theorem statements, proofs, definitions, examples, or exposition;
- changes to figures, appendices, citations, or bibliography entries that affect a paper's scholarly content;
- changes to `main.tex` or included paper-local source files; and
- publication of an immutable `pdf/paperN.pdf` release artifact.

Research changes require paper-specific review and must preserve the independent build boundary of the affected paper.

### Documentation changes

Documentation changes explain repository use, governance, build policy, or release policy without changing manuscript substance. Examples include:

- updates to `README.md`;
- updates to `REPRODUCIBILITY.md`;
- contributor notes; and
- explanatory comments that do not change build behavior.

Documentation changes must not modify immutable release artifacts or manuscript content unless they are explicitly reclassified as research changes.

### Infrastructure changes

Infrastructure changes alter validation, automation, dependency baselines, or repository mechanics. Examples include:

- updates to GitHub Actions workflows;
- changes to TeX Live versions, build flags, or artifact collection behavior;
- build scripts or linting configuration; and
- repository automation that can create, move, or delete generated artifacts.

Infrastructure changes must preserve the repository invariants in this document. Any infrastructure change that can write to release-artifact paths must be treated as release-sensitive and reviewed as a potential research or release change.

## Release policy

New PDF release artifacts should be published only when at least one of the following conditions is true:

- manuscript content changes;
- accepted editorial revisions occur; or
- a version number changes.

PDF release artifacts must never be published simply because CI runs. CI validates generated candidate artifacts; it does not publish them.

When a PDF release artifact is created, the release change must identify:

- which paper changed;
- why regeneration is required;
- which source commit produced the PDF;
- which TeX baseline and build command were used; and
- whether the change is research, editorial, or version-only.

### Accepted-change-to-release transition

An accepted research change reaches publication only through this ordered transition:

1. Review and accept the changed research object; record its version and scope. If the change has no object representation, record acceptance of the manuscript change instead.
2. Update the human-authored manuscript source so every selected object statement and version is represented accurately, with no unresolved semantic differences.
3. Validate object schemas/invariants and the paper-local source boundary.
4. Build `main.pdf` as a generated candidate artifact using the documented TeX baseline and command.
5. Compare the candidate against the accepted objects and manuscript source. Review rendered equations, citations, references, figures, and other material content; byte equality is not required when only permitted PDF metadata differs.
6. Record the source commit, selected object versions, TeX baseline, build command, validation evidence, and candidate digest in release provenance.
7. In an explicit release change, publish the reviewed candidate at `pdf/paperN.pdf` as a new immutable release artifact; tag or otherwise version it so later corrections do not rewrite its identity.

A release commit may include source changes and the corresponding new PDF release artifact when needed to keep them aligned. It must not include unrelated infrastructure or documentation drift unless explicitly justified. Until steps 1–7 pass, an older committed PDF remains historical but is marked stale relative to the accepted objects or manuscript source.

## Acceptance criteria

This document is the authoritative repository policy governing reproducible research builds. Future changes to research objects, paper sources, PDF release artifacts, CI workflows, build scripts, or release procedures should be evaluated against this specification.

A repository change satisfies this reproducibility specification when it:

- preserves independent buildability for all three papers;
- does not introduce cross-paper source-tree dependencies;
- keeps immutable PDF release artifacts separate from generated candidate PDFs;
- uses the documented TeX baseline and build boundary for validation;
- classifies repository evolution as research, documentation, or infrastructure change;
- publishes PDF release artifacts only under the release policy;
- verifies that each manuscript statement covered by an accepted research object has the same meaning, object identity, and version as that object;
- verifies that each generated candidate PDF materially matches both the accepted objects selected for the paper and the human-authored manuscript source;
- records release provenance sufficient to associate the immutable PDF with its source commit, selected object versions, build environment, command, and digest;
- detects a stale release whenever accepted object meaning or manuscript source has changed since the recorded release provenance, or when a fresh candidate materially differs from the committed PDF for reasons other than permitted metadata variation;
- blocks publication while any object/source/candidate mismatch is unresolved and marks an existing mismatched PDF release as stale rather than treating it as authority; and
- leaves reproducibility evidence visible through build logs, workflow artifacts, or documented local commands.
