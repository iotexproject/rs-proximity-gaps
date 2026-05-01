#!/usr/bin/env python3
"""
Fiber analysis of the σ-image map.

Core question for sum-product approach:
- Fix σ_1 = c. How many distinct σ_2 values on this fiber?
- Fix (σ_1, σ_2) = (c1, c2). How many B achieve this?
- Full fiber distribution of D∘σ for codimension-c affine subspaces.

If σ_1 and σ_2 are "independent" (in sum-product sense), then
fixing σ_1 still leaves σ_2 well-distributed → M = O(N/p²).
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


# ================================================================
print("=" * 70)
print("σ-IMAGE FIBER ANALYSIS")
print("=" * 70)

for n, p in [(6, 7), (8, 17), (10, 11), (10, 31), (12, 13), (12, 37), (14, 29)]:
    if (p - 1) % n != 0:
        continue
    k = n // 2
    w = math.ceil((1 - math.sqrt(k / n)) * n)
    N = math.comb(n, w)
    conds = n - k - w
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"\n{'='*70}")
    print(f"n={n}, k={k}, w={w}, conds={conds}, p={p}, N={N}")
    print(f"N/p = {N/p:.2f}, N/p² = {N/p**2:.4f}")
    print(f"{'='*70}")

    # Compute full σ-image
    all_B = list(combinations(range(n), w))
    sigma_map = {}  # (σ_1, ..., σ_w) → list of B's
    sigma1_map = {}  # σ_1 → list of B's
    sigma12_map = {}  # (σ_1, σ_2) → list of B's

    for B in all_B:
        roots = [L[i] for i in B]
        es = elem_sym(roots, p)
        sig = tuple(es[j] % p for j in range(1, w + 1))
        sigma_map.setdefault(sig, []).append(B)
        sigma1_map.setdefault(sig[0], []).append(B)
        if w >= 2:
            sigma12_map.setdefault((sig[0], sig[1]), []).append(B)

    # 1. Full σ-image statistics
    img_size = len(sigma_map)
    fiber_sizes = [len(v) for v in sigma_map.values()]
    fiber_hist = Counter(fiber_sizes)
    print(f"\nFull σ-image: {img_size} distinct values out of N={N}")
    print(f"  Injectivity: {img_size/N:.4f}")
    print(f"  Max fiber: {max(fiber_sizes)}")
    print(f"  Fiber histogram: {dict(sorted(fiber_hist.items()))}")

    # 2. σ_1-fiber analysis
    sig1_sizes = [len(v) for v in sigma1_map.values()]
    print(f"\nσ_1 fibers: {len(sigma1_map)} distinct values")
    print(f"  avg fiber = {N/len(sigma1_map):.2f} (expected N/p = {N/p:.2f})")
    print(f"  max fiber = {max(sig1_sizes)}")
    print(f"  min fiber = {min(sig1_sizes)}")

    # 3. For each σ_1 fiber: how many distinct σ_2 values?
    if w >= 2:
        print(f"\nσ_2 spread WITHIN σ_1 fibers:")
        sig1_vals = sorted(sigma1_map.keys(), key=lambda k: -len(sigma1_map[k]))
        for sig1_val in sig1_vals[:5]:
            fiber = sigma1_map[sig1_val]
            sig2_vals = set()
            for B in fiber:
                roots = [L[i] for i in B]
                es = elem_sym(roots, p)
                sig2_vals.add(es[2] % p)
            print(f"  σ_1={sig1_val}: fiber_size={len(fiber)}, "
                  f"distinct_σ_2={len(sig2_vals)}, "
                  f"ratio={len(sig2_vals)/len(fiber):.3f}")

    # 4. (σ_1, σ_2) joint fiber analysis
    if w >= 2:
        sig12_sizes = [len(v) for v in sigma12_map.values()]
        sig12_hist = Counter(sig12_sizes)
        print(f"\n(σ_1, σ_2) joint fibers: {len(sigma12_map)} distinct pairs")
        print(f"  avg fiber = {N/len(sigma12_map):.2f} (expected N/p² = {N/p**2:.4f})")
        print(f"  max fiber = {max(sig12_sizes)}")
        print(f"  Histogram: {dict(sorted(sig12_hist.items()))}")

    # 5. Check σ_j independence: for j=1,...,w, count distinct σ_j values on σ_1 fibers
    if w >= 3:
        print(f"\nσ_j spread on largest σ_1 fiber:")
        biggest_sig1 = max(sigma1_map, key=lambda k: len(sigma1_map[k]))
        fiber = sigma1_map[biggest_sig1]
        for j in range(2, w + 1):
            sig_j_vals = set()
            for B in fiber:
                roots = [L[i] for i in B]
                es = elem_sym(roots, p)
                sig_j_vals.add(es[j] % p)
            print(f"  σ_{j}: {len(sig_j_vals)} distinct values "
                  f"(out of {len(fiber)} B's, max possible {p})")


# ================================================================
print("\n\n" + "=" * 70)
print("CONDITIONAL DISTRIBUTION: σ_2 | σ_1")
print("=" * 70)

# For the sum-product theorem: we need
# |{B : σ_1(B) = c_1, σ_2(B) = c_2}| ≤ C · N/p² for all (c_1, c_2)
#
# Equivalently: the conditional distribution of σ_2 given σ_1 = c is
# approximately uniform over F_p.

for n, p in [(8, 17), (10, 31), (12, 37), (14, 29)]:
    if (p - 1) % n != 0:
        continue
    k = n // 2
    w = math.ceil((1 - math.sqrt(k / n)) * n)
    N = math.comb(n, w)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"\nn={n}, p={p}, w={w}, N={N}")

    all_B = list(combinations(range(n), w))

    # Compute (σ_1, σ_2, ..., σ_w) for all B
    sigma_data = []
    for B in all_B:
        roots = [L[i] for i in B]
        es = elem_sym(roots, p)
        sigma_data.append(tuple(es[j] % p for j in range(1, w + 1)))

    # For each σ_1 value, compute σ_2 distribution
    sig1_to_sig2 = {}
    for sd in sigma_data:
        sig1_to_sig2.setdefault(sd[0], []).append(sd[1])

    # Compute the maximum "conditional fiber" max_{c1,c2} |{B: σ_1=c1, σ_2=c2}|
    max_joint = 0
    for c1, sig2_list in sig1_to_sig2.items():
        hist = Counter(sig2_list)
        local_max = max(hist.values())
        if local_max > max_joint:
            max_joint = local_max
            worst_c1 = c1
            worst_c2 = hist.most_common(1)[0][0]
            worst_count = local_max

    print(f"  max |{{B: σ_1=c₁, σ_2=c₂}}| = {max_joint} "
          f"(at σ_1={worst_c1}, σ_2={worst_c2})")
    print(f"  N/p² = {N/p**2:.4f}")
    print(f"  ratio = {max_joint / (N/p**2):.2f}")

    # Deeper: for all (σ_1, σ_2, σ_3) triples
    if w >= 3:
        triple_counts = Counter()
        for sd in sigma_data:
            triple_counts[sd[:3]] += 1
        max_triple = max(triple_counts.values())
        print(f"  max |{{B: σ_1=c₁, σ_2=c₂, σ_3=c₃}}| = {max_triple}")
        print(f"  N/p³ = {N/p**3:.6f}")


# ================================================================
print("\n\n" + "=" * 70)
print("ADDITIVE ENERGY OF σ-IMAGE")
print("=" * 70)

# E(Σ) = |{(B1,B2,B3,B4) : σ(B1)+σ(B2) = σ(B3)+σ(B4)}|
# For pseudorandom Σ: E ≈ N^3/p^w (trivial) + N² (diagonal)
# High energy = concentration; low energy = well-spread

for n, p in [(6, 7), (8, 17)]:
    if (p - 1) % n != 0:
        continue
    k = n // 2
    w = math.ceil((1 - math.sqrt(k / n)) * n)
    N = math.comb(n, w)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"\nn={n}, p={p}, w={w}, N={N}")

    all_B = list(combinations(range(n), w))
    sigma_vals = []
    for B in all_B:
        roots = [L[i] for i in B]
        es = elem_sym(roots, p)
        sigma_vals.append(tuple(es[j] % p for j in range(1, w + 1)))

    # Pairwise σ-differences
    diff_counts = Counter()
    for i in range(N):
        for j in range(N):
            diff = tuple((sigma_vals[i][k] - sigma_vals[j][k]) % p for k in range(w))
            diff_counts[diff] += 1

    E = sum(c**2 for c in diff_counts.values())
    E_random = N**3 + N**2  # N^4/p^w is negligible
    E_diagonal = N  # pairs (B,B)
    print(f"  Additive energy E = {E}")
    print(f"  E_random ≈ {E_random}")
    print(f"  E/N² = {E/N**2:.2f} (= Σ fiber² for differences)")
    print(f"  max diff multiplicity = {max(diff_counts.values())}")
    print(f"  zero diff count = {diff_counts[tuple([0]*w)]}")
