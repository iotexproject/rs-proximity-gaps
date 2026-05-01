"""sweep_p257_K1_full.py — sweep all K=1 (i,j) odd-odd pairs at q=257
to find the actual K=1 leader at this q (might differ from q=97 leader).

Tests 66 odd-odd pairs (i,j) with i,j ∈ [k_0=8, n_0=32). For each, tries 3
coef pairs (1,1), (10,17), (37,91) and computes max tie_upper.

Result: 9 cases give tie > 0.5 (gap=2,4,6,16) but ALL are below-J or at-J
when filtered through Lemma 1 (d_1 ≤ 8 ⟹ dist(f, C_0) ≤ 16 = w_J).

True above-J K=1 worst case at q=257: tie ≈ 0.382 (d_1 = 10).

See note 0134 for full analysis.
"""
from __future__ import annotations
import sys, os, time
from itertools import combinations
import numpy as np
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

P = 257
N0 = 32
K0 = 8
R = 2

from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft(fhat, L, p):
    return [sum(fhat[k] * pow(L[i], k, p) for k in range(len(fhat))) % p for i in range(len(L))]


def fast_d1(fold1_arr, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1):
    extras = batched_extras(info_sets_arr, fold1_arr, L1_arr, D1, inv_D1, p)
    return n1 - k1 - int(extras.max())


def fast_d2(fold2, L2, p):
    n2 = len(L2)
    max_agree = 0
    for i, j in combinations(range(n2), 2):
        xi, xj = L2[i], L2[j]
        yi, yj = fold2[i] % p, fold2[j] % p
        if xi == xj: continue
        slope = ((yj - yi) * pow((xj - xi) % p, p - 2, p)) % p
        intercept = (yi - slope * xi) % p
        agree = sum(1 for k in range(n2) if (intercept + slope * L2[k]) % p == fold2[k] % p)
        if agree > max_agree: max_agree = agree
    return n2 - max_agree


def compute_tie_robust(f, chain, p):
    L0 = chain[0][0]
    L1, k1, _ = chain[1]
    L2, k2, _ = chain[2]
    n1, n2 = len(L1), len(L2)

    L1_arr = np.array(L1, dtype=np.int64)
    L2_list = list(L2)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    info_sets = list(combinations(range(n1), k1))
    info_sets_arr = np.array(info_sets, dtype=np.int64)

    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)

    sum_tie = 0.0
    d1_dist = Counter()
    for a1 in range(p):
        fold1_arr = (f_e_arr + a1 * f_o_arr) % p
        d1 = fast_d1(fold1_arr, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1)
        d1_dist[d1] += 1
        fold1 = fold1_arr.tolist()
        g_e, g_o = even_odd_parts(fold1, L1, p)
        for a2 in range(p):
            fold2 = [(g_e[j] + a2 * g_o[j]) % p for j in range(n2)]
            d2 = fast_d2(fold2, L2_list, p)
            P_B = 1.0 - d2 / n2
            P_A_ub = 1.0 - d1 / n1
            sum_tie += max(P_A_ub, P_B)
    return (sum_tie / (p*p), d1_dist)


def main():
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L0 = chain[0][0]
    print(f"=== q={p} K=1 sweep over all odd-odd pairs in [k_0, n_0) ===")
    n1 = N0 // 2
    print(f"Chain: n_1 = {n1}, k_1 = 4, δn_1 = 8")

    odd_positions = [i for i in range(K0, N0) if i % 2 == 1]
    pairs = list(combinations(odd_positions, 2))
    print(f"Odd-odd pairs in [{K0}, {N0}): {len(pairs)} pairs")

    results = []
    for i, j in pairs:
        max_tie_pair = 0.0
        max_d1_pair = None
        for c1, c2 in [(1, 1), (10, 17), (37, 91)]:
            fhat = [0] * N0
            fhat[i] = c1
            fhat[j] = c2
            f = evaluate_dft(fhat, L0, p)
            tie, d1d = compute_tie_robust(f, chain, p)
            if tie > max_tie_pair:
                max_tie_pair = tie
                max_d1_pair = dict(sorted(d1d.items()))
        gap = j - i
        results.append((i, j, gap, max_tie_pair, max_d1_pair))
        marker = " ★" if gap == 8 else ""
        print(f"  ({i},{j}) gap={gap}{marker}: max_tie={max_tie_pair:.4f}, d_1 dist={max_d1_pair}")

    print("\n=== Top 5 K=1 odd-odd cases at q=257 ===")
    results.sort(key=lambda r: -r[3])
    for i, j, gap, tie, d1d in results[:5]:
        print(f"  ({i},{j}) gap={gap}: tie={tie:.4f}, d_1={d1d}")

    print(f"\nMax tie_upper for K=1 odd-odd at q=257: {results[0][3]:.4f}")
    print(f"Compared to q=97: 0.4490")


if __name__ == "__main__":
    main()
