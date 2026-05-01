"""
irreducibility_explicit.py — Print FULL explicit r_0(σ)-1 polynomial
and analyze Newton polytope for Gao's irreducibility criterion.

Gao's theorem (2001): If Newton polytope P of f is integrally indecomposable
and all vertex coefficients are nonzero, then f is absolutely irreducible.

Key observation from data: leading form is ALWAYS σ_1^{n-w} · σ_w (single monomial).
The edge from (0,...,0) to (n-w,0,...,0,1) is in a PRIMITIVE direction
(gcd of coordinates = gcd(n-w, 1) = 1).
"""

import random
from math import comb, gcd as math_gcd

# ---- Multivariate polynomial arithmetic ----

def mpoly_const_w(c, p, w):
    c = c % p
    return {(0,)*w: c} if c else {}

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

def mpoly_degree(f):
    if not f: return -1
    return max(sum(e) for e in f.keys())

def compute_r0_full(n, p, w):
    sigma_polys = [mpoly_var(j, w) for j in range(w)]
    c_polys = [None] * w
    for j in range(w):
        sign = pow(-1, w - j + 1, p)
        c_polys[j] = mpoly_scale(sigma_polys[w - j - 1], sign, p)
    state = [mpoly_const_w(0, p, w) for _ in range(w)]
    state[0] = mpoly_const_w(1, p, w)
    for step in range(n):
        top = state[w - 1]
        new_state = [None] * w
        new_state[0] = mpoly_mul(top, c_polys[0], p)
        for j in range(1, w):
            new_state[j] = mpoly_add(state[j-1], mpoly_mul(top, c_polys[j], p), p)
        state = new_state
    return state

def print_poly(f, var_names, p):
    """Print polynomial with variable names."""
    if not f:
        print("    0")
        return

    items = sorted(f.items(), key=lambda x: (-sum(x[0]), x[0]))
    for exps, c in items:
        # Make c signed: c or c-p
        c_signed = c if c <= p//2 else c - p
        var_parts = []
        for i, e in enumerate(exps):
            if e > 0:
                if e == 1:
                    var_parts.append(var_names[i])
                else:
                    var_parts.append(f"{var_names[i]}^{e}")
        var_str = "·".join(var_parts) if var_parts else "1"
        if c_signed >= 0:
            print(f"    + {c_signed}·{var_str}")
        else:
            print(f"    - {-c_signed}·{var_str}")

def newton_polytope_analysis(f, w):
    """Analyze the Newton polytope of f."""
    if not f:
        return

    support = list(f.keys())
    print(f"\n  Support ({len(support)} points):")

    # Find vertices of convex hull (in w dimensions)
    # For small w, we can do this by checking extreme points in each direction
    # For our purposes, just list all support points

    # Check if polytope is "edge-like": all points on the line from origin to leading monomial
    total_degs = [sum(e) for e in support]
    max_deg = max(total_degs)
    leading = [e for e in support if sum(e) == max_deg]

    print(f"  Leading monomials (degree {max_deg}): {leading}")

    if len(leading) == 1:
        lead = leading[0]
        print(f"  SINGLE leading monomial: {lead}")

        # Check if direction is primitive
        g = 0
        for x in lead:
            g = math_gcd(g, x)
        if g == 1:
            print(f"  Direction is PRIMITIVE (gcd of coords = 1)")
        else:
            print(f"  Direction gcd = {g} (not primitive)")

        # Check: is the constant term nonzero?
        zero_exp = (0,) * w
        if zero_exp in f:
            print(f"  Constant term: {f[zero_exp]} (nonzero)")
        else:
            print(f"  NO constant term!")

        # For Gao's criterion: check if the polytope is indecomposable
        # Key sufficient condition: if P has exactly 2 vertices, one at origin
        # and one at a primitive lattice point, then P is indecomposable.
        #
        # More generally: if P is a simplex with primitive edge directions,
        # it's indecomposable.

        # Let's identify the convex hull vertices
        # For small support, check each point: is it a vertex?
        # (A point is a vertex if it's not a convex combination of others)
        # Simplified: just check extreme points in each coordinate direction
        vertices = []
        for dim in range(w):
            max_coord = max(e[dim] for e in support)
            if max_coord > 0:
                candidates = [e for e in support if e[dim] == max_coord]
                for c in candidates:
                    if c not in vertices:
                        vertices.append(c)
            min_coord = min(e[dim] for e in support)
            candidates = [e for e in support if e[dim] == min_coord]
            for c in candidates:
                if c not in vertices:
                    vertices.append(c)

        # Also add origin if in support
        if zero_exp in f and zero_exp not in vertices:
            vertices.append(zero_exp)

        print(f"  Extreme points: {vertices}")

        # Check edge decomposability for the leading edge
        # Edge from origin to lead: if lead = (a₁,...,a_w) with gcd = 1,
        # then the edge is indecomposable as a Minkowski summand.
        print(f"\n  EDGE from (0,...,0) to {lead}:")
        print(f"    gcd(coords) = {g}")
        if g == 1:
            print(f"    → Edge is in PRIMITIVE direction → indecomposable")
            print(f"    → By Gao's criterion: if this edge is a face of the")
            print(f"      Newton polytope AND both endpoints have nonzero coefficients,")
            print(f"      THEN r_0-1 is absolutely irreducible.")

            # Verify: is the edge (0,...,0)-(lead) actually a face of the polytope?
            # It's a face if there exists a supporting hyperplane containing both
            # endpoints but no other support points below it.
            # For the edge to be a face, we need a linear functional L such that
            # L(origin) = L(lead) = 0 and L(x) > 0 for all other support points.
            # Or more precisely, L takes the SAME value on origin and lead,
            # and strictly higher on all other support points.
            # Since L(0) = 0 always, we need L(lead) = 0 and L(x) > 0 for x not on the edge.

            # The edge has direction lead = (a₁,...,a_w). Points on the edge are
            # t·lead for t ∈ [0,1]. Support points on the edge are those of the
            # form (t·a₁,...,t·a_w) for some rational t.

            on_edge = []
            off_edge = []
            for e in support:
                # Check if e is a scalar multiple of lead
                # e = t * lead iff e[i]/lead[i] is the same for all i where lead[i] > 0
                # and e[i] = 0 where lead[i] = 0
                is_on = True
                t_val = None
                for i in range(w):
                    if lead[i] == 0:
                        if e[i] != 0:
                            is_on = False
                            break
                    else:
                        if t_val is None:
                            t_val = e[i] / lead[i]
                        elif abs(e[i] / lead[i] - t_val) > 1e-10:
                            is_on = False
                            break
                if is_on and t_val is not None and 0 <= t_val <= 1:
                    on_edge.append((e, t_val))
                else:
                    off_edge.append(e)

            print(f"    Points on edge: {[e for e, t in on_edge]}")
            print(f"    Points off edge: {off_edge}")

            if len(off_edge) > 0:
                # Need to check if there's a supporting hyperplane
                # This is equivalent to: all off-edge points are on one side
                # of the affine span of the edge.
                # The edge lives in the line {t·lead : t ∈ R}.
                # A supporting hyperplane is H = {x : L(x) = 0} with L(lead) = 0.
                # We need all off-edge points to have L(x) > 0 (or all < 0).
                print(f"    Need to verify edge is a face of the polytope...")
                # For w=2: straightforward
                # For w≥3: need to solve LP
                # Skip formal check, report empirically
            else:
                print(f"    ALL support points on edge → polytope IS the edge → IRREDUCIBLE")


