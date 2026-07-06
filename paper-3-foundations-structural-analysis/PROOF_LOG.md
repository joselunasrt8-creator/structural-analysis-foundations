# Proof Log (Internal)

This file tracks the *development status and history* of theorem work for Paper 3. It is not part of the manuscript.

---

## Manuscript review notes (Paper 3 v0.2)

- **Date:** 2026-07-06
- **Milestone:** Paper 3 has crossed from **framework discovery** into **framework validation** (moving from defining objects/predicates to defining **admissible computations** over canonical structural objects).
- **Series progression to preserve**
  - Paper 1: dependency predicate — “What is dependency?”
  - Paper 2: canonical structural object — “What is the graph?”
  - Paper 3: structural analysis operator — “What is a structural analysis?”
- **Why the minimal interface feels right at v0.2** (avoid adding definitions unless proof obligations force them):
  - admissible observation spaces
  - structural observables
  - representation-invariant observables
  - evidence / witness objects
  - structural analysis operators
  - perturbation families
- **Key recommendation before theorem phase:** add **one framing sentence** immediately before the Section 5 definitions to explain the abstraction level (explanatory, not theoretical). Candidate wording:
  - “The following definitions specify the minimal interface required for structural analyses over canonical structural objects. They are intentionally independent of any particular analysis family, algorithm, or application domain so that subsequent results apply uniformly across the taxonomy introduced in Section 4.”
- **Theorem order to keep:** well-definedness → representation invariance → composition → perturbation compatibility.
- **Practical rule for the theorem phase:**
  - If a theorem can’t be stated, introduce the smallest missing definition.
  - If a proof can’t be completed, introduce the required structure at that point.
  - Otherwise, don’t expand the interface.
- **Explicit avoid-unless-needed:** monoids / categories / algebras / lattices / semirings (only introduce if forced by proofs).

---

## Theorem template

### Theorem N — <Title>

**Existence gate**
- □ Exact statement fixed
- □ Minimal definitions identified (necessary + sufficient)
- □ Counterexample attempt across taxonomy families
- □ Classified (theorem / proposition / lemma / definition)

**Stabilization**
- □ Dependency audit passed
- □ Proof sketch
- □ Formal proof

**Manuscript promotion gate**
- □ Necessity
- □ Independence
- □ Narrative role
- □ Decision recorded (promote to `main.tex` / stay internal)

**Issues**
- <bulleted list>

**Open questions**
- <bulleted list>

**Change log**
- YYYY-MM-DD: <what changed and why>

---

## Proposition 1 — Typed Well-Formedness (formerly planned Theorem 1)
**Existence gate**
- ☑ Exact statement fixed
- ☑ Minimal definitions identified (necessary + sufficient)
- ☑ Counterexample attempt across taxonomy families
- ☑ Classified (proposition: definitional/typing consequence)

**Stabilization**
- □ Dependency audit passed
- □ Proof sketch
- □ Formal proof

**Manuscript promotion gate**
- □ Necessity
- □ Independence
- □ Narrative role
- ☑ Decision recorded (stay internal; cite only if convenient)

**Issues**
- None

**Open questions**
- Does composition require an additional lemma?

**Change log**
- 2026-07-06: Initialized theorem entry and checklist.
- 2026-07-06: Updated entry to match the refined existence/promotion-gate workflow.
- 2026-07-06: Completed existence gate; downgraded planned Theorem 1 to Proposition 1 (typed well-formedness) and recorded “stay internal” decision.


---

## Definition Sufficiency Audit — Composition and Counterfactual Structural Perturbations

**Date:** 2026-07-06

**Intent**
- Determine whether the current Composition candidate requires a new mathematical object to support counterfactual structural perturbations, or whether the existing trilogy already supplies the necessary semantics.

**Exact scope**
- Audited Paper 1 dependency semantics, Paper 2 canonical structural objects / counterfactual deletion / projection closure, Paper 3 structural analysis operators and perturbation families, and the internal Composition candidate.
- Mutated only this proof log and, if needed, the internal theorem dependency graph.
- Left `v0_3_theorems.tex` unchanged because the audit does not justify adding a definition there.
- Did not modify `main.tex`.

**Preserved invariants**
- No proof construction.
- No perturbation propagation rule.
- No algebraic structure.
- No assumption that Composition must be promoted to a theorem.
- No widening of the Paper 3 operator interface beyond deterministic maps from canonical structural objects to admitted observation spaces.

**Mutation-capable surfaces**
- `paper-3-foundations-structural-analysis/PROOF_LOG.md`
- `paper-3-foundations-structural-analysis/THEOREM_DEPENDENCY_GRAPH.md`

**Replay implications**
- This audit records a classification decision only. It does not alter executable, compilation, theorem, or manuscript semantics.
- Future theorem work should replay this audit before introducing any new object for Composition, counterfactual analysis, or perturbation compatibility.

**Proof requirements deliberately not initiated**
- No formal proof of Composition.
- No formal proof of perturbation compatibility.
- No construction of perturbation propagation across evidence, pipelines, or analysis families.

