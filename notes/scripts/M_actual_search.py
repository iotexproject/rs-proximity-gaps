#!/usr/bin/env python3
"""
Correct M computation: count DISTINCT codewords at distance ≤ w from center.
M_algebraic (compatible B's) overcounts when d(c, f) < w.

Key formula: for each compatible B, interpolate c on S = L\B to get f.
M_actual = |{distinct f}|.

Also: classify by distance (how many at d=1, d=2, ..., d=w).
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
    return math.ceil((1 - math.sqrt(k / n)) * n)


def interpolate_on_S(c_vals, S_indices, L, k, p):
    """
    Given center values c_vals and agreement indices S,
    interpolate to find the unique degree-<k polynomial f.
    Returns f as evaluations on all of L, or None if no solution.
    """
    # Build Vandermonde system: V * a = c|_S
    # V[i][j] = L[S[i]]^j, a = (a_0,...,a_{k-1})
    S = list(S_indices)
    m = len(S)
    if m < k:
        return None  # underdetermined

    # Build augmented matrix [V | c_S]
    aug = []
    for i in range(m):
        row = [pow(L[S[i]], j, p) for j in range(k)]
        row.append(c_vals[S[i]])
        aug.append(row)

    # Gaussian elimination
    n_cols = k
    pivot_cols = []
    for col in range(n_cols):
        piv = -1
        for row in range(len(pivot_cols), m):
            if aug[row][col] % p != 0:
                piv = row
                break
        if piv == -1:
            continue
        aug[len(pivot_cols)], aug[piv] = aug[piv], aug[len(pivot_cols)]
        inv_p = pow(aug[len(pivot_cols)][col], p - 2, p)
        for row in range(m):
            if row != len(pivot_cols) and aug[row][col] % p != 0:
                f = aug[row][col] * inv_p % p
                for j in range(n_cols + 1):
                    aug[row][j] = (aug[row][j] - f * aug[len(pivot_cols)][j]) % p
        pivot_cols.append(col)

    if len(pivot_cols) < k:
        return None  # system doesn't have unique solution? (shouldn't happen for |S| >= k)

    # Check consistency of remaining rows
    for row in range(k, m):
        if aug[row][k] % p != 0:
            return None  # incompatible — no degree-<k interpolant exists

    # Extract solution
    a = [0] * k
    for idx, col in enumerate(pivot_cols):
        a[col] = aug[idx][k] * pow(aug[idx][col], p - 2, p) % p

    # Evaluate f on all of L
    n = len(L)
    f_vals = tuple(sum(a[j] * pow(L[i], j, p) for j in range(k)) % p for i in range(n))
    return f_vals


def analyze_case(n, k, p, w, verbose=True):
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    conds = n - w - k
    n_B = math.comb(n, w)

    if verbose:
        print(f"\n{'=' * 70}")
        print(f"RS[{n},{k}] over F_{p}, w={w}, conds/B={conds}")
        print(f"C({n},{w}) = {n_B}, avg M_alg = {n_B / p**conds:.2f}")

    # Precompute σ for all B's
    all_B = list(combinations(range(n), w))
    all_sigma = []
    for B in all_B:
        roots = [L[i] for i in B]
        sigma = elem_sym(roots, p)
        all_sigma.append(tuple(sigma[j] % p for j in range(1, w + 1)))

    def compute_M(c_high):
        """Compute M_actual = distinct codewords at distance ≤ w."""
        # Build center values from c_high
        # c(x) = Σ c_j x^j. c_high gives c_k,...,c_{n-1}.
        # For the compatibility check, we only need c evaluated at L.
        # c(ω^i) = Σ_{j=0}^{n-1} c_j ω^{ij}
        # We set c_0,...,c_{k-1} = 0 (WLOG, shifting by a codeword doesn't change M)
        c_coeffs = [0] * k + list(c_high)
        c_vals = [sum(c_coeffs[j] * pow(L[i], j, p) for j in range(n)) % p for i in range(n)]

        # Find compatible B's via linear conditions
        compatible = []
        for idx, (B, sv) in enumerate(zip(all_B, all_sigma)):
            ok = True
            for m in range(k + w, n):
                val = 0
                for j in range(w + 1):
                    c_idx = m - j
                    c_val = c_coeffs[c_idx] if 0 <= c_idx < n else 0
                    # P_B[j] = (-1)^{w-j} σ_{w-j}
                    if j == w:
                        pb_j = 1
                    elif j == 0:
                        pb_j = sv[w - 1] if (w % 2 == 0) else (p - sv[w - 1]) % p
                        # (-1)^w σ_w
                        pb_j = pow(-1, w, p) * sv[w - 1] % p
                    else:
                        pb_j = pow(-1, w - j, p) * sv[w - j - 1] % p
                    val = (val + pb_j * c_val) % p
                if val != 0:
                    ok = False
                    break
            if ok:
                compatible.append(B)

        if not compatible:
            return 0, 0, {}

        # For each compatible B, compute the interpolant
        codewords = set()
        dist_count = {}
        for B in compatible:
            S = [i for i in range(n) if i not in B]
            f = interpolate_on_S(c_vals, S, L, k, p)
            if f is not None:
                d = sum(1 for i in range(n) if c_vals[i] != f[i])
                codewords.add(f)
                dist_count[d] = dist_count.get(d, 0) + 1

        M_alg = len(compatible)
        M_actual = len(codewords)
        return M_actual, M_alg, dist_count

    # Search for worst-case center
    best_actual = 0
    best_c = None
    best_info = None
    n_trials = 0

    # Strategy 1: sparse c_high
    for num_nonzero in range(1, min(4, n - k) + 1):
        pos_limit = min(n - k, 6)
        for positions in combinations(range(pos_limit), min(num_nonzero, pos_limit)):
            for vals_idx in range(min((p - 1) ** num_nonzero, 3000)):
                vals = []
                temp = vals_idx
                for _ in range(num_nonzero):
                    vals.append(temp % (p - 1) + 1)
                    temp //= (p - 1)
                c_high = [0] * (n - k)
                for j, pos in enumerate(positions):
                    c_high[pos] = vals[j]
                M_act, M_alg, dists = compute_M(c_high)
                if M_act > best_actual:
                    best_actual = M_act
                    best_c = c_high[:]
                    best_info = (M_alg, dists)
                n_trials += 1
                if verbose and n_trials % 5000 == 0:
                    print(f"  ... {n_trials} trials, best M_actual={best_actual}")

    # Strategy 2: random c_high
    for _ in range(min(20000, p ** min(3, n - k))):
        c_high = [random.randint(0, p - 1) for _ in range(n - k)]
        M_act, M_alg, dists = compute_M(c_high)
        if M_act > best_actual:
            best_actual = M_act
            best_c = c_high[:]
            best_info = (M_alg, dists)
        n_trials += 1
        if verbose and n_trials % 5000 == 0:
            print(f"  ... {n_trials} trials, best M_actual={best_actual}")

    if verbose:
        print(f"\nBest M_actual = {best_actual}, M_algebraic = {best_info[0]}")
        print(f"Distance distribution: {best_info[1]}")
        print(f"c_high = {best_c}")
        print(f"({n_trials} trials)")

    return best_actual


# Test cases
print("=" * 70)
print("CORRECT M_actual SEARCH (distinct codewords at distance ≤ w)")
print("=" * 70)

for n, k, p, w in [(6, 3, 7, 2), (8, 4, 17, 3), (10, 5, 11, 3), (12, 6, 13, 4)]:
    analyze_case(n, k, p, w)

# Larger cases
for n in [14, 16]:
    k = n // 2
    w = johnson_radius(n, k)
    p = smallest_prime_cong_1(n, n + 1)
    print(f"\n>>> n={n}, k={k}, w={w}, p={p}")
    analyze_case(n, k, p, w)

# Try multiple primes for same n to check p-independence of M
print(f"\n{'=' * 70}")
print("M vs PRIME (p-independence check)")
print("=" * 70)
for n, k, w in [(8, 4, 3), (10, 5, 3)]:
    for p in [smallest_prime_cong_1(n, q) for q in [n + 1, 2 * n + 1, 5 * n + 1]]:
        print(f"\nn={n}, k={k}, w={w}, p={p}:")
        M = analyze_case(n, k, p, w, verbose=False)
        print(f"  M_actual = {M}")
