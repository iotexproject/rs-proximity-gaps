#!/usr/bin/env python3
"""
Agreement graph analysis for M_actual bound.

For codewords f_1, ..., f_M in the list (distance ≤ w from center c):
- Agreement set A_i = {j ∈ [n] : f_i(ω^j) = c(ω^j)}, |A_i| ≥ n-w
- For any pair: A_i ∩ A_j has |A_i ∩ A_j| ≥ 2(n-w) - n = n - 2w
- f_i - f_j has degree < k and ≥ n-2w zeros
- If n-2w ≥ k: then f_i = f_j (unique decoding zone)
- If n-2w < k: f_i - f_j has "few" non-zeros (at most k-1 minus n-2w ... wait)

Actually: f_i - f_j has degree < k. It has ≥ |A_i ∩ A_j| ≥ n-2w zeros on L.
So it has at most n - (n-2w) = 2w positions where it's nonzero.
Actually no: f_i - f_j vanishes on A_i ∩ A_j but can be nonzero on [n] \ (A_i ∩ A_j).
|[n] \ (A_i ∩ A_j)| ≤ n - (n-2w) = 2w.

So d(f_i, f_j) ≤ 2w. But f_i - f_j is a polynomial of degree < k with at most 2w
nonzero evaluations on L. Since deg < k and L has n points:
number of zeros ≥ n - 2w, but if n - 2w ≥ k then f_i = f_j.

At Johnson radius w ≈ (1-√ρ)n:
n - 2w ≈ n(2√ρ - 1). For ρ = 1/2: n-2w ≈ 0.414n, k = 0.5n.
So n-2w < k. The polynomial f_i - f_j has degree < k and n-2w zeros,
with k - (n-2w) ≈ 0.086n "extra degrees of freedom."

Key question: how many degree-<k polynomials can have ≥ n-2w zeros on L?
This is a counting problem on the Reed-Solomon code.

More precisely: the set S = {f_i - f_j : i ≠ j} consists of degree-<k
polynomials with ≥ n-2w zeros on L and ≤ 2w nonzero evaluations.

These polynomials form a subset of the "low-weight" codewords of RS[n,k].
By the MDS property: a nonzero codeword of RS[n,k] has weight ≥ n-k+1.
So d(f_i, f_j) ≥ n-k+1 = n(1-ρ)+1.

For ρ = 1/2: d ≥ n/2 + 1. And d ≤ 2w ≈ 0.586n.
So n/2 + 1 ≤ d ≤ 0.586n. This leaves a "window" of possible distances.

The NUMBER of codewords of weight exactly d is:
A_d = C(n, d) Σ_{j=0}^{d-n+k-1} (-1)^j C(d, j) (p^{d-j-n+k} - 1)
(from the weight enumerator of RS codes).

If the differences f_i - f_j must lie in this sparse set of low-weight
codewords, and there are M(M-1)/2 pairs, we get a constraint on M.

Let's verify this numerically.
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

def eval_poly(coeffs, x, p):
    val = 0
    xpow = 1
    for c in coeffs:
        val = (val + c * xpow) % p
        xpow = xpow * x % p
    return val

# ================================================================
print("=" * 70)
print("AGREEMENT GRAPH ANALYSIS")
print("=" * 70)

for n, p_list in [(10, [11, 31]), (12, [13, 37]), (14, [29]), (16, [17]),
                   (18, [19])]:
    k = n // 2
    w = math.ceil((1 - math.sqrt(k / n)) * n)
    nk = n - k
    conds = nk - w

    for p in p_list:
        if (p - 1) % n != 0:
            continue
        omega = find_omega(n, p)
        L = [pow(omega, i, p) for i in range(n)]

        print(f"\n{'='*60}")
        print(f"n={n}, k={k}, w={w}, conds={conds}, p={p}")
        print(f"n-2w = {n-2*w}, k = {k}")
        print(f"Min codeword weight (MDS): {n-k+1}")
        print(f"Max pairwise distance: 2w = {2*w}")
        print(f"Distance window: [{n-k+1}, {2*w}]")

        # Enumerate ALL codewords (feasible for small p^k)
        if p**k > 500000:
            print(f"  p^k = {p**k} too large, sampling instead")

            # For large p^k: find a center with several close codewords
            import random
            random.seed(42 + n + p)

            best_M = 0
            best_list = []

            for trial in range(200):
                # Random center
                c_coeffs = [random.randint(0, p-1) for _ in range(n)]
                c_vals = [eval_poly(c_coeffs, L[i], p) for i in range(n)]

                # Find codewords close to c by random sampling
                close_cws = []
                for _ in range(5000):
                    f_coeffs = [random.randint(0, p-1) for _ in range(k)]
                    f_vals = [eval_poly(f_coeffs, L[i], p) for i in range(n)]
                    dist = sum(1 for i in range(n) if f_vals[i] != c_vals[i])
                    if dist <= w:
                        close_cws.append((tuple(f_coeffs), tuple(f_vals), dist))

                if len(close_cws) > best_M:
                    best_M = len(close_cws)
                    best_list = close_cws

            if best_M > 0:
                print(f"  Found {best_M} close codewords")
                for i, (fc, fv, d) in enumerate(best_list):
                    print(f"    f_{i}: dist={d}")
                if best_M >= 2:
                    # Pairwise distances
                    for i in range(len(best_list)):
                        for j in range(i+1, len(best_list)):
                            d_ij = sum(1 for pos in range(n)
                                       if best_list[i][1][pos] != best_list[j][1][pos])
                            print(f"    d(f_{i}, f_{j}) = {d_ij}")
            continue

        # Enumerate all codewords
        all_codewords = []
        for idx in range(p**k):
            coeffs = []
            tmp = idx
            for _ in range(k):
                coeffs.append(tmp % p)
                tmp //= p
            vals = tuple(eval_poly(coeffs, L[i], p) for i in range(n))
            all_codewords.append((tuple(coeffs), vals))

        print(f"  Enumerated {len(all_codewords)} codewords (p^k = {p**k})")

        # For each pair of codewords: compute distance
        dist_hist = Counter()
        low_weight_count = 0
        for i in range(len(all_codewords)):
            for j in range(i+1, len(all_codewords)):
                d = sum(1 for pos in range(n)
                        if all_codewords[i][1][pos] != all_codewords[j][1][pos])
                if n - k + 1 <= d <= 2 * w:
                    dist_hist[d] += 1
                    low_weight_count += 1

        print(f"  Codeword pairs in distance window [{n-k+1}, {2*w}]:")
        for d in sorted(dist_hist):
            print(f"    d={d}: {dist_hist[d]} pairs")
        print(f"  Total low-weight pairs: {low_weight_count}")

        # Find ALL centers with M_actual ≥ 2
        # For each pair (f_i, f_j) with d ≤ 2w: any center within distance w of both
        # is a center where both appear in the list.
        # Agreement: A_i ∩ A_j has size ≥ n - d(f_i, f_j)
        # A center c must satisfy: c agrees with f_i on ≥ n-w positions
        # AND c agrees with f_j on ≥ n-w positions.
        # The "good" positions for both: A_i ∩ A_j (where f_i = f_j = c)
        # has size ≥ n - d_ij.
        # So c must additionally agree with f_i on w - (d_ij - w) more positions
        # from where f_i ≠ f_j.

        # Count M_actual for ALL possible centers
        # This is O(p^n) — too large. Instead, find the max M_actual.
        print(f"\n  Finding max M_actual across all centers...")

        max_M = 0
        max_center = None
        max_list = []

        # Strategy: for each codeword f, c that agrees with f on ≥ n-w positions
        # is within distance w. Sample centers near random codewords.
        import random
        random.seed(42 + n + p)

        for trial in range(min(1000, len(all_codewords))):
            f_idx = random.randint(0, len(all_codewords) - 1)
            _, f_vals = all_codewords[f_idx]

            # Create a center by flipping w random positions
            flip_pos = random.sample(range(n), w)
            c_vals = list(f_vals)
            for pos in flip_pos:
                c_vals[pos] = (c_vals[pos] + random.randint(1, p-1)) % p
            c_vals = tuple(c_vals)

            # Count codewords within distance w of c
            close = []
            for idx2, (_, cw_vals) in enumerate(all_codewords):
                d = sum(1 for i in range(n) if cw_vals[i] != c_vals[i])
                if d <= w:
                    close.append((idx2, d))

            if len(close) > max_M:
                max_M = len(close)
                max_center = c_vals
                max_list = close

        print(f"  max M_actual found: {max_M}")
        if max_M >= 2:
            for idx, d in max_list:
                print(f"    f: dist={d}")
            # Pairwise distances in the list
            print(f"  Pairwise distances in best list:")
            for i in range(len(max_list)):
                for j in range(i+1, len(max_list)):
                    idx_i, _ = max_list[i]
                    idx_j, _ = max_list[j]
                    d = sum(1 for pos in range(n)
                            if all_codewords[idx_i][1][pos] != all_codewords[idx_j][1][pos])
                    print(f"    d(f_{i}, f_{j}) = {d}")