# ---- Run ----

print("=" * 70)
print("EXPLICIT r_0(σ) - 1 POLYNOMIALS")
print("=" * 70)

# w=3 (3 variables)
var3 = ["σ₁", "σ₂", "σ₃"]
var4 = ["σ₁", "σ₂", "σ₃", "σ₄"]

for n, p, w in [(6, 7, 3), (8, 11, 3), (8, 13, 3), (10, 11, 3), (10, 13, 3)]:
    print(f"\n{'='*60}")
    print(f"n={n}, p={p}, w={w}, D={n-w+1}")

    remainders = compute_r0_full(n, p, w)
    r0m1 = mpoly_sub(remainders[0], mpoly_const_w(1, p, w), p)
    var_names = var3 if w == 3 else var4

    print(f"\n  r_0(σ) - 1 =")
    print_poly(r0m1, var_names, p)

    # Also print r_1
    r1 = remainders[1]
    print(f"\n  r_1(σ) =")
    print_poly(r1, var_names, p)

    newton_polytope_analysis(r0m1, w)

# w=4
for n, p, w in [(8, 11, 4), (10, 11, 4), (10, 13, 4)]:
    print(f"\n{'='*60}")
    print(f"n={n}, p={p}, w={w}, D={n-w+1}")

    remainders = compute_r0_full(n, p, w)
    r0m1 = mpoly_sub(remainders[0], mpoly_const_w(1, p, w), p)
    var_names = var4

    print(f"\n  r_0(σ) - 1 =")
    print_poly(r0m1, var_names, p)

    # Also print r_1
    r1 = remainders[1]
    print(f"\n  r_1(σ) =")
    print_poly(r1, var_names, p)

    newton_polytope_analysis(r0m1, w)

# ---- Check: is r_0(σ)-1 independent of p? ----
print(f"\n\n{'='*70}")
print("p-INDEPENDENCE TEST: same n,w, different p")
print("="*70)

for n, w in [(8, 3), (10, 3), (10, 4)]:
    print(f"\n  n={n}, w={w}:")
    # Compare r_0 for different p
    polys = {}
    for p in [11, 13, 17, 19, 23, 29, 31]:
        if p <= n:
            continue
        remainders = compute_r0_full(n, p, w)
        r0m1 = mpoly_sub(remainders[0], mpoly_const_w(1, p, w), p)
        # Represent coefficients as "signed" integers in [-p/2, p/2]
        signed = {}
        for k, v in r0m1.items():
            sv = v if v <= p//2 else v - p
            signed[k] = sv
        polys[p] = signed
        print(f"    p={p}: {dict(sorted(signed.items(), key=lambda x: (-sum(x[0]), x[0])))}")

    # Check if all are "the same" (same signed coefficients)
    # This would mean the polynomial is defined over Z, not just F_p
    p_list = sorted(polys.keys())
    if len(p_list) >= 2:
        same = True
        for p2 in p_list[1:]:
            if polys[p_list[0]] != polys[p2]:
                same = False
                break
        if same:
            print(f"    → SAME polynomial over Z for all tested p!")
        else:
            print(f"    → Polynomial differs between p values")
            # Show which coefficients differ
            all_keys = set()
            for poly in polys.values():
                all_keys.update(poly.keys())
            for k in sorted(all_keys, key=lambda x: (-sum(x), x)):
                vals = {p: polys[p].get(k, 0) for p in p_list}
                if len(set(vals.values())) > 1:
                    print(f"      {k}: {vals}")
