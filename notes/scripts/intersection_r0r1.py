"""
intersection_r0r1.py — Study V(r₀-1) ∩ V(r₁) in F_p[σ₁, σ_w].

Goal: prove |V(r₀-1) ∩ V(r₁)(F_p)| = O(1).

Strategy:
1. Compute ALL r_i(σ₁, σ_w) over Z (bivariate specialization)
2. Study r₁: Newton polygon, degree, irreducibility
3. Compute resultant Res_{σ_w}(r₀-1, r₁) ∈ F_p[σ₁]
4. Factor the resultant → count degree-1 factors → count F_p-rational intersection points
5. Test across (n, w, p) parameters
"""

from math import gcd

# ---- Big integer bivariate polynomial arithmetic ----
# Dict {(a, b): int_coeff} where monomial is σ₁^a · σ_w^b

def zpoly_zero():
    return {}

def zpoly_const(c):
    if c == 0: return {}
    return {(0,0): c}

def zpoly_var(idx):
    key = [0, 0]; key[idx] = 1
    return {tuple(key): 1}

def zpoly_add(f, g):
    r = dict(f)
    for k, v in g.items():
        r[k] = r.get(k, 0) + v
        if r[k] == 0: del r[k]
    return r

def zpoly_sub(f, g):
    r = dict(f)
    for k, v in g.items():
        r[k] = r.get(k, 0) - v
        if r[k] == 0: del r[k]
    return r

def zpoly_mul(f, g):
    r = {}
    for (a1, b1), c1 in f.items():
        for (a2, b2), c2 in g.items():
            key = (a1+a2, b1+b2)
            r[key] = r.get(key, 0) + c1 * c2
            if r[key] == 0: del r[key]
    return r

def zpoly_scale(f, c):
    if c == 0: return {}
    return {k: v * c for k, v in f.items() if v * c != 0}

def zpoly_mod_p(f, p):
    """Reduce coefficients mod p."""
    r = {}
    for k, v in f.items():
        c = v % p
        if c != 0:
            r[k] = c
    return r

def zpoly_degree(f):
    if not f: return -1
    return max(a + b for a, b in f.keys())

def zpoly_weighted_degree(f, weights=(1, None)):
    """Weighted degree with wt(σ₁)=1, wt(σ_w)=w."""
    if not f: return -1
    w = weights[1]
    return max(a + w*b for (a,b) in f.keys())

# ---- Companion matrix recurrence over Z[σ₁, σ_w] ----

def compute_all_ri_bivariate_Z(n, w):
    """Compute [r₀, r₁, ..., r_{w-1}] over Z in bivariate (σ₁, σ_w).

    Setting σ₂=...=σ_{w-1}=0:
    Λ(x) = x^w - σ₁x^{w-1} + (-1)^w σ_w
    c_0 = (-1)^{w+1} σ_w,  c_{w-1} = σ₁,  c_j = 0 otherwise
    """
    eps = (-1)**(w+1)
    sigma1 = zpoly_var(0)
    sigmaw = zpoly_var(1)

    c_polys = [zpoly_zero() for _ in range(w)]
    c_polys[0] = zpoly_scale(sigmaw, eps)
    c_polys[w-1] = sigma1

    state = [zpoly_zero() for _ in range(w)]
    state[0] = zpoly_const(1)

    for step in range(n):
        top = state[w - 1]
        new_state = [None] * w
        new_state[0] = zpoly_mul(top, c_polys[0])
        for j in range(1, w):
            new_state[j] = zpoly_add(state[j-1], zpoly_mul(top, c_polys[j]))
        state = new_state

    return state  # [r_0, r_1, ..., r_{w-1}]

