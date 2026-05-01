"""g3_sanity_q97.py — sanity-check the dist computation at q=97.

If this passes (count=8 confirmed for the known witness), the same dist code at
q=1153 is probably correct → count=1153 is real.
If this fails, the dist computation has a bug we need to find.

Compares the count=8 witness from notes 0156/0157 (pos=[18,19,30], coeffs=(10,92,63)
at q=97) by recomputing bad-α set and checking it matches B = 2 + 19·μ_8 = {21, 22, 32, 47, 54, 69, 79, 80}.

Single-threaded; should run in <30 seconds.
"""
import sys, os, time
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from collections import Counter

from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft(fhat, L, p):
    n = len(L)
    f = [0] * n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j] != 0:
                v = (v + fhat[j] * pow(x, j, p)) % p
        f[i] = v
    return f


def dist_to_rs(f_arr, L_arr, n, k, D, inv_D, p):
    info_sets = list(combinations(range(n), k))
    info_sets_arr = np.array(info_sets, dtype=np.int64)
    extras = batched_extras(info_sets_arr, f_arr, L_arr, D, inv_D, p)
    return n - k - int(extras.max())


def main():
    p = 97
    n0, k0 = 32, 8
    pos = (18, 19, 30)
    coeffs = (10, 92, 63)
    expected_bad = {21, 22, 32, 47, 54, 69, 79, 80}

    print(f"=== Sanity check at q={p}, pos={pos}, coeffs={coeffs} ===")
    print(f"Expected bad α set: B = 2 + 19·μ_8 = {sorted(expected_bad)}")

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1 = chain[1][0]
    L1_arr = np.array(L1, dtype=np.int64)
    n1, k1 = len(L1), k0 // 2
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    print(f"  n_0={n0}, k_0={k0}, n_1={n1}, k_1={k1}")

    fhat = [0] * n0
    for ps, c in zip(pos, coeffs):
        fhat[ps] = c
    f = evaluate_dft(fhat, L0, p)
    f_arr = np.array(f, dtype=np.int64)
    n_zeros = sum(1 for v in f if v == 0)
    print(f"  f n_zeros = {n_zeros}")

    d_f = dist_to_rs(f_arr, L0_arr, n0, k0, D0, inv_D0, p)
    print(f"  dist(f, RS_8 on L_0) = {d_f}  (should be > w_J=16 for above-J)")

    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)

    d_e = dist_to_rs(f_e_arr, L1_arr, n1, k1, D1, inv_D1, p)
    d_o = dist_to_rs(f_o_arr, L1_arr, n1, k1, D1, inv_D1, p)
    print(f"  dist(f_e, RS_4 on L_1) = {d_e}")
    print(f"  dist(f_o, RS_4 on L_1) = {d_o}")

    threshold = 8
    print(f"\n  Scanning all {p} alphas, threshold dist ≤ {threshold}...")
    t0 = time.time()
    bad = []
    dist_hist = Counter()
    for a in range(p):
        fold = (f_e_arr + a * f_o_arr) % p
        d1 = dist_to_rs(fold, L1_arr, n1, k1, D1, inv_D1, p)
        dist_hist[d1] += 1
        if d1 <= threshold:
            bad.append(a)
    elapsed = time.time() - t0
    print(f"  Scan complete in {elapsed:.1f}s")
    print(f"  |bad α| = {len(bad)}: {bad}")
    print(f"  Distance histogram:")
    for d in sorted(dist_hist):
        print(f"    d={d}: {dist_hist[d]:3d} alphas{'  *BAD*' if d <= threshold else ''}")

    matched = set(bad) == expected_bad
    print(f"\n  Match expected? {'YES ✓' if matched else 'NO ✗'}")
    if not matched:
        print(f"    extra in computed: {set(bad) - expected_bad}")
        print(f"    missing from computed: {expected_bad - set(bad)}")


if __name__ == "__main__":
    main()
