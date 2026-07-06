# Repository Audit

Audit date: 2026-07-06

This audit verifies repository structure, build readiness, PDF organization, documentation consistency, and paper independence for the Structural Analysis Foundations repository. It does not review, modify, or recommend changes to mathematical content, proofs, definitions, or research claims.

## Repository Health

Overall assessment: **Needs source-file reconciliation before publication-ready build validation.**

The repository clearly communicates the three-paper research progression and contains the expected paper directories, README files, and organizational subdirectories. However, the required `main.tex` and `references.bib` files are not present in any paper directory at audit time, so independent LaTeX builds cannot be validated yet. Each paper has a PDF, but the PDFs currently sit at the paper directory root while the paper READMEs describe generated PDFs under `pdf/`.

## Structure

Status: **Fail**

Expected paper directories:

| Paper | Directory present | `main.tex` | `references.bib` | `README.md` | `figures/` | `appendices/` | `pdf/` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Paper 1 | Pass | Fail | Fail | Pass | Pass | Pass | Pass |
| Paper 2 | Pass | Fail | Fail | Pass | Pass | Pass | Pass |
| Paper 3 | Pass | Fail | Fail | Pass | Pass | Pass | Pass |

## Build Validation

Status: **Fail: source files missing**

### Paper 1

Directory: `paper-1-dependency/`

- `main.tex`: not found.
- `references.bib`: not found.
- Figure-path validation: blocked because `main.tex` is absent.
- Appendix-path validation: blocked because `main.tex` is absent.
- Bibliography-path validation: blocked because `main.tex` and `references.bib` are absent.
- Independent-build validation: failed because required source files are absent.

### Paper 2

Directory: `paper-2-canonical-structural-analysis/`

- `main.tex`: not found.
- `references.bib`: not found.
- Figure-path validation: blocked because `main.tex` is absent.
- Appendix-path validation: blocked because `main.tex` is absent.
- Bibliography-path validation: blocked because `main.tex` and `references.bib` are absent.
- Independent-build validation: failed because required source files are absent.

### Paper 3

Directory: `paper-3-foundations-structural-analysis/`

- `main.tex`: not found.
- `references.bib`: not found.
- Figure-path validation: blocked because `main.tex` is absent.
- Appendix-path validation: blocked because `main.tex` is absent.
- Bibliography-path validation: blocked because `main.tex` and `references.bib` are absent.
- Independent-build validation: failed because required source files are absent.

## PDF Verification

Status: **Pass with organization recommendation**

| Paper | PDF found | Current location | README-stated generated PDF |
| --- | --- | --- | --- |
| Paper 1 | Pass | `paper-1-dependency/1.1 The_Mathematics_of_Dependency.pdf` | `paper-1-dependency/pdf/paper1.pdf` |
| Paper 2 | Pass | `paper-2-canonical-structural-analysis/1.1 Paper_2___Canonical_Structural_Analysis.pdf` | `paper-2-canonical-structural-analysis/pdf/paper2.pdf` |
| Paper 3 | Pass | `paper-3-foundations-structural-analysis/0.4 Paper_3___Foundations_for_Structural_Analysis_.pdf` | `paper-3-foundations-structural-analysis/pdf/paper3.pdf` |

The PDF filenames preserve paper-specific title/version information, but they are not located in the `pdf/` directories described by the READMEs. To avoid confusion, either move/copy generated PDFs into each paper's `pdf/` directory using the README-stated names, or update the READMEs to identify the current checked-in PDF filenames as canonical.

## Documentation

Status: **Pass with suggestions**

- The root README describes the three-paper program and correctly communicates the progression:
  - Paper 1: What is dependency?
  - Paper 2: What is the graph?
  - Paper 3: What is a structural analysis?
- Each paper README includes a research question, scope, build instructions, and generated PDF location.
- The build instructions are currently aspirational because `main.tex` is absent in each paper directory.

Suggested documentation improvements:

1. Add a short root-level "Current repository status" section that distinguishes scaffolded directories, checked-in PDFs, and source files awaiting reconciliation.
2. Update each paper README after sources are added to specify the exact compiler and bibliography workflow, such as `latexmk -pdf`, `biber`, or `bibtex` as applicable.
3. Align each README's generated-PDF path with the actual checked-in PDF organization.
4. Add a compact build matrix once all source files are present.

## Consistency

### Naming

Status: **Pass with minor recommendation**

- Paper directory names are lowercase, hyphenated, and descriptive.
- PDF filenames use version/title naming with spaces and underscores. This is understandable, but less automation-friendly than the directory naming convention.
- Recommendation: choose one canonical PDF convention before publication packaging, preferably under each paper's `pdf/` directory.

### Folders

Status: **Pass**

- Each paper directory has `figures/`, `appendices/`, and `pdf/` folders.
- Each paper directory is self-contained at the folder-structure level.
- Top-level `figures/paper1`, `figures/paper2`, and `figures/paper3` also exist; these should remain auxiliary only unless the build system intentionally references them. Paper builds should prefer local paper-level `figures/` directories to preserve independence.

### README

Status: **Pass with source-status caveat**

- README capitalization and section structure are consistent.
- README content covers the required categories.
- README generated-PDF paths do not match current PDF locations.

### PDF organization

Status: **Pass with organization recommendation**

- One PDF exists for each paper.
- PDFs are not currently inside the paper-local `pdf/` folders.
- Recommend reconciling either file locations or README paths before release.

## Paper Independence

Status: **Not verifiable until source files are present**

The directory scaffold supports independent builds because each paper has its own paper directory with local `figures/`, `appendices/`, and `pdf/` folders. Independence cannot be proven at audit time because no `main.tex` or `references.bib` files are present to inspect for cross-paper dependencies.

## Recommendations

Only structural recommendations are included below.

1. Add or restore `main.tex` and `references.bib` to each paper directory.
2. Keep all paper build inputs local to the corresponding paper directory.
3. Reconcile PDF organization by either:
   - moving/copying PDFs into each paper's `pdf/` directory with stable generated names, or
   - updating the paper READMEs to identify the current root-level PDF filenames as canonical.
4. After source files are present, run `latexmk -pdf main.tex` from each paper directory and record the exact successful build commands.
5. If top-level `figures/` remains, document whether it is archival/auxiliary; do not make paper builds depend on it unless paper independence is intentionally changed.
