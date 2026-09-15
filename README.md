# Structural Analysis Foundations

<p align="center">
  <img
    src="figures/08A2BFBF-817F-4438-BACA-E9A4DCB31AB8.png"
    alt="Structural Analysis Foundations Research Program"
    width="100%">
</p>

Structural Analysis Foundations is a three-paper research program developing bounded mathematical models for structural analysis.

The program asks three progressively broader questions:

- **Paper 1:** How can workload-relative dependency be formalized?
- **Paper 2:** Under what definitions can structural analysis be made canonical and representation-invariant?
- **Paper 3:** What mathematical interface can characterize a class of admissible structural-analysis operators?

The papers develop formal objects and propositions inside explicitly declared models. They do not establish that those models are the unique, complete, or universally correct description of real software systems.

```text
Formal definition ≠ empirical discovery
Proof within assumptions ≠ truth outside assumptions
Canonical representation ≠ uniquely natural representation
Representation invariance ≠ external validity
Mathematical admissibility ≠ operational usefulness
```

## Research program

### Paper 1 — The Mathematics of Dependency

**Research question:** How can workload-relative dependency be formalized?

**Contribution:** Defines dependency relative to a specified workload and observational/modeling context rather than treating dependency as an undefined informal graph relation.

Its results are conditional on the paper's definitions, structural object, workload model, and assumptions. The formalism does not by itself establish that every real-world notion of software dependency is captured by the predicate.

### Paper 2 — Canonical Structural Analysis

**Research question:** Under what declared equivalences can a structural object and analysis be canonical?

**Contribution:** Develops deterministic, representation-invariant structural analysis over defined canonical structural objects.

Here, “canonical” means canonical under the paper's formal representation/equivalence contract. It does not mean that the representation is the only legitimate ontology of a real system or that all consequential runtime structure is observable in it.

### Paper 3 — Foundations for Structural Analysis

**Research question:** What properties characterize the proposed class of structural analyses?

**Contribution:** Investigates a minimal mathematical interface for admissible structural-analysis operators under the paper's definitions.

“Admissible” is a formal property within that framework. It is not execution permission, scientific authority, safety certification, or proof that an operator is useful for a particular engineering decision.

## Formal claim boundary

This repository can establish claims of the form:

> Given definitions D, assumptions A, and model M, proposition P follows by the stated argument/proof.

It cannot obtain empirical premises merely by formalizing them.

A valid theorem can coexist with a poor real-world model. Therefore every downstream use must distinguish:

1. **internal validity** — does the result follow from the definitions and assumptions?;
2. **model adequacy** — does the mathematical object preserve the real-system properties relevant to the intended claim?;
3. **external correspondence** — do predictions/conclusions survive observation of real systems?; and
4. **decision usefulness** — does using the formal result improve a concrete engineering outcome?

The papers primarily address the first. The others require evidence outside mathematical derivation alone.

## Canonicality boundary

Canonicalization is useful when multiple encodings should denote the same structural object. But a canonical representation requires a declared equivalence relation and information-preservation boundary.

Accordingly:

```text
Same canonical object
    means
Equivalent under the declared structural semantics

It does not automatically mean
Equivalent for every possible software property
```

If two systems collapse to the same canonical representation while differing on a property important to the intended analysis, the representation is insufficient for that use even if the canonicalization theorem is correct.

## Dependency boundary

Workload-relative dependency should be interpreted at the level established by Paper 1's formal model.

A dependency result does not automatically imply:

- causal necessity in every execution environment;
- operational criticality;
- performance sensitivity;
- security significance;
- organizational ownership;
- economic importance;
- inability to substitute another component; or
- universal dependency across all workloads.

Those require additional definitions or empirical evidence.

## Research authority and artifact terms

The repository uses separate artifact roles. The JSON records currently under `paper-*/research-objects/` are **seed records**, not automatically authoritative research objects.

- **Authoritative research object:** an accepted, versioned object that fixes research meaning within a declared scope, including its schema, invariants, and evidence contract.
- **Human-authored manuscript source:** paper-local `main.tex`, bibliography, prose, figures, and appendices used to express the paper's argument and presentation.
- **Generated candidate artifact:** rebuildable output such as `main.pdf`, HTML preview, graph export, or validation report. It has no publication authority by itself.
- **Immutable release artifact:** reviewed committed publication bytes associated with an identified source state.

“Authoritative” here is repository governance over the intended meaning of an artifact. It is not authority over external reality and does not make a proposition true.

For the same declared research meaning, repository precedence may order accepted research objects, manuscript source, and release artifacts. That precedence resolves internal artifact disagreement; it does not replace scientific review or mathematical verification.

Implementations are conformance hypotheses against research objects, not the source of mathematical or scientific truth.

Current governance/review documentation includes:

- [Minimal Promotion Contract](docs/minimal-promotion-contract.md)
- [Consumer Promotion Records](promotion-records/README.md)
- [Research-object lifecycle and authority](docs/research-object-lifecycle.md)

Promotion is bounded repository governance. A promotion decision may authorize a downstream repository to treat an artifact as admitted under its own contract; it cannot strengthen the theorem, empirical evidence, or external validity contained in that artifact.

## Seed and specification boundary

Current seed/specification materials include:

- [Dependency Predicate seed](paper-1-dependency/research-objects/definition.dependency.dependency-predicate.json)
- [Reachability Profile seed](paper-3-foundations-structural-analysis/research-objects/concept.structural-observation.reachability-profile.json)
- [Canonical Reachability Profile specification](docs/research-objects/canonical-reachability-profile.md)

A seed becoming canonical means its repository lifecycle requirements were satisfied. It does not mean the represented concept has been established as a universal property of software systems.

