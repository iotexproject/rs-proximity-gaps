"""K(f_1, f_2) sweep using GS Sudan list-decoder.

Polynomial in q (not q^k) — works at deployment scale.

K(f_1, f_2; τ) := #{ α ∈ F_q^* : GS_decode(f_1 + α·f_2, τ) is non-empty }

This is a PROXY for K_Johnson — at Sudan(m=1), τ < Johnson.
"""
from __future__ import annotations

import random
import sys
import time

from gs_sudan import (
    primitive_root_of_unity, encode_rs, gs_decode, hamming, find_d_for_n,
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


def K_via_gs(p, omega, n, k, f1, f2, d=None):
    """Count α ∈ F_q^* such that GS-decode(f_1 + α f_2) is non-empty."""
    if d is None:
        d = find_d_for_n(n, k)
    count = 0
    matched = []
    for alpha in range(1, p):
        h = [(f1[j] + alpha * f2[j]) % p for j in range(n)]
        decoded = gs_decode(p, omega, n, k, h, d=d)
        # Filter: codeword within Sudan τ (auto-satisfied since interpolation
        # only finds codewords within τ at multiplicity m=1).
        # Verify: decoded msg → recompute codeword → Hamming dist.
        # GS gives candidates; filter to those within τ = n - d - 1
        tau = n - d - 1
        for msg in decoded:
            cw = encode_rs(p, omega, n, k, msg)
            if hamming(h, cw) <= tau:
                count += 1
                matched.append((alpha, msg))
                break
    return count, matched


def focused_gs_sweep(p, n, k, n_random_per_s=10, seed=42):
    rng = random.Random(seed)
    omega = primitive_root_of_unity(p, n)
    if omega is None:
        print(f"  no primitive {n}-th root in GF({p}), skipping")
        return
    d = find_d_for_n(n, k)
    tau = n - d - 1
    print(f"\n=== GS K-sweep at p={p}, ({n}, {k}), τ={tau} ===")

    above_J = list(range(k, n))
    rows = []
    for s in range(2, len(above_J) + 1):
        max_K = 0
        best = None
        t0 = time.time()
        for trial in range(n_random_per_s):
            supp1 = sorted(rng.sample(above_J, s))
            supp2 = sorted(rng.sample(above_J, s))
            cs1 = [rng.randint(1, p - 1) for _ in supp1]
            cs2 = [rng.randint(1, p - 1) for _ in supp2]
            f1, f2 = make_sparse_pencil(p, n, omega, supp1, supp2, cs1, cs2)
            K, _ = K_via_gs(p, omega, n, k, f1, f2, d=d)
            if K > max_K:
                max_K = K
                best = (supp1, supp2)
        elapsed = time.time() - t0
        rows.append((s, max_K, best))
        print(f"  s={s}: max K = {max_K} ({best}) [{elapsed:.1f}s, {n_random_per_s} trials]")

    # Dense baseline
    max_K_dense = 0
    t0 = time.time()
    for trial in range(n_random_per_s):
        f1 = [rng.randint(0, p - 1) for _ in range(n)]
        f2 = [rng.randint(0, p - 1) for _ in range(n)]
        K, _ = K_via_gs(p, omega, n, k, f1, f2, d=d)
        if K > max_K_dense:
            max_K_dense = K
    elapsed = time.time() - t0
    print(f"  dense: max K = {max_K_dense} [{elapsed:.1f}s, {n_random_per_s} trials]")
    return rows, max_K_dense


def main():
    targets = sys.argv[1:] if len(sys.argv) > 1 else ['8_2_17', '16_4_17', '16_4_97']
    for tgt in targets:
        if tgt == '8_2_17':
            print("--- (8, 2) at p=17, GS Sudan ---")
            focused_gs_sweep(p=17, n=8, k=2, n_random_per_s=50)
        elif tgt == '16_4_17':
            print("\n--- (16, 4) at p=17, GS Sudan ---")
            focused_gs_sweep(p=17, n=16, k=4, n_random_per_s=80)
        elif tgt == '16_4_97':
            print("\n--- (16, 4) at p=97, GS Sudan ---")
            focused_gs_sweep(p=97, n=16, k=4, n_random_per_s=20)
        elif tgt == '32_8_257':
            print("\n--- (32, 8) at p=257, GS Sudan ---")
            focused_gs_sweep(p=257, n=32, k=8, n_random_per_s=4)
        else:
            print(f"Unknown target: {tgt}")


if __name__ == '__main__':
    main()
