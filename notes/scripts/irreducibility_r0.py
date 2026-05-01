"""
irreducibility_r0.py — Test irreducibility of r_0(s_1,s_2) - 1 in F_p[s_1,s_2].

Attack plan:
1. Compute r_0 - 1 as explicit polynomial in F_p[s_1,s_2]
2. Test: is r_0(s_1, a) - 1 irreducible in F_p[s_1] for generic a? (Hilbert irreducibility)
3. Count |V(r_0-1)(F_p)| and compare with Weil prediction p + O(D√p)
4. Try to find a factorization r_0 - 1 = f * g (bivariate Hensel/substitution)
5. Check Newton polygon structure

Key insight: if r_0(s_1, a) - 1 is irreducible for SOME a ∈ F_p,
then r_0 - 1 has no factor of positive s_2-degree → at most a
factor in F_p[s_1] alone. Then check the s_1-slice similarly.
"""

import random
from math import comb, gcd, isqrt

# ---- Polynomial arithmetic in F_p[s_1, s_2] (from overdetermined_coprime.py) ----

def poly_zero():
    return {}

def poly_const(c, p):
    c = c % p
    return {(0,0): c} if c else {}

def poly_var(idx):
    key = [0, 0]
    key[idx] = 1
    return {tuple(key): 1}

def poly_add(f, g, p):
    result = dict(f)
    for k, v in g.items():
        result[k] = (result.get(k, 0) + v) % p
        if result[k] == 0:
            del result[k]
    return result

def poly_sub(f, g, p):
    result = dict(f)
    for k, v in g.items():
        result[k] = (result.get(k, 0) - v) % p
        if result[k] == 0:
            del result[k]
    return result

def poly_mul(f, g, p):
    result = {}
    for (a1, b1), c1 in f.items():
        for (a2, b2), c2 in g.items():
            key = (a1+a2, b1+b2)
            result[key] = (result.get(key, 0) + c1 * c2) % p
            if result[key] == 0:
                del result[key]
    return result

def poly_scale(f, c, p):
    c = c % p
    if c == 0:
        return {}
    return {k: (v * c) % p for k, v in f.items() if (v * c) % p != 0}

def poly_degree(f):
    if not f:
        return -1
    return max(a + b for a, b in f.keys())

def poly_eval(f, s1, s2, p):
    result = 0
    for (a, b), c in f.items():
        result = (result + c * pow(s1, a, p) * pow(s2, b, p)) % p
    return result

def poly_s1_degree(f):
    """Max s_1-degree."""
    if not f:
        return -1
    return max(a for a, b in f.keys())

def poly_s2_degree(f):
    """Max s_2-degree."""
    if not f:
        return -1
    return max(b for a, b in f.keys())

# ---- Univariate polynomial arithmetic in F_p[t] ----

def upoly_from_list(coeffs, p):
    """coeffs[i] = coefficient of t^i."""
    return {i: c % p for i, c in enumerate(coeffs) if c % p != 0}

def upoly_degree(f):
    if not f:
        return -1
    return max(f.keys())

def upoly_add(f, g, p):
    result = dict(f)
    for k, v in g.items():
        result[k] = (result.get(k, 0) + v) % p
        if result[k] == 0:
            del result[k]
    return result

def upoly_sub(f, g, p):
    result = dict(f)
    for k, v in g.items():
        result[k] = (result.get(k, 0) - v) % p
        if result[k] == 0:
            del result[k]
    return result

def upoly_mul(f, g, p):
    result = {}
    for i, a in f.items():
        for j, b in g.items():
            k = i + j
            result[k] = (result.get(k, 0) + a * b) % p
            if result[k] == 0:
                del result[k]
    return result

def upoly_scale(f, c, p):
    c = c % p
    if c == 0:
        return {}
    return {k: (v * c) % p for k, v in f.items() if (v * c) % p != 0}

def upoly_mod(f, g, p):
    """f mod g in F_p[t]."""
    f = dict(f)
    dg = upoly_degree(g)
    if dg < 0:
        raise ValueError("division by zero poly")
    lc_inv = pow(g[dg], p - 2, p)
    while True:
        df = upoly_degree(f)
        if df < dg:
            return f
        shift = df - dg
        coeff = (f[df] * lc_inv) % p
        for i, v in g.items():
            k = i + shift
            f[k] = (f.get(k, 0) - coeff * v) % p
            if f[k] == 0:
                del f[k]

def upoly_gcd(f, g, p):
    """GCD in F_p[t]."""
    while g:
        f, g = g, upoly_mod(f, g, p)
    if f:
        # Make monic
        lc = f[upoly_degree(f)]
        lc_inv = pow(lc, p - 2, p)
        f = {k: (v * lc_inv) % p for k, v in f.items()}
    return f

def upoly_eval(f, x, p):
    result = 0
    for i, c in f.items():
        result = (result + c * pow(x, i, p)) % p
    return result