def print_zpoly(f, name="f"):
    if not f:
        print(f"  {name} = 0")
        return
    items = sorted(f.items(), key=lambda x: (-sum(x[0]), x[0]))
    parts = []
    for (a, b), c in items:
        var_parts = []
        if a > 0: var_parts.append(f"s1^{a}" if a > 1 else "s1")
        if b > 0: var_parts.append(f"sw^{b}" if b > 1 else "sw")
        var_str = "*".join(var_parts) if var_parts else "1"
        if c == 1 and var_parts: parts.append(f"+{var_str}")
        elif c == -1 and var_parts: parts.append(f"-{var_str}")
        elif c > 0: parts.append(f"+{c}*{var_str}")
        else: parts.append(f"{c}*{var_str}")
    s = " ".join(parts)
    if s.startswith("+"): s = s[1:]
    print(f"  {name} = {s}")

# ---- Univariate polynomial in F_p[t] ----

def upoly_add(f, g, p):
    r = dict(f)
    for k, v in g.items():
        r[k] = (r.get(k, 0) + v) % p
        if r[k] == 0: del r[k]
    return r

def upoly_sub(f, g, p):
    r = dict(f)
    for k, v in g.items():
        r[k] = (r.get(k, 0) - v) % p
        if r[k] == 0: del r[k]
    return r

def upoly_mul(f, g, p):
    r = {}
    for i, a in f.items():
        for j, b in g.items():
            k = i + j
            r[k] = (r.get(k, 0) + a * b) % p
            if r[k] == 0: del r[k]
    return r

def upoly_scale(f, c, p):
    c = c % p
    if c == 0: return {}
    return {k: (v * c) % p for k, v in f.items() if (v * c) % p != 0}

def upoly_degree(f):
    if not f: return -1
    return max(f.keys())

def upoly_mod(f, g, p):
    f = dict(f)
    dg = upoly_degree(g)
    if dg < 0: raise ValueError("division by zero")
    lc_inv = pow(g[dg], p - 2, p)
    while True:
        df = upoly_degree(f)
        if df < dg: return f
        shift = df - dg
        coeff = (f[df] * lc_inv) % p
        for i, v in g.items():
            k = i + shift
            f[k] = (f.get(k, 0) - coeff * v) % p
            if f[k] == 0: del f[k]

def upoly_gcd(f, g, p):
    while g:
        f, g = g, upoly_mod(f, g, p)
    return f

def upoly_eval(f, x, p):
    r = 0
    for d, c in f.items():
        r = (r + c * pow(x, d, p)) % p
    return r

def upoly_roots(f, p):
    """Find all roots in F_p (brute force for small p)."""
    return [x for x in range(p) if upoly_eval(f, x, p) == 0]

def upoly_factor_ddf(f, p):
    """Distinct-degree factorization. Returns [(degree, product_of_factors), ...]."""
    if upoly_degree(f) <= 0:
        return []

    # Make monic
    lc = f[upoly_degree(f)]
    lc_inv = pow(lc, p-2, p)
    f = upoly_scale(f, lc_inv, p)

    factors = []
    h = {1: 1}  # x
    f_remaining = dict(f)
    d = 0

    while upoly_degree(f_remaining) > 0:
        d += 1
        if 2*d > upoly_degree(f_remaining):
            factors.append((upoly_degree(f_remaining), dict(f_remaining)))
            f_remaining = {0: 1}
            break

        # h = x^{p^d} mod f_remaining
        # Compute by squaring: h = h^p mod f_remaining
        h_new = {0: 1}
        base = dict(h)
        exp = p
        while exp > 0:
            if exp % 2 == 1:
                h_new = upoly_mod(upoly_mul(h_new, base, p), f_remaining, p)
            base = upoly_mod(upoly_mul(base, base, p), f_remaining, p)
            exp //= 2
        h = h_new

        # g = gcd(h - x, f_remaining)
        h_minus_x = upoly_sub(h, {1: 1}, p)
        g = upoly_gcd(h_minus_x, f_remaining, p)

        if upoly_degree(g) > 0:
            factors.append((d, g))
            # divide out
            while upoly_degree(f_remaining) >= upoly_degree(g):
                rem = upoly_mod(f_remaining, g, p)
                if not rem or upoly_degree(rem) < 0:
                    # divide f_remaining by g
                    f_remaining = upoly_exact_div(f_remaining, g, p)
                    break
                else:
                    break

    return factors

