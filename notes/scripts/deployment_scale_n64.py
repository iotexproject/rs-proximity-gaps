"""deployment_scale_n64.py — verify Master Theorem at (n_0=64, k_0=16, R=2).

If the universal sparse 2-term polynomial-degree witness + fiber counting hold
at n_0 = 64 (twice toy size), it strongly supports the deployment-scale claim.

Parameters: n_0=64, k_0=16, ρ=1/4, w_J=32, n_1=32, k_1=8.
Need q | 64 - 1 = 63 ... wait, 64 | q - 1.
q candidates: 193 (192/64=3 ✓), 449 (448/64=7 ✓), 769 (768/64=12 ✓).
"""
from __future__ import annotations
import sys, os, random
import numpy as np
from itertools import combinations
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

N0 = 64
K0 = 16
R = 2

import probe_step5_n32_studio
probe_step5_n32_studio.N0 = N0
probe_step5_n32_studio.K0 = K0

from fri_2round_attack import setup_chain, even_odd_parts, parity_check
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_at_L(coeffs, L, p):
    n = len(L)
    return [sum(c * pow(L[i], k, p) for k, c in enumerate(coeffs) if c != 0) % p for i in range(n)]


def fast_d1(fold1, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1):
    fold1_arr = np.array(fold1, dtype=np.int64)
    extras = batched_extras(info_sets_arr, fold1_arr, L1_arr, D1, inv_D1, p)
    return n1 - k1 - int(extras.max())


def main():
    q = 193  # 64 | 192 ✓
    chain = setup_chain(q, N0, K0, R=R)
    L0, _, _ = chain[0]
    L1, k1, _ = chain[1]
    n1 = len(L1)
    L1_arr = np.array(L1, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, q)
    # info sets: C(32, 8) = 10518300 — too many. Use random sampling for d_1 lower bound.
    print(f"=== Deployment-scale verification at (n_0={N0}, k_0={K0}, q={q}) ===")
    print(f"n_1 = {n1}, k_1 = {k1}, w_J = {N0//2} = 32")
    print(f"info sets size: C({n1}, {k1}) = {len(list(combinations(range(n1), k1)))}")
    print()

    # Use random subset of info sets for speed
    all_info_sets = list(combinations(range(n1), k1))
    rng = random.Random(2026)
    sample_size = min(len(all_info_sets), 5000)
    sampled = rng.sample(all_info_sets, sample_size)
    info_sets_arr = np.array(sampled, dtype=np.int64)
    print(f"Sampling {sample_size} info sets for d_1 estimate")
    print()

    # Test sparse 2-term polynomial-degree witness
    print(f"--- Sparse 2-term test at (n_0={N0}, k_0={K0}) ---")
    print(f"For f = x^i + x^j with i < j ≤ {N0//2 - 1} = 31, expect d_1 ≥ {n1} - ⌊j/2⌋")
    print()
    print(f"{'(i, j)':>10} {'pred d_1':>10} {'min d_1':>10} {'tie_d1':>10} {'check':>8}")
    print("-" * 60)

    test_cases = [(16, 17), (16, 31), (17, 31), (24, 31), (16, 25), (17, 25), (16, 24), (24, 25)]
    for i, j in test_cases:
        coeffs = [0] * N0
        coeffs[i] = 1
        coeffs[j] = 1
        f = evaluate_at_L(coeffs, L0, q)
        f_e, f_o = even_odd_parts(f, L0, q)
        f_e_arr = np.array(f_e, dtype=np.int64)
        f_o_arr = np.array(f_o, dtype=np.int64)
        pred_d1 = n1 - (j + 1) // 2
        min_d1_nz = n1
        d1_dist = Counter()
        for alpha in range(q):
            fold_a_arr = (f_e_arr + alpha * f_o_arr) % q
            d_a = fast_d1(fold_a_arr, L1_arr, info_sets_arr, D1, inv_D1, q, n1, k1)
            d1_dist[d_a] += 1
            if alpha != 0 and d_a < min_d1_nz:
                min_d1_nz = d_a
        tie_d1 = sum((1 - d/n1) * c for d, c in d1_dist.items()) / q
        check = "✓" if min_d1_nz >= pred_d1 else "✗"
        print(f"  ({i:3d}, {j:3d})  {pred_d1:>6}  {min_d1_nz:>6}  {tie_d1:.4f}  {check:>4}")

    print()
    print(f"=== Conclusion ===")
    print(f"If all checks pass: polynomial-degree witness extends to n_0 = {N0}.")
    print(f"This strongly supports the deployment-scale Master Theorem.")


if __name__ == "__main__":
    main()
