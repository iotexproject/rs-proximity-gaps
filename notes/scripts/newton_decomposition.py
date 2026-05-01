#!/usr/bin/env python3
"""
Newton's identity decomposition of the character sum.

Key idea: express σ_j in terms of power sums p_k = Σ_{i∈B} ω^{ki}.
Since p_k is a sum over the subgroup (additive), its character sum
factors more naturally.

Newton's identities:
  σ_1 = p_1
  σ_2 = (σ_1 p_1 - p_2) / 2
  σ_3 = (σ_2 p_1 - σ_1 p_2 + p_3) / 3

General: k σ_k = Σ_{j=1}^{k} (-1)^{j+1} σ_{k-j} p_j

Or equivalently: σ_k = (1/k) Σ_{j=1}^{k} (-1)^{j+1} σ_{k-j} p_j

So σ is a POLYNOMIAL in (p_1, ..., p_w) of specific structure.

The character sum S(α) = Σ_B ψ(Σ_j α_j σ_j(B))
becomes a sum of ψ applied to a polynomial in power sums.

Power sums have the key property:
  p_k(B) = Σ_{i∈B} ω^{ki} = Σ_{i∈B} (ω^k)^i

This is a sum of terms, each depending on a single element of B.
So p_k factors into a "per-element" structure.

If the argument of ψ were LINEAR in p_k, the sum would factor as
a product. But σ_j for j≥2 is NONLINEAR in p — it involves products
of power sums. So the sum doesn't factor.

However, we can compute the degree of σ_j as a polynomial in p
and use that to bound the character sum.

This script:
1. Verifies Newton decomposition computationally
2. Computes the degree of σ_j in terms of p_k
3. Explores whether any useful factorization exists
"""

import math
import cmath
from itertools import combinations
from functools import lru_cache

PI2 = 2 * math.pi


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


def elem_sym(roots, p):
    w = len(roots)
    e = [0] * (w + 1)
    e[0] = 1
    for r in roots:
        for j in range(w, 0, -1):
            e[j] = (e[j] + e[j - 1] * r) % p
    return e


def power_sums(roots, p, max_k):
    """Compute power sums p_k = Σ r^k mod p for k=1,...,max_k."""
    ps = [0] * (max_k + 1)
    for k in range(1, max_k + 1):
        ps[k] = sum(pow(r, k, p) for r in roots) % p
    return ps


def sigma_from_newton(ps, w, p):
    """
    Compute σ_1,...,σ_w from power sums using Newton's identities.
    k σ_k = Σ_{j=1}^{k} (-1)^{j+1} σ_{k-j} p_j
    """
    sigma = [0] * (w + 1)
    sigma[0] = 1
    for k in range(1, w + 1):
        s = 0
        for j in range(1, k + 1):
            s += pow(-1, j + 1, p) * sigma[k - j] * ps[j]
        sigma[k] = s * pow(k, p - 2, p) % p  # k^{-1} mod p
    return sigma


def psi(x, p):
    return cmath.exp(1j * PI2 * (x % p) / p)


# ============================================================
# Part 1: Verify Newton decomposition
# ============================================================
print("=" * 70)
print("NEWTON'S IDENTITY DECOMPOSITION")
print("=" * 70)

for n, p_val in [(6, 7), (8, 17), (10, 11), (12, 13)]:
    k = n // 2
    w = math.ceil((1 - math.sqrt(k / n)) * n)
    omega = find_omega(n, p_val)
    L = [pow(omega, i, p_val) for i in range(n)]

    print(f"\nn={n}, k={k}, w={w}, p={p_val}")

    # Test on a few random subsets
    import random
    for trial in range(3):
        B = sorted(random.sample(range(n), w))
        roots = [L[i] for i in B]

        # Direct elementary symmetric
        es_direct = elem_sym(roots, p_val)

        # Via Newton
        ps = power_sums(roots, p_val, w)
        es_newton = sigma_from_newton(ps, w, p_val)

        match = all(es_direct[j] % p_val == es_newton[j] % p_val for j in range(w + 1))
        print(f"  B={B}: direct={[e % p_val for e in es_direct[1:]]}, "
              f"newton={[e % p_val for e in es_newton[1:]]}, {'OK' if match else 'FAIL'}")