def upoly_is_irreducible(f, p):
    """Test irreducibility of f in F_p[t] via distinct-degree factorization.
    f irreducible of degree d iff:
      - gcd(f, x^{p^i} - x) = 1 for i = 1, ..., d-1
      - f | (x^{p^d} - x)
    """
    d = upoly_degree(f)
    if d <= 0:
        return False
    if d == 1:
        return True

    # Make monic
    lc = f[d]
    lc_inv = pow(lc, p - 2, p)
    fm = {k: (v * lc_inv) % p for k, v in f.items()}

    # x^{p^i} mod f, built by repeated squaring mod f
    # Start with h = x
    h = {1: 1}  # h = x

    for i in range(1, d):
        # h = h^p mod f
        h = upoly_powmod(h, p, fm, p)
        # g = gcd(f, h - x)
        hx = upoly_sub(h, {1: 1}, p)
        g = upoly_gcd(dict(fm), hx, p)
        if upoly_degree(g) > 0:
            return False  # f has a factor of degree i

    return True

def upoly_powmod(base, exp, modulus, p):
    """base^exp mod modulus in F_p[t]."""
    result = {0: 1}
    b = dict(base)
    while exp > 0:
        if exp & 1:
            result = upoly_mod(upoly_mul(result, b, p), modulus, p)
        b = upoly_mod(upoly_mul(b, b, p), modulus, p)
        exp >>= 1
    return result

# ---- Bivariate → Univariate specialization ----

def specialize_s2(f_bivar, s2_val, p):
    """Substitute s_2 = s2_val in F_p[s_1, s_2] → F_p[s_1]."""
    result = {}
    for (a, b), c in f_bivar.items():
        val = (c * pow(s2_val, b, p)) % p
        if val:
            result[a] = (result.get(a, 0) + val) % p
            if result[a] == 0:
                del result[a]
    return result

def specialize_s1(f_bivar, s1_val, p):
    """Substitute s_1 = s1_val in F_p[s_1, s_2] → F_p[s_2]."""
    result = {}
    for (a, b), c in f_bivar.items():
        val = (c * pow(s1_val, a, p)) % p
        if val:
            result[b] = (result.get(b, 0) + val) % p
            if result[b] == 0:
                del result[b]
    return result

# ---- Companion matrix computation ----

def compute_remainder_poly(sigma_polys, n, p):
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

# ---- Main analysis ----

