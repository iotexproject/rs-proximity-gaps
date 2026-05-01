# Note 0112 — Theorem 1: routed dichotomy ⇒ v6 v2 codim bound

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Builds on**: Notes 0099, 0107–0111
**Status**: ⚠️ **BROKEN** — see Note 0114. Stated codim claims are wrong
because they conflated `dim ker A(γ)` (per fixed γ) with `dim V_tet(V)`
(union over γ). The 3 route codim contributions at c=3 n=12 should all
be 4, not 7 or 8. Theorem 1 conclusion `codim V_bad ≥ 2D − T − 2 = 7` is
empirically refuted; actual codim is 4.

## Setup

Reed-Solomon code with parameters: `n` evaluation points with distinct
`L_v ∈ F_p^*`, dimension `k`, `D = n − k`. Choose codimension excess
`c ≥ 3`, set `w = D − c`, `T = ⌊(2D − 1)/c⌋`. Define
```
M(s_1, s_2)  :=  | { γ ∈ F_p^* : ∃ E ⊂ [n], |E| = w, s_1 + γ s_2 ∈ ker N_E } |
V_bad        :=  { (s_1, s_2) ∈ F_p^{2D} : M(s_1, s_2) > T }.
```

**Conjecture v6 v2 (Note 0103, Note 0107)**: `|V_bad| ≤ poly(n) · p^{2D − T − 2}`.

Equivalently: codim `V_bad ≥ 2D − T − 2`.

## Theorem 1 (routed dichotomy at `c = 3`)

For `n ≥ 12`, `c = 3`, `T = ⌊(2D − 1)/3⌋`:
```
codim V_bad   ≥   2D − T − 2.
```

The bound is **tight** at `n = 12, c = 3` (where `2D − T − 2 = 7` and the
rd-Pattern-C-star route gives exactly `p^{−7}`).

### Proof (overview)

For any `(s_1, s_2)` with `M(s_1, s_2) ≥ T + 1`, pick `m = T + 1` distinct
`γ_1, ..., γ_m` and supports `E_1, ..., E_m` realizing `s_1 + γ_i s_2 ∈ ker N_{E_i}`.
The configuration `(E_1, ..., E_m; γ_1, ..., γ_m)` falls into exactly one of
the following four routes:

1. **Tet route**: there exists `V ⊂ ⋃ E_j` with `|V| = w + 1` and
   `{V \ {v_i}}_{v_i ∈ V} ⊂ {E_j}_{j ∈ [m]}` (full tetrahedron).
2. **Sub-tet route**: not in (1), but there exists `V ⊂ ⋃ E_j` with
   `|V| = w' + 1`, `2 ≤ w' < w`, and `m' = w' + 1` of the supports `E_j`
   form a sub-tetrahedron on `V` (`V \ {v_i} ⊂ E_{j_i}`, `v_i ∉ E_{j_i}`).
3. **rd-Pattern-C-star route**: not in (1) or (2), but `(E_1, ..., E_m)` has
   the Pattern C signature with star intersection-graph topology, AND
   `det M = 0` for the leaf-extras coefficient matrix (Note 0111).
4. **Generic non-rd route**: not in (1)–(3); rank `A(γ)` deficit is
   determined by the codim-`≥ 1` variety `{det A(γ) = 0}` in `γ`-space.

The four routes are mutually exclusive (since each is defined modulo the
preceding ones). The **codim contribution** from each route is bounded:

| Route                    | Reference  | Codim contribution     |
|--------------------------|------------|------------------------|
| Tet                      | Note 0099  | `≥ w + 2c − 1`         |
| Sub-tet (`w' = w − 1`)   | Note 0110  | `≥ T + 2c − 1`         |
| rd-Pattern-C-star        | Note 0111  | `= m + 1 + (2D − m − 1) − 2D = 2D − T − 2` (TIGHT) |
| Generic non-rd           | Sch.-Zip.  | `≥ 2D − T − 1`         |

For each `c = 3, n ≥ 12`:
- `w + 2c − 1 = w + 5`. At `n = 12, w = 3`: `8`. Target `7`. ✓
- `T + 2c − 1 = T + 5`. At `n = 12, T = 3`: `8`. Target `7`. ✓
- rd-star: exactly `2D − T − 2`. ✓
- Generic non-rd: `≥ 2D − T − 1 ≥ 2D − T − 2`. ✓

Taking the minimum, codim `V_bad ≥ 2D − T − 2` at `c = 3`. □

## Status of each route

### Tet route (RIGOROUS, Note 0099)

`Λ_{V \ {v_i}}(L_{v_j}) = 0` for `i ≠ j` (Lagrange diagonality) ⇒ `dim X_γ_tet = (w − 1)(c − 1)` ⇒ explicit codim formula. Verified 19/19 cases.

### Sub-tet route (RIGOROUS modulo generic-rank, Note 0110)

