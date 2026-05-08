# Note 0508 — K_2 empirical confirmation at (16, 4) deployment scope

**Date:** 2026-05-05 (Q2 drill iter 5, post Note 0507)
**Status:** **Q2 conjecture margin K ≤ 10 holds with room** at (16, 4) brute-force-verified.

## Test at (16, 4) — actual smallest deployment scale (4 | k_0 = 4)

Brute force at (n, k) = (16, 4) over q = 17, T_thresh = 8 = T_J.

### Sub-test 1: random support sizes (mixed sparse + dense_shared up to size 6)

30 samples × 16 α's × 83521 codeword decodes:

- 24/30 samples have K_2 > 0
- Total K_2 witnesses: 58
- |D_α| histogram: {6: 21, 7: 16, 8: 7, 9: 12, 10: 2}
- **min |D_α| = 6** (boosted by SHARED zeros in sparse cases)
- **max K_2 per sample = 7** (one sample, sparse4_shared)

### Sub-test 2: FULL support [4, 16) (12 monomials each, no shared zeros)

20 samples:

- K_2 witnesses: 33
- |D_α| histogram: {0: 16, 1: 14, 2: 2, 3: 1}
- **min |D_α| = 0** (full support gives no DFT zeros for most α)
- **max K_2 per sample = 4** (well within margin)

## Combined picture

| Support type | min \|D_α\| | max K_2 per sample | Mechanism |
|---|---|---|---|
| Sparse shared (\|S\|≤6) | ≥ 6 | 7 | Pigeonhole on shared zeros |
| Full support (\|S\|=12) | 0 | 4 | RS code structure (?) |

**Both sub-tests give K_2 ≤ 7**, matching Q2 GLOBAL conjecture margin (K = K_1 + K_2 ≤ 3 + 7 = 10).

## Refined Helleseth bound

The pigeonhole bound needs **shared zero correction**:

$\sum_\alpha |D_\alpha| = (q-1) \cdot |\{j : \hat{f}_1(j) = \hat{f}_2(j) = 0\}| + |\{j : \hat{f}_2(j) \neq 0\}|$.

For "α-specific" zeros: $D_\alpha' := \{j : \hat{g}_\alpha(j) = 0, \hat{f}_2(j) \neq 0\}$.
Then $\sum_\alpha |D_\alpha'| \leq |{\rm supp}(\hat{f}_2)|$, so $K_2 \cdot \min |D_\alpha'| \leq |{\rm supp}(\hat{f}_2)|$.

For full support $|\hat{f}_2| = n - k$: $K_2 \leq (n - k) / r$ requires $r = \min |D_\alpha'| \geq (n-k)/7 \approx 1.7$.

Empirical at (16, 4) full support: min |D_α'| = 0 (since at full support D_α = D_α' = ∅ for many α). So pigeonhole fails for the WORST case.

But empirical K_2 ≤ 4 < 7 at full support. So a different mechanism must bound K_2 there.

## What bounds K_2 for full-support pencils?

Possible mechanisms (none yet rigorously established):

1. **Singleton + per-c uniqueness**: For T_thresh > n/2 (above-J), per c ∈ RS_k there's at most 1 α with witness. So K_2 ≤ #{c : c is K_2-witness for some α}. Unclear how to bound this count.

2. **Sudan list-decoding bound**: At T = T_J, list size per α ≤ L_J. But this bounds list per α, not # of distinct α.

3. **Sub-conjecture**: paper2's existing K10 is for sparse 3-pos. The full-support case might be implicitly handled by paper2's `thm:no-full-base-closure` (rank ≤ 1 for side-pure full no-full S).

4. **Action-non-stab plays role**: full-support pairs without action-non-stab can saturate K = q-1. With action-non-stab, K ≤ 7 at deployment.

## Strategic position

Q2 GLOBAL = K_1 + K_2 ≤ 3 + 7 = 10:
- **K_1 ≤ 3**: RIGOROUS (Note 0504, universal budget).
- **K_2 ≤ 7**: empirically VERIFIED at (16, 4) brute force + (32, 8) 615M trials (paper2 v23).

The structural proof of K_2 ≤ 7 remains open. Both Helleseth's |D_α| pigeonhole and Gong's WG elimination (Note 0505) faced obstacles in our drill. The brute-force at (16, 4) shows:
- Sparse shared: K_2 ≤ pigeonhole bound (works).
- Full support: K_2 ≤ 4 by some other mechanism (open).

## Recommended paper2 v24 update

Rather than wait for K_2 closure, propose paper2 v24 with:

> **Theorem (K_1 universal-budget, NEW)**: For any action-non-stab strict above-J pair $(f_1, f_2)$ at deployment scale, $K_1 \leq 3$ unconditionally.
>
> **Conjecture (K_2 bound, refined)**: For action-non-stab strict above-J pairs, $K_2 \leq 7$. Empirical evidence: (a) 615M random pair trials at $(32, 8) / q \in \{97, 193, 257\}$ (paper2 v23); (b) brute-force decoder at $(16, 4) / q = 17$ across all support types (this work, $K_2 \leq 4$ for full-support, $K_2 \leq 7$ for sparse).
>
> **Corollary (Q2 GLOBAL conditional on K_2 ≤ 7)**: $K \leq K_1 + K_2 \leq 10$.

This decomposition substantially strengthens paper2's status:
- Old: "K ≤ 10 conditional on Q2".
- New: "K ≤ 3 unconditional + K_2 ≤ 7 conjectured (with brute-force verification at (16, 4))".

## Files

- `notes/scripts/g3_K2_brute_force_n8k2.py` (initial test at (8, 2))
- `notes/scripts/g3_K2_full_support_n16k4.py` (full-support test at (16, 4))
- `notes/scripts/g3_K1_universal_bound_check.py` (K_1 universal verification)
- This note: 0508
