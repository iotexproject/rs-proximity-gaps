# Note 0098 — Multi-clique violations and refined max_bad picture

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Builds on**: Note 0097 (tetrahedron refutes v5)

## Headline findings

1. **Tetrahedron**: m = w+1 distinct bad γ. Universal at c ≥ 3, all primes.
2. **Tet + compatible extras**: at n=12 c=3 we get m=5; at n=16 c=3 we get m=8.
   Greedy growth from a single tetrahedron continues until the remaining
   compatible extras are exhausted.
3. The worst-case max_bad **grows linearly in n** at fixed c≥3 via the
   tetrahedron alone (m_max ≥ w+1 = D-c+1), far exceeding the
   conjectured ⌊(2D-1)/c⌋ bound. Disjoint tetrahedra do NOT combine.
4. All these witnesses live on **measure-zero subvarieties** of (s_1, s_2)-space,
   so random search at FRI-relevant primes never sees them.

## Empirical scan

### Single tetrahedron always violates (Note 0097, confirmed)

| n  | c | w  | Bound ⌊(2D-1)/c⌋ | m=w+1 (tet) | violation |
|----|---|----|------------------|-------------|-----------|
| 12 | 3 | 3  | 3                | 4           | 1.33×     |
| 16 | 3 | 5  | 5                | 6           | 1.20×     |
| 20 | 3 | 7  | 6                | 8           | 1.33×     |
| 24 | 3 | 9  | 7                | 10          | 1.43×     |
| 28 | 3 | 11 | 9                | 12          | 1.33×     |
| 28 | 4 | 10 | 6                | 11          | 1.83×     |
| 28 | 5 | 9  | 5                | 10          | 2.00×     |

### Disjoint multi-tetrahedra DON'T combine

Pairs of disjoint (w+1)-vertex sets, each a tetrahedron pattern: kernel exists
but joint realization always fails (`best=0` over 30 trials). E.g.:
- n=24 c=3, 2 disjoint tetrahedra (m=20): best=0
- n=28 c=4, 2 disjoint tetrahedra (m=22): best=0

The intersection of the two kernels in (s_2)-space forces some N_E·s_2 = 0,
breaking the open conditions for at least one tetrahedron.

### Tet + extras (greedy)

| n  | c | Tet m₀ | Greedy m_max | extras |
|----|---|--------|--------------|--------|
| 12 | 3 | 4      | 5            | +1     |
| 16 | 3 | 6      | 8            | +2     |

Extras are carefully chosen supports outside the tetrahedron that "fit" the
existing kernel structure. Fewer than expected — m_max grows slowly with n
beyond the tet baseline.

## Density of violations (random search blindness)

50,000 random (s_1, s_2) at n=12 c=3 p=1009 with tetrahedron supports:
- 100% gave 0 realized γ (no witness)
- Predicted density of bad (s_1, s_2): codim ≥ 4 → fraction ~ p^{-4} ≈ 10^{-12}

This explains why all prior empirical "max ≤ bound" reports across 14000+
random configurations missed the structural violations.

## Reformulated conjecture (v6)

**Worst-case bound is FALSE**. The right separation is:

- **Worst-case lower bound**: max_{(s_1,s_2)} M(s_1, s_2) ≥ w+1 + (extras),
  growing at least linearly in n at c=3, achieved on measure-zero set.
- **Generic / high-probability bound** (Conjecture v6, conjectured): for random
  (s_1, s_2) ∈ F_p^{2D},
  ```
     Pr[M(s_1, s_2) > ⌊(2D-1)/c⌋] ≤ O(p^{-c'}) for some c' ≥ 1
  ```
  i.e., the exception set is a Zariski-closed proper subvariety of codimension ≥ 1.

**For FRI / RS soundness in the prize context**: the verifier's challenge is
random, so the high-probability bound is what matters. The worst-case violations,
while real, are inaccessible to a prover and irrelevant to soundness.

## Implications for the original #322 issue

The author's own resolution proposal stated:
> close #322 as "strong unconditional version disproved (factor 2× counterexample),
> refined unconditional bound ⌊(2D−1)/c⌋ adopted as the empirical/conjectural
> target"

Our finding strengthens this further:
1. **Refined unconditional bound is also FALSE** at c ≥ 3 (tetrahedron + extras).
2. The right statement is the **generic** version: holds outside a measure-zero
   subvariety of (s_1, s_2)-space.
3. The "Open-Set Rank Lemma" claimed in the issue thread is **false on tetrahedra**;
   it holds only on configurations not containing a (w+1)-clique sub-pattern.

Both adjustments are corroborated by author's own c=1 counterexample (Paper 1
Theorem 4.1: max_bad = C(n, w) at c=1).

## Connection to Paper 1

Paper 1 §4 (c=1) and §6.5 (c=2 exponential) describe exact worst-case behavior.
Paper 1 §6.6 (c≥3) was DRAFTED as "linear bound at large p" — this is wrong
(per this note). The correct §6.6 statement is:

> **Phase Diagram (revised)**:
> - c=1: M_max = C(n, w) (Paper 1 Theorem 4.1, tight)
> - c=2: M_max ≈ 0.63 × 1.355^n (exponential, c=2 paper)
> - c≥3 worst-case: M_max ≥ w+1 (tetrahedron, Note 0097), ≥ ~n/2 via multi-clique
> - c≥3 generic: M_max ≤ ⌊(2D-1)/c⌋ outside Zariski-closed measure-zero subvariety
>   (conjectured)

## Files

- `notes/scripts/op2_iterative_max.py` — greedy multi-clique search
- `notes/scripts/op2_tet_plus_extra.py` — tet + 1 extra distribution
- `notes/scripts/op2_tet_consolidated.py` — full verification at large primes
- `notes/0097-tetrahedron-refutes-v5.md` — initial refutation
- `notes/0098-multiclique-violations.md` — this file

## Next steps

1. Complete n=20, 24 greedy data → asymptotic formula
2. Prove generic bound (Conjecture v6) — replaces the broken Open-Set Rank Lemma
3. Draft #322 update comment with these findings
4. Rewrite Paper §6.6 with the Phase Diagram (revised)