# ============================================================
# Part 2: Structure of power sums p_k(B) for subgroup elements
# ============================================================
print("\n\n" + "=" * 70)
print("POWER SUM STRUCTURE")
print("=" * 70)
print("For B ⊂ Z/nZ, p_k(B) = Σ_{i∈B} ω^{ki}")
print("Key: ω^{ki} = (ω^k)^i, so p_k depends on ω^k = ω_k")
print("If gcd(k,n) = d, then ω^k has order n/d")
print()

for n in [6, 8, 10, 12]:
    print(f"n={n}:")
    k_rs = n // 2
    w = math.ceil((1 - math.sqrt(k_rs / n)) * n)
    for kk in range(1, w + 1):
        d = math.gcd(kk, n)
        order = n // d
        print(f"  p_{kk}: ω^{kk} has order {order} = n/{d}, "
              f"Σ ω^{{ki}} sums over {order}-th roots (with multiplicity if d>1)")
    print()


# ============================================================
# Part 3: Factorization attempt via "per-element" structure
# ============================================================
print("=" * 70)
print("FACTORIZATION ANALYSIS")
print("=" * 70)
print()
print("For LINEAR functions of σ: F(B) = Σ_j α_j σ_j(B)")
print("Question: can we decompose F into functions of individual elements?")
print()

# For σ_1 (= p_1): F = α_1 p_1 = α_1 Σ ω^{b_i}
#   → ψ(F) = Π_i ψ(α_1 ω^{b_i})  (FACTORS!)
# For σ_2 = (p_1² - p_2)/2: F = α_2 (p_1² - p_2)/2
#   → involves p_1² which COUPLES all b_i's. Does NOT factor.

print("σ_1 = p_1 → ψ(α_1 σ_1) = Π_i ψ(α_1 ω^{b_i}) → FACTORS")
print("σ_2 = (p_1² - p_2)/2 → involves p_1² → does NOT factor")
print("σ_w = ω^{Σ b_i} → ψ(α_w σ_w) = Π_i ψ'(b_i) → FACTORS (multiplicatively)")
print()

# So among σ_1,...,σ_w, only σ_1 and σ_w give factoring character sums.
# For σ_1: S(α_1,0,...,0) = Σ_B Π_{i∈B} ψ(α_1 ω^{b_i})
#   = [z^w] Π_{j=0}^{n-1} (1 + z ψ(α_1 ω^j))   ???

# Not quite — we're summing over SUBSETS, not ordered tuples.
# But the elementary symmetric polynomial approach gives:
# Σ_{B,|B|=w} Π_{i∈B} x_i = e_w(x_0,...,x_{n-1})

# So: S(α_1,0,...,0) = e_w(ψ(α_1 ω^0), ψ(α_1 ω^1), ..., ψ(α_1 ω^{n-1}))

# But wait, ψ is NOT multiplicative in the F_p sense, it's a complex exponential.
# So this doesn't directly apply.

# Let me reconsider. The character sum is:
# S(α) = Σ_B ψ(Σ_j α_j σ_j(B))
# = Σ_B ψ(F(B))  where F(B) ∈ F_p

# For F = α_1 σ_1 = α_1 Σ_{i∈B} ω^i:
# S = Σ_B ψ(α_1 Σ_{i∈B} ω^i) = Σ_B Π_{i∈B} ψ(α_1 ω^i)

# This factors! And the sum becomes:
# S = e_w(ψ(α_1 ω^0), ..., ψ(α_1 ω^{n-1}))
# where e_w is the w-th elementary symmetric polynomial of COMPLEX numbers.

print("=" * 70)
print("σ_1-ONLY CHARACTER SUM: PRODUCT FORMULA")
print("=" * 70)
print()
print("S(α_1, 0,...,0) = e_w(ψ(α_1·1), ψ(α_1·ω), ..., ψ(α_1·ω^{n-1}))")
print("where e_w is the w-th elementary symmetric poly of complex numbers.")
print()

