"""
irreducibility_sigma_space.py — Test irreducibility of r_0(σ_1,...,σ_w) - 1
in the FULL σ-space F_p[σ_1,...,σ_w].

Key question: Is r_0(σ) - 1 irreducible in F_p[σ_1,...,σ_w]?
If YES → Bertini theorem → restriction to generic 2-plane is irreducible
→ Weil bound → |V(r_0-1) ∩ 2-plane| ≈ p → intersection with V(r_1) gives M = O(1)

We use multivariate polynomial representation: dict of tuples → coeff.
"""

import random
from math import comb, isqrt
from itertools import product as iproduct

# ---- Multivariate polynomial arithmetic in F_p[σ_1,...,σ_w] ----
# Exponent vector: tuple of w non-negative integers

def mpoly_zero():
    return {}

def mpoly_const(c, p):
    c = c % p
    if c == 0: return {}
    w = 0  # will be determined by context
    return {}  # use explicit zero-tuple

def mpoly_const_w(c, p, w):
    c = c % p
    if c == 0: return {}
    return {(0,)*w: c}

def mpoly_var(idx, w):
    """σ_{idx+1} as polynomial."""
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

def mpoly_eval(f, vals, p):
    """Evaluate f at σ_1=vals[0], ..., σ_w=vals[w-1]."""
    r = 0
    for exps, c in f.items():
        term = c
        for i, e in enumerate(exps):
            if e > 0:
                term = (term * pow(vals[i], e, p)) % p
        r = (r + term) % p
    return r

def mpoly_nterms(f):
    return len(f)

# ---- Companion matrix in σ-space ----

def compute_r0_full(n, p, w):
    """Compute r_0(σ_1,...,σ_w) as polynomial in F_p[σ_1,...,σ_w].

    Uses companion matrix recurrence for x^n mod Λ(x).
    Λ(x) = x^w - σ_1 x^{w-1} + σ_2 x^{w-2} - ... + (-1)^w σ_w

    Recurrence coefficients: c_j = (-1)^{w-j+1} σ_{w-j} for j=0,...,w-1
    (these are the coefficients of x^w ≡ c_0 + c_1 x + ... + c_{w-1} x^{w-1} mod Λ)
    """
    # σ_j polynomial: just the j-th variable (0-indexed: σ_{j+1} = var j)
    sigma_polys = [mpoly_var(j, w) for j in range(w)]

    # Recurrence coefficients
    c_polys = [None] * w
    for j in range(w):
        sign = pow(-1, w - j + 1, p)
        c_polys[j] = mpoly_scale(sigma_polys[w - j - 1], sign, p)

    # State: coefficients of x^0 = 1
    state = [mpoly_const_w(0, p, w) for _ in range(w)]
    state[0] = mpoly_const_w(1, p, w)

    for step in range(n):
        top = state[w - 1]
        new_state = [None] * w
        new_state[0] = mpoly_mul(top, c_polys[0], p)
        for j in range(1, w):
            new_state[j] = mpoly_add(state[j-1], mpoly_mul(top, c_polys[j], p), p)
        state = new_state

        if (step + 1) % 5 == 0:
            max_terms = max(mpoly_nterms(s) for s in state)

    return state  # [r_0, r_1, ..., r_{w-1}]

# ---- Univariate irreducibility test ----

def upoly_degree(f):
    if not f: return -1
    return max(f.keys())

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

def upoly_mul(f, g, p):
    r = {}
    for i, a in f.items():
        for j, b in g.items():
            k = i + j
            r[k] = (r.get(k, 0) + a * b) % p
            if r[k] == 0: del r[k]
    return r

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

def upoly_sub(f, g, p):
    r = dict(f)
    for k, v in g.items():
        r[k] = (r.get(k, 0) - v) % p
        if r[k] == 0: del r[k]
    return r

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

# ---- Specialization: fix all but one variable ----

def specialize_to_univariate(f_mpoly, var_idx, fixed_vals, p, w):
    """Fix all variables except var_idx. Returns univariate polynomial in that variable."""
    result = {}
    for exps, c in f_mpoly.items():
        term = c
        for i in range(w):
            if i == var_idx:
                continue
            if exps[i] > 0:
                term = (term * pow(fixed_vals[i], exps[i], p)) % p
        if term:
            deg = exps[var_idx]
            result[deg] = (result.get(deg, 0) + term) % p
            if result[deg] == 0:
                del result[deg]
    return result

# ---- Main ----

