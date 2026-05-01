"""g3_minpoly_factor.py — for count > 0 supports, factor the bad-alpha
minimal polynomial over F_q. PR #373 predicts low-degree factors
correspond to cyclotomic orbits.

Approach:
  bad-α set B = {α_1, ..., α_c}, count = c.
  Build polynomial p(α) = prod_i (α - α_i) ∈ F_q[α] of degree c.
  Factor p over F_q (using simple pollard/berlekamp-style trial divisions).
  Report factor degrees → orbit structure.
"""
import sys, os, math, random
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from collections import Counter
from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft_local(fhat, L, p):
    n = len(L)
    f = [0] * n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j] != 0:
                v = (v + fhat[j] * pow(x, j, p)) % p
        f[i] = v
    return f


def bad_alpha_full(positions, coeffs, p, n0, k0, threshold,
                   L0, L1_arr, all_T, D1, inv_D1):
    fhat = [0] * n0
    for ps, c in zip(positions, coeffs):
        fhat[ps] = c
    f = evaluate_dft_local(fhat, L0, p)
    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)
    n1 = len(L1_arr)
    k1 = k0 // 2

    bad = []
    for alpha in range(p):
        fold = (f_e_arr + alpha * f_o_arr) % p
        extras = batched_extras(all_T, fold, L1_arr, D1, inv_D1, p)
        d1 = n1 - k1 - int(extras.max())
        if d1 <= threshold:
            bad.append(alpha)
    return bad


# Polynomial arithmetic over F_p
def poly_mul(a, b, p):
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x == 0: continue
        for j, y in enumerate(b):
            r[i+j] = (r[i+j] + x*y) % p
    return r


def poly_from_roots(roots, p):
    poly = [1]
    for r in roots:
        poly = poly_mul(poly, [(-r) % p, 1], p)
    return poly


def poly_normalize(a, p):
    while len(a) > 1 and a[-1] == 0:
        a = a[:-1]
    return a


def poly_div(a, b, p):
    """a / b → (q, r). a, b lowest-degree-first."""
    a = poly_normalize(a, p)[:]
    b = poly_normalize(b, p)
    if len(b) == 1 and b[0] == 0:
        raise ZeroDivisionError
    inv_lead = pow(b[-1], p - 2, p)
    q = [0] * max(0, len(a) - len(b) + 1)
    while len(a) >= len(b):
        coef = a[-1] * inv_lead % p
        deg_diff = len(a) - len(b)
        q[deg_diff] = coef
        for i, bi in enumerate(b):
            a[i + deg_diff] = (a[i + deg_diff] - coef * bi) % p
        a = poly_normalize(a, p)
    return q, a


def poly_gcd(a, b, p):
    a = poly_normalize(a, p)[:]
    b = poly_normalize(b, p)[:]
    while len(b) > 1 or (len(b) == 1 and b[0] != 0):
        _, r = poly_div(a, b, p)
        a, b = b, r
    if a[-1] != 1:
        inv = pow(a[-1], p - 2, p)
        a = [(c * inv) % p for c in a]
    return a


def poly_mod_pow(base, exp, mod_poly, p):
    """base^exp mod mod_poly."""
    result = [1]
    base = poly_div(base, mod_poly, p)[1]
    while exp > 0:
        if exp & 1:
            result = poly_div(poly_mul(result, base, p), mod_poly, p)[1]
        base = poly_div(poly_mul(base, base, p), mod_poly, p)[1]
        exp >>= 1
    return result


def factor_squarefree_distinct_degree(f, p):
    """Distinct-degree factorization of squarefree poly f.
    Returns dict {d: [(degree d factor), ...]} where d divides total degree.
    Approximate: using gcd with x^{p^d} - x.
    """
    factors = {}
    h = [0, 1]  # X
    g = f
    d = 1
    while len(g) - 1 >= 2 * d:
        h = poly_mod_pow(h, p, g, p)  # h = X^{p^d} mod g
        # gcd(h - X, g) gives product of degree-d factors
        h_minus_x = h[:]
        if len(h_minus_x) >= 2:
            h_minus_x[1] = (h_minus_x[1] - 1) % p
        else:
            while len(h_minus_x) < 2: h_minus_x.append(0)
            h_minus_x[1] = (h_minus_x[1] - 1) % p
        gd = poly_gcd(h_minus_x, g, p)
        if len(gd) > 1:
            factors[d] = (len(gd) - 1) // d  # number of degree-d irreducible factors
            g, _ = poly_div(g, gd, p)
        d += 1
    if len(g) > 1:
        factors[len(g) - 1] = 1
    return factors


def main():
    p = 1153
    n0, k0 = 32, 8
    n1, k1 = 16, 4
    threshold = n1 - int(math.isqrt(k1 * n1))  # = 8

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L1 = chain[1][0]
    L1_arr = np.array(L1, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    all_T = np.array(list(combinations(range(n1), k1)), dtype=np.int64)

    # representatives: count=9 (both σ-classes), count=8, biquadratic count=4, generic count=4/5
    samples = [
        ('count=9 σ=()',   (8, 9, 20)),
        ('count=9 σ=(9)',  (9, 20, 21)),
        ('count=9 σ=(9)',  (13, 16, 17)),
        ('count=8',        (8, 20, 21)),
        ('count=4 biquadr (a even)', (8, 17, 24)),
        ('count=5 biquadr (a odd)',  (9, 16, 25)),
        ('count=6',        (8, 16, 25)),
        ('count=5',        (8, 9, 16)),
        ('count=4',        (8, 16, 17)),
    ]

    rng = random.Random(2026)
    print(f"=== Bad-alpha minimal polynomial factorization at q={p}, ({n0},{k0}) ===\n")

    for label, sup in samples:
        # 2 trials, factor the min-poly
        for trial in range(2):
            coeffs = tuple(rng.randrange(1, p) for _ in range(3))
            bad = bad_alpha_full(sup, coeffs, p, n0, k0, threshold,
                                  L0, L1_arr, all_T, D1, inv_D1)
            cnt = len(bad)
            if cnt == 0 or cnt > 32:
                print(f"  {label} sup={sup} trial={trial} coefs={coeffs}: count={cnt}, skip factoring")
                continue
            # build polynomial
            pol = poly_from_roots(bad, p)
            # for distinct-degree factorization, need squarefree (it should be since roots are distinct)
            try:
                deg_factors = factor_squarefree_distinct_degree(pol, p)
            except Exception as e:
                deg_factors = f"error: {e}"
            # σ_1 .. σ_3
            sigma1 = sum(bad) % p
            sigma2 = sum(bad[i]*bad[j] for i in range(len(bad)) for j in range(i+1,len(bad))) % p
            sigma3 = sum(bad[i]*bad[j]*bad[k] for i in range(len(bad)) for j in range(i+1,len(bad)) for k in range(j+1,len(bad))) % p
            print(f"  {label} sup={sup} trial={trial}: count={cnt}, "
                  f"σ_1={sigma1}, σ_2={sigma2}, σ_3={sigma3}, "
                  f"degree-factor profile = {deg_factors}")
        print()


if __name__ == "__main__":
    main()
