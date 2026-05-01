"""verify_thm_doubly_above_J.py — empirical sanity check of Theorem 0145.

Theorem 0145: For K=2 above-J f with dist(f_e, C_1) ≥ 9 AND dist(f_o, C_1) ≥ 9:
    count_α(d_1 ≤ 8) ≤ 234.

This script measures actual count_α(d_1 ≤ 8) across many such f's and confirms
the bound is satisfied. Empirical max is expected to be much smaller (≤ 8).
"""
from __future__ import annotations
import sys, os, random
import numpy as np
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, even_odd_parts

import probe_step5_n32_studio
from probe_step5_n32_studio import N0, K0, R, evaluate_dft

W_J = N0 // 2


def main():
    from mds_decoder import dist_lower_bound_sampling, precompute_diff_inv, batched_extras

    print("=== Empirical verification of Theorem 0145 (count_α ≤ 234) ===")
    print()
    overall_max = 0
    n_tested_total = 0
    for p in [97, 193, 449]:
        if (p - 1) % N0 != 0: continue
        chain = setup_chain(p, N0, K0, R=R)
        L0 = chain[0][0]
        L1, k1, _ = chain[1]
        n1 = len(L1)
        L1_arr = np.array(L1, dtype=np.int64)
        D1, inv_D1 = precompute_diff_inv(L1_arr, p)
        info_sets = list(combinations(range(n1), k1))
        info_sets_arr = np.array(info_sets, dtype=np.int64)
        rng = random.Random(2026 + p)
        max_count = 0
        n_tested = 0
        n_tries = 0
        while n_tested < 30 and n_tries < 200:
            n_tries += 1
            # Generate random K=2 above-J f
            n_pos = rng.choice([3, 4, 5, 6])
            positions = sorted(rng.sample(range(K0, N0), n_pos))
            has_even = any(j % 2 == 0 for j in positions)
            has_odd = any(j % 2 == 1 for j in positions)
            if not (has_even and has_odd): continue
            fhat = [0] * N0
            for pos in positions:
                fhat[pos] = rng.randrange(1, p)
            f = evaluate_dft(fhat, L0, p)
            d = dist_lower_bound_sampling(f, L0, K0, p, n_samples=2000, batch=2048, seed=rng.randrange(10**9))
            if d <= W_J: continue
            f_e, f_o = even_odd_parts(f, L0, p)
            f_e_arr = np.array(f_e, dtype=np.int64)
            f_o_arr = np.array(f_o, dtype=np.int64)
            extras_fe = batched_extras(info_sets_arr, f_e_arr, L1_arr, D1, inv_D1, p)
            extras_fo = batched_extras(info_sets_arr, f_o_arr, L1_arr, D1, inv_D1, p)
            d_fe = n1 - k1 - int(extras_fe.max())
            d_fo = n1 - k1 - int(extras_fo.max())
            if d_fe < 9 or d_fo < 9: continue  # not doubly-above-J@1
            # Count α with d_1(α) ≤ 8
            count_8 = 0
            for a in range(p):
                fold = (f_e_arr + a * f_o_arr) % p
                extras = batched_extras(info_sets_arr, fold, L1_arr, D1, inv_D1, p)
                d1 = n1 - k1 - int(extras.max())
                if d1 <= 8: count_8 += 1
            n_tested += 1
            n_tested_total += 1
            if count_8 > max_count:
                max_count = count_8
                print(f"  q={p} pos={positions}: d_fe={d_fe}, d_fo={d_fo}, count_α(d_1≤8) = {count_8}")
        print(f"  q={p}: {n_tested} doubly-above-J@1 K=2 cases, max count_α(d_1≤8) = {max_count}")
        if max_count > overall_max: overall_max = max_count
        print()

    print(f"=== Total: {n_tested_total} cases, overall max count = {overall_max} ===")
    print(f"Theorem 0145 bound: 234")
    if overall_max <= 234:
        print(f"✓ Bound HOLDS empirically ({overall_max} ≤ 234).")
    else:
        print(f"✗ Bound VIOLATED: {overall_max} > 234.")


if __name__ == "__main__":
    main()
