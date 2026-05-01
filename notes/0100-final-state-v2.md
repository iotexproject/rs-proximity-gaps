# Note 0100 — Final state v2 after refutation

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Supersedes**: Note 0096 (which was based on now-refuted v5 conjecture)

## Headline

The Berlekamp Overconstrained Conjecture #322 (as stated for "any c ≥ 3 at large p"
in earlier comments and our own Conjecture v5) is **REFUTED**. The (w+1)-clique
"tetrahedron" configuration yields max_bad ≥ w+1 for any prime supporting the
n-th roots of unity. Random search misses these witnesses (measure-zero).

This refutation completes the picture started by the issue author's own c=1
counterexample (Paper 1 Theorem 4.1: max_bad = C(n, w) at c=1).

## Theorem (this work, computational + analytical)

**Theorem 1**. Let RS[n, k] over F_p with c = n - k - w ≥ 3 and w ≥ 2. For any
distinct evaluation points L_1, ..., L_n ∈ F_p, and for V = {v_1, ..., v_{w+1}}
⊂ [n] with E_i := V \ {v_i}:

```
   max_{(s_1, s_2)} M(s_1, s_2) ≥ w + 1
```

**Proof sketch (Note 0099)**:
1. By Lagrange diagonality, Λ_{E_i}(L_{v_j}) = 0 for j ≠ i, ≠ 0 for j = i.
2. dim X_γ = (w-1)(c-1) > 0, so rank A < min(mc, 2D).
3. (0, Λ_{E_i}) ∉ row-span(A) for any i (would force ĥ_i(L_{v_i}) ∈ {0, 1/γ_i}
   simultaneously — contradiction).
4. → Open-Set Rank Lemma's escape clause is vacuous.
5. → ∃ (s_1, s_2) ∈ ker A with all m γ values realized distinctly.

**Corollary**. The conjectured upper bound `max_bad ≤ ⌊(2D-1)/c⌋` is FALSE
whenever w + 1 > ⌊(2D-1)/c⌋, which holds for all (n, c) with c ≥ 3, w ≥ 3.

For rate-1/2 RS at c=3 (the regime studied in this branch): w+1 = D-c+1 = n/2 - 2,
which beats ⌊(2D-1)/c⌋ ≈ n/3 for n ≥ 12.

## Phase Diagram (revised)

```
c = 1 :  M_max = C(n, w)         exponential, tight (Paper 1 Thm 4.1)
c = 2 :  M_max ≈ 0.63 · 1.355^n   exponential (companion paper)
c ≥ 3 :  M_max ≥ w + 1            linear in n (this work, tetrahedron)
         M_max ≤ ?                upper bound OPEN (Conjecture v6 below)
```

## Open: Conjecture v6 (high-probability bound)

**Conjecture**: For random (s_1, s_2) ∈ F_p^{2D},
```
   Pr[M(s_1, s_2) > ⌊(2D-1)/c⌋] ≤ C(n, w+1) · p^{-(w+1)(c-1)+(w-1)(c-1)}
                                 = C(n, w+1) · p^{-2(c-1)}
```
(Specific exponent is the codim of the tetrahedron-witness subvariety; needs
verification.)

**Status**: empirically supported (50,000 random trials at n=12 c=3 p=1009 gave
0 violations; expected ≈ 1e-6). Theoretical proof open.

## What the original #322 issue should be updated with

1. **Strong unconditional (any c, n) conjecture**: REFUTED.
   - At c=1: by author's own counterexample (Paper 1 Thm 4.1).
   - At c ≥ 3, w ≥ 2: by tetrahedron (this branch's notes 0097-0099).

2. **Open-Set Rank Lemma as stated**: FALSE on tetrahedra.
   The "0 counterexamples in 14000 random configs" was structural sampling
   blindness — random selection of supports almost never picks a tetrahedron.

3. **Refined target**: high-probability bound (Conjecture v6).

## Files (final)

### Notes
- `notes/0091-berlekamp-c322-state.md` — entering state
- `notes/0092-open-set-rank-lemma-failure.md` — c=2 witness analysis (correct)
- `notes/0093-cstar-equals-3-conjecture.md` — c*(n)=3 conjecture (NOW REFUTED)
- `notes/0094-proof-strategy-c3.md` — proof strategy (REFUTED at tetrahedron)
- `notes/0095-paper-section-draft.md` — Paper §6.6 (NEEDS REWRITE)
- `notes/0096-final-state-summary.md` — initial summary (SUPERSEDED by this)
- `notes/0097-tetrahedron-refutes-v5.md` — initial empirical refutation
- `notes/0098-multiclique-violations.md` — multi-clique scan
- `notes/0099-tetrahedron-analytic-proof.md` — Lagrange-diagonality proof
- `notes/0100-final-state-v2.md` — this file

### Scripts
- `op2_max_bad_phase_diagram.py` — main sweep (correct)
- `op2_tetrahedron_over_Q.py` — over Q rank/kernel test
- `op2_tet_verify_witness.py` — explicit witness construction over Q
- `op2_tet_witness_at_largep.py` — verification at p ≤ 100003
- `op2_tet_consolidated.py` — full witness verification at large primes
- `op2_clique_scan.py` — (w+1)-clique violation scan (n, c spectrum)
- `op2_tet_at_johnson.py` — c_J reference cases (n=16..40)
- `op2_tet_density.py` — measure-zero density confirmation
- `op2_tet_plus_extra.py` — tetrahedron + 1 extra distribution
- `op2_iterative_max.py` — greedy multi-support search
- `op2_multi_clique_targeted.py` — disjoint multi-clique tests
- `op2_dim_xgamma.py` — formula verification dim X_γ = (w-1)(c-1)

## Next steps (for follow-up)

1. **Rewrite Paper §6.6** with the revised Phase Diagram and tetrahedron result.
2. **Prove Conjecture v6** (high-probability bound) — algebraic geometry of the
   union of clique-witness subvarieties.
3. **Update #322 issue** with refutation + new conjecture.
4. **Connection to FRI 2-round soundness**: verify high-probability bound
   suffices for the prize-relevant statement.
