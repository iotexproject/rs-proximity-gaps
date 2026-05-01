#!/usr/bin/env python3
"""
Distribution of M_actual across random centers.
M_actual = number of DISTINCT codewords within Johnson radius.
Correctly accounts for overcounting.
"""

import math
import random
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


random.seed(123)

print("=" * 70)
print("M_actual DISTRIBUTION (DISTINCT CODEWORDS)")
print("=" * 70)

for n, p in [(10, 11), (10, 31), (12, 13), (12, 37), (14, 29),
             (16, 17), (16, 97), (18, 19), (18, 37)]:
    if (p - 1) % n != 0:
        continue
    k = n // 2
    w = math.ceil((1 - math.sqrt(k / n)) * n)
    nk = n - k
    conds = nk - w
    N = math.comb(n, w)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"\n{'='*60}")
    print(f"n={n}, k={k}, w={w}, conds={conds}, p={p}, N={N}, N/p^c={N/p**conds:.4f}")

    # Precompute σ
    all_B = list(combinations(range(n), w))
    all_sigma = []
    for B in all_B:
        roots = [L[i] for i in B]
        all_sigma.append(elem_sym(roots, p))

    # Sample centers
    n_sample = min(2000, p**min(conds, 3))
    M_actual_values = []
    dist_profile = Counter()  # dist → count of codewords at that distance

    for trial in range(n_sample):
        c_high = [random.randint(0, p-1) for _ in range(nk)]

        # Find compatible B's (fast check via conditions)
        compat_Bs = []
        for b_idx in range(N):
            sigma = all_sigma[b_idx]
            ok = True
            for m_off in range(conds):
                val = 0
                for j in range(w + 1):
                    idx = m_off + j
                    if idx < nk:
                        val = (val + pow(-1, j, p) * sigma[j] * c_high[idx]) % p
                if val % p != 0:
                    ok = False
                    break
            if ok:
                compat_Bs.append(b_idx)

        if len(compat_Bs) == 0:
            M_actual_values.append(0)
            continue

        # Compute M_actual via interpolation
        c_coeffs = [0] * k + c_high
        c_vals = [sum(c_coeffs[j] * pow(L[i], j, p) for j in range(n)) % p for i in range(n)]

        codewords = set()
        for b_idx in compat_Bs:
            B = set(all_B[b_idx])
            result = interpolate_codeword(n, k, p, L, c_vals, B)
            if result is not None:
                f_vals, d = result
                codewords.add(f_vals)
                dist_profile[d] += 1

        M_actual = len(codewords)
        M_actual_values.append(M_actual)

    hist = Counter(M_actual_values)
    print(f"  Sampled {n_sample} centers")
    print(f"  M_actual histogram: {dict(sorted(hist.items()))}")
    print(f"  max M_actual = {max(M_actual_values)}")
    print(f"  avg M_actual = {sum(M_actual_values)/len(M_actual_values):.3f}")
    print(f"  Distance profile: {dict(sorted(dist_profile.items()))}")