# Verify this!
for n, p_val in [(6, 7), (8, 17), (10, 11)]:
    k_rs = n // 2
    w = math.ceil((1 - math.sqrt(k_rs / n)) * n)
    omega = find_omega(n, p_val)
    L = [pow(omega, i, p_val) for i in range(n)]

    for alpha1 in [1, 2, 3]:
        # Direct computation
        S_direct = 0j
        for B in combinations(range(n), w):
            roots = [L[i] for i in B]
            sigma1 = sum(roots) % p_val
            S_direct += psi(alpha1 * sigma1, p_val)

        # Product formula: e_w of complex values
        z_vals = [psi(alpha1 * L[i], p_val) for i in range(n)]
        # Compute e_w(z_0,...,z_{n-1}) using dynamic programming
        # dp[j] = e_j(z_0,...,z_{i})
        dp = [0j] * (w + 1)
        dp[0] = 1
        for z in z_vals:
            for j in range(min(w, len([x for x in dp if x != 0])), 0, -1):
                dp[j] += dp[j - 1] * z
        S_product = dp[w]

        err = abs(S_direct - S_product)
        print(f"  n={n}, p={p_val}, α_1={alpha1}: S_direct={S_direct:.4f}, "
              f"S_product={S_product:.4f}, err={err:.2e}")


# ============================================================
# Part 4: The generating function identity
# ============================================================
print("\n\n" + "=" * 70)
print("GENERATING FUNCTION IDENTITY")
print("=" * 70)
print()
print("Key: Σ_{w=0}^n e_w(z_0,...,z_{n-1}) · u^w = Π_{i=0}^{n-1} (1 + u·z_i)")
print()
print("For z_i = ψ(α·ω^i):")
print("  Π_i (1 + u·ψ(α·ω^i))")
print()
print("This is a PRODUCT over n-th roots of unity — can be evaluated via")
print("the resultant or DFT-type computation!")
print()

# The product Π_{i=0}^{n-1} (1 + u·ψ(α·ω^i)) is:
# = Π_{i=0}^{n-1} (1 + u·e^{2πi α ω^i/p})
#
# The coefficient of u^w in this product is S(α,0,...,0).
#
# For α = 0: z_i = 1 for all i, so Π(1+u) = (1+u)^n, and [u^w] = C(n,w). ✓
#
# For general α: this is a product of n terms, each a linear function of u.
# The product can be computed in O(n²) or O(n log n) time.
#
# More importantly: if we can compute |[u^w] Π(1+u·ψ(αω^i))| analytically,
# we get bounds on S(α,0,...,0).

# Let's compute this for small cases and see the pattern.
for n, p_val in [(6, 7), (8, 17), (10, 11)]:
    k_rs = n // 2
    w = math.ceil((1 - math.sqrt(k_rs / n)) * n)
    omega = find_omega(n, p_val)
    L = [pow(omega, i, p_val) for i in range(n)]

    print(f"\nn={n}, p={p_val}, w={w}:")

    max_S1 = 0
    for alpha in range(1, p_val):
        z_vals = [psi(alpha * L[i], p_val) for i in range(n)]

        # Compute Π(1+u·z_i) via polynomial multiplication
        poly = [1 + 0j]
        for z in z_vals:
            new_poly = [0j] * (len(poly) + 1)
            for j, c in enumerate(poly):
                new_poly[j] += c
                new_poly[j + 1] += c * z
            poly = new_poly

        S_w = poly[w]
        mag = abs(S_w)
        max_S1 = max(max_S1, mag)

        if alpha <= 3:
            print(f"  α={alpha}: |S(α,0,...,0)| = {mag:.4f}, S = {S_w:.4f}")
            # Also show the full generating polynomial magnitudes
            mags = [abs(poly[j]) for j in range(len(poly))]
            print(f"    |coeff| = {[f'{m:.2f}' for m in mags]}")

    print(f"  max|S(α,0,...,0)| over all α = {max_S1:.4f}")
    print(f"  C(n,w)/n = {math.comb(n,w)/n:.4f}")
    print(f"  √C(n,w) = {math.sqrt(math.comb(n,w)):.4f}")


# ============================================================
# Part 5: General α — attempt multi-variable generating function
# ============================================================
print("\n\n" + "=" * 70)
print("GENERAL α: MULTI-VARIABLE ANALYSIS")
print("=" * 70)
print()
print("For S(α) = Σ_B ψ(Σ_j α_j σ_j(B)):")
print("We have σ_j(B) = e_j(ω^{b_1},...,ω^{b_w}).")
print()
print("Key identity: Σ_j α_j e_j(x_1,...,x_w) = [coefficient extraction from")
print("  Π_i Σ_j α_j x_i^{w-j}...] — but this doesn't factor nicely.")
print()

