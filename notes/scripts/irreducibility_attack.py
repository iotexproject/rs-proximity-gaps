#!/usr/bin/env python3
"""
Irreducibility attack on r_0(s_1,s_2) - 1.

If r_0 - 1 is IRREDUCIBLE over F_p:
  - V(r_0-1) is a plane curve of degree D = n-w+1
  - By Weil: |V(r_0-1)(F_p)| = p + O(D√p)
  - Intersection with V(r_1): |V(r_0-1,r_1)(F_p)| ≤ D² (Bézout)
  - But rational intersection ≈ D (heuristic)

Strategy:
1. Compute r_0, r_1 as explicit polynomials in F_p[s_1,s_2]
2. Factor r_0-1 over F_p using sympy
3. Check irreducibility and smoothness
4. Count rational points, verify Weil
5. Sweep many (n,p,w) configs

Multi-core for the sweep.
"""

import random
from math import comb, sqrt, gcd
from multiprocessing import Pool, cpu_count
import time
import sys

# ---- Polynomial arithmetic in F_p[s_1, s_2] ----

def poly_zero():
    return {}

def poly_const(c, p):
    c = c % p
    if c == 0: return {}
    return {(0,0): c}

def poly_var(idx):
    key = [0, 0]; key[idx] = 1
    return {tuple(key): 1}

def poly_add(f, g, p):
    result = dict(f)
    for k, v in g.items():
        result[k] = (result.get(k, 0) + v) % p
        if result[k] == 0: del result[k]
    return result

def poly_sub(f, g, p):
    result = dict(f)
    for k, v in g.items():
        result[k] = (result.get(k, 0) - v) % p
        if result[k] == 0: del result[k]
    return result

def poly_mul(f, g, p):
    result = {}
    for (a1, b1), c1 in f.items():
        for (a2, b2), c2 in g.items():
            key = (a1+a2, b1+b2)
            result[key] = (result.get(key, 0) + c1 * c2) % p
            if result[key] == 0: del result[key]
    return result

def poly_scale(f, c, p):
    c = c % p
    if c == 0: return {}
    return {k: (v * c) % p for k, v in f.items() if (v * c) % p != 0}

def poly_degree(f):
    if not f: return -1
    return max(a + b for a, b in f.keys())

def poly_eval(f, s1, s2, p):
    result = 0
    for (a, b), c in f.items():
        result = (result + c * pow(s1, a, p) * pow(s2, b, p)) % p
    return result

# ---- Companion matrix x^n mod Λ(x) ----

def compute_remainders(sigma_polys, n, p):
    """Compute x^n mod Λ(x) where σ_j are polynomials in (s_1, s_2)."""
    w = len(sigma_polys)
    c_polys = [None] * w
    for j in range(w):
        sign = pow(-1, w - j + 1, p)
        c_polys[j] = poly_scale(sigma_polys[w - j - 1], sign, p)

    state = [poly_const(0, p) for _ in range(w)]
    state[0] = poly_const(1, p)

    for step in range(n):
        top = state[w - 1]
        new_state = [None] * w
        new_state[0] = poly_mul(top, c_polys[0], p)
        for j in range(1, w):
            new_state[j] = poly_add(state[j-1], poly_mul(top, c_polys[j], p), p)
        state = new_state

    return state

# ---- Random flat generation ----

