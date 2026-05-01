#!/usr/bin/env python3
"""
Direction A — Polynomial Factorization Exploration (Round 1)

Key constraint: In max-M list, ALL pairwise differences f_i - f_j are
minimum-weight RS codewords (degree < k, exactly k-1 zeros on L).

This means g_{ij}(x) = a_{ij} * Prod_{l in Z_{ij}} (x - omega^l)
where Z_{ij} subset L, |Z_{ij}| = k-1.

TRANSITIVITY: g_{12} + g_{23} = g_{13}, so
  a_{12} * P_{Z12} + a_{23} * P_{Z23} = a_{13} * P_{Z13}

Sum of two degree-(k-1) products from L must be another such product.
This is extremely restrictive.

Experiments:
A. Enumerate all min-weight codewords of RS[n,k] over F_p
B. Find max cliques in the "difference graph" (pairs of codewords at d_min)
C. Verify transitivity constraint: when does P_Z1 + a*P_Z2 factor completely over L?
D. Count factorizable sums vs total sums (sparsity measure)
E. Structural analysis of zero sets in max-M lists
"""

import itertools
from collections import defaultdict

def find_primitive_root(p):
    for g in range(2, p):
        seen = set()
        val = 1
        for _ in range(p - 1):
            seen.add(val)
            val = val * g % p
        if len(seen) == p - 1:
            return g
    return None

def find_omega(g, p, n):
    """Find primitive n-th root of unity in F_p."""
    assert (p - 1) % n == 0
    return pow(g, (p - 1) // n, p)

def poly_eval(coeffs, x, p):
    """Evaluate polynomial with coefficients [c0, c1, ..., c_{k-1}] at x mod p."""
    val = 0
    xpow = 1
    for c in coeffs:
        val = (val + c * xpow) % p
        xpow = xpow * x % p
    return val

def poly_from_roots(roots, p):
    """Build monic polynomial from roots. Returns [c0, c1, ..., c_d, 1]."""
    poly = [1]  # constant 1
    for r in roots:
        # multiply by (x - r)
        new_poly = [0] * (len(poly) + 1)
        for i, c in enumerate(poly):
            new_poly[i + 1] = (new_poly[i + 1] + c) % p
            new_poly[i] = (new_poly[i] - c * r) % p
        poly = new_poly
    return poly  # poly[i] = coefficient of x^i

def johnson_w(n, k):
    """Johnson radius for MDS code: w = floor(n - sqrt(n*(k-1)))."""
    import math
    return int(math.floor(n - math.sqrt(n * (k - 1))))

def primes_1modn(n, count=5):
    """Find primes p ≡ 1 mod n."""
    result = []
    p = n + 1
    while len(result) < count:
        if all(p % i != 0 for i in range(2, int(p**0.5) + 1)):
            if p % n == 1:
                result.append(p)
        p += 1 if p == 2 else (n if (p - 1) % n == 0 else 1)
        if p > 10000:
            break
    # fallback: brute force
    if len(result) < count:
        result = []
        for p in range(n + 1, 10000):
            if p % n != 1:
                continue
            if all(p % i != 0 for i in range(2, int(p**0.5) + 1)):
                result.append(p)
                if len(result) >= count:
                    break
    return result

# ============================================================
# Experiment A: Enumerate min-weight codewords
# ============================================================
def exp_A_minweight_codewords(n, p):
    """Enumerate all minimum-weight codewords of RS[n,k] on L = <omega>."""
    print(f"\n{'='*60}")
    print(f"Exp A: Min-weight codewords of RS[{n},{n//2}] over F_{p}")
    print(f"{'='*60}")

    k = n // 2
    d_min = n - k + 1  # = n/2 + 1
    w = johnson_w(n, k)

    g = find_primitive_root(p)
    omega = find_omega(g, p, n)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"  k={k}, d_min={d_min}, Johnson w={w}")
    print(f"  omega={omega}, L={L[:8]}...")

    # A min-weight codeword has weight d_min = n-k+1
    # It has k-1 zeros on L, so it's determined by:
    #   - choice of k-1 element zero set Z subset [n], |Z|=k-1
    #   - leading coefficient (scalar)
    # f(x) = a * Prod_{i in Z} (x - L[i]), degree k-1

    min_weight_count = 0
    zero_sets = []

    for Z in itertools.combinations(range(n), k - 1):
        # Build monic polynomial from these roots
        roots = [L[i] for i in Z]
        poly = poly_from_roots(roots, p)
        # poly has degree k-1, coefficients poly[0..k-1]

        # Evaluate on L to find weight
        evals = [poly_eval(poly, L[i], p) for i in range(n)]
        weight = sum(1 for v in evals if v != 0)

        if weight == d_min:
            min_weight_count += 1
            zero_sets.append(Z)

    print(f"  Total zero sets C({n},{k-1}) = {len(list(itertools.combinations(range(n), k-1)))}")
    print(f"  Min-weight codewords (up to scalar): {min_weight_count}")

    # Every (k-1)-subset of L gives a polynomial of degree k-1
    # Its weight on L is n - (k-1) = n-k+1 = d_min
    # So EVERY such subset gives a min-weight codeword!
    expected = len(list(itertools.combinations(range(n), k - 1)))
    print(f"  Expected (all C(n,k-1)): {expected}")
    print(f"  Match: {min_weight_count == expected}")

    return L, zero_sets, k, d_min, w

