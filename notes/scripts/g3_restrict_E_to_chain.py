"""g3_restrict_E_to_chain.py — restrict E_{h-1}, E_{h-2} to V(chain),
get univariate polys, compute gcd.

V(chain) is 0-dim with LEX GB:
  x_1 - p_1(x_{h-1}) = 0
  x_2 - p_2(x_{h-1}) = 0
  ...
  x_{h-2} - p_{h-2}(x_{h-1}) = 0
  f(x_{h-1}) = 0   (univariate)

So V(chain) = {(p_1(t), ..., p_{h-2}(t), t) : f(t) = 0}.

Restrict E_{h-1}(x_1, ..., x_{h-1}) to V(chain) by substituting:
  E_{h-1}|_curve(t) := E_{h-1}(p_1(t), ..., p_{h-2}(t), t).

This is a univariate polynomial in t = x_{h-1}.

The closure condition: V(chain) ∩ V(E_{h-1}) ∩ V(E_{h-2}) = {origin (t=0)}.
Equivalently: gcd_F(E_{h-1}|, E_{h-2}|, f) = t^k (some power of t).

Test at h = 4, 5, 6, 7 — compute these gcds and inspect.
"""
from __future__ import annotations

import argparse
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


def parameterize_chain(h):
    """Compute lex GB of chain. Return:
      - subs: {x_1: p_1(t), ..., x_{h-2}: p_{h-2}(t)} (t = x_{h-1})
      - f(t): univariate generator (degree = #points in V(chain))
      - x_lst: [x_1, ..., x_{h-1}]
    """
    x, c_chain = chain_eqs(h)
    G = sp.groebner(c_chain, *x, order="lex")
    print(f"  chain LEX |G|={len(G)}", flush=True)

    # In sympy, lex with [x1, x2, ..., x_{h-1}] order = x_1 highest.
    # GB has form: x_1 - p_1(x_2..x_{h-1}), x_2 - p_2(...), ..., x_{h-2} - p_{h-2}(x_{h-1}), f(x_{h-1}).
    # We want to extract.

    t = x[-1]  # x_{h-1}
    subs = {}
    f_t = None
    for g in G:
        # Determine which variable g "solves for".
        for xi in x[:-1]:  # x_1, ..., x_{h-2}
            if g.has(xi) and sp.Poly(g, xi).degree() == 1:
                # g = a_xi · xi + (rest in lower vars). Solve.
                p = sp.Poly(g, xi)
                lc = p.coeff_monomial(xi)
                rest = sp.expand(g - lc * xi)
                if not any(g.has(xj) for xj in x[:-1] if xj != xi and not xi in subs):
                    subs[xi] = sp.expand(-rest / lc)
                    break
        else:
            # g is in t only (univariate)
            if g.has(t) and not any(g.has(xj) for xj in x[:-1]):
                f_t = g

    # Verify: subs should cover x_1..x_{h-2}.
    missing = [xi for xi in x[:-1] if xi not in subs]
    if missing:
        print(f"  WARN: missing subs for {missing}; using full GB", flush=True)
        # Fallback: solve recursively
        subs_filled = dict(subs)
        for g in G:
            for xi in missing:
                if g.has(xi):
                    g_sub = sp.expand(g.subs(subs_filled))
                    p = sp.Poly(g_sub, xi)
                    if p.degree() == 1:
                        lc = p.coeff_monomial(xi)
                        rest = sp.expand(g_sub - lc * xi)
                        subs_filled[xi] = sp.expand(-rest / lc)
                        break
        subs = subs_filled

    return subs, f_t, t, x


def restrict_E_and_gcd(h, verbose=False):
    print(f"\n========== h = {h} ==========", flush=True)
    subs, f_t, t, x_lst = parameterize_chain(h)
    if f_t is None:
        print("  no univariate found; abort", flush=True)
        return
    print(f"  f(t) = {sp.factor(f_t)}", flush=True)
    deg_f = sp.Poly(f_t, t).degree()
    print(f"  deg f = {deg_f}", flush=True)

    _, c_endpt = endpoint_eqs(h)
    E_hm2, E_hm1 = c_endpt[0], c_endpt[1]

    # Substitute subs into E.
    E_hm2_in_t = sp.expand(E_hm2.subs(subs))
    E_hm1_in_t = sp.expand(E_hm1.subs(subs))

    print(f"\n  E_{h-2}|_curve as poly in t = x_{h-1}:")
    s = str(sp.factor(E_hm2_in_t))
    if len(s) > 250: s = s[:250] + " ..."
    print(f"    {s}", flush=True)

    print(f"\n  E_{h-1}|_curve as poly in t = x_{h-1}:")
    s = str(sp.factor(E_hm1_in_t))
    if len(s) > 250: s = s[:250] + " ..."
    print(f"    {s}", flush=True)

    # gcd in F[t]:
    g1 = sp.gcd(E_hm2_in_t, f_t, t)
    g2 = sp.gcd(E_hm1_in_t, f_t, t)
    g_all = sp.gcd(g1, E_hm1_in_t, t)
    print(f"\n  gcd(E_{h-2}|, f) = {sp.factor(g1)}", flush=True)
    print(f"  gcd(E_{h-1}|, f) = {sp.factor(g2)}", flush=True)
    print(f"  gcd(E_{h-2}|, E_{h-1}|, f) = {sp.factor(g_all)}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h-list", default="4,5,6")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    for h in args.h_list.split(","):
        restrict_E_and_gcd(int(h), verbose=args.verbose)


if __name__ == "__main__":
    main()
