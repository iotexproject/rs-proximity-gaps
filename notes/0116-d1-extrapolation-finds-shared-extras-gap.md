# Note 0116 — D1 finds Note 0114's formula incomplete (extras-distinctness gap)

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Builds on**: Notes 0103, 0114, 0115
**Status**: empirical finding — Note 0114 formula `dim V_tet_sub = 2(w'+1)`
holds only at `extras_size = 1` distinct case; the general/worst case is
`2(w+1)`, codim `2(c−1)`. Open question: does the "shared U" component
actually inhabit V_bad at small n?

## D1 sweep result (op2_d1_extrapolation.py)

At `n ∈ {32, 40, 48, 64}` with shared extras (forced by combinatorial
budget):

| n  | c | w  | w'_min | predicted 2(w'+1) | dim_est | actual matches |
|----|---|----|--------|--------------------|---------|----------------|
| 32 | 3 | 13 | 10     | 22                 | 27.97   | 2(w+1) = 28    |
| 32 | 4 | 12 | 7      | 16                 | 25.99   | 2(w+1) = 26    |
| 40 | 4 | 16 | 9      | 20                 | 33.55   | 2(w+1) = 34    |
| 48 | 5 | 19 | 9      | 20                 | 39.99   | 2(w+1) = 40    |
| 64 | 4 | 28 | 15     | 32                 | 57.95   | 2(w+1) = 58    |