# ============================================================
# Experiment B: Max-M list structure
# ============================================================
def exp_B_max_M_list(n, p):
    """Find max-M list and analyze its polynomial structure."""
    print(f"\n{'='*60}")
    print(f"Exp B: Max-M list for RS[{n},{n//2}] over F_{p}")
    print(f"{'='*60}")

    k = n // 2
    d_min = n - k + 1
    w = johnson_w(n, k)

    g = find_primitive_root(p)
    omega = find_omega(g, p, n)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"  k={k}, d_min={d_min}, w={w}")

    # Enumerate ALL RS_k codewords (only feasible for small p^k)
    if p**k > 500000:
        print(f"  p^k = {p**k} too large, sampling instead")
        return None

    # Generate all codewords: f(x) = c0 + c1*x + ... + c_{k-1}*x^{k-1}
    codewords = []
    for coeffs_tuple in itertools.product(range(p), repeat=k):
        evals = tuple(poly_eval(list(coeffs_tuple), L[i], p) for i in range(n))
        codewords.append((coeffs_tuple, evals))

    print(f"  Total codewords: {len(codewords)}")

    # For each center c (try random ones + zero center), find list size
    best_M = 0
    best_center = None
    best_list = None

    # Try the zero codeword as center first
    import random
    random.seed(42)

    centers_to_try = [tuple([0]*n)]  # zero center
    # Add some random centers
    for _ in range(min(200, p**k)):
        c_coeffs = tuple(random.randint(0, p-1) for _ in range(k))
        c_evals = tuple(poly_eval(list(c_coeffs), L[i], p) for i in range(n))
        centers_to_try.append(c_evals)

    # Also try non-codeword centers (random evaluation vectors)
    for _ in range(200):
        c_evals = tuple(random.randint(0, p-1) for _ in range(n))
        centers_to_try.append(c_evals)

    for c_evals in centers_to_try:
        # Count codewords within Johnson radius w
        close = []
        for coeffs, evals in codewords:
            dist = sum(1 for i in range(n) if evals[i] != c_evals[i])
            if dist <= w:
                close.append((coeffs, evals, dist))

        M = len(close)
        if M > best_M:
            best_M = M
            best_center = c_evals
            best_list = close

    print(f"  Best M_actual = {best_M}")

    if best_M < 2:
        print("  M < 2, no pairwise analysis possible")
        return None

    # Analyze pairwise distances
    print(f"\n  Pairwise distances in best list:")
    dists = defaultdict(int)
    for i in range(len(best_list)):
        for j in range(i+1, len(best_list)):
            d = sum(1 for l in range(n) if best_list[i][1][l] != best_list[j][1][l])
            dists[d] += 1

    for d in sorted(dists):
        print(f"    d={d}: {dists[d]} pairs")

    # For each pair at d_min, analyze the difference polynomial
    print(f"\n  Difference polynomials (pairs at d_min={d_min}):")
    diff_zero_sets = []
    for i in range(len(best_list)):
        for j in range(i+1, len(best_list)):
            d = sum(1 for l in range(n) if best_list[i][1][l] != best_list[j][1][l])
            if d == d_min:
                # Difference polynomial coefficients
                diff_coeffs = tuple((best_list[i][0][c] - best_list[j][0][c]) % p for c in range(k))
                diff_evals = tuple((best_list[i][1][l] - best_list[j][1][l]) % p for l in range(n))
                zeros = tuple(l for l in range(n) if diff_evals[l] == 0)
                nonzeros = tuple(l for l in range(n) if diff_evals[l] != 0)
                diff_zero_sets.append((i, j, zeros, nonzeros, diff_coeffs))
                if len(diff_zero_sets) <= 10:
                    print(f"    f_{i}-f_{j}: zeros={zeros}, #zeros={len(zeros)}, coeffs={diff_coeffs}")

    print(f"\n  Total d_min pairs: {len(diff_zero_sets)}")

    return best_list, diff_zero_sets, L, k, d_min, w, p

