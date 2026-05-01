"""
resultant_intermediate.py — Test resultant structure beyond bivariate.

Key question: Does Res_{σ_w}(r₀-1, r₁) = s1^{...} · G(s1^n) hold
when intermediate σ-variables are NOT set to 0?

Test cases for w=4:
(a) σ₂=σ₃=0: bivariate (known, G(s1^n) confirmed)
(b) σ₃=0, σ₂ free: trivariate → Res ∈ F_p[σ₁, σ₂]
(c) σ₃=0, σ₂=c (const): bivariate with shifted σ₂ → Res ∈ F_p[σ₁]
(d) random 2-flat in full σ-space → Res ∈ F_p[s]
"""

import random
from math import gcd

# ---- Multivariate poly in F_p ----
def mpoly_zero(): return {}
def mpoly_const(c, p, w):
    c = c % p
    if c == 0: return {}
    return {(0,)*w: c}
def mpoly_var(idx, w):
    key = tuple(1 if i == idx else 0 for i in range(w))
    return {key: 1}
def mpoly_add(f, g, p):
    r = dict(f)
    for k, v in g.items():
        r[k] = (r.get(k, 0) + v) % p
        if r[k] == 0: del r[k]
    return r
def mpoly_sub(f, g, p):
    r = dict(f)
    for k, v in g.items():
        r[k] = (r.get(k, 0) - v) % p
        if r[k] == 0: del r[k]
    return r
def mpoly_mul(f, g, p):
    r = {}
    for e1, c1 in f.items():
        for e2, c2 in g.items():
            key = tuple(a+b for a, b in zip(e1, e2))
            r[key] = (r.get(key, 0) + c1 * c2) % p
            if r[key] == 0: del r[key]
    return r
def mpoly_scale(f, c, p):
    c = c % p
    if c == 0: return {}
    return {k: (v * c) % p for k, v in f.items() if (v * c) % p != 0}
def mpoly_eval_partial(f, assignments, p):
    """Partially evaluate: assignments = {var_idx: value}.
    Returns polynomial in remaining variables (same tuple format, assigned vars = 0)."""
    r = {}
    for exps, c in f.items():
        val = c
        new_exps = list(exps)
        for idx, v in assignments.items():
            if exps[idx] > 0:
                val = (val * pow(v, exps[idx], p)) % p
            new_exps[idx] = 0
        key = tuple(new_exps)
        if val != 0:
            r[key] = (r.get(key, 0) + val) % p
            if r[key] == 0: del r[key]
    return r

def compute_all_ri_full(n, p, w):
    sigma_polys = [mpoly_var(j, w) for j in range(w)]
    c_polys = [None] * w
    for j in range(w):
        sign = pow(-1, w - j + 1, p)
        c_polys[j] = mpoly_scale(sigma_polys[w - j - 1], sign, p)
    state = [mpoly_const(0, p, w) for _ in range(w)]
    state[0] = mpoly_const(1, p, w)
    for step in range(n):
        top = state[w - 1]
        new_state = [None] * w
        new_state[0] = mpoly_mul(top, c_polys[0], p)
        for j in range(1, w):
            new_state[j] = mpoly_add(state[j-1], mpoly_mul(top, c_polys[j], p), p)
        state = new_state
    return state

# ---- Univariate resultant ----
def upoly_degree(f):
    if not f: return -1
    return max(f.keys())

def upoly_eval(f, x, p):
    r = 0
    for d, c in f.items():
        r = (r + c * pow(x, d, p)) % p
    return r

def upoly_roots(f, p):
    return [x for x in range(p) if upoly_eval(f, x, p) == 0]

def upoly_gcd_poly(f, g, p):
    """GCD of two univariate polys in F_p[x]."""
    while g:
        dg = upoly_degree(g)
        if dg < 0:
            return f
        lc_inv = pow(g[dg], p-2, p)
        f_copy = dict(f)
        while True:
            df = upoly_degree(f_copy)
            if df < dg:
                f, g = g, f_copy
                break
            shift = df - dg
            coeff = (f_copy.get(df, 0) * lc_inv) % p
            for i, v in g.items():
                k = i + shift
                f_copy[k] = (f_copy.get(k, 0) - coeff * v) % p
                if f_copy[k] == 0: del f_copy[k]
    return f

