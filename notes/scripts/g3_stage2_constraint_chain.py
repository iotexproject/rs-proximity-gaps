"""g3_stage2_constraint_chain.py — derive structural constraint chain C_1, ..., C_{h-1}.

Builds on Note 0252 (master αβ identity) and Note 0253 (y0-y2 cancellation).

For each c ∈ [1, h-1]: combine [s^0] [z^c] (αβ) = 0 (the y0 layer) and
[s^2] [z^c] (αβ) = 0 (the y2 layer), AFTER substituting in the elimination
chain x_1 = f_1, x_2 = f_2(x_1), ..., x_{c-1} = f_{c-1}(x_<{c-1}>) derived
at lower c.

The result C_c is a polynomial in {x_c, ..., x_{h-1}} (free variables) that
must vanish on V(I_stage2).

If the chain terminates with X = 0 forced (by combining all C_c), Stage 2
is closed structurally.

Approach (v1): linearly combine y0 and y2 to eliminate x_c, then look at the
residual as a constraint on the remaining variables.

  y0_c: (x_c - W_c)/4 + (3/4) V_c + (1/2) (X·W)_c - (1/4) (W²)_c = 0
  y2_c: (3/2) x_c - (3/2) W_c - V_c + [z^{2h+c}] X³ = 0

Eliminate x_c (linear in both):
  6·y0_c - 4·y2_c (or some multiple) — let me normalize.
  y0_c = (x_c - W_c)/4 + (other) ⟹ x_c = W_c + ... (after solving)
  y2_c = (3/2)(x_c - W_c) - V_c + [z^{2h+c}]X³ = 0 ⟹ x_c = W_c + (2/3) V_c - (2/3) [z^{2h+c}]X³

Substitute y2_c into y0_c (or vice versa) gives constraint on (V_c, W_c, [z^...]X³, etc.).
"""
from __future__ import annotations

import argparse
import sys
import os
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def setup(h):
    z = sp.Symbol("z")
    x = [sp.Symbol(f"x{i}") for i in range(1, h)]
    X = sum(x[i - 1] * z**i for i in range(1, h))
    X2 = sp.expand(X * X)
    X3 = sp.expand(X * X * X)

    Wc = {c: X2.coeff(z, h + c) for c in range(0, h)}  # extend to W_0
    Vc = {c: X2.coeff(z, c) for c in range(0, h)}
    cubic = {c: X3.coeff(z, 2 * h + c) for c in range(0, h)}

    # Cross-conv (X·W)_c := sum_{a+b=c, a,b>=1} x_a W_b  for c >= 2
    XW = {c: sum(x[a - 1] * Wc[c - a] for a in range(1, c) if 0 < c - a < h)
          for c in range(0, h)}
    # (W²)_c := sum_{a+b=c, a,b>=1} W_a W_b
    WW = {c: sum(Wc[a] * Wc[c - a] for a in range(1, c) if 0 < c - a < h)
          for c in range(0, h)}

    return z, x, X, Wc, Vc, cubic, XW, WW


def y0_eq(c, x, Wc, Vc, XW, WW):
    """Returns [s^0] [z^c] (αβ) · 4 (multiplied to clear denominators)."""
    return (x[c - 1] - Wc[c]) + 3 * Vc[c] + 2 * XW[c] - WW[c]


def y2_eq(c, x, Wc, Vc, cubic):
    """Returns [s^2] [z^c] (αβ) · 2."""
    return 3 * x[c - 1] - 3 * Wc[c] - 2 * Vc[c] + 2 * cubic[c]


def derive_chain(h, verbose=True):
    z, x, X, Wc, Vc, cubic, XW, WW = setup(h)

    # Elimination chain: solve y0_c AND y2_c for x_c, get constraint.
    # x_c from y2_c: x_c = W_c + (2/3) V_c - (2/3) cubic_c.
    # y0_c · 4: x_c - W_c + 3 V_c + 2 XW_c - WW_c = 0.
    # Substitute x_c from y2: (2/3) V_c - (2/3) cubic_c + 3 V_c + 2 XW_c - WW_c = 0
    # ⟹ (11/3) V_c - (2/3) cubic_c + 2 XW_c - WW_c = 0
    # ⟹ 11 V_c - 2 cubic_c + 6 XW_c - 3 WW_c = 0

    # Substitution dict: as we proceed c=1,2,...,h-1, we substitute x_c via y2 elim.
    subs = {}
    for c in range(1, h):
        # y2 elim: x_c = W_c + (2/3) V_c - (2/3) cubic_c (with subs applied to RHS)
        rhs = sp.expand((Wc[c] + sp.Rational(2, 3) * Vc[c]
                         - sp.Rational(2, 3) * cubic[c]).subs(subs))
        subs[x[c - 1]] = rhs
        if verbose:
            print(f"\n--- c = {c} ---")
            print(f"  x_{c} via y2_elim = {sp.factor(rhs)}")

        # The y0_c constraint, with x_c substituted via y2_elim and lower x_a substituted:
        y0c = sp.expand(y0_eq(c, x, Wc, Vc, XW, WW).subs(subs))
        # After substitution, y0_c should be in terms of x_{c+1}, ..., x_{h-1}.
        # If y0_c == 0 identically, no new constraint at this c.
        # Else: constraint C_c = y0_c.
        if y0c == 0:
            print(f"  y0_{c} (after y2 elim) = 0 identically (no new constraint)")
        else:
            # Verify constraint involves only x_{c+1}, ..., x_{h-1}
            free_vars = [x[i - 1] for i in range(c + 1, h)] if c < h - 1 else []
            if verbose:
                print(f"  C_{c} = {sp.factor(y0c)}")
                # Note: at this point all x_1..x_c should be eliminated.
                # If C_c == 0 identically, derived no info. Else it's a constraint.

    # Final substitutions
    x_final = [sp.expand(xi.subs(subs)) for xi in x]
    print("\n--- Final substitutions (after y2 chain) ---")
    for i, xi in enumerate(x_final):
        print(f"  x_{i+1} = {sp.factor(xi)}")

    return subs, x_final


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h", type=int, default=4)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    derive_chain(args.h, verbose=not args.quiet)


if __name__ == "__main__":
    main()