def random_flat(n, p, w, c, seed=None):
    """Generate a random c-dimensional flat in F_p^w parameterized by d=w-c variables.
    Returns sigma_polys: list of w polynomials in (s_1,...,s_d)."""
    d = w - c
    if seed is not None:
        random.seed(seed)

    # Random c × w matrix (normals) + c offsets
    normals = [[random.randint(0, p-1) for _ in range(w)] for _ in range(c)]
    offsets = [random.randint(0, p-1) for _ in range(c)]

    # Row reduce
    mat = [normals[j] + [offsets[j]] for j in range(c)]
    pivots = []
    for col in range(w):
        if len(pivots) >= c: break
        row = len(pivots)
        found = False
        for r in range(row, c):
            if mat[r][col] % p != 0:
                mat[row], mat[r] = mat[r], mat[row]
                found = True
                break
        if not found: continue
        inv = pow(mat[row][col], p-2, p)
        for j in range(w+1):
            mat[row][j] = (mat[row][j] * inv) % p
        for r in range(c):
            if r != row and mat[r][col] % p != 0:
                fac = mat[r][col]
                for j in range(w+1):
                    mat[r][j] = (mat[r][j] - fac * mat[row][j]) % p
        pivots.append(col)

    if len(pivots) < c: return None

    free_vars = [j for j in range(w) if j not in pivots]
    if len(free_vars) != d: return None

    a_vals = [0]*w
    b_vals = [[0]*d for _ in range(w)]
    for idx, piv in enumerate(pivots):
        a_vals[piv] = mat[idx][w]
        for fi, fv in enumerate(free_vars):
            b_vals[piv][fi] = (-mat[idx][fv]) % p
    for fi, fv in enumerate(free_vars):
        a_vals[fv] = 0
        b_vals[fv][fi] = 1

    sigma_polys = []
    for j in range(w):
        poly = poly_const(a_vals[j], p)
        for i in range(d):
            if b_vals[j][i] % p != 0:
                vi = poly_var(i)
                poly = poly_add(poly, poly_scale(vi, b_vals[j][i], p), p)
        sigma_polys.append(poly)

    return sigma_polys

# ---- Convert to sympy for factoring ----

def to_sympy_poly(f_dict, p):
    """Convert dict polynomial to sympy Poly over GF(p)."""
    from sympy import Symbol, Poly, GF as SymGF
    s1 = Symbol('s1')
    s2 = Symbol('s2')

    expr = 0
    for (a, b), c in f_dict.items():
        expr += int(c) * s1**a * s2**b

    if expr == 0:
        return Poly(0, s1, s2, domain=SymGF(p))
    return Poly(expr, s1, s2, domain=SymGF(p))

def factor_poly(f_dict, p):
    """Factor bivariate polynomial over F_p. Returns (irreducible, factor_list)."""
    try:
        sp = to_sympy_poly(f_dict, p)
        flist = sp.factor_list()
        # flist = (content, [(factor1, mult1), (factor2, mult2), ...])
        content, factors = flist
        irreducible = len(factors) == 1 and factors[0][1] == 1
        return irreducible, factors
    except Exception as e:
        return None, str(e)

# ---- Irreducibility via substitution test (faster for large cases) ----

def irreducibility_heuristic(f_dict, p, num_tests=20):
    """Heuristic irreducibility test:
    1. For random c ∈ F_p: factor f(s1, c) as univariate over F_p.
    2. If f(s1, c) is irreducible for many c → likely f is irreducible.

    More precisely: if f(s1, c0) is irreducible for SOME c0, then f is irreducible.
    (Bertini's theorem for finite fields.)
    """
    from sympy import Symbol, Poly, GF as SymGF
    s1 = Symbol('s1')

    D = poly_degree(f_dict)
    num_irred = 0

    for _ in range(num_tests):
        c = random.randint(0, p-1)
        # Evaluate f(s1, c) as univariate
        uni = {}
        for (a, b), coeff in f_dict.items():
            cb = pow(c, b, p)
            val = (coeff * cb) % p
            uni[a] = (uni.get(a, 0) + val) % p

        # Convert to sympy univariate
        expr = sum(int(v) * s1**k for k, v in uni.items() if v != 0)
        if expr == 0:
            continue

        try:
            up = Poly(expr, s1, domain=SymGF(p))
            deg = up.degree()
            if deg != D:  # Degree drop → f has content in s2
                continue
            fl = up.factor_list()
            _, factors = fl
            if len(factors) == 1 and factors[0][1] == 1:
                num_irred += 1
        except:
            continue

    return num_irred, num_tests

# ---- Smoothness check ----

def partial_deriv(f_dict, var_idx, p):
    """Partial derivative w.r.t. s_{var_idx+1}."""
    result = {}
    for (a, b), c in f_dict.items():
        if var_idx == 0 and a > 0:
            new_c = (c * a) % p
            if new_c != 0:
                result[(a-1, b)] = new_c
        elif var_idx == 1 and b > 0:
            new_c = (c * b) % p
            if new_c != 0:
                result[(a, b-1)] = new_c
    return result

