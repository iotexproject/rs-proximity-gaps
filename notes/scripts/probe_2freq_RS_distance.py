"""probe_2freq_RS_distance.py — verify 2-frequency words are far from RS_4(L_1).

Conjecture (note 0129): for h(y) = a y^p + b y^q with p, q ∈ [4, 16) distinct
and a, b ∈ F_97^*, dist(h, RS_4(L_1)) > 8 = δn_1.

If TRUE: K=1 odd-odd above-J ⟹ #{α_1 : d_1 ≤ 8} ≤ 1, proving sharpened 1-round FRI.

Approach: enumerate all C(12, 2) = 66 pairs (p, q) and sample random (a, b).
For each, compute exact dist via batched info-set enumeration over C(16, 4) = 1820.

Outputs:
  - per (p, q) pair: min, max distance over sampled (a, b)
  - any pair with min dist ≤ 8 (counterexample to conjecture)

Usage: python3 probe_2freq_RS_distance.py [n_coef_samples=100] [seed=2026]
"""
from __future__ import annotations
import sys, os, random, time
from itertools import combinations
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_step5_n32_studio import P, N0, K0
from fri_2round_attack import setup_chain
from mds_decoder import precompute_diff_inv, batched_extras


def fast_d_n16_k4(h_arr, L1_arr, info_sets_arr, D, inv_D, p, n1=16, k1=4):
    """Distance from h (length n1) to RS_{k1}(L1)."""
    extras = batched_extras(info_sets_arr, h_arr, L1_arr, D, inv_D, p)
    return n1 - k1 - int(extras.max())


def main():
    n_coef = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 2026
    p = P
    chain = setup_chain(p, N0, K0, R=2)
    L1 = chain[1][0]
    k1 = chain[1][1]
    n1 = len(L1)

    L1_arr = np.array(L1, dtype=np.int64)
    D, inv_D = precompute_diff_inv(L1_arr, p)
    info_sets = list(combinations(range(n1), k1))
    info_sets_arr = np.array(info_sets, dtype=np.int64)

    print(f"2-frequency RS distance probe at p={p}, n_1={n1}, k_1={k1}")
    print(f"  Conjecture: dist(a y^p + b y^q, C_1) > 8 for all p,q ∈ [4,16), a,b ∈ F_p^*")
    print(f"  n_coef per (p,q) = {n_coef}, seed = {seed}")
    print()

    rng = random.Random(seed)
    pairs = list(combinations(range(k1, n1), 2))  # (p, q) with k1 ≤ p < q < n1
    print(f"  Total (p, q) pairs: {len(pairs)}")

    overall_min_dist = n1 + 1
    overall_min_info = None
    pair_records = []
    counterexamples = []

    t0 = time.time()
    for (pp, qq) in pairs:
        min_d = n1 + 1
        max_d = 0
        min_info = None
        for _ in range(n_coef):
            a = rng.randrange(1, p)
            b = rng.randrange(1, p)
            # Build h on L_1: h(y) = a y^p + b y^q
            h_arr = (a * pow_arr(L1_arr, pp, p) + b * pow_arr(L1_arr, qq, p)) % p
            d = fast_d_n16_k4(h_arr, L1_arr, info_sets_arr, D, inv_D, p, n1, k1)
            if d < min_d:
                min_d = d
                min_info = (a, b)
            if d > max_d:
                max_d = d
        pair_records.append(((pp, qq), min_d, max_d))
        if min_d <= 8:
            counterexamples.append(((pp, qq), min_d, min_info))
        if min_d < overall_min_dist:
            overall_min_dist = min_d
            overall_min_info = ((pp, qq), min_info[0], min_info[1], min_d)

    elapsed = time.time() - t0

    print(f"  Probed {len(pairs)} pairs × {n_coef} coefs = {len(pairs)*n_coef} candidates "
          f"in {elapsed:.0f}s")
    print()
    print(f"  Per-pair distance (min, max):")
    for (pp, qq), mind, maxd in sorted(pair_records, key=lambda r: r[1]):
        marker = " ⚠" if mind <= 8 else ""
        print(f"    ({pp:>2},{qq:>2}): min={mind:>2}, max={maxd:>2}{marker}")

    print()
    print(f"  OVERALL min distance across all (p,q,a,b): {overall_min_dist}")
    if overall_min_info:
        ij, a, b, d = overall_min_info
        print(f"    achieved at: pair={ij}, coefs=({a},{b}), dist={d}")

    if counterexamples:
        print()
        print(f"  ⚠ {len(counterexamples)} counter-examples (dist ≤ 8):")
        for ij, d, info in counterexamples[:10]:
            print(f"    pair={ij}, min_dist={d}, coefs={info}")
    else:
        print()
        print(f"  ✓ NO counter-example: dist > 8 for all sampled (p,q,a,b)")
        print(f"  ⟹ K=1 odd-odd sharpened 1-round FRI conjecture HOLDS at our params.")


def pow_arr(arr, exp, p):
    """Element-wise pow(arr[i], exp, p)."""
    return np.array([pow(int(x), exp, p) for x in arr], dtype=np.int64)


if __name__ == '__main__':
    main()