# ============================================================
# Experiment C: Transitivity constraint
# ============================================================
def exp_C_transitivity(n, p):
    """Check: when does P_Z1 + a*P_Z2 factor completely over L?"""
    print(f"\n{'='*60}")
    print(f"Exp C: Transitivity — sum of root products over L")
    print(f"  RS[{n},{n//2}] over F_{p}")
    print(f"{'='*60}")

    k = n // 2

    g = find_primitive_root(p)
    omega = find_omega(g, p, n)
    L = [pow(omega, i, p) for i in range(n)]

    # For each pair of (k-1)-subsets Z1, Z2 of [n], and scalar a in F_p*,
    # check if P_{Z1} + a*P_{Z2} has exactly k-1 zeros on L
    # (i.e., is also a min-weight codeword)

    # Too many pairs for large n, so sample
    subsets = list(itertools.combinations(range(n), k - 1))

    if len(subsets) > 500:
        import random
        random.seed(42)
        sample_subsets = random.sample(subsets, min(100, len(subsets)))
    else:
        sample_subsets = subsets

    total_pairs = 0
    factorizable_count = 0
    factorizable_examples = []

    for Z1 in sample_subsets[:30]:
        roots1 = [L[i] for i in Z1]
        P1 = poly_from_roots(roots1, p)
        evals1 = [poly_eval(P1, L[i], p) for i in range(n)]

        for Z2 in sample_subsets[:30]:
            if Z1 == Z2:
                continue
            roots2 = [L[i] for i in Z2]
            P2 = poly_from_roots(roots2, p)
            evals2 = [poly_eval(P2, L[i], p) for i in range(n)]

            for a in range(1, min(p, 20)):
                total_pairs += 1
                # Evaluate P1 + a*P2 on L
                sum_evals = [(evals1[i] + a * evals2[i]) % p for i in range(n)]
                zeros = sum(1 for v in sum_evals if v == 0)

                if zeros == k - 1:
                    factorizable_count += 1
                    zero_set = tuple(i for i in range(n) if sum_evals[i] == 0)
                    if len(factorizable_examples) < 10:
                        factorizable_examples.append((Z1, Z2, a, zero_set))

    print(f"  Tested {total_pairs} triples (Z1, Z2, a)")
    print(f"  Factorizable (k-1 zeros on L): {factorizable_count}")
    print(f"  Ratio: {factorizable_count/max(1,total_pairs):.6f}")

    if factorizable_examples:
        print(f"\n  Examples:")
        for Z1, Z2, a, Z3 in factorizable_examples[:5]:
            print(f"    Z1={Z1}, Z2={Z2}, a={a} -> Z3={Z3}")

    # Expected: if random, probability ≈ C(n,k-1)/p^{k-1} ≈ tiny
    import math
    expected_prob = math.comb(n, k-1) / p**(k-1)
    print(f"\n  Random baseline prob: C({n},{k-1})/p^{k-1} = {expected_prob:.6f}")
    print(f"  Observed vs random: {factorizable_count/max(1,total_pairs)/max(1e-12,expected_prob):.2f}x")

    return factorizable_count, total_pairs

