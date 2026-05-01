"""
irreducibility_deep.py — Deep analysis of r_0-1 irreducibility.

Focus:
1. The "failing" case (n=12,p=13,w=4,trial 0): actually try to factor
2. Same (n,w) with larger p: is irreducibility p-independent?
3. Count: over many random flats, what fraction has r_0-1 irreducible?
4. Structural: check if r_0-1 factors as product of lower-degree curves
"""

import random
from math import comb, gcd, isqrt

# ---- Polynomial arithmetic (F_p[s_1,s_2] and F_p[t]) ----

def poly_zero(): return {}
def poly_const(c, p):
    c = c % p
    return {(0,0): c} if c else {}
def poly_var(idx):
    key = [0, 0]; key[idx] = 1
    return {tuple(key): 1}
def poly_add(f, g, p):
    r = dict(f)
    for k, v in g.items():
        r[k] = (r.get(k, 0) + v) % p
        if r[k] == 0: del r[k]
    return r
def poly_sub(f, g, p):
    r = dict(f)
    for k, v in g.items():
        r[k] = (r.get(k, 0) - v) % p
        if r[k] == 0: del r[k]
    return r
def poly_mul(f, g, p):
    r = {}
    for (a1, b1), c1 in f.items():
        for (a2, b2), c2 in g.items():
            key = (a1+a2, b1+b2)
            r[key] = (r.get(key, 0) + c1 * c2) % p
            if r[key] == 0: del r[key]
    return r
def poly_scale(f, c, p):
    c = c % p
    if c == 0: return {}
    return {k: (v * c) % p for k, v in f.items() if (v * c) % p != 0}
def poly_degree(f):
    if not f: return -1
    return max(a + b for a, b in f.keys())
def poly_eval(f, s1, s2, p):
    r = 0
    for (a, b), c in f.items():
        r = (r + c * pow(s1, a, p) * pow(s2, b, p)) % p
    return r
def poly_s1_degree(f):
    if not f: return -1
    return max(a for a, b in f.keys())
def poly_s2_degree(f):
    if not f: return -1
    return max(b for a, b in f.keys())

# Univariate
def upoly_degree(f):
    if not f: return -1
    return max(f.keys())
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
def upoly_mod(f, g, p):
    f = dict(f)
    dg = upoly_degree(g)
    if dg < 0: raise ValueError
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
    if f:
        lc = f[upoly_degree(f)]
        lc_inv = pow(lc, p - 2, p)
        f = {k: (v * lc_inv) % p for k, v in f.items()}
    return f
def upoly_powmod(base, exp, modulus, p):
    result = {0: 1}; b = dict(base)
    while exp > 0:
        if exp & 1: result = upoly_mod(upoly_mul(result, b, p), modulus, p)
        b = upoly_mod(upoly_mul(b, b, p), modulus, p)
        exp >>= 1
    return result
def upoly_is_irreducible(f, p):
    d = upoly_degree(f)
    if d <= 0: return False
    if d == 1: return True
    lc = f[d]; lc_inv = pow(lc, p - 2, p)
    fm = {k: (v * lc_inv) % p for k, v in f.items()}
    h = {1: 1}
    for i in range(1, d):
        h = upoly_powmod(h, p, fm, p)
        hx = upoly_sub(h, {1: 1}, p)
        g = upoly_gcd(dict(fm), hx, p)
        if upoly_degree(g) > 0: return False
    return True

def specialize_s2(f_bivar, s2_val, p):
    r = {}
    for (a, b), c in f_bivar.items():
        val = (c * pow(s2_val, b, p)) % p
        if val:
            r[a] = (r.get(a, 0) + val) % p
            if r[a] == 0: del r[a]
    return r

def specialize_s1(f_bivar, s1_val, p):
    r = {}
    for (a, b), c in f_bivar.items():
        val = (c * pow(s1_val, a, p)) % p
        if val:
            r[b] = (r.get(b, 0) + val) % p
            if r[b] == 0: del r[b]
    return r

# ---- Companion matrix ----
def compute_remainder_poly(sigma_polys, n, p):
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

