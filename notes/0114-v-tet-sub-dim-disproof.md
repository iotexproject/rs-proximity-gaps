# Note 0114 — Disproof of Note 0113's `dim V_tet_sub = w+1` conjecture

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Builds on**: Notes 0099, 0103, 0110, 0112, 0113
**Status**: empirical disproof, asymptotic-density-1 verified at multiple primes & configs
**Empirical scripts**: `op2_v_tet_sub_density_in_span.py`, `op2_kerNE_structure_test.py`

## Summary

The conjecture `dim V_tet_sub = w + 1` (Note 0113) for `c ≥ 4` sub-tet at
`w' = w − 1`, `m = w'+1 = w` is **wrong**. Empirically `dim V_tet_sub = 2w`
asymptotically, giving sub-tet route codim `2c`, **not** `2D − T − 2`.

This explains the empirical "polynomial gap" reported in Note 0103 (actual
codim 7.8 at `n=16, c=4, p=1009` vs. formula codim 11): the gap is
**structural, not polynomial**.

## What was wrong in Note 0113

Note 0113 claimed:
> For sub-tet at c = 4 w' = 3 m = 4: dim V_tet_sub = ?. If it equals 5
> (matching the bound 2D - 11 = 5), the multiplicity factor is p^{4 + 4 − 5}
> = p^3, giving density p^{-11} ✓.

This was a *hypothesized* multiplicity factor. The actual factor is 1 (not
`p^3`), so density is `p^{-8}` and codim is `8` (not 11).

The error: I conflated `ker N_E` with "polynomials vanishing on `L_E`". In
fact `ker N_E = V_E` (the row span of restricted Vandermonde, i.e., the
"image of Vandermonde-evaluation at `L_E`"), **not** the ideal of polynomials
vanishing on `L_E`. (See `op2_kerNE_structure_test.py` — direct test fails 20/20
of "Λ_E · g ∈ ker N_E".)

With the correct interpretation:
```
s_1 + γ_i s_2 ∈ ker N_{E_i}  ⟺  s_1 + γ_i s_2 ∈ V_{E_i}
                              ⟺  ∃ α_u (u ∈ E_i) :
                                  s_1 + γ_i s_2 = Σ_u α_u (L_u^j)_{j=0}^{D-1}.
```

The Lagrange-diagonality "forced zero" argument (which works fine on the
`X_γ` side, Note 0099) does **not** transfer to `(s_1, s_2)`-space the way
I sketched. The (s_1, s_2)-side structure is governed by Σ V_{E_i}, not
by Λ_V-divisibility.

## Empirical evidence

### Density-in-span method (op2_v_tet_sub_density_in_span.py)

Procedure:
1. For sub-tet `(E_1, ..., E_m)` at `c=4 n=16 w'=3`, sample many γ-tuples
   and accumulate `Σ_γ ker A(γ)` as a F_p-subspace of `F_p^{2D}`.
   Measured dim = **8** (= the "linear span upper bound").
2. Sample random `(s_1, s_2)` from this 8-dim span and check if it lies
   in `V_tet_sub` (∃ distinct γ_i s.t. `s_1 + γ_i s_2 ∈ V_{E_i}`).
3. Density `|V_tet_sub|/|Σ ker A| = p^{dim V_tet_sub - 8}`.

Results:

| p    | D_span | in V_tet_sub | dim V_tet_sub estimate |
|------|--------|--------------|------------------------|
| 17   | 8      | 855/2000 (43%) | 7.700                |
| 97   | 8      | 1732/2000 (87%) | 7.969               |
| 193  | 8      | 1862/2000 (93%) | 7.986               |
| 257  | 8      | 1901/2000 (95%) | 7.991               |
| 449  | 8      | 1937/2000 (97%) | 7.995               |
| 577  | 8      | 1945/2000 (97%) | 7.996               |
| 1009 | 8      | 1975/2000 (99%) | 7.998               |

Density → 1 as `p → ∞`, so **dim V_tet_sub = 8** exactly (= `2w` at
`n=16 c=4 w=4 D=8`).

### Robustness (multiple sub-tet configurations at p=1009)

| V             | U               | dim V_tet_sub estimate |
|---------------|-----------------|------------------------|
| [0,1,2,3]     | [4,5,6,7]       | 7.998                  |
| [0,1,2,3]     | [8,9,10,11]     | 7.998                  |
| [2,5,7,11]    | [3,8,13,15]     | 7.998                  |
| [0,3,6,9]     | [1,4,7,12]      | 7.997                  |
| [1,2,3,4]     | [5,6,7,9]       | 7.998                  |