def det_mod_p(mat, n, p):
    mat = [row[:] for row in mat]
    det = 1
    for col in range(n):
        pivot = -1
        for row in range(col, n):
            if mat[row][col] % p != 0:
                pivot = row
                break
        if pivot == -1: return 0
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

def univariate_resultant(f, g, p):
    df = upoly_degree(f)
    dg = upoly_degree(g)
    if df < 0 or dg < 0: return 0
    N = df + dg
    if N == 0: return 1
    mat = [[0]*N for _ in range(N)]
    for i in range(dg):
        for j in range(df + 1):
            mat[i][i + df - j] = f.get(j, 0)
    for i in range(df):
        for j in range(dg + 1):
            mat[dg + i][i + dg - j] = g.get(j, 0)
    return det_mod_p(mat, N, p)

# ---- Extract bivariate → univariate via evaluation ----

def bivariate_to_univariate_at(f_biv, var_idx, val, w, p):
    """From a w-variate polynomial, fix variable var_idx = val, return {remaining_exp: coeff}."""
    result = {}
    for exps, c in f_biv.items():
        v = (c * pow(val, exps[var_idx], p)) % p
        if v == 0: continue
        # Key: the remaining variable's exponent
        new_exps = list(exps)
        new_exps[var_idx] = 0
        key = tuple(new_exps)
        result[key] = (result.get(key, 0) + v) % p
        if result[key] == 0: del result[key]
    return result

def extract_univariate_in_var(f, var_idx, w):
    """From a w-variate poly, extract as univariate in var_idx.
    Returns {degree_in_var: coeff_poly} where coeff_poly has the var zeroed."""
    coeffs = {}
    for exps, c in f.items():
        d = exps[var_idx]
        new_exps = list(exps)
        new_exps[var_idx] = 0
        key = tuple(new_exps)
        if d not in coeffs:
            coeffs[d] = {}
        coeffs[d][key] = coeffs[d].get(key, 0) + c
    return coeffs

def resultant_by_eval(r0m1, r1, eval_var_idx, elim_var_idx, w, p):
    """Compute Res_{elim_var}(r₀-1, r₁) by evaluating eval_var at 0,1,...,p-1.

    Returns univariate in eval_var: {degree: coeff mod p}.
    """
    # Get max degree in elim_var for bound on resultant degree in eval_var
    max_deg_r0 = max((e[eval_var_idx] for e in r0m1.keys()), default=0)
    max_deg_r1 = max((e[eval_var_idx] for e in r1.keys()), default=0)
    max_elim_r0 = max((e[elim_var_idx] for e in r0m1.keys()), default=0)
    max_elim_r1 = max((e[elim_var_idx] for e in r1.keys()), default=0)

    res_deg_bound = max_elim_r0 * max_deg_r1 + max_elim_r1 * max_deg_r0

    if res_deg_bound >= p:
        return None  # can't interpolate

    eval_values = []
    for v in range(res_deg_bound + 1):
        # Fix eval_var = v, get polynomials in elim_var only
        f_spec = {}  # univariate in elim_var
        for exps, c in r0m1.items():
            coeff = (c * pow(v, exps[eval_var_idx], p)) % p
            if coeff == 0: continue
            d = exps[elim_var_idx]
            f_spec[d] = (f_spec.get(d, 0) + coeff) % p
            if f_spec[d] == 0: del f_spec[d]

        g_spec = {}
        for exps, c in r1.items():
            coeff = (c * pow(v, exps[eval_var_idx], p)) % p
            if coeff == 0: continue
            d = exps[elim_var_idx]
            g_spec[d] = (g_spec.get(d, 0) + coeff) % p
            if g_spec[d] == 0: del g_spec[d]

        res_val = univariate_resultant(f_spec, g_spec, p)
        eval_values.append(res_val)

    # Lagrange interpolation
    xs = list(range(res_deg_bound + 1))
    ys = eval_values
    result = lagrange_interp(xs, ys, p)
    return result

