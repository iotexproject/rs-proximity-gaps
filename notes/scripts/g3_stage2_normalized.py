"""Lambda-normalized Stage 2 system (after Codex Note 0248-0249 on
fri-conje-attack branch).

Substitution lam^h = rho, q_i = lam^(3h-i) x_i, y = lam^h s = rho s.
The normalized residue-c equation is the s-coefficients of

    U_c(s) = sum_{a+b=c}     P_a(s) R_b(s)
           + s sum_{a+b=c+h} P_a(s) R_b(s)

where for c >= 1:
    P_c(s) = (3/2) x_c - (1/2) W_c + x_c s
    R_c(s) = (1/2) x_c + (1/2) W_c - x_c s
    W_c    = [z^{h+c}] X(z)^2,   X(z) = sum_{i=1..h-1} x_i z^i,
and on-block:
    P_0(s) = s^4 + s^3 - s/2 - 1/4
    R_0(s) = s^4 - s^3 + s^2 - s/2 + 1/4.

Empirically deg_s U_c <= 2 (after y3/y4 reductions baked into q-only).

This script:
  1. Builds normalized_model(h);
  2. Runs sympy.groebner on its s-coefficients;
  3. Reports timing and reduction of x_i to verify ideal = <x_1,...,x_{h-1}>.
"""
from __future__ import annotations

import argparse
import time

import sympy as sp


def normalized_model(h: int):
    s, z = sp.symbols("s z")
    x = [sp.Symbol(f"x{i}") for i in range(1, h)]
    X = sum(x[i - 1] * z**i for i in range(1, h))
    X2 = sp.expand(X * X)

    P = {0: s**4 + s**3 - sp.Rational(1, 2) * s - sp.Rational(1, 4)}
    R = {0: s**4 - s**3 + s**2 - sp.Rational(1, 2) * s + sp.Rational(1, 4)}
    for c in range(1, h):
        wrap = X2.coeff(z, h + c)
        P[c] = sp.Rational(3, 2) * x[c - 1] - sp.Rational(1, 2) * wrap + x[c - 1] * s
        R[c] = sp.Rational(1, 2) * x[c - 1] + sp.Rational(1, 2) * wrap - x[c - 1] * s

    U = {}
    for c in range(1, h):
        row = sp.Integer(0)
        for a in range(h):
            b = c - a
            if 0 <= b < h:
                row += P[a] * R[b]
            b = c + h - a
            if 0 <= b < h:
                row += s * P[a] * R[b]
        U[c] = sp.expand(row)
    return s, x, U


def verify_h(h: int, order: str = "grevlex", show_basis: bool = False) -> bool:
    s, x_vars, U = normalized_model(h)
    eqs = []
    max_deg = 0
    for c in range(1, h):
        poly = sp.Poly(U[c], s)
        max_deg = max(max_deg, poly.degree())
        for k in range(poly.degree() + 1):
            coef = sp.factor(poly.coeff_monomial(s**k))
            if coef != 0:
                eqs.append(coef)

    print(f"h={h}: vars={len(x_vars)}, eqs={len(eqs)}, max deg_s={max_deg}")

    t0 = time.time()
    basis = sp.groebner(eqs, *x_vars, order=order)
    elapsed = time.time() - t0

    failures = []
    for x_i in x_vars:
        rem = basis.reduce(x_i)[1]
        if sp.factor(rem) != 0:
            failures.append((x_i, sp.factor(rem)))

    print(f"  GB time={elapsed:.3f}s  basis_len={len(basis.polys)}  "
          f"failures={len(failures)}")
    if show_basis:
        for poly in basis.polys:
            print(f"    {poly}")
    if failures:
        for x_i, rem in failures[:5]:
            print(f"    FAIL {x_i} -> {rem}")
        return False
    print(f"  PASS — ideal = <x_1, ..., x_{h-1}>")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h-list", default="2,3,4,5,6,7,8,9")
    parser.add_argument("--order", default="grevlex",
                        choices=["lex", "grlex", "grevlex"])
    parser.add_argument("--show-basis", action="store_true")
    args = parser.parse_args()

    ok = True
    for raw_h in args.h_list.split(","):
        ok = verify_h(int(raw_h), args.order, args.show_basis) and ok
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
