# Note 0117 — Rigorous codim V_bad ≤ 2(c−1) via V_S × V_S inclusion

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Builds on**: Notes 0114, 0116
**Status**: **RIGOROUS** upper bound on codim V_bad — first non-conjectural
result in this rescope. Open: matching lower bound.

## Headline result

For RS at parameters `(n, k, c)` with `w = D − c` and `T = ⌊(2D−1)/c⌋`,
provided `w ≥ T`:
```
V_bad  ⊇  ⋃_{S ⊂ [n], |S| = w+1}  V_S × V_S
codim V_bad  ≤  2(c − 1)
```
where `V_S = span{ev_v : v ∈ S} ⊂ F_p^D`.

**`w ≥ T` holds at deployment-scale parameters** (n large vs c).

## Proof

For any `S ⊂ [n]` with `|S| = w + 1` and any `(s_1, s_2) ∈ V_S × V_S`:
```
s_1 = Σ_{u ∈ S} α_u ev_u,    s_2 = Σ_{u ∈ S} β_u ev_u.
```
For each `u_0 ∈ S`, define
- `E := S \ {u_0}` (size `w`, a valid support),
- `γ_{u_0} := −α_{u_0} / β_{u_0}` (well-defined when `β_{u_0} ≠ 0`).

Then
```
s_1 + γ_{u_0} s_2  =  Σ_{u ∈ S} (α_u + γ_{u_0} β_u) ev_u
                  =  Σ_{u ∈ E} (α_u + γ_{u_0} β_u) ev_u    ∈ V_E = ker N_E.
```
(The last equality uses Note 0114's `ker N_E = V_E`.)

Generic `(s_1, s_2)` realizes `w+1` distinct nonzero γ-values, one per
`u_0 ∈ S`. Since `w + 1 > T` (using `w ≥ T`), this is a `V_bad` witness.
Hence `V_S × V_S ⊂ V_bad` (modulo a Zariski-closed degenerate locus).

## Empirical confirmation (op2_v_S_test.py)

5 different `(n, c)` cases, 100% bad witnesses at `|S| = w+1`:

| (n, c)   | D  | w | T | |S| | M observed | M > T |
|----------|----|---|---|-----|------------|-------|
| (16, 4)  | 8  | 4 | 3 | 5   | 5          | 20/20 |
| (20, 5)  | 10 | 5 | 3 | 6   | 4–6        | 20/20 |
| (24, 4)  | 12 | 8 | 5 | 9   | 8–9        | 20/20 |
| (24, 5)  | 12 | 7 | 4 | 8   | 7–8        | 20/20 |
| (12, 3)  | 6  | 3 | 3 | 4   | 4          | 20/20 |

Sanity: at `|S| > w + 1`, M = 0 (no realizers). The construction
specifically requires `|S| = w + 1` so that `S \ {u_0}` is a valid
size-`w` support.

## Why Note 0103's empirical 7.8 missed this

Note 0103 reports empirical codim ≈ 7.8 at n=16 c=4 p=1009 by uniform
sampling `(s_1, s_2)`. The hit probability for `V_S × V_S` is
`p^{−6}` per sample per `S`. With `C(16, 5) = 4368` choices of `S`,
total Pr ≈ `4368 · p^{−6} ≈ 4 · 10^{−15}` at `p = 1009`. Detecting
this requires `~10^{15}` samples; Note 0103 likely used `~10^4`.

So Note 0103's measurement was **sample-limited and underestimated**
`|V_bad|`. The structural V_S × V_S component was always there, just
not detected by uniform sampling at small p.

## Implication for prize-grade soundness

Combining the rigorous upper bound `codim V_bad ≤ 2(c−1)`:
```
Pr[(s_1, s_2) ∈ V_bad]  ≥  q^{−2(c−1)}    [RIGOROUS LOWER BOUND on Pr[bad]]
```
This is an **absolute floor**: no Berlekamp-style soundness analysis
can give a tighter bound than this. For 128-bit security, we need
`q ≥ 2^{64/(c−1)}`:

| c | required `log_2 q` for 128-bit |
|---|--------------------------------|
| 3 | 32                             |
| 4 | 21.3                           |
| 5 | 16                             |
| 6 | 12.8                           |
| 9 | 8                              |

**Implication**: at base 31-bit fields (KoalaBear, BabyBear, Mersenne31)
with `c = 3`, prize-grade 128-bit security is **structurally impossible**
via Berlekamp/RS-proximity. ABF §6.3's choice of sextic extension
(F = 186 bits) is empirically necessary, not gratuitous.

## What changes vs Notes 0114, 0115, 0116

- **Note 0114** (`dim V_tet_sub = 2(w'+1)`) is correct but only describes
  the `extras_size = 1` distinct case, NOT the worst-case V_bad component.
- **Note 0116** (worst-case = 2(c−1)) was conjectural. Now **rigorous**.
- **Note 0115** (deployment rescope) — the deployment table needs
  reframing: `codim_worst = 2(c−1)` is the RIGOROUS bound; replace
  "optimistic" column wording.

## What's still open

The codim **lower bound** (upper bound on `|V_bad|`):
```
?    codim V_bad  ≥  2(c − 1) − O(log_p n)    [matching lower bound]
```
Equivalently: is `V_bad ⊆ ⋃_S V_S × V_S + (poly·dim correction)`?

If yes, then `codim V_bad = 2(c−1)` exactly and prize-grade soundness
follows wherever the table allows. If no, V_bad has additional larger
components, codim is even smaller, and the obstruction is even tighter.

Existing data points:
- Note 0103 empirical 7.8 at (n=16, c=4) is sample-limited (see above).
  Re-running with biased sampling (deliberately drawing from V_S × V_S
  components) would give ~6, not 7.8.
- 17/17 small-(n,c) Note 0114 distinct-extras data: dim 2(w'+1). This
  is a smaller component than V_S × V_S; doesn't bear on the bottleneck.
- Need new measurement: at (n=16, c=4, p) with importance-sampling of
  V_S × V_S, count `|V_bad ∩ V_S × V_S| / |V_S × V_S|`. If ≈ 1, `V_bad`
  near-equals the union of these slices.

## Files

- `notes/scripts/op2_v_S_test.py` — direct test, 5/5 cases at |S|=w+1
- `notes/scripts/op2_v_S_test.output.txt` — output
