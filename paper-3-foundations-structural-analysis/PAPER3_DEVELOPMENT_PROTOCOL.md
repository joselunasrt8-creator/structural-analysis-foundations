# Paper 3 Development Protocol (Internal)

This document is an internal research workflow protocol for Paper 3 and later papers in this theorem-driven framework research program. It is **not** part of the manuscript and should never be included in the PDF.

## 1. Always-Compiles Invariant

- **Every commit must compile successfully.**
- Experimental theorem files (e.g., `v0_3_theorems.tex`) are **never** included in `main.tex` until the relevant theorems are mathematically stable.
- Incomplete theorem development should live in isolated files that are not `\input{}`'d.

## 2. Theorem Development Workflow

A candidate result may enter the manuscript only after it has passed each quality gate below.

### 2.1 Existence gate ("does this theorem deserve to exist?")

Before attempting any proof sketch, answer:

1. **Exact statement:** fix the fully formal quantifiers and conclusion.
2. **Minimal interface:** identify which definitions are necessary and sufficient (no hidden assumptions).
3. **Counterexample attempt:** try to falsify the claim across taxonomy families / instantiations.
4. **Theorem vs. definitional consequence:** decide whether the result is genuinely nontrivial or should be reframed as a definition, proposition, or lemma.

#### Branch outcome

- If counterexamples exist: **revise** the statement/hypotheses (prefer revising the theorem before expanding the interface).
- If the claim survives but is immediate from definitions: **downgrade** to definition/proposition/lemma.
- If the claim survives and is nontrivial: **promote** to theorem candidate.

### 2.2 Stabilization gates (only after the existence gate passes)

1. **Dependency audit** (update `THEOREM_DEPENDENCY_GRAPH.md`).
2. **Proof sketch** (high-level argument; identify proof obligations).
3. **Formal proof** (complete, internally consistent).

### 2.3 Manuscript promotion gate ("does this result earn space in the paper?")

Immediately before moving a proved result into `main.tex`, check:

- **Necessity:** removing it would make the manuscript materially weaker.
- **Independence:** it is not already implied by existing definitions + earlier results.
- **Narrative role:** it advances the mathematical story (not merely an implementation fact).

If any check fails: keep the result in the theorem workspace and cite it only internally.

4. **Promotion** into `main.tex` (only after the promotion gate passes).

### 2.4 Feedback loops (when gates fail repeatedly)

- If a candidate repeatedly fails the **Existence gate**: revisit whether (i) the statement is actually needed, or (ii) the interface is missing a minimal definition/assumption.
- If multiple proved results repeatedly fail the **Manuscript promotion gate**: revisit the manuscript scope and consider whether those results belong in an appendix, a later paper, or should remain internal.

## 3. Definition Discipline

- Do **not** introduce a new definition unless an existing theorem cannot be proved without it.
- Prefer proving **lemmas** over expanding the core interface.
- Freeze interfaces before theorem development.

## 4. Research Philosophy

- Mathematics drives the framework.
- Failed proofs inform **theorem revision before interface revision**.
- Novelty is established through proof obligations and comparison with prior work, not by introducing additional abstractions.