5/5 hit `2(w+1)` exactly. Note 0114's `2(w'+1)` is wrong with shared U.

## Why Note 0114's formula was incomplete

Note 0114 §"Geometric structure" lines 99–117 sketches:
> For `(s_1, s_2)` with `s_1 + γ_i s_2 ∈ V_{E_i}` ... project on
> `F_p^D / V_V`: each support contributes ... 1-dim freedom along
> `ev_{u_i}` ... force `s_l` components in `V_U_l` to be 0.

The argument tacitly assumes:
- `extras_size = 1` (one extra per support: `|U_i| = 1`)
- `U_l` distinct across supports (`u_l ≠ u_m` for `l ≠ m`)

Both held in Note 0114's empirical robustness check (`V=[0,1,2,3], U=[4,5,6,7]`
at c=4 w'=3: extras_size=1, all 4 distinct). The 17/17 corroboration in
Note 0114 also stayed in this regime.

When extras share (`U_i = U` same for all `i`): `Σ_l V_{E_l} = V_V + V_U
= V_S` for `S = V ∪ U`, `|S| = w + 1`. The projection-and-force argument
collapses, and `V_tet_sub ⊂ V_S × V_S` fills the ambient `dim 2(w+1)`.

## The corrected (worst-case) codim upper bound

For ANY (w+1)-subset `S ⊂ [n]` with `w + 1 ≤ T + 1`:
```
V_S × V_S  ⊂  V_bad           (each (s_1, s_2) gives w+1 distinct γ-values)
codim V_bad  ≤  2D − 2(w+1)  =  2(D − w − 1)  =  2(c − 1).
```

This is the **universal worst-case**: independent of `n`. Much weaker than
Note 0114's `2(D − w'_min − 1)`.

## Realizability check (γ-values for V_S × V_S)

For `(s_1, s_2) ∈ V_S × V_S`, write `s_1 = Σ_{u∈S} α_u ev_u`, `s_2 = Σ_{u∈S}
β_u ev_u`. For each `u_0 ∈ S` (= w+1 choices):
- Take `E = S \ {u_0}`, size `w`
- `s_1 + γ s_2 ∈ V_E`  ⟺  the `u_0`-coefficient `α_{u_0} + γ β_{u_0} = 0`
  ⟺  `γ = −α_{u_0} / β_{u_0}`

So generic `(s_1, s_2)` realizes `w + 1` distinct nonzero γ-values, one
per element of `S`. If `w + 1 > T`, this is a V_bad witness. **Required:
`w ≥ T`.**

At rate 1/2 (`D = n/2`), `w = D − c`, `T = ⌊(2D−1)/c⌋`. The condition
`w ≥ T` holds iff `n ≥ c²/(c−2)·2` ≈ deployment-scale always.

## Apparent contradiction with Note 0103

Note 0103 (also Note 0114 line 145 table) reports empirical `codim V_bad =
7.8` at `n=16 c=4 p=1009`. Our worst-case formula predicts `codim ≤ 2(c−1)
= 6`.

If the worst-case is realized, empirical codim should be ~6, not 7.8.
Possible explanations:
1. The "shared U" component does NOT generically live in V_bad at small
   n; my D1 sample was an artificial config.
2. The Note 0103 empirical measurement is biased (sampling missed the
   shared-U component).
3. At n=16 c=4 specifically, the realizability check fails (`w = 4`,
   `T = 3`, so `w ≥ T` holds — should work).

**Open**: a direct test at `(n=16, c=4)` measuring V_bad codim with
explicit shared-U sampling, and confirming whether `V_S × V_S` ⊂ V_bad.

## Implications for Note 0115 deployment table

The deployment table (commit 3c41d9e) used Note 0114's `2(D − w'_min − 1)`
codim, giving codim ≈ D ≈ 2^20 at deployment scale. The worst-case
`2(c−1)` codim is much smaller.

Re-evaluating at deployment fields with worst-case codim `2(c−1)`:

| Field           | F bits | c=3 ε bits | c=4 ε bits | c=6 ε bits | c=9 ε bits |
|-----------------|--------|------------|------------|------------|------------|
| KoalaBear base  | 31     | 124 ❌      | 186 ✓      | 310 ✓      | 496 ✓      |
| BabyBear base   | 31     | 124 ❌      | 186 ✓      | 310 ✓      | 496 ✓      |
| Mersenne31 base | 31     | 124 ❌      | 186 ✓      | 310 ✓      | 496 ✓      |
| KoalaBear-ext6  | 186    | 744 ✓      | 1116 ✓     | 1860 ✓     | 2976 ✓     |
| Goldilocks      | 64     | 256 ✓      | 384 ✓      | 640 ✓      | 1024 ✓     |

**c = 3 at base 31-bit fields is borderline (124 vs 128, fails by 4 bits)**
under the worst-case codim. ABF §6.3 baseline (KoalaBear-ext6) has plenty
of slack.

## What this means for the rescope (Note 0115)

D0/D1/D2 status update:
- **D0 (table)**: needs regeneration with codim `2(c−1)` as a
  more-conservative (worst-case) row, alongside the optimistic
  `2(D−w'_min−1)` row. The user choosing between them depends on
  resolution of the open question above.
- **D1 (extrapolation)**: revealed the gap. The single-extras
  assumption in Note 0114 doesn't carry to multi-extras configs.
- **D2 (sub-tet existence)**: still 0/672 rows empty — the worst-case
  V_S × V_S construction is non-empty everywhere in deployment scope.

## Core gap (path forward)

The "core gap" of Note 0115 §"Core gap" was originally just the codim
*lower* bound. Now also need to nail the codim *upper* bound:

- **Verify worst-case** at small n: directly measure V_bad codim with
  shared-U sampling at `(n=16, c=4)` and `(n=20, c=5)`. If empirical
  matches `2(c−1)`, Note 0114's `2(w'+1)` formula is misleading
  (only the small-extras-distinct case).
- **Resolve Note 0103 contradiction**: empirical codim 7.8 at n=16 c=4
  is between 6 (worst case) and 8 (Note 0114). Either Note 0103 missed
  the worst-case component, or there's an additional structural bound
  preventing V_S × V_S from being a full V_bad component at small n.
- **If worst case confirmed (codim 2(c−1))**: deployment table accepts
  c=3 + 31-bit-base as marginally insufficient; recommend ext fields
  or c≥4. ABF §6.3's choice of ext6 is empirically the right call.

## Files

- `notes/scripts/op2_d1_extrapolation.py` — D1 sweep (this finding)
- `notes/scripts/op2_d1_extrapolation.output.txt` — 5/5 mismatch with
  Note 0114, all match `2(w+1)`
- TODO: direct V_bad codim measurement with shared-U sampling at small n