Additional research objects should define their scientific purpose, inputs, outputs, invariants, preconditions, postconditions, evidence contract, reproducibility requirements, schema, and deterministic fixtures before implementation-specific adapters are treated as reference behavior.

## From real system to formal object

The current architecture can be summarized as:

```text
Real system
    ↓ observation / abstraction
Structural representation
    ↓ canonicalization under declared semantics
Canonical structural object
    ↓ formal definition
Research object / proposition
    ↓
Specific analysis
```

The most consequential boundary is the first arrow. Mathematics can reason precisely over the structural object once supplied; it cannot prove that the abstraction retained every real-system property relevant to the intended use.

That correspondence must be investigated empirically.

## Relationship to ABR

Architectural Boundary Research can provide bounded empirical evidence about recurring structures in observed software systems. Structural Analysis Foundations can formalize precisely stated propositions once their premises and scope are independently justified.

```text
Empirical recurrence ≠ theorem
Theorem ≠ empirical recurrence
```

ABR evidence may motivate or constrain formalization, but empirical recurrence alone does not establish mathematical necessity. Conversely, a theorem about a model does not establish that real systems satisfy its premises.

## Relationship to Structology

Structology is a provisional candidate structural vocabulary. Structural Analysis Foundations may formalize concepts compatible with it, but the validity of a proof cannot validate Structology's broader transfer/generalization claims.

Formal work should remain interpretable from its explicit definitions even if Structology is later revised or rejected.

## Relationship to SYNAPSE

SYNAPSE may implement deterministic analyses corresponding to formal definitions from this repository.

```text
Formal specification
        ↓ implementation
SYNAPSE analysis
        ↓ conformance evidence
Deterministic result
```

Passing implementation tests can establish conformance to an encoded specification. It cannot establish that the specification is mathematically correct or externally adequate unless those questions are tested separately.

## Relationship to ContinuityOS

Formal structural results may become inputs to a legitimacy system, but structural truth does not create authority.

```text
Structural proposition ≠ permission
Formal validity ≠ execution eligibility
```

Any downstream mapping from a formal result to execution policy belongs to the consuming legitimacy/governance system and requires independent authority.

## Validation program

The next high-value work is not simply adding more formal objects. The program should test both mathematical robustness and external correspondence.

Priority work includes:

1. **Independent proof review** — have qualified reviewers attempt to verify, find counterexamples to, or weaken the principal propositions without relying on repository tests.
2. **Assumption audit** — enumerate which conclusions fail when each assumption is removed or weakened.
3. **Representation challenge** — construct non-isomorphic or behaviorally distinct systems that map to the same canonical object and determine which distinctions are intentionally discarded versus consequentially lost.
4. **Alternative-formalism comparison** — compare the proposed definitions against established graph, dependency, program-analysis, architecture, and category-theoretic formulations where applicable.
5. **Empirical correspondence** — use ABR or another empirical environment to test whether the formal structural predicates correspond to observed system behavior.
6. **Implementation conformance** — verify that SYNAPSE or other implementations reproduce the formal semantics without treating implementation agreement as proof.

## Falsification and revision boundary

Formal results should be revised if a proof is invalid, a counterexample violates a stated theorem, or hidden assumptions are discovered.

The broader research program should be narrowed if:

- the proposed canonical representation loses information required for its intended analyses;
- dependency definitions fail to capture consequential forms of dependency in target domains;
- the Paper 3 interface excludes important structural analyses without principled reason;
- existing mathematical frameworks express the same results more simply or generally;
- external-system correspondence is weak; or
- formal machinery adds no consequential engineering value beyond simpler representations.

A mathematically valid but externally unhelpful framework is still a legitimate mathematical result; it should simply carry a narrower claim.

## Repository status

Immutable PDF release artifacts are present at:

- [paper-1-dependency/pdf/paper1.pdf](paper-1-dependency/pdf/paper1.pdf)
- [paper-2-canonical-structural-analysis/pdf/paper2.pdf](paper-2-canonical-structural-analysis/pdf/paper2.pdf)
- [paper-3-foundations-structural-analysis/pdf/paper3.pdf](paper-3-foundations-structural-analysis/pdf/paper3.pdf)

Paper-local `main.tex` and `references.bib` sources are present for each paper.

## Continuous LaTeX validation

GitHub Actions builds each paper independently with `latexmk -pdf main.tex`. Generated PDFs are candidate build artifacts; committed PDFs under `paper-*/pdf/` remain immutable release artifacts under the repository's release process.

To reproduce the build locally:

```sh
cd paper-1-dependency && latexmk -pdf main.tex
cd ../paper-2-canonical-structural-analysis && latexmk -pdf main.tex
cd ../paper-3-foundations-structural-analysis && latexmk -pdf main.tex
```

A successful LaTeX build establishes source/build consistency, not theorem correctness.

Canonical fixtures can be checked against their declared schemas with:

```sh
python tools/validate_canonical_fixtures.py
```

Schema validity establishes conformance to the schema, not validity of the represented scientific claim.

## Repository organization

- `paper-1-dependency/` — Paper 1: The Mathematics of Dependency
- `paper-2-canonical-structural-analysis/` — Paper 2: Canonical Structural Analysis
- `paper-3-foundations-structural-analysis/` — Paper 3: Foundations for Structural Analysis
- `figures/` — shared figure organization
- `docs/` — research-object lifecycle, promotion, and specification documentation
- `promotion-records/` — consumer-side evidence admission/promotion records

## Current conclusion

Structural Analysis Foundations contains a coherent formal research program spanning workload-relative dependency, canonical structural representations, and candidate foundations for structural-analysis operators.

Its strongest legitimate claims are conditional mathematical claims inside explicit definitions and assumptions. The next claims to earn are independent mathematical verification and demonstrated correspondence between those formal objects and consequential properties of real software systems.
