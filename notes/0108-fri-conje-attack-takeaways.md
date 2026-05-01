# Note 0108 — Takeaways from fri-conje-attack for v6 v2 codim proof

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Source branch**: `origin/codex/fri-conje-attack` (notes 0187 — 0226)
**Use**: cross-pollination — what techniques from the FRI ConjE / G3 attack
transfer to the v6 v2 codim bound (Note 0107 target)?

## Headline takeaways

The G3 attack on FRI ConjE matured a lot in the parallel branch. Three
techniques look directly applicable to v6 v2.

### 1. Locator/divisor elimination → eliminating polynomial Φ(γ)

**Their setup** (Notes 0200, 0204, 0217, 0224): a bad ratio ρ corresponds to
a monic locator P(x) with `P | x^n − 1` plus high-vector certificate
equations. Bezout-style elimination of the locator coefficients produces a
q-independent polynomial `Φ(ρ)` of degree ≤ 9 cutting out the bad-ratio set.

**Translation to Berlekamp**: for a support tuple (E_1, ..., E_m) and
γ-tuple (γ_1, ..., γ_m), the rank deficit `rank A(γ) < mc` is cut out by
m × c minors of A(γ) — polynomials in (γ_1, ..., γ_m) of degree ≤ c per
variable. The eliminating ideal `I_E = <minors>` should have a low-degree
generator after elimination of the auxiliary X_γ syzygy variables.

**Where this helps**: codim of V_rd(E) := {γ : rank A(γ) < mc} in (γ-space)^m
controls the contribution of (E, γ) configurations to V_bad. If we can show
codim V_rd(E) ≥ k_E for non-tet supports, then by Schwartz-Zippel the
contribution density is `p^{−k_E}` smaller than naive.

### 2. Routed dichotomy (Note 0202)

**Their setup**: instead of "universal m ≤ 1", classify the bad ratios into
4 routes (empty / boundary-all-rho / sign-paired / ordinary), each with its
own bound. Sum of route bounds gives the prize-grade total.

**Translation to Berlekamp**: instead of "universal codim 2D − T − 2", split
support tuples (E_1, ..., E_m) into routes:
- **Tet route**: E contains a (w+1)-clique sub-pattern. Codim 2D − (w+1) =
  2D − T − 2 (NOTE: this matches the target asymptotically, since
  T+2 = w+2 at full rate via T = ⌊(2D−1)/c⌋). RIGOROUS via Note 0099.
- **Pattern A/B/C/D routes**: 4 specific non-tet structural failure modes
  catalogued in Note 0103. Each gives ker dim 1 or 2 → contribution codim
  2D − 1 or 2D − 2.
- **Generic non-tet route**: all other tuples have rank A = mc (full),
  contribution codim mc − m = m(c−1) ≥ T(c−1) ≈ 2D − T (since T ≈ 2D/c).

So `min` over routes = min(2D − T − 2, 2D − 1) = 2D − T − 2. ✓

### 3. Subperiod / wrong-period locator (Note 0212)

**Their finding**: the (n,k)=(24,6) partial-profile counterexample fails
because its locator lies in F[X^4] instead of the desired F[X^6] —
"competing subperiod" obstruction.

**Translation to Berlekamp**: Pattern D at n=12 c=3 m=4 has degree
distribution {0:5, 1:3, 2:3, 3:1} on a 7-element union, with ker dim 2.
Hypothesis: Pattern D is a "competing subperiod" — supports lie in a
sub-(w+1)-clique structure on a smaller index set. Test: does Pattern D
embed a (w'+1)-clique on a subset of [n] for some w' < w?

Pattern A / B / C / D may all be competing-period analogs; if so, the
"right period" (full tetrahedron) is the only ordinary route and the others
are bounded by the subperiod codim.

## What does NOT directly transfer

### Action/orbit theorem (Note 0187)

In FRI ConjE, the cyclic group action on bad ratios reduces enumeration by
the orbit size. In Berlekamp, the natural action is `(s_1, s_2) ↦ (λ s_1,
μ s_2)` for (λ, μ) ∈ (F_p^*)^2, which moves γ ↦ (μ/λ)γ. This is a
2-dim action on V_bad, but it doesn't reduce the codim (it just reduces
the polynomial factor in the count).

### Sign-paired coset rigidity (Note 0197)

The 4-th-root-of-unity rigidity uses the cyclic structure of L_n. Berlekamp
has no native cyclic structure on the support set (just abstract subsets of
[n]). Could possibly help if we restrict to L = multiplicative subgroup,
but that's not the generic Berlekamp setup.

## Concrete attack plan for v6 v2

**Phase 1 (this session)**: test Routed Dichotomy hypothesis computationally.

For each non-tet bad pattern observed at n=12 c=3 m=4:
- Compute codim of V_rd(E) ⊂ (F_p^*)^m via Schwartz-Zippel sampling
- Check "sub-tetrahedron embedding" hypothesis (Pattern D first, Note 0212-style)
- Build eliminating polynomial Φ_E(γ_1, ..., γ_m) and compute its degree

**Phase 2 (next sessions)**: prove the route-codim bounds rigorously.

For Pattern A: codim V_rd(E) = ?, generic δ = ?, contribution codim = ?
For Pattern D (subperiod): apply Note 0099 Lagrange diagonality to the
sub-tetrahedron, get codim ≥ (w'+1)·... bound.

**Phase 3**: assemble routed theorem + non-tet route closure → v6 v2
RIGOROUS at small n, then scale-uniform via subperiod analysis.

## Files to read in tandem

- `notes/0107-math-handoff.md` — original math handoff (single problem statement)
- `origin/codex/fri-conje-attack:notes/0202-prize-facing-g3-closure-theorem.md`
  — the routed dichotomy template
- `origin/codex/fri-conje-attack:notes/0212-competing-subperiod-obstruction.md`
  — subperiod obstruction
- `origin/codex/fri-conje-attack:notes/0224-a32k-family-scale-uniform-certificate.md`
  — scale-uniform locator gap via Groebner

## Specific transfer hypothesis

**H1**: Pattern A/B/C at n=12 c=3 m=4 are "competing-subperiod" tetrahedra
on smaller subsets of [n].
**Test**: enumerate all (w'+1)-cliques on subsets of size ≤ 8 of [n]=12;
check if Pattern A/B/C supports embed any.

**H2**: The eliminating polynomial Φ_E(γ_1, ..., γ_m) has degree O(c) per
variable for non-tet supports.
**Test**: compute Φ_E via resultant for Pattern A and measure degree.

**H3**: Pattern D's ker dim 2 corresponds to a "second-order" subperiod
phenomenon with codim contribution 2D − 2 (not 2D − 1).
**Test**: empirical density measurement at multiple p.

If H1 holds: routed theorem reduces to tet codim + subperiod codim, both
provable by Lagrange diagonality on the appropriate sub-clique.

If H2 holds: eliminating polynomial gives explicit codim bound matching
Schwartz-Zippel.

H3 is for refinement, not the main bound.
