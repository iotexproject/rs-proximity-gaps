#!/usr/bin/env python3 -u
"""Test: tetrahedron (4 supports) + 1 extra support outside V.
Goal: determine if max_bad can exceed w+1.

Setup: n=12, c=3, w=3, V_tet={1,4,5,8}, extra support E_5 from outside V.
Bound = 3. Tetrahedron gives 4. Can we get 5?
"""

import sys
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega, elp
from op2_clique_scan import rank_mod, kernel_mod, derive_realized_gammas
from op2_tet_consolidated import make_NEs, solve_for_witness, verify_witness

def test_tet_plus_extra(p, V=(1, 4, 5, 8), E_extra=(0, 2, 3)):
    n, k, c = 12, 6, 3
    D = n - k; w = D - c
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    Es_tet = list(combinations(V, w))
    Es = Es_tet + [E_extra]
    m = len(Es)
    bound = (2 * D - 1) // c
    print(f"\n=== Tet + extra n=12 c=3 p={p} V={V} extra={E_extra} ===")
    print(f"Supports = {Es}, m={m}")

    NEs = make_NEs(Es, L, p, D, c, w)
    rng = np.random.default_rng(0)

    best = 0
    for trial in range(50):
        gammas = []
        seen = set()
        while len(gammas) < m:
            g = int(rng.integers(2, p))
            if g not in seen: gammas.append(g); seen.add(g)
        A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
        if not ker: continue
        for v in ker[:6]:
            s1 = v[:D]; s2 = v[D:]
            if not np.any(s2 != 0): continue
            der = derive_realized_gammas(NEs, gammas, s1, s2, p, c)
            distinct = set(g for g in der if g is not None)
            if len(distinct) > best:
                best = len(distinct)
    print(f"  Best across 50 trials: {best} distinct γ "
          f"(bound={bound}, w+1={w+1}, violation? {best>bound})")
    return best

def scan_extra_supports(p):
    n, k, c = 12, 6, 3
    w = 3
    V = (1, 4, 5, 8)
    print(f"\n=== Scan: tetrahedron + each possible extra support ===")
    all_supports = list(combinations(range(n), w))
    tet_supports = list(combinations(V, w))
    extras = [E for E in all_supports if E not in tet_supports]

    counts = {}
    for E_extra in extras:
        best = test_tet_plus_extra(p, V=V, E_extra=E_extra)
        counts[E_extra] = best
    print(f"\n  Distribution of best counts:")
    from collections import Counter
    cnt = Counter(counts.values())
    for k_, v_ in sorted(cnt.items()):
        print(f"    best={k_}: {v_} extras")
    print(f"\n  Max best across all extras: {max(counts.values())}")

if __name__ == '__main__':
    print("Single tests (verify approach):")
    test_tet_plus_extra(1009, V=(1, 4, 5, 8), E_extra=(0, 2, 3))
    test_tet_plus_extra(1009, V=(1, 4, 5, 8), E_extra=(2, 3, 6))
    test_tet_plus_extra(1009, V=(1, 4, 5, 8), E_extra=(0, 4, 5))  # shares with V

    print("\n" + "="*60)
    scan_extra_supports(1009)
