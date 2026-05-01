"""g3_chain_curve_param.py — verify V(chain) is 1-dim curve, parameterize.

Per Note 0257 + user suggestion: empirically check whether V(chain) is
1-dimensional, parametrized by W_1 (or equivalently x_1). If so, restrict
E_{h-1}, E_{h-2} to the curve to get univariate polynomials in W_1, and
check gcd_F(E_{h-1}|, E_{h-2}|) = W_1^k.

Workflow at fixed h:
  1. Compute chain GB.
  2. Compute Krull dim of V(chain) via sympy.
  3. If dim 1: parameterize curve. Check via implicitization or rational
     parameterization.
  4. Restrict E_{h-1}, E_{h-2} to the curve.
  5. Compute gcd in F[W_1].
"""
from __future__ import annotations

import argparse
import time
import sympy as sp


def setup(h):
    z = sp.Symbol("z")
    x = [sp.Symbol(f"x{i}") for i in range(1, h)]
    X = sum(x[i - 1] * z**i for i in range(1, h))
    X2 = sp.expand(X * X)
    Wc = {c: X2.coeff(z, h + c) for c in range(0, h)}
    Vc = {c: X2.coeff(z, c) for c in range(0, 2 * h)}
    XW = {c: sum(x[a - 1] * Wc[c - a] for a in range(1, c + 1)
                 if 1 <= c - a < h) for c in range(0, h)}
    WW = {c: sum(Wc[a] * Wc[c - a] for a in range(1, c)
                 if 1 <= c - a < h) for c in range(0, h)}
    return x, Wc, Vc, XW, WW


def chain_eqs(h):
    x, Wc, Vc, XW, WW = setup(h)
    return x, [(x[c - 1] - Wc[c]) + 3 * Vc[c] + 2 * XW[c] - WW[c] for c in range(1, h)]


def endpoint_eqs(h):
    x, Wc, Vc, XW, WW = setup(h)
    eqs = []
    for c in [h - 2, h - 1]:
        Uc_sq = Vc[c] - 2 * XW[c] + WW[c]
        eqs.append(14 * Vc[c] - 3 * Uc_sq)
    return x, eqs


def analyze(h, verbose=False):
    print(f"\n========== h = {h} ==========")
    x, c_chain = chain_eqs(h)
    _, c_endpt = endpoint_eqs(h)

    t0 = time.time()
    G = sp.groebner(c_chain, *x, order="lex")
    dt = time.time() - t0
    print(f"  chain LEX GB: |G|={len(G)}, time={dt:.2f}s")

    if verbose:
        for g in G:
            s = str(sp.factor(g))
            if len(s) > 150: s = s[:150] + " ..."
            print(f"    {s}")

    # Try Krull dim. The dim of V(I_chain) in F[x] relates to the
    # transcendence degree of F[x]/I_chain over F.
    try:
        # sp.groebner has .dimension property.
        from sympy.polys.orderings import grevlex
        Ggrev = sp.groebner(c_chain, *x, order="grevlex")
        try:
            dim_fp = Ggrev.dimension
            print(f"  dim V(chain) (Krull) = {dim_fp}")
        except Exception as e:
            print(f"  dim computation failed: {e}")
    except Exception as e:
        print(f"  dim attempt failed: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h-list", default="4,5,6,7")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    for h in args.h_list.split(","):
        analyze(int(h), verbose=args.verbose)


if __name__ == "__main__":
    main()
