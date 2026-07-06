# Paper 2: Canonical Structural Analysis

## Research question

What is the graph?

## Scope

This directory is the self-contained workspace for Paper 2, including manuscript source, bibliography, figures, appendices, and generated PDF output when available.

## Build instructions

When `main.tex` and `references.bib` are present, compile `main.tex` from this directory with the LaTeX engine and bibliography workflow used by the paper, for example:

```sh
latexmk -pdf main.tex
```

## Generated PDF location

The generated PDF for this paper should be stored at:

[pdf/paper2.pdf](pdf/paper2.pdf)

Current source status: `main.tex` and `references.bib` are present in this paper directory; local LaTeX builds require LaTeX tooling such as `latexmk` or `pdflatex`.