def upoly_exact_div(f, g, p):
    """Exact polynomial division f/g in F_p[x]. Assumes g | f."""
    f = dict(f)
    result = {}
    dg = upoly_degree(g)
    lc_inv = pow(g[dg], p-2, p)

    while True:
        df = upoly_degree(f)
        if df < 0:
            return result
        if df < dg:
            return result  # remainder
        shift = df - dg
        coeff = (f.get(df, 0) * lc_inv) % p
        result[shift] = coeff
        for i, v in g.items():
            k = i + shift
            f[k] = (f.get(k, 0) - coeff * v) % p
            if f[k] == 0: del f[k]

# ---- Resultant via Sylvester matrix ----

def resultant_sigma_w(f_biv, g_biv, p, max_deg_sw=None):
    """Compute Res_{σ_w}(f, g) ∈ F_p[σ₁].

    f, g are bivariate polynomials {(a,b): coeff} in (σ₁, σ_w).
    Treat them as polynomials in σ_w with coefficients in F_p[σ₁].

    Returns univariate polynomial in σ₁ (dict {deg: coeff mod p}).
    """
    # Extract max degree in σ_w
    def max_sw_deg(poly):
        if not poly: return -1
        return max(b for (a, b) in poly.keys())

    df = max_sw_deg(f_biv)
    dg = max_sw_deg(g_biv)
    if df < 0 or dg < 0:
        return {0: 0}

    N = df + dg  # Sylvester matrix size

    # Build coefficient arrays: f_coeffs[j] = polynomial in σ₁ (coeff of σ_w^j)
    def extract_sw_coeffs(poly, max_d):
        coeffs = [{}] * (max_d + 1)
        coeffs = [{} for _ in range(max_d + 1)]
        for (a, b), c in poly.items():
            c_mod = c % p
            if c_mod != 0:
                if a in coeffs[b]:
                    coeffs[b][a] = (coeffs[b][a] + c_mod) % p
                else:
                    coeffs[b][a] = c_mod
        return coeffs

    f_coeffs = extract_sw_coeffs(f_biv, df)
    g_coeffs = extract_sw_coeffs(g_biv, dg)

    # For small cases, compute resultant by evaluation at σ₁ = 0, 1, ..., p-1
    # and interpolate. The resultant has degree ≤ df*deg_s1(g) + dg*deg_s1(f).
    max_s1_deg_f = max((a for (a,b) in f_biv.keys()), default=0)
    max_s1_deg_g = max((a for (a,b) in g_biv.keys()), default=0)
    res_deg_bound = df * max_s1_deg_g + dg * max_s1_deg_f

    if res_deg_bound >= p:
        print(f"    WARNING: resultant degree bound {res_deg_bound} >= p={p}, can't interpolate")
        return None

    # Evaluate resultant at σ₁ = 0, 1, ..., res_deg_bound
    eval_points = list(range(res_deg_bound + 1))
    eval_values = []

    for s1_val in eval_points:
        # Specialize f, g to univariate in σ_w at σ₁ = s1_val
        f_uni = {}
        for (a, b), c in f_biv.items():
            c_mod = (c * pow(s1_val, a, p)) % p
            if c_mod != 0:
                f_uni[b] = (f_uni.get(b, 0) + c_mod) % p
                if f_uni[b] == 0: del f_uni[b]

        g_uni = {}
        for (a, b), c in g_biv.items():
            c_mod = (c * pow(s1_val, a, p)) % p
            if c_mod != 0:
                g_uni[b] = (g_uni.get(b, 0) + c_mod) % p
                if g_uni[b] == 0: del g_uni[b]

        # Compute resultant of two univariates via subresultant / Euclidean
        res_val = univariate_resultant(f_uni, g_uni, p)
        eval_values.append(res_val)

    # Interpolate
    result = lagrange_interpolate(eval_points, eval_values, p)
    return result

