"""Test crafted witnesses at deployment (32, 8) p=257 with Sudan(m=2).

Random sampling missed all K>0 configs. Try crafted configs:
  1. f_1, f_2 supported on adjacent positions (paper3 Note 0316 trivial saturation)
  2. 3-mono pairs with disjoint above-J supports (paper2 K_3 ≤ 10 max-config)
  3. Lifted Note 0310 codim-1 branch construction (if applicable to (32,8))
"""
from __future__ import annotations

import time

from gs_sudan_m2 import primitive_root_of_unity, gs_decode_m2, encode_rs, hamming, find_d_for_n_m


def make_f_from_supp(p, n, omega, supp, coeffs):
    f = [0] * n
    for j in range(n):
        for a, c in zip(supp, coeffs):
            f[j] = (f[j] + c * pow(omega, a * j, p)) % p
    return f


def K_via_gs_m2(p, omega, n, k, f1, f2, d, tau, verbose=False):
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
                if verbose:
                    print(f"    α={alpha}: hit msg {msg}, dist={hamming(h, cw)}")
                break
    return count, matched


def run(p, n, k, label, supp1, supp2, c1, c2):
    omega = primitive_root_of_unity(p, n)
    d = find_d_for_n_m(n, k, m=2)
    tau = (n * 2 - d - 1) // 2
    J = n - int((n * k) ** 0.5)
    print(f"\n--- {label}: ({n},{k}) p={p}, d={d}, τ={tau}, J={J} ---")
    print(f"   supp1={supp1}, c1={c1}")
    print(f"   supp2={supp2}, c2={c2}")
    f1 = make_f_from_supp(p, n, omega, supp1, c1)
    f2 = make_f_from_supp(p, n, omega, supp2, c2)
    t0 = time.time()
    K, alphas = K_via_gs_m2(p, omega, n, k, f1, f2, d, tau)
    elapsed = time.time() - t0
    print(f"   K = {K} ({elapsed:.1f}s, |S*|={len(set(supp1)|set(supp2))})")
    if K > 0:
        print(f"   matched α: {alphas[:20]}{'...' if len(alphas)>20 else ''}")


def main():
    # (16, 4) sanity tests first
    print("=== (16, 4) crafted witnesses ===")
    # Adjacent 2-mono (Note 0316 spirit)
    run(p=97, n=16, k=4, label="adjacent 2-mono [4,5] vs [6,7]",
        supp1=[4, 5], supp2=[6, 7], c1=[1, 2], c2=[3, 5])
    # Disjoint 3-mono
    run(p=97, n=16, k=4, label="disjoint 3-mono [4,5,6] vs [7,8,9]",
        supp1=[4, 5, 6], supp2=[7, 8, 9], c1=[1, 2, 3], c2=[5, 7, 11])
    # Same support 3-mono
    run(p=97, n=16, k=4, label="same-supp 3-mono [4,5,6] vs [4,5,6]",
        supp1=[4, 5, 6], supp2=[4, 5, 6], c1=[1, 2, 3], c2=[5, 7, 11])

    print("\n=== (32, 8) p=257 crafted witnesses ===")
    # Adjacent 2-mono, very low |S*|
    run(p=257, n=32, k=8, label="adjacent 2-mono [8,9] vs [10,11]",
        supp1=[8, 9], supp2=[10, 11], c1=[1, 2], c2=[3, 5])
    # Disjoint 3-mono
    run(p=257, n=32, k=8, label="disjoint 3-mono [8,9,10] vs [11,12,13]",
        supp1=[8, 9, 10], supp2=[11, 12, 13], c1=[1, 2, 3], c2=[5, 7, 11])


if __name__ == '__main__':
    main()
