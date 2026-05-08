# Paper 1 Lean 4 formalization — status board

This is the per-theorem formalization status of Paper 1
("FRI Soundness Above the Johnson Bound via Threshold Halving",
ePrint [2026/861](https://eprint.iacr.org/2026/861)).

**Build status (latest CI run):** see badge in repo root README.
The Lean library currently uses `lean-toolchain = leanprover/lean4:v4.30.0-rc2`
and Mathlib pinned in `lake-manifest.json`.

## Overview

| Metric | Value |
|--------|------:|
| `sorry` count (excluding docstring word-mentions) | **0** |
| `axiom` count | **1** (`bciks_proximity_gap`, stand-in for BCIKS Thm 1.2) |
| Top-level public theorems / lemmas across the 8 files | ~30 |
| Paper labels with a Lean counterpart at the **statement-faithful** level | **3 / ~22 soundness-relevant** |
| Paper labels with at least a **building block** in Lean | **~12 / ~22** |

The single project axiom is `Coupling.bciks_proximity_gap`, modelled on the
external BCIKS '20 result (Theorem 1.2). Its current signature uses a
placeholder fold (`linComb f f α`) and is not yet a faithful transcription;
it is treated as a black box by every consumer. A faithful transcription
is on the roadmap.

## Status legend

| Symbol | Meaning |
|--------|---------|
| ✅ STATEMENT-FAITHFUL | Lean theorem statement matches the paper label, no `sorry`, no new axioms beyond Mathlib |
| 🟦 AXIOMATIZED | Stated; depends on `bciks_proximity_gap` (the only project axiom) |
| 🟨 COUNTING-FORM | Combinatorial / rational ratio bound proved, but not yet bridged to the paper's probability statement |
| 🟧 HELPER-ONLY | Building block(s) present in Lean but the paper-labelled statement is not yet packaged at the code-level distance / FRI-domain instance |
| ⬜ NOT STARTED | No Lean statement |
| 📜 PAPER-CONJECTURE | Paper labels this a conjecture; Lean formalization is N/A by design |

## Per-theorem status

### Section 3 — Half-Threshold CA

| Paper label | Statement | Lean identifier | File | Status |
|-------------|-----------|-----------------|------|--------|
| `thm:ca-halved` | At most one bad γ ⟹ `Pr_γ[Δ(f₁ + γ f₂, C) ≤ d] ≤ 1/|F|` (the paper states the looser `≤ 2/|F|` form; Lean proves the tighter contrapositive) | `FRISoundness.ca_halved` | `CA.lean` | ✅ |

### Section 4 — Equal-Threshold CA

| Paper label | Statement | Lean identifier | File | Status |
|-------------|-----------|-----------------|------|--------|
| `thm:eq-threshold-upper` | `\| { γ : f₁+γf₂ within w of C } \| ≤ \binom{n}{w}` | `FRISoundness.ca_equal_threshold` | `EqualThresholdCA.lean` | ✅ |
| `prop:eq-threshold-tight` | matching lower bound construction | — | — | ⬜ |
| `cor:eq-threshold-equality` | asymptotic equality | — | — | ⬜ |

### Section 5 — FRI Soundness Above Johnson

| Paper label | Statement | Lean identifier | File | Status |
|-------------|-----------|-----------------|------|--------|
| `lem:fri-coupling` | even/odd RS isomorphism with γ-twist on the multiplicative FRI domain | building blocks: `coupling_pointwise`, `coupling_counting` (RSCode.lean); the RS isomorphism is parametrized by `RSIsomorphismWitness` and is not yet instantiated for a concrete FRI domain | `RSCode.lean` | 🟧 |
| `thm:proximity-gap` | round-1 ≤ 1 bad α (above Johnson) | `FRISoundness.proximity_gap` is a renaming of `ca_halved` over an arbitrary linear submodule; the bridge from "f δ-far from RS_k" to "joint distance > 2d for (fE, fO)" uses `coupling_counting` + an instantiated `RSIsomorphismWitness`, which is not yet packaged as one theorem matching the paper label | `Coupling.lean` | 🟧 |
| `lem:catch-prob` | catch probability under i.i.d. base sampling | — | — | ⬜ |
| `thm:fri-full` | `Pr[FRI accepts] ≤ nR/\|F\| + (1−δ/2)^q` | `FRISoundness.fri_soundness_above_johnson_counting`, `fri_soundness_above_johnson_probability` | `Probability.lean` | 🟨 |

### Section 6 — List-size moment results

These are second-moment results on the random list size `M_γ`. They are not on the FRI-soundness critical path; not yet formalized.

| Paper label | Title | Status |
|-------------|-------|--------|
| `lem:locator-normal`, `lem:pairwise-indep`, `thm:second-moment` | Pairwise indep & second moment, c=2 | ⬜ |
| `lem:locator-normal-c`, `thm:pairwise-c`, `cor:moments-c`, `cor:expected-Mtrue` | Generalized to c≥2 | ⬜ |
| `prop:m2-obstruction`, `prop:qrank`, `lem:mobius`, `thm:mtrue-2c`, `thm:birthday-expected` | Worst-case bound, sub-Poisson tail | ⬜ |
| `conj:openset-rank` | Open-Set Rank Lemma at c≥3 | 📜 |

### Section 7 — STIR / WHIR

| Paper label | Statement | Lean identifier | File | Status |
|-------------|-----------|-----------------|------|--------|
| `thm:batch-ca` | Half-Threshold Batch CA (∑ αᵢ fᵢ form) | `FRISoundness.batch_ca_aggregate` proves only the per-coordinate union of bad scalars under fixed `rest i` (each `Bᵢ` is a singleton, total ≤ \|ι\|); the tuple-count / `m/\|F\|` probability statement of the paper is a corollary not yet packaged | `BatchCA.lean` | 🟧 |
| `thm:stir-full` | STIR soundness above Johnson | (`batch_ca_aggregate` is one building block; STIR-specific lemmas 4.4 / 4.5 + transcript packaging not ported) | — | 🟧 |
| `cor:whir` | Linear-subcode CA (Cor.) | (depends on a folding-aware variant of `batch_ca_aggregate`) | — | ⬜ |
| `lem:whir-iter` | Per-iteration commit-phase error | — | — | ⬜ |
| `thm:whir-full` | WHIR soundness above Johnson | — | — | 📜 |
| `lem:whir-mca-orthogonality` | OOD/shift MCA-orthogonality | — | — | ⬜ |

### Section 8 — Char-2 / Circle FRI

| Paper label | Statement | Lean identifier | File | Status |
|-------------|-----------|-----------------|------|--------|
| `lem:additive-iso` | Additive even/odd RS-code isomorphism | building blocks: `gen_recover_fst`, `gen_recover_snd` (recovery identities only; the additive RS-code-level isomorphism is not yet stated against an instantiated additive `GenFRIPairing`) | `Char2.lean` | 🟧 |
| `lem:additive-coupling` | Additive FRI code-distance coupling | building blocks: `gen_coupling_pointwise`, `gen_coupling_counting` (generic counting lemmas; the code-distance bridge for the additive RS-code is not yet packaged) | `Char2.lean` | 🟧 |
| `thm:proximity-gap-char2` | Char-2 round-1 proximity gap | `FRISoundness.proximity_gap_char2` is a renaming of `ca_halved` over an arbitrary `GenFRIPairing`; no concrete additive instance and no code-distance hypothesis are present yet | `Char2.lean` | 🟧 |
| `thm:fri-char2` | Full Char-2 FRI soundness | — | — | ⬜ |
| `lem:circle-iso` | Circle even/odd iso | building block: `GenFRIPairing` abstraction; explicit circle pairing not yet constructed | `Char2.lean` | 🟧 |
| `lem:circle-coupling` | Circle FRI coupling | building blocks: `gen_coupling_*`; circle instance not yet constructed | `Char2.lean` | 🟧 |
| `thm:circle-pg` | Circle round-1 proximity gap | building block: `proximity_gap_char2`; circle instance not yet constructed | `Char2.lean` | 🟧 |
| `thm:fri-circle` | Full circle FRI soundness | — | — | ⬜ |

### Section 9 — Round-by-round / Non-interactive variants

| Paper label | Title | Status |
|-------------|-------|--------|
| `thm:fri-rbr` | RBR Soundness of Half-Threshold FRI | ⬜ |
| `thm:fri-ni` | Non-Interactive FRI Soundness | ⬜ (depends on Fiat-Shamir) |
| `thm:deep-fri` | DEEP-FRI Knowledge Soundness | ⬜ |
| `cor:pcs-ni` | Non-Interactive PCS Soundness | ⬜ |

## What "✅ STATEMENT-FAITHFUL" means precisely

For each ✅ entry: the Lean theorem's statement matches the paper label
(modulo a tighter constant where noted, e.g.\ `thm:ca-halved`), every proof
in the corresponding file closes via standard Mathlib lemmas, with **no
`sorry` tactic and no `admit`**. Outside Mathlib's standard axioms
(classical logic, choice, propext), the only project-level axiom referenced
anywhere in the library is `bciks_proximity_gap`.

## What "🟧 HELPER-ONLY" means precisely

The Lean file contains the necessary lower-level building blocks (counting
lemmas, recovery identities, abstract pairings) but the paper-labelled
theorem at the level of the concrete FRI domain and code-distance hypothesis
is not yet packaged. The chain of building blocks is sound and the
remaining packaging is a routine exercise; we mark these honestly so a
reviewer can match the Lean library against the paper without surprise.

## What "🟨 COUNTING-FORM" means for `thm:fri-full`

`fri_soundness_above_johnson_probability` proves the rational inequality

```
badChallenges/|F|  +  (missing^q)/(n^q)
  ≤ (n·R)/|F|     +  ((n−d)^q)/(n^q)
```

over uniformly sampled finite transcript spaces. The paper's
`(1 − δ/2)^q` form is recovered by setting `d = ⌈δn/2⌉` so that
`(n−d)/n ≤ 1 − δ/2`. The remaining gap to a paper-form theorem is the
**event instantiation**: tying the abstract `event : Ω → Prop` of
`UniformTranscriptModel` to the concrete acceptance predicate of an
interactive (or Fiat-Shamir-transformed) FRI run.

The commit-phase `nR` term is a per-round union bound (round 1 contributes
≤ 1 bad scalar via `ca_halved`; rounds 2..R contribute ≤ n each via
`bciks_proximity_gap`), not a tuple count over `F^R` — `Σ_i bad_i/|F| ≤ nR/|F|`.
The query-phase `(1-δ/2)^q` term is the standard q-fold miss probability.

## Roadmap

In priority order for further Lean work:

1. **`thm:fri-full` — close the protocol-event gap**: instantiate
   `UniformTranscriptModel.event` with the FRI verifier acceptance
   predicate and propagate the rational bound. Converts 🟨 → ✅.
2. **`thm:proximity-gap` packaging**: instantiate `RSIsomorphismWitness`
   for a concrete multiplicative-coset FRI domain and combine
   `coupling_counting` + `ca_halved` into a single theorem against the
   code-distance hypothesis. Converts 🟧 → ✅ (or 🟦 once it composes
   with `bciks_proximity_gap` for rounds ≥ 2).
3. **`thm:proximity-gap-char2` packaging**: construct an explicit additive
   `GenFRIPairing` instance for `s(x) = x² + βx` over an `F₂`-linear
   subspace and package the code-level char-2 proximity gap. Converts
   `lem:additive-iso`, `lem:additive-coupling`, `thm:proximity-gap-char2`
   from 🟧 → ✅.
4. **`thm:eq-threshold-upper` lower-bound matching** (`prop:eq-threshold-tight`):
   the construction is explicit in the paper.
5. **`thm:batch-ca`**: strengthen `batch_ca_aggregate` from per-coordinate
   union to tuple-count / probability `m/|F|` form.
6. **`thm:stir-full`**: port STIR Lemmas 4.4 / 4.5 and combine with the
   strengthened batch CA.
7. **Circle FRI chain**: `lem:circle-iso → lem:circle-coupling →
   thm:circle-pg → thm:fri-circle`. Construct the circle `GenFRIPairing`
   instance with `(x,y) ↦ (x,-y)` and parametrize the coupling.
8. **RBR / non-interactive / DEEP-FRI**: depends on a Fiat-Shamir
   formalization layer in Mathlib (currently absent).

## Notes for reviewers

- The single non-Mathlib axiom in the library is `bciks_proximity_gap`,
  located at `Coupling.lean`. It is a stand-in for BCIKS '20 Theorem 1.2
  (zero-loss proximity gap below the Johnson bound); its current signature
  uses a placeholder fold and is not a faithful transcription of the
  external statement. A faithful transcription is on the roadmap.
- The paper's Theorem 1 (`thm:ca-halved`) is RVW13's classical 1:2
  inequality; we acknowledge this in §3. The Lean formalization gives a
  self-contained, machine-checkable proof within Mathlib (no external
  axiom). Lean proves the tighter "at most one bad γ" form, which implies
  the paper's `≤ 2/|F|` bound.
- Theorem `thm:eq-threshold-upper` (the `\binom{n}{w}/|F|` upper bound)
  is, to our knowledge, **new in this paper**. Its Lean formalization
  closes via an injection into `Finset.powersetCard`.
- `thm:whir-full` is **stated as a conjecture in the paper** (the
  iteration-level induction with the substituted folding term is left
  for follow-up work). The MCA-orthogonality content for the
  proximity-layer term-substitution is rigorously stated as
  `lem:whir-mca-orthogonality` in the paper; a Lean version is on the
  roadmap.
