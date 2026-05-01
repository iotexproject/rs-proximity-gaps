"""Derive divisor-closure equations for the live ConjE locator cases.

This script combines:

  1. the exact high-vector certificate equations, and
  2. the divisor condition P(x) | x^n - 1

for the small live cases used in Note 0198.  The output is a Groebner basis of
the resulting locator-coordinate system after substituting the certificate
equations.  It is meant as a proof-shape extractor, not as a large search.
"""

from __future__ import annotations

import argparse

import sympy as sp


def groebner_case_n8_43() -> list[sp.Expr]:
    x = sp.Symbol("x")
    p0, p1, p3 = sp.symbols("p0 p1 p3")
    # Certificate equations for (n,k,a,b)=(8,2,4,3): p2=0, rho=p3^{-1}.
    P = x**4 + p3 * x**3 + p1 * x + p0
    rem = [sp.expand(c) for c in sp.Poly(sp.rem(x**8 - 1, P, x), x).all_coeffs()]
    return [sp.factor(g.as_expr()) for g in sp.groebner(rem, p0, p1, p3, order="lex").polys]


def groebner_case_n16_48() -> list[sp.Expr]:
    x = sp.Symbol("x")
    p0, p1, p2, p3, p4 = sp.symbols("p0 p1 p2 p3 p4")
    # Certificate equations for (n,k,a,b)=(16,4,4,8): p5=p6=p7=0, rho=p4.
    P = x**8 + p4 * x**4 + p3 * x**3 + p2 * x**2 + p1 * x + p0
    rem = [sp.expand(c) for c in sp.Poly(sp.rem(x**16 - 1, P, x), x).all_coeffs()]
    return [sp.factor(g.as_expr()) for g in sp.groebner(rem, p0, p1, p2, p3, p4, order="lex").polys]


def groebner_case_n16_410() -> list[sp.Expr]:
    x = sp.Symbol("x")
    p0, p1, p2, p6, p7 = sp.symbols("p0 p1 p2 p6 p7")
    # Certificate equations for (n,k,a,b)=(16,4,4,10):
    #   p5 = 2*p6*p7 - p7^3
    #   p4 = p6^2 + p6*p7^2 - p7^4
    #   p3 = p6*p7*(3*p6 - 2*p7^2)
    p5 = 2 * p6 * p7 - p7**3
    p4 = p6**2 + p6 * p7**2 - p7**4
    p3 = p6 * p7 * (3 * p6 - 2 * p7**2)
    P = x**8 + p7 * x**7 + p6 * x**6 + p5 * x**5 + p4 * x**4 + p3 * x**3 + p2 * x**2 + p1 * x + p0
    rem = [sp.expand(c) for c in sp.Poly(sp.rem(x**16 - 1, P, x), x).all_coeffs()]
    return [sp.factor(g.as_expr()) for g in sp.groebner(rem, p0, p1, p2, p6, p7, order="lex").polys]


CASES = {
    "n8-43": groebner_case_n8_43,
    "n16-48": groebner_case_n16_48,
    "n16-410": groebner_case_n16_410,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=sorted(CASES), default=None)
    args = parser.parse_args()

    cases = [args.case] if args.case else sorted(CASES)
    for name in cases:
        print(f"locator divisor closure {name}")
        for expr in CASES[name]():
            print(f"  {expr}")


if __name__ == "__main__":
    main()
