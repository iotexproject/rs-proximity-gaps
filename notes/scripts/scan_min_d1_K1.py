"""scan_min_d1_K1.py — for each q, scan all K=1 odd-odd 2-freq words and find
minimum d_1 (subject to above-J).

Above-J ⟺ min_{α≠0} d_1 ≥ 9. Among above-J f's, what's the smallest d_1 achievable?
At q=97: empirical min = 9 (the (15,23) leader saturates).
At q=257: full sweep showed min d_1 = 10 (no d_1 = 9).
This script: confirm at q=193 and q=449.
"""
from __future__ import annotations
import sys, os
from itertools import combinations
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

N0 = 32
K0 = 8

from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft(fhat, L, p):
    return [sum(fhat[k] * pow(L[i], k, p) for k in range(len(fhat))) % p for i in range(len(L))]


def fast_d1(fold_arr, L_arr, info_sets_arr, D, inv_D, p, n, k):
    extras = batched_extras(info_sets_arr, fold_arr, L_arr, D, inv_D, p)
    return n - k - int(extras.max())


def scan_q(p):
    chain = setup_chain(p, N0, K0, R=2)
    L0 = chain[0][0]
    L1 = chain[1][0]
    k1 = chain[1][1]
    n1 = len(L1)
    L1_arr = np.array(L1, dtype=np.int64)
    D, invD = precompute_diff_inv(L1_arr, p)
    info_sets = list(combinations(range(n1), k1))
    info_sets_arr = np.array(info_sets, dtype=np.int64)

    odd_positions = [i for i in range(K0, N0) if i % 2 == 1]
    pairs = list(combinations(odd_positions, 2))

    min_d1_above_J = n1
    min_pair = None
    for i, j in pairs:
        # Try a few coefs to see if any gives above-J with low d_1
        for c1, c2 in [(1, 1), (1, 2), (1, 3), (2, 1), (3, 1), (10, 17), (37, 91), (5, 7), (7, 5)]:
            fhat = [0] * N0
            fhat[i] = c1
            fhat[j] = c2
            f = evaluate_dft(fhat, L0, p)
            f_e, f_o = even_odd_parts(f, L0, p)
            f_e_arr = np.array(f_e, dtype=np.int64)
            f_o_arr = np.array(f_o, dtype=np.int64)
            # Min d_1 over all α_1 ≠ 0
            min_d_here = n1
            for a1 in range(1, p):
                fold_arr = (f_e_arr + a1 * f_o_arr) % p
                d = fast_d1(fold_arr, L1_arr, info_sets_arr, D, invD, p, n1, k1)
                if d < min_d_here:
                    min_d_here = d
            # Above-J via Lemma 1: min_d ≥ 9
            if min_d_here >= 9 and min_d_here < min_d1_above_J:
                min_d1_above_J = min_d_here
                min_pair = (i, j, c1, c2)
    return min_d1_above_J, min_pair


def main():
    for p in [97, 193, 257, 449]:
        print(f"=== q={p} ===")
        min_d1, pair = scan_q(p)
        print(f"  Min d_1 (above-J K=1 odd-odd): {min_d1}, achieved at pair/coefs: {pair}")
        # Predicted tie_upper at min_d_1
        if pair:
            n1 = 16
            generic = 1 - min_d1 / n1
            cascade_boost = (2/p) * (0.5 + 1/n1)
            predicted = generic + cascade_boost
            print(f"  Predicted tie_upper ≈ {predicted:.4f}")


if __name__ == "__main__":
    main()
