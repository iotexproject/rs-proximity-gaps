#!/usr/bin/env python3
"""
Algebraic approach to bounding M.

For center v = eval(g) (degree d_g, coefficients g_0,...,g_{n-1} with g_j=0 for j<k)
and codeword f = eval(h) (degree < k):

d(v,f) = w iff g-h has exactly n-w roots on L = {1, ω, ..., ω^{n-1}}.

So g-h = Q · P_S where:
  P_S = ∏_{i∈S}(x - ω^i)   (degree n-w, the "agreement polynomial")
  Q is quotient of degree (d_g) - (n-w)

Since we work modulo x^n - 1 on L: P_S divides x^n - 1.
And x^n - 1 = P_S · P_B where P_B = ∏_{i∈B}(x - ω^i) (degree w).

The condition deg(h) < k means: the coefficients of g - Q·P_S at degrees k,...,n-1
must be zero. This is a LINEAR SYSTEM in Q's coefficients.

Number of unknowns: deg(Q) + 1 = d_g - (n-w) + 1.
For d_g = n-1, n-w = k+1: deg(Q) = n-1-(k+1) = w-2. So w-1 unknowns.

Number of equations: n-k (the syndrome dimension).

For rate 1/2 at Johnson (w ≈ 0.293n, k = n/2):
  unknowns = w-1 ≈ 0.293n - 1
  equations = n/2

Since equations > unknowns: OVERDETERMINED. Generic: 0 solutions.
For a solution to exist: equations must be compatible.
This gives (n/2) - (w-1) ≈ 0.207n compatibility conditions on P_S (i.e., on S).

Each compatibility condition is a polynomial in the coefficients of P_S.
The number of S satisfying all conditions is bounded by Bézout's theorem.

This script computes the compatibility conditions and their degrees.
"""

from itertools import combinations
from collections import defaultdict


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


def poly_mult_mod_p(a, b, p):
    """Multiply two polynomials (lists of coefficients, low-degree first) mod p."""
    if not a or not b:
        return []
    result = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            result[i + j] = (result[i + j] + ai * bj) % p
    return result


def poly_coeffs(roots, p):
    """Compute polynomial (x-r1)(x-r2)...(x-rk) mod p."""
    result = [1]
    for r in roots:
        result = poly_mult_mod_p(result, [(-r) % p, 1], p)
    return result


def dft(v, omega, n, p):
    """DFT: g_j = (1/n) sum_i v_i * omega^{-ij}."""
    omega_inv = pow(omega, p - 2, p)
    n_inv = pow(n, p - 2, p)
    g = [0] * n
    for j in range(n):
        s = 0
        for i in range(n):
            s = (s + v[i] * pow(omega_inv, i * j, p)) % p
        g[j] = s * n_inv % p
    return g


def idft(g, omega, n, p):
    """Inverse DFT: v_i = sum_j g_j * omega^{ij}."""
    v = [0] * n
    for i in range(n):
        s = 0
        for j in range(n):
            s = (s + g[j] * pow(omega, i * j, p)) % p
        v[i] = s % p
    return v


def rank_mod_p(mat, p):
    if not mat or not mat[0]:
        return 0
    m = len(mat)
    nn = len(mat[0])
    M_mat = [row[:] for row in mat]
    for i in range(m):
        for j in range(nn):
            M_mat[i][j] %= p
    rank = 0
    for col in range(nn):
        pivot = -1
        for row in range(rank, m):
            if M_mat[row][col] % p != 0:
                pivot = row
                break
        if pivot == -1:
            continue
        M_mat[rank], M_mat[pivot] = M_mat[pivot], M_mat[rank]
        inv_pivot = pow(M_mat[rank][col], p - 2, p)
        for row in range(m):
            if row != rank and M_mat[row][col] % p != 0:
                factor = M_mat[row][col] * inv_pivot % p
                for j in range(nn):
                    M_mat[row][j] = (M_mat[row][j] - factor * M_mat[rank][j]) % p
        rank += 1
    return rank


