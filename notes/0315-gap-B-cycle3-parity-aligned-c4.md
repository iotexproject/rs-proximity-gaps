# Note 0315 — Gap B cycle 3: parity-aligned 3-pos sparse construction at (16, 4, c=4)

**Branch:** `feat/op1a-algorithm-fixes` (PR #414)
**Date:** 2026-05-01
**Status:** Cycle 3 deliverable — second small-proxy structural-composition mechanism.

## Goal

Cycle 1 + 2 strengthened Note 0310's `(16, 4, c=3)` construction with multi-prime evidence (Note 0314). Cycle 3 explores whether the structural-composition mechanism (sparse witnesses reaching paper3 V_bad strata) extends to a different `c` value at the same proxy `n=16`. The finding: yes, with a **simpler** mechanism — a codim-zero parity-aligned construction at `(16, 4, c=4)` Johnson-boundary.

## The construction

**Cell:** `(n, k, c) = (16, 4, 4)`, so `D = 12`, `w = 8`, `T_c = ⌊(2D-1)/c⌋ = 5`.

**Note:** `δ = w/n = 1/2 = J/n` (Johnson radius), **not** strictly above-Johnson. So this proxy is at the Johnson boundary, outside paper2's K10 above-J scope. paper2 K10 does not apply.

**Construction:** Both `s_1, s_2` are 3-position sparse with all support on **odd positions** in `[k, n-1] = [4, 15]`, i.e., `supp(s_i) ⊆ {5, 7, 9, 11, 13, 15}`. Concretely:
- `s_1 = ev_5 + 2·ev_7 + 3·ev_9`
- `s_2 = 5·ev_{11} + 7·ev_{13} + 11·ev_{15}`

**Claim:** `M(s_1, s_2) = q - 1` (saturated) for any prime `p` admitting `16 | (p-1)`.

## Why it works

For `v` odd, `ω^{8v} = (ω^8)^v = (-1)^v = -1`, so for any `j`:
```
ev_v[j] + ev_v[j+8] = ω^{jv} + ω^{(j+8)v} = ω^{jv}(1 + ω^{8v}) = ω^{jv}·0 = 0.
```

Hence for any `s = sum_l ξ_l·ev_{v_l}` with all `v_l` odd, `s[j] + s[j+8] = 0` for `j ∈ {0,1,2,3}`. So `s ∈ V_E` for `E = {odd positions in [16]}` of size `8 = w`.

This holds for both `s_1` and `s_2`, hence `x_α = s_1 + α·s_2 ∈ V_E` for **every** `α ∈ F_p`. So every `α` gives a weight-`w` realizer (with `E = odd_positions`), and `M(s_1, s_2) = q - 1` (excluding only `α` such that `x_α = 0` if any).

## Empirical verification

`notes/scripts/cycle3_parity_aligned_c4.py`:

| Prime  | M(s_1, s_2) | Expected (q-1) | T_c | Result |
|--------|-------------|----------------|-----|--------|
| `p=17`   | 16          | 16             | 5   | PASS   |
| `p=97`   | 96          | 96             | 5   | PASS   |
| `p=113`  | 112         | 112            | 5   | PASS   |
| `p=193`  | 192         | 192            | 5   | PASS   |

All 4 primes saturate `M = q - 1`. Far above `T_c = 5`. Joint Vandermonde support `|S*| = 6 < w + 1 = 9`, so `(s_1, s_2)` is in V_bad **sub-leading** stratum (codim `> 2(c-1) = 6`).

## Comparison with Note 0310

| Aspect                    | Note 0310 ((16,4,c=3))             | Note 0315 ((16,4,c=4))                  |
|---------------------------|-------------------------------------|------------------------------------------|
| paper2 K10 applies?       | Yes (above-J: δ=9/16 > 1/2)         | No (Johnson boundary: δ=1/2)             |
| K(s_1, s_2) achieved      | K = 9 (matches T_c+1=8 lower bound) | K = q-1 (full saturation)                |
| Mechanism                 | Codim-1 branches `H_r: b_8 = ω^{-2r} b_6` | Codim-0 (open subset of parity-aligned 3-mono pairs) |
| paper3 stratum reached    | LEADING (`|S*| = w+1 = 10`)         | sub-leading (`|S*| = 6 < w+1 = 9`)       |
| Construction complexity   | 8 explicit branches with closed-form α_{r,x} formula | Trivial: any 3-pos s_1, s_2 with odd-only support |

## Why the (16, 4, c=4) finding doesn't lift to deployment

The construction relies on `w = n/2`, i.e., `c = D - w = (3n/4) - (n/2) = n/4`. At rate `1/4`, this gives `c = n/4`, growing linearly with `n`. ABF deployment range is `c ∈ {3, 4, 6, 9}` (constant); only at `n = 16` does `c = n/4 = 4` coincide. At larger `n`, the construction's specific `Q_E = z^{n/2} ± 1` factorization gives `|E| = n/2 ≠ w` and the parity-orthogonality fails.

So this cell is small-scale-specific, like Note 0310's. The two findings are **complementary** structural-composition mechanisms at small proxies, **not** deployment-scale results.

## Significance for Gap B

This is paper3-INTERNAL evidence that V_bad has rich structural sub-locus reachable by sparse witnesses — but only at small proxies. It does not weaken Cycle 1's conclusion that Gap B is genuinely outside paper3's reach at deployment scale. It does strengthen the **structural support** for `conj:sparse-worst` by showing a SECOND independent small-proxy mechanism for sparse-witness reaching V_bad. Paper3's "compatible with both routes" framing (cycle 2's frontier paragraph) is supported.

## Files

- `notes/scripts/cycle3_parity_aligned_c4.py` — verification script.
- This note.

## Cross-refs

- Note 0310 — Zariski-open branch theorem at (16, 4, c=3).
- Note 0313 — Gap B structural analysis.
- Note 0314 — Multi-prime certification of Note 0310.
