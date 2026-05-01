#!/usr/bin/env python3
"""
Support structure of list-decoded codewords.

For M codewords f_1,...,f_M within distance w of center c:
- D_i = {pos : f_i(pos) ≠ c(pos)}, |D_i| ≤ w
- supp(f_i - f_j) ⊆ D_i ∪ D_j
- wt(f_i - f_j) ≥ n - k + 1 (MDS)

Compute the EXACT support structure for real list-decoding instances
to understand what constraints are actually binding.
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


def eval_poly(coeffs, x, p):
    val = 0
    xpow = 1
    for c in coeffs:
        val = (val + c * xpow) % p
        xpow = xpow * x % p
    return val


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

print("=" * 70)
print("SUPPORT STRUCTURE OF LIST-DECODED CODEWORDS")
print("=" * 70)

# For each (n, p): find a center with M_actual ≥ 3 and analyze
for n, p in [(12, 13), (14, 29), (18, 19)]:
    if (p - 1) % n != 0:
        continue
    k = n // 2
    w = math.ceil((1 - math.sqrt(k / n)) * n)
    nk = n - k
    conds = nk - w
    N = math.comb(n, w)
    delta = 2 * w - n + k - 1
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"\n{'='*60}")
    print(f"n={n}, k={k}, w={w}, conds={conds}, p={p}, δ={delta}")

    # Precompute σ
    all_B = list(combinations(range(n), w))
    all_sigma = []
    for B in all_B:
        roots = [L[i] for i in B]
        all_sigma.append(elem_sym(roots, p))

    # Find center with large M_actual
    best_M = 0
    best_center = None
    best_codewords = None

    for trial in range(5000):
        c_high = [random.randint(0, p-1) for _ in range(nk)]
        c_coeffs = [0] * k + c_high
        c_vals = [sum(c_coeffs[j] * pow(L[i], j, p) for j in range(n)) % p
                  for i in range(n)]

        # Find compatible B's
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

        if not compat_Bs:
            continue

        # Get distinct codewords
        codewords = {}
        for b_idx in compat_Bs:
            B = set(all_B[b_idx])
            result = interpolate_codeword(n, k, p, L, c_vals, B)
            if result is not None:
                f_vals, d = result
                if f_vals not in codewords:
                    codewords[f_vals] = d

        M_actual = len(codewords)
        if M_actual > best_M:
            best_M = M_actual
            best_center = c_vals
            best_codewords = codewords

    if best_M < 2:
        print(f"  Best M_actual = {best_M}, need ≥ 2 for analysis")
        continue

    print(f"  Found center with M_actual = {best_M}")

    # Analyze support structure
    cw_list = list(best_codewords.items())
    c_vals = best_center

    print(f"\n  Codeword distances to center:")
    D_sets = []
    for idx, (f_vals, d) in enumerate(cw_list):
        D_i = frozenset(i for i in range(n) if f_vals[i] != c_vals[i])
        D_sets.append(D_i)
        print(f"    f_{idx}: dist={d}, D_{idx}={sorted(D_i)}")

    # Pairwise analysis
    print(f"\n  Pairwise distances and overlaps:")
    for i in range(len(cw_list)):
        for j in range(i+1, len(cw_list)):
            fi_vals = cw_list[i][0]
            fj_vals = cw_list[j][0]
            d_ij = sum(1 for pos in range(n) if fi_vals[pos] != fj_vals[pos])
            overlap = len(D_sets[i] & D_sets[j])
            union = len(D_sets[i] | D_sets[j])
            print(f"    d(f_{i},f_{j}) = {d_ij}, |D_{i}∩D_{j}| = {overlap}, "
                  f"|D_{i}∪D_{j}| = {union}")
            # Verify: supp(f_i-f_j) ⊆ D_i ∪ D_j
            supp_diff = set(pos for pos in range(n)
                           if fi_vals[pos] != fj_vals[pos])
            if not supp_diff.issubset(D_sets[i] | D_sets[j]):
                print(f"    *** VIOLATION: supp not subset of D_i ∪ D_j!")
            else:
                # How much of D_i ∪ D_j is actually used?
                usage = len(supp_diff) / union * 100
                print(f"    supp(f_i-f_j) = {sorted(supp_diff)}, "
                      f"usage = {usage:.0f}%")

    # Union of all D_i
    D_union = frozenset().union(*D_sets)
    print(f"\n  |∪ D_i| = {len(D_union)}, n = {n}")
    print(f"  Union: {sorted(D_union)}")

    # Intersection matrix
    if best_M <= 10:
        print(f"\n  Overlap matrix:")
        for i in range(len(D_sets)):
            row = [len(D_sets[i] & D_sets[j]) for j in range(len(D_sets))]
            print(f"    {row}")


# ================================================================
print("\n\n" + "=" * 70)
print("REFINED BOUND: UNION-SIZE CONSTRAINT")
print("=" * 70)

# Better bound: |∪ D_i| ≤ n constrains M.
# Each D_i has |D_i| ≤ w.
# pairwise: |D_i ∩ D_j| ≤ δ = 2w - n + k - 1.
#
# By the Bonferroni/Turán-type inequality:
# |∪ D_i| ≥ Σ|D_i| - Σ|D_i∩D_j| + Σ|D_i∩D_j∩D_k| - ...
# (alternating signs, but only the first two terms are useful)
#
# |∪ D_i| ≥ Mw - C(M,2)δ   [first-order Bonferroni]
# Since |∪ D_i| ≤ n: Mw - C(M,2)δ ≤ n
# This gives M ≤ (1 + √(1 + 8n/δ)) · δ/(2w) + ... not clean.
#
# Actually, a SHARPER approach:
# The D_i form a "covering design" on n points.
# Each point is in at most Mw/n D_i's on average.
# Double-counting: Σ_i |D_i| = Mw.
# Each pair D_i, D_j covers |D_i ∪ D_j| ≥ n-k+1 points.
#
# By the handshaking lemma on the bipartite graph (points, sets):
# Σ_pos deg(pos) = Mw, where deg(pos) = #{i : pos ∈ D_i}.
# Σ_pos C(deg(pos), 2) = Σ_{i<j} |D_i ∩ D_j| ≤ C(M,2)·δ.
#
# By convexity: Σ C(deg(pos), 2) ≥ n · C(Mw/n, 2) (Jensen).
# Actually if deg distribution is (d_1,...,d_n) with Σ d_pos = Mw:
# Σ C(d_pos, 2) ≥ n · C(Mw/n, 2) by convexity of C(x,2) = x(x-1)/2.
#
# So: n · (Mw/n)(Mw/n - 1)/2 ≤ C(M,2)·δ
# Mw(Mw - n) ≤ M(M-1)nδ
# Mw - n ≤ (M-1)nδ/(Mw)  ... hmm, simplify:
# w(Mw - n) ≤ (M-1)nδ
# Mw² - nw ≤ Mnδ - nδ
# M(w² - nδ) ≤ nw - nδ = n(w - δ)
# If w² - nδ > 0: M ≤ n(w-δ)/(w²-nδ)

for n in [10, 12, 14, 16, 18, 20, 22, 24, 26, 50, 100]:
    k = n // 2
    w = math.ceil((1 - math.sqrt(k / n)) * n)
    delta = max(0, 2 * w - n + k - 1)
    denom = w * w - n * delta
    if denom > 0 and delta > 0:
        M_bound = n * (w - delta) / denom
        print(f"  n={n}: w={w}, δ={delta}, w²-nδ={denom}, M ≤ {M_bound:.1f}")
    elif delta == 0:
        print(f"  n={n}: w={w}, δ=0 (unique decoding zone)")
    else:
        print(f"  n={n}: w={w}, δ={delta}, denom={denom} ≤ 0 (bound not applicable)")
