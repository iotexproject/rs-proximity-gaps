# Note 0484 — L1+L2+L3 Structural Closure Roadmap

**Date:** 2026-05-04 night (post-compact, post f6bd2e1).
**Status:** ROADMAP — initial exploration. Two mis-starts logged for next iteration.

## Goal

Close K_BW ≤ 2 structurally and unconditionally at all three deployment scales:

| Layer | (n, k) | τ_BW | Status (after f6bd2e1) |
|---|---|---|---|
| L1 | (16, 4) | 10 | sweep verified, no structural proof |
| L2 | (32, 8) | 20 | empirical only (805+ tests via L_3 reduction) |
| L3 | (128, 32) | 80 | 4/5 components unconditional; residual = L_2 + (64, 16) Conj A |

## Mis-start 1: random RS_8 stratum (B) pairs at L_2

`issue419_L2_kbw_structural_explore.py`: generated f_u, f_v with Fourier support in {0,1,4,5} vs {2,3,6,7} (i.e., RS_8(L_2) coefficients), measured K_BW. All gave K_BW = 0 across 15 (p, seed) tests.

**Why this was meaningless**: The L_2 deployment-scale K_BW question is for f_u, f_v with **above-J Fourier support** on L_2 (degrees [8, 32) ⊂ Z/32), NOT for codewords in RS_8 (degrees [0, 8)). My setup put f_u, f_v inside RS_8, making h_α = f_u + α f_v itself a codeword — trivially K_BW = p-1 if BW decoder works correctly.

## Mis-start 2: BW decoder bug

`issue419_L2_kbw_with_T4.py`: full BW decoder returned None even on a clean codeword input. Bug in the `poly_divmod` shim or in the matrix system setup. Need to reuse the existing tested decoder from `issue419_conjA_zero_codeword_optimal.py` (`berlekamp_welch`), not rewrite.

## Correct L_2 K_BW setup (next iteration)

L_2 = (32, 8) deployment-scale K_BW question:
- f_u Fourier support ⊆ {r ∈ [8, 32) : r ≡ 0, 1 mod 4} (12 frequencies, dim 12)
- f_v Fourier support ⊆ {r ∈ [8, 32) : r ≡ 2, 3 mod 4} (12 frequencies, dim 12)
- Stratum (B) cross-side K = ?: pair has K-dim kernel structure for compatible (u, v) splits.
- "K = 16" at L_3 came from a specific construction; the L_2 analog at (32, 8) needs derivation.

For each (f_u, f_v) above-J pair on L_2, h_α := f_u + α f_v is above-J on L_2 (not a codeword in RS_8). K_BW^{L_2} := #{α : ∃ c_0 ∈ RS_8(L_2) \ {0} with agr_{L_2}(h_α, c_0) ≥ 20}.

## Structural close strategy at L_2

Same chain as L_3, scaled to L_2:

**(L1) Budget at L_2 → L_4 = μ_8**: pair on L_4 = (8, 2) has |T_4| common zeros; budget gives Σ_α (agr(h_α, 0) - 4|T_4|) = 4(8 - |T_4|).

**(L2) Degree counting (lem:degree-counting at L_2)**: any non-zero c_0 ∈ RS_8(L_2) gives agr ≤ 7 + (32 - N_α) = 39 - N_α.

**(L3) Saturation pigeonhole**:
- |T_4| = 5: budget 12, excess = 0 (degenerate).
- |T_4| = 4: budget 16, excess 4. K · 4 ≤ 16, K ≤ 4. ✗
- |T_4| = 3: budget 20, excess 8. K · 8 ≤ 20, K ≤ 2. ✓
- |T_4| = 2: budget 24, excess 12. K · 12 ≤ 24, K ≤ 2. ✓
- |T_4| = 1: budget 28, excess 16. K · 16 ≤ 28, K ≤ 1. ✓
- |T_4| = 0: budget 32, excess 20. K · 20 ≤ 32, K ≤ 1. ✓

**Need to determine: what's the max |T_4| for stratum (B) above-J pairs at L_2?** Empirical sweep next iteration.

