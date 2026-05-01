#!/usr/bin/env python3
"""
Algebraic M bound v3: Direct polynomial factorization.

Center c ∈ F_p^n. Polynomial repr: c(x) of degree < n, unique,
with c(ω^i) = c_i.

Codeword f ∈ RS_k: f(x) has degree < k, f(ω^i) = f_i.

Error e = c - f: e(ω^i) = c_i - f_i. wt(e) = w means e vanishes
on S = {i : e_i = 0}, |S| = n-w.

Polynomial factorization: e(x) = Q(x) · P_S(x) where
  P_S(x) = ∏_{i∈S}(x - ω^i), degree n-w
  Q(x) has degree w-1

Condition f = c - e = c - Q·P_S has degree < k:
  [c(x) - Q(x)·P_S(x)]_j = 0 for j = k, ..., n-1
  → [Q·P_S]_j = c_j for j = k, ..., n-1

This is (n-k) equations in w unknowns.
Overdetermined by (n-k-w).

Compatibility: det conditions on P_S's coefficients.
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


def lagrange_poly(values, points, p):
    """Polynomial interpolation: returns coefficients [a_0, ..., a_{n-1}]
    such that a(points[i]) = values[i] for all i."""
    n = len(values)
    assert len(points) == n
    result = [0] * n
    for i in range(n):
        # Lagrange basis: L_i(x) = ∏_{j≠i} (x - points[j]) / (points[i] - points[j])
        denom = 1
        for j in range(n):
            if j != i:
                denom = denom * (points[i] - points[j]) % p
        denom_inv = pow(denom, p - 2, p)

        # Compute basis polynomial coefficients
        basis = [denom_inv * values[i] % p]
        for j in range(n):
            if j != i:
                new_basis = [0] * (len(basis) + 1)
                for k in range(len(basis)):
                    new_basis[k] = (new_basis[k] + (-points[j]) * basis[k]) % p
                    new_basis[k+1] = (new_basis[k+1] + basis[k]) % p
                basis = new_basis

        for j in range(len(basis)):
            if j < n:
                result[j] = (result[j] + basis[j]) % p
    return result


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


def solve_mod_p(A, b, p):
    """Solve A*x = b mod p. Returns (solution, is_compatible)."""
    m = len(A)
    nn = len(A[0])
    aug = [A[i][:] + [b[i]] for i in range(m)]
    r_A = rank_mod_p(A, p)
    r_aug = rank_mod_p(aug, p)
    return r_A, r_aug, r_A == r_aug


def analyze(n, k, p, w):
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"\n{'='*70}")
    print(f"n={n}, k={k}, p={p}, w={w}, conds/B={n-w-k}")

    # Compute polynomial representation of center c via Lagrange interpolation.
    # For each center, c(x) is the unique poly of degree < n with c(ω^i) = c_i.

    # Find worst-case center
    # For each pair of codewords at distance 2w: they can share a ball of radius w.
    # Strategy: enumerate weight-w error vectors and group by syndrome.

    # But we can use a SIMPLER approach: for each B (|B|=w), and each set of
    # nonzero values on B: check if c = f + e where f ∈ RS_k and supp(e) = B.
    #
    # For each B: the codeword f is the Lagrange interpolant through c|_{[n]\B}.
    # If f has degree < k: valid. Otherwise: not a valid error set.
    #
    # But we need c first...

    # Use the approach: enumerate all codewords, compute pairwise distances,
    # find the center via the ball intersection.

    # Actually, simplest approach for the algebraic analysis:
    # Pick a specific worst-case center (e.g., from v3 script).
    # Compute its polynomial, then check the factorization for each B.

    # For generality: use a weight-w error vector as center.
    # The codeword f=0 is at distance w. Other codewords at distance w
    # correspond to other weight-w error vectors with same syndrome.

    # Let me enumerate all weight-w error vectors and group by syndrome.
    # (Correct syndrome using the CORRECT parity check H'[r][i] = ω^{i(r+1)}.)

    # Actually, the syndrome is just a unique label for the coset.
    # Let me use the original (possibly incorrect) H for labeling purposes only —
    # the KEY computation (polynomial factorization) doesn't use H at all.

    # Use any labeling. Let's use: for error vector e, label = (e positions, e values on those positions).
    # Group by: "which other weight-w vectors are in the same coset?"
    # Two error vectors e, e' are in the same coset iff e - e' ∈ RS_k.

    # Check: e - e' ∈ RS_k iff eval(e - e') has degree < k iff
    # the Lagrange interpolant of (e - e') has degree < k.

    # For small cases: enumerate and check.

    # Generate all codewords
    codewords = []
    for idx in range(p**k):
        a = []
        temp = idx
        for _ in range(k):
            a.append(temp % p)
            temp //= p
        f = tuple(sum(a[j] * pow(L[i], j, p) for j in range(k)) % p for i in range(n))
        codewords.append(f)

    if len(codewords) > 5_000_000:
        print("  Too many codewords")
        return

    print(f"  {len(codewords)} codewords")

    # For each center c: M(c) = |{f ∈ RS_k : d(c,f) ≤ w}|
    # Use the approach: for each error vector e with wt = w:
    # c = e (taking f=0 as one list member). Count other f with d(e, f) ≤ w.

    # d(e, f) = |{i : e_i ≠ f_i}|.
    # For wt(e) = w: e_i = 0 on n-w positions and nonzero on w positions.
    # f_i = e_i on agreement positions and f_i ≠ e_i on error positions.

    # Just: for each codeword f, wt(e - f) = distance.

    # Optimization: for each center e (try a few), count M.

    # Let me find a worst-case center by sampling a few error vectors.
    import random
    random.seed(42)

    best_M = 0
    best_e = None

    # Try structured error vectors: first w positions nonzero
    for trial in range(min(200, p**w)):
        if trial < p**w and p**w <= 200:
            # Exhaustive for first w positions
            vals = []
            temp = trial
            for _ in range(w):
                vals.append(temp % p)
                temp //= p
            if 0 in vals:
                continue  # need all nonzero
        else:
            vals = [random.randint(1, p-1) for _ in range(w)]

        e = [0] * n
        for j in range(w):
            e[j] = vals[j]

        M = sum(1 for f in codewords if sum(1 for i in range(n) if (e[i] - f[i]) % p != 0) <= w)
        if M > best_M:
            best_M = M
            best_e = e[:]

    # Also try random positions
    for _ in range(200):
        positions = sorted(random.sample(range(n), w))
        vals = [random.randint(1, p-1) for _ in range(w)]
        e = [0] * n
        for j, pos in enumerate(positions):
            e[pos] = vals[j]
        M = sum(1 for f in codewords if sum(1 for i in range(n) if (e[i] - f[i]) % p != 0) <= w)
        if M > best_M:
            best_M = M
            best_e = e[:]

    print(f"  Best M found: {best_M}")

    if best_M <= 1:
        print("  Trivial M, skip")
        return

    # Now: compute c(x) — the polynomial of center c = best_e
    c_poly = lagrange_poly(best_e, L, p)
    print(f"  Center: c = {best_e}")
    print(f"  c(x) = {c_poly}")
    d_c = max((j for j in range(n) if c_poly[j] != 0), default=0)
    print(f"  deg(c(x)) = {d_c}")

    # Find all codewords at distance exactly w from center
    list_codewords = []
    for f in codewords:
        dist = sum(1 for i in range(n) if (best_e[i] - f[i]) % p != 0)
        if dist == w:
            list_codewords.append(f)

    print(f"  M (at distance exactly {w}) = {len(list_codewords)}")

    # For each list codeword: verify the factorization
    for ci, f in enumerate(list_codewords[:5]):
        # Error e = c - f
        e = [(best_e[i] - f[i]) % p for i in range(n)]
        B = tuple(i for i in range(n) if e[i] != 0)
        S = tuple(i for i in range(n) if e[i] == 0)

        # P_S
        P_S = poly_coeffs([L[i] for i in S], p)
        deg_PS = len(P_S) - 1
        assert deg_PS == n - w

        # e(x) = Q(x) · P_S(x)
        # e(x) polynomial: Lagrange interpolant of e
        e_poly = lagrange_poly(e, L, p)
        d_e = max((j for j in range(n) if e_poly[j] != 0), default=0)

        # Polynomial division: Q = e_poly / P_S
        # Since P_S | e_poly (by construction), this should be exact.
        if d_e < deg_PS:
            print(f"  Codeword {ci}: deg(e) = {d_e} < deg(P_S) = {deg_PS}, skip")
            continue

        # Polynomial division mod p
        Q = [0] * (d_e - deg_PS + 1)
        remainder = e_poly[:d_e+1]  # copy
        for i in range(d_e, deg_PS - 1, -1):
            if remainder[i] % p != 0:
                coeff = remainder[i] * pow(P_S[deg_PS], p - 2, p) % p
                Q[i - deg_PS] = coeff
                for j in range(deg_PS + 1):
                    remainder[i - deg_PS + j] = (remainder[i - deg_PS + j] - coeff * P_S[j]) % p

        # Check remainder is zero
        rem_ok = all(r % p == 0 for r in remainder)

        deg_Q = max((j for j in range(len(Q)) if Q[j] != 0), default=-1)

        print(f"  Codeword {ci}: B={B}, deg(e)={d_e}, deg(Q)={deg_Q}, exact_div={'✓' if rem_ok else '✗'}")

        # Now check the system: [Q·P_S]_j = c_j for j = k,...,n-1
        # This should be satisfied by construction.
        QP = [0] * (len(Q) + len(P_S) - 1) if Q else [0]
        for a in range(len(Q)):
            for b in range(len(P_S)):
                if a + b < len(QP):
                    QP[a+b] = (QP[a+b] + Q[a] * P_S[b]) % p

        # Check c_j - QP_j = f_j for j = 0,...,k-1 and = 0 for j = k,...,n-1
        f_poly = lagrange_poly(list(f), L, p)
        for j in range(n):
            lhs = (c_poly[j] - (QP[j] if j < len(QP) else 0)) % p
            rhs = f_poly[j] if j < len(f_poly) else 0
            if lhs != rhs % p:
                print(f"    MISMATCH at j={j}: c_j - QP_j = {lhs}, f_j = {rhs % p}")

    # === The algebraic compatibility check ===
    # For each error set B (|B|=w): compute P_S, build system, check compatibility.

    # System: [Q·P_S]_j = c_j for j = k, ..., n-1
    # A[j-k][l] = P_S[j-l] for l = 0,...,w-1
    # rhs[j-k] = c_j

    compatible = 0
    compatible_B = []

    for B in combinations(range(n), w):
        S = [i for i in range(n) if i not in B]
        P_S = poly_coeffs([L[i] for i in S], p)

        num_Q = w  # Q has degree w-1, so w coefficients
        num_eq = n - k

        A = [[0] * num_Q for _ in range(num_eq)]
        rhs = [0] * num_eq
        for eq_idx in range(num_eq):
            j = k + eq_idx
            rhs[eq_idx] = c_poly[j] if j < len(c_poly) else 0
            for l in range(num_Q):
                ps_idx = j - l
                if 0 <= ps_idx < len(P_S):
                    A[eq_idx][l] = P_S[ps_idx] % p

        r_A, r_aug, compat = solve_mod_p(A, rhs, p)
        if compat:
            compatible += 1
            compatible_B.append(B)

    print(f"\n  Compatible error sets (algebraic): {compatible}")
    for B in compatible_B:
        print(f"    B = {B}")

    # Cross-check with actual list
    actual_B = set()
    for f in list_codewords:
        e = [(best_e[i] - f[i]) % p for i in range(n)]
        B = tuple(i for i in range(n) if e[i] != 0)
        actual_B.add(B)

    print(f"  Actual error sets from list: {len(actual_B)}")
    for B in sorted(actual_B):
        print(f"    B = {B}")

    match = compatible == len(actual_B) and set(tuple(sorted(B)) for B in compatible_B) == set(tuple(sorted(B)) for B in actual_B)
    print(f"  Match: {'✓' if match else '✗'}")


analyze(6, 3, 7, 2)
analyze(8, 4, 17, 3)
analyze(10, 5, 11, 3)
