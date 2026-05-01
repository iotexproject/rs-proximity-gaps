#!/usr/bin/env python3 -u
"""Verify the formula dim X_γ = (w-1)(c-1) for tetrahedron configuration.

Compute dim ker A = m·c - rank A for tetrahedron at various (n, c, w).
Compare to predicted (w-1)(c-1).

Note: dim X_γ = m·c - rank A. For tetrahedron m = w+1.
"""

import sys
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega, elp
from op2_clique_scan import rank_mod
from op2_tet_consolidated import make_NEs, solve_for_witness

def measure_dim(n, k, c, p):
    D = n - k; w = D - c
    if w < 1: return None
    omega = find_omega(n, p)
    if omega is None: return None
    L = [pow(omega, i, p) for i in range(n)]
    V = tuple(range(w + 1))
    if max(V) >= n: return None
    Es = list(combinations(V, w))
    m = len(Es)
    NEs = make_NEs(Es, L, p, D, c, w)
    rng = np.random.default_rng(0)
    gammas = []
    while len(gammas) < m:
        g = int(rng.integers(2, p))
        if g not in gammas: gammas.append(g)
    A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
    dim_X = m * c - rA
    return {
        'n': n, 'c': c, 'w': w, 'm': m,
        'rank': rA, 'dim_X_gamma': dim_X,
        'predicted': (w - 1) * (c - 1),
        'match': dim_X == (w - 1) * (c - 1),
    }

if __name__ == '__main__':
    print(f"{'n':>4} {'c':>3} {'w':>3} {'m':>3} {'rank':>5} {'dim X_γ':>8} "
          f"{'pred (w-1)(c-1)':>17} {'match':>6}")
    cases = []
    for n in [12, 16, 20, 24, 28]:
        for c in [3, 4, 5, 6]:
            r = measure_dim(n, n // 2, c, 1009 if n != 20 else 1021)
            if r is None: continue
            cases.append(r)
            print(f"{r['n']:>4} {r['c']:>3} {r['w']:>3} {r['m']:>3} {r['rank']:>5} "
                  f"{r['dim_X_gamma']:>8} {r['predicted']:>17} "
                  f"{'✓' if r['match'] else '✗':>6}")
    matches = sum(1 for r in cases if r['match'])
    print(f"\n{matches}/{len(cases)} cases match the formula dim X_γ = (w-1)(c-1)")