def univariate_resultant(f, g, p):
    """Resultant of two univariate polynomials in F_p[x] via determinant."""
    df = upoly_degree(f)
    dg = upoly_degree(g)
    if df < 0 or dg < 0:
        return 0

    N = df + dg
    if N == 0:
        return 1

    # Build Sylvester matrix
    mat = [[0]*N for _ in range(N)]

    # Rows 0..dg-1: shifts of f
    for i in range(dg):
        for j in range(df + 1):
            mat[i][i + df - j] = f.get(j, 0)

    # Rows dg..N-1: shifts of g
    for i in range(df):
        for j in range(dg + 1):
            mat[dg + i][i + dg - j] = g.get(j, 0)

    # Determinant via Gaussian elimination mod p
    return det_mod_p(mat, N, p)

def det_mod_p(mat, n, p):
    """Determinant of n×n matrix mod p."""
    mat = [row[:] for row in mat]  # copy
    det = 1
    for col in range(n):
        # Find pivot
        pivot = -1
        for row in range(col, n):
            if mat[row][col] % p != 0:
                pivot = row
                break
        if pivot == -1:
            return 0

        if pivot != col:
            mat[col], mat[pivot] = mat[pivot], mat[col]
            det = (-det) % p

        inv = pow(mat[col][col], p - 2, p)
        det = (det * mat[col][col]) % p

        for row in range(col + 1, n):
            if mat[row][col] % p != 0:
                factor = (mat[row][col] * inv) % p
                for j in range(col, n):
                    mat[row][j] = (mat[row][j] - factor * mat[col][j]) % p

    return det

def lagrange_interpolate(xs, ys, p):
    """Lagrange interpolation in F_p. Returns dict {deg: coeff}."""
    n = len(xs)
    result = {}
    for i in range(n):
        if ys[i] == 0:
            continue
        # Basis polynomial for point i
        basis = {0: 1}
        for j in range(n):
            if j == i:
                continue
            # multiply by (x - x_j) / (x_i - x_j)
            denom = (xs[i] - xs[j]) % p
            denom_inv = pow(denom, p - 2, p)
            # basis *= (x - x_j) * denom_inv
            new_basis = {}
            for d, c in basis.items():
                # c * denom_inv * x
                new_basis[d+1] = (new_basis.get(d+1, 0) + c * denom_inv) % p
                # c * denom_inv * (-x_j)
                new_basis[d] = (new_basis.get(d, 0) - c * denom_inv * xs[j]) % p
            basis = {k: v % p for k, v in new_basis.items() if v % p != 0}

        # Add ys[i] * basis to result
        for d, c in basis.items():
            result[d] = (result.get(d, 0) + ys[i] * c) % p
            if result[d] == 0: del result[d]

    return result

# ---- Direct intersection count ----

def count_intersection_bruteforce(r_all, p, w):
    """Count |V(r₀-1) ∩ V(r₁)(F_p)| by brute force over F_p²."""
    r0 = r_all[0]
    r1 = r_all[1]

    def eval_biv(f, s1, sw, p):
        r = 0
        for (a, b), c in f.items():
            r = (r + c * pow(s1, a, p) * pow(sw, b, p)) % p
        return r

    points = []
    for s1 in range(p):
        for sw in range(p):
            v0 = eval_biv(r0, s1, sw, p)
            if (v0 - 1) % p != 0:
                continue
            v1 = eval_biv(r1, s1, sw, p)
            if v1 % p != 0:
                continue
            # Check ALL r_i = 0 for i >= 1
            all_zero = True
            for i in range(2, w):
                vi = eval_biv(r_all[i], s1, sw, p)
                if vi % p != 0:
                    all_zero = False
                    break
            points.append((s1, sw, all_zero))
    return points

