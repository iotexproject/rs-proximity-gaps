"""verify_doubly_above_J.py — verify how often K=2 above-J f satisfies dist(f_e, C_1) ≥ 9 AND dist(f_o, C_1) ≥ 9.

The hypothesis of Theorem 0145. Empirical fraction informs how much of the
K=2 dense case the rigorous bound covers.
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

    n_per_q = 50
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
        n_above_J = 0
        n_doubly = 0
        n_K2 = 0
        n_doubly_K2 = 0
        d_fe_dist = {}
        d_fo_dist = {}
        for trial in range(n_per_q * 3):
            n_pos = rng.choice([3, 4, 5, 6])
            positions = sorted(rng.sample(range(K0, N0), n_pos))
            fhat = [0] * N0
            for pos in positions:
                fhat[pos] = rng.randrange(1, p)
            f = evaluate_dft(fhat, L0, p)
            d = dist_lower_bound_sampling(f, L0, K0, p, n_samples=2000, batch=2048, seed=rng.randrange(10**9))
            if d <= W_J: continue
            n_above_J += 1
            f_e, f_o = even_odd_parts(f, L0, p)
            f_e_arr = np.array(f_e, dtype=np.int64)
            f_o_arr = np.array(f_o, dtype=np.int64)
            extras_fe = batched_extras(info_sets_arr, f_e_arr, L1_arr, D1, inv_D1, p)
            extras_fo = batched_extras(info_sets_arr, f_o_arr, L1_arr, D1, inv_D1, p)
            d_fe = n1 - k1 - int(extras_fe.max())
            d_fo = n1 - k1 - int(extras_fo.max())
            d_fe_dist[d_fe] = d_fe_dist.get(d_fe, 0) + 1
            d_fo_dist[d_fo] = d_fo_dist.get(d_fo, 0) + 1
            is_K2 = (any(j % 2 == 0 for j in positions if j >= K0) and
                     any(j % 2 == 1 for j in positions if j >= K0))
            if is_K2:
                n_K2 += 1
                if d_fe >= 9 and d_fo >= 9:
                    n_doubly_K2 += 1
            if d_fe >= 9 and d_fo >= 9:
                n_doubly += 1
            if n_above_J >= n_per_q: break
        print(f"q={p}: above-J f = {n_above_J}, K=2 = {n_K2}, doubly-above-J@1 = {n_doubly}, K=2 doubly-above-J@1 = {n_doubly_K2}")
        print(f"  dist(f_e, C_1) distribution: {sorted(d_fe_dist.items())}")
        print(f"  dist(f_o, C_1) distribution: {sorted(d_fo_dist.items())}")
        if n_K2 > 0:
            print(f"  Fraction K=2 doubly above-J at level 1: {n_doubly_K2 / n_K2:.2%}")
        print()


if __name__ == "__main__":
    main()
