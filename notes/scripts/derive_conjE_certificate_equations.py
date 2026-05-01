"""Derive the formal coefficient equations for ConjE exact certificates.

For a monic degree-t locator

    P(x)=x^t + p_{t-1}x^{t-1}+...+p_0,

a half-set S certifies the pencil rho*x^a + x^b exactly when the high
coefficients, degrees k..t-1, of

    rho * (x^a mod P) + (x^b mod P)

vanish.  This script derives those equations symbolically.  The point is to
look for sparse locator patterns forced by the exact certificate surface, which
is stronger than the underdetermined pair-cancellation equation.
"""

from __future__ import annotations

import argparse

import sympy as sp


def remainder_power(exp: int, t: int, coeffs: tuple[sp.Symbol, ...], memo: dict[int, list[sp.Expr]]) -> list[sp.Expr]:
    if exp in memo:
        return memo[exp]
    if exp < t:
        vec = [sp.Integer(0)] * t
        vec[exp] = sp.Integer(1)
        memo[exp] = vec
        return vec

    # x^exp = x^(exp-t) * x^t and x^t = -sum_i p_i x^i.
    out = [sp.Integer(0)] * t
    base = exp - t
    for i, p_i in enumerate(coeffs):
        sub = remainder_power(base + i, t, coeffs, memo)
        for j, val in enumerate(sub):
            out[j] -= p_i * val
    out = [sp.factor(v) for v in out]
    memo[exp] = out
    return out


def equations(n: int, k: int, a: int, b: int) -> tuple[list[sp.Expr], list[sp.Expr], list[sp.Expr]]:
    t = n // 2
    coeffs = sp.symbols("p0:" + str(t))
    rho = sp.Symbol("rho")
    memo: dict[int, list[sp.Expr]] = {}
    rem_a = remainder_power(a, t, coeffs, memo)
    rem_b = remainder_power(b, t, coeffs, memo)
    high = [sp.factor(rho * rem_a[d] + rem_b[d]) for d in range(k, t)]
    minors = []
    for i in range(k, t):
        for j in range(i + 1, t):
            minors.append(sp.factor(rem_a[i] * rem_b[j] - rem_a[j] * rem_b[i]))
    return rem_a, rem_b, high, [sp.factor(m) for m in minors]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=8)
    parser.add_argument("--k", type=int, default=None)
    parser.add_argument("--a", type=int, required=True)
    parser.add_argument("--b", type=int, required=True)
    args = parser.parse_args()

    k = args.k if args.k is not None else args.n // 4
    rem_a, rem_b, high, minors = equations(args.n, k, args.a, args.b)
    print(f"ConjE certificate equations n={args.n} k={k} t={args.n//2} (a,b)=({args.a},{args.b})")
    print("x^a mod P high:")
    for degree, expr in enumerate(rem_a):
        if degree >= k:
            print(f"  deg {degree}: {sp.factor(expr)}")
    print("x^b mod P high:")
    for degree, expr in enumerate(rem_b):
        if degree >= k:
            print(f"  deg {degree}: {sp.factor(expr)}")
    print("high equations rho*Ra+Rb=0:")
    for degree, expr in enumerate(high, start=k):
        print(f"  deg {degree}: {sp.factor(expr)}")
    print("rho-eliminated rank-one minors:")
    for expr in minors:
        if expr != 0:
            print(f"  {sp.factor(expr)}")


if __name__ == "__main__":
    main()
