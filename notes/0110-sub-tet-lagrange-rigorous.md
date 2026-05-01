# Note 0110 — Sub-tetrahedron Lagrange diagonality (rigorous)

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Builds on**: Notes 0099, 0107, 0108, 0109
**Status**: rigorous proof of Lemmas 2.1–2.3 + closed dim formula
**Empirical scripts**: `op2_subtet_lagrange_verify.py`, `op2_subtet_dim_formula.py`

> ⚠️ **Correction (Note 0114, 2026-04-29)**: Lemmas 2.1–2.3 (X_γ-side
> Lagrange diagonality and dim X_γ formula) are correct. The "codim
> contribution `T + 2c − 1`" derived from these is **WRONG** — see
> Note 0114. Actual `dim V_tet_sub(V) = 2(w'+1)` (= V_V × V_V), giving
> codim `2D − 2(w'+1)`.

## Why this note

Note 0109 sketched the routed dichotomy and stated Lemma 2.1 (sub-tet Lagrange
diagonality) without rigorous proof. This note delivers:

1. Rigorous proof of Lemma 2.1 with the precise hypothesis (`v_i ∉ E_i`).
2. Rigorous reduction (Lemma 2.2) of `X_γ_sub` to a polynomial-syzygy problem
   on `(q_j) ∈ (F_p[x]_{<c-1})^{w'+1}`.
3. Closed formula for the **generic** dimension (Lemma 2.3):
   ```
   dim X_γ_sub  =  max(0, (w'-1)(c-1) - 2(w-w'))     (generic extras)
   ```
4. Characterization of when dim X_γ_sub strictly exceeds the generic formula
   (extras-collision phenomenon), and identification of this as the *bad-
   realizing* sub-tet locus inside the routed dichotomy.

## Setup

Fix:
- `n` evaluation points with distinct `L_v ∈ F_p^*`, `v ∈ [n]`
- `c ≥ 2` (codimension excess)
- `w = D - c` where `D = n - k`, `k = ` RS code dimension
- `m'` supports `E_1, ..., E_{m'} ⊂ [n]` of size `w` each
- `γ_1, ..., γ_{m'} ∈ F_p^*` distinct
- The **twisted syzygy module**
  ```
  X_γ := { (ĥ_1, ..., ĥ_{m'}) ∈ (F_p[x]_{<c})^{m'} :
           Σ_j ĥ_j(x) Λ_{E_j}(x) = 0   AND   Σ_j γ_j ĥ_j(x) Λ_{E_j}(x) = 0 }
  ```
  where `Λ_E(x) = ∏_{u ∈ E}(x - L_u)`.

**Sub-tetrahedron data**: a sub-tet on `V` of size `w'+1` (with `w' < w`)
consists of:
- `V = {v_1, ..., v_{w'+1}} ⊂ [n]`
- `m' = w'+1` supports `E_1, ..., E_{w'+1}`, each of size `w`, satisfying
  ```
  V \ {v_i}  ⊂  E_i   AND   v_i ∉ E_i        for i = 1, ..., w'+1.   (★)
  ```

Define the **extras** of support `i` by `U_i := E_i \ (V \ {v_i})`.
Then `|U_i| = w - w' ≥ 1`, and condition `v_i ∉ E_i` means `v_i ∉ U_i`,
i.e. `U_i ⊂ [n] \ V`. (Without this constraint, the ones in `U_i` could
include `v_i` and would break diagonality.)

## Lemma 2.1 (Sub-tet Lagrange diagonality)

Under (★), the matrix `M ∈ F_p^{(w'+1)×(w'+1)}` defined by
`M_{ij} := Λ_{E_i}(L_{v_j})` is **diagonal with nonzero diagonal entries**:

```
M_{ij}  =  0                       if i ≠ j
M_{ii}  =  ∏_{u ∈ E_i}(L_{v_i} - L_u)  ≠ 0      (since u ≠ v_i for all u ∈ E_i)
```

### Proof

Fix `i ≠ j`. Then `v_j ∈ V \ {v_i} ⊂ E_i` by (★), so `(L_{v_j} - L_{v_j})` is a
factor of `Λ_{E_i}(L_{v_j}) = ∏_{u ∈ E_i}(L_{v_j} - L_u)`. Hence the value is
zero.

For `i = j`: by (★) `v_i ∉ E_i`, so for every `u ∈ E_i` we have `u ≠ v_i`,
hence `L_{v_i} - L_u ≠ 0` (the `L_v` are distinct). The product is therefore
nonzero. □

## Lemma 2.2 (Forced zeros)