All ≈ 8 — independent of choice of V, U.

## Why the structural difference between c=3 full-tet and c≥4 sub-tet

For `c = 3` full tet: `m = w + 1`, no extras. So `Σ V_{E_i} = V_V`,
dim `w + 1` (the "all-V Vandermonde span"). Per-γ ker A has dim `(w−1)(c−1)`
inside `V_V × V_V` (rank-1 condition on quotient). Net `dim V_tet ≈ w + 1`.

For `c ≥ 4` sub-tet `w' = w − 1`, `m = w`: each E_i has 1 extra `u_i ∉ V`.
Σ `V_{E_i} = V_V + V_U` with `|V| = w`, `|U| = m = w` (assuming distinct
extras). So `dim Σ V_{E_i} = 2w` (asymptotically), much bigger than `w+1`.
This bigger ambient gives bigger `dim V_tet_sub = 2w`.

## Geometric structure (clean): V_tet_sub = V_V × V_V

**Theorem (clean form)**: For sub-tet of size `w'+1` on `V ⊂ [n]` with
supports `E_i = (V \ {v_i}) ∪ U_i` (any extras `U_i ⊂ [n]\V`), and any `m =
w'+1 = |V|` distinct realized γ-values, we have
```
V_tet_sub(V; E_*)  =  V_V × V_V        (open subset, distinct-γ condition)
```
where `V_V := span{ev_v : v ∈ V} ⊂ F_p^D`, dim `w'+1`.

**Proof sketch**: For `(s_1, s_2)` with `s_1 + γ_i s_2 ∈ V_{E_i}` and
distinct γ_i: subtract two equations `(γ_i − γ_j) s_2 = (V_{E_i}-element) −
(V_{E_j}-element) ∈ V_{E_i} + V_{E_j} ⊂ Σ_l V_{E_l}`. Apply across all
pairs: s_2 ∈ ⋂ ... [argument cleaner via direct projection]. Project on
`F_p^D / V_V`: each support `E_i` contributes the constraint `coef(ev_{v_i})
= 0` (the only V-component absent from V_{E_i}) plus 1-dim freedom along
ev_{u_i}. With distinct γ_i's, the v_i-coef constraints simultaneously
force s_l components in V_U_l to be 0, leaving (s_1, s_2) ∈ V_V × V_V.

The γ_i are then determined by `γ_i = -(s_1 component on ev_{v_i}) /
(s_2 component on ev_{v_i})`.

