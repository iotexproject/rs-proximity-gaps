"""
overdetermined_coprime.py — Compute r_i(s_1, s_2) as EXPLICIT polynomials
in F_p[s_1, s_2] and test coprimality.

KEY QUESTION: Is gcd(r_0 - 1, r_1) = 1 in F_p[s_1, s_2]?
If yes: the intersection V(r_0-1, r_1) is 0-dimensional of degree ≤ D^2
and the F_p-rational points are bounded by Weil estimates.

Polynomial representation: dict {(a, b): coeff} where s_1^a * s_2^b has coefficient coeff.
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

# ---- Polynomial arithmetic in F_p[s_1, s_2] ----

def poly_zero():
    return {}

def poly_const(c, p):
    c = c % p
    if c == 0:
        return {}
    return {(0,0): c}

def poly_var(idx):
    """s_1 = poly_var(0), s_2 = poly_var(1)"""
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
    """Total degree."""
    if not f:
        return -1
    return max(a + b for a, b in f.keys())

def poly_eval(f, s1, s2, p):
    """Evaluate polynomial at (s1, s2) mod p."""
    result = 0
    for (a, b), c in f.items():
        result = (result + c * pow(s1, a, p) * pow(s2, b, p)) % p
    return result

def poly_is_zero(f):
    return len(f) == 0

def poly_leading_terms(f, show=3):
    """Show the highest-degree terms."""
    if not f:
        return "0"
    items = sorted(f.items(), key=lambda x: -(x[0][0]+x[0][1]))
    parts = []
    for (a, b), c in items[:show]:
        if a == 0 and b == 0:
            parts.append(str(c))
        else:
            s = f"{c}" if c != 1 else ""
            if a > 0:
                s += f"s1^{a}" if a > 1 else "s1"
            if b > 0:
                s += f"s2^{b}" if b > 1 else "s2"
            parts.append(s)
    return " + ".join(parts) + (" + ..." if len(items) > show else "")

# ---- Companion matrix computation with polynomial entries ----

def compute_remainder_poly(sigma_polys, n, p, d=2):
    """Compute x^n mod Λ(x) where σ_j are polynomials in (s_1, ..., s_d).

    sigma_polys[j] = polynomial for σ_{j+1} (j=0,...,w-1)
    Returns list of w polynomials [r_0, r_1, ..., r_{w-1}].

    Recurrence: state represents a_0 + a_1 x + ... + a_{w-1} x^{w-1}
    Multiply by x mod Λ(x):
      new[0] = old[w-1] * (-1)^{w+1} σ_w
      new[j] = old[j-1] + old[w-1] * (-1)^{w-j+1} σ_{w-j}  (j ≥ 1)
    """
    w = len(sigma_polys)

    # Precompute the coefficients c_j = (-1)^{w-j+1} σ_{w-j}
    # x^w ≡ c_0 + c_1 x + ... + c_{w-1} x^{w-1} mod Λ(x)
    c_polys = [None] * w
    for j in range(w):
        sign = pow(-1, w - j + 1, p)
        c_polys[j] = poly_scale(sigma_polys[w - j - 1], sign, p)

    # Initial state: x^0 = (1, 0, ..., 0)
    state = [poly_const(0, p) for _ in range(w)]
    state[0] = poly_const(1, p)

    for step in range(n):
        top = state[w - 1]  # coefficient of x^{w-1}
        new_state = [None] * w
        new_state[0] = poly_mul(top, c_polys[0], p)
        for j in range(1, w):
            new_state[j] = poly_add(state[j-1], poly_mul(top, c_polys[j], p), p)
        state = new_state

        # Progress for large n
        if n >= 20 and step % 5 == 0:
            max_terms = max(len(s) for s in state)
            max_deg = max(poly_degree(s) for s in state)
            # Don't print — just track

    return state

def analyze_coprime(n, p, w, c, num_trials=5):
    """Compute r_i as explicit polynomials and check structure."""
    d = w - c
    k = n - w - c
    D = n - w

    if k < 1 or d != 2:
        return

    print(f"\n{'='*70}")
    print(f"n={n}, p={p}, w={w}, c={c}, d={d}, k={k}, D={D}")
    print(f"  Bézout bound: D^d = {D**d}")

    random.seed(42)

    for trial in range(num_trials):
        # Random flat: c conditions on w-dimensional σ-space
        normals = [tuple(random.randint(0, p-1) for _ in range(w)) for _ in range(c)]
        offsets = [random.randint(0, p-1) for _ in range(c)]

        # Row-reduce to get parameterization σ_j = a_j + s_1 b_{j,0} + s_2 b_{j,1}
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
            a_vals[fv] = 0
            b_vals[fv][fi] = 1

        # Create σ_j as polynomials in (s_1, s_2)
        sigma_polys = []
        for j in range(w):
            poly = poly_const(a_vals[j], p)
            for i in range(d):
                if b_vals[j][i] % p != 0:
                    vi = poly_var(i)
                    poly = poly_add(poly, poly_scale(vi, b_vals[j][i], p), p)
            sigma_polys.append(poly)

        print(f"\n  Trial {trial}:")
        for j in range(w):
            print(f"    σ_{j+1} = {poly_leading_terms(sigma_polys[j], 5)}")

        # Compute r_0, r_1, ..., r_{w-1} as polynomials
        print(f"    Computing x^{n} mod Λ(x) in F_{p}[s_1,s_2]...")
        remainders = compute_remainder_poly(sigma_polys, n, p, d)

        for j in range(w):
            deg = poly_degree(remainders[j])
            nterms = len(remainders[j])
            print(f"    r_{j}: degree={deg}, #terms={nterms}")
            if deg <= 8:
                print(f"         = {poly_leading_terms(remainders[j], 6)}")

        # r_0 - 1
        r0m1 = poly_sub(remainders[0], poly_const(1, p), p)
        r1 = remainders[1]

        deg_r0m1 = poly_degree(r0m1)
        deg_r1 = poly_degree(r1)
        print(f"    deg(r_0-1) = {deg_r0m1}, deg(r_1) = {deg_r1}")

        # Verify by brute-force evaluation: count zeros
        zeros_r0m1 = 0
        zeros_r1 = 0
        zeros_both = 0
        zeros_all = 0

        for s1 in range(p):
            for s2 in range(p):
                vals = [poly_eval(remainders[j], s1, s2, p) for j in range(w)]
                if vals[0] == 1:
                    zeros_r0m1 += 1
                if vals[1] == 0:
                    zeros_r1 += 1
                if vals[0] == 1 and vals[1] == 0:
                    zeros_both += 1
                if vals[0] == 1 and all(v == 0 for v in vals[1:]):
                    zeros_all += 1

        print(f"    |V(r_0-1)| = {zeros_r0m1}")
        print(f"    |V(r_1)|   = {zeros_r1}")
        print(f"    |V(r_0-1,r_1)| = {zeros_both}")
        print(f"    |V(all)|   = {zeros_all} = M")

        # Check: are r_0-1 and r_1 coprime?
        # Simple test: if they share a common factor f, then
        # |V(f)| ≤ |V(r_0-1) ∩ V(r_1)| = zeros_both
        # If f has degree ≥ 1, then |V(f)| ≥ p - O(√p) (Weil for irreducible)
        # or |V(f)| ≥ 1 (for any nonzero polynomial)
        #
        # So if zeros_both < p/2, they likely DON'T share a degree-1 factor.
        # If zeros_both < √(p), they likely don't share ANY common factor.
        if zeros_both <= D:
            print(f"    → |V_01| ≤ D={D}: COPRIME (0-dim intersection)")
        else:
            print(f"    → |V_01| > D: may share common factor!")

        # Check the ratio |V_01| / (|V(r_0-1)| * |V(r_1)| / p^2)
        expected_random = zeros_r0m1 * zeros_r1 / p**2
        print(f"    Random expectation: {expected_random:.2f}, actual: {zeros_both}, ratio: {zeros_both/max(expected_random, 0.01):.2f}")

        # Leading monomials analysis
        if deg_r0m1 > 0 and deg_r1 > 0:
            # Extract degree-D part of r_0-1
            top_r0 = {k: v for k, v in r0m1.items() if k[0]+k[1] == deg_r0m1}
            top_r1 = {k: v for k, v in r1.items() if k[0]+k[1] == deg_r1}
            print(f"    Leading form of r_0-1: {poly_leading_terms(top_r0, 10)}")
            print(f"    Leading form of r_1:   {poly_leading_terms(top_r1, 10)}")

            # Check if leading forms are proportional (would mean parallel asymptotes)
            if len(top_r0) > 0 and len(top_r1) > 0:
                # Normalize by first coefficient
                k0, v0 = next(iter(top_r0.items()))
                k1, v1 = next(iter(top_r1.items()))
                inv_v0 = pow(v0, p-2, p)
                inv_v1 = pow(v1, p-2, p)
                norm_r0 = {k: (v * inv_v0) % p for k, v in top_r0.items()}
                norm_r1 = {k: (v * inv_v1) % p for k, v in top_r1.items()}
                if norm_r0 == norm_r1:
                    print(f"    !! Leading forms are PROPORTIONAL")
                else:
                    print(f"    Leading forms are NOT proportional → coprime at infinity")

# Test small cases
for n, p, w in [(10, 11, 4), (10, 13, 4), (12, 13, 4)]:
    c = w - 2
    if n - w - c >= 1:
        analyze_coprime(n, p, w, c, num_trials=3)

# Also test d=2 with larger w
for n, p, w in [(12, 13, 5), (14, 17, 5)]:
    c = w - 2
    if n - w - c >= 1:
        analyze_coprime(n, p, w, c, num_trials=2)