def find_primitive_root(p):
    for g in range(2, p):
        seen = set(); x = 1
        for _ in range(p-1):
            seen.add(x); x = (x * g) % p
        if len(seen) == p-1: return g
    return None

# ---- Flat parameterization ----
def make_flat(n, p, w, c, rng):
    d = w - c
    normals = [tuple(rng.randint(0, p-1) for _ in range(w)) for _ in range(c)]
    offsets = [rng.randint(0, p-1) for _ in range(c)]
    mat = [[normals[j][i] for i in range(w)] + [offsets[j]] for j in range(c)]
    pivots = []
    for col in range(w):
        if len(pivots) >= c: break
        row = len(pivots); found = False
        for r in range(row, c):
            if mat[r][col] % p != 0:
                mat[row], mat[r] = mat[r], mat[row]; found = True; break
        if not found: continue
        inv = pow(mat[row][col], p-2, p)
        for j in range(w+1): mat[row][j] = (mat[row][j] * inv) % p
        for r in range(c):
            if r != row and mat[r][col] % p != 0:
                fac = mat[r][col]
                for j in range(w+1): mat[r][j] = (mat[r][j] - fac * mat[row][j]) % p
        pivots.append(col)
    if len(pivots) < c: return None
    free_vars = [j for j in range(w) if j not in pivots]
    if len(free_vars) != d: return None
    a_vals = [0]*w; b_vals = [[0]*d for _ in range(w)]
    for idx, piv in enumerate(pivots):
        a_vals[piv] = mat[idx][w]
        for fi, fv in enumerate(free_vars):
            b_vals[piv][fi] = (-mat[idx][fv]) % p
    for fi, fv in enumerate(free_vars):
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

# ---- Factorization attempt for bivariate polynomial ----
def try_factor_bivariate(f, p):
    """Try to factor f ∈ F_p[s_1,s_2] by looking for a factor via specialization + Hensel.

    Strategy: if f = g·h, then for each s_2 = a, f(s_1, a) = g(s_1, a)·h(s_1, a).
    Find all factorizations of f(s_1, a) for several values of a,
    then try to lift a consistent factorization.

    Returns: list of (degree, degree) pairs for each found factorization at each s_2,
             or "IRREDUCIBLE" if no consistent factorization pattern exists.
    """
    D = poly_degree(f)
    ds1 = poly_s1_degree(f)

    # For each s_2 = a, factor f(s_1, a) in F_p[s_1]
    factor_patterns = {}  # s_2_val -> list of factor degrees

    for a in range(p):
        spec = specialize_s2(f, a, p)
        d_spec = upoly_degree(spec)
        if d_spec <= 0:
            factor_patterns[a] = [0]
            continue

        # Find all irreducible factors via distinct-degree factorization
        factors = ddf_factorization(spec, p)
        factor_patterns[a] = factors

    return factor_patterns