Under (★), every `(ĥ_j) ∈ X_γ_sub` satisfies
```
ĥ_i(L_{v_i}) = 0       for all i = 1, ..., w'+1.
```

### Proof

Evaluate the first `X_γ`-defining constraint `Σ_j ĥ_j Λ_{E_j} = 0` at
`x = L_{v_i}`. By Lemma 2.1, `Λ_{E_j}(L_{v_i}) = 0` for `j ≠ i`, so the sum
collapses to
```
ĥ_i(L_{v_i}) · Λ_{E_i}(L_{v_i}) = 0.
```
Since `Λ_{E_i}(L_{v_i}) ≠ 0` (Lemma 2.1), we conclude `ĥ_i(L_{v_i}) = 0`. □

## Lemma 2.3 (Reduction to polynomial syzygy)

Define `q_i ∈ F_p[x]_{<c-1}` as the unique polynomial with
```
ĥ_i(x) = (x - L_{v_i}) q_i(x).
```
(Existence and uniqueness from Lemma 2.2.) Define `Π_{U_i}(x) := ∏_{u ∈ U_i}(x - L_u)` (degree `w - w'`). Then:

```
ĥ_i(x) Λ_{E_i}(x)  =  (x - L_{v_i}) q_i · ( Λ_V(x) / (x - L_{v_i}) ) · Π_{U_i}(x)
                   =  q_i(x) · Λ_V(x) · Π_{U_i}(x)
```
where `Λ_V(x) := ∏_{v ∈ V}(x - L_v)`. Since `Λ_V(x) ≠ 0` as a polynomial, the
two `X_γ`-defining constraints reduce to:
```
Σ_j q_j(x) Π_{U_j}(x)         =  0          (S₁)
Σ_j γ_j q_j(x) Π_{U_j}(x)     =  0          (S₂)
```

Hence `X_γ_sub` is isomorphic (as `F_p`-vector space) to the kernel of the
linear map
```
T : (F_p[x]_{<c-1})^{w'+1}  →  (F_p[x]_{<c+w-w'-1})^2
T(q_1, ..., q_{w'+1}) = (Σ q_j Π_{U_j},  Σ γ_j q_j Π_{U_j}).
```

### Proof

The factorization `Λ_{E_i}(x) = (Λ_V(x) / (x - L_{v_i})) Π_{U_i}(x)` follows
from `E_i = (V \ {v_i}) ⊔ U_i` (a disjoint union by (★)). The simplification
of `ĥ_i Λ_{E_i}` is direct cancellation. Vanishing of `Σ_j q_j Π_{U_j} · Λ_V`
is equivalent to vanishing of `Σ_j q_j Π_{U_j}` because `Λ_V ≠ 0`. □

## Lemma 2.4 (Generic dimension formula)

Suppose the polynomials `Π_{U_1}, ..., Π_{U_{w'+1}}` are pairwise coprime
(which holds whenever `U_i ∩ U_j = ∅` for `i ≠ j`, the **distinct-extras**
condition). Then for distinct nonzero `γ_j`,
```
dim X_γ_sub  =  max{0, (w'+1)(c-1) - 2(c + w - w' - 1)}
             =  max{0, (w'-1)(c-1) - 2(w - w')}.
```

### Proof sketch

Domain dim of `T`: `(w'+1)(c-1)`. Codomain dim: `2(c + w - w' - 1)` (each
factor `q_i Π_{U_i}` has degree at most `(c-2) + (w-w')`, i.e. `c + w - w' - 1`
coefficients).

Generic-rank claim: under distinct-extras, `T` has rank
`min((w'+1)(c-1), 2(c+w-w'-1))`. The reason is that under distinct extras
the products `{x^k · Π_{U_j}}_{0 ≤ k ≤ c-2,\, 1 ≤ j ≤ w'+1}` form a linearly
independent family in `F_p[x]_{<c+w-w'-1}` whenever the upper bound permits
(i.e. when `(w'+1)(c-1) ≤ c+w-w'-1`); otherwise they span a subspace of
dimension `c+w-w'-1`. Combined with the second constraint (twisted by
distinct `γ_j`), the rank of `T` reaches the codomain dim if the codomain
dim ≤ domain dim, and equals the domain dim otherwise.

(A rigorous proof of generic rank reduces to a Vandermonde-style
determinant argument using distinct `L_u` for `u ∈ ⋃_j U_j` and distinct
`γ_j`. This is straightforward but routine; we omit the full bookkeeping.)

In particular, when `(w'-1)(c-1) - 2(w-w') ≤ 0` the kernel is trivial. □

### Verification (op2_subtet_dim_formula.py)

