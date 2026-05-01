"""Universal R_d sampler — verify Q1 at h = 2^k via numerical Newton.

Q1 (Note 0273): R_d ≢ 0 on V_d^primitive, where
  R_d := -3 x_{d/2} + 2 V_{d/2} + 3 W_{d/2}
       ≡ E_{d/2} (mod c_{d/2}).

R_d ≠ 0 on V_d^prim is equivalent (via Galois) to vdim(I_chain^d + E_{d/2}) = 1.

This sampler avoids GB by Newton-iterating chain to find length-d orbit
points and evaluating R_d numerically.

Usage:
  python3 g3_Rd_sampler_universal.py [h1 h2 ...]
"""
import sys
import time
import random
from math import gcd
from functools import reduce

import sympy as sp
import numpy as np
from scipy.optimize import fsolve


def build_chain(h):
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
    chain = [(x[c - 1] - Wc[c]) + 3 * Vc[c] + 2 * XW[c] - WW[c]
             for c in range(1, h)]
    c_half = h // 2
    R_h = -3 * x[c_half - 1] + 2 * Vc[c_half] + 3 * Wc[c_half]
    return chain, R_h, x


def classify_orbit(sol, h, eps=1e-6):
    nz = [a for a in range(1, h) if abs(sol[a - 1]) > eps]
    if not nz:
        return 1
    g = reduce(gcd, nz)
    return h // g


def run_h(h, n_trials=30, seed=123):
    print(f"\n{'='*60}")
    print(f"h={h}, sampling {n_trials} Newton starts")
    t0 = time.time()
    chain, R_h, x = build_chain(h)
    chain_fn = sp.lambdify(x, chain, "numpy")
    R_fn = sp.lambdify(x, R_h, "numpy")
    print(f"  build time: {time.time()-t0:.1f}s, vars: {len(x)}")
    rng = random.Random(seed)
    hits = {}
    R_vals_at_h = []
    t1 = time.time()
    for trial in range(n_trials):
        start = np.array([rng.uniform(-0.4, 0.4) for _ in range(h-1)])
        try:
            def F(v):
                return np.array(chain_fn(*v), dtype=float)
            sol, info, ier, msg = fsolve(F, start, full_output=True,
                                          xtol=1e-10, maxfev=5000)
            if ier != 1 or np.linalg.norm(F(sol)) > 1e-6:
                continue
            d0 = classify_orbit(sol, h)
            hits[d0] = hits.get(d0, 0) + 1
            if d0 == h:
                R_val = float(R_fn(*sol))
                R_vals_at_h.append(R_val)
        except Exception:
            continue
    elapsed = time.time() - t1
    print(f"  Newton time: {elapsed:.1f}s")
    print(f"  Hit distribution: {hits}")
    if R_vals_at_h:
        absvals = [abs(v) for v in R_vals_at_h]
        print(f"  Length-{h} hits: {len(R_vals_at_h)}, "
              f"R_{h} range: |R| in [{min(absvals):.3e}, {max(absvals):.3e}]")
        if all(v > 1e-6 for v in absvals):
            print(f"  ✓ Q1@d={h}: R_{h} nonzero on ALL found V_{h}^prim points")
            return True
        else:
            print(f"  ✗ Q1@d={h}: R_{h} too small at some point — INVESTIGATE")
            return False
    else:
        print(f"  No length-{h} orbit found.  Try more trials or skip.")
        return None


if __name__ == "__main__":
    targets = ([16, 32, 64] if len(sys.argv) == 1
               else [int(a) for a in sys.argv[1:]])
    summary = {}
    for h in targets:
        result = run_h(h, n_trials=30)
        summary[h] = result
    print(f"\n{'='*60}")
    print("Summary:")
    for h, r in summary.items():
        marker = "✓" if r is True else ("✗" if r is False else "?")
        print(f"  h={h}: {marker}")
