#!/usr/bin/env python3 -u
"""Test: do two tetrahedron varieties intersect non-trivially?

If yes: a single (s_1, s_2) realizes BOTH tetrahedra → M = 2(w+1) γ's.
If no: V_bad components are essentially disjoint, and the density bound
       C(n, w+1) × p^{-(w+2c-1)} is sharp.

Method: take random (s_1, s_2) ∈ V_tet(V_1), check if it's in V_tet(V_2)
for various V_2 ≠ V_1.
"""

import sys
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega, elp
from op2_clique_scan import rank_mod, kernel_mod
from op2_tet_consolidated import make_NEs, solve_for_witness
from op2_witness_full_M import compute_M_full

def get_tet_witness(n, k, c, p, V, seed=0):
    """Return a (s_1, s_2) ∈ V_tet(V)."""
    D = n - k; w = D - c
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    Es = list(combinations(V, w))
    NEs = make_NEs(Es, L, p, D, c, w)
    rng = np.random.default_rng(seed)
    gammas = []
    while len(gammas) < len(Es):
        g = int(rng.integers(2, p))
        if g not in gammas: gammas.append(g)
    A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
    if not ker: return None, None, L
    # Random kernel combination
    coefs = rng.integers(1, p, size=len(ker))
    v = np.zeros(2 * D, dtype=np.int64)
    for cf, u in zip(coefs, ker):
        v = (v + cf * u) % p
    s1 = v[:D].astype(np.int64); s2 = v[D:].astype(np.int64)
    return s1, s2, L

def is_in_tet_variety(s1, s2, V, L, p, n, c, w):
    """Check if (s_1, s_2) realizes all w+1 γ's of tetrahedron(V)."""
    Es = list(combinations(V, w))
    realized = 0
    for E in Es:
        # Get N_E (could precompute)
        lam = elp(E, L, p)
        N = np.zeros((c, len(s1)), dtype=np.int64)
        for r in range(c):
            for j in range(len(s1)):
                t = j - r
                if 0 <= t <= w:
                    N[r, j] = lam[t] % p
        aE = (N @ s2) % p
        bE = (N @ s1) % p
        nz = None
        for j in range(c):
            if aE[j] != 0: nz = j; break
        if nz is None: continue
        prop = all(
            (int(aE[j_]) * int(bE[k_]) - int(aE[k_]) * int(bE[j_])) % p == 0
            for j_ in range(c) for k_ in range(c)
        )
        if prop: realized += 1
    return realized == len(Es)

if __name__ == '__main__':
    n, k, c = 12, 6, 3
    D = n - k; w = D - c
    p = 1009
    V1 = (1, 4, 5, 8)
    print(f"=== Intersection test: V1={V1} witness vs other tetrahedra ===")
    s1, s2, L = get_tet_witness(n, k, c, p, V1, seed=0)
    print(f"  V1 witness: s_2 = {s2.tolist()}")

    # Compute full M for this witness
    full_M = compute_M_full(s1, s2, L, p, n, c, w)
    print(f"  Full M = {len(full_M)}")
    realized_supports = [E for Es in full_M.values() for E in Es]
    print(f"  All realized supports: {sorted(realized_supports)}")

    # Find which tetrahedra are realized
    print(f"\n  Scan all V ⊂ [n] of size w+1=4 for full tetrahedron realization:")
    realized_tetrahedra = []
    for V_test in combinations(range(n), w + 1):
        Es_test = list(combinations(V_test, w))
        if all(E in realized_supports for E in Es_test):
            realized_tetrahedra.append(V_test)
            # Get γ values from full_M
            gammas_V = [
                next(g for g, Es in full_M.items() if E in Es)
                for E in Es_test
            ]
            unique_g = len(set(gammas_V))
            print(f"    V={V_test}: realized (γ's: {gammas_V}, distinct: {unique_g})")

    print(f"\n  Total tetrahedra realized: {len(realized_tetrahedra)}")
    print(f"  Expected if intersection trivial: 1 (just V1)")