def analyze_irreducibility(n, p, w, c, num_trials=5):
    """For each random flat, compute r_0 - 1 and test irreducibility."""
    d = w - c
    k = n - w - c
    D = n - w + 1  # Corrected degree

    if k < 1 or d != 2:
        return

    print(f"\n{'='*70}")
    print(f"n={n}, p={p}, w={w}, c={c}, d={d}, k={k}")
    print(f"  D = n-w+1 = {D}")
    print(f"  Weil prediction: |V(r_0-1)| ≈ p ± {D}√p ≈ {p} ± {D*isqrt(p)}")

    random.seed(42)
    g = find_primitive_root(p)
    omega = pow(g, (p-1)//n, p)

    for trial in range(num_trials):
        # Random flat
        normals = [tuple(random.randint(0, p-1) for _ in range(w)) for _ in range(c)]
        offsets = [random.randint(0, p-1) for _ in range(c)]

        # Row-reduce
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

        # Build polynomial parameterization
        a_vals = [0]*w
        b_vals = [[0]*d for _ in range(w)]
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

        print(f"\n  Trial {trial}:")

        # Compute remainders
        remainders = compute_remainder_poly(sigma_polys, n, p)
        r0m1 = poly_sub(remainders[0], poly_const(1, p), p)

        deg_r0m1 = poly_degree(r0m1)
        deg_s1 = poly_s1_degree(r0m1)
        deg_s2 = poly_s2_degree(r0m1)
        nterms = len(r0m1)
        print(f"    r_0-1: total_deg={deg_r0m1}, s1_deg={deg_s1}, s2_deg={deg_s2}, #terms={nterms}")

        # --- Test 1: Count rational points |V(r_0-1)(F_p)| ---
        v_count = 0
        for s1 in range(p):
            for s2 in range(p):
                if poly_eval(r0m1, s1, s2, p) == 0:
                    v_count += 1

        weil_low = p - D * isqrt(p)
        weil_high = p + D * isqrt(p)
        in_weil = "YES" if weil_low <= v_count <= weil_high else "NO"
        print(f"    |V(r_0-1)(F_p)| = {v_count}")
        print(f"    Weil range: [{weil_low}, {weil_high}] → {in_weil}")

        # --- Test 2: Irreducibility of s_1-specializations ---
        irred_count = 0
        red_count = 0
        for s2_val in range(p):
            spec = specialize_s2(r0m1, s2_val, p)
            d_spec = upoly_degree(spec)
            if d_spec < 1:
                continue
            if upoly_is_irreducible(spec, p):
                irred_count += 1
            else:
                red_count += 1

        print(f"    s_2-specializations: {irred_count} irreducible, {red_count} reducible out of {p}")

        # If ANY specialization is irreducible with full degree,
        # then r_0-1 has no factor of positive s_2-degree
        full_deg_irred = 0
        for s2_val in range(p):
            spec = specialize_s2(r0m1, s2_val, p)
            if upoly_degree(spec) == deg_s1 and upoly_is_irreducible(spec, p):
                full_deg_irred += 1
                break  # one suffices for Hilbert

        if full_deg_irred > 0:
            print(f"    → Full-degree irreducible s_2-specialization EXISTS")
            print(f"      → r_0-1 has no factor of positive s_2-degree")

            # Now check: does it have a factor in F_p[s_1] alone?
            # Substitute s_1 = a for all a: if some gives irreducible in F_p[s_2],
            # then no factor in F_p[s_2] alone either → fully irreducible.
            for s1_val in range(p):
                spec1 = specialize_s1(r0m1, s1_val, p)
                if upoly_degree(spec1) == deg_s2 and upoly_is_irreducible(spec1, p):
                    print(f"      Full-degree irreducible s_1-specialization at s_1={s1_val}")
                    print(f"      → r_0-1 is ABSOLUTELY IRREDUCIBLE")
                    break
            else:
                print(f"      No full-degree irreducible s_1-specialization found!")
                # Maybe the s_1-degree drops or all specs factor
                print(f"      Checking all s_1-specializations...")
                for s1_val in range(min(p, 20)):
                    spec1 = specialize_s1(r0m1, s1_val, p)
                    d1 = upoly_degree(spec1)
                    is_irr = upoly_is_irreducible(spec1, p) if d1 > 0 else False
                    if d1 < deg_s2:
                        print(f"        s_1={s1_val}: degree DROPS to {d1}")
                    elif not is_irr:
                        print(f"        s_1={s1_val}: degree {d1}, REDUCIBLE")
        else:
            print(f"    → No full-degree irreducible specialization found!")
            # Check if degree drops for all specializations
            for s2_val in range(min(p, 10)):
                spec = specialize_s2(r0m1, s2_val, p)
                d_spec = upoly_degree(spec)
                is_irr = upoly_is_irreducible(spec, p) if d_spec > 0 else False
                print(f"        s_2={s2_val}: degree {d_spec}/{deg_s1}, irred={is_irr}")

        # --- Test 3: Number of absolutely irreducible components ---
        # Heuristic: if |V(F_p)| ≈ c·p for c components, then c ≈ v_count/p
        approx_components = v_count / max(p, 1)
        print(f"    Approx components ≈ |V|/p = {approx_components:.2f}")

        # --- Test 4: Check r_1 structure too ---
        r1 = remainders[1]
        v1_count = 0
        for s1 in range(p):
            for s2 in range(p):
                if poly_eval(r1, s1, s2, p) == 0:
                    v1_count += 1
        print(f"    |V(r_1)(F_p)| = {v1_count}, approx components ≈ {v1_count/p:.2f}")

        # --- Test 5: V(r_0-1) ∩ V(r_1) ---
        v01 = 0
        for s1 in range(p):
            for s2 in range(p):
                if poly_eval(r0m1, s1, s2, p) == 0 and poly_eval(r1, s1, s2, p) == 0:
                    v01 += 1
        print(f"    |V(r_0-1) ∩ V(r_1)| = {v01}")

        # --- Test 6: Newton polygon ---
        # The support (set of exponent pairs) determines much about irreducibility
        support = set(r0m1.keys())
        min_s1 = min(a for a, b in support)
        max_s1 = max(a for a, b in support)
        min_s2 = min(b for a, b in support)
        max_s2 = max(b for a, b in support)
        print(f"    Newton polygon: s1 ∈ [{min_s1},{max_s1}], s2 ∈ [{min_s2},{max_s2}]")

        # Check: is (0,0) in support (constant term)?
        has_const = (0,0) in r0m1
        # Check corner monomials
        corners = [(max_s1, 0), (0, max_s2), (max_s1, max_s2)]
        present = [(a,b) in support for a,b in corners]
        print(f"    Corners: ({max_s1},0)={present[0]}, (0,{max_s2})={present[1]}, ({max_s1},{max_s2})={present[2]}")
        print(f"    Constant term: {has_const}")


# ---- Run ----

print("=" * 70)
print("IRREDUCIBILITY ANALYSIS OF r_0(s_1, s_2) - 1")
print("=" * 70)

# Small cases where we can do exhaustive computation
test_cases = [
    (8, 11, 3, 1),   # w=3, c=1, d=2
    (10, 11, 4, 2),  # w=4, c=2, d=2
    (10, 13, 4, 2),
    (12, 13, 4, 2),
    (12, 13, 5, 3),  # w=5, c=3, d=2
]

for n, p, w, c in test_cases:
    analyze_irreducibility(n, p, w, c, num_trials=3)
