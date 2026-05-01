#!/usr/bin/env python3
"""
Algebraic dependencies among σ_j for subsets of roots of unity.

Newton's identities: σ_j = f_j(p_1, ..., p_j) where p_k = Σ_{i∈B} ω^{ki}.
The power sums p_k have CYCLIC structure: p_k depends only on the
"k-projection" of B in Z/nZ.

Key question: for subsets of n-th roots of unity, how much do the σ_j
values constrain each other? Are there "hidden" algebraic relations
beyond Newton's identities?

Specifically: given σ_1 = c_1, how many degrees of freedom remain
for (σ_2, ..., σ_w)?
"""

import math
from itertools import combinations
from collections import Counter

def find_primitive_root(p):
    factors = set()
    temp = p - 1
    d = 2
    while d * d <= temp:
        while temp % d == 0:
            factors.add(d)
            temp //= d
        d += 1
    if temp > 1:
        factors.add(temp)
    for g in range(2, p):
        if all(pow(g, (p - 1) // q, p) != 1 for q in factors):
            return g


def find_omega(n, p):
    return pow(find_primitive_root(p), (p - 1) // n, p)


def elem_sym(roots, p):
    w = len(roots)
    e = [0] * (w + 1)
    e[0] = 1
    for r in roots:
        for j in range(w, 0, -1):
            e[j] = (e[j] + e[j - 1] * r) % p
    return e


def power_sums(indices, n, omega, p, max_k):
    """Compute p_k = Σ_{i∈B} ω^{ki} for k=1,...,max_k."""
    ps = []
    for k in range(1, max_k + 1):
        val = sum(pow(omega, k * i, p) for i in indices) % p
        ps.append(val)
    return ps


# ================================================================
print("=" * 70)
print("POWER SUM STRUCTURE FOR ROOTS OF UNITY SUBSETS")
print("=" * 70)

# Key fact: p_k = Σ ω^{ki}. Since ω has order n, ω^{ki} depends only
# on (ki mod n). So p_k is determined by the "k-fold projection" of B.
#
# For k|n: ω^k has order n/k. So p_k = Σ ζ^i where ζ = ω^k has order n/k.
# The values of ζ^{b_i} repeat with period n/k.
# This creates DEPENDENCIES: subsets with the same "k-fold projection"
# have the same p_k.

for n, p in [(12, 13), (12, 37), (16, 17)]:
    if (p - 1) % n != 0:
        continue
    k_code = n // 2
    w = math.ceil((1 - math.sqrt(k_code / n)) * n)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"\n{'='*50}")
    print(f"n={n}, p={p}, w={w}")

    all_B = list(combinations(range(n), w))
    N = len(all_B)

    # Compute power sums and elementary symmetric polys for all B
    data = []
    for B in all_B:
        roots = [L[i] for i in B]
        es = elem_sym(roots, p)
        ps = power_sums(B, n, omega, p, w)
        data.append({
            'B': B,
            'sigma': tuple(es[j] % p for j in range(1, w+1)),
            'power': tuple(ps)
        })

    # 1. For each k|n: how many distinct p_k values?
    print(f"\nPower sum p_k distribution (k=1,...,{w}):")
    for kk in range(1, w + 1):
        pk_vals = [d['power'][kk-1] for d in data]
        distinct = len(set(pk_vals))
        order_omk = n // math.gcd(kk, n)
        print(f"  p_{kk}: {distinct} distinct values, "
              f"ord(ω^{kk})={order_omk}, "
              f"k|n={kk % n == 0 or n % kk == 0}")

    # 2. For each (p_1, p_2) pair: how many B's?
    p12_map = {}
    for d in data:
        key = (d['power'][0], d['power'][1])
        p12_map.setdefault(key, []).append(d['B'])

    p12_sizes = [len(v) for v in p12_map.values()]
    print(f"\n(p_1, p_2) joint fibers: {len(p12_map)} pairs")
    print(f"  max fiber = {max(p12_sizes)}")
    print(f"  histogram = {dict(Counter(p12_sizes).most_common(10))}")

    # 3. Dimension of σ-image: rank of the Jacobian
    # For a subset B = {b_1,...,b_w} ∈ Z/nZ, we have w free parameters.
    # σ_j = e_j(ω^{b_1},...,ω^{b_w}), j=1,...,w.
    # If all σ_j are "independent", the image has dimension w (generic position).
    # But the cyclotomic structure may reduce the effective dimension.

    # Test: what is the rank of the σ-image over F_p?
    # Count distinct σ vectors
    sigma_set = set(d['sigma'] for d in data)
    print(f"\nσ-image: {len(sigma_set)} distinct vectors out of N={N}")

    # 4. KEY TEST: for n=16, check if there are σ-value collisions
    #    that would explain M_alg=78
    if n == 16:
        # For each σ value: which B's map to it?
        sigma_fibers = {}
        for d in data:
            sigma_fibers.setdefault(d['sigma'], []).append(d['B'])
        max_sigma_fiber = max(len(v) for v in sigma_fibers.values())
        print(f"\n  Max σ-fiber (σ-collisions): {max_sigma_fiber}")
        if max_sigma_fiber > 1:
            for sig, Bs in sigma_fibers.items():
                if len(Bs) > 1:
                    print(f"  σ={sig} has {len(Bs)} B's:")
                    for B in Bs[:5]:
                        print(f"    {B}")

    # 5. Conditional entropy: H(σ_2 | σ_1)
    # If σ_2 is fully determined by σ_1 → dependency!
    sig1_to_sig2_set = {}
    for d in data:
        s1 = d['sigma'][0]
        sig1_to_sig2_set.setdefault(s1, set()).add(d['sigma'][1])

    min_sig2_count = min(len(v) for v in sig1_to_sig2_set.values())
    max_sig2_count = max(len(v) for v in sig1_to_sig2_set.values())
    print(f"\n  σ_2 | σ_1: min distinct = {min_sig2_count}, "
          f"max distinct = {max_sig2_count}")

    # 6. Check Newton identity constraints
    # Newton: p_1 = σ_1
    #         p_2 = σ_1·p_1 - 2σ_2 = σ_1² - 2σ_2
    #         p_3 = σ_1·p_2 - σ_2·p_1 + 3σ_3
    # So: σ_2 = (σ_1² - p_2)/2
    #     σ_3 = (p_3 - σ_1·p_2 + σ_2·p_1)/3
    #          = (p_3 - σ_1·p_2 + σ_1·(σ_1²-p_2)/2)/3
    #
    # If σ_1 is fixed AND p_2 is determined by the k-fold projection
    # of B → σ_2 is determined!
    #
    # When is p_2 determined by σ_1?
    # p_2 = Σ ω^{2i}. This is a sum of ω^{2i} for i∈B.
    # If gcd(2,n) > 1 (n even): ω² has order n/2, so there are only n/2
    # distinct values. p_2 depends on the 2-fold projection.
    # σ_1 = Σ ω^i gives some constraint on the 2-fold projection, but
    # it's not deterministic.

    print(f"\n  Newton identity check:")
    inv2 = pow(2, p - 2, p) if p != 2 else None
    for d in data[:5]:
        s1, s2 = d['sigma'][0], d['sigma'][1]
        p1, p2 = d['power'][0], d['power'][1]
        # Check: σ_2 = (σ_1² - p_2) / 2
        if inv2:
            s2_from_newton = (s1 * s1 - p2) * inv2 % p
            print(f"  B={d['B']}: σ_1={s1}, σ_2={s2}, "
                  f"Newton σ_2={(s1*s1-p2)*inv2%p} ({'OK' if s2==s2_from_newton else 'MISMATCH'})")


# ================================================================
print("\n\n" + "=" * 70)
print("CYCLOTOMIC CONSTRAINTS: WHEN DOES p_k CONSTRAIN σ?")
print("=" * 70)

# For n=12: divisors of 12 are {1,2,3,4,6,12}.
# p_1 = σ_1 (trivial)
# p_2 = Σ ω^{2i}: ω² has order 6 (since 12/gcd(2,12) = 6)
# p_3 = Σ ω^{3i}: ω³ has order 4
# p_4 = Σ ω^{4i}: ω⁴ has order 3
# p_6 = Σ ω^{6i}: ω⁶ has order 2 (= -1, so p_6 = Σ (-1)^i)
#
# For B with w=4 elements from Z/12:
# p_6 = #{even indices in B} - #{odd indices in B}
# If B has a even and 4-a odd: p_6 = a - (4-a) = 2a-4 ∈ {-4,-2,0,2,4}
#
# p_3: ω³ is a 4th root of unity. {ω^{3·0}, ω^{3·1}, ..., ω^{3·11}}
# = {1, ω³, ω⁶, ω⁹, 1, ω³, ...} cycling with period 4.
# So p_3 depends on how many elements of B fall in each residue class mod 4.

n = 12
for p in [13, 37]:
    if (p-1) % n != 0:
        continue
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    w = 4
    print(f"\nn={n}, p={p}")

    # Classify B by residue patterns
    all_B = list(combinations(range(n), w))
    for d in [2, 3, 4, 6]:
        n_classes = n // d
        # For each B: count how many indices fall in each residue class mod d
        pattern_to_Bs = {}
        for B in all_B:
            pattern = tuple(sorted([i % d for i in B]))
            pattern_to_Bs.setdefault(pattern, []).append(B)

        print(f"\n  Residue mod {d} (ω^{d} has order {n//d}):")
        print(f"  {len(pattern_to_Bs)} patterns, largest group = "
              f"{max(len(v) for v in pattern_to_Bs.values())}")

        # For each pattern: is p_d constant?
        for pattern, Bs in sorted(pattern_to_Bs.items(), key=lambda x: -len(x[1]))[:3]:
            pd_vals = set()
            for B in Bs:
                pd = sum(pow(omega, d*i, p) for i in B) % p
                pd_vals.add(pd)
            print(f"    pattern {pattern}: {len(Bs)} B's, "
                  f"p_{d} takes {len(pd_vals)} values: {pd_vals}")
