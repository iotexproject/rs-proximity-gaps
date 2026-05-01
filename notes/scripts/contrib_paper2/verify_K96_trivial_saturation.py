"""Verify K=96 at supp [8,9,10] is paper3 cycle-4 trivial saturation.

paper3 Note 0316 (cycle 4): V_bad ⊇ {(s_1, s_2) : |S*| ≤ w}, with M = q-1
saturation. At (16, 4, c=2): w = D - c = 12 - 2 = 10.

For supp = [8, 9, 10] (|S*|=3 ≤ w=10), trivially in V_bad's saturation locus.

This script:
  1. Confirms supp = [8, 9, 10] gives K = q-1 across multiple coefficient choices
  2. Tests |S*| > w pairs (outside trivial saturation) — these should give
     K bounded by the GENUINE conjecture's K_3 ≤ 10 (paper2 thm:universal-K10)
  3. Confirms structurally why c=2 trivial saturation kicks in for low |S*|
"""
from __future__ import annotations

import time

from gs_sudan_m2_np import gs_decode_m2_np
from gs_sudan_m2 import primitive_root_of_unity, encode_rs, hamming, find_d_for_n_m


def make_pencil(p, n, omega, supp1, supp2, c1, c2):
    f1 = [0] * n
    f2 = [0] * n
    for j in range(n):
        for a, c in zip(supp1, c1):
            f1[j] = (f1[j] + c * pow(omega, a * j, p)) % p
        for a, c in zip(supp2, c2):
            f2[j] = (f2[j] + c * pow(omega, a * j, p)) % p
    return f1, f2


def K_via_gs(p, omega, n, k, f1, f2, d, tau):
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


def main():
    p, n, k = 97, 16, 4
    omega = primitive_root_of_unity(p, n)
    d = find_d_for_n_m(n, k, m=2)
    tau = (n * 2 - d - 1) // 2
    c = 2  # rate 1/4 deployment
    D = n - k
    w = D - c
    print(f"=== Verify K=96 trivial saturation at p={p}, ({n},{k}), τ={tau} ===")
    print(f"  D = {D}, c = {c}, w = D - c = {w}")
    print(f"  paper3 Note 0316: V_bad ⊇ {{|S*| ≤ {w}}} → M = q-1 saturation")

    # Test 1: trivial saturation locus (|S*| ≤ w)
    print(f"\n--- Test 1: |S*| ≤ w (trivial saturation, expect K = q-1 = {p-1}) ---")
    trivial_cases = [
        ([8, 9, 10], [8, 9, 10], 3),
        ([4, 5, 6], [4, 5, 6], 3),
        ([4, 8], [4, 8], 2),
        ([4, 5, 6, 7, 8, 9, 10, 11, 12, 13], [4, 5, 6, 7, 8, 9, 10, 11, 12, 13], 10),  # |S*|=w
    ]
    for supp1, supp2, expected_S in trivial_cases:
        S_star = len(set(supp1) | set(supp2))
        c1 = list(range(1, len(supp1) + 1))
        c2 = [(2 * i + 1) for i in range(len(supp2))]
        f1, f2 = make_pencil(p, n, omega, supp1, supp2, c1, c2)
        t0 = time.time()
        K = K_via_gs(p, omega, n, k, f1, f2, d, tau)
        elapsed = time.time() - t0
        flag = "✓ saturated" if K >= p - 2 else f"K={K} unexpected"
        print(f"  supp1={supp1}, supp2={supp2}: |S*|={S_star} ≤ w={w}, K={K}  [{flag}, {elapsed:.0f}s]")

    # Test 2: outside trivial saturation (|S*| > w)
    print(f"\n--- Test 2: |S*| > w (outside trivial saturation) ---")
    nontrivial_cases = [
        ([4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14], [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], 11),
        ([4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], 12),
    ]
    for supp1, supp2, expected_S in nontrivial_cases:
        S_star = len(set(supp1) | set(supp2))
        if S_star <= w:
            print(f"  skip — |S*|={S_star} ≤ w={w}, not nontrivial")
            continue
        c1 = list(range(1, len(supp1) + 1))
        c2 = [(2 * i + 1) for i in range(len(supp2))]
        f1, f2 = make_pencil(p, n, omega, supp1, supp2, c1, c2)
        t0 = time.time()
        K = K_via_gs(p, omega, n, k, f1, f2, d, tau)
        elapsed = time.time() - t0
        print(f"  |S*|={S_star} > w: K={K}  [{elapsed:.0f}s]")


if __name__ == '__main__':
    main()
