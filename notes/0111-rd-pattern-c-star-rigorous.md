# Note 0111 — rd-Pattern-C-star analytic characterization (rigorous)

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Builds on**: Notes 0099, 0107–0110
**Status**: rigorous proof of Lemma 3.1 + closed form for the rd-locus
**Empirical scripts**: `op2_rd_star_deep.py`, `op2_rd_star_lagrange.py`

> ⚠️ **Correction (Note 0114, 2026-04-29)**: Lemma 3.1 (`rd ⇔ det M = 0`)
> is correct. The codim claim "rd-Pattern-C-star tightness at codim
> `2D − T − 2`" becomes moot because the **other** routes' codim
> contributions were overstated; the rd-Pattern-C-star route does NOT
> determine the V_bad codim bottleneck. See Note 0114.

## Headline result

**Theorem (Lemma 3.1)**: A Pattern C star configuration `(E_c; E_a, E_b, E_d)`
admits `dim X_γ ≥ 1` for all generic distinct `γ ∈ (F_p^*)^4` (the "rd-star"
condition) **if and only if**
```
Π_{U_a}(x), Π_{U_b}(x), Π_{U_d}(x)   are linearly dependent in F_p[x]_{<c},
```
where `U_j := E_j \ {v_j}` is the leaf-`j` extras (size `c - 1`) and `v_j` is
the unique vertex shared by leaf `j` with `E_c`.

Equivalently, `det M = 0` where `M ∈ F_p^{c × c}` is the matrix whose `j`-th
column is the coefficient vector of `Π_{U_j}(x)`.

When `det M = 0`, `dim X_γ = 1` (one-dim kernel) and the unique-up-to-scale
basis `(ĥ_c, ĥ_a, ĥ_b, ĥ_d)` of `X_γ` is given by:
```
ĥ_j(x)  =  α_j · Λ_{E_c}(x) / (x - L_{v_j})       for j ∈ {a, b, d}    (Lag)
ĥ_c(x)  =  − Σ_{leaf j} α_j · Π_{U_j}(x)                                (Cen)
```
where `(α_a, α_b, α_d)` spans `ker M` and (γ_j − γ_c) factors absorb to give
the kernel of `M` directly.

## Setup (Pattern C star)

A 4-tuple of size-`w` supports `(E_0, E_1, E_2, E_3) ⊂ [n]` is a **Pattern C
star** iff:

1. (Pattern C signature) pair intersections (sorted) = `(0,0,0,1,1,1)`,
   triple intersections all `0`, quad intersection `0`.
2. (Star intersection graph) one support `E_c` (the **central**) shares a
   single vertex with each of the other three (the **leaves** `E_a, E_b, E_d`),
   while the leaves are pairwise disjoint.

