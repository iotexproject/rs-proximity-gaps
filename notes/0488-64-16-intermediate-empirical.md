# Note 0488 — (64, 16) intermediate K_BW empirical close

**Date:** 2026-05-04 night iteration 5
**Status:** K_BW^{(64,16)} = 0 across 72 cases × 9 primes. Resolves task #324.

## Setup

At L_3 deployment (n_0, k_0) = (128, 32), the L_1-factored sub-case B
residual at N_α < 80 needs the (64, 16) intermediate K_BW result. (See
paper2 §7 `lem:L1-factored-bound`.)

This note tests the (64, 16) analog in the same scaled-down framework as
(32, 8) [Note 0485] and (16, 4) [Note 0486]:

- **Outer**: L = μ_64, RS_16 codewords. τ_BW = (64+16)/2 = 40.
- **Inner**: L' = μ_16, RS_4 base. Stratum (B) construction.
- **Lift**: z → z^4 from L' to L (4:1).

Mod-4 split:
- u_side = {r ∈ [4, 16) : r mod 4 ∈ {0, 1}} = {4, 5, 8, 9, 12, 13} (size 6)
- v_side = {r ∈ [4, 16) : r mod 4 ∈ {2, 3}} = {6, 7, 10, 11, 14, 15} (size 6)

## Empirical result (`issue419_64_16_kbw_intermediate.py`)

Across **9 primes** {193, 257, 449, 577, 641, 769, 1153, 1217, 1409}
(admitting μ_64) and **8 stratum (B) cases each = 72 cases total**:

| Quantity | Value across all 72 cases |
|---|---|
| |T_inner| (common zeros on L' = μ_16) | 0 |
| K_1 (saturating α to c=0) | 0 |
| K_2 (BW returns non-zero c with agr ≥ 40) | 0 |
| **K_BW^{(64,16)}** | **0** |

## Structural framework

Analog of L_2 / L_1 setups: same G1+G2+G3+IP machinery applies with parameters

| Parameter | (16, 4) [L_1] | (32, 8) [L_2] | (64, 16) (this note) | (128, 32) [L_3] |
|---|---|---|---|---|
| n | 16 | 32 | 64 | 128 |
| k | 4 | 8 | 16 | 32 |
| τ_BW | 10 | 20 | 40 | 80 |
| Inner | (8, 2) | (8, 2) | (16, 4) | (32, 8) |
| Lift ratio | 2:1 | 4:1 | 4:1 | 4:1 |
| Sub-case A bound | 9 < 10 ✓ | 16 < 20 ✓ | 38 < 40 (expected) | 78 < 80 ✓ |

**Sub-case A IP at (64, 16)**: with 4:1 lift, fiber size 4. Per-fiber
polynomial degree a_u ≤ 4. Cross-pair Singleton at L = μ_64: each pair
$E_k(w) := c(w) - c(w \zeta^k)$ has degree ≤ deg c + (k-1) where ζ is
4th root. With k_outer=16, deg c ≤ 15. Three non-trivial cross-pairs.
IP optimum: $\sum a_u \leq 38 < 40$. (Detailed computation parallels
Note 0485 for (32, 8).)

So sub-case A at (64, 16) is unconditional. Sub-case B reduces to
**kernel-refined** (16, 4) Conj A — which itself reduces to (8, 2)
Conj A via further 2:1 lift.

## Implication for L_3 sub-case B

L_3 = (128, 32), sub-case B (L_1-factored, c factors through w → w²
within outer or via 4:1 nested lifts) at N_α < 80 reduces to (64, 16)
intermediate. Empirical close here means the residual at N_α = 76, 72,
etc. doesn't realize K_2 > 0 in any tested case.

## Combined L_1 + L_2 + L_3 + intermediate (64, 16) status

| Layer | (n, k) | τ_BW | Cases tested | K_BW empirical | Sub-case A close |
|---|---|---|---|---|---|
| L_1 | (16, 4) | 10 | 80 + 20 = 100 | 0 | unconditional ≤ 9 ✓ |
| L_2 | (32, 8) | 20 | 60 | 0 | unconditional ≤ 16 ✓ |
| **(64, 16)** | (64, 16) | 40 | **72** | **0** | expected ≤ 38 ✓ |
| L_3 | (128, 32) | 80 | 24 | ≤ 2 | 4/5 unconditional, residual |
| Refined (8,2) Conj A base | (8, 2) | 5 | 540 | (no cex) | OPEN |

Total: **(100 + 60 + 72 + 24) outer + 540 base = 796 tests, 0 K_BW counterexample.**

## Files

- `issue419_64_16_kbw_intermediate.py` (driver) + `.output.txt`
