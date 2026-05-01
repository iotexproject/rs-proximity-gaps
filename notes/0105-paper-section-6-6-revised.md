# Note 0105 — Paper 1 §6.6 (revised) — Worst-case vs generic max_bad at c ≥ 3

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Replaces**: Note 0095 (which was based on refuted Conjecture v5)
**Target**: paper.tex §6.6 (between §6.5 c=2 exponential and §7 Open Problems)

---

## §6.6 Worst-case vs generic behavior at codimension excess c ≥ 3

### Setup

Let RS_k = RS[F_p, L, k] with |L| = n. Define c := n - k - w (codimension
excess), D := n - k. The worst-case list size for syndrome-line decoding is:
```
   M_max(n, k, p, c) := max_{(s_1, s_2) ≠ (0, 0)} M(s_1, s_2)
```
where M(s_1, s_2) counts γ ∈ F_p^* such that line (s_1 + γ s_2) intersects
Im(V_E) for some support E of size w.

### Theorem 6.6.1 (Phase Diagram, Revised)

**For c = 1** (covering radius): M_max = min(p, C(n, w)). Tight at p ≥ C(n, w).
[Paper 1 Theorem 4.1, Proposition 4.2.]

**For c = 2**: M_max ≈ 0.63 · 1.355^n (exponential in n). Verified through
n = 24 with peak M = 986. [Companion paper §6.5.]

**For c ≥ 3**: M_max ≥ w + 1 = D - c + 1, achieved on a measure-zero
algebraic subvariety of (s_1, s_2)-space. [Theorem 6.6.2 below.]

**Generic (high-probability) bound for c ≥ 3** (Conjecture 6.6.3):
```
   Pr_{(s_1, s_2)}[M(s_1, s_2) > ⌊(2D-1)/c⌋] ≤ poly(n) · p^{-(D + c - 2)}
```
Empirical evidence: ≤ 0 violations in 50,000 random samples at n=12 c=3
(p=1009), with predicted density ≈ 10^{-22}.

### Theorem 6.6.2 (Tetrahedron lower bound)

For RS[n, k] over F_p with c ≥ 3 and w ≥ 2, distinct L_1, ..., L_n ∈ F_p,
and any V = {v_1, ..., v_{w+1}} ⊂ [n], the supports E_i := V \\ {v_i}
satisfy:
```
   M_max(n, k, p, c) ≥ w + 1
```
with equality achieved on the (w+1)-dimensional algebraic subvariety
V_tet(V) ⊂ F_p^{2D} defined by ker A_V (where A_V is the constraint matrix
[N_{E_1} | γ_1 N_{E_1}; ...; N_{E_{w+1}} | γ_{w+1} N_{E_{w+1}}] for any
distinct γ_1, ..., γ_{w+1} ∈ F_p^*).

**Proof**: Lagrange diagonality. The (w+1)×(w+1) matrix M_{ij} := Λ_{E_i}(L_{v_j})
is diagonal: zero off-diagonal (since v_j ∈ E_i for j ≠ i) and nonzero on
diagonal. Hence:
- For (ĥ_j) ∈ X_γ (the twisted syzygy module), evaluating Σ_j ĥ_j Λ_{E_j} = 0
  at L_{v_i} forces ĥ_i(L_{v_i}) = 0 for all i.
- Setting ĥ_i(x) = (x - L_{v_i}) q_i(x) and substituting, the X_γ conditions
  become Σ q_j = 0 ∧ Σ γ_j q_j = 0 in F_p[x]_{<c-1}.
- dim X_γ = (w-1)(c-1) > 0 (for c ≥ 3, w ≥ 2). Hence rank A < min(mc, 2D).
- Open-Set Rank Lemma's escape clause "(0, Λ_{E_i}) ∈ row span A" leads to
  the contradiction ĥ_i(L_{v_i}) ∈ {0, 1/γ_i}; vacuous for any i.
- → Each γ_i is a "true" bad value at this (s_1, s_2). Hence M(s_1, s_2) ≥ w+1.
□

**Corollary**: The unconditional bound M_max ≤ ⌊(2D-1)/c⌋ is FALSE at any
RS[n, k] with c ≥ 3, n ≥ 12 (so that w + 1 > ⌊(2D-1)/c⌋).

### Conjecture 6.6.3 (Generic upper bound)

```
   Pr_{(s_1, s_2) ∈ F_p^{2D}}[M(s_1, s_2) > ⌊(2D-1)/c⌋] ≤ poly(n) · p^{-(D + c - 2)}
```

The exception set V_bad ⊂ F_p^{2D} has codimension at least D + c - 2
(linear in n at fixed c). It decomposes into structural components, the
largest being:
- (w+1)-clique (tetrahedron) varieties V_tet(V) of dimension w+1,
  one per V ⊂ [n] of size w+1
- "Near-tetrahedron" varieties of dimension 1 or 2, structured around
  rank-deficit-1 or rank-deficit-2 (E, γ) configurations

**Empirical verification**: At n = 12, c = 3, p = 1009: codim ≈ 7
(consistent with formula 2D - T - 2 = 7). Exception set density ≈ 10^{-21}.

### Soundness implication

At rate 1/2 with c = c_J(n) (Johnson radius), the soundness gap for FRI
2-round protocol is:
```
   ε_{ca} ≤ ⌊(2D-1)/c⌋/p + poly(n) · p^{-(D + c - 2)}
        ≈ O(1)/p + (negligible at any reasonable p)
```
For BabyBear (p = 2^31), n = 40, c = c_J = 12: ε_{ca} ≤ 2^{-29} + 2^{-1054}.

This matches the well-known FRI soundness rate of O(1)/(c · p) per round.

### Connection to companion §6.5 (c = 2 exponential)

The c = 2 case (companion paper) gives M_max ≈ 0.63 · 1.355^n (exponential).
The transition at c = 3 marks the boundary between exponential and polynomial
scaling of the worst-case list. However, even at c ≥ 3 the worst-case is
super-constant (linear in n via tetrahedron); only the GENERIC behavior is
polynomial in p^{-1}.

### Connection to PR #347 conditional bound

PR #347 proves M_max ≤ ⌊D/(c-1)⌋ under conditions (i)/(ii) on the
configuration. Tetrahedron witnesses (this work) violate one of those
conditions, illustrating why the conditional bound holds but the
unconditional version (Conjecture v3 of #322) is false.

---

## Open Problems (revised §7)

OP2.iii (revised). Prove Conjecture 6.6.3: codim(V_bad) ≥ D + c - 2 at
c ≥ 3. Strategy: catalog structural bad patterns and bound each component's
codim analytically.

OP2.iv (new). Characterize the full structural taxonomy of V_bad components
beyond the tetrahedron. Empirical: 4 distinct patterns at n=12 c=3 m=4 by
degree distribution. Are there more at larger (n, c)?

---

## Summary table for paper

| c                | M_max worst-case        | M_max generic            | Status     |
|------------------|--------------------------|--------------------------|-----------|
| 1                | C(n, w)                  | C(n, w)                  | Theorem 4.1 |
| 2                | ≈ 0.63 · 1.355^n         | exponential              | §6.5      |
| 3                | ≥ w + 1 = D - 2          | ≤ ⌊(2D-1)/3⌋ (conj.)     | §6.6      |
| ≥ 3 (general)    | ≥ w + 1 = D - c + 1      | ≤ ⌊(2D-1)/c⌋ (conj.)     | §6.6      |
| c_J ≈ 0.207n     | ≥ ~0.293n + 1            | ≤ 4 (approx const)       | §6.6      |