Notation: write `v_j` for the unique vertex shared by `E_c` and leaf `j`.
Then `E_c = {v_a, v_b, v_d}` (size `w` requires `w = 3` ⇒ `c = D - w = D - 3`,
so for `n = 12, k = 6` we have `D = 6, c = 3, w = 3`). Each leaf
`E_j = {v_j} ⊔ U_j` with `|U_j| = w - 1 = c - 1` and `U_j ⊂ [n] \ V` (since
star ensures the U_j's are disjoint from `V = E_c` and from each other).

## Two key polynomial identities

For `(ĥ_j) ∈ X_γ` define
```
P(x)  :=  Σ_{j=0}^{3} ĥ_j(x) Λ_{E_j}(x)            (= 0 by X_γ definition)
Q(x)  :=  Σ_{j=0}^{3} γ_j ĥ_j(x) Λ_{E_j}(x)        (= 0 by X_γ definition)
```
Form `R(x) := γ_c P(x) − Q(x) = − Σ_{j leaf}(γ_j − γ_c) ĥ_j Λ_{E_j}`. Since
`P = Q = 0`, we have `R = 0` as well.

`R` involves only the **leaves**.

## Lemma 3.1 (Forced zeros at central shared vertices)

**Claim**: For any `(ĥ_j) ∈ X_γ` with `γ_c, γ_a, γ_b, γ_d` distinct,
```
ĥ_j(L_{v_l})  =  0       for every leaf j and every l ≠ j (l also leaf).
```

### Proof

Fix a leaf index `l`. Evaluate `P(x)` and `R(x)` at `x = L_{v_l}`. Two
factorizations:
- `Λ_{E_c}(L_{v_l}) = 0` because `v_l ∈ E_c`.
- `Λ_{E_l}(L_{v_l}) = 0` because `v_l ∈ E_l`.
- For any other leaf `j ∉ {c, l}`: `v_l ∉ E_j` (star ⇒ leaves pairwise
  disjoint and `v_l ∉ U_j` since `U_j ⊂ [n] \ V`). So `Λ_{E_j}(L_{v_l}) ≠ 0`.

Hence `P(L_{v_l})` and `R(L_{v_l})` reduce to:
```
P :   Σ_{j leaf, j ≠ l} ĥ_j(L_{v_l}) Λ_{E_j}(L_{v_l})           = 0
R :   Σ_{j leaf, j ≠ l} (γ_j − γ_c) ĥ_j(L_{v_l}) Λ_{E_j}(L_{v_l}) = 0
```
This is a `2 × 2` linear system in the two unknowns
`x_j := ĥ_j(L_{v_l}) Λ_{E_j}(L_{v_l})` (for the two leaves j ≠ l). The
coefficient matrix is `[ [1,1], [γ_{j_1} − γ_c, γ_{j_2} − γ_c] ]`, with
determinant `γ_{j_2} − γ_{j_1} ≠ 0`. Hence `x_{j_1} = x_{j_2} = 0`, and
since `Λ_{E_j}(L_{v_l}) ≠ 0`, we get `ĥ_j(L_{v_l}) = 0` for both leaves `j ≠ l`. □

## Lemma 3.2 (Reduction to coefficient linear dependence)

By Lemma 3.1, each leaf `ĥ_j` (degree `< c = 3`) vanishes at the two
`L_{v_l}` for `l ≠ j` leaves. Hence
```
ĥ_j(x)  =  α_j · ∏_{l ≠ j, l leaf} (x − L_{v_l})
        =  α_j · Λ_{E_c}(x) / (x − L_{v_j})
```
for some `α_j ∈ F_p`.

Substituting into `P(x) = 0`:
```
ĥ_c Λ_{E_c} + Σ_{leaf j} α_j · ( Λ_{E_c} / (x − L_{v_j}) ) · (x − L_{v_j}) Π_{U_j}
= Λ_{E_c} ( ĥ_c + Σ_{leaf j} α_j Π_{U_j} ) = 0.
```
Since `Λ_{E_c} ≠ 0` as a polynomial,
```
ĥ_c(x)  =  − Σ_{leaf j} α_j Π_{U_j}(x).                         (Cen)
```

Substituting into `Q(x) = 0` and using (Cen):
```
γ_c ĥ_c + Σ_{leaf j} γ_j α_j Π_{U_j}
=  γ_c (−Σ α_j Π_{U_j}) + Σ γ_j α_j Π_{U_j}
=  Σ_{leaf j} (γ_j − γ_c) α_j Π_{U_j}(x)        =  0.            (Lin)
```

Equation (Lin) is a polynomial identity in `F_p[x]_{<c}`. □

## Lemma 3.3 (rd ⇔ linear dependence)

Define the `c × c` matrix `M` whose `j`-th column (for `j ∈ {a, b, d}`) holds
the coefficients of `Π_{U_j}(x)`.

**Claim**:
```
dim X_γ ≥ 1  for distinct γ_c, γ_a, γ_b, γ_d   ⇔   det M = 0.
```

### Proof

**(⇐)** Suppose `det M = 0`. Pick `(c_a, c_b, c_d)` ∈ `ker M^T` non-trivially,
i.e. `Σ c_j Π_{U_j} = 0`. Set `α_j := c_j / (γ_j − γ_c)` for each leaf `j`.
Then `Σ (γ_j − γ_c) α_j Π_{U_j} = Σ c_j Π_{U_j} = 0`, so (Lin) holds.
Define `ĥ_j` from the formulas (Lag) and (Cen). All `X_γ` constraints are
satisfied by construction. `(ĥ_j) ≠ 0` because at least one `α_j ≠ 0`.

**(⇒)** Suppose `(ĥ_j) ∈ X_γ` is non-trivial. By Lemma 3.2, `ĥ_j` has the form
(Lag) for leaves and (Cen) for the central. Substitute into (Lin). If
`det M ≠ 0`, the only solution to `Σ (γ_j − γ_c) α_j Π_{U_j} = 0` is
`(γ_j − γ_c) α_j = 0` for all `j`. Since `γ_j ≠ γ_c`, all `α_j = 0`, hence
all `ĥ_j_leaf = 0`, hence by (Cen) `ĥ_c = 0`, hence `(ĥ_j) = 0` —
contradiction. □

## dim X_γ formula (rd case)

When `det M = 0`, `dim ker M = 1` (generically — no further degeneracy),
so `dim X_γ = 1`. (If `M` has corank 2 or more, `dim X_γ` jumps.)

Empirically across 51 rd-stars, all had `dim X_γ = 1` (Counter at 30 random γ:
`{1: 30}` for each).

## Counting rd-stars (codim contribution to V_bad)

The matrix `M` has entries which are degree `≤ c − 1` polynomials in
`(L_u)_{u ∈ ⋃_j U_j}`. Hence `det M` is a polynomial of degree `≤ c(c-1) = 6`
in these `3(c-1) = 6` algebraic variables.

For fixed evaluation domain `(L_v)_{v ∈ [n]}` (the RS code's domain), the
condition `det M = 0` cuts out a **codim-1 subvariety** of the configuration
space `(E_c; U_a, U_b, U_d)`. The total count of rd-Pattern-C-star configs is
therefore at most:
```
# rd-star  ≤  (# Pattern C star configs) × (1 / Schwartz-Zippel-rate)
            =  poly(n).
```

Empirically at `n = 12, c = 3, p = 1009`:
- Pattern C star configurations: 394 (out of 4212 Pattern C, out of 22905 4-tuples)
- rd-star configurations: 51 (≈ 3.4% of stars)

(The 3.4% rate is finite-combinatorial — it is not `1/p` because `det M`
takes values in a small subset of `F_p` for the multiplicative-subgroup
choice of `L_v`. For a *generic* `L_v`, the rate would be `~1/p`. Either
way, `# rd-star ≤ poly(n)`.)

## Codim contribution

For each rd-star (E_c; E_a, E_b, E_d):
- `γ`-space: `(F_p^*)^m`, full (rank deficit holds for all γ), volume `≈ p^m`.
- For each `γ`, `ker A(γ)` has dim 1 in `(s_1, s_2)`-space, so `p` points.
- Total realizing `(s_1, s_2)`-set per config: `p^{m+1}`.
- Density per config: `p^{m + 1 − 2D}`.

For `n = 12, c = 3, m = 4, 2D = 12`: per-config density `p^{−7}`.

Total contribution to `V_bad` density: `# rd-star × p^{−7} = poly(n) × p^{−7}`.

This matches the **target codim `2D − T − 2 = 7` TIGHT**.

## Summary: routed dichotomy at n=12 c=3

| Route                | # configs    | density per config | contribution |
|----------------------|--------------|--------------------|--------------|
| Tetrahedron          | `C(12, 4) = 495` | `p^{−8}` (Note 0099) | `~p^{−8}` ≈ codim 8 |
| Sub-tet (Pattern A/B/D) | `O(n^{?})` poly | `p^{−8}` (Note 0110) | `~p^{−8}` |
| **rd-Pattern-C-star** | `≤ poly(n)`, det M = 0 | `p^{−7}` | `~p^{−7}` ≈ codim 7 |
| Generic Pattern C (non-rd) | `poly(n)` | `p^{−8}` (codim-1 V_rd in γ) | `~p^{−8}` |

**Min over routes = `p^{−7}` ↔ codim 7 = `2D − T − 2` TIGHT.**

The bottleneck is rd-Pattern-C-star, and Lemma 3.1–3.3 give a **rigorous and
explicit** algebraic characterization of this route as the codim-1 subvariety
`{det M = 0}` of star configurations.

## Verification (op2_rd_star_lagrange.py)

```
Stars sampled: 1500
Quadrant counts (det==0?, rd?):
  det != 0, rd = NO  : 1449  (generic stars)
  det != 0, rd = YES :    0  (★ no false positives)
  det == 0, rd = NO  :    0  (★ no false negatives)
  det == 0, rd = YES :   51  (rd-stars)
```
**100% of 1500 sampled stars match the ⇔ characterization.**

Basis-vector predicted form (Lag) was also verified on 3 explicit rd-stars:
each leaf `ĥ_j` matches `α_j · Λ_{E_c} / (x − L_{v_j})` for some `α_j ∈ F_p^*`.

## Open items

1. **Pattern C non-star** (path / triangle+iso topologies): Lemma 3.1 used
   the star structure crucially (forced zeros at shared vertices). For
   non-star Pattern C, the V_rd in γ-space has codim ≥ 1 (det A(γ) is
   non-zero polynomial in γ of degree ≤ mc), giving codim 8 contribution
   that's *better* than star. ✓ no bottleneck issue.

2. **`c ≥ 4` analog**: Pattern C star at `c=4` has leaves of size `c=4`
   sharing 1 vertex with `E_c`. The matrix `M` becomes `c × c` (`= 4 × 4`).
   Linear dependence of `Π_{U_j}` (degree `c − 1 = 3`, so 4 coefficients)
   is again a single algebraic condition. Generalizes verbatim, but at
   `c=4` non-tet bad has multiple sub-patterns (Note 0109 §"Routed
   dichotomy at c=4") and rd-star may not be the unique bottleneck.

3. **Theorem 1 assembly**: combine Notes 0099 (tet), 0110 (sub-tet), 0111
   (rd-star) into a single routed-dichotomy theorem statement and write
   the bookkeeping cleanly.

## Files

- `notes/scripts/op2_rd_star_deep.py` — basis-vector structure observation
- `notes/scripts/op2_rd_star_lagrange.py` — det M ⇔ rd verification
- `notes/0099-tetrahedron-analytic-proof.md` — full-tet route
- `notes/0110-sub-tet-lagrange-rigorous.md` — sub-tet route
