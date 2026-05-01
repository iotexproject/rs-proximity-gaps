# Note 0107 — Math Handoff for Next Session

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Use**: read this FIRST in next session (post-compact)

## Single math problem to attack

**Prove Conjecture v6 v2**:
```
   Pr_{(s_1, s_2) ∈ F_p^{2D}}[M(s_1, s_2) > T] ≤ poly(n) · p^{-(2D - T - 2)}
```
where T := ⌊(2D-1)/c⌋ and `M(s_1, s_2)` counts γ ∈ F_p^* such that
`s_1 + γ s_2 ∈ ker N_E` for some support E ⊂ [n] of size w.

Equivalent: codim of `V_bad := {(s_1, s_2) : M > T}` is ≥ 2D - T - 2 over
algebraic closure (asymptotically tight).

## What's already done (load these into context)

### Rigorous (don't re-derive)

1. **Theorem 1 (Note 0099)**: tetrahedron variety V_tet(V) for V ⊂ [n], |V|=w+1.
   - dim V_tet(V) = w + 1 (proven via dim X_γ = (w-1)(c-1))
   - codim = w + 2c - 1
   - On V_tet(V): M(s_1, s_2) = exactly w + 1
   - Proof via Lagrange diagonality: Λ_{V\{v_i}}(L_{v_j}) = 0 for j ≠ i

2. **Codim formula `dim X_γ = (w-1)(c-1)`** verified 19/19 cases.

### Empirical (use as evidence/intuition)

3. **At n=12 c=3 m=4**: 4 distinct non-tet bad pattern types observed
   (op2_nontet_pattern_analysis.py output). Each gives ker dim 1 or 2.
4. **Codim 2D - T - 2 verified** at p=1009 for n ∈ {12, 16, 20, 24}, c ∈ {3, 4, 5}
   modulo polynomial factor (asymptotic at large p).
5. **At larger m (m=6, 7)**: 0 non-tet bad in 2000 trials — only tet contributes.
   Suggests non-tet bad CONFINED to small m regime (= small T, = larger c).

## Proof strategies to try

### Strategy A: catalog non-tet patterns

For (s_1, s_2) realizing m γ's via supports E_1, ..., E_m, the (E, γ) config
has rank deficit ≥ 1 AND lemma escape fails for all i.

Empirical finding: only ~1-2% of random (E, γ) tuples are "non-tet bad" at
small m; 0% at larger m.

**Sub-problem**: characterize all (E, γ) tuples admitting (s_1, s_2) with
M = m. Empirically, 4 patterns at n=12 c=3:
- Pattern A: degree {0:4, 1:4, 2:4}, intersection {0:3, 1:2, 2:1}, |union|=8
- Pattern B: {0:5, 1:2, 2:5}, {0:2, 1:3, 2:1}, |union|=7
- Pattern C: {0:3, 1:6, 2:3}, {0:3, 1:3}, |union|=9
- Pattern D: {0:5, 1:3, 2:3, 3:1}, {0:3, 2:3}, |union|=7, ker dim=2

Hint: Pattern D has 3 of 4 supports forming a "tetrahedron minus one vertex"
sub-structure on a 4-set. Other patterns may have similar hidden structure.

### Strategy B: κ-distribution analysis

For (ĥ_j) ∈ X_γ, evaluate constraints at L_v. Define κ_v := |{j : v ∉ E_j}|.

**Already shown** (Note 0099 + op2_pointwise_evaluation.py):
- κ_v ≤ 2 (and γ's distinct) → all ĥ_j(L_v) = 0 for j ∈ J(v)
- κ_v = 1 at tet vertices forces ĥ_v(L_v) = 0 (single root)
- ĥ_j with c forced zeros → ĥ_j ≡ 0

**To prove**: For non-tet supports, ALWAYS exists j with |F_j| ≥ c (forcing ĥ_j ≡ 0).
Then if some ĥ_j is forced 0, the X_γ syzygy has effective length < m, and
combinatorial argument → bound on m.

### Strategy C: shifted syzygy direct construction

The lemma's escape: ∃ (p_j) with `Σ p_j Λ_{E_j} = 0 ∧ Σ γ_j p_j Λ_{E_j} = Λ_{E_i}`.

For non-tet supports, construct (p_j) explicitly via Vandermonde-style argument
on (γ_j) — should work generically except for tet-pattern algebraic
coincidences.

**To prove**: For non-tet supports, the "obstruction" to shifted syzygy is
codim ≥ ? in (γ tuple) space. Combined with f_bad ≈ p^{-1} per (E, γ), the
total bad set codim is 2D - T - 2 + corrections.

## Files to read (in order)

```bash
# Rigorous proofs
notes/0099-tetrahedron-analytic-proof.md     # Theorem 1, Lagrange diagonality

# Conjectures + empirics
notes/0103-revised-v6.md                      # Conjecture v6 v2 statement
notes/0101-prize-ready-conjecture.md          # codim derivation

# Tooling
notes/scripts/op2_dim_xgamma.py               # X_γ dim verification
notes/scripts/op2_pointwise_evaluation.py     # κ-distribution analysis
notes/scripts/op2_shifted_syzygy.py           # lemma escape clause
notes/scripts/op2_nontet_pattern_analysis.py  # 4 pattern catalog
notes/scripts/op2_verify_codim.py             # density measurement

# Strategic context (skip if pure math focus)
notes/0102-prize-readiness-assessment.md
notes/0104-fri-soundness-application.md
notes/0106-session-final.md
```

## Specific computational experiments to run if stuck

1. **At n=20 c=5 m=4** (T=3): characterize all non-tet bad patterns, count them.
2. **At n=12 c=4 m=3** (T=2): does m=3 admit non-tet bad? If yes, what patterns?
3. **At very small p** (p=11 or 13): do exhaustive enumeration of (s_1, s_2)
   with M > T. Verify directly which pattern each falls into.
4. **Polynomial-factor scaling**: vary p ∈ {97, 257, 1009, 4001, 16001} at fixed
   (n, c) to extract the asymptotic codim formula precisely.

## Math strategy: where to start

Start with **Strategy B (κ-distribution)** — most concrete and partially worked
out in Notes 0099 and op2_pointwise_evaluation.py. The goal:

> **Lemma (target)**: For supports E_1, ..., E_m of size w in [n] with m ≥ 1
> and X_γ ≠ {0}, if E does NOT contain a (w+1)-clique sub-pattern, then ∃ j
> with |F_j| ≥ c (forcing ĥ_j ≡ 0 in any X_γ syzygy).

If proven: any non-tet rank-deficient config has effective syzygy length < m,
which by induction/case analysis gives the desired codim bound.

## Don't write paper until math is done

Per user instruction (compact + next session):
- Focus on math problem
- Paper writeup deferred
- 不着急 — quality over speed
