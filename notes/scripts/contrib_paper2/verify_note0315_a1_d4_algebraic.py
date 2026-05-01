"""Algebraic verification of A_1(0) = 0 claim at d=4.

Strategy: parameterize V_4 algebraically using sympy. Compute the GB and
extract orbit structure. For each length-4 orbit, compute s = t^4 and
A_1(s) = x_1 / t. Check whether A_1(0) — the constant term in the
s-expansion of A_1 over F̄[s]/H_4(s) — is 0.
"""
from __future__ import annotations

import sympy as sp


def main():
    x1, x2, x3, t, s = sp.symbols('x1 x2 x3 t s')

    # Chain at d=4 (Note 0315 hand-proof)
    c1 = x1 - 2 * x2 * x3 + 4 * x1**2 * x3 + 2 * x1 * x2**2
    c2 = x2 - x3**2 + 3 * x1**2 + 8 * x1 * x2 * x3 + 2 * x2**3 - 4 * x2**2 * x3**2
    c3 = x3 + 6 * x1 * x2 + 6 * x1 * x3**2 + 6 * x2**2 * x3 - 4 * x2 * x3**3

    print("Computing GB of [c1, c2, c3] ...")
    G = sp.groebner([c1, c2, c3], x1, x2, x3, order='lex')
    print(f"GB has {len(G.polys)} polys")
    for i, p in enumerate(G.polys):
        deg_x1 = sp.Poly(p.as_expr(), x1).degree() if x1 in p.as_expr().free_symbols else 0
        print(f"  poly {i}: lead in x1 deg {deg_x1}")

    # Eliminate to get univariate polynomial in x_3
    print("\nEliminating x1, x2 to get poly in x_3 alone:")
    elim = sp.groebner([c1, c2, c3], x1, x2, x3, order='lex')
    last = elim.polys[-1].as_expr()
    print(f"  last poly: {sp.expand(last)}")
    if x1 not in last.free_symbols and x2 not in last.free_symbols:
        # Pure x3 polynomial
        x3_poly = sp.Poly(last, x3)
        print(f"  x3 poly degree: {x3_poly.degree()}")
        print(f"  x3 poly: {x3_poly}")
        roots = sp.solve(last, x3)
        print(f"  # roots in x3: {len(roots)}")
        for r in roots:
            print(f"    x3 = {r}")


if __name__ == '__main__':
    main()
