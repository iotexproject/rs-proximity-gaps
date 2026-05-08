# Paper 1 Lean 4 formalization — status board

This is the per-theorem formalization status of Paper 1
("FRI Soundness Above the Johnson Bound via Threshold Halving",
ePrint [2026/861](https://eprint.iacr.org/2026/861)).

**Build status (latest CI run):** see badge in repo root README.
The Lean library currently uses `lean-toolchain = leanprover/lean4:v4.13.0` and Mathlib pinned in `lake-manifest.json`.

## Overview

| Metric | Value |
|--------|------:|
| `sorry` count (excluding docstring mentions) | **0** |
| `axiom` count | **1** |
| Top-level theorems / lemmas | **23** |
| Paper theorems with a Lean counterpart | **7 / ~22 soundness-relevant** |

The single axiom is `Coupling.bciks_proximity_gap`, the **external BCIKS** proximity gap result (Theorem 1.6 of BCIKS '20). It is a published, peer-reviewed result; we treat it as a black-box dependency.

## Status legend

| Symbol | Meaning |
|--------|---------|
| ✅ ZERO-SORRY | Top-level statement matches paper, no `sorry`, no new axioms |
| 🟦 AXIOMATIZED | Stated, depends on a clearly named external axiom (currently only `bciks_proximity_gap`) |
| 🟨 COUNTING-FORM | Combinatorial / rational ratio bound proved, but not yet bridged to the paper's probability statement |
| 🟧 WIP | Building blocks present, top-level statement not yet packaged |
| ⬜ NOT STARTED | No Lean statement |
| 📜 PAPER-CONJECTURE | Paper labels this a conjecture; Lean is N/A by design |

## Per-theorem status

### Section 3 — Half-Threshold CA

| Paper label | Statement | Lean identifier | File | Status |
|-------------|-----------|-----------------|------|--------|
| `thm:ca-halved` | `Pr_γ[ wt(f₁ + γ f₂ from C) ≤ δ/2 ] ≤ 2/|F|` (RVW13 form) | `FRISoundness.ca_halved` | `CA.lean` | ✅ |

### Section 4 — Equal-Threshold CA

| Paper label | Statement | Lean identifier | File | Status |
|-------------|-----------|-----------------|------|--------|
| `thm:eq-threshold-upper` | `\| { γ : f₁+γf₂ within w of C } \| ≤ \binom{n}{w}` | `FRISoundness.ca_equal_threshold` | `EqualThresholdCA.lean` | ✅ |
| `prop:eq-threshold-tight` | matching lower bound construction | — | — | ⬜ |
| `cor:eq-threshold-equality` | asymptotic equality | — | — | ⬜ |

### Section 5 — FRI Soundness Above Johnson

| Paper label | Statement | Lean identifier | File | Status |
|-------------|-----------|-----------------|------|--------|
| `lem:fri-coupling` | even/odd RS isomorphism with γ-twist | `FRISoundness.coupling_pointwise`, `coupling_counting` | `RSCode.lean` | ✅ |
| `thm:proximity-gap` | round-1 ≤ 1 bad α (above Johnson) | `FRISoundness.proximity_gap`, `bad_alpha_count` | `Coupling.lean` | 🟦 (depends on `bciks_proximity_gap` for rounds ≥ 2) |
| `lem:catch-prob` | catch probability under i.i.d. base sampling | — | — | ⬜ |
| `thm:fri-full` | `Pr[FRI accepts] ≤ nR/\|F\| + (1−δ/2)^q` | `FRISoundness.fri_soundness_above_johnson_counting`, `fri_soundness_above_johnson_probability` | `Probability.lean` | 🟨 (rational counting form proved; transcript-event instantiation deliberately left abstract — noted in file docstring) |

### Section 6 — List-size moment results

These are second-moment results on the random list size `M_γ`. They are not on the FRI soundness critical path; not yet formalized.

| Paper label | Title | Status |
|-------------|-------|--------|
| `lem:locator-normal`, `lem:pairwise-indep`, `thm:second-moment` | Pairwise indep & second moment, c=2 | ⬜ |
| `lem:locator-normal-c`, `thm:pairwise-c`, `cor:moments-c`, `cor:expected-Mtrue` | Generalized to c≥2 | ⬜ |
| `prop:m2-obstruction`, `prop:qrank`, `lem:mobius`, `thm:mtrue-2c`, `thm:birthday-expected` | Worst-case bound, sub-Poisson tail | ⬜ |
| `conj:openset-rank` | Open-Set Rank Lemma at c≥3 | 📜 (paper conjecture) |

### Section 7 — STIR / WHIR

| Paper label | Statement | Lean identifier | File | Status |
|-------------|-----------|-----------------|------|--------|
| `thm:batch-ca` | Half-Threshold Batch CA | `FRISoundness.batch_ca_aggregate` | `BatchCA.lean` | ✅ |
| `thm:stir-full` | STIR soundness above Johnson | (`batch_ca_aggregate` is the building block; STIR-specific lemmas 4.4 / 4.5 + transcript packaging not yet ported) | `BatchCA.lean` | 🟧 |
| `cor:whir` | Linear-subcode CA (Cor.) | (depends on a folding-aware variant of `batch_ca_aggregate`) | — | ⬜ |
| `lem:whir-iter` | Per-iteration commit-phase error | — | — | ⬜ |
| `thm:whir-full` | WHIR soundness above Johnson | — | — | 📜 (paper conjecture; iteration-level induction not re-derived) |
| `lem:whir-mca-orthogonality` | OOD/shift MCA-orthogonality | — | — | ⬜ |

### Section 8 — Char-2 / Circle FRI

| Paper label | Statement | Lean identifier | File | Status |
|-------------|-----------|-----------------|------|--------|
| `lem:additive-iso` | Additive even/odd iso | `FRISoundness.gen_recover_fst`, `gen_recover_snd` | `Char2.lean` | ✅ |
| `lem:additive-coupling` | Additive FRI coupling | `FRISoundness.gen_coupling_pointwise`, `gen_coupling_counting` | `Char2.lean` | ✅ |
| `thm:proximity-gap-char2` | Char-2 round-1 proximity gap | (gen_coupling_* + ca_halved chain assembled in paper; not packaged as one Lean theorem yet) | — | 🟧 |
| `thm:fri-char2` | Full Char-2 FRI soundness | — | — | ⬜ |
| `lem:circle-iso`, `lem:circle-coupling`, `thm:circle-pg`, `thm:fri-circle` | Circle FRI chain | — | — | ⬜ |

### Section 9 — Round-by-round / Non-interactive variants

| Paper label | Title | Status |
|-------------|-------|--------|
| `thm:fri-rbr` | RBR Soundness of Half-Threshold FRI | ⬜ |
| `thm:fri-ni` | Non-Interactive FRI Soundness | ⬜ (depends on Fiat-Shamir) |
| `thm:deep-fri` | DEEP-FRI Knowledge Soundness | ⬜ |
| `cor:pcs-ni` | Non-Interactive PCS Soundness | ⬜ |

## What "ZERO-SORRY" means precisely

For each ✅ entry: every proof in the corresponding Lean file closes via standard Mathlib lemmas, with **no `sorry` tactic and no `admit`**. Outside Mathlib's standard axioms (classical logic, choice, propext), the only project-level axiom referenced anywhere in the library is `bciks_proximity_gap`, and we mark every transitive consumer with the 🟦 label.

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
interactive (or Fiat-Shamir transformed) FRI run. We chose to keep this
abstract because the protocol-event encoding is the standard part — the
proximity-gap content is the contribution.

## Roadmap

In priority order for further Lean work (matches the order the user has
chosen for the next session):

1. **`thm:fri-full` — close the protocol-event gap**: instantiate
   `UniformTranscriptModel.event` with the FRI verifier acceptance
   predicate and propagate the rational bound. This converts 🟨 → ✅.
2. **`thm:eq-threshold-upper` lower-bound matching** (`prop:eq-threshold-tight`):
   the construction is explicit in the paper; re-encoding it in Lean
   gives a tightness statement.
3. **`thm:proximity-gap-char2` packaging**: `gen_coupling_*` is already
   formalized; package `gen_coupling_counting + ca_halved` as one
   theorem matching the paper's labelled statement.
4. **`thm:stir-full`**: port STIR Lemmas 4.4 / 4.5 and combine with
   `batch_ca_aggregate`.
5. **Circle FRI chain**: `lem:circle-iso → lem:circle-coupling →
   thm:circle-pg → thm:fri-circle`. The skeleton mirrors the
   multiplicative case; new piece is the `i^2 + j^2 = 1` circle
   parametrization in Mathlib.
6. **RBR / non-interactive / DEEP-FRI**: depends on a Fiat-Shamir
   formalization layer in Mathlib (currently absent).

## Notes for reviewers

- The single non-Mathlib axiom in the library is `bciks_proximity_gap`,
  located at `Coupling.lean:95`. It directly transcribes BCIKS '20
  Theorem 1.6 (zero-loss proximity gap below the Johnson bound) and is
  the **only** place where an external proven result is taken on faith.
- The paper's Theorem 1 (`thm:ca-halved`) is RVW13's classical 1:2
  inequality; we acknowledge this in §3. The Lean formalization gives
  a self-contained, machine-checkable proof within Mathlib (no external
  axiom).
- Theorem `thm:eq-threshold-upper` (the `\binom{n}{w}/|F|` upper bound)
  is, to our knowledge, **new in this paper**. Its Lean formalization
  closes via an injection into `Finset.powersetCard`.
- `thm:whir-full` is **stated as a conjecture in the paper** (the
  iteration-level induction with our substituted folding term is left
  for follow-up work). The MCA-orthogonality content needed for the
  proximity-layer term-substitution is rigorously stated as
  `lem:whir-mca-orthogonality` in the paper; a Lean version is on the
  TODO list above.
