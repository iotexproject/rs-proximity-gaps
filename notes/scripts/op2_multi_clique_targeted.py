#!/usr/bin/env python3 -u
"""Test specific multi-clique patterns: tetrahedron + disjoint tetrahedron(s).

For (n, c), divide [n] into ⌊n/(w+1)⌋ disjoint (w+1)-vertex sets, each yielding
a tetrahedron pattern. Try realizing all tetrahedra simultaneously.
"""

import sys
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega, elp
from op2_clique_scan import rank_mod, kernel_mod, derive_realized_gammas
from op2_tet_consolidated import make_NEs, solve_for_witness

def best_realized(NEs, p, D, c, n_trials=20):
    m = len(NEs)
    rng = np.random.default_rng(0)
    best = 0
    for trial in range(n_trials):
        gammas = []
        seen = set()
        while len(gammas) < m:
            g = int(rng.integers(2, p))
            if g not in seen: gammas.append(g); seen.add(g)
        A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
        if not ker: continue
        for v in ker[:8]:
            s1 = v[:D]; s2 = v[D:]
            if not np.any(s2 != 0): continue
            der = derive_realized_gammas(NEs, gammas, s1, s2, p, c)
            distinct = set(g for g in der if g is not None)
            if len(distinct) > best: best = len(distinct)
    return best

def test_disjoint_tets(n, k, c, p, num_tets):
    """Use first num_tets disjoint (w+1)-vertex sets."""
    D = n - k; w = D - c
    omega = find_omega(n, p)
    if omega is None: return None
    L = [pow(omega, i, p) for i in range(n)]
    Vs = [tuple(range(i*(w+1), (i+1)*(w+1))) for i in range(num_tets)]
    if max(max(V) for V in Vs) >= n: return None
    Es = []
    for V in Vs:
        Es.extend(combinations(V, w))
    NEs = make_NEs(Es, L, p, D, c, w)
    bound = (2 * D - 1) // c
    best = best_realized(NEs, p, D, c, n_trials=30)
    print(f"  n={n} c={c} p={p}: {num_tets} disjoint tetrahedra → "
          f"m={len(Es)}, best={best}, bound={bound}")
    return best

def test_n_c_systematic(n, k, c, p):
    D = n - k; w = D - c
    print(f"\n=== n={n} k={k} c={c} (w={w}, w+1={w+1}, bound={(2*D-1)//c}) ===")
    max_tets = n // (w + 1)
    for num_tets in range(1, max_tets + 1):
        test_disjoint_tets(n, k, c, p, num_tets)

if __name__ == '__main__':
    for n, p in [(12, 1009), (16, 1009), (20, 1021), (24, 1009), (28, 1009)]:
        k = n // 2
        for c in [3, 4, 5]:
            D = n - k; w = D - c
            if w < 1 or w + 1 > n: continue
            test_n_c_systematic(n, k, c, p)
