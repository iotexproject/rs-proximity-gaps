#!/usr/bin/env python3
"""
Verify: for conds/B = 1, the WORST-CASE center has the condition σ_w = const,
which gives M_alg = N(n,w,s*) = max_s N(n,w,s).

For gcd(w,n) = 1: N(n,w,s) = C(n,w)/n (uniform), so M_alg = C(n,w)/n.

Question: does M_actual = M_alg = C(n,w)/n for the σ_w-only center?
This requires: all C(n,w)/n compatible subsets give distinct codewords at distance exactly w.
"""

from itertools import combinations
import math


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
    g = find_primitive_root(p)
    return pow(g, (p - 1) // n, p)


def johnson_radius(n, k):
    return math.ceil((1 - math.sqrt(k / n)) * n)


def smallest_prime(n, start=2):
    p = start
    while True:
        if p % n == 1:
            is_prime = p > 1
            for d in range(2, int(p ** 0.5) + 1):
                if p % d == 0:
                    is_prime = False
                    break
            if is_prime:
                return p
        p += 1


def check_case(n, k, p, w):
    """For conds/B = 1, construct σ_w-only center and verify M_actual."""
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    conds = n - w - k

    if conds != 1:
        return None

    # Center: c_high = (1, 0, ..., 0, 1) — only c_k and c_{n-1} nonzero
    # This gives condition: c_k + (-1)^w σ_w c_{n-1} = 0
    # i.e., 1 + (-1)^w σ_w = 0
    # σ_w = (-1)^{w+1} = ω^s for some s

    c_high = [0] * (n - k)
    c_high[0] = 1   # c_k = 1
    c_high[-1] = 1  # c_{n-1} = 1

    # Condition: from the derivation, the condition at m = n-1:
    # Σ_{j=0}^w (-1)^j σ_j c_{n-1-w+j} = 0
    # = c_{n-1-w} - σ_1 c_{n-w} + ... + (-1)^w σ_w c_{n-1}
    # With c_high = (1, 0, ..., 0, 1):
    # c_k = c_{n-1-w+...hmm, let me just compute

    # Actually, let me compute the condition directly:
    # Condition at m = k+w = n-1 (since conds/B=1 means k+w = n-1):
    # Σ_{j=0}^w (-1)^j σ_j c_{k+j} = 0
    # c_k = c_high[0] = 1
    # c_{k+1} = c_high[1] = 0 (if w > 1)
    # ...
    # c_{k+w} = c_{n-1} = c_high[n-k-1] = 1

    print(f"\n{'='*60}")
    print(f"n={n}, k={k}, w={w}, p={p}, conds/B={conds}")

    # Compute condition coefficients
    cond_str = []
    for j in range(w + 1):
        c_idx = j  # index into c_high: c_{k+j} = c_high[j]
        c_val = c_high[c_idx] if c_idx < len(c_high) else 0
        sign = pow(-1, j, p)
        if c_val != 0:
            if j == 0:
                cond_str.append(f"{sign * c_val % p}")
            else:
                cond_str.append(f"{sign * c_val % p}·σ_{j}")
    print(f"Condition: {' + '.join(cond_str)} = 0")

    # Compute c_vals
    c_coeffs = [0] * k + list(c_high)
    c_vals = [sum(c_coeffs[j] * pow(L[i], j, p) for j in range(n)) % p
              for i in range(n)]

    # Find all compatible B's via σ_w condition
    target_sw = (p - 1) % p  # σ_w = (-1)^{w+1} mod p? Let me compute directly
    # Condition: c_k + (-1)^w σ_w c_{n-1} = 0
    # 1 + (-1)^w σ_w = 0 → σ_w = (-1)^{w+1} = p-1 if w even, 1 if w odd... wait

    # Direct computation: σ_0 c_k + Σ (-1)^j σ_j c_{k+j}
    # = 1·1 + (only σ_w gets c_{k+w}=c_{n-1}=1: (-1)^w σ_w · 1)
    # = 1 + (-1)^w σ_w = 0
    # σ_w = (-1)^{w+1}
    if w % 2 == 1:
        target_sw = 1
    else:
        target_sw = p - 1

    print(f"σ_w = {target_sw}")

    # Count subsets with σ_w = target_sw
    from itertools import combinations

    def elem_sym_w(roots, w_val, p):
        """Compute just σ_w = product of roots."""
        prod = 1
        for r in roots:
            prod = prod * r % p
        return prod

    compat_B = []
    for B in combinations(range(n), w):
        roots = [L[i] for i in B]
        sw = elem_sym_w(roots, w, p)
        if sw == target_sw:
            compat_B.append(B)

    M_alg = len(compat_B)
    N_uniform = math.comb(n, w) // n  # expected if uniform

    print(f"M_alg = {M_alg} (N(n,w,s*) for sum giving σ_w={target_sw})")
    print(f"C(n,w)/n = {math.comb(n,w)}/{n} = {N_uniform}")
    print(f"gcd(w,n) = {math.gcd(w,n)}")

    # Now check M_actual: interpolate for each compatible B
    codewords = set()
    dists = {}
    for B in compat_B:
        S = [i for i in range(n) if i not in B]
        m_sys = len(S)
        aug = [[pow(L[S[i]], j, p) for j in range(k)] + [c_vals[S[i]]]
               for i in range(m_sys)]
        pivot_cols = []
        for col in range(k):
            piv = -1
            for row in range(len(pivot_cols), m_sys):
                if aug[row][col] % p != 0:
                    piv = row
                    break
            if piv == -1:
                continue
            r2 = len(pivot_cols)
            aug[r2], aug[piv] = aug[piv], aug[r2]
            inv_p = pow(aug[r2][col], p - 2, p)
            for row in range(m_sys):
                if row != r2 and aug[row][col] % p != 0:
                    f2 = aug[row][col] * inv_p % p
                    for j2 in range(k + 1):
                        aug[row][j2] = (aug[row][j2] - f2 * aug[r2][j2]) % p
            pivot_cols.append(col)
        consistent = True
        for row in range(len(pivot_cols), m_sys):
            if aug[row][k] % p != 0:
                consistent = False
                break
        if not consistent:
            continue
        a = [0] * k
        for idx2, col in enumerate(pivot_cols):
            a[col] = aug[idx2][k] * pow(aug[idx2][col], p - 2, p) % p
        f_vals = tuple(sum(a[j] * pow(L[i], j, p) for j in range(k)) % p
                      for i in range(n))
        d = sum(1 for i in range(n) if c_vals[i] != f_vals[i])
        codewords.add(f_vals)
        dists[d] = dists.get(d, 0) + 1

    M_actual = len(codewords)
    print(f"M_actual = {M_actual}")
    print(f"Distances: {dict(sorted(dists.items()))}")
    print(f"M_actual = M_alg? {'YES' if M_actual == M_alg else 'NO (overcounting!)'}")

    return M_actual, M_alg


# Test conds/B = 1 cases at rate 1/2
print("=" * 60)
print("conds/B = 1 CASES: M = C(n,w)/n ?")
print("=" * 60)

# n = 2m, k = m, w = m-1 → conds/B = 2m - (m-1) - m = 1
# Johnson: w = ceil((1-1/√2)n). For rate 1/2:
# w/n = 1 - 1/√2 ≈ 0.293. So w = ceil(0.293n).
# conds/B = n - w - k = n - w - n/2 = n/2 - w.
# For conds/B = 1: n/2 - w = 1, i.e., w = n/2 - 1.
# But Johnson w = ceil(0.293n) ≈ 0.293n. And n/2 - 1 ≈ 0.5n.
# These don't match! conds/B = 1 requires w = n/2 - 1, but Johnson gives w ≈ 0.293n.

# So for rate 1/2 at Johnson radius, conds/B ≈ n/2 - 0.293n = 0.207n ≥ 1 for n ≥ 5.
# conds/B = 1 only for small n where ceil(0.293n) = n/2 - 1.
# n=6: w=2, n/2-1=2. conds/B = 1. ✓
# n=8: w=3, n/2-1=3. conds/B = 1. ✓
# n=10: w=3, n/2-1=4. conds/B = 2. ✗

# So conds/B = 1 at Johnson radius only for n ≤ 8 (rate 1/2).
# For other rates:
# k = n-2, w=1 → conds/B = n-1-n+2=1 (but trivial)
# k = n/3, Johnson w ≈ (1-√(1/3))n ≈ 0.423n. conds/B = n-0.423n-n/3 = 0.244n.

for n in [6, 8]:
    k = n // 2
    w = johnson_radius(n, k)
    for p in [smallest_prime(n, n+1), smallest_prime(n, 3*n+1)]:
        check_case(n, k, p, w)

# What about non-rate-1/2 cases with conds/B = 1?
# conds/B = n - w - k = 1 means w = n - k - 1.
# Johnson: w = ceil((1-√(k/n))n)
# So: n-k-1 = ceil((1-√(k/n))n)
# For large n: n-k-1 ≈ n(1-√(k/n)) → k/n ≈ (1+1/n)^2 ≈ 1. Near rate 1.
# Specifically: 1-k/n-1/n = 1-√(k/n) → √(k/n) = k/n+1/n →
# Let ρ = k/n: √ρ = ρ + 1/n. For large n: √ρ ≈ ρ, so ρ ≈ 1. Not useful.

# For small n: check manually
print(f"\n{'='*60}")
print("SCAN: (n,k) pairs with conds/B = 1 at Johnson radius")
print("="*60)
for n in range(4, 30):
    for k in range(1, n):
        w = johnson_radius(n, k)
        if w <= 0 or w >= n:
            continue
        conds = n - w - k
        if conds == 1:
            # Check if it's non-trivial (w >= 2)
            if w >= 2:
                print(f"n={n}, k={k}, ρ={k/n:.3f}, w={w}, conds/B=1, "
                      f"C(n,w)={math.comb(n,w)}, C(n,w)/n={math.comb(n,w)/n:.1f}, "
                      f"gcd(w,n)={math.gcd(w,n)}")
