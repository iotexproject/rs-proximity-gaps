"""
overdetermined_resultant.py — Compute Res_{s_1}(r_0-1, r_1) to bound affine intersections.

The degree of Res_{s_1}(r_0-1, r_1) in s_2 = number of affine intersections (with multiplicity).
If this degree is O(1), we have M = O(1).

Also: investigate the high tangency at infinity that makes δ_affine << (D+1)^2.
"""

import random
from math import comb

def find_primitive_root(p):
    for g in range(2, p):
        seen = set()
        x = 1
        for _ in range(p-1):
            seen.add(x)
            x = (x * g) % p
        if len(seen) == p-1:
            return g
    return None

# ---- Univariate polynomial in F_p[s_2] ----
# Represented as list: [a_0, a_1, ..., a_d] for a_0 + a_1 s_2 + ... + a_d s_2^d

def upoly_trim(f, p):
    while f and f[-1] % p == 0:
        f.pop()
    return [x % p for x in f]

def upoly_add(f, g, p):
    r = [0] * max(len(f), len(g))
    for i, v in enumerate(f): r[i] = (r[i] + v) % p
    for i, v in enumerate(g): r[i] = (r[i] + v) % p
    return upoly_trim(r, p)

def upoly_sub(f, g, p):
    r = [0] * max(len(f), len(g))
    for i, v in enumerate(f): r[i] = (r[i] + v) % p
    for i, v in enumerate(g): r[i] = (r[i] - v) % p
    return upoly_trim(r, p)

def upoly_mul(f, g, p):
    if not f or not g:
        return []
    r = [0] * (len(f) + len(g) - 1)
    for i, a in enumerate(f):
        for j, b in enumerate(g):
            r[i+j] = (r[i+j] + a * b) % p
    return upoly_trim(r, p)

def upoly_scale(f, c, p):
    return upoly_trim([(x * c) % p for x in f], p)

def upoly_deg(f):
    return len(f) - 1 if f else -1

def upoly_zero():
    return []

def upoly_const(c, p):
    c = c % p
    return [c] if c else []

def upoly_eval(f, x, p):
    r = 0
    for c in reversed(f):
        r = (r * x + c) % p
    return r

# ---- Bivariate polynomial as list of univariate: f(s_1, s_2) = sum_i a_i(s_2) * s_1^i ----
# Represented as list of upoly: [a_0(s_2), a_1(s_2), ..., a_m(s_2)]

def bpoly_from_dict(d, p):
    """Convert dict {(i,j): coeff} to list-of-lists representation."""
    if not d:
        return []
    max_s1 = max(i for i, j in d.keys())
    result = [upoly_zero() for _ in range(max_s1 + 1)]
    for (i, j), c in d.items():
        while len(result[i]) <= j:
            result[i].append(0)
        result[i][j] = c % p
    result = [upoly_trim(r, p) for r in result]
    # Trim trailing zero polys
    while result and not result[-1]:
        result.pop()
    return result

def bpoly_deg_s1(f):
    return len(f) - 1 if f else -1

def bpoly_eval(f, s1, s2, p):
    """Evaluate f(s1, s2) mod p."""
    result = 0
    s1_pow = 1
    for ai in f:
        coeff = upoly_eval(ai, s2, p)
        result = (result + coeff * s1_pow) % p
        s1_pow = (s1_pow * s1) % p
    return result

# ---- Sylvester resultant ----

def resultant_s1(f_bpoly, g_bpoly, p):
    """Compute Res_{s_1}(f, g) as a polynomial in s_2.

    f = sum a_i(s_2) s_1^i,  deg_s1 = m
    g = sum b_j(s_2) s_1^j,  deg_s1 = n

    Sylvester matrix is (m+n) × (m+n) with entries in F_p[s_2].
    Resultant = determinant of Sylvester matrix (a polynomial in s_2).
    """
    m = bpoly_deg_s1(f_bpoly)
    n = bpoly_deg_s1(g_bpoly)

    if m < 0 or n < 0:
        return upoly_zero()

    # Pad f and g
    a = [f_bpoly[i] if i < len(f_bpoly) else upoly_zero() for i in range(m+1)]
    b = [g_bpoly[j] if j < len(g_bpoly) else upoly_zero() for j in range(n+1)]

    # Sylvester matrix: size (m+n) × (m+n)
    # First n rows: shifted copies of (a_m, a_{m-1}, ..., a_0)
    # Next m rows: shifted copies of (b_n, b_{n-1}, ..., b_0)
    size = m + n
    matrix = [[upoly_zero() for _ in range(size)] for _ in range(size)]

    for i in range(n):
        for j in range(m+1):
            matrix[i][i+j] = list(a[m-j])  # Copy

    for i in range(m):
        for j in range(n+1):
            matrix[n+i][i+j] = list(b[n-j])

    # Gaussian elimination to compute determinant
    det = upoly_const(1, p)
    for col in range(size):
        # Find pivot
        pivot_row = -1
        for row in range(col, size):
            if matrix[row][col]:
                pivot_row = row
                break
        if pivot_row < 0:
            return upoly_zero()  # Singular

        if pivot_row != col:
            matrix[col], matrix[pivot_row] = matrix[pivot_row], matrix[col]
            det = upoly_scale(det, p-1, p)  # Multiply by -1

        pivot = matrix[col][col]
        det = upoly_mul(det, pivot, p)

        # Eliminate below
        pivot_inv_exists = len(pivot) == 1  # Only works cleanly for constant pivot
        if pivot_inv_exists:
            inv_val = pow(pivot[0], p-2, p)
            for row in range(col+1, size):
                if matrix[row][col]:
                    factor = upoly_scale(matrix[row][col], inv_val, p)
                    for j in range(col, size):
                        matrix[row][j] = upoly_sub(matrix[row][j],
                                                    upoly_mul(factor, matrix[col][j], p), p)
        else:
            # Need fraction-free elimination
            for row in range(col+1, size):
                if matrix[row][col]:
                    # row = pivot * row - matrix[row][col] * pivot_row
                    factor = matrix[row][col]
                    for j in range(size):
                        matrix[row][j] = upoly_sub(
                            upoly_mul(pivot, matrix[row][j], p),
                            upoly_mul(factor, matrix[col][j], p), p)

    return upoly_trim(det, p)

