#!/usr/bin/env python3 -u
"""Iteratively grow a bad-support set.

Start with tetrahedron (m=4 supports of (w+1)-set V).
Greedy: add the support that maximally extends "co-realizable" set.
Stops when no support can be added without dropping realized count.
"""

import sys
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega, elp
from op2_clique_scan import rank_mod, kernel_mod, derive_realized_gammas
from op2_tet_consolidated import make_NEs, solve_for_witness

def best_realized_for_supports(Es, NEs, p, D, c, n_trials=30):
    """For these supports, find the maximum (over trials, kernel vectors,
    γ choices) of distinct realized γ count."""
    m = len(Es)
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
        for v in ker[:5]:
            s1 = v[:D]; s2 = v[D:]
            if not np.any(s2 != 0): continue
            der = derive_realized_gammas(NEs, gammas, s1, s2, p, c)
            distinct = set(g for g in der if g is not None)
            if len(distinct) > best: best = len(distinct)
    return best

def iterative_grow(p, n=12, k=6, c=3, V_init=(1, 4, 5, 8), max_iter=20):
    D = n - k; w = D - c
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    all_supports = list(combinations(range(n), w))

    Es_cur = list(combinations(V_init, w))
    print(f"Iteration 0: tetrahedron with V={V_init}, m={len(Es_cur)}")
    NEs_cur = make_NEs(Es_cur, L, p, D, c, w)
    best_cur = best_realized_for_supports(Es_cur, NEs_cur, p, D, c)
    print(f"  current best realized = {best_cur}")

    for itr in range(1, max_iter):
        # Try adding each support not already in Es_cur
        candidates = [E for E in all_supports if E not in Es_cur]
        gains = []
        for E_new in candidates:
            Es_try = Es_cur + [E_new]
            NEs_try = make_NEs(Es_try, L, p, D, c, w)
            best_new = best_realized_for_supports(Es_try, NEs_try, p, D, c, n_trials=15)
            if best_new > best_cur:
                gains.append((best_new, E_new))
        if not gains:
            print(f"  No support adds gain. Stopping at m={len(Es_cur)}, "
                  f"best realized={best_cur}")
            break
        # Take the max gain
        gains.sort(reverse=True)
        best_new, E_add = gains[0]
        Es_cur = Es_cur + [E_add]
        NEs_cur = make_NEs(Es_cur, L, p, D, c, w)
        best_cur = best_new
        print(f"Iteration {itr}: added {E_add}, m={len(Es_cur)}, "
              f"best realized={best_cur}, gains_count={len(gains)}")
    print(f"\nFinal: {len(Es_cur)} supports, max distinct γ = {best_cur}")
    print(f"Supports: {Es_cur}")
    bound = (2 * D - 1) // c
    print(f"Bound = ⌊(2D-1)/c⌋ = {bound}; violation factor = {best_cur / bound:.2f}")
    return best_cur, Es_cur

if __name__ == '__main__':
    print("=== Iterative max_bad search at n=12 c=3 p=1009 ===")
    iterative_grow(1009, n=12, k=6, c=3, V_init=(1, 4, 5, 8))
    print()
    print("=== Iterative max_bad search at n=16 c=3 p=1009 ===")
    iterative_grow(1009, n=16, k=8, c=3, V_init=(0, 1, 2, 3, 4, 5))