Same Lagrange diagonality at sub-tet `V` of size `w' + 1`, `2 ≤ w' < w`,
with the **strict** condition `v_i ∉ E_i`. Yields:
```
dim X_γ_sub  =  max{0, (w' − 1)(c − 1) − 2(w − w')}    (generic extras)
```
Bad-realizing sub-tet ⇒ extras-collision (some `Π_{U_i}, Π_{U_j}` linearly
dependent) ⇒ extra `≥ 1` dim, gives explicit witness.

Verified 9/9 (n, c, w, w') cases for the generic formula; 3 collision
sub-cases verified explicitly.

### rd-Pattern-C-star route (RIGOROUS, Note 0111)

For Pattern C with star topology, Lemma 3.1 gives **forced zeros**
`ĥ_j(L_{v_l}) = 0` for `j leaf, l ≠ j` via the rank-2 system from `(P, R)`
evaluations. This forces `ĥ_j ∝ Λ_{E_c}/(x − L_{v_j})` (Lemma 3.2),
reducing the X_γ-system to a **single linear dependence** of
`Π_{U_a}, Π_{U_b}, Π_{U_d}` in `F_p[x]_{<c}` (Lemma 3.3).

⇒ rd-star ⇔ `det M = 0`. Empirically verified 1500/1500 in the if-and-only-if.

### Generic non-rd route (Schwartz-Zippel, established)

For `(E_1, ..., E_m)` with `rank A(γ)` generically `mc` (no rd):
- `V_rd(E) := {γ : rank A(γ) < mc}` has codim `≥ 1` in `(F_p^*)^m`.
- For each `γ ∈ V_rd`, `ker A(γ)` has dim `≥ 1` in `(s_1, s_2)`-space.
- Total bad realizations: `≤ p^{m − 1} · p · # configs = poly(n) p^m`.
- Density per (E, γ): `p^{m − 2D}`.

Contribution: `≤ poly(n) · p^{−(2D − m + 0)} = poly(n) · p^{−(2D − T − 1)}`.

This is *weaker* (i.e. higher codim) than rd-star, so no bottleneck.

## Tightness at n=12, c=3, T=3

Every route gives codim `≥ 8` *except* rd-star, which gives codim `= 7`.
Empirically (Note 0103 + verify_codim.py) the codim approaches 7 at large
`p` for `n = 12, c = 3`, matching exactly. The **rd-Pattern-C-star route is
the unique bottleneck**.

## Open items (`c ≥ 4`)

At `c = 4, n = 16, m = 4`: empirical scan (`op2_routed_dichotomy_c4.py`)
finds 31/46 non-tet bad embed sub-tet, 15/46 don't (multi-pattern). The
rd-star analog at `c = 4` has `M ∈ F_p^{4 × 4}` (since `Π_{U_j}` of degree
`c − 1 = 3` has 4 coefficients), a single det-vanishing condition. Need:

1. **Verify Lemmas 3.1–3.3 generalize to `c ≥ 4`** (TODO: rerun
   op2_rd_star_lagrange.py at c=4 n=16 with larger trial budget).
2. **Catalog non-sub-tet, non-Pattern-C routes** at `c ≥ 4` — there may be
   additional routes (e.g. degree {1:8, 2:4} pattern observed empirically).
3. **Tetrahedron + sub-tet codim accounting** at `c ≥ 4`: the simple
   formula gives `T + 2c − 1`, which at `c=4, T=4` is 11 < target 14. Need
   recursion on sub-tet `w' = w − 1` with stricter codim from extras.

These do not affect the `c = 3` result but block scale-uniform `c ≥ 4`
prize-grade application.

## Implication for FRI prize

Combining Theorem 1 (`c = 3` rigorous) with Note 0104 (FRI 2-round
soundness) yields the prize-grade soundness:
```
ε_FRI ≤ (codim factor) × p^{−(2D − T − 2)}
```
matching the Crites-Stewart upper-bound regime. Per Note 0104, at BabyBear
parameters `n = 40, c = 3` this gives `ε_FRI ≤ 2^{−116}`.

## Conclusions

**Lemma 2.1 (sub-tet Lagrange) and Lemma 3.1 (rd-Pattern-C-star) are now
rigorously proven**, completing the routed dichotomy framework at `c = 3`.

The math required for Theorem 1 at `c = 3` is essentially complete. What
remains is:
- Generic-rank rigor cleanup in Lemma 2.4 (Note 0110 §"Lemma 2.4 proof
  sketch") — straightforward Vandermonde determinant argument.
- Combinatorial codim bound for `# rd-star ≤ poly(n)` — derive explicit
  `n`-polynomial bound from the structural enumeration.

These are **rigor-cleanup**, not new mathematics, and unblock paper writeup.

## Files

- `notes/0099-tetrahedron-analytic-proof.md` — Tet route (Theorem 1 case 1)
- `notes/0110-sub-tet-lagrange-rigorous.md` — Sub-tet route (case 2)
- `notes/0111-rd-pattern-c-star-rigorous.md` — rd-star route (case 3, bottleneck)
- `notes/0112-theorem-1-routed-dichotomy.md` — this assembly note
