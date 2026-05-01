"""Test SUBSTITUTION PRINCIPLE: (a, b) at (n, k) ≡ (a/d, b/d) at (n/d, k/d)
where d = gcd(a, b, n) and d | k.

For (4, 6) at (8, 2) with d = gcd(4, 6, 8) = 2: should map to (2, 3) at (4, 1).
For (3k/2, 2k) at (4k, k) with d = k/2: maps to (3, 4) at (8, 2).
For (4, 8) at (16, 4) with d = 4: maps to (1, 2) at (4, 1).

Verify by computing eliminator at the reduced scale and comparing.
"""
import sympy as sp


def eliminator(n, k, a, b):
    z = sp.Symbol("z")
    rho = sp.Symbol("rho")
    t = 2 * k
    p = sp.symbols("p0:" + str(t))
    sigma = z**t + sum(p[i] * z**i for i in range(t))
    rem_a = sp.Poly(sp.rem(z**a, sigma, z), z)
    rem_b = sp.Poly(sp.rem(z**b, sigma, z), z)
    cert_eqs = [
        sp.expand(rho * rem_a.coeff_monomial(z**d) + rem_b.coeff_monomial(z**d))
        for d in range(k, t)
    ]
    rem_n = sp.Poly(sp.rem(z**n - 1, sigma, z), z)
    div_eqs = [sp.expand(c) for c in rem_n.all_coeffs()]
    eqs = [e for e in cert_eqs + div_eqs if e != 0]
    if not eqs:
        return None
    G = sp.groebner(eqs, *p, rho, order="lex")
    last = G[-1]
    return sp.factor(last)


def test_reduction(n, k, a, b):
    from math import gcd as g
    d = g(g(a, b), n)
    if d > 1 and k % d == 0 and (n // d) > 0 and (k // d) > 0:
        n_red = n // d
        k_red = k // d
        a_red = a // d
        b_red = b // d
        print(f"\n(a={a}, b={b}) at (n={n}, k={k}) — d = gcd(a, b, n) = {d}")
        print(f"  Reduces (via u = z^{d}) to (a={a_red}, b={b_red}) at (n={n_red}, k={k_red})")
        Phi = eliminator(n, k, a, b)
        Phi_red = eliminator(n_red, k_red, a_red, b_red)
        print(f"  Φ (full): {Phi}")
        print(f"  Φ (reduced): {Phi_red}")
        match = sp.simplify(Phi - Phi_red) == 0
        print(f"  MATCH: {match}")
    else:
        Phi = eliminator(n, k, a, b)
        print(f"\n(a={a}, b={b}) at (n={n}, k={k}) — d={d}, no reduction (d=1 or k % d ≠ 0)")
        print(f"  Φ: {Phi}")


# Test cases
test_reduction(8, 2, 4, 6)   # d=2 → (2,3) at (4,1)
test_reduction(8, 2, 3, 4)   # d=1, no reduction
test_reduction(8, 2, 2, 5)   # d=1, no reduction
test_reduction(16, 4, 6, 8)  # d=2 → (3,4) at (8,2)
test_reduction(16, 4, 4, 8)  # d=4 → (1,2) at (4,1)
test_reduction(16, 4, 4, 12) # d=4 → (1,3) at (4,1)
test_reduction(16, 4, 5, 9)  # d=1, no reduction
