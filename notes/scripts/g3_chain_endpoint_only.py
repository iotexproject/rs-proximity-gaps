"""g3_chain_endpoint_only.py — does (chain + endpoint constraints) close
without bulk?

Setup at fixed h:
  Chain (h-1 eqs):  x_c = W_c + corr (from y0_c after chain).
                    Equivalent to 4 y0_c with x_<c subbed = (x_c - W_c) + 3 V_c
                    + 2 (X·W)_c - (W²)_c = 0.

  Bulk constraints (h-3 eqs, c ∈ [1, h-3]):
                    cubic_c = 7 V_c - δ_c, i.e., 2 [z^{2h+c}] X³ - 14 V_c
                    + 3 [z^c] U² = 0.

  Endpoint constraints (2 eqs, c ∈ {h-2, h-1}):
                    14 V_c - 3 [z^c] U² = 0  (since cubic_c = 0).

Test:
  (A) chain alone — should NOT close.
  (B) chain + endpoint — does it close? (Hopefully yes — tells us bulk
      constraints are redundant.)
  (C) chain + endpoint + bulk = y0 + y2.
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
    X3 = sp.expand(X * X * X)
    Wc = {c: X2.coeff(z, h + c) for c in range(0, h)}
    Vc = {c: X2.coeff(z, c) for c in range(0, 2 * h)}
    cubic_c = {c: X3.coeff(z, 2 * h + c) for c in range(0, h)}

    XW = {c: sum(x[a - 1] * Wc[c - a] for a in range(1, c + 1)
                 if 1 <= c - a < h) for c in range(0, h)}
    WW = {c: sum(Wc[a] * Wc[c - a] for a in range(1, c)
                 if 1 <= c - a < h) for c in range(0, h)}

    return x, Wc, Vc, cubic_c, XW, WW


def chain_eqs(h):
    """y0_c chain equations: 4 y0_c = (x_c - W_c) + 3 V_c + 2 (X·W)_c - (W²)_c = 0."""
    x, Wc, Vc, _, XW, WW = setup(h)
    return x, [(x[c - 1] - Wc[c]) + 3 * Vc[c] + 2 * XW[c] - WW[c] for c in range(1, h)]


def bulk_constraints(h):
    """For c ∈ [1, h-3]: 2 cubic_c - 14 V_c + 3 [z^c] U² = 0.

    [z^c] U² where U = X - W is a poly in x's.
    Compute [z^c] (X - W)² = [z^c] X² - 2 [z^c] X W + [z^c] W²
                           = V_c - 2 (X·W)_c + (W²)_c.
    """
    x, Wc, Vc, cubic_c, XW, WW = setup(h)
    eqs = []
    for c in range(1, h - 2):  # c = 1 .. h-3
        Uc_sq = Vc[c] - 2 * XW[c] + WW[c]
        eqs.append(2 * cubic_c[c] - 14 * Vc[c] + 3 * Uc_sq)
    return x, eqs


def endpoint_constraints(h):
    """For c ∈ {h-2, h-1}: 14 V_c - 3 [z^c] U² = 0."""
    x, Wc, Vc, cubic_c, XW, WW = setup(h)
    eqs = []
    for c in [h - 2, h - 1]:
        if c < 1: continue
        Uc_sq = Vc[c] - 2 * XW[c] + WW[c]
        eqs.append(14 * Vc[c] - 3 * Uc_sq)
    return x, eqs


def gb_close(eqs, x, label):
    t0 = time.time()
    G = sp.groebner(eqs, *x, order="grevlex")
    dt = time.time() - t0
    in_G = []
    for xi in x:
        r = sp.reduced(xi, G)
        in_G.append(r[1] == 0)
    closes = all(in_G)
    print(f"  [{label}] |G|={len(G)}, time={dt:.2f}s, closes={closes}")
    if not closes:
        not_in = [str(xi) for xi, b in zip(x, in_G) if not b]
        print(f"    Vars not killed: {not_in}")
    return closes


def test_h(h):
    print(f"\n========== h = {h} ==========")
    x, c_chain = chain_eqs(h)
    _, c_bulk = bulk_constraints(h)
    _, c_endpt = endpoint_constraints(h)
    print(f"  chain: {len(c_chain)}, bulk: {len(c_bulk)}, endpoint: {len(c_endpt)}")
    gb_close(c_chain, x, "chain only")
    gb_close(c_chain + c_endpt, x, "chain + endpoint")
    gb_close(c_chain + c_bulk, x, "chain + bulk")
    gb_close(c_chain + c_bulk + c_endpt, x, "chain + bulk + endpoint = y0+y2")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h-list", default="3,4,5,6,7")
    args = parser.parse_args()
    for h in args.h_list.split(","):
        test_h(int(h))


if __name__ == "__main__":
    main()
