# Structural Analysis Research

[![LaTeX validation](actions/workflows/latex.yml/badge.svg)](actions/workflows/latex.yml)

This repository contains a three-paper mathematical research program on dependency, canonical structural analysis, and foundations for structural analysis.

## Research progression

### Paper 1

**The Mathematics of Dependency**

**Question:** What is dependency?

↓

### Paper 2

**Canonical Structural Analysis**

**Question:** What is the graph?

↓

### Paper 3

**Foundations for Structural Analysis**

**Question:** What is a structural analysis?


## Current repository status

Canonical paper PDFs are present at:

- [paper-1-dependency/pdf/paper1.pdf](paper-1-dependency/pdf/paper1.pdf)
- [paper-2-canonical-structural-analysis/pdf/paper2.pdf](paper-2-canonical-structural-analysis/pdf/paper2.pdf)
- [paper-3-foundations-structural-analysis/pdf/paper3.pdf](paper-3-foundations-structural-analysis/pdf/paper3.pdf)

Current source status: `main.tex` and `references.bib` are present in each paper directory; local LaTeX builds require LaTeX tooling such as `latexmk` or `pdflatex`.


## Continuous LaTeX validation

This repository is self-validating through the GitHub Actions workflow at `.github/workflows/latex.yml`. The workflow builds each paper independently with `latexmk -pdf main.tex` in a maintained TeX Live environment:

- `paper-1-dependency/`
- `paper-2-canonical-structural-analysis/`
- `paper-3-foundations-structural-analysis/`

Each matrix job runs in the paper directory so the bibliography, cross-references, labels, included files, figures, and appendices must resolve from that paper's own source tree. A failure in any paper fails the workflow, while `fail-fast: false` lets the run report which papers passed or failed.

The workflow treats the committed PDFs under `paper-*/pdf/paper*.pdf` as canonical published artifacts and never writes to those paths. Generated PDFs are produced as transient CI outputs and uploaded only as workflow artifacts together with `build.log` and useful auxiliary files for debugging.

### Local build instructions

To reproduce the CI build locally, install a TeX Live distribution with `latexmk`, then run each paper from its own directory:

```sh
cd paper-1-dependency && latexmk -pdf main.tex
cd ../paper-2-canonical-structural-analysis && latexmk -pdf main.tex
cd ../paper-3-foundations-structural-analysis && latexmk -pdf main.tex
```

Local builds generate `main.pdf` and LaTeX auxiliary files beside each `main.tex`. Do not copy those generated files over the canonical published PDFs in the `pdf/` directories unless intentionally publishing a new canonical artifact through the repository's review process.

## Repository organization

Each paper is organized as a self-contained directory intended to hold its manuscript source, bibliography, appendices, figures, and generated PDF output.

- `paper-1-dependency/` — Paper 1: The Mathematics of Dependency
- `paper-2-canonical-structural-analysis/` — Paper 2: Canonical Structural Analysis
- `paper-3-foundations-structural-analysis/` — Paper 3: Foundations for Structural Analysis
- `figures/` — top-level figure organization by paper

Each paper can be compiled independently once its manuscript sources are present in its directory. The trilogy forms a progressive research program: Paper 1 develops dependency, Paper 2 develops the canonical graph perspective, and Paper 3 develops the foundations for structural analysis.
