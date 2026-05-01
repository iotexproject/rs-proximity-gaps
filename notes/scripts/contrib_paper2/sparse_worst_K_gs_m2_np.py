"""K-sweep using numpy-accelerated Sudan(m=2) — for deployment empirical."""
from __future__ import annotations

import random
import sys
import time

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


def sweep(p, n, k, n_random_per_s, max_s, seed=42):
    rng = random.Random(seed)
    omega = primitive_root_of_unity(p, n)
    if omega is None:
        print("  no primitive root")
        return
    d = find_d_for_n_m(n, k, m=2)
    tau = (n * 2 - d - 1) // 2
    J = n - int((n * k) ** 0.5)
    print(f"\n=== {p=}, ({n},{k}), d={d}, τ={tau}, J={J} ===")

    above_J = list(range(k, n))
    rows = []
    overall_t0 = time.time()
    for s in range(2, max_s + 1):
        max_K = 0
        best = None
        t0 = time.time()
        for trial in range(n_random_per_s):
            supp1 = sorted(rng.sample(above_J, s))
            supp2 = sorted(rng.sample(above_J, s))
            cs1 = [rng.randint(1, p - 1) for _ in supp1]
            cs2 = [rng.randint(1, p - 1) for _ in supp2]
            f1, f2 = make_sparse_pencil(p, n, omega, supp1, supp2, cs1, cs2)
            K = K_via_gs_m2(p, omega, n, k, f1, f2, d, tau)
            if K > max_K:
                max_K = K
                best = (supp1, supp2)
        elapsed = time.time() - t0
        rows.append((s, max_K))
        print(f"  s={s}: max K = {max_K} ({best}) [{elapsed:.0f}s, {n_random_per_s} trials]")

    max_K_dense = 0
    t0 = time.time()
    for trial in range(n_random_per_s):
        f1 = [rng.randint(0, p - 1) for _ in range(n)]
        f2 = [rng.randint(0, p - 1) for _ in range(n)]
        K = K_via_gs_m2(p, omega, n, k, f1, f2, d, tau)
        if K > max_K_dense:
            max_K_dense = K
    elapsed = time.time() - t0
    print(f"  dense: max K = {max_K_dense} [{elapsed:.0f}s, {n_random_per_s} trials]")
    print(f"\n  TOTAL: {time.time()-overall_t0:.0f}s")
    return rows, max_K_dense


def main():
    targets = sys.argv[1:] if len(sys.argv) > 1 else ['16_4_97', '32_8_257']
    for tgt in targets:
        if tgt == '16_4_97':
            print("--- (16, 4) p=97 numpy ---")
            sweep(p=97, n=16, k=4, n_random_per_s=30, max_s=6)
        elif tgt == '32_8_257':
            print("\n--- (32, 8) p=257 numpy ---")
            sweep(p=257, n=32, k=8, n_random_per_s=15, max_s=5)
        elif tgt == '32_8_577':
            # 577-1 = 576 = 32*18, smaller deployment-scale prime with 32 | (q-1)
            print("\n--- (32, 8) p=577 numpy ---")
            sweep(p=577, n=32, k=8, n_random_per_s=10, max_s=5)


if __name__ == '__main__':
    main()
