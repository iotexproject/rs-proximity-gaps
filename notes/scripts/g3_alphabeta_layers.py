"""g3_alphabeta_layers.py — explicit s-layer support of αβ in A.

Verify which s-degrees actually appear in [z^c] (αβ) in A = F(s)[z]/(z^h - s)
for c = 1..h-1.
"""
from __future__ import annotations
import sympy as sp


def alphabeta_in_A(h):
    s, z = sp.symbols("s z")
    x = [sp.Symbol(f"x{i}") for i in range(1, h)]
    P0 = s**4 + s**3 - sp.Rational(1, 2) * s - sp.Rational(1, 4)
    R0 = s**4 - s**3 + s**2 - sp.Rational(1, 2) * s + sp.Rational(1, 4)
    X = sum(x[i - 1] * z**i for i in range(1, h))
    X2 = sp.expand(X * X)
    Wc = {c: X2.coeff(z, h + c) for c in range(1, h)}
    P = sum((sp.Rational(3, 2) * x[c - 1] - sp.Rational(1, 2) * Wc[c]
             + x[c - 1] * s) * z**c for c in range(1, h))
    R = sum((sp.Rational(1, 2) * x[c - 1] + sp.Rational(1, 2) * Wc[c]
             - x[c - 1] * s) * z**c for c in range(1, h))
    direct = sp.expand((P0 + P) * (R0 + R))
    poly_z = sp.Poly(direct, z)
    coefs = poly_z.all_coeffs()[::-1]
    in_A = sp.Integer(0)
    for d, cc in enumerate(coefs):
        shift = d
        c = cc
        while shift >= h:
            shift -= h
            c = c * s
        in_A += c * z**shift
    return s, x, sp.expand(in_A)


def report(h):
    print(f"\n=== h = {h} ===")
    s, x, ab = alphabeta_in_A(h)
    polz = sp.Poly(ab, sp.Symbol("z"))
    for c in range(0, h):
        coef_zc = polz.coeff_monomial(sp.Symbol("z")**c)
        polys = sp.Poly(coef_zc, s)
        layers_present = sorted([j for j, _ in polys.terms()
                                  if not (sp.expand(polys.coeff_monomial(s**j[0])) == 0)])
        # simpler: enumerate degrees with nonzero coef
        deg = polys.degree() if coef_zc != 0 else 0
        present = []
        for j in range(deg + 1):
            cf = polys.coeff_monomial(s**j)
            if sp.expand(cf) != 0:
                present.append(j)
        print(f"  c = {c}: s-layers present = {present}")


for h in [3, 4, 5, 6]:
    report(h)
