"""Derive symbolic locator rigidity for sign-paired ConjE templates.

For sign-paired pencils h_rho = rho*x^a + x^(a+n/2), the desired rigidity is
that every exact half-set divisor P of x^n-1 satisfying the high-vector
certificate equations is a two mod-4 coset locator:

    P(x) = x^(n/2) + u*x^(n/4) + v.

This script computes the high-vector triangular substitution, adds
P(x) | x^n - 1, and prints the Groebner basis.  At n=8 and n=16 it forces all
non-0,k locator coefficients to vanish and gives rho^4=1.
"""

from __future__ import annotations

import argparse

import sympy as sp

from triangular_ratio_elimination_sweep import high_equations, triangular_substitution


def signpaired_basis(n: int, k: int, a: int) -> tuple[dict[sp.Symbol, sp.Expr], list[sp.Symbol], list[sp.Expr]]:
    x = sp.Symbol("x")
    b = a + n // 2
    rho, p, eqs = high_equations(n, k, a, b)
    substitutions, residual = triangular_substitution(eqs, p, rho)
    t = n // 2
    P = sp.expand((x**t + sum(p[i] * x**i for i in range(t))).subs(substitutions))
    divisor_eqs = [sp.expand(c) for c in sp.Poly(sp.rem(x**n - 1, P, x), x).all_coeffs()]
    divisor_eqs = [eq for eq in divisor_eqs if eq != 0]
    remaining = [var for var in p if var not in substitutions]
    basis = sp.groebner(divisor_eqs + residual, *remaining, rho, order="lex")
    return substitutions, remaining, [sp.factor(g.as_expr()) for g in basis.polys]


def default_cases() -> list[tuple[int, int, int]]:
    return [
        (8, 2, 2),
        (8, 2, 3),
        (16, 4, 4),
        (16, 4, 5),
        (16, 4, 6),
        (16, 4, 7),
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=None)
    parser.add_argument("--k", type=int, default=None)
    parser.add_argument("--a", type=int, default=None)
    parser.add_argument("--default-cases", action="store_true")
    args = parser.parse_args()

    if args.default_cases:
        cases = default_cases()
    else:
        if args.n is None or args.a is None:
            parser.error("pass --default-cases or provide --n --a")
        k = args.k if args.k is not None else args.n // 4
        cases = [(args.n, k, args.a)]

    for n, k, a in cases:
        print(f"sign-paired locator rigidity n={n} k={k} a={a} b={a+n//2}")
        substitutions, remaining, basis = signpaired_basis(n, k, a)
        print(f"  substitutions={len(substitutions)} remaining={remaining}")
        for expr in basis:
            print(f"  {expr}")


if __name__ == "__main__":
    main()