**Validation requirements**
- Verify that the trilogy already defines: dependency by counterfactual deletion and reachability; canonical structural object; counterfactual deletion on structural graphs; projection/deletion compatibility; structural analysis operators; perturbation families as deterministic transformations on canonical structural objects.
- Verify that no existing definition conflicts with treating perturbed objects as ordinary canonical structural objects consumed by ordinary structural analysis operators.

### Four-outcome audit

1. **Existing definition is already sufficient.**
   - **Decision: selected for basic counterfactual structural perturbations.**
   - Paper 3 already defines a perturbation family as deterministic transformations `\delta:\Sigma\to\Sigma`, explicitly intended to model counterfactual edits.
   - Paper 3 already defines a structural analysis operator as a deterministic operator `\mathsf A:\Sigma\to Y` for some `Y\in\mathsf{Obs}`.
   - Notation normalized: `\Sigma` denotes the domain of canonical structural objects, while `W\in\Sigma` denotes an individual structural object. Therefore, for any admitted perturbation `\delta\in\Delta`, the perturbed object `\delta(W)` is already in the same canonical-object domain consumed by `\mathsf A`. The expression `\mathsf A(\delta(W))` is well-typed without introducing a new object.
   - Paper 1 supplies a concrete instance of this pattern through deletion and reachability: dependency is defined by applying a counterfactual removal operator and then evaluating reachability.
   - Paper 2 lifts the same semantics to canonical structural objects by defining counterfactual deletion on structural graphs and proving that projection and counterfactual deletion commute up to structural equivalence.
   - Consequence: **Composition does not require genuinely new mathematics merely to support counterfactual structural perturbations.**

2. **Existing definitions imply the property indirectly.**
   - **Decision: applicable only if a citable internal statement is desired.**
   - A lemma could record the typing fact: if `\delta:\Sigma\to\Sigma` is in a perturbation family and `\mathsf A:\Sigma\to Y` is a structural analysis operator, then `\mathsf A\circ\delta:\Sigma\to Y` is a deterministic total map into an admitted observation space.
   - This would be a lemma/proposition-level typing consequence, not a new theorem and not a new mathematical object.
   - The Perturbation Compatibility candidate is closed at the Existence Gate under this minimal typed-evaluability interpretation.
   - Stronger compatibility notions---stability, monotonicity, refinement, simulation, commutation, or output-side compatibility predicates---remain possible future theorem candidates and are intentionally deferred/uninstantiated.
   - No lemma is required before the framework can express counterfactual structural analyses; it would only prevent repeated re-explanation.

3. **Existing framework is insufficient.**
   - **Decision: not selected for the stated objective.**
   - The only insufficiency found concerns the current Composition candidate if it is read as closure of structural analysis operators under arbitrary second-stage maps `Y_1\to Y_2`.
   - Structural analysis operators are currently maps out of `\Sigma`, not maps out of arbitrary observation spaces. Thus `\mathsf A_2:Y_1\to Y_2` is not itself a structural analysis operator under the existing definition.
   - This is a post-observation admissibility issue, not a counterfactual-perturbation issue. It should not be repaired by introducing perturbation propagation, algebraic composition, or a new counterfactual object.
   - If future proof obligations genuinely require chained post-observation processing, the single minimal missing concept would be: **an admissible deterministic post-observation map** `f:Y_1\to Y_2` with `Y_1,Y_2\in\mathsf{Obs}`. The present audit does not require adding it.

4. **Existing framework is inconsistent.**
   - **Decision: not selected.**
   - No conflict was found among the audited definitions.
   - Paper 1 deletion/reachability semantics, Paper 2 canonical structural objects and counterfactual deletion, and Paper 3 perturbation families and structural analysis operators are mutually compatible for evaluating analyses on perturbed canonical structural objects.

### Final audit answer

Composition does **not** require genuinely new mathematics to support counterfactual structural perturbations. The trilogy already contains the necessary semantics: perturbations are deterministic endomaps on canonical structural objects, and structural analysis operators are deterministic maps out of canonical structural objects. The smallest justified action is to treat the Composition candidate as a typed-function/post-observation admissibility audit item, not as a new theorem and not as a new perturbation concept. If a future manuscript needs a reusable statement, add only a typing lemma for `\mathsf A\circ\delta`; otherwise no expansion is warranted.

**Remaining reconciliation gaps**
- Decide later whether Composition is needed at all as a promoted result, or whether it should remain an internal typed-composition observation.
- If future work needs chained analyses `Y_1\to Y_2`, address that narrowly as post-observation map admissibility, separate from perturbation semantics.

**Unresolved drift risks**
- Treating evidence-producing operators as if evidence automatically composes would introduce an unstated propagation rule; avoid this unless explicitly required.
- Treating arbitrary `Y_1\to Y_2` maps as structural analysis operators would silently widen the operator domain; avoid this unless a minimal post-observation-map definition is deliberately added.
