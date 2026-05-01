"""g3_chain_endpoint_modular.py — modular GB to bypass laptop OOM at h=16.

For h = 2^k, verify the single-endpoint conjecture (Theorem 0268):
  chain + E_{h/2}  closes to {origin}
by computing GB modulo small primes p ∉ {2, 7}. If GB mod p closes for
several primes, this is rigorous evidence for closure over Q (semi-continuity
of Hilbert function in good characteristic).

Targets:
  - h=8 + E_4: known to close (Note 0271). Sanity check mod 11, 13.
  - h=16 + E_8: laptop OOM over Q. Test mod 11, 13, 17, 19.
  - h=12 + E_6: known to NOT close alone (needs E_8 too — h=12 has ω=2).
"""
from __future__ import annotations

import argparse
import time
import sympy as sp
from sympy.polys.domains import GF


def setup(h, p=None):
    z = sp.Symbol("z")
    x = [sp.Symbol(f"x{i}") for i in range(1, h)]
    X = sum(x[i - 1] * z ** i for i in range(1, h))
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


def endpoint_E(h, c_idx):
    """E_{c_idx} := 14 V_c - 3 [z^c] U^2  where U = X - W. Equivalent:
       11 V_c + 6 XW_c - 3 WW_c."""
    x, Wc, Vc, XW, WW = setup(h)
    return x, 14 * Vc[c_idx] - 3 * (Vc[c_idx] - 2 * XW[c_idx] + WW[c_idx])


def gb_close_mod(eqs, x, p, label, time_limit_s=600):
    """Compute GB mod p, check whether all x_i are reduced to 0 by GB."""
    t0 = time.time()
    domain = GF(p)
    try:
        G = sp.groebner(eqs, *x, order="grevlex", domain=domain)
    except Exception as e:
        dt = time.time() - t0
        print(f"  [{label} mod {p}] FAILED ({dt:.1f}s): {type(e).__name__}: {e}",
              flush=True)
        return None
    dt = time.time() - t0
    in_G = []
    for xi in x:
        r = sp.reduced(xi, G, *x, domain=domain)
        in_G.append(r[1] == 0)
    closes = all(in_G)
    print(f"  [{label} mod {p}] |G|={len(G)}, time={dt:.1f}s, closes={closes}",
          flush=True)
    if not closes:
        not_in = [str(xi) for xi, b in zip(x, in_G) if not b]
        print(f"    Not killed: {not_in[:10]}", flush=True)
    return closes


def test_h_mod(h, c_idx, primes):
    print(f"\n========== h = {h}, single endpoint E_{c_idx} ==========", flush=True)
    x, c_chain = chain_eqs(h)
    _, e_eq = endpoint_E(h, c_idx)
    eqs = c_chain + [e_eq]
    print(f"  chain: {len(c_chain)} eqs, vars: {len(x)}", flush=True)
    results = {}
    for p in primes:
        if p in {2, 7}:
            continue
        results[p] = gb_close_mod(eqs, x, p, f"h={h}+E_{c_idx}")
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h", type=int, default=16)
    parser.add_argument("--primes", default="11,13,17,19,23")
    args = parser.parse_args()

    primes = [int(p) for p in args.primes.split(",")]
    h = args.h
    c_idx = h // 2

    print(f"=== Modular GB test: h = {h}, single endpoint E_{c_idx} ===")
    print(f"Primes: {primes}")
    results = test_h_mod(h, c_idx, primes)
    print()
    print("=== Summary ===")
    for p, closes in results.items():
        marker = "?"
        if closes is True: marker = "✓"
        elif closes is False: marker = "✗"
        print(f"  mod {p}: {marker}")

    if all(c is True for c in results.values()):
        print()
        print(f"CONCLUSION: h={h} + E_{c_idx} closes mod every tested prime.")
        print(f"Single-endpoint conjecture holds at h={h} mod {sorted(results.keys())}.")
    elif any(c is False for c in results.values()):
        bad = [p for p, c in results.items() if c is False]
        print()
        print(f"WARNING: h={h} + E_{c_idx} does NOT close mod {bad}.")
        print(f"Single-endpoint conjecture fails or characteristic-dependent.")


if __name__ == "__main__":
    main()