If max |T_4| ≤ 4: K_1^{L_2} ≤ 4 by budget+pigeonhole. Empirically expect K = 0 or 2 for L_2 (mirror of L_3's K=2 cases).

**G1+G2+G3 + L_1-factored at L_2 → L_4**: same machinery, smaller scale.
- G1: a_u ≤ 4 with equality iff F ≡ 0 on fiber.
- G2: a_u = 4 requires c_{0,1}(u) = c_{0,2}(u) = c_{0,3}(u) = 0; these are deg ≤ 1 polys on L_4 (|L_4| = 8). Each has ≤ 1 zero. Common ≤ 1. So **N_4 ≤ 1**.
- G3: E_k(z) := c_0(z) - c_0(z ζ_4^k), deg ≤ 7, factors as z · Ẽ_k with deg Ẽ_k ≤ 6. M_k ≤ 6 each. **Σ a_u(a_u-1) ≤ 18**.
- IP at L_2: max Σ a_u s.t. a_u ≤ 4, N_4 ≤ 1, Σ a_u(a_u-1) ≤ 18, Σ N_i = 8.
  - Optimum at (N_2, rest) = (8, 0): cost 16, value 16. < 20. ✓

**L_1-factored sub-case at L_2**: c_0 = c_{0,0}(z^4) + z^2 c_{0,2}(z^4), factoring through z → z^2 to L_3' = μ_16. But h_α at L_2 doesn't factor (above-J on L_2). So bound via direct (non-factorization) argument needed; possibly via degree counting on a related polynomial.

## L_1 = (16, 4) plan

Smallest scale. Above-J Fourier support [4, 16) gives 12 frequencies.

Stratum (B) split mod 2 (since lift L_1 → L_2' = μ_8 is 2:1): f_u on r ≡ 0 mod 2, f_v on r ≡ 1 mod 2 in [4, 16).

|T_8| = common zeros on L_2' = μ_8. Budget: Σ_α (agr_{L_1}(h_α, 0) - 2|T_8|) = 2(8 - |T_8|).

Saturation at τ_{L_1} = 10 = 2|T_8| + (10 - 2|T_8|):
- |T_8| = 5: excess 0 (degenerate).
- |T_8| = 4: excess 2. K · 2 ≤ 8, K ≤ 4. ✗
- |T_8| = 3: excess 4. K · 4 ≤ 10, K ≤ 2. ✓
- |T_8| ≤ 2: K ≤ 1.

Same G1-G3 + L_1-factored at L_1 → L_2' = (8, 2) (4:1 lift via w → w^4):
- G1: a_u ≤ 4
- G2: a_u = 4 requires c_{0,1}(u) = c_{0,2}(u) = c_{0,3}(u) = 0; these are constants on L_2' (since RS_2(L_2') = constants? No, RS_{k_2'} where k_2' = ?)

Hmm L_1 = (16, 4) lifted from L_2' via w → w^4: L_2' = μ_4, RS_1(L_2') = constants. Too degenerate.

Better: L_1 = (16, 4) lifted via w → w^2 from L_2' = μ_8, RS_2(L_2') = degree ≤ 1 polys.
- G1: a_u ≤ 2 (per fiber of size 2).
- G2: a_u = 2 requires c_{0,1}(u) = 0; deg ≤ 1 polynomial on L_2' has ≤ 1 zero. So N_2 ≤ 1.
- G3: cross-pair Σ a_u(a_u-1) ≤ ?. At fiber size 2, only one pair per fiber. Σ a_u(a_u-1) = 2 N_2 ≤ 2.

L_1-factored sub-case empty (no intermediate fiber decomposition since fiber size 2 = lift dimension).

IP at L_1: max Σ a_u s.t. a_u ≤ 2, N_2 ≤ 1, Σ a_u(a_u-1) ≤ 2, Σ N_i = 8.
- N_2 = 1: cost 2, slots 1+rest. Max value = 2 + 7 = 9 (with N_1 = 7).
- Hmm value 9 < 10 = τ_{L_1}. Close but ✓ (10-1=9).

So K_BW^{L_1} ≤ 0 from non-induced + budget bounds K_1^{L_1} from saturation. Combining → K_BW^{L_1} ≤ 2 for |T_8| ∈ {0, 1, 2, 3}, ≤ 4 for |T_8| = 4 (loose).

## Estimated work

- Fix BW decoder (reuse existing), 15 min.
- Set up correct above-J pair structure at L_2, sweep K_BW empirically across (case, α). 30 min.
- Verify K_BW ≤ 2 + structural argument fits the L_2 analog. Write up `lem:L2-K-BW-2-structural`. 60 min.
- L_1 same path. 60 min.
- (64, 16) intermediate. 30 min.
- paper2 §7 integration. 60 min.

Total: ~5 hours of focused work.

## Next steps (each iteration)

1. Reuse existing `berlekamp_welch` from `issue419_conjA_zero_codeword_optimal.py`.
2. Reuse existing `find_stratum_B_cases` for L_3 setup; adapt for L_2 by adjusting subgroup parameters.
3. Empirical sweep: K_BW at L_2 across the same 24 cases (as f_u, f_v at L_2) — but we need an L_2-analog of "stratum B cross-side K=16 pair".

Concretely: scale the L_3 `(n_2, k_2) = (32, 8)` parameters to L_2's `(n_2', k_2') = (8, 2)`:
- L_2 plays the role of "L_0" in this smaller analog.
- L_4 = μ_8 plays the role of "L_2".
- (f_u', f_v') ∈ above-J on L_4 = (8, 2). RS_2 = constants + linear. Above-J support on r ∈ [2, 8) (6 freqs).
- Stratum (B) split: f_u' on r ≡ 0,1 mod 4 → {4, 5}, f_v' on r ≡ 2,3 mod 4 → {2, 3, 6, 7}.

Hmm asymmetric splits. Possibly degenerate at this scale.

Worst case: at very small scales (L_1, base), K_BW might require direct enumeration / different framework rather than scale-down of L_3 chain.
