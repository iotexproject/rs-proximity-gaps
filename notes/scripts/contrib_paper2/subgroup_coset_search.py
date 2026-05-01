"""Targeted search on subgroup-coset structured supports.

K_3 = 6 was found with supp [4, 8, 12] (subgroup of Z/16 ∩ above-J). Try
all subgroup-cosets at (16, 4) and find max K.

Subgroups of Z/16:
  H_2 = {0, 8}
  H_4 = {0, 4, 8, 12}
  H_8 = {0, 2, 4, ..., 14}

Cosets of H_4 in Z/16:
  {0, 4, 8, 12}
  {1, 5, 9, 13}
  {2, 6, 10, 14}
  {3, 7, 11, 15}

In above-J (positions ∈ [4, 15]):
  H_4 ∩ above-J = {4, 8, 12}
  (1+H_4) ∩ above-J = {5, 9, 13}
  (2+H_4) ∩ above-J = {6, 10, 14}
  (3+H_4) ∩ above-J = {7, 11, 15}
"""
from __future__ import annotations

import random
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
    matched = []
    for alpha in range(1, p):
        h = [(f1[j] + alpha * f2[j]) % p for j in range(n)]
        decoded = gs_decode_m2_np(p, omega, n, k, h, d=d)
        for msg in decoded:
            cw = encode_rs(p, omega, n, k, msg)
            if hamming(h, cw) <= tau:
                count += 1
                matched.append(alpha)
                break
    return count, matched


def search_supp(p, n, k, supp1, supp2, n_coeff_trials=50, seed=42):
    """For fixed (supp1, supp2), search over random coefficients to max K."""
    rng = random.Random(seed)
    omega = primitive_root_of_unity(p, n)
    d = find_d_for_n_m(n, k, m=2)
    tau = (n * 2 - d - 1) // 2
    max_K = 0
    best_coeffs = None
    for trial in range(n_coeff_trials):
        c1 = [rng.randint(1, p - 1) for _ in supp1]
        c2 = [rng.randint(1, p - 1) for _ in supp2]
        f1, f2 = make_sparse_pencil(p, n, omega, supp1, supp2, c1, c2)
        K, _ = K_via_gs_m2(p, omega, n, k, f1, f2, d, tau)
        if K > max_K:
            max_K = K
            best_coeffs = (c1, c2)
    return max_K, best_coeffs


def main():
    p, n, k = 97, 16, 4
    omega = primitive_root_of_unity(p, n)
    d = find_d_for_n_m(n, k, m=2)
    tau = (n * 2 - d - 1) // 2
    print(f"=== Subgroup-coset search at p={p}, ({n},{k}), τ={tau} ===")

    H4_intersected = [
        ('H_4   ∩ aJ', [4, 8, 12]),
        ('1+H_4 ∩ aJ', [5, 9, 13]),
        ('2+H_4 ∩ aJ', [6, 10, 14]),
        ('3+H_4 ∩ aJ', [7, 11, 15]),
    ]

    # Same-support variants
    print("\n--- supp1 = supp2 (same coset) ---")
    for label, supp in H4_intersected:
        t0 = time.time()
        K, coeffs = search_supp(p, n, k, supp, supp, n_coeff_trials=30)
        print(f"  {label}: max K = {K} [{time.time()-t0:.0f}s, supp={supp}]")

    # Different-support variants (cross-coset)
    print("\n--- supp1, supp2 different cosets ---")
    for (l1, s1), (l2, s2) in itertools.combinations(H4_intersected, 2):
        t0 = time.time()
        K, coeffs = search_supp(p, n, k, s1, s2, n_coeff_trials=30)
        print(f"  {l1} × {l2}: max K = {K} [{time.time()-t0:.0f}s]")

    # Mixed-coset 3-pos: skip the full sweep; instead spot-check one trio config
    print("\n--- spot-check mixed (one from each of cosets 0, 1, 2) ---")
    cosets = [s for _, s in H4_intersected]
    for combo in [(4, 5, 6), (4, 9, 14), (8, 9, 10), (12, 13, 14)]:
        supp = list(combo)
        t0 = time.time()
        K, _ = search_supp(p, n, k, supp, supp, n_coeff_trials=20)
        print(f"  supp={supp}: max K = {K} [{time.time()-t0:.0f}s]")


if __name__ == '__main__':
    main()