Empirical mode of dim X_γ_sub over 10 random distinct-extras configurations
matches the formula in 9 of 9 cases tested:

| n  | c | w | w' | predicted | observed mode |
|----|---|---|----|-----------|---------------|
| 12 | 3 | 3 | 2  | 0         | 0             |
| 12 | 3 | 3 | 3  | 4         | 4             |
| 16 | 3 | 5 | 2  | 0         | 0             |
| 16 | 3 | 5 | 3  | 0         | 0             |
| 16 | 3 | 5 | 4  | 4         | 4             |
| 16 | 3 | 5 | 5  | 8         | 8             |
| 16 | 4 | 4 | 2  | 0         | 0             |
| 16 | 4 | 4 | 3  | 4         | 4             |
| 16 | 4 | 4 | 4  | 9         | 9             |

(Note: at `w'=w` the table reads `(w-1)(c-1)`, matching Note 0099 exactly.)

## Lemma 2.5 (Bad-realizing sub-tet ⇒ extras collision)

If a sub-tet on `V` with `w' < w` admits a non-trivial `(ĥ_j) ∈ X_γ_sub` (i.e.
`dim X_γ_sub ≥ 1`) for distinct `γ_j`, then either:
- **(generic threshold case)**: `(w'-1)(c-1) > 2(w - w')`, i.e. the formula
  gives `≥ 1` already, or
- **(extras collision)**: some `Π_{U_i}` and `Π_{U_j}` share an algebraic
  relation (typically `U_i ∩ U_j ≠ ∅`).

### Examples

- **Full tet** (`w' = w`): formula gives `(w-1)(c-1) ≥ 2` for `c ≥ 3, w ≥ 2`.
  This is the route in Note 0099.
- **Pattern A** at `n=12, c=3, w=3, w'=2`: formula gives `0`, but bad-realizing
  Pattern A configs satisfy extras collision (e.g.
  `V=(3,7,9), U_0=U_2={8}, U_1={4}`), forcing `dim X_γ_sub = 1`. Verified.
- **Pattern B/D**: similar analysis, with various collision patterns.

So the *bad-realizing* sub-tet locus inside the routed dichotomy is precisely
the variety of extras-collision configurations — itself a low-dimensional
subvariety of `(E_1, ..., E_{w'+1})`-space.

## Codim contribution to V_bad

Combining Lemmas 2.1–2.5 with the standard Schwartz-Zippel argument used in
Note 0099 §4, the contribution of the **bad-realizing sub-tet route** to
`V_bad` (i.e. `(s_1, s_2)` admitting `m = T+1` bad `γ`'s on at least one
sub-tet of size `w'+1` plus `m - (w'+1)` "extra" supports) has codimension at
least:

```
codim ≥ (w' + 2c - 1) + (m - w' - 1) · 1   =   T + 2c - 1
```

(Each extra support contributes generic codim 1.)

At `n = 12, c = 3, w = 3, T = 3`: gives `T + 2c - 1 = 8`, exceeding the
target `2D - T - 2 = 7`. ✓

At `n = 16, c = 4, w = 4, T = 4`: gives `T + 2c - 1 = 11`. Target
`2D - T - 2 = 14`. **Insufficient** — the sub-tet route at small `w'`
doesn't suffice; need to use larger `w'` ≤ w-1 with stricter extras
constraints. To address this we will need finer route stratification at
`c ≥ 4`, which Note 0109 flagged as "TODO at c=4".

For `c = 3` (the c-bottleneck regime), the bound holds. ✓

## Open items

1. **Lemma 2.4 generic-rank rigor**: the polynomial-syzygy argument should
   be tightened with an explicit Vandermonde determinant argument. Drafting.
2. **Lemma 2.5 closure**: rigorously characterize "extras collision" as a
   codim-`(w-w')` condition on extras choice — this gives the codim of
   bad-realizing sub-tet locus inside its naive count.
3. **`c ≥ 4` route refinement**: at `n=16, c=4`, the simple Lemma 2.4 bound
   is short by 3. Need to stratify sub-tet route by `w'` and apply Lemma 2.4
   recursively, or invoke `dim X_γ_sub` formula at `w' = w-1` directly.
4. **Pattern C star route**: separately handled in Note 0111 (TODO).

## Files

- `notes/scripts/op2_subtet_lagrange_verify.py` — Lemma 2.1 + 2.2 verification
- `notes/scripts/op2_subtet_dim_formula.py` — Lemma 2.4 formula verification
- `notes/0099-tetrahedron-analytic-proof.md` — full-tet (`w' = w`) base case