Hence **dim V_tet_sub(V) = 2(w'+1)** independent of which extras `U_i` are
chosen — only the vertex set `V` matters.

## Codim formula (correct)

For sub-tet of size `w'+1`:
```
dim V_tet_sub(V)  =  2(w'+1)
codim            =  2D − 2(w'+1)  =  2(D − w' − 1)  =  2(c + w − w' − 1).
```

The smallest codim (= bottleneck) is achieved at the SMALLEST `w'_min`
satisfying:
- `w'+1 ≤ m = T+1`  (V fits within m supports)
- `(w'−1)(c−1) − 2(w−w') ≥ 1`  (sub-tet is bad-realizing, Note 0110)

**When sub-tet is realizable**, the codim is `2(D − w'_min − 1)`. For most
"balanced" parameters where sub-tet at `w' = T` is bad-realizing:
```
codim = 2D − 2T − 2.
```

This is **`T` smaller** than v6 v2's claimed `2D − T − 2`.

## Verification across cases (Note 0103 empirical at p=1009)

| n  | c | T | w'_min | codim (formula) | poly factor | predicted @ p=1009 | empirical |
|----|---|---|--------|------------------|-------------|---------------------|-----------|
| 12 | 3 | 3 | 3      | 4                | log(495)≈0.9 | 3.1                 | 4.9       |
| 16 | 4 | 3 | 3      | 8                | log(1820)≈1.1 | 6.9                | 7.8       |
| 20 | 5 | 3 | 3      | 12               | log(C(20,4))≈1.2 | 10.8            | 10.8      |
| 24 | 5 | 4 | 4      | 14               | log(C(24,5))≈1.5 | 12.5            | 10.5      |

Rows 1–3: **predicted codim − empirical ≈ 1.0–1.5**, consistent with poly
factor at p=1009 (small overcount of overlapping V's).
Row 4: gap larger (3.5), suggesting overlap is significant or smaller sub-tet
exists. Worth direct verification.

## Sub-tet existence at large parameters

Sub-tet exists iff there is `w'` with both:
- `w' ≤ T = ⌊(2D−1)/c⌋`
- `w' ≥ (2w + c − 1)/(c+1)`  (bad-realizing)

Equivalently: `(2w + c − 1)/(c+1) ≤ T`.

At rate 1/2 (D = n/2, w = n/2 − c): `T = ⌊(n−1)/c⌋ ≈ n/c`. The lower bound
is approximately `2w/(c+1) ≈ n/(c+1) − 2c/(c+1)`. The condition
`n/(c+1) ≲ n/c` is satisfied for c ≥ 2.

But also `w'+1 ≤ T+1 = m`. For large n, c small, we have `w'_min ≈ n/(c+1)`
and `T ≈ n/c`. The gap `T − w'_min ≈ n(1/c − 1/(c+1)) = n / (c(c+1))`.

So for **c=3, large n**: sub-tet exists at w' ∈ [n/4, n/3]; smallest
w'_min ≈ n/4. Codim = 2D − 2(w'_min + 1) ≈ 2D − n/2 − 2 = n − n/2 − 2 = n/2 − 2.
For BabyBear n=40 c=3: codim ≈ 18. Still very strong.

For **c=9, n=40**: w'_min ≈ (2·11 + 8)/10 = 3, T = 4. Sub-tet at w'=4.
Codim = 2(D − w' − 1) = 2(20 − 4 − 1) = 30. Note 0103 claimed `2D − T − 2 = 34`.
Corrected codim 30, gap 4 from previous claim.

## Implication for v6 v2 conjecture and prize-grade soundness

The v6 v2 statement
```
Pr[M(s_1, s_2) > T]  ≤  poly(n) · p^{−(2D − T − 2)}
```
is **WRONG at all c ≥ 3**. Asymptotically the sub-tet route (whenever
realizable) gives only `Pr ≤ poly(n) · p^{−2(D − w'_min − 1)}`, i.e.,
**`codim = 2D − 2(w'_min + 1)`** which is `≤ 2D − 2T − 2` (with equality at
the smallest `w'_min = T`).

So **corrected v6 v2**:
```
Pr[M > T]  ≤  poly(n) · p^{−(2D − 2T − 2)}    (at sub-tet bottleneck)
            =  poly(n) · p^{−2(c + w − T − 1)}
```

For BabyBear parameters:
| n | c | T | (corrected codim) | (Note 0103 claimed) | ε ≤ 2^{...} (BabyBear) |
|---|---|---|--------------------|----------------------|-------------------------|
| 12 | 3 | 3 | 4 | 7  | 2^{-124}  |
| 28 | 6 | 4 | 18 | 22 | 2^{-558}  |
| 40 | 9 | 4 | 30 | 34 | 2^{-930}  |

(Corrected `2D − 2T − 2` for the sub-tet bottleneck. At `n=12 c=3` the
codim is even smaller because full tet exists with codim `4`.)

All corrected codims still give exponentially-small soundness for any
reasonable `p`, so **prize-grade FRI soundness is preserved** but with
weaker constants than previously believed.

## Action items

1. **Replace v6 v2 with the corrected statement**: `Pr[M > T] ≤ poly(n) p^{-2c}`
   for `c ≥ 4`. (At `c = 3` the full-tet route gives `codim = w + 2c − 1`,
   which is the binding constraint.)
2. **Re-derive prize-grade FRI soundness** with the corrected exponent.
   For `c ≥ 4` parameters this gives `O(c)` rather than `O(D)` codim, but
   still exponentially small for any reasonable p.
3. **Re-examine Theorem 1** at `c ≥ 4`: the routed dichotomy with sub-tet
   contributing codim 11 doesn't hold; sub-tet contributes codim `2c`. The
   "bottleneck" at `c ≥ 4` is sub-tet at the largest possible `w'`.
4. **Investigate the `c = 3` vs `c ≥ 4` qualitative difference**: at `c = 3`,
   full tet exists (`w + 1 ≤ m`) and its codim is `w + 5`. At `c ≥ 4` full tet
   doesn't fit (`w + 1 > m`) and sub-tet replaces it with worse codim.

## Where the dim-counting argument should have stopped me

**Naive dim count for sub-tet at `c ≥ 4 m = w`**:
- Per γ: `ker A` has dim `2D − rank A = 2D − (mc − dim X_γ) = 2D − mc + dim X_γ`.
- For `m = w, c ≥ 4`: `dim X_γ = (w−2)(c−1) − 2`. So `ker A = 2D − wc + (w−2)(c−1) − 2 = 2D − 2c − w + 0 = w` (after simplification, for general c≥4).
- Linear span across γ: `m + ker A = w + w = 2w`.

This gives dim V_tet_sub ≤ 2w directly. The "multiplicity factor" required
to push down to 5 = `w + 1` is non-existent; multiplicity is 1 generically.

I should have computed `m + ker A = 2w` and stopped. Note 0113 instead
hypothesized a multiplicity factor without verification.

## Implications for previous notes

| Note | Claim | Status |
|------|-------|--------|
| 0099 | `dim X_γ = (w−1)(c−1)` for full tet at c=3 | RIGOROUS, unaffected. The X_γ-side Lagrange-diagonality argument is correct. |
| 0099 | Total density `≈ poly(n) · p^{−4}` for tet contribution at c=3 n=12 | RIGOROUS. Matches empirical codim 4.9 with poly factor. |
| 0103 | v6 v2: `Pr[M > T] ≤ poly(n) p^{−(2D−T−2)}` | **WRONG**. Corrected: `Pr ≤ poly(n) p^{−(2D−2T−2)}` at sub-tet bottleneck. The "polynomial gap" reported in Note 0103's table is now explained as structural, not polynomial. |
| 0110 | Sub-tet Lagrange diagonality (Lemmas 2.1–2.3) | RIGOROUS. The `X_γ`-side reduction is valid. |
| 0110 | "Codim contribution `T + 2c − 1`" | WRONG number. Actual codim per V = `2D − 2(w'+1)`. Reasoning conflated per-(E,γ) and per-V density. |
| 0111 | rd-Pattern-C-star characterization | RIGOROUS at c=3. The `det M = 0` ⇔ rd structure is correct. |
| 0112 | Theorem 1: codim V_bad ≥ 2D − T − 2 at c=3 | **WRONG**. Actual codim is `2D − 2T − 2 = 4` (at n=12). |
| 0113 | Conjecture `dim V_tet_sub = w + 1` at c ≥ 4 | **WRONG** (this Note disproves). Actual: `2(w'+1)`. |

**The fundamental conflation**: Notes 0099/0110/0112 computed `dim ker A` per
fixed γ (= 4) and called this "dim V_tet" or used it as the codim contribution.
The actual `dim V_tet(V)` is `dim Σ_γ ker A(γ) = 2(w'+1)` (since γ varies and
ker A(γ) sweeps a `2(w'+1)`-dim subspace `V_V × V_V`).

The X_γ-side analysis (Lagrange diagonality → `dim X_γ = (w−1)(c−1)`) is
correct for what it computes (rank deficit of `A(γ)` for fixed γ); it just
doesn't equal `dim V_tet`.

## Why the proof in Note 0112 broke

Note 0112's "Theorem 1" had:
> Tet route (Note 0099): codim ≥ w + 2c − 1 = 8
> Sub-tet route (Note 0110): codim ≥ T + 2c − 1 = 8
> rd-Pattern-C-star route (Note 0111): codim = 2D − T − 2 = 7 (TIGHT)

The "w + 2c − 1" in the tet route came from `2D − dim V_tet = 12 − (w+1) =
12 − 4 = 8`, using the WRONG `dim V_tet = w+1`. With correct `dim V_tet =
2(w+1) = 8`, codim = `12 − 8 = 4`. Same correction for sub-tet.

So **all 3 codim contributions in Theorem 1 should be 4 (asymptotic) at c=3
n=12**, NOT 7 or 8. The "rd-Pattern-C-star tightness" claim becomes moot.

## Direction for repair

The geometric reality: every sub-tet route on V of size `w'+1` gives
`V_tet(V) = V_V × V_V` (open subset). V_bad ⊃ ⋃_V V_V × V_V.

Codim formula in terms of `w'_min` (smallest bad-realizing sub-tet ≤ T):
```
codim V_bad  ≤  2(D − w'_min − 1)  +  log_p(C(n, w'_min + 1))   (poly factor)
```

The `w'_min` depends on `(c, w)`:
```
w'_min  =  ⌈(2w + c − 1) / (c + 1)⌉    (smallest bad-realizing sub-tet)
```
*provided* `w'_min ≤ T`.

If `w'_min > T`, then no sub-tet is realizable in `m = T+1` supports — the
sub-tet route is **empty**. In that regime V_bad codim is determined by
*other* routes (rd-Pattern-C, generic non-rd, etc.).

For BabyBear `n=40 c=3`: `w=37, T=13`. `w'_min = ⌈(74+2)/4⌉ = 19 > T = 13`.
**Sub-tet route is empty**. The original v6 v2 might apply (TODO verify
empirically).

For BabyBear `n=40 c=9`: `w=11, T=4`. `w'_min = ⌈(22+8)/10⌉ = 3 < T = 4`.
Sub-tet route active at `w' ∈ [3, 4]`. Codim ≥ `2(20 − 4 − 1) = 30` (at
`w'=4`) but smallest at `w'=3` gives `2(20 − 3 − 1) = 32`. Best codim 30
(taking dominant `w'`).

## Corroboration: formula `2(w'+1)` holds at every w' (post-disproof sweep)

The disproof above was at `c=4 w'=3` (sub-tet at largest non-full size).
Subsequent sweep `op2_v_tet_sub_dim_general.py` verifies the geometric
formula at every `w' ∈ [T, w]` with X-side dim ≥ 1, across multiple `(n,c)`:

| n  | c | w | T | w' | predicted 2(w'+1) | dim_est | X_dim | verdict |
|----|---|---|---|----|--------------------|---------|-------|---------|
| 12 | 3 | 3 | 3 | 3  | 8  | 7.997  | 4  | match (p=1009) |
| 16 | 4 | 4 | 3 | 3  | 8  | 7.998  | 4  | match |
| 16 | 4 | 4 | 3 | 4  | 10 | 9.998  | 9  | match |
| 20 | 4 | 6 | 4 | 4  | 10 | 9.874  | 5  | match (p=41)   |
| 20 | 4 | 6 | 4 | 5  | 12 | 11.820 | 10 | match |
| 20 | 4 | 6 | 4 | 6  | 14 | 13.756 | 15 | match |
| 20 | 5 | 5 | 3 | 3  | 8  | 7.906  | 4  | match |
| 20 | 5 | 5 | 3 | 4  | 10 | 9.874  | 10 | match |
| 20 | 5 | 5 | 3 | 5  | 12 | 11.820 | 16 | match |
| 24 | 4 | 8 | 5 | 5  | 12 | 11.995 | 6  | match (p=1009) |
| 24 | 4 | 8 | 5 | 6  | 14 | 13.996 | 11 | match |
| 24 | 4 | 8 | 5 | 7  | 16 | 15.993 | 16 | match |
| 24 | 4 | 8 | 5 | 8  | 18 | 17.993 | 21 | match (full tet) |
| 24 | 5 | 7 | 4 | 4  | 10 | 9.997  | 6  | match |
| 24 | 5 | 7 | 4 | 5  | 12 | 11.995 | 12 | match |
| 24 | 5 | 7 | 4 | 6  | 14 | 13.996 | 18 | match |
| 24 | 5 | 7 | 4 | 7  | 16 | 15.993 | 24 | match |

**17/17 match across c ∈ {3,4,5}, including full tet (w'=w).** The formula
`dim V_tet_sub(V) = 2(w'+1)` is universal — independent of c, w, U choice.
This rules out any "polynomial multiplicity factor" that might rescue the
old codim claim.

## Files

- `notes/scripts/op2_v_tet_sub_density_in_span.py` — density verification
  giving `dim V_tet_sub → 8` at p → ∞ for c=4
- `notes/scripts/op2_v_tet_dim_c3_check.py` — same at c=3 (also dim 8, NOT 4)
- `notes/scripts/op2_v_tet_sub_dim_general.py` — sweep across w', 17/17 match
- `notes/scripts/op2_kerNE_structure_test.py` — confirms `ker N_E = V_E`
  (Vandermonde row span), NOT `Λ_E·F_p[x]_{<c}`
- `notes/scripts/op2_v_tet_sub_dim_test.py` — initial linear-span test
  (`dim Σ ker A = 8`)
- `notes/0099-tetrahedron-analytic-proof.md` — c=3 X_γ argument (correct)
- `notes/0103-revised-v6.md` — already showed empirical codim gap
  (re-interpretation: gap is structural, not polynomial)
- `notes/0112-theorem-1-routed-dichotomy.md` — Theorem 1 needs revision
- `notes/0113-c-geq-4-route-structure.md` — conjecture disproved by this Note