def analyze_algebraic(n, k, p, w):
    """
    For each agreement set S (|S| = n-w):
    1. Compute P_S = ∏_{i∈S}(x - ω^i)
    2. Build the linear system for Q: coefficients of Q*P_S at degrees k,...,n-1 = g_{k,...,n-1}
    3. Check compatibility (rank of augmented vs coefficient matrix)
    """
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"\n{'='*70}")
    print(f"n={n}, k={k}, p={p}, w={w}")
    print(f"ω = {omega}")

    # We need a specific canonical center g.
    # Use the worst-case syndrome from v3.
    # For each syndrome s, the canonical g has g_j = 0 for j < k and
    # g_{n-k-r} = s[r] / n for r = 0,...,n-k-1.

    # First find worst-case syndrome
    H = [[pow(L[i], k + r, p) for i in range(n)] for r in range(n - k)]
    syndrome_count = defaultdict(int)

    for wt in range(1, w + 1):
        for positions in combinations(range(n), wt):
            def enum_nonzero(wt, p):
                if wt == 0:
                    yield ()
                    return
                for v in range(1, p):
                    for rest in enum_nonzero(wt - 1, p):
                        yield (v,) + rest
            for vals in enum_nonzero(wt, p):
                s = [0] * (n - k)
                for j, pos in enumerate(positions):
                    for r in range(n - k):
                        s[r] = (s[r] + vals[j] * H[r][pos]) % p
                syndrome_count[tuple(s)] += 1

    max_M = max(syndrome_count.values())
    best_s = [s for s, m in syndrome_count.items() if m == max_M][0]

    # Canonical representative: v = idft(g) where g_j = 0 for j < k
    # Find g from s: s[r] = n * g_{n-k-r}
    n_inv = pow(n, p - 2, p)
    g = [0] * n
    for r in range(n - k):
        g[n - k - r] = best_s[r] * n_inv % p

    v = idft(g, omega, n, p)
    print(f"  Max M = {max_M}")
    print(f"  Syndrome: {best_s}")
    print(f"  g = {g}")
    print(f"  v = {v}")

    # Now: for each agreement set S (|S| = n-w, so B = [n]\S has |B| = w):
    # Check the algebraic condition.

    # g - h = Q * P_S, where deg(h) < k.
    # deg(g) = max{j: g_j ≠ 0}. Let d_g = deg(g).
    d_g = max(j for j in range(n) if g[j] != 0)
    print(f"  deg(g) = {d_g}")

    # Q has deg = d_g - (n-w) = d_g - |S|
    deg_Q = d_g - (n - w)
    num_Q_coeffs = deg_Q + 1
    print(f"  deg(Q) = {deg_Q}, #Q coeffs = {num_Q_coeffs}")
    print(f"  #high-degree equations = {n - k}")
    print(f"  Overdetermined by: {(n-k) - num_Q_coeffs}")

    # For each agreement set S: build the system
    compatible_count = 0
    compatible_sets = []

    for S in combinations(range(n), n - w):
        # P_S = ∏_{i∈S}(x - L[S_i])
        P_S = poly_coeffs([L[i] for i in S], p)
        assert len(P_S) == n - w + 1  # degree n-w

        # Linear system: sum_l Q_l * P_S_{j-l} = g_j for j = k, ..., n-1
        # where P_S_m = coefficient of x^m in P_S (0 for m > n-w or m < 0)
        # Q_l for l = 0, ..., deg_Q
        # j ranges from k to n-1: n-k equations

        # A[j-k][l] = P_S_{j-l}
        A = [[0] * num_Q_coeffs for _ in range(n - k)]
        rhs = [0] * (n - k)
        for j in range(k, n):
            rhs[j - k] = g[j]
            for l in range(num_Q_coeffs):
                idx = j - l
                if 0 <= idx < len(P_S):
                    A[j - k][l] = P_S[idx]

        # Check compatibility: rank([A]) vs rank([A | rhs])
        r_A = rank_mod_p(A, p)
        aug = [A[i][:] + [rhs[i]] for i in range(n - k)]
        r_aug = rank_mod_p(aug, p)

        if r_aug == r_A:
            compatible_count += 1
            compatible_sets.append(S)

    B_sets = [tuple(i for i in range(n) if i not in S) for S in compatible_sets]
    print(f"\n  Compatible agreement sets: {compatible_count}")
    print(f"  = M = {compatible_count}")

    # Show the compatible sets
    for i, S in enumerate(compatible_sets[:10]):
        B = tuple(j for j in range(n) if j not in S)
        print(f"    S = {S}, B = {B}")

    # Now analyze the DETERMINANTAL condition.
    # The system A*q = rhs has (n-k) equations and num_Q_coeffs unknowns.
    # Compatibility: det of augmented matrix must be zero (when n-k = num_Q_coeffs + 1).

    # For n=8, k=4, w=3: num_Q_coeffs = w-1 = 2. Equations = 4. Overdetermined by 2.
    # The compatibility requires TWO independent conditions on P_S.

    # Let's examine the rank of A for each S:
    rank_dist = defaultdict(int)
    for S in combinations(range(n), n - w):
        P_S = poly_coeffs([L[i] for i in S], p)
        A = [[0] * num_Q_coeffs for _ in range(n - k)]
        for j in range(k, n):
            for l in range(num_Q_coeffs):
                idx = j - l
                if 0 <= idx < len(P_S):
                    A[j - k][l] = P_S[idx]
        r = rank_mod_p(A, p)
        rank_dist[r] += 1

    print(f"\n  Rank distribution of A:")
    for r in sorted(rank_dist.keys()):
        print(f"    rank = {r}: {rank_dist[r]} agreement sets")

    # The EXPECTED rank of A is min(n-k, num_Q_coeffs) = num_Q_coeffs (since n-k > num_Q_coeffs).
    # If rank(A) = num_Q_coeffs for all S: then compatibility requires rhs to lie in
    # a num_Q_coeffs-dimensional subspace of F_p^{n-k}. This gives n-k - num_Q_coeffs conditions.

    # For each condition: it's a polynomial in the coefficients of P_S.
    # P_S's coefficients are elementary symmetric polynomials in {L[i] : i ∈ S}.
    # These are themselves polynomials in ω.

    # The KEY INSIGHT: the conditions are POLYNOMIAL in ω, and since ω is a fixed
    # primitive root of unity, the number of "good" P_S (satisfying all conditions)
    # is bounded by the degree of the polynomial system.

    print(f"\n  Summary:")
    print(f"    Unknowns (Q coeffs): {num_Q_coeffs}")
    print(f"    Equations (high-deg): {n-k}")
    print(f"    Overdetermined by: {(n-k) - num_Q_coeffs}")
    print(f"    Expected #conditions: {(n-k) - num_Q_coeffs}")
    print(f"    Total agreement sets: {len(list(combinations(range(n), n-w)))}")
    print(f"    Compatible: {compatible_count} = M")


# Run
analyze_algebraic(6, 3, 7, 2)
analyze_algebraic(8, 4, 17, 3)
analyze_algebraic(10, 5, 11, 3)
