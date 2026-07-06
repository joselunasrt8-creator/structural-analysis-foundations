# Paper 1: The Mathematics of Dependency

## Research question

What is dependency?

## Scope

This directory is the self-contained workspace for Paper 1, including manuscript source, bibliography, figures, appendices, and generated PDF output when available.

## Build instructions

When `main.tex` and `references.bib` are present, compile `main.tex` from this directory with the LaTeX engine and bibliography workflow used by the paper, for example:

```sh
latexmk -pdf main.tex
```

## Generated PDF location

The generated PDF for this paper should be stored at:

[pdf/paper1.pdf](pdf/paper1.pdf)

Current blocker: `main.tex` and `references.bib` are not present in this paper directory, so LaTeX builds are not validated.