# ============================================================
# Experiment D: x^n - 1 factorization constraint
# ============================================================
def exp_D_cyclotomic(n, p):
    """Analyze how x^n - 1 factors over F_p and what this constrains."""
    print(f"\n{'='*60}")
    print(f"Exp D: Cyclotomic factorization of x^{n}-1 over F_{p}")
    print(f"{'='*60}")

    k = n // 2
    g = find_primitive_root(p)
    omega = find_omega(g, p, n)
    L = [pow(omega, i, p) for i in range(n)]

    # x^n - 1 = Prod_{d|n} Phi_d(x) over Q
    # Over F_p, Phi_d may factor further

    # Find the factorization by computing gcd with x^{p^j} - x
    # For each divisor d of n, Phi_d splits into phi(d)/ord_d(p) factors of degree ord_d(p)

    divisors = [d for d in range(1, n+1) if n % d == 0]
    print(f"  Divisors of {n}: {divisors}")

    # ord_d(p) = multiplicative order of p mod d
    for d in divisors:
        if d == 1:
            ord_d = 1
        else:
            ord_d = 1
            val = p % d
            while val != 1:
                val = val * p % d
                ord_d += 1

        from math import gcd
        phi_d = sum(1 for i in range(1, d+1) if gcd(i, d) == 1)
        num_factors = phi_d // ord_d if ord_d > 0 else 0
        print(f"  Phi_{d}: deg={phi_d}, ord_{d}(p)={ord_d}, splits into {num_factors} factors of degree {ord_d}")

    # Key: a min-weight codeword f(x) of degree k-1 has k-1 roots among L
    # f(x) = Prod_{i in Z} (x - omega^i), |Z| = k-1
    #
    # This is related to: f(x) | x^n - 1  (since all roots are n-th roots of unity)
    # So f is a DIVISOR of x^n - 1 of degree k-1
    #
    # The number of divisors of x^n - 1 of degree k-1 over F_p
    # = number of ways to choose factors from the irreducible factorization
    #   that sum to degree k-1

    # Let's compute this directly
    # First, find irreducible factors of x^n - 1 over F_p
    # We'll do this by finding minimal polynomials of each omega^i

    factors = []
    used = set()

    for i in range(n):
        if i in used:
            continue
        # Find minimal polynomial of omega^i over F_p
        # Conjugates: omega^{i*p^j} for j = 0, 1, ...
        conjugate_indices = set()
        idx = i
        while idx not in conjugate_indices:
            conjugate_indices.add(idx)
            idx = (idx * p) % n

        # Mark all conjugates as used
        used.update(conjugate_indices)

        # Build minimal polynomial
        roots = [pow(omega, j, p) for j in conjugate_indices]
        min_poly = poly_from_roots(roots, p)
        factors.append((sorted(conjugate_indices), len(conjugate_indices)))

    print(f"\n  Irreducible factors of x^{n}-1 over F_{p}:")
    for indices, deg in sorted(factors, key=lambda x: x[1]):
        print(f"    degree {deg}: roots at indices {indices}")

    # Count divisors of degree k-1
    factor_degrees = [deg for _, deg in factors]

    def count_subsets_with_sum(degrees, target):
        """Count subsets of degrees that sum to target."""
        # DP
        dp = [0] * (target + 1)
        dp[0] = 1
        for d in degrees:
            if d > target:
                continue
            for s in range(target, d - 1, -1):
                dp[s] += dp[s - d]
        return dp[target]

    num_divisors = count_subsets_with_sum(factor_degrees, k - 1)
    print(f"\n  Divisors of x^{n}-1 of degree {k-1}: {num_divisors}")
    print(f"  C({n},{k-1}) = {len(list(itertools.combinations(range(n), k-1)))}")
    print(f"  Ratio: {num_divisors / len(list(itertools.combinations(range(n), k-1))):.6f}")

    # The difference: not every (k-1)-subset of L roots corresponds to a
    # DIVISOR of x^n-1 that respects the cyclotomic factorization.
    # But every (k-1)-subset DOES give a valid polynomial.
    # The question is: which subsets correspond to "structured" polynomials
    # (products of cyclotomic factors)?

    return factors, factor_degrees

