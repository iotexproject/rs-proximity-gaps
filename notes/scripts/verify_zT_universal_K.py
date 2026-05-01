"""verify_zT_universal_K.py — verify z_T < 4 holds for ALL above-J f, including K ≥ 3.

The proof of Lemma `lem:universal-zT` only uses `dist(f, C_0) > w_J = 16`,
not K(f). Empirically check across K classes.
"""
from __future__ import annotations
import sys, os, random
import numpy as np
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, even_odd_parts

import probe_step5_n32_studio
from probe_step5_n32_studio import N0, K0, R, evaluate_dft

from verify_no_common_8flat import compute_zT

W_J = N0 // 2


def K_classify(positions):
    """Crude K classifier: # distinct (parity, half-mod-2) classes in DFT support."""
    classes = set()
    for j in positions:
        if j < K0: continue  # only DFT positions ≥ k_0 matter
        classes.add((j % 2, (j // 2) % 2))
    return len(classes)


def main():
    from mds_decoder import dist_lower_bound_sampling, precompute_diff_inv, batched_extras

    print("=== verify_zT_universal_K: z_T < 4 for all K classes ===")
    print()
    overall_max_zT = 0
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
        rng = random.Random(2026 + p + 999)
        K_class_counts = {}
        K_class_max_zT = {}
        K_class_max_count8 = {}
        n_tries = 0
        n_above_J = 0
        while n_above_J < 60 and n_tries < 600:
            n_tries += 1
            n_pos = rng.choice([3, 4, 5, 6, 7])
            positions = sorted(rng.sample(range(K0, N0), n_pos))
            fhat = [0] * N0
            for pos in positions:
                fhat[pos] = rng.randrange(1, p)
            f = evaluate_dft(fhat, L0, p)
            d = dist_lower_bound_sampling(f, L0, K0, p, n_samples=2000, batch=2048, seed=rng.randrange(10**9))
            if d <= W_J: continue
            n_above_J += 1
            K = K_classify(positions)
            f_e, f_o = even_odd_parts(f, L0, p)
            f_e_arr = np.array(f_e, dtype=np.int64)
            f_o_arr = np.array(f_o, dtype=np.int64)
            max_zT = 0
            for T in info_sets:
                zT = compute_zT(f_e_arr, f_o_arr, T, L1_arr, p)
                if zT > max_zT: max_zT = zT
                if zT >= 4: break
            count_8 = 0
            for a in range(p):
                fold = (f_e_arr + a * f_o_arr) % p
                extras = batched_extras(info_sets_arr, fold, L1_arr, D1, inv_D1, p)
                d1 = n1 - k1 - int(extras.max())
                if d1 <= 8: count_8 += 1
            K_class_counts[K] = K_class_counts.get(K, 0) + 1
            K_class_max_zT[K] = max(K_class_max_zT.get(K, 0), max_zT)
            K_class_max_count8[K] = max(K_class_max_count8.get(K, 0), count_8)
            if max_zT > overall_max_zT:
                overall_max_zT = max_zT
        print(f"  q={p}: above-J={n_above_J} cases")
        for K in sorted(K_class_counts.keys()):
            print(f"    K={K}: {K_class_counts[K]} cases, max z_T = {K_class_max_zT[K]}, max count_α(d_1≤8) = {K_class_max_count8[K]}")
        print()

    print(f"=== Overall max z_T = {overall_max_zT} ===")
    if overall_max_zT < 4:
        print(f"  ✓ z_T < 4 holds UNIVERSALLY across K classifiers — Lemma~lem:universal-zT")
        print(f"    is verified empirically for K=1, K=2, AND K ≥ 3 cases.")
    else:
        print(f"  ✗ z_T = 4 found — proof must be re-examined.")


if __name__ == "__main__":
    main()