# Actually, there IS a generating function approach for the general case!
# Define g(x) = Σ_{j=0}^w α_j x^j (a polynomial of degree w).
# Then Σ_j α_j e_j(x_1,...,x_w) = ???
#
# NOT directly related to g evaluated at anything, because e_j is a
# symmetric polynomial, not a power.
#
# But consider: Π_{i=1}^w (1 + x_i z) = Σ_j e_j z^j
# So Σ_j α_j e_j = (coefficient-weighted sum) = α · (e_0,...,e_w)
#
# This is just a linear form, which we already knew.
#
# The question is whether the SUM over B can be evaluated.
#
# Σ_B ψ(α · σ(B)) = Σ_B ψ(α_0 + α_1 σ_1 + ... + α_w σ_w)
# (with σ_0 = 1, so α_0 is a constant phase)
#
# = ψ(α_0) · Σ_B ψ(α_1 σ_1 + ... + α_w σ_w)
#
# For the SUM to factor, we'd need ψ(α_1 σ_1 + ... + α_w σ_w) to
# factor as Π_{i∈B} f(ω^i) for some function f. This happens only when
# the argument is LINEAR in the individual ω^{b_i}, i.e., only for σ_1.
#
# For σ_w = Π ω^{b_i}, we have ψ(α_w σ_w) = ψ(α_w · Π ω^{b_i}),
# which does NOT factor as Π f(ω^{b_i}) because ψ is additive, not multiplicative.
#
# HOWEVER: σ_w = ω^{Σ b_i}, so ψ(α_w σ_w) = ψ(α_w ω^{Σ b_i}).
# And ψ(α_w ω^{a+b}) ≠ ψ(α_w ω^a) ψ(α_w ω^b) in general.
# So σ_w also doesn't factor through ψ.
#
# Wait, but the subset sum Σ b_i is additive:
# ψ(α_w ω^{Σ b_i}) depends on Σ b_i, which IS additive.
# But ω^{Σ b_i} = Π ω^{b_i}, and applying ψ doesn't distribute over products.

# KEY INSIGHT: The only case that factors is σ_1 (additive).
# For all other σ_j (j ≥ 2), the character sum is fundamentally non-factoring.

# Let's verify: compare |S(α_1,0,...,0)| with |S(0,...,0,α_w)|
# and |S(α_1,...,α_w)| for a mixed case.

print("\nComparison of character sum magnitudes:")
print(f"{'n':>3} {'p':>4} {'|S(α_1,0,...)|':>15} {'|S(0,...,α_w)|':>15} {'|S(mixed)|':>12}")
print("-" * 55)

for n, p_val in [(6, 7), (6, 13), (8, 17), (10, 11)]:
    k_rs = n // 2
    w = math.ceil((1 - math.sqrt(k_rs / n)) * n)
    omega = find_omega(n, p_val)
    L = [pow(omega, i, p_val) for i in range(n)]

    max_S1 = 0  # max for α_1-only
    max_Sw = 0  # max for α_w-only
    max_Sm = 0  # max for mixed

    for alpha in range(1, p_val):
        # σ_1-only
        S1 = 0j
        for B in combinations(range(n), w):
            roots = [L[i] for i in B]
            s1 = sum(roots) % p_val
            S1 += psi(alpha * s1, p_val)
        max_S1 = max(max_S1, abs(S1))

        # σ_w-only
        Sw = 0j
        for B in combinations(range(n), w):
            roots = [L[i] for i in B]
            es = elem_sym(roots, p_val)
            Sw += psi(alpha * es[w], p_val)
        max_Sw = max(max_Sw, abs(Sw))

        # Mixed: α_1 = α, α_w = 1
        Sm = 0j
        for B in combinations(range(n), w):
            roots = [L[i] for i in B]
            es = elem_sym(roots, p_val)
            Sm += psi(alpha * es[1] + es[w], p_val)
        max_Sm = max(max_Sm, abs(Sm))

    N = math.comb(n, w)
    print(f"{n:3d} {p_val:4d} {max_S1:15.4f} {max_Sw:15.4f} {max_Sm:12.4f}  (N={N})")
