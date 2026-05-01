"""g3_chain_endpoint_fast.py — focused test: only "chain + endpoint" closure.

Skip chain-only and chain+bulk to save time. At higher h, just verify the
key claim: chain + 2 endpoints suffices for closure.
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


def endpoint_constraints(h):
    x, Wc, Vc, XW, WW = setup(h)
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
    print(f"  [{label}] |G|={len(G)}, time={dt:.2f}s, closes={closes}", flush=True)
    if not closes:
        not_in = [str(xi) for xi, b in zip(x, in_G) if not b]
        print(f"    Vars not killed: {not_in}", flush=True)
    return closes


def test_h(h):
    print(f"\n========== h = {h} ==========", flush=True)
    x, c_chain = chain_eqs(h)
    _, c_endpt = endpoint_constraints(h)
    print(f"  chain: {len(c_chain)}, endpoint: {len(c_endpt)}", flush=True)
    gb_close(c_chain + c_endpt, x, "chain + endpoint")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h-list", default="8,9,10")
    args = parser.parse_args()
    for h in args.h_list.split(","):
        test_h(int(h))


if __name__ == "__main__":
    main()
