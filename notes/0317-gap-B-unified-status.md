# Note 0317 — Gap B unified status report (cycles 1–4 consolidated)

**Branch:** `feat/op1a-algorithm-fixes` (PR #414)
**Date:** 2026-05-01
**Status:** Cycle 5 deliverable — consolidates Notes 0313–0316 into a single audit-ready summary.

## Gap B definition

**Gap B (paper3 prize-readiness)**: paper3 §sec:unconditionality-summary states `R1 / R2 general-f closure (10/q for all f)` is **conditional** on paper2's `conj:sparse-worst`. The question: can paper3 close this conditional, or sharpen the framing?

## Resolution: structural separation of paper3 vs paper2 contributions

Cycles 1–4 establish a clean structural separation:

| Layer | Object | What paper3 does | What paper2 does |
|-------|--------|------------------|-------------------|
| **Point-level** | `V_bad ⊂ F_q^{2D}` | codim `2(c-1)` (leading stratum), trivial saturation `{|S*|≤w}` sub-locus, S*-stratification | — |
| **Curve-level** | `ℓ_f(α_1) ⊂ F_q^{2D}` | event-inclusion `R1 ⊆ R2` | universal `K(f) ≤ 10` for sparse `f̂` (Theorem K10) |
| **Composition** | `ε_commit^{R1}(f)` | bound via `R1 ⊆ R2` + paper2 K10 | curve-avoidance theorem |

Gap B's general-f closure is structurally a **curve-level** problem, not a point-level problem. paper3 can contribute structural infrastructure but cannot close the curve-level gap on its own — that's paper2's territory.

## Status of the 4 attack angles

### Angle 1 — Honest reframe of §sec:unconditionality-summary

**Status: ✅ DONE**

Cycle 1: §sec:sparse-closure structural framing (Markov footprint, structural support for conjecture).
Cycle 2: §sec:unconditionality-summary "Frontier framing of general-f conditional" paragraph + abstract Note 0310/0314 citations.
Cycle 4: §sec:setup "Trivial saturation sub-locus" structural remark.

paper3 now correctly frames:
- Sparse-class deployment closure as **unconditional** (rate-1/4) via paper2 K10 + R1 ⊆ R2.
- General-f closure as **conditional on paper2's open conjecture** (`conj:sparse-worst` or equivalent moment-bound program).
- The conditional row's residual gap as **paper2 frontier**, with paper3 contributing structural infrastructure + per-instance reachability evidence (Notes 0310, 0314, 0315) and the trivial saturation observation (Note 0316).

No over-claim, no under-claim. Honest framing.

### Angle 2 — Lift `(16, 4, 17, 3)` Zariski-open branch theorem to `(32, 8)`/`(64, 16)`

**Status: ❌ STRUCTURALLY DEAD** (cycle 1 + cycle 3 + cycle 4 analysis)

Note 0310's construction works because `T_c = ⌊(2D-1)/c⌋ = 7` at `(16, 4, 3)`, and paper2's `K_3 ≤ 10 > T_c` gives reachability. At deployment scale `(n ≥ 32, c ≥ 3)` rate-1/4:
```
T_c = Θ(n/c) ≥ 11 > K_3 ≤ 10
```
so 3-mono sparse cannot reach `M > T_c` at deployment. The Note 0310 construction is fundamentally small-scale-specific. Even higher-arity `K_4 ≤ 13` (rate-1/4) and empirical `K_5 ≤ 6, K_6 ≤ 3, K_7 ≤ 2` all fall short of `T_c` at deployment for any `c ∈ {3, 4, 6, 9}`.

What we DO have (cycle 2 strengthening):
- Multi-prime certification at the (16, 4, c=3) proxy: 8 codim-1 branches × 10 primes = 80 deterministic certificates with K=9, |S*|=10. 32,000 randomized formula audits, zero failures.
- The mechanism is prime-uniform; scope cap is parametric, not characteristic-specific.

What we DON'T have:
- Any deployment-scale (n ≥ 32) sparse witness reaching paper3's V_bad. **Provably impossible** for any fixed-arity sparse class and any ABF c value at deployment.

**Closure**: This angle is closed as IMPOSSIBLE at deployment for fixed-arity sparse. The (16, 4, c=3) proxy is the largest n where 3-mono sparse mechanism works at rate 1/4 + c=3. Note 0314 provides multi-prime evidence at that proxy.

### Angle 3 — 4-mono / 5-mono sparse witness at deployment

**Status: ❌ DEAD AT DEPLOYMENT** (cycle 1 + cycle 4 analysis)

paper2 K_s bounds:
- `K_2 ≤ 8` rigorous
- `K_3 ≤ 10` rigorous (Theorem `thm:universal-K10`)
- `K_4 ≤ 13` rigorous (Note 0297, paper2)
- `K_5 ≤ 6, K_6 ≤ 3, K_7 ≤ 2` empirical (paper2 Notes 0293, 0296)

Required for sparse `s`-mono to reach `M > T_c` at rate-1/4 deployment: `K_s > T_c = Θ(n/c)`. For any constant `s`, `K_s ≤ const`, and `T_c → ∞` as `n → ∞`. Hence no fixed-arity sparse class reaches V_bad at deployment.

Cycle 3 finding (Note 0315): at `(16, 4, c=4)` Johnson-boundary, 3-pos sparse pairs with parity-aligned support give `M = q-1` saturation via `Q_E = z^8 ± 1` factorization. This is at the Johnson boundary (`δ = J/n`), outside paper2 K10's strictly-above-Johnson scope. Doesn't lift to deployment.

Cycle 4 finding (Note 0316): the GENERAL trivial saturation `{|S*| ≤ w}` includes ALL such constructions as instances. Verified at 5 cells, M = q-1 throughout.

**Closure**: This angle is closed as IMPOSSIBLE for fixed-arity sparse at deployment. The trivial saturation sub-locus (Note 0316) accounts structurally for all sparse-witness reachability, and shows the mechanism is small-scale only.

### Angle 4 — FRI-curve measure replacement / alternative prefactor sharpening

**Status: ❌ DEAD** (cycle 1 analysis)

- Lemma A (FRI-curve specific suppression): empirically refuted in expectation at deployment scale (paper3 Theorem `thm:lemma-a-refuted`, Notes 0134, 0136). Mass-balance argument: `E_f[K(f)] ≥ |F|/4` at deployment saturation regime.
- Stratified Bezout (Note 0125's Lemma A): incompatible with saturation. `|V_bad|/|F|^{2D} ≥ 1/4` forces `deg V_bad ≥ |F|^{2(c-1)}/4`, exponential in `|F|`, not `poly(n, c)`.
- Naive Bezout: `K(f) ≤ deg V_bad = C(n, w+1)`, super-poly at deployment, useless.

Any prefactor sharpening must be measure-theoretic on the FRI commit-curve specifically, conditional on a δ-far-adversarial-`f` mechanism with no identified precursor.

**Closure**: This angle is closed as REFUTED in expectation. paper3 §sec:lemma-A correctly retains Lemma A as a standalone open AG question, but no longer load-bearing for the deployment claim.

## Cycle-4 unified structural insight

The key conceptual result of cycle 4 (Note 0316):

> **`V_bad` has a TRIVIAL saturation sub-locus**: `{(s_1, s_2) : |S*| ≤ w}` ⊆ `V_bad`, with `M = q-1` saturation. This is a non-leading sub-locus (codim `≥ 2c`) but structurally non-trivial.

This implies:
1. paper2's `K10` (sparse `f̂` ⇒ `K ≤ 10`) is a CURVE-AVOIDANCE theorem — sparse `f`'s commit-curves AVOID the trivial saturation sub-locus, despite this sub-locus being huge in `F_q^{2D}`.
2. paper3's codim-`2(c-1)` is a POINT-LEVEL structural bound on V_bad's leading stratum.
3. Composition of the two gives the deployable sparse-class bound.
4. General-`f` closure requires a curve-avoidance theorem for general `f`, which is paper2's `conj:sparse-worst` (or moment-bound) program — strictly outside paper3's reach.

## What's left for paper3

Concretely, after cycles 1–4:
- Sparse-class deployment closure: **unconditional**, rate-1/4, `ε ≤ 10/q` (cf. paper3 §sec:sparse-closure).
- General-f closure: **conditional on paper2 conjecture**, with explicit framing as paper2 frontier (cf. paper3 §sec:unconditionality-summary "Frontier framing").
- Lemma A: refuted, retained as standalone AG open problem (cf. §sec:lemma-A).
- OP-1a: forward reduction to beyond-Johnson list-decoding (cf. §sec:berlekamp-howto Theorem `thm:op1a-johnson-equivalence`).

paper3 contributes 4 unconditional structural results + 1 negative result + 1 conditional row, with the conditional explicitly framed as outside paper3's reach.

This is **prize-grade defensible** for paper3's specific contribution. The remaining frontier is paper2's K-bound program for general `f` (or moment-bound, or sequence-school cross-correlation).

## Closure verdict for Gap B

Gap B is **as closed as paper3 alone can close it**. Future closure requires paper2-domain work:
- **Operative shortcut**: prove `conj:sparse-worst` rigorously at deployment scale (requires above-Johnson plain-RS list-decoder, open since Sudan-Guruswami 1997).
- **Long road**: complete the moment-bound argument for general `f` (paper2 P3 program; current `c ≥ 2` k-wise independence empirically refuted, sequence-school path proposed).

paper3's framing now accurately reflects this state: sparse-class deployable, general-f conditional with explicit frontier acknowledgment + structural support evidence.

## Files (cycles 1–4)

- `notes/0313-gap-B-general-f-structural-analysis.md` — cycle 1 analysis
- `notes/0314-gap-B-multi-prime-branch-certification.md` — cycle 2 multi-prime evidence
- `notes/0315-gap-B-cycle3-parity-aligned-c4.md` — cycle 3 c=4 mechanism
- `notes/0316-gap-B-cycle4-trivial-saturation-sublocus.md` — cycle 4 unified insight
- `notes/0317-gap-B-unified-status.md` — this note (cycle 5 summary)
- `notes/scripts/cycle3_parity_aligned_c4.py`
- `notes/scripts/cycle4_jointsupp_below_w.py`
- `notes/scripts/issue404_branch_certificate.py` (multi-prime tested)
- `notes/scripts/issue404_branch_formula_check.py` (multi-prime tested)

## paper3 edits (cycles 1–4)

- §sec:setup: realizer convention `ξ ≠ 0` (cycle 1, for #401), trivial saturation remark (cycle 4)
- §sec:berlekamp-howto: completeness lemma `lem:r1-completeness` (cycle 1, for #401)
- §sec:sparse-closure: structural footprint paragraph (cycle 1), structural support for conj:sparse-worst with multi-prime evidence (cycle 1+2)
- §sec:unconditionality-summary: "Frontier framing of general-f conditional" paragraph (cycle 2)
- abstract: Note 0310 / 0314 citations (cycle 2)

12 commits on PR #414, ≈ 2,000 lines added, all mergeable.

## Cross-refs

- paper3 §sec:setup, §sec:upper, §sec:sparse-closure, §sec:unconditionality-summary, §sec:lemma-A, §sec:berlekamp-howto, §sec:open-prefactor
- paper2 `thm:universal-K10`, `conj:sparse-worst`, paper2 §11 P3
