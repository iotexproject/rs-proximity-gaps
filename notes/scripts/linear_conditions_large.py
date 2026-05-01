#!/usr/bin/env python3
"""
Extend linear-condition analysis to larger n.
Find worst-case M by searching over centers.

Key insight: conditions [P_B·c]_m = 0 are LINEAR in σ_i,
so M = |{w-subsets B : σ(B) on a codim-c affine subspace}|.

Search strategy: random centers in the "high coefficient" space (c_k,...,c_{n-1}).
"""

from itertools import combinations
import random
import math

random.seed(42)


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


def smallest_prime_cong_1(n, start=2):
    """Find smallest prime p ≡ 1 mod n, p >= start."""
    p = start
    while True:
        if p % n == 1:
            is_prime = p > 1
            for d in range(2, int(p**0.5) + 1):
                if p % d == 0:
                    is_prime = False
                    break
            if is_prime:
                return p
        p += 1


def johnson_radius(n, k):
    """w = ceil((1 - sqrt(k/n)) * n)"""
    return math.ceil((1 - math.sqrt(k / n)) * n)


def analyze_large(n, k, p, w):
    """
    Precompute σ-image, then search for worst-case center.
    """
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    conds = n - w - k
    n_B = math.comb(n, w)

    print(f"\n{'=' * 70}")
    print(f"RS[{n},{k}] over F_{p}, w={w}, conds/B={conds}")
    print(f"C({n},{w}) = {n_B} error sets")
    print(f"Average M = C(n,w)/p^c = {n_B}/{p**conds} ≈ {n_B / p**conds:.2f}")

    # Precompute σ for all B's
    all_B = list(combinations(range(n), w))
    all_sigma = []
    for B in all_B:
        roots = [L[i] for i in B]
        sigma = elem_sym(roots, p)
        all_sigma.append(tuple(sigma[j] % p for j in range(1, w + 1)))

    # Check injectivity of σ-map
    n_distinct = len(set(all_sigma))
    print(f"Distinct σ values: {n_distinct} / {n_B} (injective: {n_distinct == n_B})")

    # Build the condition matrix for a generic center.
    # Conditions: Σ_{j=0}^{w} P_B[j] · c[m-j] = 0 for m = k+w,...,n-1
    # P_B[j] = (-1)^{w-j} σ_{w-j}
    #
    # Each condition: Σ_{j=0}^{w} (-1)^{w-j} σ_{w-j} c_{m-j} = 0
    # = σ_0 (-1)^w c_{m-w} + σ_1 (-1)^{w-1} c_{m-w+1} + ... + σ_w c_m = 0
    #
    # The coefficients of σ_1,...,σ_w come from c_k,...,c_{n-1}.
    # The RHS (from σ_0=1) also depends on c.

    # For the search: parameterize by c_high = (c_k,...,c_{n-1}).
    # The condition at m is:
    #   Σ_{i=1}^{w} (-1)^{w-i} c_{m-w+i} σ_i = -(-1)^w c_{m-w}
    # i.e., Σ_i a_{m,i} σ_i = b_m  where a_{m,i} = (-1)^{w-i} c_{m-w+i}

    def compute_M(c_high):
        """Given c_high = (c_k,...,c_{n-1}), count compatible B's."""
        # Build linear conditions
        A = []
        b = []
        for m in range(k + w, n):
            row = [0] * w
            rhs = 0
            for i in range(w + 1):
                c_idx = m - w + i  # = m - w + i
                if k <= c_idx < n:
                    c_val = c_high[c_idx - k]
                else:
                    c_val = 0
                sign = pow(-1, w - i, p)
                if i == 0:
                    rhs = (-sign * c_val) % p
                else:
                    row[i - 1] = (sign * c_val) % p
            A.append(row)
            b.append(rhs)

        # Count σ values satisfying all conditions
        count = 0
        for sv in all_sigma:
            ok = True
            for row, rhs in zip(A, b):
                val = sum(row[j] * sv[j] for j in range(w)) % p
                if val != rhs % p:
                    ok = False
                    break
            if ok:
                count += 1
        return count

    # Search for worst-case center
    best_M = 0
    best_c = None
    n_trials = 0

    # Strategy 1: sparse c_high (few nonzero entries)
    for num_nonzero in range(1, min(conds + 2, n - k) + 1):
        if num_nonzero > 3:
            break
        for positions in combinations(range(n - k), num_nonzero):
            for vals_idx in range(min((p - 1) ** num_nonzero, 2000)):
                vals = []
                temp = vals_idx
                for _ in range(num_nonzero):
                    vals.append(temp % (p - 1) + 1)
                    temp //= (p - 1)
                c_high = [0] * (n - k)
                for j, pos in enumerate(positions):
                    c_high[pos] = vals[j]
                M_val = compute_M(c_high)
                if M_val > best_M:
                    best_M = M_val
                    best_c = c_high[:]
                n_trials += 1
                if n_trials % 5000 == 0:
                    print(f"  ... {n_trials} trials, best M = {best_M}")

    # Strategy 2: random c_high
    for _ in range(min(10000, p ** min(3, n - k))):
        c_high = [random.randint(0, p - 1) for _ in range(n - k)]
        M_val = compute_M(c_high)
        if M_val > best_M:
            best_M = M_val
            best_c = c_high[:]
        n_trials += 1

    print(f"\nBest M = {best_M} (after {n_trials} trials)")
    print(f"Best c_high = {best_c}")

    # Analyze the best case
    if best_M > 0 and best_c is not None:
        A = []
        b = []
        for m in range(k + w, n):
            row = [0] * w
            rhs = 0
            for i in range(w + 1):
                c_idx = m - w + i
                if k <= c_idx < n:
                    c_val = best_c[c_idx - k]
                else:
                    c_val = 0
                sign = pow(-1, w - i, p)
                if i == 0:
                    rhs = (-sign * c_val) % p
                else:
                    row[i - 1] = (sign * c_val) % p
            A.append(row)
            b.append(rhs)

        print(f"\nConditions for best center:")
        for r, (row, rhs) in enumerate(zip(A, b)):
            terms = [f"{row[j]}·σ_{j+1}" for j in range(w) if row[j] != 0]
            print(f"  [{k+w+r}] {' + '.join(terms)} = {rhs}")

        print(f"\nCompatible B's:")
        for idx, (B, sv) in enumerate(zip(all_B, all_sigma)):
            ok = True
            for row, rhs in zip(A, b):
                val = sum(row[j] * sv[j] for j in range(w)) % p
                if val != rhs % p:
                    ok = False
                    break
            if ok:
                print(f"  B={B}  σ=({', '.join(str(s) for s in sv)})")

    # Distribution analysis: σ_w values (product of error positions)
    sigma_w_dist = {}
    for sv in all_sigma:
        sw = sv[w - 1]
        sigma_w_dist[sw] = sigma_w_dist.get(sw, 0) + 1
    print(f"\nσ_w distribution: {sorted(sigma_w_dist.items(), key=lambda x: -x[1])[:10]}")
    max_sw = max(sigma_w_dist.values())
    min_sw = min(sigma_w_dist.values())
    print(f"  max count = {max_sw}, min count = {min_sw}, avg = {n_B/len(sigma_w_dist):.1f}")

    return best_M


# ===== Run for increasing n =====
print("=" * 70)
print("WORST-CASE M SEARCH FOR LARGER n")
print("=" * 70)

# Verified cases
for n, k, p, w in [(6, 3, 7, 2), (8, 4, 17, 3), (10, 5, 11, 3), (12, 6, 13, 4)]:
    analyze_large(n, k, p, w)

# New cases
for n in [14, 16, 18, 20]:
    k = n // 2
    w = johnson_radius(n, k)
    p = smallest_prime_cong_1(n, n + 1)
    print(f"\n>>> n={n}, k={k}, w={w}, p={p}")
    analyze_large(n, k, p, w)
