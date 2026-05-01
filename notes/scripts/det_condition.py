#!/usr/bin/env python3
"""
Fast determinant condition analysis.
Use known worst-case centers and compute det for all C(n,w) error sets.
"""

from itertools import combinations


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


def lagrange_poly(values, points, p):
    n = len(values)
    result = [0] * n
    for i in range(n):
        denom = 1
        for j in range(n):
            if j != i:
                denom = denom * (points[i] - points[j]) % p
        denom_inv = pow(denom, p - 2, p)
        basis = [denom_inv * values[i] % p]
        for j in range(n):
            if j != i:
                new_basis = [0] * (len(basis) + 1)
                for kk in range(len(basis)):
                    new_basis[kk] = (new_basis[kk] + (-points[j]) * basis[kk]) % p
                    new_basis[kk+1] = (new_basis[kk+1] + basis[kk]) % p
                basis = new_basis
        for j in range(len(basis)):
            if j < n:
                result[j] = (result[j] + basis[j]) % p
    return result


def det_mod_p(mat, p):
    """Determinant mod p via row reduction."""
    n = len(mat)
    M = [row[:] for row in mat]
    det_val = 1
    for col in range(n):
        pivot = -1
        for row in range(col, n):
            if M[row][col] % p != 0:
                pivot = row
                break
        if pivot == -1:
            return 0
        if pivot != col:
            M[col], M[pivot] = M[pivot], M[col]
            det_val = (-det_val) % p
        det_val = det_val * M[col][col] % p
        inv_p = pow(M[col][col], p - 2, p)
        for row in range(col + 1, n):
            if M[row][col] % p != 0:
                factor = M[row][col] * inv_p % p
                for j in range(col, n):
                    M[row][j] = (M[row][j] - factor * M[col][j]) % p
    return det_val % p


def analyze(n, k, p, w, center):
    """Compute det compatibility condition for all C(n,w) error sets."""
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    c_poly = lagrange_poly(center, L, p)
    conds_per_B = n - w - k

    print(f"\n{'='*60}")
    print(f"n={n}, k={k}, p={p}, w={w}, conds/B={conds_per_B}")

    compatible = 0
    compatible_B = []

    for B in combinations(range(n), w):
        S = [i for i in range(n) if i not in B]
        P_S = poly_coeffs([L[i] for i in S], p)

        # Build system A*q = rhs
        # A[eq][l] = P_S[k+eq-l], rhs[eq] = c_poly[k+eq]
        num_eq = n - k
        num_Q = w

        A = [[0] * num_Q for _ in range(num_eq)]
        rhs = [0] * num_eq
        for eq in range(num_eq):
            j = k + eq
            rhs[eq] = c_poly[j] if j < len(c_poly) else 0
            for l in range(num_Q):
                idx = j - l
                if 0 <= idx < len(P_S):
                    A[eq][l] = P_S[idx] % p

        # Check compatibility: rank([A]) = rank([A|rhs])
        # For conds/B = 1: single det condition
        if conds_per_B == 1:
            # [A|rhs] is (w+1) x (w+1)
            mat = [A[i][:] + [rhs[i]] for i in range(num_eq)]
            d = det_mod_p(mat, p)
            if d == 0:
                compatible += 1
                compatible_B.append(B)
        else:
            # General: check via rank
            from copy import deepcopy
            def rank_p(mat, p):
                if not mat or not mat[0]:
                    return 0
                m = len(mat)
                nn2 = len(mat[0])
                M2 = [row[:] for row in mat]
                for i in range(m):
                    for j in range(nn2):
                        M2[i][j] %= p
                rank = 0
                for col in range(nn2):
                    piv = -1
                    for row in range(rank, m):
                        if M2[row][col] % p != 0:
                            piv = row
                            break
                    if piv == -1:
                        continue
                    M2[rank], M2[piv] = M2[piv], M2[rank]
                    inv_p = pow(M2[rank][col], p - 2, p)
                    for row in range(m):
                        if row != rank and M2[row][col] % p != 0:
                            f = M2[row][col] * inv_p % p
                            for j2 in range(nn2):
                                M2[row][j2] = (M2[row][j2] - f * M2[rank][j2]) % p
                    rank += 1
                return rank
            rA = rank_p(A, p)
            aug = [A[i][:] + [rhs[i]] for i in range(num_eq)]
            raug = rank_p(aug, p)
            if raug == rA:
                compatible += 1
                compatible_B.append(B)

    print(f"  Compatible (M_alg): {compatible}")
    for B in compatible_B:
        print(f"    B = {B}")

    # For conds/B=1: analyze the det polynomial's structure
    if conds_per_B == 1:
        # The det is a polynomial in P_S coefficients (and hence in S).
        # Let's see how it varies as we change P over different primes.
        print(f"\n  Checking p-independence of M:")
        for p2 in [p] + [q for q in range(p+1, p+50) if all(q % d != 0 for d in range(2, int(q**0.5)+1)) and (q-1) % n == 0][:2]:
            if p2 == p:
                continue
            omega2 = find_omega(n, p2)
            L2 = [pow(omega2, i, p2) for i in range(n)]
            # Scale center values to F_{p2}
            c2 = [center[i] % p2 for i in range(n)]
            c_poly2 = lagrange_poly(c2, L2, p2)
            count2 = 0
            for B in combinations(range(n), w):
                S = [i for i in range(n) if i not in B]
                P_S = poly_coeffs([L2[i] for i in S], p2)
                mat = [[0] * (w+1) for _ in range(w+1)]
                for eq in range(w+1):
                    j = k + eq
                    for l in range(w):
                        idx = j - l
                        if 0 <= idx < len(P_S):
                            mat[eq][l] = P_S[idx] % p2
                    mat[eq][w] = c_poly2[j] if j < len(c_poly2) else 0
                if det_mod_p(mat, p2) == 0:
                    count2 += 1
            print(f"    p={p2}: M = {count2}")


# Known worst-case centers from v3 script
# n=6: center = [5, 1, 0, 0, 0, 0], M=3
analyze(6, 3, 7, 2, [5, 1, 0, 0, 0, 0])

# n=8: center = [1, 6, 8, 0, 0, 0, 0, 0], M=7
analyze(8, 4, 17, 3, [1, 6, 8, 0, 0, 0, 0, 0])

# n=10: center = [1, 1, 4, 0, 0, 0, 0, 0, 0, 0], M=3
analyze(10, 5, 11, 3, [1, 1, 4, 0, 0, 0, 0, 0, 0, 0])

# n=12: center = [1, 5, 12, 0, 5, 0, 0, 0, 0, 0, 0, 0], M=6
analyze(12, 6, 13, 4, [1, 5, 12, 0, 5, 0, 0, 0, 0, 0, 0, 0])
