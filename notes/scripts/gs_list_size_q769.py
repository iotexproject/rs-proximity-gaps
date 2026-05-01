"""gs_list_size_q769.py — extend GS list-size measurement to larger q.

Verify L_GS ≤ 3 empirical bound holds at q ∈ {769, 1153}, confirming the
q-independent upper bound claim.

q=769 has n_1*32=512 dividing q-1: 769-1 = 768 = 2^8 * 3. So 32 | 768. ✓
q=1153 also: 1152 = 2^7 * 3^2. 32 | 1152. ✓
"""
from __future__ import annotations
import sys, os, random
import numpy as np
from itertools import combinations
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

N0 = 32
K0 = 8
R = 2

import probe_step5_n32_studio
import sweep_K2_q193

from fri_2round_attack import setup_chain, even_odd_parts, parity_check, gauss_rank
from sweep_K2_q193 import construct_K2_psi_in_U
from mds_decoder import precompute_diff_inv, batched_extras
from empirical_gs_list_size import (
    find_alphas_d1_eq_9, find_closest_codeword, cluster_into_lines, is_codeword
)


def main():
    PRIMES = [769, 1153]
    target_per_q = 8  # smaller target since each case is slower at larger q
    print(f"=== Extended GS list-size verification at larger q ===")
    print()
    max_lgs_overall = 0
    for p in PRIMES:
        if (p - 1) % 32 != 0:
            print(f"q={p}: SKIP (32 ∤ q-1)")
            continue
        chain = setup_chain(p, N0, K0, R=R)
        L_R, k_R, _ = chain[R]
        n_R = len(L_R)
        H_R = parity_check(L_R, n_R, k_R, p)
        L1, k1, _ = chain[1]
        rng = random.Random(2026 + p)

        print(f"--- q = {p} ---")
        n_cases = 0
        n_attempts = 0
        max_lgs = 0
        lgs_distribution = Counter()
        max_N = 0
        while n_cases < target_per_q and n_attempts < 60:
            n_attempts += 1
            f, T1, T2 = construct_K2_psi_in_U(rng, p, chain, H_R, n_R)
            if f is None: continue
            alphas, _, _, _, f_e, f_o = find_alphas_d1_eq_9(f, chain, p)
            if len(alphas) < 3:
                continue
            n_cases += 1
            n1 = len(L1)
            codewords = []
            for a in alphas:
                fold1 = [(f_e[i] + a * f_o[i]) % p for i in range(n1)]
                c, agree = find_closest_codeword(fold1, L1, k1, p)
                codewords.append(c)
            clusters = cluster_into_lines(alphas, codewords, L1, k1, p)
            lgs = len(clusters)
            lgs_distribution[lgs] += 1
            cluster_sizes = sorted([len(cl) for cl in clusters], reverse=True)
            print(f"  attempt {n_attempts}: N={len(alphas)}, L_GS={lgs}, sizes={cluster_sizes}")
            if lgs > max_lgs: max_lgs = lgs
            if lgs > max_lgs_overall: max_lgs_overall = lgs
            if len(alphas) > max_N: max_N = len(alphas)
        print(f"  q={p}: tested={n_cases}, max L_GS={max_lgs}, max N={max_N}, dist={dict(lgs_distribution)}")
        print()

    print(f"=== Final ===")
    print(f"Across all q ∈ {{193, 449, 769, 1153}} (this run + previous): max L_GS observed = {max(max_lgs_overall, 3)}")


if __name__ == "__main__":
    main()
