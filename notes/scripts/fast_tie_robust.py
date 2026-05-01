"""fast_tie_robust.py — fast tie_robust_upper computation via review's decoder approach.

Two key speedups vs audit_tie_robust_upper.py:
  (1) Level-1 distance via vectorized info-set enumeration (C(16,4)=1820, batched_extras).
  (2) Level-2 distance via line enumeration (C(8,2)=28 — trivial).

Empirical: ~30-60s per f vs ~600s for the brute-force audit.

Validates against the K=1 leader (15,23) coefs (10,17) → tie_upper = 0.4490.

Usage:
  python3 fast_tie_robust.py                # run validation + K=2 dense 24-pos
  python3 fast_tie_robust.py --validate     # only validate K=1 leader
"""
from __future__ import annotations
import sys, os, time, argparse
from itertools import combinations
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_step5_n32_studio import P, N0, K0, R, N_R, W_J, evaluate_dft
from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


def fast_d1(fold1_arr, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1):
    """Distance from fold1 to RS_{k1}(L1) via info-set enumeration.

    Returns d1. Valid when d1 ≤ n1 - k1 (max agreement found by some info set).
    """
    extras = batched_extras(info_sets_arr, fold1_arr, L1_arr, D1, inv_D1, p)
    max_extras = int(extras.max())
    return n1 - k1 - max_extras


def fast_d2(fold2, L2, p):
    """Distance from fold2 (length n2=8) to RS_2(L2) via line enumeration over C(8,2)=28."""
    n2 = len(L2)
    max_agree = 0
    for i, j in combinations(range(n2), 2):
        xi, xj = L2[i], L2[j]
        yi, yj = fold2[i] % p, fold2[j] % p
        if xi == xj:
            continue
        slope = ((yj - yi) * pow((xj - xi) % p, p - 2, p)) % p
        intercept = (yi - slope * xi) % p
        agree = sum(1 for k in range(n2) if (intercept + slope * L2[k]) % p == fold2[k] % p)
        if agree > max_agree:
            max_agree = agree
    return n2 - max_agree


def compute_tie_robust_fast(f, chain, p):
    """Same outputs as audit_tie_robust_upper.compute_tie_robust but ~10-20x faster."""
    L0, _, _ = chain[0]
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

    sum_PB = 0.0
    sum_tie = 0.0
    d1_dist, d2_dist = {}, {}
    joint = {}

    for a1 in range(p):
        fold1_arr = (f_e_arr + a1 * f_o_arr) % p
        d1 = fast_d1(fold1_arr, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1)
        d1_dist[d1] = d1_dist.get(d1, 0) + 1
        fold1 = fold1_arr.tolist()
        g_e, g_o = even_odd_parts(fold1, L1, p)
        for a2 in range(p):
            fold2 = [(g_e[j] + a2 * g_o[j]) % p for j in range(n2)]
            d2 = fast_d2(fold2, L2_list, p)
            d2_dist[d2] = d2_dist.get(d2, 0) + 1
            joint[(d1, d2)] = joint.get((d1, d2), 0) + 1
            P_B = 1.0 - d2 / n2
            P_A_ub = 1.0 - d1 / n1
            sum_PB += P_B
            sum_tie += max(P_A_ub, P_B)

    n_pairs = p * p
    return (sum_PB / n_pairs, sum_tie / n_pairs, d1_dist, d2_dist, joint)


def make_rank1_two_freq(positions, coefs, p, L0):
    fhat = [0] * N0
    for pos, c in zip(positions, coefs):
        fhat[pos] = c
    return evaluate_dft(fhat, L0, p)


FHAT_NONZERO_K2_DENSE = [
    (8, 85), (9, 73), (10, 61), (11, 25),
    (12, 53), (13, 9), (14, 62), (15, 80),
    (16, 21), (17, 42), (18, 63), (19, 22),
    (20, 4), (21, 8), (22, 12), (23, 91),
    (24, 63), (25, 29), (26, 92), (27, 13),
    (28, 6), (29, 12), (30, 18), (31, 89),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--validate', action='store_true')
    args = parser.parse_args()

    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L0 = chain[0][0]

    print(f"Fast tie_robust_upper at p={p}")
    print()

    # (a) Validation
    print("=" * 70)
    print("(a) Validation: K=1 leader (15,23) coefs (10,17), expect tie_upper=0.4490")
    print("=" * 70)
    f = make_rank1_two_freq((15, 23), (10, 17), p, L0)
    t0 = time.time()
    P_B, tie, d1d, d2d, jd = compute_tie_robust_fast(f, chain, p)
    t1 = time.time() - t0
    print(f"  P_B = {P_B:.6f}  tie_upper = {tie:.6f}  ({t1:.1f}s)")
    if abs(tie - 0.449038) < 0.001:
        print(f"  ✓ matches 0.449038")
    else:
        print(f"  ⚠ mismatch — expected 0.4490")
    print(f"  d_1: {sorted(d1d.items())}")
    print()

    if args.validate:
        return

    # (b) K=2 dense 24-pos
    print("=" * 70)
    print("(b) K=2 dense 24-pos counterexample (review note 0114)")
    print("=" * 70)
    fhat = [0] * N0
    for idx, val in FHAT_NONZERO_K2_DENSE:
        fhat[idx] = val
    f = evaluate_dft(fhat, L0, p)
    t0 = time.time()
    P_B, tie, d1d, d2d, jd = compute_tie_robust_fast(f, chain, p)
    t1 = time.time() - t0
    print(f"  P_B = {P_B:.6f}  tie_upper = {tie:.6f}  ({t1:.1f}s)")
    print(f"  d_1: {sorted(d1d.items())}")
    print(f"  d_2 (top 5): {sorted(d2d.items())[:5]}")
    top_joint = sorted(jd.items(), key=lambda x: -x[1])[:5]
    print(f"  top joint cells: {top_joint}")
    n_low = sum(c for d, c in d1d.items() if d <= 8)
    print(f"  #(d_1 ≤ 8) = {n_low}")
    print()

    K1_leader_max = 0.4490
    K2_breach_max = 0.4477
    if tie > K1_leader_max:
        print(f"  ⚠ NEW UNIVERSAL MAX: K=2 dense 24-pos {tie:.4f} > K=1 leader {K1_leader_max:.4f}")
    elif tie > K2_breach_max:
        print(f"  ◎ K=2 dense beats K=2 sparse breaches but not K=1 leader")
    else:
        print(f"  ✓ K=2 dense ({tie:.4f}) does NOT beat K=1 leader → 0.449 cap holds")


if __name__ == '__main__':
    main()
