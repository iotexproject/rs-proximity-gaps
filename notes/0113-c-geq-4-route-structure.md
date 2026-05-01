# Note 0113 — Route structure at c ≥ 4 (qualitative shift from c = 3)

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Builds on**: Notes 0099, 0107–0112
**Status**: empirical catalog + structural observations; rigor at c ≥ 4 TODO
**Empirical scripts**: `op2_c4_routes_catalog.py`, `op2_c4_codim_per_route.py`

## Why c ≥ 4 needs a different treatment

At `c = 3, n = 12`: `m = T + 1 = 4 = w + 1`, so the **full tetrahedron**
fits in `m` supports. Tet route is non-empty and rigorous (Note 0099).
Sub-tet at `w' = w − 1 = 2` is GENERICALLY rank-FULL (formula
`max{0, (w'−1)(c−1) − 2(w−w')} = max{0, 0} = 0`); rd happens only via
extras-collision (Note 0110). The bottleneck is rd-Pattern-C-star (Note 0111).

At `c = 4, n = 16`: `m = T + 1 = 4`, but `w + 1 = 5 > m`. **Tet route is
EMPTY**. Sub-tet at `w' = 3` has `m' = w' + 1 = 4 = m`, so the entire
m-tuple is the sub-tet (no "extras" supports outside the sub-tet). The
generic dim is
```
dim X_γ_sub  =  (w'−1)(c−1) − 2(w−w')  =  2·3 − 2·1  =  4.
```
That is, **sub-tet at c = 4 w' = 3 is GENERICALLY rd with kernel dim 4** —
not a special degeneration but the typical case.

This is a qualitative shift from c = 3.

## Empirical catalog at c = 4 (op2_c4_routes_catalog.py)

50,000 random `(E, γ)` trials at `n = 16, c = 4, p = 97` produced **521
bad configurations** (≈1 %). Classification:

| Class                                         | Count | Example          |
|-----------------------------------------------|-------|------------------|
| sub-tet, n_shared=6, topo=other-(3,2,2,1), rd | 161   | (sub-tet w'=3)   |
| sub-tet, n_shared=5, triangle+iso, rd         | 120   | (sub-tet w'=3)   |
| sub-tet, n_shared=7, (3,3,2,2), rd            | 36    |                  |
| sub-tet, n_shared=5, (3,2,2,1), rd            | 31    |                  |
| sub-tet, n_shared=4, triangle+iso, rd         | 26    |                  |
| sub-tet, n_shared=4, (3,2,2,1), non-rd        | 24    | (rare — non-rd!) |
| **non-sub-tet, n_shared=4, path, non-rd**     | 17    | (Pattern X analog) |
| non-sub-tet, n_shared=5, (2,2,2,2), non-rd    | 14    |                  |
| ... (smaller classes)                         | 92    |                  |
| TOTAL                                         | 521   |                  |

Of 521 bad configs: **~84% have sub-tet structure**, ~16% don't. Of the
non-sub-tet, only 2 are rd (both star-topology with n_shared=4 — the
"Pattern X analog at c=4 with one extra-share-pair").

## Per-config codim (op2_c4_codim_per_route.py)

Per-config rank deficit:
- **ker dim 1** (codim 11): "shallow rd" — most rd routes
- **ker dim 2** (codim 10): "medium rd" — triangle+iso, (3,3,3,3) topologies
- **ker dim 3** (codim 9): "deep rd" — n_shared=0, K_4 topology
  (very rare structural pattern)

Target codim `2D − T − 2 = 11`. The empirical bound (Note 0103) approaches
codim 11 at large p, so the rare "ker dim ≥ 2" routes must have **#config
counts compensating** — they're combinatorially limited.

## Structural observations

### 1. Tet emptiness at c ≥ 4 m ≤ w

For codimension excess `c` and decoding parameter `T = ⌊(2D−1)/c⌋`,
`m = T + 1`. Full tet requires `w + 1 ≤ m`. We have:
```
w + 1 ≤ m   ⇔   D − c + 1 ≤ ⌊(2D−1)/c⌋ + 1
              ⇔   D − c ≤ ⌊(2D−1)/c⌋.
```
At `c = 3, D = 6`: `3 ≤ 3`. Boundary, tet fits exactly.
At `c = 3, D = 9`: `6 ≤ 5`. Tet does NOT fit at `n = 18`.
At `c = 4, D = 8`: `4 ≤ 3`. Tet does NOT fit. ✓
At `c = 4, D = 12`: `8 ≤ 5`. Tet does NOT fit.

So **tet route is non-empty only at c ≤ 3** (for "round" `(n, k)` with
`D` not far above `3c − 3`). For larger `c` or large `D`, tet route is
empty and sub-tet is the only structural starting point.

### 2. Sub-tet generic rd at c ≥ 4

The generic dim formula `max{0, (w'−1)(c−1) − 2(w−w')}` is positive
when `(w'−1)(c−1) > 2(w−w')`, i.e., `w' (c−1) − (c−1) > 2w − 2w'`,
i.e., `w'(c+1) > 2w + (c−1)`, i.e., `w' > (2w + c − 1) / (c + 1)`.

For `c = 3`: `w' > (2w + 2)/4 = (w+1)/2`. At `w = 3`: `w' > 2`, so only
`w' = 3` (full tet) gives positive generic dim.

For `c = 4`: `w' > (2w + 3)/5`. At `w = 4`: `w' > 11/5 = 2.2`, so `w' = 3`
gives positive generic dim ✓. (Also `w' = 4 = w` if it fit, but at m = 4
we can't have `m' = 5`.)

So the **regime where sub-tet is generically rd (X_γ_sub ≠ 0)** starts
at c = 4 (with w'=w−1) and persists for higher c. This means at c ≥ 4
the sub-tet route is dense and structured, not a sparse algebraic
degeneration as at c = 3.

### 3. Pattern C analog at c ≥ 4 is essentially absent

At c = 3, rd-Pattern-C-star (codim 7 = 2D − T − 2) was the unique
bottleneck. At c = 4 the rd-Pattern-C-star analog requires
**linear dependence of 3 polynomials of degree c−1 = 3 in F_p[x]_{<c}**,
i.e., rank `M < 3` for `M ∈ F_p^{c × 3} = F_p^{4 × 3}` whose columns
are the Π_{U_j} coefficients. This is a **codim-2 determinantal
variety** (4 simultaneous 3×3 minors must vanish), not codim 1.

Verified: 0 / 2000 randomly-sampled Pattern C stars at n = 16, c = 4,
p = 97 satisfy the all-minors-zero condition. (At c = 3: ~3.4 % of
stars satisfy det M = 0.)

So at c = 4 the rd-Pattern-C-star route is essentially absent under
the multiplicative-subgroup choice of L. **The bottleneck at c ≥ 4 is
elsewhere** — most likely sub-tet rd at w' = w − 1, but its codim
contribution requires careful analysis (Open Question §"sub-tet codim").

## Implications for Theorem 1 (c ≥ 4)

The c = 3 framework (4 routes: tet / sub-tet / rd-Pattern-C-star / generic)
**does not directly transfer**. The c ≥ 4 framework is:

- **Sub-tet route (PRIMARY)**: w' = w − 1 sub-tet always rd with dim 4.
  Codim of `V_tet_sub(V)` ≤ ?? — needs careful (γ-uniform) analysis.
- **Sub-tet at smaller w'**: w' < w−1, generically non-rd, contributes via
  extras-collision (Note 0110 §"Lemma 2.5").
- **Non-sub-tet bad**: ~16 % of bad configs, sparse and combinatorially
  limited.

### Sub-tet route codim at c = 4 w' = 3 m' = m = 4

Naive formula `T + 2c − 1 = 10` is **insufficient** (target 11).

Refined analysis: for a w' = 3 sub-tet at c = 4 with dim X_γ_sub = 4:
- Per (E, γ): ker A in (s_1, s_2)-space has dim 4. Density per (E, γ)
  realization: `p^{m + ker_dim - 2D} = p^{4 + 4 − 16} = p^{−8}`.
- # γ's giving rd: rd holds for ALL γ ∈ (F_p^*)^m (since dim X_γ_sub > 0
  uniformly). So no γ-codim factor.
- # E configs in this route: `O(C(n, w'+1) · n^{w−w'} · m!) = poly(n)`.

Total contribution: `poly(n) × p^{−8}`. Codim **8**, NOT 11.

But empirics show codim 11 is achieved. So the per-config density
formula `p^{m + ker_dim − 2D}` MUST be over-counting — the projection
γ ↔ (s_1, s_2) is NOT 1-to-1; there's a multiplicity factor.

**Open question**: what is the multiplicity factor for sub-tet w' = w − 1
at c ≥ 4? At c = 3 full tet: multiplicity is `p^{ker_dim − (w+1−m)}` —
or related to the dim V_tet formula `w + 1` from Note 0099.

For full tet at c = 3 m = w + 1: dim V_tet = m = 4, so |V_tet| = p^4.
`p^{m + ker_dim - 2D}` = p^{-4}. So multiplicity factor = p^{m + ker_dim - dim V_tet} = p^{4+4-4} = p^4.

For sub-tet at c = 4 w' = 3 m = 4: dim V_tet_sub = ?. If it equals
5 (matching the bound 2D - 11 = 5), the multiplicity factor is
p^{4 + 4 − 5} = p^3, giving density p^{-11} ✓.

So the open conjecture is: **dim V_tet_sub at c = 4 w' = 3 = 5**, NOT
the naive `m' = 4`.

### Conjecture (TODO verify)

At c ≥ 4 with w' = w − 1 sub-tet (m' = m = w' + 1 supports), the variety
`V_tet_sub(V; E_1, ..., E_{w'+1})` has dimension `T + 2 = w' + 2 = w + 1`.

Equivalently, codim `2D − (w + 1) = 2D − T − 2` (TIGHT).

This is the c ≥ 4 analog of Note 0099's `dim V_tet = w + 1` for full tet.

## Action items for Paper 3 path

1. **Verify dim V_tet_sub conjecture** at c = 4 by direct empirical
   density measurement (small p).
2. **Prove dim V_tet_sub = w + 1** rigorously for sub-tet at c ≥ 4.
   Likely via Lagrange-form reduction analogous to Note 0099 but
   adjusted for the w' < w sub-tet case (instead of full tet).
3. **Catalog non-sub-tet routes at c = 4** more completely; verify each
   contributes codim ≥ 11.
4. **Generalize Lemma 3.1 (rd-Pattern-C-star) to c ≥ 4**: at c = 4 the
   matrix is 6×6 (not 3×3); det-vanishing is still codim 1 but the
   contribution is non-bottleneck.
5. **Theorem 1 (c ≥ 4)**: assemble the above into a routed-dichotomy
   theorem with the same `2D − T − 2` codim bound.

Once 1–5 are done, Paper 3 has a complete and uniform Theorem at all
`c ≥ 3`.

## Files

- `notes/scripts/op2_c4_routes_catalog.py` — 521 bad configs at c=4 classified
- `notes/scripts/op2_c4_codim_per_route.py` — per-config ker dim & codim
- `notes/0099-tetrahedron-analytic-proof.md` — c=3 tet baseline
- `notes/0110-sub-tet-lagrange-rigorous.md` — sub-tet Lagrange + dim formula
- `notes/0111-rd-pattern-c-star-rigorous.md` — rd-star at c=3 (codim 7 TIGHT)
- `notes/0112-theorem-1-routed-dichotomy.md` — Theorem 1 statement at c=3