# ---- Companion matrix with polynomial entries ----

def compute_remainder_bpoly(sigma_bpoly, n, p):
    """Compute x^n mod Λ(x) where σ_j are bivariate polynomials.

    sigma_bpoly[j] = bivariate poly for σ_{j+1}
    Returns list of w bivariate polynomials [r_0, r_1, ..., r_{w-1}].
    """
    w = len(sigma_bpoly)

    # Precompute c_j: x^w ≡ c_0 + c_1 x + ... + c_{w-1} x^{w-1} mod Λ(x)
    # c_j = (-1)^{w-j+1} σ_{w-j}
    c_dict = [None] * w
    for j in range(w):
        sign = pow(-1, w - j + 1, p)
        # σ_{w-j} is sigma_bpoly[w-j-1]
        # Scale by sign
        c_dict[j] = [upoly_scale(coeff, sign, p) for coeff in sigma_bpoly[w-j-1]] if sigma_bpoly[w-j-1] else []

    # Initial state: x^0 = (1, 0, ..., 0) as bivariate polynomials
    state = [[] for _ in range(w)]
    state[0] = [upoly_const(1, p)]  # Constant 1

    for step in range(n):
        top = state[w-1]  # bivariate poly for x^{w-1} coefficient
        new_state = [None] * w
        new_state[0] = bpoly_mul_bpoly(top, c_dict[0], p)
        for j in range(1, w):
            prod = bpoly_mul_bpoly(top, c_dict[j], p)
            new_state[j] = bpoly_add_bpoly(state[j-1], prod, p)
        state = new_state

    return state

def bpoly_mul_bpoly(f, g, p):
    """Multiply two bivariate polynomials (list-of-upoly representation)."""
    if not f or not g:
        return []
    m = len(f)
    n = len(g)
    result = [upoly_zero() for _ in range(m + n - 1)]
    for i in range(m):
        for j in range(n):
            prod = upoly_mul(f[i], g[j], p)
            result[i+j] = upoly_add(result[i+j], prod, p)
    # Trim
    while result and not result[-1]:
        result.pop()
    return result

def bpoly_add_bpoly(f, g, p):
    """Add two bivariate polynomials."""
    r = [upoly_zero() for _ in range(max(len(f), len(g)))]
    for i in range(len(f)):
        r[i] = upoly_add(r[i], f[i], p)
    for i in range(len(g)):
        r[i] = upoly_add(r[i], g[i], p)
    while r and not r[-1]:
        r.pop()
    return r

def bpoly_sub_const(f, c, p):
    """Subtract constant from bivariate poly."""
    result = [list(coeff) for coeff in f] if f else []
    if not result:
        result = [[(-c) % p]]
    else:
        result[0] = upoly_sub(result[0], upoly_const(c, p), p)
    while result and not result[-1]:
        result.pop()
    return result

