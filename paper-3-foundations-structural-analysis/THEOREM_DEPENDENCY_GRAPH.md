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
- Ordinary typed function composition, if the result is weakened to a typing lemma/proposition
- A future post-observation-map admissibility definition only if the statement insists that arbitrary maps $Y_1\to Y_2$ participate in the structural-analysis interface

Produces:
- No required perturbation semantics. Counterfactual structural perturbations are already supported by `def:perturbation-family` together with `def:structural-analysis-operator`.
- Theorem 4 (Perturbation compatibility) only if a later compatibility statement explicitly cites a typed-composition lemma.

Notes:
- Definition Sufficiency Audit (2026-07-06): Composition does not require a new mathematical object to support counterfactual structural perturbations.
- Existing perturbation families provide deterministic maps $\delta:\Sigma\to\Sigma$; existing structural analysis operators consume canonical structural objects, so $\mathsf A(\delta(\Sigma))$ is already well-typed.
- Do not introduce perturbation propagation, evidence-combination operators, algebraic structures, or product/function-space closure for this audit.
- If future proof obligations require chained post-observation processing, the single minimal missing concept is an admissible deterministic post-observation map $f:Y_1\to Y_2$ with $Y_1,Y_2\in\mathsf{Obs}$; this audit does not require adding it.

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

---

## Candidate Characterization — Admissible Structural Analysis Operators (`audit:admissible-operator-characterization`)

Depends on:
- Proposition 1 (`prop:typed-well-formedness`)
- Theorem 2 candidate (`thm:representation-invariance`)
- Canonical structural object boundary from Paper 2
- Definition (Structural analysis operator): `def:structural-analysis-operator`
- Definition (Perturbation family): `def:perturbation-family`
- Canonical Intermediate Boundary (`def:canonical-intermediate-boundary`)
- Composition and perturbation sufficiency audits already recorded in this graph/log

Produces:
- No theorem or proof obligation yet.
- A finite interface-specification horizon for Paper 3.
- A candidate-only characterization theorem horizon if future work proves sufficiency of the independent root clauses.

Accepted-property classification:

| Property | Classification | Dependency summary |
| --- | --- | --- |
| Typed Well-Formedness | Both; independent root interface clause | Root typing clause for total maps into admitted observation spaces. |
| Determinism | Necessary; independent unless folded into Typed Well-Formedness | Supports uniqueness of observable values; may be definitionally embedded. |
| Canonical Structural Objects | Necessary; independent | Supplies the operator domain boundary inherited from Paper 2. |
| Representation Invariance | Necessary for invariant observables; independent | Not implied by typing, determinism, or canonical-domain choice. |
| Domain Compatibility | Derivable for ordinary analyses; conditionally independent for external pre-analysis maps | Follows from operator domain typing unless an additional pre-analysis map is proposed. |
| Counterfactual Evaluability | Derivable | Follows from perturbation endomaps and structural-analysis-operator typing. |
| Perturbation Compatibility (minimal interpretation) | Derivable; redundant as a theorem-level property | Same content as typed evaluability of `A(delta(W))`. |
| Canonical Intermediate Boundary | Necessary for composition-like downstream invariance; independent of single-stage admissibility | Blocks representational divergence at intermediate codomains. |
| Downstream Invariance Distribution | Derivable | Follows from Representation Invariance plus Canonical Intermediate Boundary and downstream respectfulness. |

Dependency matrix (acyclic):

```text
P3 Canonical Structural Objects -> P1 Typed Well-Formedness
P2 Determinism -> P1 Typed Well-Formedness, when P1 includes uniqueness
P1 Typed Well-Formedness -> P5 Domain Compatibility
P3 Canonical Structural Objects -> P5 Domain Compatibility
P1 Typed Well-Formedness -> P6 Counterfactual Evaluability
P3 Canonical Structural Objects -> P6 Counterfactual Evaluability
P5 Domain Compatibility -> P6 Counterfactual Evaluability
P6 Counterfactual Evaluability -> P7 Perturbation Compatibility (minimal)
P4 Representation Invariance -> P9 Downstream Invariance Distribution
P8 Canonical Intermediate Boundary -> P9 Downstream Invariance Distribution
```

Existence Gate outcome:
- Q1: A finite list exists, but a finite **independent axiom set** is not presently justified because several accepted properties are corollaries or audit labels rather than independent axioms.
- Q2: Current independent properties are Typed Well-Formedness, Determinism if not definitionally embedded, Canonical Structural Objects, Representation Invariance, and Canonical Intermediate Boundary.
- Q3: Domain Compatibility, Counterfactual Evaluability, Perturbation Compatibility under the minimal interpretation, and Downstream Invariance Distribution are corollaries/redundant theorem-level candidates under the current interface.
- Q4: Paper 3 presently admits a finite interface specification. A Characterization Theorem remains candidate-only pending a future sufficiency argument.

Notes:
- The graph remains acyclic: all arrows point from root typing/domain/invariance/boundary clauses toward evaluability, minimal compatibility, and downstream distribution consequences.
- Do not introduce post-observation operator classes, output perturbations, metrics, preorders, algebraic structure, or evidence propagation solely to force a characterization theorem.
