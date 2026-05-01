"""K(f_1, f_2) sweep using GS Sudan(m=2) — reaches Johnson at (16,4),
τ=15 at (32,8).

For deployment-scale (32,8), m=3 needed for J=16 exact, but m=2 τ=15
already differentiates sparse vs dense for the above-J empirical.
"""
from __future__ import annotations

import random
import sys
import time

from gs_sudan_m2 import (
    primitive_root_of_unity, gs_decode_m2, encode_rs, hamming, find_d_for_n_m,
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


def K_via_gs_m2(p, omega, n, k, f1, f2, d=None, tau=None):
    """Count α ∈ F_q^* with non-empty Sudan(m=2) decoder list at radius τ."""
    if d is None:
        d = find_d_for_n_m(n, k, m=2)
    if tau is None:
        tau = (n * 2 - d - 1) // 2  # τ < n - d/2 ⟹ τ ≤ floor((2n - d - 1)/2)

    count = 0
    matched = []
    for alpha in range(1, p):
        h = [(f1[j] + alpha * f2[j]) % p for j in range(n)]
        decoded = gs_decode_m2(p, omega, n, k, h, d=d)
        for msg in decoded:
            cw = encode_rs(p, omega, n, k, msg)
            if hamming(h, cw) <= tau:
                count += 1
                matched.append(alpha)
                break
    return count, matched


def focused_gs_m2_sweep(p, n, k, n_random_per_s=10, seed=42, max_s=None):
    rng = random.Random(seed)
    omega = primitive_root_of_unity(p, n)
    if omega is None:
        print(f"  no primitive {n}-th root in GF({p})")
        return
    d = find_d_for_n_m(n, k, m=2)
    tau = (n * 2 - d - 1) // 2
    J = n - int((n * k) ** 0.5)
    print(f"\n=== Sudan(m=2) K-sweep p={p}, ({n},{k}), d={d}, τ={tau}, J={J} ===")

    above_J = list(range(k, n))
    if max_s is None:
        max_s = len(above_J)
    rows = []
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
            K, _ = K_via_gs_m2(p, omega, n, k, f1, f2, d=d, tau=tau)
            if K > max_K:
                max_K = K
                best = (supp1, supp2)
        elapsed = time.time() - t0
        rows.append((s, max_K, best))
        print(f"  s={s}: max K = {max_K} ({best}) [{elapsed:.1f}s, {n_random_per_s} trials]")

    max_K_dense = 0
    t0 = time.time()
    for trial in range(n_random_per_s):
        f1 = [rng.randint(0, p - 1) for _ in range(n)]
        f2 = [rng.randint(0, p - 1) for _ in range(n)]
        K, _ = K_via_gs_m2(p, omega, n, k, f1, f2, d=d, tau=tau)
        if K > max_K_dense:
            max_K_dense = K
    elapsed = time.time() - t0
    print(f"  dense: max K = {max_K_dense} [{elapsed:.1f}s, {n_random_per_s} trials]")
    return rows, max_K_dense


def main():
    targets = sys.argv[1:] if len(sys.argv) > 1 else ['16_4_17', '16_4_97']
    for tgt in targets:
        if tgt == '16_4_17':
            print("--- (16, 4) p=17, Sudan(m=2) τ=Johnson=8 ---")
            focused_gs_m2_sweep(p=17, n=16, k=4, n_random_per_s=30)
        elif tgt == '16_4_97':
            print("\n--- (16, 4) p=97, Sudan(m=2) τ=Johnson=8 ---")
            focused_gs_m2_sweep(p=97, n=16, k=4, n_random_per_s=8, max_s=6)
        elif tgt == '32_8_257':
            print("\n--- (32, 8) p=257, Sudan(m=2) τ=15 (J-1=15) ---")
            focused_gs_m2_sweep(p=257, n=32, k=8, n_random_per_s=2, max_s=5)
        else:
            print(f"Unknown: {tgt}")


if __name__ == '__main__':
    main()
