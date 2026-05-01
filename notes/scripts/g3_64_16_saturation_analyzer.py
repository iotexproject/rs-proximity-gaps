"""g3_64_16_saturation_analyzer.py — analyze (64, 16) saturating supports.

For each support that achieves K=2q at (64, 16), characterize:
  - mod-4 quadrant pattern of support
  - L_2 projection positions
  - whether f_o on L_1 is above-J (recursive above-J check)
"""
import sys, os, random, time
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from collections import Counter

from fri_2round_attack import setup_chain, even_odd_parts, modinv
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft(fhat, L, p):
    n = len(L); f = [0]*n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j]: v = (v + fhat[j]*pow(x, j, p)) % p
        f[i] = v
    return f


def support_to_mod4_pattern(sup):
    """Classify each j in support by mod-4 quadrant. Returns (count_0, count_1, count_2, count_3)."""
    cnt = [0, 0, 0, 0]
    for j in sup: cnt[j % 4] += 1
    return tuple(cnt)


def support_to_L2_positions(sup, n0):
    """Get L_2 projection positions (4 quadrants on L_2)."""
    L2_positions = {0: [], 1: [], 2: [], 3: []}
    for j in sup:
        r = j % 4; q = j // 4
        L2_positions[r].append(q)
    return L2_positions


def estimate_d_f(f, L0_arr, n0, k0, info_sets_sample, D0, inv_D0, p):
    f_arr = np.array(f, dtype=np.int64)
    ext = batched_extras(info_sets_sample, f_arr, L0_arr, D0, inv_D0, p)
    return n0 - k0 - int(ext.max())


def main():
    p = 193
    n0, k0, R = 64, 16, 2
    n1, k1 = 32, 8
    w_J_L0 = 32
    w_J_L1 = 16

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]; L1 = chain[1][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1_arr = np.array(L1, dtype=np.int64)
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)

    # Test cases: known saturating + non-saturating supports at (64, 16)
    test_supports = [
        (33, 35, 47),  # known saturating from quick test
        (33, 44, 45),  # NEW: saturating K=386 from above-J sweep
        (39, 40, 41),  # NEW: saturating K=386
        (38, 40, 46),  # NEW: saturating K=386
        (17, 19, 21),  # non-saturating control: all ≡ 1 mod 4
        (17, 19, 23),  # mixed mod-4
        (19, 21, 23),  # all ≡ 3 mod 4
        (16, 17, 18),  # adjacent low
        (16, 32, 48),  # arithmetic progression
        (17, 33, 49),  # arithmetic odd
        (16, 17, 33),  # (e,o,o)
    ]

    # Sample info_sets for d_f estimation
    rng = np.random.default_rng(2026)
    info_sample_n0 = []
    seen = set()
    while len(info_sample_n0) < 50000:
        T = tuple(sorted(rng.choice(n0, size=k0, replace=False).tolist()))
        if T not in seen:
            seen.add(T); info_sample_n0.append(T)
    info_sets_n0 = np.array(info_sample_n0, dtype=np.int64)

    info_sample_n1 = []
    seen = set()
    while len(info_sample_n1) < 5000:
        T = tuple(sorted(rng.choice(n1, size=k1, replace=False).tolist()))
        if T not in seen:
            seen.add(T); info_sample_n1.append(T)
    info_sets_n1 = np.array(info_sample_n1, dtype=np.int64)

    print(f"\n=== (64, 16) saturation analysis at q={p} ===\n")
    print(f"{'sup':<18} {'mod4':<14} {'d_f@L0':<8} {'d_fo@L1':<10} {'d_fold1@L1*':<14}")
    print(f"{'':<18} {'(c0,c1,c2,c3)':<14} {'(>32?)':<8} {'(>16?)':<10} {'(>16 always?)':<14}")
    print("-"*80)

    for sup in test_supports:
        sup_rng = random.Random((42 ^ (hash(sup) & 0xFFFFFFFF)))
        coefs = [sup_rng.randrange(1, p-1) for _ in range(3)]
        fhat = [0]*n0
        for j, c in zip(sup, coefs): fhat[j] = c % p

        f = evaluate_dft(fhat, L0, p)
        d_f = estimate_d_f(f, L0_arr, n0, k0, info_sets_n0, D0, inv_D0, p)

        f_e, f_o = even_odd_parts(f, L0, p)
        # f_o lives on L_1
        d_fo = n1 - k1 - int(batched_extras(info_sets_n1,
                                              np.array(f_o, dtype=np.int64),
                                              L1_arr, D1, inv_D1, p).max())

        # Check d_fold1 = d_1(f_e + α_1·f_o) for a few sample α_1
        fe_arr = np.array(f_e, dtype=np.int64); fo_arr = np.array(f_o, dtype=np.int64)
        d_fold_min = float('inf')
        d_fold_min_alpha = None
        for a1_test in [1, 2, 3, 5, 7, 11, 13]:
            fold1 = (fe_arr + a1_test * fo_arr) % p
            d = n1 - k1 - int(batched_extras(info_sets_n1, fold1,
                                              L1_arr, D1, inv_D1, p).max())
            if d < d_fold_min:
                d_fold_min = d; d_fold_min_alpha = a1_test

        mod4 = support_to_mod4_pattern(sup)

        print(f"{str(sup):<18} {str(mod4):<14} "
              f"{d_f} ({'Y' if d_f > w_J_L0 else 'N'})    "
              f"{d_fo} ({'Y' if d_fo > w_J_L1 else 'N'})      "
              f"{d_fold_min}@α={d_fold_min_alpha} ({'Y' if d_fold_min > w_J_L1 else 'N'})")


if __name__ == "__main__":
    main()
