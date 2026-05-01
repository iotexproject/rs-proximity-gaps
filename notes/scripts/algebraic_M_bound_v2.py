#!/usr/bin/env python3
"""
Algebraic M bound v2: correct polynomial representation.

The center c is an ARBITRARY vector in F_p^n (not in RS_k^⊥).
Its polynomial g = DFT(c) has degree up to n-1.

For codeword f with polynomial h (degree < k):
g - h has degree n-1 (since deg(g) = n-1 > k-1 = deg(h)).
The agreement set S = {i : c_i = f(ω^i)} = zeros of eval(g-h) on L.
|S| = n - w iff g-h has exactly n-w roots on L.

Factorization: g - h = Q · P_S in F_p[x], where:
  P_S = ∏_{i∈S}(x - ω^i), degree n-w
  Q = (g-h) / P_S, degree = (n-1) - (n-w) = w-1

The condition deg(h) < k means:
  [Q · P_S]_j = g_j for j = k, ..., n-1  (n-k equations)
  [Q · P_S]_j = g_j - h_j for j = 0, ..., k-1  (determines h)

So: n-k equations in w unknowns (q_0, ..., q_{w-1}).
Overdetermined by: (n-k) - w = n - k - w = conds/B.

For a solution to exist: conds/B compatibility conditions on P_S.

This script computes these conditions and bounds M.
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


def poly_coeffs(roots, p):
    result = [1]
    for r in roots:
        new = [0] * (len(result) + 1)
        for i in range(len(result)):
            new[i] = (new[i] + (-r) * result[i]) % p
            new[i+1] = (new[i+1] + result[i]) % p
        result = new
    return result


def dft(v, omega, n, p):
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


def analyze(n, k, p, w):
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"\n{'='*70}")
    print(f"n={n}, k={k}, p={p}, w={w}")

    # Find worst-case error vector
    H = [[pow(L[i], k + r, p) for i in range(n)] for r in range(n - k)]
    syndrome_errors = defaultdict(list)

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
                e = [0] * n
                for j, pos in enumerate(positions):
                    e[pos] = vals[j]
                syndrome_errors[tuple(s)].append(e)

    max_M = max(len(v) for v in syndrome_errors.values())
    best_s = [s for s, v in syndrome_errors.items() if len(v) == max_M][0]

    # Use the FIRST error vector as center
    center_e = syndrome_errors[best_s][0]
    center_g = dft(center_e, omega, n, p)

    print(f"  Max M = {max_M}")
    print(f"  Center (error vector): e = {center_e}")
    print(f"  Center polynomial: g = {center_g}")
    d_g = max((j for j in range(n) if center_g[j] != 0), default=0)
    print(f"  deg(g) = {d_g}")

    # Parameters
    deg_Q = d_g - (n - w)  # w - 1 when d_g = n-1
    num_Q = deg_Q + 1
    num_eq = n - k
    overdetermined = num_eq - num_Q

    print(f"  deg(Q) = {deg_Q}, #Q unknowns = {num_Q}")
    print(f"  #equations = {num_eq}")
    print(f"  Overdetermined by = {overdetermined} = conds/B")

    # For each agreement set S: build system and check compatibility
    compatible = 0
    compatible_sets = []

    for B in combinations(range(n), w):
        S = [i for i in range(n) if i not in B]
        P_S = poly_coeffs([L[i] for i in S], p)

        # System: sum_l q_l * P_S_{j-l} = g_j for j = k, ..., n-1
        # Matrix A: A[j-k][l] = P_S_{j-l} for l = 0,...,deg_Q
        # where P_S has coefficients P_S[0], ..., P_S[n-w]

        if num_Q <= 0:
            # No Q unknowns: check if g_k = ... = g_{n-1} = 0
            ok = all(center_g[j] == 0 for j in range(k, n))
            if ok:
                compatible += 1
                compatible_sets.append(B)
            continue

        A = [[0] * num_Q for _ in range(num_eq)]
        rhs = [0] * num_eq
        for eq_idx in range(num_eq):
            j = k + eq_idx
            rhs[eq_idx] = center_g[j]
            for l in range(num_Q):
                ps_idx = j - l
                if 0 <= ps_idx < len(P_S):
                    A[eq_idx][l] = P_S[ps_idx]

        # Check compatibility
        r_A = rank_mod_p(A, p)
        aug = [A[i][:] + [rhs[i]] for i in range(num_eq)]
        r_aug = rank_mod_p(aug, p)

        if r_aug == r_A:
            compatible += 1
            compatible_sets.append(B)

    print(f"\n  Compatible error sets (M): {compatible}")

    # Show compatible sets
    for i, B in enumerate(compatible_sets[:10]):
        S = [j for j in range(n) if j not in B]
        print(f"    B_{i} = {B}, S = {S}")

    # Rank distribution of A
    rank_dist = defaultdict(int)
    for B in combinations(range(n), w):
        S = [i for i in range(n) if i not in B]
        P_S = poly_coeffs([L[i] for i in S], p)
        if num_Q <= 0:
            rank_dist[0] += 1
            continue
        A = [[0] * num_Q for _ in range(num_eq)]
        for eq_idx in range(num_eq):
            j = k + eq_idx
            for l in range(num_Q):
                ps_idx = j - l
                if 0 <= ps_idx < len(P_S):
                    A[eq_idx][l] = P_S[ps_idx]
        r = rank_mod_p(A, p)
        rank_dist[r] += 1

    print(f"\n  Rank distribution of A:")
    for r in sorted(rank_dist.keys()):
        print(f"    rank(A) = {r}: {rank_dist[r]} error sets")

    # The compatibility condition is: rhs lies in col(A).
    # When rank(A) = num_Q (full column rank):
    #   Compatibility requires overdetermined equations to be consistent.
    #   This gives overdetermined many conditions.
    #
    # The KEY: these conditions are POLYNOMIAL in the coefficients of P_S.
    # P_S coefficients = elementary symmetric polynomials of {L[i] : i ∈ S}.
    # So the conditions are polynomial in the choice of S.
    #
    # The DEGREE of each condition bounds the number of good S.

    # Let me compute the EXPLICIT compatibility condition for small cases.
    if overdetermined == 1 and num_Q > 0:
        print(f"\n  Explicit compatibility condition (overdetermined by 1):")
        print(f"  The condition is: det([A | rhs]) = 0")
        print(f"  where [A | rhs] is (num_Q+1) x (num_Q+1)")
        print(f"  (using the num_Q+1 rows that form a square matrix)")

        # The matrix A has num_eq rows and num_Q columns.
        # Take any (num_Q+1) rows: the condition det([rows | rhs_rows]) = 0.
        # If all such (num_Q+1)-row determinants vanish: compatible.
        # Since rank(A) = num_Q generically: exactly 1 condition.

        # The condition is: a specific polynomial in P_S coefficients = 0.
        # Let me compute this polynomial for the first few cases.
        pass


# Run
analyze(6, 3, 7, 2)
analyze(8, 4, 17, 3)
analyze(10, 5, 11, 3)
analyze(12, 6, 13, 4)
