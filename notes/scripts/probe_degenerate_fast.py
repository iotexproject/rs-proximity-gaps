"""probe_degenerate_fast.py — fast d_1 measurement using batched MDS distance bound.

For q=193 pos {9,16,25}: get tie via batched fold computation.
"""
from __future__ import annotations
import sys, os, random
import numpy as np
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, even_odd_parts

import probe_step5_n32_studio
from probe_step5_n32_studio import N0, K0, R, evaluate_dft

P = 193


def main():
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L0 = chain[0][0]
    L1, k1, _ = chain[1]
    n1 = len(L1)

    # Reproduce the f
    rng = random.Random(2026 + p)
    from mds_decoder import dist_lower_bound_sampling, precompute_diff_inv, batched_extras
    W_J = N0 // 2
    f_target = None
    for trial_idx in range(5):
        while True:
            n_pos = rng.choice((3, 4, 5, 6))
            positions = sorted(rng.sample(range(K0, N0), n_pos))
            fhat = [0] * N0
            for pos in positions:
                fhat[pos] = rng.randrange(1, p)
            f = evaluate_dft(fhat, L0, p)
            d = dist_lower_bound_sampling(f, L0, K0, p, n_samples=2000, batch=2048, seed=rng.randrange(10**9))
            if d > W_J:
                if trial_idx == 4:
                    f_target = (f, positions, fhat)
                break
    f, positions, fhat = f_target
    print(f"q={p}, pos={positions}")
    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)
    L1_arr = np.array(L1, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    info_sets = list(combinations(range(n1), k1))
    info_sets_arr = np.array(info_sets, dtype=np.int64)

    # Batched: compute d_1 for each α via max agreement (= info_set with smallest extras)
    d1_dist = {}
    for a in range(p):
        fold = (f_e_arr + a * f_o_arr) % p
        extras = batched_extras(info_sets_arr, fold, L1_arr, D1, inv_D1, p)
        max_agree = int(extras.max())  # max agreement = k_1 + max_agree?
        # Actually batched_extras returns max # of additional matches beyond info-set, so agreement = k_1 + extras
        # And d_1 = n_1 - agreement = n_1 - k_1 - extras = 12 - extras
        d1 = n1 - k1 - max_agree
        d1_dist[d1] = d1_dist.get(d1, 0) + 1

    print(f"d_1 distribution: {sorted(d1_dist.items())}")
    avg = sum(d * c for d, c in d1_dist.items()) / p
    print(f"Average d_1 = {avg:.4f}")
    tie = 1 - avg / n1
    print(f"tie (1-round) = {tie:.4f}")
    print(f"Compared 7/16 = {7/16:.4f}, (1-δ) = 1/2 = {0.5:.4f}")
    print(f"K=1 multi-round bound (R=2): tie ≤ {7/16 + 2/p * 9/16:.4f}")

    # Also compute dist(f_e, C_1) and dist(f_o, C_1)
    extras_fe = batched_extras(info_sets_arr, f_e_arr, L1_arr, D1, inv_D1, p)
    extras_fo = batched_extras(info_sets_arr, f_o_arr, L1_arr, D1, inv_D1, p)
    d_fe = n1 - k1 - int(extras_fe.max())
    d_fo = n1 - k1 - int(extras_fo.max())
    print(f"dist(f_e, C_1) = {d_fe}, dist(f_o, C_1) = {d_fo}")


if __name__ == "__main__":
    main()