def count_singular_points(f_dict, p):
    """Count singular points of V(f) in A^2(F_p): where f = df/ds1 = df/ds2 = 0."""
    df_ds1 = partial_deriv(f_dict, 0, p)
    df_ds2 = partial_deriv(f_dict, 1, p)

    singular = []
    for s1 in range(p):
        for s2 in range(p):
            if (poly_eval(f_dict, s1, s2, p) == 0 and
                poly_eval(df_ds1, s1, s2, p) == 0 and
                poly_eval(df_ds2, s1, s2, p) == 0):
                singular.append((s1, s2))

    return singular

# ---- Main analysis ----

def analyze_config(args):
    """Analyze a single (n, p, w, c, seed) configuration."""
    n, p, w, c, seed = args
    d = w - c
    k = n - w - c
    D = n - w + 1  # corrected degree

    if d != 2 or k < 1:
        return None

    sigma_polys = random_flat(n, p, w, c, seed=seed)
    if sigma_polys is None:
        return None

    # Compute remainder polynomials
    remainders = compute_remainders(sigma_polys, n, p)

    r0m1 = poly_sub(remainders[0], poly_const(1, p), p)
    r1 = remainders[1]

    deg_r0m1 = poly_degree(r0m1)
    deg_r1 = poly_degree(r1)

    # Count zeros by brute force
    zeros_r0m1 = 0
    zeros_r1 = 0
    zeros_both = 0
    zeros_all = 0

    for s1 in range(p):
        for s2 in range(p):
            v0 = poly_eval(r0m1, s1, s2, p)
            v1 = poly_eval(r1, s1, s2, p)
            if v0 == 0: zeros_r0m1 += 1
            if v1 == 0: zeros_r1 += 1
            if v0 == 0 and v1 == 0:
                zeros_both += 1
                # Check all remaining
                all_zero = True
                for j in range(2, w):
                    if poly_eval(remainders[j], s1, s2, p) != 0:
                        all_zero = False
                        break
                    # Also check r_0 = 1 (already checked via r0m1)
                if all_zero:
                    zeros_all += 1

    # Weil bound for smooth irreducible curve of degree D:
    # |V(F_p)| = p + 1 - t where |t| ≤ (D-1)(D-2)√p
    weil_bound = (D-1)*(D-2)*sqrt(p)

    # Check irreducibility
    irred_result = None
    factor_info = None

    if len(r0m1) < 2000:  # Only factor if not too many terms
        try:
            irred, factors = factor_poly(r0m1, p)
            irred_result = irred
            if factors and isinstance(factors, list):
                factor_info = [(poly_degree({}), m) for _, m in factors]
                # Get degrees from sympy factors
                factor_info = []
                for fac, mult in factors:
                    try:
                        fd = fac.total_degree()
                    except:
                        fd = "?"
                    factor_info.append((fd, mult))
        except Exception as e:
            irred_result = f"error: {e}"

    # Heuristic irreducibility (faster)
    num_irred_sub, num_tests = irreducibility_heuristic(r0m1, p, num_tests=15)

    # Singular points
    singular = []
    if p <= 50:  # Only check for small p
        singular = count_singular_points(r0m1, p)

    result = {
        'n': n, 'p': p, 'w': w, 'c': c, 'd': d, 'k': k, 'D': D,
        'deg_r0m1': deg_r0m1, 'deg_r1': deg_r1,
        'zeros_r0m1': zeros_r0m1, 'zeros_r1': zeros_r1,
        'zeros_both': zeros_both, 'zeros_all': zeros_all,
        'weil_bound': weil_bound,
        'irred': irred_result, 'factor_info': factor_info,
        'irred_heuristic': (num_irred_sub, num_tests),
        'singular': singular,
        'seed': seed,
        'density': comb(n, w) / p**c,
    }
    return result