def analyze_full_sigma(n, p, w):
    """Compute r_0 - 1 in F_p[σ_1,...,σ_w] and test irreducibility."""
    D = n - w + 1
    print(f"\n{'='*70}")
    print(f"n={n}, p={p}, w={w}, D={D}")
    print(f"Computing r_0(σ_1,...,σ_{w}) in F_{p}[σ_1,...,σ_{w}]...")

    remainders = compute_r0_full(n, p, w)
    r0 = remainders[0]
    r0m1 = mpoly_sub(r0, mpoly_const_w(1, p, w), p)

    deg = mpoly_degree(r0m1)
    nterms = mpoly_nterms(r0m1)
    print(f"  r_0-1: degree={deg}, #terms={nterms}")

    # Degree in each variable
    for j in range(w):
        max_deg_j = max((e[j] for e in r0m1.keys()), default=0)
        print(f"  deg_σ_{j+1} = {max_deg_j}")

    # Count F_p-rational zeros (only feasible for small p^w)
    if p**w <= 100000:
        zero_count = 0
        for vals in iproduct(range(p), repeat=w):
            if mpoly_eval(r0m1, vals, p) == 0:
                zero_count += 1
        print(f"  |V(r_0-1)(F_p)| = {zero_count}")
        print(f"  Expected for irreducible hypersurface: ≈ p^{w-1} = {p**(w-1)}")
        print(f"  Ratio: {zero_count / p**(w-1):.3f}")
        # Lang-Weil: |V(F_p)| = p^{w-1} + O(p^{w-3/2}) for irreducible degree-D hypersurface
    else:
        print(f"  p^w = {p**w} too large for exhaustive count")
        zero_count = None

    # Test irreducibility via specialization
    # Fix all variables except σ_j, sweep σ_j
    print(f"\n  Irreducibility test via specialization:")

    for var_idx in range(w):
        irred_count = 0
        total = 0
        full_deg_irred = False
        max_deg_var = max((e[var_idx] for e in r0m1.keys()), default=0)

        # Sample random specializations
        rng = random.Random(42 + var_idx)
        num_samples = min(50, p**(w-1))

        for _ in range(num_samples):
            fixed = [rng.randint(0, p-1) for _ in range(w)]
            spec = specialize_to_univariate(r0m1, var_idx, fixed, p, w)
            d_spec = upoly_degree(spec)
            total += 1
            if d_spec > 0 and upoly_is_irreducible(spec, p):
                irred_count += 1
                if d_spec == max_deg_var:
                    full_deg_irred = True

        print(f"    σ_{var_idx+1}: max_deg={max_deg_var}, irred={irred_count}/{total}, full_deg_irred={full_deg_irred}")

    # Also test: are r_0-1 and r_j coprime in F_p[σ_1,...,σ_w]?
    # Indirect test: count |V(r_0-1, r_j)(F_p)|
    if p**w <= 100000:
        print(f"\n  Intersection counts in full σ-space:")
        for j in range(1, w):
            rj = remainders[j]
            inter = 0
            for vals in iproduct(range(p), repeat=w):
                if mpoly_eval(r0m1, vals, p) == 0 and mpoly_eval(rj, vals, p) == 0:
                    inter += 1
            print(f"    |V(r_0-1, r_{j})(F_p)| = {inter}")
            print(f"    Expected (2 independent degree-{D} hypers): ≈ p^{w-2} = {p**(w-2)}")

        # Count actual valid subsets (all conditions)
        all_inter = 0
        for vals in iproduct(range(p), repeat=w):
            if mpoly_eval(r0m1, vals, p) == 0:
                ok = True
                for j in range(1, w):
                    if mpoly_eval(remainders[j], vals, p) != 0:
                        ok = False
                        break
                if ok:
                    all_inter += 1
        print(f"    |V(all)(F_p)| = {all_inter} = C({n},{w}) = {comb(n,w)}")

    # Structural analysis: leading form
    top_deg = mpoly_degree(r0m1)
    leading = {k: v for k, v in r0m1.items() if sum(k) == top_deg}
    print(f"\n  Leading form (degree {top_deg}): {mpoly_nterms(leading)} terms")
    if mpoly_nterms(leading) <= 15:
        for k, v in sorted(leading.items()):
            var_str = "*".join(f"σ_{i+1}^{e}" for i, e in enumerate(k) if e > 0)
            print(f"    {v} * {var_str}")


# ---- Run ----
print("="*70)
print("r_0 - 1 IN FULL σ-SPACE")
print("="*70)

# w=3 cases (3 variables, manageable)
for n, p in [(6, 7), (8, 11), (8, 13), (10, 11), (10, 13)]:
    w = 3
    if n > w:
        analyze_full_sigma(n, p, w)

# w=4 cases (4 variables, p^4 can be large)
for n, p in [(8, 11), (10, 11), (10, 13)]:
    w = 4
    if n > w:
        analyze_full_sigma(n, p, w)
