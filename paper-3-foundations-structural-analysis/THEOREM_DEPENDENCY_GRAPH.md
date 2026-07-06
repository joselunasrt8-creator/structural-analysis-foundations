# Theorem Dependency Graph (internal)

This file tracks mathematical dependencies among the v0.3 framework theorems and supporting definitions/lemmas.
It is an internal research artifact (not intended for inclusion in the manuscript).

Legend:
- **Depends on**: prerequisites that must already be defined/stated.
- **Produces**: downstream theorems that (likely) rely on this result.
- **Notes**: potential missing lemmas/definitions revealed by auditing.

---

## Proposition 1 — Typed Well-Formedness (`prop:typed-well-formedness`)

Depends on:
- Definition (Admissible observation spaces): `def:observation-spaces` (Paper 3)
- Definition (Structural analysis operator): `def:structural-analysis-operator` (Paper 3)
- Canonical structural object notation $\Sigma$ (Paper 2 → assumed in Paper 3)

Produces:
- (Optional) Theorem 2 (Representation invariance), if later statements cite typed uniqueness/totality explicitly.

Notes:
- This is a definitional/typing consequence (kept for citation convenience).
- If “well-definedness” is later strengthened beyond typing (e.g., extensionality on $\equiv$-classes), it should re-enter as a substantive theorem with a new identifier.

---

## Theorem 2 — Representation Invariance (`thm:representation-invariance`)

Depends on:
- Definition (Representation-invariant observable): `def:representation-invariant-observable` (Paper 3)
- Representation-artifact equivalence $\equiv$ on canonical structural objects (Paper 2)
- (Optional) Proposition 1 (`prop:typed-well-formedness`), if typed totality/uniqueness is cited explicitly

Produces:
- Theorem 3 (Composition) (if composition must preserve invariance)
- Theorem 4 (Perturbation compatibility) (if perturbations interact with equivalence)

Notes:
- Evidence objects: require invariance of $y$; for $e$, likely require existence of some checkable evidence rather than equality across representations.

---

## Theorem 3 — Composition (`thm:composition`)

Depends on:
- Definition (Admissible observation spaces): `def:observation-spaces` (Paper 3)
- Definition (Structural analysis operator): `def:structural-analysis-operator` (Paper 3)
- (Optional) Theorem 2 (Representation invariance), if admissibility includes invariance
- Any closure conditions on $\mathsf{Obs}$ needed by the statement (e.g., products, function spaces)

Produces:
- Theorem 4 (Perturbation compatibility) (if compatibility is preserved under composition)

Notes:
- Avoid assuming closure: state conditional results ("if $\mathsf{Obs}$ is closed under X, then...").
- If evidence is propagated, may require a definition of an evidence-combination operator (or explicitly avoid it).

---

## Theorem 4 — Perturbation Compatibility (`thm:perturbation-compatibility`)

Depends on:
- Definition (Perturbation family): `def:perturbation-family` (Paper 3)
- Definition (Structural analysis operator): `def:structural-analysis-operator` (Paper 3)
- Theorem 1 (Well-defined structural analysis)
- (Optional) Theorem 2 (Representation invariance), depending on how perturbations respect $\equiv$

Produces:
- Future instantiations: resilience/redundancy/blast-radius operators, counterfactual analyses, robustness/sensitivity notions

Notes:
- Decide the precise compatibility notion (commutation is likely too strong).
- Quantitative outputs may want a stability bound; set-valued outputs may want monotonicity/refinement.

---

## Dependency-audit workflow checklist (per theorem)

Stage 1 — Formal statement only
- [ ] Every symbol is introduced earlier (or listed as a prerequisite).
- [ ] All types/codomains are explicit.

Stage 2 — Dependency audit
- [ ] All referenced definitions exist and are stable.
- [ ] No hidden closure assumptions (state them explicitly).
- [ ] No cycles in theorem prerequisites.

Stage 3 — Proof sketch (≤ 1 page)
- [ ] Sketch succeeds without introducing new objects “because convenient”.
- [ ] If the sketch fails: revise the theorem statement/assumptions.

Stage 4 — Formal proof
- [ ] Only after the sketch is stable.