def lagrange_interp(xs, ys, p):
    n = len(xs)
    result = {}
    for i in range(n):
        if ys[i] == 0: continue
        basis = {0: 1}
        for j in range(n):
            if j == i: continue
            denom_inv = pow((xs[i] - xs[j]) % p, p - 2, p)
            new_basis = {}
            for d, c in basis.items():
                v1 = (c * denom_inv) % p
                new_basis[d+1] = (new_basis.get(d+1, 0) + v1) % p
                new_basis[d] = (new_basis.get(d, 0) - v1 * xs[j]) % p
            basis = {k: v % p for k, v in new_basis.items() if v % p != 0}
        for d, c in basis.items():
            result[d] = (result.get(d, 0) + ys[i] * c) % p
            if result[d] == 0: del result[d]
    return result

def upoly_factor_check_power(f, n, p):
    """Check if f(s) = c · s^a · G(s^n) for some G, a, c."""
    if not f: return None

    deg = upoly_degree(f)

    # Find lowest nonzero power
    min_pow = min(f.keys())

    # Check if all exponents ≡ min_pow mod n
    residues = set((d - min_pow) % n for d in f.keys())

    if residues == {0}:
        # YES! f(s) = s^{min_pow} · G(s^n) where G has support at (d-min_pow)/n
        G = {}
        for d, c in f.items():
            G_deg = (d - min_pow) // n
            G[G_deg] = c
        return min_pow, G
    else:
        return None

def print_upoly(f, var="s"):
    if not f:
        print("  0")
        return
    items = sorted(f.items(), key=lambda x: -x[0])
    parts = []
    for d, c in items:
        if d == 0:
            parts.append(f"{c}")
        elif d == 1:
            parts.append(f"{c}*{var}" if c != 1 else var)
        else:
            parts.append(f"{c}*{var}^{d}" if c != 1 else f"{var}^{d}")
    print("  " + " + ".join(parts))

# ---- Main tests ----

print("="*70)
print("RESULTANT STRUCTURE: BEYOND BIVARIATE")
print("="*70)

random.seed(42)

test_configs = [
    # (n, w, p)
    (8, 4, 29),
    (8, 4, 37),
    (8, 4, 41),
    (10, 4, 31),
    (10, 4, 41),
    (12, 4, 37),
    (8, 3, 29),
    (8, 3, 41),
    (10, 3, 31),
    (10, 3, 41),
]

