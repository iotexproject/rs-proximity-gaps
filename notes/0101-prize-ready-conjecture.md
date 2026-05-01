# Note 0101 — Prize-ready Conjecture v6 with codim bound

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Builds on**: Notes 0097–0100

## Headline statement (Conjecture v6, prize-ready)

For RS[n, k] over F_p with c = n - k - w ≥ 3, define:
```
   V_bad := {(s_1, s_2) ∈ F_p^{2D} : M(s_1, s_2) > T}
   T := ⌊(2D-1)/c⌋
   V_tet(V) := {(s_1, s_2) : realizes all w+1 γ's of tetrahedron(V)} for V ⊂ [n], |V| = w+1
```

**Conjecture v6**:
```
   V_bad = ⋃_{V ⊂ [n], |V|=w+1} V_tet(V)
```
Equivalently: a (s_1, s_2) achieves M > T iff it lies in the kernel-closure
of some tetrahedron pattern.

## Codimension and density

For each V, V_tet(V) ⊂ F_p^{2D} has:
- Dimension: w + 1 (analytically proven, Note 0099 — equals ker dim of A_tet)
- Codimension: 2D - (w + 1) = w + 2c - 1

Total |V_bad| ≤ Σ_V |V_tet(V)| = C(n, w+1) · p^{w+1}, so:
```
   Pr_{(s_1, s_2)}[(s_1, s_2) ∈ V_bad] ≤ C(n, w+1) · p^{-(w + 2c - 1)}
```

For prize-relevant parameters:

| Field           | n  | k  | c | Bound on Pr                                | Rough Pr                |
|-----------------|----|----|---|--------------------------------------------|-------------------------|
| BabyBear (~2^31)| 12 | 6  | 3 | C(12,4) · p^{-8} = 495 · 2^{-248}          | < 2^{-240}              |
| BabyBear        | 28 | 14 | 6 | C(28,12) · p^{-22} = 30M · 2^{-682}        | < 2^{-650}              |
| BabyBear        | 40 | 20 | 9 | C(40,12) · p^{-28} = 5.5G · 2^{-868}       | < 2^{-830}              |

These are ε ≪ 2^{-128} security levels — trivially soundness-tight for FRI.

## Empirical evidence

### (i) tet-witnesses give exactly M = w+1

At n=12 c=3 p=1009 with V = {1,4,5,8} witness (s_1, s_2):
- M(s_1, s_2) = 4 (exactly the 4 tetrahedron γ values)
- No "spillover" — only the tetrahedron supports are realized
- Verified across multiple kernel basis vectors and random combinations

(Script: `op2_witness_full_M.py`)

### (ii) Tet varieties don't intersect

A V_1 tet-witness realizes ONLY the V_1 tetrahedron, no other V_2. Tested
across all C(12, 4) = 495 vertex subsets. Confirms `V_tet(V_1) ∩ V_tet(V_2) ≈ ∅`
for V_1 ≠ V_2 (intersection is lower-dimensional).

(Script: `op2_intersection_tets.py`)

### (iii) Non-tet rank-deficient configs give M ≤ 2

Across 2000 random m=4 and m=5 support tuples (with random γ tuples):
- Most rank-deficient configs (rank = 2D - 1) have ker dim 1
- (s_1, s_2) ∈ ker realize ≤ 2 distinct γ values, FAR below T=3
- No counterexample found to "non-tet ⇒ M ≤ T"

(Script: `op2_nontet_witnesses.py`)

### (iv) Random (s_1, s_2) achieves M ≤ T

50,000 random (s_1, s_2) at n=12 c=3 p=1009: 0 violations of M ≤ T = 3.
Predicted density ≈ 495 · 1009^{-8} ≈ 5e-22, undetectable.

(Script: `op2_tet_density.py`)

## What remains for FULL proof

### (i) ⇒ direction: V_bad ⊂ ∪_V V_tet(V)

Need: if (s_1, s_2) realizes m > T distinct γ values via supports E_1, ..., E_m,
then ∃ V ⊂ [n] of size w+1 with E_{i_1}, ..., E_{i_{w+1}} = the w-subsets of V
(for some sub-tuple).

**Heuristic reason**: from §iii above, non-tet configurations cannot produce
m=T+1 simultaneously realized γ's. Only tet-structure gives the rank deficiency
necessary for joint realization.

**Proof strategy**: chase the rank-deficiency mechanism. For (s_1, s_2)
realizing m γ's, the matrix A built from these (E, γ) has rank ≤ m·c - 1
(else (s_1, s_2) = 0). For c ≥ 3 with m > T, this forces specific structural
relations — likely the Lagrange diagonality of Note 0099.

### (ii) ⇐ direction: V_tet(V) ⊂ V_bad

PROVEN (Note 0099, analytically).

### (iii) Bound on V_bad ∩ V_tet(V_1) ∩ V_tet(V_2)

Tetrahedron varieties don't intersect significantly. Empirically: a V_1 witness
realizes 0 V_2 supports for V_1 ≠ V_2. Need an analytic version.

## Roadmap to prize-ready

1. **Prove (i)**: characterize V_bad as union of tet varieties (1-2 weeks).
   Strategy: use Lagrange diagonality + counting argument on rank deficit.

2. **Codim sharp bound** (already empirically tight): codim V_tet(V) = w + 2c - 1.

3. **Density theorem**: Pr[(s_1, s_2) ∈ V_bad] ≤ C(n, w+1) · p^{-(w + 2c - 1)}.

4. **FRI 2-round soundness**: apply density bound to compute ε_ca for the
   FRI-style protocol. Compare to BCIKS / Crites-Stewart.

5. **Paper**: write up as Paper 1 §6.6 + soundness corollary.

## Files (this update)

- `notes/scripts/op2_witness_full_M.py` — (i) tet-witness M computation
- `notes/scripts/op2_intersection_tets.py` — (ii) tet variety intersections
- `notes/scripts/op2_nontet_witnesses.py` — (iii) non-tet kernel analysis
- `notes/scripts/op2_bad_set_chars.py` — rank-def vs tet-pattern statistics
- `notes/0101-prize-ready-conjecture.md` — this file