# ---- Main analysis ----

print("=" * 70)
print("INTERSECTION ANALYSIS: V(r₀-1) ∩ V(r₁) in F_p[σ₁, σ_w]")
print("(bivariate specialization: σ₂ = ... = σ_{w-1} = 0)")
print("=" * 70)

for w in [3, 4, 5]:
    for n in range(w + 2, min(w + 14, 22), 2):
        print(f"\n{'='*60}")
        print(f"n={n}, w={w}, D=n-w+1={n-w+1}")
        print(f"{'='*60}")

        # Compute all r_i over Z
        r_all_Z = compute_all_ri_bivariate_Z(n, w)

        # Print r₀-1 and r₁
        r0m1_Z = zpoly_sub(r_all_Z[0], zpoly_const(1))
        print(f"\nr₀ - 1:")
        print_zpoly(r0m1_Z, "r₀-1")

        print(f"\nr₁:")
        print_zpoly(r_all_Z[1], "r₁")

        # Degree analysis
        print(f"\n  deg(r₀-1) = {zpoly_degree(r0m1_Z)}")
        print(f"  deg(r₁)   = {zpoly_degree(r_all_Z[1])}")
        print(f"  wt-deg(r₀-1) = {zpoly_weighted_degree(r0m1_Z, (1, w))}")
        print(f"  wt-deg(r₁)   = {zpoly_weighted_degree(r_all_Z[1], (1, w))}")

        # Newton polygon of r₁
        if r_all_Z[1]:
            support_r1 = sorted(r_all_Z[1].keys())
            print(f"\n  r₁ support: {support_r1}")
            # Check weighted degrees
            wts = [a + w*b for (a,b) in support_r1]
            print(f"  r₁ weighted degrees: {sorted(set(wts))}")

        # For each prime p > n, count intersection
        primes = [p for p in range(n+1, 80) if all(p % i != 0 for i in range(2, min(p, 8)))]
        primes = primes[:5]  # first 5 primes > n

        for p in primes:
            # Reduce mod p
            r0m1_p = zpoly_mod_p(r0m1_Z, p)
            r1_p = zpoly_mod_p(r_all_Z[1], p)

            # Brute force intersection count
            pts = count_intersection_bruteforce(r_all_Z, p, w)
            V01 = [(s1, sw) for (s1, sw, _) in pts]
            V01_all = [(s1, sw) for (s1, sw, all_z) in pts if all_z]

            print(f"\n  p={p}:")
            print(f"    |V(r₀-1) ∩ V(r₁)| = {len(V01)}")
            print(f"    |V(r₀-1) ∩ V(r₁) ∩ ... ∩ V(r_{w-1})| = {len(V01_all)}")
            if V01:
                print(f"    Points: {V01[:20]}")

            # Compute resultant
            res = resultant_sigma_w(r0m1_Z, r_all_Z[1], p)
            if res is not None:
                res_deg = upoly_degree(res)
                res_roots = upoly_roots(res, p) if res_deg >= 0 and res_deg <= p else []
                print(f"    Res_sw(r₀-1, r₁): degree={res_deg}, #roots={len(res_roots)}")
                if res_roots:
                    print(f"    Resultant roots: {res_roots[:20]}")

                # DDF of resultant
                if res and res_deg > 0:
                    ddf = upoly_factor_ddf(res, p)
                    ddf_summary = [(d, upoly_degree(g)) for d, g in ddf]
                    print(f"    DDF of resultant: {ddf_summary}")
                    # Count degree-1 factors
                    deg1_count = sum(upoly_degree(g) for d, g in ddf if d == 1)
                    print(f"    #degree-1 irred factors in resultant: {deg1_count}")

print("\n" + "="*70)
print("SUMMARY: Checking if |V₀₁(F_p)| = O(1)")
print("="*70)