# ============================================================
# Experiment E: Pairwise d_min ↔ polynomial divisibility
# ============================================================
def exp_E_divisibility(n, p):
    """For max-M list: check if f_i - f_j divides x^n - 1 (or has cyclotomic structure)."""
    print(f"\n{'='*60}")
    print(f"Exp E: Divisibility structure in max-M list")
    print(f"{'='*60}")

    result = exp_B_max_M_list(n, p)
    if result is None:
        return

    best_list, diff_zero_sets, L, k, d_min, w, p = result

    # For each difference polynomial, check if it divides x^n - 1
    # f_i - f_j has zero set Z_{ij} subset L with |Z_{ij}| = k-1
    # It divides x^n - 1 iff Z_{ij} is a union of cyclotomic cosets

    g = find_primitive_root(p)
    omega = find_omega(g, p, n)

    # Find cyclotomic cosets
    used = set()
    cosets = []
    for i in range(n):
        if i in used:
            continue
        coset = set()
        idx = i
        while idx not in coset:
            coset.add(idx)
            idx = (idx * p) % n
        used.update(coset)
        cosets.append(frozenset(coset))

    print(f"\n  Cyclotomic cosets mod {n} (p={p}):")
    for c in cosets:
        print(f"    {sorted(c)}")

    print(f"\n  Checking if zero sets of differences are unions of cyclotomic cosets:")
    for i, j, zeros, nonzeros, coeffs in diff_zero_sets[:10]:
        zero_set = set(zeros)
        # Check if zero_set is a union of cyclotomic cosets
        is_union = all(
            c.issubset(zero_set) or c.isdisjoint(zero_set)
            for c in cosets
        )
        parts = [sorted(c) for c in cosets if c.issubset(zero_set)]
        print(f"    f_{i}-f_{j}: Z={sorted(zeros)}, union_of_cosets={is_union}")
        if is_union:
            print(f"      Parts: {parts}")

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("Direction A: Polynomial Factorization Exploration")
    print("=" * 60)

    # Start with small cases
    test_cases = [
        (6, 7),    # n=6, p=7, k=3, d_min=4, w=2
        (8, 17),   # n=8, p=17, k=4, d_min=5, w=3
        (10, 11),  # n=10, p=11, k=5, d_min=6, w=3
    ]

    for n, p in test_cases:
        print(f"\n\n{'#'*60}")
        print(f"# n={n}, p={p}")
        print(f"{'#'*60}")

        # Exp A: verify all (k-1)-subsets give min-weight codewords
        exp_A_minweight_codewords(n, p)

        # Exp B: find max-M list
        exp_B_max_M_list(n, p)

        # Exp C: transitivity constraint
        exp_C_transitivity(n, p)

        # Exp D: cyclotomic factorization
        exp_D_cyclotomic(n, p)

    # Exp E: divisibility structure for best case
    print(f"\n\n{'#'*60}")
    print(f"# Detailed divisibility analysis")
    print(f"{'#'*60}")
    for n, p in [(8, 17), (10, 11)]:
        exp_E_divisibility(n, p)
