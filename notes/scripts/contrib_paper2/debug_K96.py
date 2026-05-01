"""Debug K=96 finding at supp [8, 9, 10].

Inspect what's happening: pick specific α, compute h_α, GS-decode, verify.
"""
from __future__ import annotations

from gs_sudan_m2_np import gs_decode_m2_np
from gs_sudan_m2 import primitive_root_of_unity, encode_rs, hamming, find_d_for_n_m


def main():
    p, n, k = 97, 16, 4
    omega = primitive_root_of_unity(p, n)
    d = find_d_for_n_m(n, k, m=2)
    tau = (n * 2 - d - 1) // 2
    supp1 = [8, 9, 10]
    supp2 = [8, 9, 10]
    c1 = [1, 2, 3]
    c2 = [1, 3, 5]

    # Build f1, f2
    f1 = [0] * n
    f2 = [0] * n
    for j in range(n):
        for a, c in zip(supp1, c1):
            f1[j] = (f1[j] + c * pow(omega, a * j, p)) % p
        for a, c in zip(supp2, c2):
            f2[j] = (f2[j] + c * pow(omega, a * j, p)) % p

    print(f"f1 = {f1}")
    print(f"f2 = {f2}")
    print(f"τ = {tau}, p = {p}")

    # Pick a few alphas, inspect
    K_count = 0
    for alpha in [1, 2, 3, 50, 96]:
        h = [(f1[j] + alpha * f2[j]) % p for j in range(n)]
        decoded = gs_decode_m2_np(p, omega, n, k, h, d=d)
        print(f"\n  α={alpha}: h = {h}")
        print(f"    decoded list size = {len(decoded)}")
        for msg in decoded:
            cw = encode_rs(p, omega, n, k, msg)
            dist = hamming(h, cw)
            print(f"    msg={msg} → cw[:4]={cw[:4]}..., dist={dist}, within τ={tau}? {dist <= tau}")

    # Now full count
    print("\n--- full count ---")
    count_breakdown = {}
    for alpha in range(1, p):
        h = [(f1[j] + alpha * f2[j]) % p for j in range(n)]
        decoded = gs_decode_m2_np(p, omega, n, k, h, d=d)
        min_dist = None
        for msg in decoded:
            cw = encode_rs(p, omega, n, k, msg)
            dist = hamming(h, cw)
            if min_dist is None or dist < min_dist:
                min_dist = dist
        if min_dist is not None and min_dist <= tau:
            K_count += 1
        count_breakdown[min_dist] = count_breakdown.get(min_dist, 0) + 1
    print(f"  total K = {K_count}")
    print(f"  min-dist distribution: {sorted(count_breakdown.items())}")


if __name__ == '__main__':
    main()