def ddf_factorization(f, p):
    """Distinct-degree factorization of f in F_p[t].
    Returns list of (degree_of_irreducible_factor, multiplicity) or just degrees.
    Actually, returns sorted list of degrees of irreducible factors (with repetition).
    """
    d = upoly_degree(f)
    if d <= 0: return []
    if d == 1: return [1]

    # Make monic
    lc = f[d]; lc_inv = pow(lc, p-2, p)
    fm = {k: (v * lc_inv) % p for k, v in f.items()}

    factors = []
    remaining = dict(fm)
    h = {1: 1}  # h = x

    for i in range(1, d // 2 + 1):
        h = upoly_powmod(h, p, remaining, p)
        hx = upoly_sub(h, {1: 1}, p)
        g = upoly_gcd(dict(remaining), hx, p)
        dg = upoly_degree(g)
        if dg > 0:
            # g is product of all irreducible factors of degree i
            num_factors = dg // i
            factors.extend([i] * num_factors)
            # Divide out
            while True:
                q, r = upoly_divmod(remaining, g, p)
                if not r:
                    remaining = q
                else:
                    break
            # Recompute h mod new remaining
            dr = upoly_degree(remaining)
            if dr > 0:
                h = upoly_mod(h, remaining, p)
            else:
                break

    dr = upoly_degree(remaining)
    if dr > 0:
        factors.append(dr)

    return sorted(factors)

def upoly_divmod(f, g, p):
    """Returns (quotient, remainder)."""
    f = dict(f)
    dg = upoly_degree(g)
    if dg < 0: raise ValueError
    lc_inv = pow(g[dg], p-2, p)
    q = {}
    while True:
        df = upoly_degree(f)
        if df < dg: return q, f
        shift = df - dg
        coeff = (f[df] * lc_inv) % p
        q[shift] = coeff
        for i, v in g.items():
            k = i + shift
            f[k] = (f.get(k, 0) - coeff * v) % p
            if f[k] == 0: del f[k]

# ---- Main ----

def test_irreducibility_stats(n, p, w, c, num_trials=50):
    """Run many trials, count how often r_0-1 is provably irreducible."""
    d = w - c
    k = n - w - c
    D = n - w + 1
    if k < 1 or d != 2: return

    print(f"\n{'='*70}")
    print(f"n={n}, p={p}, w={w}, c={c}, d={d}, D={D}, N=C({n},{w})={comb(n,w)}")
    print(f"Density = N/p^c = {comb(n,w)/p**c:.3f}")
    print(f"Running {num_trials} trials...")

    rng = random.Random(12345)

    abs_irred = 0
    s2_irred_only = 0  # has irred s2-spec but no irred s1-spec
    neither = 0
    point_counts = []

    for trial in range(num_trials):
        sigma_polys = make_flat(n, p, w, c, rng)
        if sigma_polys is None:
            continue

        remainders = compute_remainder_poly(sigma_polys, n, p)
        r0m1 = poly_sub(remainders[0], poly_const(1, p), p)
        ds1 = poly_s1_degree(r0m1)
        ds2 = poly_s2_degree(r0m1)

        # Count rational points
        v_count = sum(1 for s1 in range(p) for s2 in range(p)
                      if poly_eval(r0m1, s1, s2, p) == 0)
        point_counts.append(v_count)

        # Test irreducibility via specialization
        has_s2_irred = False
        has_s1_irred = False

        for a in range(p):
            spec = specialize_s2(r0m1, a, p)
            if upoly_degree(spec) == ds1 and upoly_is_irreducible(spec, p):
                has_s2_irred = True
                break

        if has_s2_irred:
            for a in range(p):
                spec = specialize_s1(r0m1, a, p)
                if upoly_degree(spec) == ds2 and upoly_is_irreducible(spec, p):
                    has_s1_irred = True
                    break

        if has_s2_irred and has_s1_irred:
            abs_irred += 1
        elif has_s2_irred:
            s2_irred_only += 1
        else:
            neither += 1

    total = abs_irred + s2_irred_only + neither
    print(f"\n  Results ({total} valid trials):")
    print(f"    Absolutely irreducible (both directions): {abs_irred} ({100*abs_irred/max(total,1):.0f}%)")
    print(f"    s2-irred only (no s1-irred found):        {s2_irred_only} ({100*s2_irred_only/max(total,1):.0f}%)")
    print(f"    Neither direction found irred:             {neither} ({100*neither/max(total,1):.0f}%)")

    avg_pts = sum(point_counts) / len(point_counts) if point_counts else 0
    min_pts = min(point_counts) if point_counts else 0
    max_pts = max(point_counts) if point_counts else 0
    print(f"    |V(r_0-1)|: avg={avg_pts:.1f}, min={min_pts}, max={max_pts}")
    print(f"    Weil prediction (1 component): {p} ± {D*isqrt(p)}")

    return abs_irred, s2_irred_only, neither, point_counts

def deep_factor_analysis(n, p, w, c, trial_seed=42):
    """For one specific flat, analyze the factorization structure in detail."""
    d = w - c
    k = n - w - c
    D = n - w + 1
    if k < 1 or d != 2: return

    print(f"\n{'='*70}")
    print(f"DEEP FACTOR ANALYSIS: n={n}, p={p}, w={w}, c={c}")

    rng = random.Random(trial_seed)
    sigma_polys = make_flat(n, p, w, c, rng)
    if sigma_polys is None:
        print("  Failed to make flat")
        return

    remainders = compute_remainder_poly(sigma_polys, n, p)
    r0m1 = poly_sub(remainders[0], poly_const(1, p), p)
    ds1 = poly_s1_degree(r0m1)
    ds2 = poly_s2_degree(r0m1)
    dtot = poly_degree(r0m1)

    print(f"  r_0-1: total_deg={dtot}, s1_deg={ds1}, s2_deg={ds2}, #terms={len(r0m1)}")

    # For each s_2 = a, factor f(s_1, a)
    print(f"\n  Factorization patterns of f(s_1, a) for a ∈ F_{p}:")
    patterns = {}
    for a in range(p):
        spec = specialize_s2(r0m1, a, p)
        d_spec = upoly_degree(spec)
        if d_spec <= 0:
            pattern = (0,)
        elif d_spec == 1:
            pattern = (1,)
        else:
            degs = ddf_factorization(spec, p)
            pattern = tuple(degs)
        patterns[a] = pattern
        print(f"    s_2={a:2d}: deg={d_spec:2d}, factors={pattern}")

    # Group by pattern
    pattern_groups = {}
    for a, pat in patterns.items():
        pattern_groups.setdefault(pat, []).append(a)

    print(f"\n  Pattern summary:")
    for pat, vals in sorted(pattern_groups.items()):
        print(f"    {pat}: {len(vals)} values ({vals[:5]}{'...' if len(vals)>5 else ''})")

    # If there's a UNIVERSAL split d1+d2 = ds1, that's a factorization candidate
    # Check: is there a pair (d1, d2) that appears in ALL factorizations?
    print(f"\n  Looking for consistent binary split...")
    for d1 in range(1, ds1):
        d2 = ds1 - d1
        consistent = True
        for a, pat in patterns.items():
            if sum(pat) < ds1:  # degree drop
                continue
            # Check if pat can be split into groups summing to d1 and d2
            if not can_split(pat, d1):
                consistent = False
                break
        if consistent:
            print(f"    Split ({d1}, {d2}) is CONSISTENT with all factorizations!")

    # Also do the s_1 direction
    print(f"\n  Factorization patterns of f(a, s_2) for a ∈ F_{p}:")
    for a in range(min(p, 15)):
        spec = specialize_s1(r0m1, a, p)
        d_spec = upoly_degree(spec)
        if d_spec <= 0:
            pattern = (0,)
        elif d_spec == 1:
            pattern = (1,)
        else:
            degs = ddf_factorization(spec, p)
            pattern = tuple(degs)
        print(f"    s_1={a:2d}: deg={d_spec:2d}, factors={pattern}")

def can_split(degrees, target):
    """Can the tuple of degrees be partitioned into a group summing to target?"""
    # Simple subset-sum check
    n = len(degrees)
    if n == 0: return target == 0
    # DP
    possible = {0}
    for d in degrees:
        new = set()
        for s in possible:
            new.add(s + d)
        possible |= new
    return target in possible


# ---- Run statistics ----
print("=" * 70)
print("IRREDUCIBILITY STATISTICS OVER MANY RANDOM FLATS")
print("=" * 70)

# Test with different p for same (n,w)
for n, p, w, c in [
    (10, 11, 4, 2),
    (10, 13, 4, 2),
    (10, 17, 4, 2),
    (10, 23, 4, 2),
    (10, 29, 4, 2),
    (12, 13, 4, 2),
    (12, 17, 4, 2),
    (12, 23, 4, 2),
    (8, 11, 3, 1),
    (8, 13, 3, 1),
    (8, 17, 3, 1),
]:
    test_irreducibility_stats(n, p, w, c, num_trials=30)

# Deep analysis of the "failing" case
print("\n\n" + "="*70)
print("DEEP FACTOR ANALYSIS OF 'FAILING' CASES")
print("="*70)

# n=12,p=13,w=4 trial 0 from previous script (seed=42)
deep_factor_analysis(12, 13, 4, 2, trial_seed=42)
