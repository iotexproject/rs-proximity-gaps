"""verify_R3_q193.py — R=3 verification at q=193, comparing to q=97.

Tests K=1 leader pattern at q=193:
  Predicted: tie_upper^(3) at q=193 should be lower than at q=97 (0.4547)
  due to the same mechanism as R=2 (q=97: 0.4490 → q=257: 0.3178).

Chain: (n_0=32, k_0=8, R=3), q=193. n=193-1=192=64·3, so 32 divides p-1. ✓
"""
from __future__ import annotations
import sys, os, time
from itertools import combinations
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

P = 193
N0 = 32
K0 = 8
R = 3

from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft(fhat, L, p):
    return [sum(fhat[k] * pow(L[i], k, p) for k in range(len(fhat))) % p for i in range(len(L))]


CHAIN = setup_chain(P, N0, K0, R=R)
L_chain = [CHAIN[i][0] for i in range(R + 1)]
k_chain = [CHAIN[i][1] for i in range(R + 1)]
n_chain = [len(L) for L in L_chain]
delta_n = [n // 2 for n in n_chain]

# Pre-compute info-set decoders for levels 1, 2.
INFO_DEC = {}
for r in [1, 2]:
    Lr_arr = np.array(L_chain[r], dtype=np.int64)
    Dr, inv_Dr = precompute_diff_inv(Lr_arr, P)
    info_sets = list(combinations(range(n_chain[r]), k_chain[r]))
    info_sets_arr = np.array(info_sets, dtype=np.int64)
    INFO_DEC[r] = (Lr_arr, Dr, inv_Dr, info_sets_arr, n_chain[r], k_chain[r])


def fast_dist(r, fold_arr):
    if r == 3:
        return n_chain[3] - max(Counter(int(v) % P for v in fold_arr).values())
    Lr_arr, Dr, inv_Dr, info_sets_arr, nr, kr = INFO_DEC[r]
    extras = batched_extras(info_sets_arr, fold_arr, Lr_arr, Dr, inv_Dr, P)
    return nr - kr - int(extras.max())


def compute_R3_tie(f):
    L0 = L_chain[0]
    L1 = L_chain[1]
    L2 = L_chain[2]
    L3 = L_chain[3]

    f_e0, f_o0 = even_odd_parts(f, L0, P)
    f_e0_arr = np.array(f_e0, dtype=np.int64)
    f_o0_arr = np.array(f_o0, dtype=np.int64)

    n1, n2, n3 = n_chain[1], n_chain[2], n_chain[3]

    sum_tie = 0.0
    n_tup = 0
    d3_dist = Counter()
    t0 = time.time()
    for a1 in range(P):
        fold1_arr = (f_e0_arr + a1 * f_o0_arr) % P
        d1 = fast_dist(1, fold1_arr)
        f_e1, f_o1 = even_odd_parts(fold1_arr.tolist(), L1, P)
        f_e1_arr = np.array(f_e1, dtype=np.int64)
        f_o1_arr = np.array(f_o1, dtype=np.int64)

        for a2 in range(P):
            fold2_arr = (f_e1_arr + a2 * f_o1_arr) % P
            d2 = fast_dist(2, fold2_arr)
            f_e2, f_o2 = even_odd_parts(fold2_arr.tolist(), L2, P)
            f_e2_arr = np.array(f_e2, dtype=np.int64)
            f_o2_arr = np.array(f_o2, dtype=np.int64)

            for a3 in range(P):
                fold3_arr = (f_e2_arr + a3 * f_o2_arr) % P
                d3 = fast_dist(3, fold3_arr)
                d3_dist[d3] += 1
                m1 = 1.0 - d1 / n1
                m2 = 1.0 - d2 / n2
                m3 = 1.0 - d3 / n3
                sum_tie += max(m1, m2, m3)
                n_tup += 1
        if (a1 + 1) % 25 == 0:
            elapsed = time.time() - t0
            print(f"   α_1 {a1+1}/{P}, elapsed={elapsed:.0f}s, ETA={elapsed*P/(a1+1):.0f}s")
    return sum_tie / n_tup, d3_dist


def main():
    print(f"=== R=3 at q={P} ===")
    print(f"Chain: n = {n_chain}, k = {k_chain}, δn = {delta_n}")
    print(f"q^3 = {P**3:,} tuples per f")
    L0 = L_chain[0]

    cases = [
        ("(15, 23) coefs (10, 17)", 15, 23, 10, 17),
        ("(15, 23) coefs (1, 1)", 15, 23, 1, 1),
        ("(13, 21) coefs (1, 1)", 13, 21, 1, 1),
    ]
    results = []
    for name, p1, p2, c1, c2 in cases:
        print(f"\n--- {name} ---")
        fhat = [0] * N0
        fhat[p1] = c1
        fhat[p2] = c2
        f = evaluate_dft(fhat, L0, P)
        tie, d3d = compute_R3_tie(f)
        deep3 = sum(c for d, c in d3d.items() if d <= delta_n[3])
        print(f"  tie_upper^(3) = {tie:.4f}, #d_3 ≤ 2 = {deep3}")
        print(f"  d_3 dist top: {dict(sorted(d3d.items())[:5])}")
        results.append((name, tie))

    print(f"\n=== Summary q={P} ===")
    for name, tie in results:
        print(f"  {name}: tie^(3) = {tie:.4f}")
    max_tie = max(r[1] for r in results)
    print(f"\nMax K=1 leader tie_upper^(3) at q={P}: {max_tie:.4f}")
    print(f"At q=97 R=3: K=1 leader = 0.4547")
    print(f"Target √ρ = 0.5")


if __name__ == "__main__":
    main()
