#!/usr/bin/env python3
"""
KEY RESULT: Compatibility conditions for RS list-decoding are LINEAR in σ_i.

For RS[n,k] on L = <ω>, center c, error set B with P_B(x) = ∏_{i∈B}(x - ω^i):
  Compatibility ⟺ [P_B · c]_m = 0  for m = k+w, ..., n-1

This is a system of (n-k-w) = conds/B LINEAR equations in (σ_1,...,σ_w).

We verify this against the rank method from det_condition.py, then analyze
the σ-distribution and M for each test case + extend to n=14,16.
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


def poly_mul(a, b, p):
    if not a or not b:
        return []
    result = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            result[i + j] = (result[i + j] + ai * bj) % p
    return result


def poly_from_roots(roots, p):
    result = [1]
    for r in roots:
        new = [0] * (len(result) + 1)
        for i, c in enumerate(result):
            new[i] = (new[i] - r * c) % p
            new[i + 1] = (new[i + 1] + c) % p
        result = new
    return result


def lagrange_interp(values, points, p):
    n = len(values)
    result = [0] * n
    for i in range(n):
        denom = 1
        for j in range(n):
            if j != i:
                denom = denom * (points[i] - points[j]) % p
        denom_inv = pow(denom, p - 2, p)
        coeff = values[i] * denom_inv % p
        basis = [1]
        for j in range(n):
            if j != i:
                new = [0] * (len(basis) + 1)
                for k2, c in enumerate(basis):
                    new[k2] = (new[k2] - points[j] * c) % p
                    new[k2 + 1] = (new[k2 + 1] + c) % p
                basis = new
        for j in range(len(basis)):
            if j < n:
                result[j] = (result[j] + coeff * basis[j]) % p
    return result


def elem_sym(roots, p):
    w = len(roots)
    e = [0] * (w + 1)
    e[0] = 1
    for r in roots:
        for j in range(w, 0, -1):
            e[j] = (e[j] + e[j - 1] * r) % p
    return e


def rank_mod_p(mat, p):
    if not mat or not mat[0]:
        return 0
    m = len(mat)
    nn = len(mat[0])
    M2 = [row[:] for row in mat]
    rank = 0
    for col in range(nn):
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
                for j in range(nn):
                    M2[row][j] = (M2[row][j] - f * M2[rank][j]) % p
        rank += 1
    return rank


def analyze_case(n, k, p, w, center_vals):
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    c_poly = lagrange_interp(center_vals, L, p)
    while len(c_poly) < n:
        c_poly.append(0)

    conds = n - w - k

    print(f"\n{'=' * 70}")
    print(f"RS[{n},{k}] over F_{p}, w={w}, conds/B={conds}")
    print(f"Center poly c(x) = {c_poly}")

    # Two methods to find compatible B's
    compat_rank = set()
    compat_prod = set()

    all_B = list(combinations(range(n), w))

    for B in all_B:
        error_pts = [L[i] for i in B]
        P_B = poly_from_roots(error_pts, p)

        # Method 1: [P_B · c]_m = 0 for m = k+w,...,n-1
        prod = poly_mul(P_B, c_poly, p)
        ok1 = all((prod[m] if m < len(prod) else 0) % p == 0
                   for m in range(k + w, n))
        if ok1:
            compat_prod.add(B)

        # Method 2: rank condition
        S = [i for i in range(n) if i not in B]
        P_S = poly_from_roots([L[i] for i in S], p)
        A = []
        rhs = []
        for eq in range(n - k):
            j = k + eq
            row = []
            for l in range(w):
                idx = j - l
                row.append(P_S[idx] % p if 0 <= idx < len(P_S) else 0)
            A.append(row)
            rhs.append(c_poly[j] if j < len(c_poly) else 0)
        rA = rank_mod_p(A, p)
        aug = [A[i][:] + [rhs[i]] for i in range(n - k)]
        raug = rank_mod_p(aug, p)
        if raug == rA:
            compat_rank.add(B)

    assert compat_rank == compat_prod, "METHODS DISAGREE"
    M = len(compat_prod)
    print(f"M = {M} (both methods agree ✓)")

    # Build the LINEAR system in σ = (σ_1,...,σ_w)
    # Condition at position m: Σ_{j=0}^{w} P_B[j] · c[m-j] = 0
    # P_B[j] = (-1)^{w-j} σ_{w-j},  σ_0 = 1
    # So: Σ_{j=0}^{w} (-1)^{w-j} σ_{w-j} c_{m-j} = 0
    # Rearranging with σ_0=1 term to RHS:
    A_lin = []
    b_lin = []
    for m in range(k + w, n):
        row = [0] * w
        rhs_val = 0
        for j in range(w + 1):
            c_idx = m - j
            c_val = c_poly[c_idx] % p if 0 <= c_idx < len(c_poly) else 0
            sign = pow(-1, w - j, p)
            s_idx = w - j  # this is σ_{w-j}
            coeff = sign * c_val % p
            if s_idx == 0:
                rhs_val = (-coeff) % p
            else:
                row[s_idx - 1] = coeff  # row[i] = coeff of σ_{i+1}
        A_lin.append(row)
        b_lin.append(rhs_val)

    print(f"\nLinear system (rows ↔ conditions m={k+w}..{n-1}):")
    for r, (row, rhs) in enumerate(zip(A_lin, b_lin)):
        lhs_str = " + ".join(f"{row[j]}·σ_{j+1}" for j in range(w) if row[j] != 0)
        print(f"  [{k+w+r}] {lhs_str} = {rhs}")

    # Verify each compatible B satisfies the linear system
    print(f"\nCompatible B's and their σ:")
    for B in sorted(compat_prod):
        sigma = elem_sym([L[i] for i in B], p)
        sv = [sigma[j] % p for j in range(1, w + 1)]
        # Check linear system
        for row, rhs in zip(A_lin, b_lin):
            val = sum(row[j] * sv[j] for j in range(w)) % p
            assert val == rhs % p, f"FAIL at B={B}"
        print(f"  B={B}  σ=({', '.join(str(s) for s in sv)})")

    # σ-distribution: how many distinct σ values, and their multiplicities
    sigma_map = {}
    for B in all_B:
        sigma = elem_sym([L[i] for i in B], p)
        sv = tuple(sigma[j] % p for j in range(1, w + 1))
        sigma_map.setdefault(sv, []).append(B)

    n_distinct = len(sigma_map)
    n_total = len(all_B)
    print(f"\nσ-map: {n_distinct} distinct σ-values / {n_total} total B's")

    # How many σ values lie on the solution subspace?
    on_subspace = {}
    for sv, Bs in sigma_map.items():
        ok = True
        for row, rhs in zip(A_lin, b_lin):
            val = sum(row[j] * sv[j] for j in range(w)) % p
            if val % p != rhs % p:
                ok = False
                break
        if ok:
            on_subspace[sv] = Bs

    print(f"σ values on solution subspace: {len(on_subspace)}")
    for sv, Bs in on_subspace.items():
        print(f"  σ={sv}: {len(Bs)} B's → {Bs}")

    # Solution subspace dimension
    r = rank_mod_p(A_lin, p)
    print(f"\nLinear system rank: {r} / {conds} conditions in {w} unknowns")
    print(f"Solution subspace dim: {w - r}")
    print(f"Expected M from subspace: need to count σ-image points on {w-r}-dim affine subspace")

    return M


# ===== Known test cases =====
print("=" * 70)
print("VERIFYING: COMPATIBILITY CONDITIONS ARE LINEAR IN σ")
print("=" * 70)

analyze_case(6, 3, 7, 2, [5, 1, 0, 0, 0, 0])
analyze_case(8, 4, 17, 3, [7, 1, 3, 0, 0, 0, 0, 0])
analyze_case(10, 5, 11, 3, [1, 1, 4, 0, 0, 0, 0, 0, 0, 0])
analyze_case(12, 6, 13, 4, [1, 5, 12, 0, 5, 0, 0, 0, 0, 0, 0, 0])
