#!/usr/bin/env python3 -u
"""For a tetrahedron-witness (s_1, s_2), compute the FULL M(s_1, s_2) by
checking all C(n, w) supports for realized γ values.

Question: is M(s_1, s_2) exactly w+1 (the tetrahedron supports) or larger?
"""

import sys
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega, elp
from op2_clique_scan import rank_mod, kernel_mod
from op2_tet_consolidated import make_NEs, solve_for_witness

def compute_M_full(s1, s2, L, p, n, c, w):
    """Compute M(s_1, s_2) by scanning all C(n, w) supports."""
    D = len(s1)
    all_supports = list(combinations(range(n), w))
    realized_gammas = {}
    for E in all_supports:
        lam = elp(E, L, p)
        N = np.zeros((c, D), dtype=np.int64)
        for r in range(c):
            for j in range(D):
                t = j - r
                if 0 <= t <= w:
                    N[r, j] = lam[t] % p
        aE = (N @ s2) % p
        bE = (N @ s1) % p
        nz = None
        for j in range(c):
            if aE[j] != 0: nz = j; break
        if nz is None: continue
        # Check proportionality
        prop = all(
            (int(aE[j_]) * int(bE[k_]) - int(aE[k_]) * int(bE[j_])) % p == 0
            for j_ in range(c) for k_ in range(c)
        )
        if not prop: continue
        gamma = (-int(bE[nz]) * pow(int(aE[nz]), p-2, p)) % p
        realized_gammas.setdefault(gamma, []).append(E)
    return realized_gammas

if __name__ == '__main__':
    n, k, c = 12, 6, 3
    D = n - k; w = D - c
    p = 1009
    V = (1, 4, 5, 8)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    Es_tet = list(combinations(V, w))

    NEs = make_NEs(Es_tet, L, p, D, c, w)
    rng = np.random.default_rng(0)
    gammas = []
    while len(gammas) < len(Es_tet):
        g = int(rng.integers(2, p))
        if g not in gammas: gammas.append(g)

    A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
    print(f"=== Tetrahedron at n=12 c=3 p=1009, V={V} ===")
    print(f"  rank A = {rA}, ker dim = {len(ker)}")
    print(f"  Tetrahedron γ tuple: {gammas}")

    # Full M for each kernel basis vector
    print(f"\n  For each kernel basis (s_1, s_2), compute FULL M:")
    for i, v in enumerate(ker):
        s1 = v[:D].astype(np.int64)
        s2 = v[D:].astype(np.int64)
        if not np.any(s2 != 0): continue
        full_M = compute_M_full(s1, s2, L, p, n, c, w)
        bound = (2 * D - 1) // c
        print(f"\n    ker[{i}]: s_2 = {s2.tolist()}")
        print(f"      M = {len(full_M)} distinct γ realized (bound = {bound})")
        print(f"      γ values: {sorted(full_M.keys())[:10]}{'...' if len(full_M) > 10 else ''}")
        # Count by # supports per γ
        from collections import Counter
        sizes = Counter(len(Es) for Es in full_M.values())
        print(f"      Distribution (# supports per γ): {dict(sizes)}")
        # Show extreme γ's
        if len(full_M) > 0:
            sorted_g = sorted(full_M.keys(), key=lambda g: -len(full_M[g]))
            for g in sorted_g[:3]:
                print(f"      γ={g}: {len(full_M[g])} supports: {full_M[g][:5]}{'...' if len(full_M[g]) > 5 else ''}")
        if i >= 2: break

    # Try a random combination of kernel vectors
    print(f"\n  Random kernel combination:")
    for trial in range(3):
        coefs = rng.integers(1, p, size=len(ker))
        v = np.zeros(2 * D, dtype=np.int64)
        for c_, u in zip(coefs, ker):
            v = (v + c_ * u) % p
        s1 = v[:D]; s2 = v[D:]
        if not np.any(s2 != 0): continue
        full_M = compute_M_full(s1, s2, L, p, n, c, w)
        print(f"    trial {trial}: coefs={coefs.tolist()}, M = {len(full_M)}")
