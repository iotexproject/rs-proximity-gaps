# Note 0313 — Gap B: general-f deployment closure structural analysis

**Branch:** `feat/op1a-algorithm-fixes` (PR #414)
**Date:** 2026-05-01
**Status:** Cycle 1 of autonomous attack on paper3 prize-readiness Gap B.

## What Gap B is

paper3 currently delivers (per §sec:unconditionality-summary):

| Statement                                              | Status                                          |
|--------------------------------------------------------|-------------------------------------------------|
| `codim V_bad = 2(c-1)`                                 | **unconditional** (Thm:main)                    |
| Uniform-measure obstruction `ε^unif ≥ |F|^{-2(c-1)}`   | **unconditional** (Thm:obstruction)             |
| Sparse-class R2 / R1 closure ≤ 10/q                    | **unconditional, rate-1/4** (via paper2 K10)    |
| **General-f R1/R2 closure ≤ 10/q for all f**           | **conditional on `conj:sparse-worst`**          |
| R1 (Lemma-A path) ε ≤ poly(n,c)/|F|^{2(c-1)}           | empirically **refuted** (Thm:lemma-a-refuted)   |
| OP-1a algorithm                                        | reduces to beyond-Johnson RS list-decoding (open since 1997) |

**Gap B = the general-f closure conditional bullet.** Its only path through paper3 is via paper2's `conj:sparse-worst`, which states: `max_{(f_1,f_2) above-J} K(f_1,f_2) = max_{3-pos sparse} K(...)` — i.e., dense adversaries are dominated by sparse ones.

## Why Gap B is structurally hard

### Direct uniform-measure path is super-polynomial

paper3's `codim V_bad = 2(c-1)` plus variety degree `deg V_bad = C(n,w+1)` gives, on uniform measure:
```
ε^unif ≤ C(n, w+1) · |F|^{-2(c-1)}.
```
At deployment (e.g. Goldilocks, n=2^20, c=3): `log_2 C(n,w+1) ≈ 850,493`, vs. `log_2 |F|^{2(c-1)} ≈ 124`. Net: ε^unif >> 1. Uniform measure is useless on dense general-f at deployment.

### FRI-curve measure path is empirically refuted (Lemma A)

The FRI commit-curve `ℓ_f(α) = (s_1(α), s_2(α))` is a 1-dim parametric curve in F_q^{2D}. Lemma A would have given `E_f #{α : ℓ_f(α) ∈ V_bad} ≤ n^{O(c)}`.

Note 0134 + Thm:lemma-a-refuted show:
- Empirical FRI/uniform ratio ρ ≈ 1.40 ± 0.10 at (8,3,17), 4σ above 1 (i.e. FRI curve does NOT suppress V_bad mass; it slightly amplifies).
- Mass-balance refutation: `E_f[N(ℓ_f)] ≥ ρ · C(n,w+1) · |F|^{-(2c-3)}`. At deployment (saturation regime) this is ≥ |F|/4.
- So Lemma A as stated FAILS by ~850k bits at deployment.

The Lemma-A path is dead.

### Bezout bound on linear curve is useless

For any f, the FRI commit-curve is **linear in α** (degree 1). Bezout gives `K(f) ≤ deg V_bad = C(n,w+1)`. At deployment this is super-polynomial in n (>> |F|), so the bound is trivially satisfied and gives no information.

### Stratified Bezout (Note 0125) is also incompatible with saturation

Note 0125 (companion repo) sketches a "stratified affine degree" approach:
sharpen the additive deg V_bad = C(n, w+1) by accounting for V_S ∩ V_{S'} =
V_{S∩S'} overlaps via inclusion-exclusion. The conjectural target was
deg^{eff}(V_bad) ≤ poly(n, c) = O(n^{O(c)}), which would give
ε ≤ poly(n,c) · |F|^{-2(c-1)}.

This route is **also blocked by saturation**:

- `lem:union-saturation` (paper3 §sec:open-prefactor): in the saturation regime
  `C(n, w+1) · |F|^{-2(c-1)} ≥ 2`, the F_q-point count of V_bad satisfies
  `|V_bad|/|F|^{2D} ≥ 1/4`. Every ABF deployment row is in saturation.
- By Lang-Weil: `|V_bad| = deg(V_bad) · q^{dim} + O(q^{dim - 1/2})`.
  `dim V_bad = 2(w+1)`, so saturation forces
  `deg(V_bad) ≥ |F|^{2(c-1)} / 4`.
- For Goldilocks (`|F|=2^64, c=3`): `deg(V_bad) ≥ 2^{126}`. For any
  poly(n, c), `n^{O(c)}` at `n=2^{20}, c=3` is `2^{O(60)} ≪ 2^{126}`.

So Note 0125's Lemma A_Bezout (stratified deg ≤ poly(n,c)) is **false at
deployment** in the saturation regime. The variety degree of V_bad is
genuinely exponential in |F|, not polynomial in n, at saturation. paper3
§sec:open-prefactor correctly identifies this: the Lemma A path "rules out
generic-line interpretations" (paper3 line 2817), leaving only an FRI-curve
specific (non-generic) suppression as the remaining theoretical possibility,
itself conditional on a δ-far adversarial-f mechanism for which no precursor
is known.

The conclusion is sharper than I gave above: there is no version of Bezout
(naive, stratified, refined) that yields `poly(n,c) · |F|^{-2(c-1)}` for
general-f at deployment, because the variety degree is itself exponential in
|F| in the saturation regime. Any sharpening must come from a
measure-theoretic restriction (specific to the FRI curve, conditional on
δ-far adversarial f) that is still open and faces strong negative evidence
from the Lemma-A FRI/uniform ratio refutation.

### Sparsity bypass (paper2 K10) requires sparsity hypothesis

paper2's K10 universal bound `K(f) ≤ 10` requires `|supp(\hat f)| ≤ 3` and the mod-4 pigeonhole hypothesis. For general f without sparsity, paper2 has no unconditional bound.

`conj:sparse-worst` is paper2's proposed extension: the worst-case max K is achieved on 3-pos sparse pairs, hence the K10 bound transfers to all f. This is paper2's open conjecture.

## Status of `conj:sparse-worst`

### What is verified empirically

- (16, 4)/F_17 (Note 0302): K_sparse^max = 17 (saturated at q), K_dense^max = 16. Sparse strictly ≥ dense by 1.
- (16, 4)/F_17 with joint-distance admissibility (Note 0304): both classes saturate at K=q=17. Sparse ≥ dense (with equality). Consistent with conjecture.

### What was refuted

The **stronger criterion** initially proposed for paper3+paper2 codim composition (#404):
> sparse class saturates paper3 codim 2(c-1); dense class does not; hence max-K on sparse.

The "dense does not saturate" premise is FALSE at (16,4,17,3). Note 0309 + Note 0310 (issue404) replaced the original criterion with a structural composition theorem: paper3's leading codim strata are **reached** by sparse 3-mono codim-1 branches (8 explicit branches at (16,4,17,3) certified at p=193, p=97).

Net: `conj:sparse-worst` itself is **not refuted**, only the easy proof route via dense-exclusion is.

### Why deployment-scale verification is blocked

Verifying `conj:sparse-worst` at (32, 8), (64, 16), or larger requires computing K(f_1, f_2) = #{α : f_1+αf_2 within Hamming distance δn of RS} at deployment scale. For δ above Johnson radius J = n - √(nk), this is exactly **above-Johnson plain-RS list-decoding** — open since Sudan-Guruswami 1997.

So empirical verification at deployment scale is blocked by the same RS-list-decoding open problem that blocks OP-1a.

## What blocks paper3 from closing Gap B itself

paper3's structural toolbox:
1. Codim 2(c-1) of V_bad — purely structural, gives no FRI-curve restriction.
2. Vandermonde / V_S × V_S decomposition — combinatorial, no measure-theoretic content.
3. Sparse-class composition with paper2 K10 — works because paper2 supplies the per-f K-bound.

**For general-f, paper3 has no native mechanism that bounds K(f) for non-sparse f.** Every avenue routes through paper2 (or beyond Johnson list-decoding, which is open).

## Attack angles considered

### A. Reframe paper3's general-f conditional more honestly

paper3 already correctly states this is conditional on a paper2 conjecture. **No over-claim to fix.**

The improvement: cite Note 0310's evidence (paper3 leading strata are reachable by sparse codim-1 branches at the small proxy) as **structural support** for the conjecture, without claiming proof. Currently paper3 only cites empirical (16,4)/F_17 evidence; adding the structural composition theorem strengthens the conditional.

**Action**: insert a `\paragraph{Structural support for the conjecture.}` block in §sec:sparse-closure citing Note 0310.

### B. Lift Note 0310's (16, 4, 17, 3) codim-1 branch construction to (32, 8) and beyond

The (16, 4, 17, 3) construction works because n=16 makes T=⌊(2D-1)/c⌋=7 small enough that 3-mono K_3 ≤ 10 exceeds T. At deployment scale T grows like n/(2c), while paper2 K_s ≤ const for fixed s — so 3-mono can never reach M > T at deployment for any fixed sparse class.

**Conclusion**: the (16,4) construction is fundamentally a small-scale artifact. It does NOT lift to deployment.

In particular, at (32, 8, 3): T=15, K_3 ≤ 10 < 15, K_4 ≤ 12 < 15. Sparse witnesses CANNOT reach V_bad at this scale. Higher-c cells help (lower T) but still bounded.

This **strengthens** paper3's framing: at deployment, V_bad is only reached by adversaries with effective monomial support `s = Ω(n/c) → ∞ as n → ∞`. Sparse adversaries (any fixed s) are **structurally excluded** from V_bad at deployment, regardless of conj:sparse-worst.

**Action**: document this in §sec:sparse-closure as a positive structural finding. The R1 modification "reject when M > T" automatically respects sparse provers at deployment, without invoking conj:sparse-worst at all.

But this doesn't close general-f for paper3. It closes sparse-class more cleanly; general-f is still blocked.

### C. Find new prefactor sharpening (besides Lemma A)

Mass-balance refutation says any sharpening of the form `ε ≤ poly(n)/|F|^{2(c-1)}` is FALSE in expectation. Only an "emergent suppression specific to δ-far above-Johnson adversarial f" could rescue, with no precursor identified.

This is genuinely open. Sequence-school directions (Helleseth, partial Gauss sums on L) might apply, but those are paper2 / future-work territory, not paper3.

**Action**: defer. Document as fundamental open problem.

### D. Rethink the deployment claim's scope

paper3 currently claims:
- Sparse: unconditional rate-1/4
- General: conditional on conj:sparse-worst

If we accept that general-f is genuinely open, paper3's prize-grade contribution is:
1. Codim 2(c-1) (structural, novel, unconditional).
2. Sparse-class deployment closure rate-1/4 (unconditional, via paper2 K10).
3. Structural mechanism explanation (V_bad reachable only by Ω(n)-effective-support adversaries at deployment).
4. Refutation of Lemma A (negative result).
5. Forward reduction OP-1a → beyond-Johnson list-decoding.

This is a 5-fold contribution. The general-f closure being open is fair frontier acknowledgment.

**Action**: clarify in §sec:unconditionality-summary that general-f is "frontier", not a defect.

## Cycle 1 deliverables

This note + (next cycle) the framing-improvement edits (A, B, D) above. Angle C deferred.

## Open question for follow-up cycles

Is there a paper3-internal mechanism (not relying on paper2's K-bound) that gives a non-trivial bound for general-f at deployment?

Quick brainstorm of possibilities (each to be investigated):

1. **Restricted Bezout via curve-degree analysis.** The FRI commit-curve has degree 1, but the "FRI multi-round commit-graph" has higher degree. Maybe the multi-round version gives a sharper Bezout.
2. **Variety-stratification and Lang-Weil.** V_bad's irreducible components have bounded codim variation; maybe the Lang-Weil error term n^{...} gives a non-trivial bound for general lines.
3. **Sequence-school cross-correlation.** Helleseth partial Gauss sums on L = ⟨ω⟩. Cycles of FRI fold are L-cyclic; maybe the L-action on V_bad gives a structural restriction.

These are speculative. Cycle 2 will pick the most tractable.

## Cross-refs

- paper3 §sec:unconditionality-summary (line 401)
- paper3 §sec:sparse-closure (line 1931)
- paper3 §sec:lemma-A / §sec:open-prefactor (line 2515)
- Note 0125 (Bezout prefactor proof — bounds K via Bezout, super-poly at deployment)
- Note 0134 (Lemma A FRI/uniform ratio empirical)
- Note 0136 (extension-field test)
- Note 0302 (sparse-worst empirical at (16,4)/F_17)
- Note 0304 (joint-filter dense counterexample at (16,4,17,3))
- Note 0309-0310 (issue404 finite-pattern theorem)