def analyze_resultant(n, p, w, c, num_trials=5):
    """Compute resultant and analyze degree."""
    d = w - c
    k = n - w - c
    D = n - w

    if k < 1 or d != 2:
        return

    print(f"\n{'='*70}")
    print(f"n={n}, p={p}, w={w}, c={c}, d={d}, D={D}")
    print(f"  Bézout: (D+1)^2 = {(D+1)**2}")

    random.seed(42)

    for trial in range(num_trials):
        # Random flat
        normals = [tuple(random.randint(0, p-1) for _ in range(w)) for _ in range(c)]
        offsets = [random.randint(0, p-1) for _ in range(c)]

        mat = [[normals[j][i] for i in range(w)] + [offsets[j]] for j in range(c)]
        pivots = []
        for col in range(w):
            if len(pivots) >= c:
                break
            row = len(pivots)
            found = False
            for r in range(row, c):
                if mat[r][col] % p != 0:
                    mat[row], mat[r] = mat[r], mat[row]
                    found = True
                    break
            if not found:
                continue
            inv = pow(mat[row][col], p-2, p)
            for j in range(w+1):
                mat[row][j] = (mat[row][j] * inv) % p
            for r in range(c):
                if r != row and mat[r][col] % p != 0:
                    fac = mat[r][col]
                    for j in range(w+1):
                        mat[r][j] = (mat[r][j] - fac * mat[row][j]) % p
            pivots.append(col)

        if len(pivots) < c:
            continue

        free_vars = [j for j in range(w) if j not in pivots]
        if len(free_vars) != d:
            continue

        a_vals = [0]*w
        b_vals = [[0]*d for _ in range(w)]
        for idx, piv in enumerate(pivots):
            a_vals[piv] = mat[idx][w]
            for fi, fv in enumerate(free_vars):
                b_vals[piv][fi] = (-mat[idx][fv]) % p
        for fi, fv in enumerate(free_vars):
            a_vals[fv] = 0
            b_vals[fv][fi] = 1

        # Build σ_j as bivariate polys: σ_j = a_j + s_1 * b_{j,0} + s_2 * b_{j,1}
        # In list-of-upoly: [a_0(s_2), a_1(s_2)] where a_0(s_2) = a_j + b_{j,1}*s_2
        # and a_1(s_2) = b_{j,0}
        sigma_bpoly = []
        for j in range(w):
            # σ_j = a_j + b_{j,1}*s_2 + s_1 * b_{j,0}
            const_part = [a_vals[j] % p]
            if b_vals[j][1] % p != 0:
                const_part.append(b_vals[j][1] % p)
            const_part = upoly_trim(const_part, p)

            s1_coeff = upoly_const(b_vals[j][0], p)

            poly = [const_part]
            if s1_coeff:
                poly.append(s1_coeff)
            while poly and not poly[-1]:
                poly.pop()
            sigma_bpoly.append(poly)

        print(f"\n  Trial {trial}: computing remainders...")

        # Compute remainders as bivariate polynomials
        remainders = compute_remainder_bpoly(sigma_bpoly, n, p)

        for j in range(min(w, 3)):
            deg_s1 = bpoly_deg_s1(remainders[j])
            max_deg_s2 = max((upoly_deg(c) for c in remainders[j] if c), default=-1)
            total_terms = sum(len(c) for c in remainders[j])
            print(f"    r_{j}: deg_s1={deg_s1}, max_deg_s2={max_deg_s2}, #terms={total_terms}")

        # r_0 - 1
        r0m1 = bpoly_sub_const(remainders[0], 1, p)
        r1 = remainders[1]

        deg_s1_r0m1 = bpoly_deg_s1(r0m1)
        deg_s1_r1 = bpoly_deg_s1(r1)

        print(f"    deg_s1(r_0-1) = {deg_s1_r0m1}, deg_s1(r_1) = {deg_s1_r1}")

        # Verify by brute-force
        M = 0
        V_01_count = 0
        for s1 in range(p):
            for s2 in range(p):
                v0 = bpoly_eval(remainders[0], s1, s2, p)
                v1 = bpoly_eval(remainders[1], s1, s2, p)
                if v0 == 1 and v1 == 0:
                    V_01_count += 1
                all_ok = (v0 == 1)
                for j in range(1, w):
                    if bpoly_eval(remainders[j], s1, s2, p) != 0:
                        all_ok = False
                        break
                if all_ok:
                    M += 1

        print(f"    M = {M}, |V_01| = {V_01_count}")

        # Compute resultant Res_{s_1}(r_0-1, r_1)
        print(f"    Computing Res_{{s1}}(r_0-1, r_1)...")
        try:
            res = resultant_s1(r0m1, r1, p)
            deg_res = upoly_deg(res)
            print(f"    deg(Res) = {deg_res}")

            # Verify: zeros of Res should include s_2-coordinates of V_01
            if res:
                res_zeros = sum(1 for s2 in range(p) if upoly_eval(res, s2, p) == 0)
                print(f"    #zeros of Res = {res_zeros} (should ≥ |V_01| = {V_01_count})")
            else:
                print(f"    Res = 0 (!!! r_0-1 and r_1 share common factor)")
        except Exception as e:
            print(f"    Resultant computation failed: {e}")

# Small cases
for n, p, w in [(10, 11, 4), (10, 13, 4)]:
    c = w - 2
    if n - w - c >= 1:
        analyze_resultant(n, p, w, c, num_trials=5)
