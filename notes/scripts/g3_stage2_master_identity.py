"""g3_stage2_master_identity.py — verify the αβ master identity in A.

Identities (Note 0252):
  P_0 R_0 = s^8 - 1/16.
  P_c = x_c + u_c, R_c = x_c - u_c, where u_c = (x_c - W_c)/2 + x_c·s.
  α β = (s^8 - 1/16) + σ X + δ U + (X² - U²) in A = F(s)[z]/(z^h - s)
  where σ = P_0 + R_0, δ = R_0 - P_0, X = Σ x_c z^c, U = Σ u_c z^c.

This script:
  1. Symbolically constructs (P_0+P)(R_0+R) directly per Codex's normalized model.
  2. Symbolically constructs the master form (s^8 - 1/16) + σX + δU + X² - U².
  3. Reduces both modulo (z^h - s); compares z^c coefficients for c=0..h-1.
  4. Confirms equality.
  5. Reports the per-c linear-order operator (should be x_c · (6 s² - 2 s + 1)/4).
"""
from __future__ import annotations

import argparse

import sympy as sp


def reduce_mod_zh_minus_s(poly_in_z, s, z, h):
    """Reduce poly in z modulo z^h - s, returning sympy polynomial in (z, s)."""
    poly = sp.Poly(sp.expand(poly_in_z), z)
    coefs = poly.all_coeffs()[::-1]  # ascending degree
    out = sp.Integer(0)
    for d, c in enumerate(coefs):
        if d < h:
            out += c * z**d
        else:
            shift = d
            while shift >= h:
                shift -= h
                c = c * s
            out += c * z**shift
    return sp.expand(out)


def build(h):
    s, z = sp.symbols("s z")
    x = [sp.Symbol(f"x{i}") for i in range(1, h)]

    X = sum(x[i - 1] * z**i for i in range(1, h))
    X2 = sp.expand(X * X)
    Wc = {c: X2.coeff(z, h + c) for c in range(1, h)}

    P0 = s**4 + s**3 - sp.Rational(1, 2) * s - sp.Rational(1, 4)
    R0 = s**4 - s**3 + s**2 - sp.Rational(1, 2) * s + sp.Rational(1, 4)
    P = sum((sp.Rational(3, 2) * x[c - 1] - sp.Rational(1, 2) * Wc[c]
             + x[c - 1] * s) * z**c
            for c in range(1, h))
    R = sum((sp.Rational(1, 2) * x[c - 1] + sp.Rational(1, 2) * Wc[c]
             - x[c - 1] * s) * z**c
            for c in range(1, h))

    direct = sp.expand((P0 + P) * (R0 + R))
    direct_in_A = reduce_mod_zh_minus_s(direct, s, z, h)

    # Master form
    sigma = sp.expand(P0 + R0)
    delta = sp.expand(R0 - P0)
    u = {c: (x[c - 1] - Wc[c]) / 2 + x[c - 1] * s for c in range(1, h)}
    U = sum(u[c] * z**c for c in range(1, h))
    master = sp.expand((s**8 - sp.Rational(1, 16))
                       + sigma * X + delta * U
                       + sp.expand(X * X) - sp.expand(U * U))
    master_in_A = reduce_mod_zh_minus_s(master, s, z, h)

    diff = sp.expand(direct_in_A - master_in_A)
    return s, z, x, sigma, delta, direct_in_A, master_in_A, diff


def verify(h):
    print(f"\n=== h={h} ===")
    s, z, x, sigma, delta, direct, master, diff = build(h)

    if sp.expand(diff) == 0:
        print(f"  Master identity HOLDS: αβ = (s⁸-1/16) + σX + δU + (X²-U²)")
    else:
        print(f"  FAIL diff = {sp.factor(diff)}")
        return False

    # Linear-order check per c.
    direct_poly_z = sp.Poly(direct, z)
    print(f"  z^0 coef of αβ in A: {sp.factor(direct_poly_z.coeff_monomial(z**0))}")
    linop = sp.expand(sigma + delta * (sp.Rational(1, 2) + s))
    print(f"  σ + δ(1/2 + s) = {sp.factor(linop)} "
          f"(should equal (6s² - 2s + 1)/4)")
    expected = sp.Rational(1, 4) * (6 * s**2 - 2 * s + 1)
    assert sp.expand(linop - expected) == 0, "linear operator mismatch"

    # Per-c check: linear part of [z^c](αβ) = x_c · linop + O(x²)
    for c in range(1, h):
        coef_zc = direct_poly_z.coeff_monomial(z**c)
        # Take linear part in (x_1,...,x_{h-1})
        linear = sp.Integer(0)
        for x_i in x:
            linear += sp.diff(coef_zc, x_i).subs({y: 0 for y in x}) * x_i
        # Must equal x_c * linop
        expected_lin = x[c - 1] * linop
        assert sp.expand(linear - expected_lin) == 0, f"linear part mismatch at c={c}"
    print(f"  Linearization: [z^c](αβ)|_lin = x_c · (6s² - 2s + 1)/4  ∀ c ∈ [1, {h-1}] ✓")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h-list", default="2,3,4,5,6")
    args = parser.parse_args()
    ok = True
    for h in args.h_list.split(","):
        ok = verify(int(h)) and ok
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