for n, w, p in test_configs:
    q = n // w
    print(f"\n{'='*60}")
    print(f"n={n}, w={w}, q={q}, p={p}")
    print(f"{'='*60}")

    # Compute full r₀, r₁ in F_p[σ₁,...,σ_w]
    r_all = compute_all_ri_full(n, p, w)
    r0m1 = mpoly_sub(r_all[0], mpoly_const(1, p, w), p)
    r1 = r_all[1]

    # --- Case (a): bivariate σ₂=...=σ_{w-1}=0 ---
    # eval_var = 0 (σ₁), elim_var = w-1 (σ_w)
    r0m1_biv = mpoly_eval_partial(r0m1, {i: 0 for i in range(1, w-1)}, p)
    r1_biv = mpoly_eval_partial(r1, {i: 0 for i in range(1, w-1)}, p)

    res_biv = resultant_by_eval(r0m1_biv, r1_biv, 0, w-1, w, p)

    if res_biv is not None:
        power_check = upoly_factor_check_power(res_biv, n, p)
        if power_check:
            a, G = power_check
            print(f"  (a) bivariate: Res = s1^{a} · G(s1^{n}), deg(G)={upoly_degree(G)}")
            if upoly_degree(G) <= 3:
                print(f"      G =", end="")
                print_upoly(G, "t")
        else:
            print(f"  (a) bivariate: NO s1^a · G(s1^n) pattern! Degree={upoly_degree(res_biv)}")
            # Show the exponent residues
            if res_biv:
                min_pow = min(res_biv.keys())
                residues = sorted(set((d - min_pow) % n for d in res_biv.keys()))
                print(f"      min_pow={min_pow}, residues mod {n}: {residues}")
    else:
        print(f"  (a) bivariate: resultant degree too large for p={p}")

    # --- Case (c): σ₃=...=σ_{w-1}=0, σ₂=c for several constants ---
    if w >= 4:
        for sigma2_val in [0, 1, 2, 3]:
            # Set σ₂=sigma2_val, σ₃=...=σ_{w-2}=0
            assignments = {i: 0 for i in range(2, w-1)}
            assignments[1] = sigma2_val  # σ₂ = sigma2_val

            r0m1_spec = mpoly_eval_partial(r0m1, assignments, p)
            r1_spec = mpoly_eval_partial(r1, assignments, p)

            res_spec = resultant_by_eval(r0m1_spec, r1_spec, 0, w-1, w, p)

            if res_spec is not None:
                power_check = upoly_factor_check_power(res_spec, n, p)
                if power_check:
                    a, G = power_check
                    roots_G = upoly_roots(G, p) if upoly_degree(G) >= 0 else []
                    print(f"  (c) σ₂={sigma2_val}: Res = s1^{a} · G(s1^{n}), deg(G)={upoly_degree(G)}, G roots={roots_G[:5]}")
                else:
                    print(f"  (c) σ₂={sigma2_val}: NO s1^a·G(s1^n). deg={upoly_degree(res_spec)}")
                    if res_spec:
                        min_pow = min(res_spec.keys())
                        residues = sorted(set((d - min_pow) % n for d in res_spec.keys()))
                        print(f"      min_pow={min_pow}, residues mod {n}: {residues}")
            else:
                print(f"  (c) σ₂={sigma2_val}: degree too large")

    # --- Case (d): random 2-flat in full σ-space ---
    for trial in range(3):
        # Random flat: σ = base + s·dir1 + t·dir2
        base = tuple(random.randrange(p) for _ in range(w))
        dir1 = tuple(random.randrange(p) for _ in range(w))
        dir2 = tuple(random.randrange(p) for _ in range(w))

        # Evaluate the resultant on this flat by brute force:
        # For each s, compute r₀-1 and r₁ as functions of t, then resultant
        res_deg_bound = 2 * n  # rough bound
        if res_deg_bound >= p:
            print(f"  (d) random flat {trial}: p too small for interpolation")
            continue

        res_values = []
        for s in range(min(res_deg_bound + 1, p)):
            f_t = {}  # r₀-1 as univariate in t
            g_t = {}  # r₁ as univariate in t

            for exps, c in r0m1.items():
                # σ_i = base[i] + s*dir1[i] + t*dir2[i]
                # Monomial: Π σ_i^{e_i} as polynomial in t
                # This is complex... let me just evaluate at specific t values
                pass

            # Simpler: evaluate by brute force over t
            # Count roots instead of computing resultant
            pass

        # Actually, let me just count |V₀₁| on this flat by brute force
        count = 0
        pts = []
        for s in range(p):
            for t in range(p):
                sigma = tuple((base[i] + s * dir1[i] + t * dir2[i]) % p for i in range(w))
                v0 = 0
                for exps, c in r0m1.items():
                    term = c
                    for i, e in enumerate(exps):
                        if e > 0:
                            term = (term * pow(sigma[i], e, p)) % p
                    v0 = (v0 + term) % p
                if v0 != 0: continue

                v1 = 0
                for exps, c in r1.items():
                    term = c
                    for i, e in enumerate(exps):
                        if e > 0:
                            term = (term * pow(sigma[i], e, p)) % p
                    v1 = (v1 + term) % p
                if v1 != 0: continue

                count += 1
                if count <= 5:
                    pts.append((s, t))

        # Check if the s-coordinates have n-th power structure
        s_vals = [s for s, t in pts]
        if s_vals:
            s_powers = [pow(s, n, p) for s in s_vals if s != 0]
            unique_powers = set(s_powers)
            n_zero = s_vals.count(0)
            print(f"  (d) random flat {trial}: |V₀₁|={count}, s=0 count={n_zero}, "
                  f"#distinct s^n={len(unique_powers)}, fibers={[s_powers.count(x) for x in sorted(unique_powers)][:5]}")
        else:
            print(f"  (d) random flat {trial}: |V₀₁|=0")

print("\n" + "="*70)
print("KEY QUESTION: Does G(s1^n) structure survive on non-bivariate flats?")
print("="*70)
