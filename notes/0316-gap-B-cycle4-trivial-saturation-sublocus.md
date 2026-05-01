# Note 0316 — Gap B cycle 4: trivial saturation sub-locus of V_bad

**Branch:** `feat/op1a-algorithm-fixes` (PR #414)
**Date:** 2026-05-01
**Status:** Cycle 4 deliverable — clean structural observation about V_bad.

## The observation

**Theorem (structural inclusion):** For any deployment cell `(n, k, c)` with `T_c = ⌊(2D-1)/c⌋ ≥ 1` and `w = D - c`,
```
V_bad ⊇ { (s_1, s_2) ∈ F_q^{2D} : |S*(s_1, s_2)| ≤ w  AND  s_1, s_2 not both zero }.
```

**Equivalently:** any pair `(s_1, s_2)` with joint Vandermonde support `≤ w` saturates `M(s_1, s_2) = q - 1` (the maximum possible per paper3 §sec:setup's `ξ ≠ 0` convention, excluding only the unique `α` with `x_α = 0` if `s_1, s_2` are linearly dependent).

## Proof

Let `S* := S*(s_1, s_2)`, `|S*| =: j ≤ w`. By the joint Vandermonde support definition, `s_1, s_2 ∈ V_{S*}`, so `x_α = s_1 + α s_2 ∈ V_{S*}` for every `α ∈ F_q`.

Pick any `E ⊇ S*` with `|E| = w`. Since `j ≤ w ≤ D`, `{ev_v : v ∈ E}` is linearly independent (Vandermonde). The unique expansion of `x_α` in the `V_E`-basis has coefficients supported on `S*`:
```
x_α = sum_{v ∈ S*} ξ_v(α) · ev_v + sum_{v ∈ E \ S*} 0 · ev_v.
```

The realizer `(E, ξ(α))` has `ξ(α) ∈ F_q^E` with non-zero entries on `S*` whenever `x_α ≠ 0`. By paper3's `ξ ≠ 0` convention (§sec:setup), this is a non-trivial weight-`w` realizer.

Hence every `α` with `x_α ≠ 0` contributes to `M(s_1, s_2)`. Excluding at most one `α` with `x_α = 0` (when `s_2 ≠ 0`, the unique `α = -s_1 / s_2` if `s_1, s_2` are co-linear; otherwise none), `M(s_1, s_2) ≥ q - 1`. Since `T_c ≤ q - 1` always (`T_c < q` strict at any deployment `|F| ≥ 2`), `M > T_c`, i.e., `(s_1, s_2) ∈ V_bad`. ∎

## Empirical verification

`notes/scripts/cycle4_jointsupp_below_w.py` — exhaustive search over all `C(n, w)` E's per `α`, no max-subsets cap.

| `(p, n, k, c)` | `w` | `T_c` | `|S*|` | `M` | `q-1` | Status |
|----------------|-----|-------|--------|-----|-------|--------|
| `(17, 16, 4, 3)`   | 9   | 7     | 6      | 16  | 16    | PASS   |
| `(97, 16, 4, 3)`   | 9   | 7     | 6      | 96  | 96    | PASS   |
| `(17, 16, 4, 2)`   | 10  | 11    | 8      | 16  | 16    | PASS   |
| `(17, 16, 4, 4)`   | 8   | 5     | 8      | 16  | 16    | PASS   |
| `(13, 12, 3, 3)`   | 6   | 5     | 6      | 12  | 12    | PASS   |

All 5 cells saturate `M = q - 1`.

## Implications

### 1. V_bad structural decomposition

V_bad has at least three structurally distinct contributions:

| Stratum                            | Codim in F_q^{2D}     | Reachability     |
|------------------------------------|------------------------|------------------|
| `{|S*| ≤ w}` (trivial saturation)  | `2(D - j)` ≥ `2c`     | trivially in V_bad |
| `{|S*| = w + 1}` (paper3 leading)  | `2(c - 1)`             | structured codim-1 branches (Note 0310) |
| `{|S*| > w + 1}` (sub-leading)     | `> 2(c - 1)`           | requires non-trivial alignment |

The paper3 LEADING codim-`2(c-1)` is the JUST-ABOVE-TRIVIAL-SATURATION regime (`|S*| = w+1`, codim `2c - 2`). The TRIVIAL-SATURATION regime (`|S*| ≤ w`, codim `≥ 2c`) is sub-dominant in the codim count but structurally distinct.

### 2. Why paper3's leading codim-2(c-1) is the right object

If we naively bounded `ε_commit ≤ |V_bad|/|F|^{2D}`, the trivial saturation contributes `≤ q^{2w}/q^{2D} = q^{-2c}`, dominated by the leading `q^{-2(c-1)}` (since `q^{-2(c-1)} > q^{-2c}` for `c ≥ 1`). So leading codim correctly identifies the dominant stratum on uniform measure.

### 3. Sparse adversary curves don't traverse trivial saturation extensively

For sparse 3-pos `f` at rate-1/4 above-J satisfying mod-4 pigeonhole, paper2's `K(f) ≤ 10` (Theorem `thm:universal-K10`) bounds the AVERAGED 2-round bad count. This implies the FRI commit-curve `ℓ_f` does **not** lie in the trivial saturation sub-locus `{|S*| ≤ w}` for many `α_1` — otherwise the per-`α_1` `M` would saturate at `q-1`, contributing `q-1` per `α_1` to `K(f)`, blowing past 10.

paper2's K10 is therefore a **NON-TRIVIAL** structural constraint on FRI commit-curves: sparse `f` curves AVOID the trivial saturation sub-locus most of the time, despite this sub-locus being huge in `F_q^{2D}`.

This is the mathematical content of paper2's K10: not "V_bad is small" (false — V_bad has trivial sub-locus), but "FRI commit-curves of sparse `f` AVOID the trivial sub-locus".

### 4. paper3's contribution clarified

paper3 contributes:
- **The codim-`2(c-1)` of V_bad** (leading stratum) — identifies the dominant structural feature.
- **The S\*-stratification** (case A / case B) — distinguishes the leading from sub-leading regimes.
- **Sparse-class deployment closure** via composition with paper2's K10 + R1 ⊆ R2 — uses paper2's curve-avoidance bound.

paper3 does **not** contribute a curve-avoidance bound for general `f` (Gap B). That requires paper2's `conj:sparse-worst` or moment-bound program. The trivial saturation observation makes this dependency explicit: V_bad's trivial sub-locus is huge, so any general-`f` bound on `ε_commit` requires CURVE-LEVEL analysis (paper2 territory), not POINT-LEVEL analysis (paper3 territory).

## Implication for paper3 framing

This observation could be added to paper3 as a structural remark in `§sec:setup` or `§sec:upper`, clarifying that:
1. V_bad is large (contains the trivial saturation sub-locus).
2. paper3's leading codim-`2(c-1)` is the dominant uniform-measure contribution.
3. The deployable bound REQUIRES curve-level constraints (paper2 territory).

Currently paper3 implicitly assumes this via the `S*`-stratification framework, but doesn't state the trivial saturation observation explicitly. Adding a one-paragraph remark would sharpen the framing.

## Cycle 4 sub-deliverable: write paper3 §sec:setup remark

Cycle 5 (next) should add this structural remark to paper3.

## Cross-refs

- Note 0310 — Zariski-open branch theorem at (16, 4, c=3) leading stratum
- Note 0313 — Gap B structural analysis (cycle 1)
- Note 0314 — Multi-prime certification (cycle 2)
- Note 0315 — Parity-aligned mechanism at (16, 4, c=4)
- paper3 §sec:setup, §sec:upper, §sec:sparse-closure
