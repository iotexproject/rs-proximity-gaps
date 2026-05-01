"""verify_inj_hypothesis.py — verify the hypothesis dist(f_o, C_1) > 9 for the
dense K=2 worst case where |{α : d_1(α) = 9}| = 10.

If this hypothesis fails for some above-J f, the injectivity argument in
Theorem 0141.A breaks down. Verify across multiple cases.
"""
from __future__ import annotations
import sys, os, random
import numpy as np
from itertools import combinations
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

P = 449
N0 = 32
K0 = 8
R = 2

import probe_step5_n32_studio
probe_step5_n32_studio.P = P
probe_step5_n32_studio.N0 = N0
probe_step5_n32_studio.K0 = K0

import sweep_K2_q193
sweep_K2_q193.P = P
sweep_K2_q193.N0 = N0
sweep_K2_q193.K0 = K0

from fri_2round_attack import setup_chain, even_odd_parts, parity_check, gauss_rank
from sweep_K2_q193 import construct_K2_psi_in_U
from mds_decoder import precompute_diff_inv, batched_extras


def dist_to_C1(vec, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1):
    vec_arr = np.array(vec, dtype=np.int64)
    extras = batched_extras(info_sets_arr, vec_arr, L1_arr, D1, inv_D1, p)
    return n1 - k1 - int(extras.max())


def main():
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)
    L0 = chain[0][0]
    L1, k1, _ = chain[1]
    n1 = len(L1)
    L1_arr = np.array(L1, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    info_sets = list(combinations(range(n1), k1))
    info_sets_arr = np.array(info_sets, dtype=np.int64)

    rng = random.Random(2026)
    print(f"=== Verify dist(f_o, C_1) > 9 for dense K=2 above-J at q={p} ===")
    print()
    print(f"{'attempt':>8} {'min d_1':>8} {'#d_1=9':>7} {'dist(f_o,C_1)':>14} {'dist(f_e,C_1)':>14} {'inj?':>5}")
    print("-" * 70)

    failures = []
    for attempt in range(20):
        f, T1, T2 = construct_K2_psi_in_U(rng, p, chain, H_R, n_R)
        if f is None: continue
        f_e, f_o = even_odd_parts(f, L0, p)
        # Distance of f_o to C_1
        d_fo = dist_to_C1(f_o, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1)
        d_fe = dist_to_C1(f_e, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1)
        # Compute d_1 distribution
        f_e_arr = np.array(f_e, dtype=np.int64)
        f_o_arr = np.array(f_o, dtype=np.int64)
        d1_dist = Counter()
        min_d1 = n1
        for a1 in range(p):
            fold1_arr = (f_e_arr + a1 * f_o_arr) % p
            extras = batched_extras(info_sets_arr, fold1_arr, L1_arr, D1, inv_D1, p)
            d1 = n1 - k1 - int(extras.max())
            d1_dist[d1] += 1
            if a1 != 0 and d1 < min_d1:
                min_d1 = d1
        n_d1_9 = d1_dist.get(9, 0)
        above_J = (2 * min_d1) > 16
        if not above_J:
            continue  # skip below-J
        inj_ok = "YES" if d_fo > 9 else "FAIL"
        print(f"{attempt+1:>8} {min_d1:>8} {n_d1_9:>7} {d_fo:>14} {d_fe:>14} {inj_ok:>5}")
        if d_fo <= 9 and n_d1_9 > 0:
            failures.append((attempt+1, d_fo, n_d1_9, T1, T2))

    print()
    print(f"=== Summary ===")
    print(f"Failures (dist(f_o,C_1) ≤ 9 with d_1=9 cases): {len(failures)}")
    if failures:
        print(f"INJECTIVITY HYPOTHESIS FAILS for these. Need stronger argument.")
        for f in failures:
            print(f"  attempt {f[0]}: dist(f_o)={f[1]}, n_d1_9={f[2]}, T1={f[3]}, T2={f[4]}")
    else:
        print(f"INJECTIVITY hypothesis dist(f_o,C_1) > 9 holds for ALL tested above-J cases.")


if __name__ == "__main__":
    main()
