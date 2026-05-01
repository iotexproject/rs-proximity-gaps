"""g3_caseB_dist_vs_q.py — measure dist(f, RS_8) for case-(b) f's at various q.

Quantifies: how far above Johnson does case-(b) δ go, as a function of q?

If δ saturates at δ_max < 0.75 (capacity), case-(b) is bounded inside the open zone.
If δ → 1 - rho, case-(b) approaches CS-like construction.

Test q ∈ {97, 193, 257, 449, 769, 1153, 2113, 3329} — primes with 32 | (q-1).
"""
import sys, os, random
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


def dist_to_rs_full(f_arr, L_arr, n, k, D, inv_D, p, batch_size=200000, n_samples=20000):
    """Sampled distance — high confidence above-J detection.
    For these case-(b) f's the dist is generally bounded by structural BCH ≥ 9,
    and we want UPPER bound on max_extras to detect above-J.
    """
    rng = np.random.default_rng(2026)
    all_T = list(combinations(range(n), k))
    if len(all_T) > n_samples:
        idx = rng.choice(len(all_T), size=n_samples, replace=False)
        sampled = [all_T[i] for i in idx]
    else:
        sampled = all_T
    T_arr = np.array(sampled, dtype=np.int64)
    extras = batched_extras(T_arr, f_arr, L_arr, D, inv_D, p)
    return n - k - int(extras.max())


def main():
    n0, k0 = 32, 8
    test_primes = [97, 193, 257, 449, 769, 1153, 2113, 3329]
    test_supports = [(19, 20, 23), (16, 17, 18), (16, 19, 22), (16, 17, 18, 19, 20, 21, 22, 23)]
    n_trials = 5

    print(f"=== dist(f, RS_8) for case-(b) supports vs q ===")
    print(f"w_J = {n0 - 16} = 16; Johnson δ_J = 0.5; capacity δ = 0.75")
    print()
    print(f"{'q':<6} {'support':<35} {'dist range':<14} {'δ range':<14}")
    print("-" * 75)

    for p in test_primes:
        chain = setup_chain(p, n0, k0, R=2)
        L0 = chain[0][0]
        L0_arr = np.array(L0, dtype=np.int64)
        D0, inv_D0 = precompute_diff_inv(L0_arr, p)

        rng = random.Random(2026 + p)
        for pos in test_supports:
            dists = []
            for trial in range(n_trials):
                coeffs = tuple(rng.randint(1, p-1) for _ in pos)
                fhat = [0] * n0
                for ps, c in zip(pos, coeffs):
                    fhat[ps] = c
                f = evaluate_dft(fhat, L0, p)
                f_arr = np.array(f, dtype=np.int64)
                d_f = dist_to_rs_full(f_arr, L0_arr, n0, k0, D0, inv_D0, p)
                dists.append(d_f)
            d_min, d_max = min(dists), max(dists)
            delta_min, delta_max = d_min/n0, d_max/n0
            print(f"{p:<6} {str(pos):<35} {d_min}-{d_max:<11} {delta_min:.3f}-{delta_max:.3f}")
        print()


if __name__ == "__main__":
    main()
