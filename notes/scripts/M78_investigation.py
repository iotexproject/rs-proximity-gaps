#!/usr/bin/env python3
"""
Investigate the M=78 outlier at n=16, p=17.

Find the exact center giving M_alg=78, then compute M_actual
(distinct codewords) to check for overcounting.
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


def interpolate_codeword(n, k, p, L, c_vals, B):
    """Given center codeword values and erasure set B, interpolate the codeword."""
    S = [i for i in range(n) if i not in B]
    m = len(S)
    aug = [[pow(L[S[i]], j, p) for j in range(k)] + [c_vals[S[i]]] for i in range(m)]
    pivot_cols = []
    for col in range(k):
        piv = -1
        for row in range(len(pivot_cols), m):
            if aug[row][col] % p != 0:
                piv = row
                break
        if piv == -1:
            continue
        r2 = len(pivot_cols)
        aug[r2], aug[piv] = aug[piv], aug[r2]
        inv_p = pow(aug[r2][col], p - 2, p)
        for row in range(m):
            if row != r2 and aug[row][col] % p != 0:
                f2 = aug[row][col] * inv_p % p
                for j2 in range(k + 1):
                    aug[row][j2] = (aug[row][j2] - f2 * aug[r2][j2]) % p
        pivot_cols.append(col)
    for row in range(len(pivot_cols), m):
        if aug[row][k] % p != 0:
            return None
    a = [0] * k
    for idx2, col in enumerate(pivot_cols):
        a[col] = aug[idx2][k] * pow(aug[idx2][col], p - 2, p) % p
    f_vals = tuple(sum(a[j] * pow(L[i], j, p) for j in range(k)) % p for i in range(n))
    d = sum(1 for i in range(n) if c_vals[i] != f_vals[i])
    return f_vals, d


n, p = 16, 17
k = 8
w = 5  # Johnson radius
nk = n - k  # = 8
conds = nk - w  # = 3
N = math.comb(n, w)
omega = find_omega(n, p)
L = [pow(omega, i, p) for i in range(n)]

print(f"n={n}, k={k}, w={w}, conds={conds}, p={p}, N={N}")
print(f"N/p^c = {N/p**conds:.4f}")

# Precompute σ
all_B = list(combinations(range(n), w))
all_sigma = []
for B in all_B:
    roots = [L[i] for i in B]
    all_sigma.append(elem_sym(roots, p))

# Find centers with large M_alg
print(f"\nSearching p^{nk} = {p**nk} centers... (sampling {p**conds})")

large_M_centers = []

# Enumerate all c_high
for c_idx in range(p**nk):
    c_high = []
    tmp = c_idx
    for _ in range(nk):
        c_high.append(tmp % p)
        tmp //= p

    # Compute M_alg
    M = 0
    compat_Bs = []
    for b_idx in range(N):
        sigma = all_sigma[b_idx]
        compatible = True
        for m_off in range(conds):
            val = 0
            for j in range(w + 1):
                idx = m_off + j
                if idx < nk:
                    val = (val + pow(-1, j, p) * sigma[j] * c_high[idx]) % p
            if val % p != 0:
                compatible = False
                break
        if compatible:
            M += 1
            compat_Bs.append(b_idx)

    if M >= 20:
        large_M_centers.append((M, c_high[:], compat_Bs[:]))
        print(f"  Found M_alg={M} at c_high={c_high}")

    if c_idx % 500000 == 0 and c_idx > 0:
        print(f"  ... checked {c_idx}/{p**nk}")

    # Stop after checking enough
    if c_idx >= 200000:
        break

print(f"\nFound {len(large_M_centers)} centers with M_alg >= 20")

# For each large-M center: compute M_actual (distinct codewords)
for rank, (M_alg, c_high, compat_Bs) in enumerate(sorted(large_M_centers, key=lambda x: -x[0])[:5]):
    print(f"\n{'='*50}")
    print(f"Center #{rank}: c_high={c_high}, M_alg={M_alg}")

    # Build center codeword values
    c_coeffs = [0] * k + c_high
    c_vals = [sum(c_coeffs[j] * pow(L[i], j, p) for j in range(n)) % p for i in range(n)]

    # Interpolate codewords from compatible B's
    codewords = set()
    for b_idx in compat_Bs:
        B = set(all_B[b_idx])
        result = interpolate_codeword(n, k, p, L, c_vals, B)
        if result is not None:
            f_vals, d = result
            codewords.add(f_vals)

    M_actual = len(codewords)
    print(f"  M_actual = {M_actual} (M_alg overcounting: {M_alg/M_actual:.1f}x)")

    # For each distinct codeword: how many compatible B's lead to it?
    cw_counts = Counter()
    for b_idx in compat_Bs:
        B = set(all_B[b_idx])
        result = interpolate_codeword(n, k, p, L, c_vals, B)
        if result is not None:
            cw_counts[result[0]] += 1

    # Compute Hamming distances
    for cw, count in cw_counts.most_common():
        d = sum(1 for i in range(n) if c_vals[i] != cw[i])
        print(f"  Codeword: distance={d}, compatible_Bs={count}, "
              f"C(n-d,w-d)={math.comb(n-d, max(w-d,0)) if d<=w else 0}")

    # Check: are the compatible B sets related to each other?
    print(f"\n  Compatible B's (first 10):")
    for b_idx in compat_Bs[:10]:
        B = all_B[b_idx]
        print(f"    B={B}")
