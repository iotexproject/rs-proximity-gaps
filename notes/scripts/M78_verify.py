#!/usr/bin/env python3
"""
Find and verify M=78 outliers at n=16, p=17.
Strategy: sample random centers, find large M_alg, then verify M_actual.
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


random.seed(42)
n, p = 16, 17
k = 8
w = 5
nk = n - k  # 8
conds = nk - w  # 3
N = math.comb(n, w)  # 4368
omega = find_omega(n, p)
L = [pow(omega, i, p) for i in range(n)]

print(f"n={n}, k={k}, w={w}, conds={conds}, p={p}, N={N}")

# Precompute σ
all_B = list(combinations(range(n), w))
all_sigma = []
for B in all_B:
    roots = [L[i] for i in B]
    all_sigma.append(elem_sym(roots, p))

# Sample centers and find large M_alg
print(f"\nSampling 20000 centers...")
large_centers = []

for trial in range(20000):
    c_high = [random.randint(0, p-1) for _ in range(nk)]

    M = 0
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
            M += 1
            compat_Bs.append(b_idx)

    if M >= 10:
        large_centers.append((M, c_high[:], compat_Bs[:]))
        if M >= 20:
            print(f"  Found M_alg={M} at c_high={c_high}")

    if trial % 5000 == 0:
        print(f"  ... {trial}/20000")

print(f"\nFound {len(large_centers)} centers with M_alg >= 10")
if large_centers:
    M_large = [x[0] for x in large_centers]
    print(f"  M_alg distribution: {Counter(M_large)}")

# Verify M_actual for top outliers
print(f"\n{'='*60}")
print("VERIFYING M_actual FOR OUTLIER CENTERS")
print(f"{'='*60}")

for rank, (M_alg, c_high, compat_Bs) in enumerate(
        sorted(large_centers, key=lambda x: -x[0])[:10]):

    # Build center values
    c_coeffs = [0] * k + c_high
    c_vals = [sum(c_coeffs[j] * pow(L[i], j, p) for j in range(n)) % p for i in range(n)]

    # Interpolate distinct codewords
    codewords = {}
    for b_idx in compat_Bs:
        B = set(all_B[b_idx])
        result = interpolate_codeword(n, k, p, L, c_vals, B)
        if result is not None:
            f_vals, d = result
            if f_vals not in codewords:
                codewords[f_vals] = {'count': 0, 'dist': d}
            codewords[f_vals]['count'] += 1

    M_actual = len(codewords)
    print(f"\nCenter #{rank}: c_high={c_high}")
    print(f"  M_alg={M_alg}, M_actual={M_actual}, overcounting={M_alg/max(M_actual,1):.1f}x")

    for cw, info in sorted(codewords.items(), key=lambda x: -x[1]['count']):
        print(f"  dist={info['dist']}, compatible_Bs={info['count']}, "
              f"C(n-d,w-d)={math.comb(n-info['dist'], max(w-info['dist'],0))}")

    # Check: is the center itself a codeword?
    # c_vals should be the evaluation of f(x) = Σ c_j x^j at L
    f_check = [sum(c_coeffs[j] * pow(L[i], j, p) for j in range(k)) % p for i in range(n)]
    is_cw = all(c_vals[i] == f_check[i] for i in range(n))
    print(f"  Center is low-degree codeword: {is_cw}")

    # Check: σ values of compatible B's
    if M_alg <= 20:
        print(f"  σ vectors of compatible B's:")
        for b_idx in compat_Bs[:5]:
            sig = all_sigma[b_idx]
            print(f"    B={all_B[b_idx]}: σ={[sig[j]%p for j in range(1,w+1)]}")
