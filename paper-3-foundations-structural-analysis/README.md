# Paper 3: Foundations for Structural Analysis

## Research question

What is a structural analysis?

## Scope

This directory is the self-contained workspace for Paper 3, including manuscript source, bibliography, figures, appendices, theorem-development notes, proof logs, dependency graphs, and generated PDF output when available.

## Build instructions

When `main.tex` and `references.bib` are present, compile `main.tex` from this directory with the LaTeX engine and bibliography workflow used by the paper, for example:

```sh
latexmk -pdf main.tex
```

## Generated PDF location

The generated PDF for this paper should be stored at:

[pdf/paper3.pdf](pdf/paper3.pdf)

Current blocker: `main.tex` and `references.bib` are not present in this paper directory, so LaTeX builds are not validated.
