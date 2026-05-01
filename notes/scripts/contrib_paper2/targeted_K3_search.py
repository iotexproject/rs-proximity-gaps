"""Targeted search: find 3-mono configurations approaching paper2 K_3 ≤ 10.

paper2 thm:universal-K10 says K_3 ≤ 10 (algebraic, over Q-bar). For specific
F_q, K_q ≤ K_alg with equality if all 10 roots split over F_q.

Run heavy random search at (16, 4) p=97 with n_random=300 to find max K_3
empirical. If max K_3 reaches near 10, validates that random 3-mono can
achieve close to algebraic bound.
"""
from __future__ import annotations

import random
import sys
import time
import itertools

from gs_sudan_m2_np import gs_decode_m2_np
from gs_sudan_m2 import (
    primitive_root_of_unity, encode_rs, hamming, find_d_for_n_m,
)


def make_sparse_pencil(p, n, omega, supp1, supp2, c1, c2):
    f1 = [0] * n
    f2 = [0] * n
    for j in range(n):
        for a, c in zip(supp1, c1):
            f1[j] = (f1[j] + c * pow(omega, a * j, p)) % p
        for a, c in zip(supp2, c2):
            f2[j] = (f2[j] + c * pow(omega, a * j, p)) % p
    return f1, f2


def K_via_gs_m2(p, omega, n, k, f1, f2, d, tau):
    count = 0
    for alpha in range(1, p):
        h = [(f1[j] + alpha * f2[j]) % p for j in range(n)]
        decoded = gs_decode_m2_np(p, omega, n, k, h, d=d)
        for msg in decoded:
            cw = encode_rs(p, omega, n, k, msg)
            if hamming(h, cw) <= tau:
                count += 1
                break
    return count


def heavy_search(p, n, k, s_target, n_trials, seed=42):
    rng = random.Random(seed)
    omega = primitive_root_of_unity(p, n)
    d = find_d_for_n_m(n, k, m=2)
    tau = (n * 2 - d - 1) // 2
    above_J = list(range(k, n))

    print(f"=== Heavy search at p={p}, ({n},{k}), s={s_target}, τ={tau} ===")
    print(f"  above-J pool size: {len(above_J)}, max trials = {n_trials}")

    max_K = 0
    best = None
    K_distribution = {}
    t0 = time.time()
    for trial in range(n_trials):
        supp1 = sorted(rng.sample(above_J, s_target))
        supp2 = sorted(rng.sample(above_J, s_target))
        cs1 = [rng.randint(1, p - 1) for _ in supp1]
        cs2 = [rng.randint(1, p - 1) for _ in supp2]
        f1, f2 = make_sparse_pencil(p, n, omega, supp1, supp2, cs1, cs2)
        K = K_via_gs_m2(p, omega, n, k, f1, f2, d, tau)
        K_distribution[K] = K_distribution.get(K, 0) + 1
        if K > max_K:
            max_K = K
            best = (supp1, supp2, cs1, cs2)
            print(f"  trial {trial}: K={K} new max! supp1={supp1}, supp2={supp2}, c1={cs1}, c2={cs2}")
        if (trial + 1) % 100 == 0:
            print(f"  [progress] {trial+1}/{n_trials}, max K so far = {max_K}, elapsed {time.time()-t0:.0f}s")

    print(f"\n  Final: max K_{s_target} = {max_K}")
    print(f"  K distribution: {sorted(K_distribution.items())}")
    print(f"  Time: {time.time()-t0:.0f}s")
    return max_K, best


def main():
    if len(sys.argv) > 1:
        s = int(sys.argv[1])
    else:
        s = 3
    n_trials = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    print(f"Searching s={s} with {n_trials} trials...")
    heavy_search(p=97, n=16, k=4, s_target=s, n_trials=n_trials)


if __name__ == '__main__':
    main()
