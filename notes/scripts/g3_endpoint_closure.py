"""g3_endpoint_closure.py — verify endpoint constraints + chain → X = 0.

Per Note 0255, the endpoint constraints (c ∈ {h-2, h-1}) read:

  [z^c] (14 X² - 3 U²) ∈ I_stage2,    c ∈ {h-1, h-2}

Where U = X - W, W_a = [z^{h+a}] X² (the "wraparound" part of X²).

Equivalently: [z^c] (11 X² + 6 X W - 3 W²) ∈ I.

Test: at fixed h, build the FULL Stage 2 ideal I (via αβ at h), and
check whether {endpoint constraints + bulk constraints + y0/y2 chain}
generate the same radical as I, i.e., V(I) = {0}.

Strategy:
  - Build the Stage 2 ideal I directly via the αβ form (or via the
    constraint chain recipe).
  - Compute a Groebner basis of I in the (h-uniform) elimination chain
    derived constraints + endpoint constraints.
  - Check the GB contains x_1, x_2, ..., x_{h-1} (i.e., V(I) = {0}).
"""
from __future__ import annotations

import argparse
import time
import sympy as sp


def build_stage2_constraints(h):
    """Build Stage 2 constraints using y0, y2 layers from the master αβ form.

    Returns list of polynomials in (x_1, ..., x_{h-1}) that must vanish
    on V(I_stage2).

    Specifically: [z^c] [s^j] (αβ) for c = 1..h-1, j = 0, 1, 2, 3, 4.
    (Other s-layers also exist but are dependent.)
    """
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

    # Reduce mod z^h - s.
    poly_z = sp.Poly(direct, z)
    coefs = poly_z.all_coeffs()[::-1]  # ascending
    in_A = sp.Integer(0)
    for d, c in enumerate(coefs):
        shift = d
        cc = c
        while shift >= h:
            shift -= h
            cc = cc * s
        in_A += cc * z**shift

    in_A = sp.expand(in_A)

    # Extract constraints: [z^c] [s^j] = 0 for c = 1..h-1.
    constraints = []
    for c in range(1, h):
        coef_zc = sp.Poly(in_A, z).coeff_monomial(z**c)
        coef_zc_poly_s = sp.Poly(coef_zc, s)
        deg_s = coef_zc_poly_s.degree()
        for j in range(deg_s + 1):
            cc = coef_zc_poly_s.coeff_monomial(s**j)
            if cc != 0:
                constraints.append(sp.expand(cc))

    # Dedupe (some may coincide).
    seen = set()
    uniq = []
    for c in constraints:
        cs = str(sp.expand(c))
        if cs not in seen:
            seen.add(cs)
            uniq.append(c)
    return x, uniq


def gb_check(h, verbose=False):
    print(f"\n========== h = {h} ==========")
    x, constraints = build_stage2_constraints(h)
    print(f"  {len(constraints)} unique constraints")
    if verbose:
        for i, c in enumerate(constraints):
            cs = str(sp.factor(c))
            if len(cs) > 100: cs = cs[:100] + " ..."
            print(f"    [{i}] {cs}")

    t0 = time.time()
    G = sp.groebner(constraints, *x, order="grevlex")
    dt = time.time() - t0
    print(f"  GB time: {dt:.2f}s, size: {len(G)}")
    print(f"  GB: {[str(sp.factor(g))[:80] for g in G[:10]]}")

    # Check radical:
    rad_check = all(any(sp.expand(g) == xi or sp.expand(g) == -xi for g in G) for xi in x)
    if rad_check:
        print(f"  → V(I) = {{0}} (each x_i ∈ G).")
    else:
        # Try to detect via dimension or by checking GB contains x_i^k
        in_gb_or_radical = []
        for xi in x:
            # is x_i in <G>?
            r = sp.reduced(xi, G)
            in_gb = (r[1] == 0)
            in_gb_or_radical.append((str(xi), in_gb))
        print(f"  x_i ∈ <G>? {in_gb_or_radical}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h-list", default="3,4,5,6")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    for h in args.h_list.split(","):
        gb_check(int(h), verbose=args.verbose)


if __name__ == "__main__":
    main()
