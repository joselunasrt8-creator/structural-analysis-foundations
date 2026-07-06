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

