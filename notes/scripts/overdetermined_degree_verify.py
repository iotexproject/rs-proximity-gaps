"""
overdetermined_degree_verify.py — Verify the actual degree of r_i(t)
as a function of the flat parameter.

Claim: degree = n - w + 1, NOT n - w as stated in paper.tex Theorem 9.4.

Verification method:
1. For d=1 (univariate): compute r_i(t) for many (n, w, p) and check degree
2. For d=2 (bivariate): check total degree from previous results
3. Count division steps explicitly
"""

import random

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

def compute_remainder_univariate(sigma_func, n, p, w):
    """Compute x^n mod Λ(x) where σ_j = sigma_func(j, t) are polynomials in t.

    sigma_func(j, t) returns σ_{j+1}(t) as a list [a_0, a_1, ..., a_d].
    Returns w lists of polynomial coefficients in t.
    """
    # Represent each coefficient as a polynomial in t
    # poly_add, poly_mul for univariate F_p[t]

    def padd(f, g):
        r = [0] * max(len(f), len(g))
        for i, v in enumerate(f): r[i] = (r[i] + v) % p
        for i, v in enumerate(g): r[i] = (r[i] + v) % p
        while r and r[-1] == 0: r.pop()
        return r or [0]

    def pmul(f, g):
        if f == [0] or g == [0]:
            return [0]
        r = [0] * (len(f) + len(g) - 1)
        for i, a in enumerate(f):
            for j, b in enumerate(g):
                r[i+j] = (r[i+j] + a * b) % p
        while r and r[-1] == 0: r.pop()
        return r or [0]

    def pscale(f, c):
        if c % p == 0: return [0]
        return [(x * c) % p for x in f] or [0]

    # Get σ polynomials
    sigmas = [sigma_func(j) for j in range(w)]

    # Precompute c_j: x^w ≡ Σ c_j x^j mod Λ(x)
    # c_j = (-1)^{w-j+1} σ_{w-j}
    c_polys = [[0]] * w
    for j in range(w):
        sign = pow(-1, w - j + 1, p)
        c_polys[j] = pscale(sigmas[w - j - 1], sign)

    # Initial state: (1, 0, ..., 0)
    state = [[0]] * w
    state[0] = [1]

    for step in range(n):
        top = state[w-1]
        new_state = [None] * w
        new_state[0] = pmul(top, c_polys[0])
        for j in range(1, w):
            new_state[j] = padd(state[j-1], pmul(top, c_polys[j]))
        state = new_state

    return state

print("Degree verification: r_i(t) for d=1 flats")
print("="*60)

# For d=1: flat parameterized by t, σ_j = a_j + t · b_j

for n, p, w in [(6, 7, 2), (6, 7, 3), (8, 11, 3), (10, 11, 3), (10, 11, 4),
                (12, 13, 4), (12, 13, 5), (14, 17, 5), (16, 17, 5), (20, 23, 6)]:
    c = w - 1  # d = 1
    k = n - w - c
    D = n - w

    if k < 1:
        continue

    random.seed(n * 100 + p * 10 + w)

    # Random affine-linear σ_j(t) = a_j + t · b_j
    a_vals = [random.randint(0, p-1) for _ in range(w)]
    b_vals = [random.randint(0, p-1) for _ in range(w)]

    def sigma_func(j):
        return [a_vals[j] % p, b_vals[j] % p]

    remainders = compute_remainder_univariate(sigma_func, n, p, w)

    degrees = [len(r) - 1 if r != [0] else -1 for r in remainders]

    print(f"n={n}, p={p}, w={w}: D=n-w={D}, actual deg(r_i) = {degrees}")

    # Check: is degree n-w or n-w+1?
    max_deg = max(degrees)
    if max_deg == D:
        result = "deg = D = n-w ✓ (paper correct)"
    elif max_deg == D + 1:
        result = "deg = D+1 = n-w+1 ✗ (paper off by 1)"
    else:
        result = f"deg = {max_deg} ??? (unexpected)"
    print(f"  → {result}")

print("\n" + "="*60)
print("Division step count verification")
print("="*60)

# Manual count: x^n mod Λ(x) with deg Λ = w
# Start at degree n, reduce to degree < w
# Each step: degree decreases by 1 (subtract leading coeff · x^{d-w} · Λ)
# Steps: n - (w-1) = n - w + 1

for n, w in [(6, 2), (6, 3), (8, 3), (10, 3), (10, 4), (12, 4), (20, 6)]:
    steps = n - (w - 1)
    print(f"n={n}, w={w}: steps = n-(w-1) = {steps}, paper says n-w = {n-w}")
    print(f"  Correct degree bound: {steps} (each step adds degree 1 in σ)")