def print_result(r):
    if r is None: return
    print(f"\n  n={r['n']}, p={r['p']}, w={r['w']}, c={r['c']}, d={r['d']}, D={r['D']}, seed={r['seed']}")
    print(f"  deg(r_0-1)={r['deg_r0m1']}, deg(r_1)={r['deg_r1']}")
    print(f"  |V(r_0-1)(F_p)| = {r['zeros_r0m1']}, Weil: p ± {r['weil_bound']:.0f} = [{r['p']-r['weil_bound']:.0f}, {r['p']+r['weil_bound']:.0f}]")
    print(f"  |V(r_1)(F_p)| = {r['zeros_r1']}")
    print(f"  |V(r_0-1,r_1)(F_p)| = {r['zeros_both']}, |V_all(F_p)| = {r['zeros_all']}")
    print(f"  Bézout bound: D^2 = {r['D']**2}")
    print(f"  density = C(n,w)/p^c = {r['density']:.4f}")

    if r['irred'] is not None:
        print(f"  IRREDUCIBLE: {r['irred']}")
        if r['factor_info']:
            print(f"  Factors: {r['factor_info']}")

    irr_h, irr_t = r['irred_heuristic']
    print(f"  Irreducibility heuristic: {irr_h}/{irr_t} substitutions give irreducible univariate")

    if r['singular']:
        print(f"  SINGULAR POINTS: {r['singular']}")
    elif r['p'] <= 50:
        print(f"  Smooth (no singular F_p-points)")

def main():
    print("=" * 70)
    print("IRREDUCIBILITY ATTACK ON r_0(s_1,s_2) - 1")
    print("=" * 70)

    # Configs: (n, p, w, c) with d = w-c = 2
    configs = []

    # Small p (full factoring feasible)
    for n, p, w, c in [
        (8, 11, 4, 2),   # D=5
        (8, 13, 4, 2),   # D=5
        (8, 17, 4, 2),   # D=5
        (8, 23, 4, 2),   # D=5
        (8, 31, 4, 2),   # D=5
        (10, 11, 4, 2),  # D=7
        (10, 13, 4, 2),  # D=7
        (10, 17, 4, 2),  # D=7
        (10, 31, 4, 2),  # D=7
        (10, 41, 4, 2),  # D=7
        (10, 61, 4, 2),  # D=7
        (10, 101, 4, 2), # D=7
        (12, 13, 5, 3),  # D=8
        (12, 17, 5, 3),  # D=8
        (12, 31, 5, 3),  # D=8
        (14, 17, 5, 3),  # D=10
        (14, 31, 5, 3),  # D=10
        (14, 41, 5, 3),  # D=10
        (16, 17, 6, 4),  # D=11 — only if d=2 check: w-c=6-4=2 ✓
        (16, 31, 6, 4),  # D=11
    ]:
        if w - c != 2:
            continue
        # Multiple seeds per config
        for seed in range(3):
            configs.append((n, p, w, c, seed * 1000 + n * 100 + p))

    print(f"Testing {len(configs)} configurations...")

    # Run with multiprocessing
    num_workers = min(cpu_count(), 16)
    t0 = time.time()

    results_by_config = {}

    with Pool(num_workers) as pool:
        results = pool.map(analyze_config, configs)

    print(f"\nDone in {time.time()-t0:.1f}s")

    # Summarize
    print("\n" + "=" * 70)
    print("SUMMARY TABLE")
    print("=" * 70)
    print(f"{'n':>3} {'p':>4} {'w':>2} {'c':>2} {'D':>3} {'|V(r0-1)|':>10} {'|V(r1)|':>8} {'|V01|':>6} {'M':>4} {'irred':>6} {'heur':>6} {'#sing':>5} {'density':>8}")

    irred_count = 0
    total_count = 0

    for r in results:
        if r is None: continue
        total_count += 1

        irred_str = "?"
        if r['irred'] is True:
            irred_str = "YES"
            irred_count += 1
        elif r['irred'] is False:
            irred_str = "NO"

        irr_h, irr_t = r['irred_heuristic']
        heur_str = f"{irr_h}/{irr_t}"

        nsing = len(r['singular']) if r['singular'] is not None else "?"

        print(f"{r['n']:>3} {r['p']:>4} {r['w']:>2} {r['c']:>2} {r['D']:>3} "
              f"{r['zeros_r0m1']:>10} {r['zeros_r1']:>8} {r['zeros_both']:>6} {r['zeros_all']:>4} "
              f"{irred_str:>6} {heur_str:>6} {str(nsing):>5} {r['density']:>8.3f}")

    print(f"\nIrreducible: {irred_count}/{total_count}")

    # Detailed output for interesting cases
    print("\n" + "=" * 70)
    print("DETAILED RESULTS")
    print("=" * 70)

    for r in results:
        if r is not None:
            print_result(r)

if __name__ == "__main__":
    main()
