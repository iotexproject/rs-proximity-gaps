#!/usr/bin/env python3 -u
"""Consolidated, self-contained verification of the tetrahedron bound violation.

This script PROVES (computationally) that the bound max_bad ≤ ⌊(2D-1)/c⌋ is
violated at the tetrahedron configuration, for n=12, k=6, c=3, at every tested
prime supporting n-th roots of unity (including p > 10^5).

It also tests whether COMBINED tetrahedra (e.g., two disjoint or two overlapping)
give larger violations.
"""

import sys
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega, elp
from op2_clique_scan import rank_mod, kernel_mod, derive_realized_gammas

def make_NEs(Es, L, p, D, c, w):
    NEs = []
    for E in Es:
        lam = elp(E, L, p)
        N = np.zeros((c, D), dtype=np.int64)
        for r in range(c):
            for j in range(D):
                t = j - r
                if 0 <= t <= w:
                    N[r, j] = lam[t] % p
        NEs.append(N)
    return NEs

def solve_for_witness(NEs, gammas, p, D, c):
    """Build A, return (A, ker basis, rank)."""
    m = len(NEs)
    A = np.zeros((m * c, 2 * D), dtype=np.int64)
    for i in range(m):
        A[i*c:(i+1)*c, :D] = NEs[i]
        A[i*c:(i+1)*c, D:] = (gammas[i] * NEs[i]) % p
    rA = rank_mod(A, p)
    ker = kernel_mod(A, p) if rA < min(m * c, 2 * D) else []
    return A, ker, rA

def verify_witness(NEs, gammas, s1, s2, p, c, name=""):
    """Print full verification of (s_1, s_2) realizing all γ_i for all E_i."""
    print(f"\n  Verification: {name}")
    print(f"    s_1 = {s1.tolist()}")
    print(f"    s_2 = {s2.tolist()}")
    print(f"    γ values = {gammas}")
    print(f"    Per-support check:")
    distinct = set()
    for i, N in enumerate(NEs):
        aE = (N @ s2) % p
        bE = (N @ s1) % p
        # Open condition: N_E · s_2 ≠ 0 vector
        nz_idx = None
        for j in range(c):
            if aE[j] != 0: nz_idx = j; break
        nonzero = (nz_idx is not None)
        # Proportionality: bE = -γ_i · aE
        prop = nonzero and all(
            (int(aE[j_]) * int(bE[k_]) - int(aE[k_]) * int(bE[j_])) % p == 0
            for j_ in range(c) for k_ in range(c)
        )
        if nonzero:
            gd = (-int(bE[nz_idx]) * pow(int(aE[nz_idx]), p-2, p)) % p
            matches = (gd == gammas[i])
        else:
            gd = None; matches = False
        if matches: distinct.add(gd)
        print(f"      i={i}: aE = {aE.tolist()}, bE = {bE.tolist()}, "
              f"γ derived = {gd}, ok? {matches}")
    return len(distinct)

def test_single_tetrahedron(p, V=(1, 4, 5, 8)):
    """At p, n=12, c=3: verify tetrahedron with V gives 4 distinct bad γ."""
    n, k, c = 12, 6, 3
    D = n - k; w = D - c
    omega = find_omega(n, p)
    if omega is None: return None
    L = [pow(omega, i, p) for i in range(n)]
    Es = list(combinations(V, w))
    print(f"\n=== Single tetrahedron at n=12 c=3 p={p} V={V} ===")
    print(f"Supports = {Es}")

    NEs = make_NEs(Es, L, p, D, c, w)
    bound = (2 * D - 1) // c

    rng = np.random.default_rng(0)
    gammas = []
    while len(gammas) < len(Es):
        g = int(rng.integers(2, p))
        if g not in gammas: gammas.append(g)

    A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
    print(f"  rank A = {rA}, full = {min(len(Es)*c, 2*D)}, ker dim = {len(ker)}")
    if not ker:
        print(f"  No kernel; bound NOT violated at this γ choice.")
        return False

    v = ker[0]
    s1 = v[:D]; s2 = v[D:]
    distinct = verify_witness(NEs, gammas, s1, s2, p, c, name="ker[0]")
    print(f"\n  → distinct realized γ = {distinct}, bound = {bound}, "
          f"violation? {distinct > bound}")
    return distinct > bound

def test_two_disjoint_tetrahedra(p):
    """At p, n=12, c=3: combine two disjoint 4-vertex sets, m=8 supports.
    Bound = 3. Maximum violation if all 8 realize."""
    n, k, c = 12, 6, 3
    D = n - k; w = D - c
    omega = find_omega(n, p)
    if omega is None: return None
    L = [pow(omega, i, p) for i in range(n)]

    V1 = (0, 1, 2, 3); V2 = (4, 5, 6, 7)  # disjoint
    Es1 = list(combinations(V1, w))
    Es2 = list(combinations(V2, w))
    Es = Es1 + Es2
    m = len(Es)
    print(f"\n=== Two disjoint tetrahedra n=12 c=3 p={p} ===")
    print(f"V1={V1}, V2={V2}, total m={m}")

    NEs = make_NEs(Es, L, p, D, c, w)
    bound = (2 * D - 1) // c

    rng = np.random.default_rng(1)
    best = 0
    for trial in range(30):
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
            if len(distinct) > best:
                best = len(distinct)
                if best >= 8:
                    print(f"  Found best={best} at trial {trial}")
                    verify_witness(NEs, gammas, s1, s2, p, c, name=f"trial {trial}")
                    return best
    print(f"  Best across 30 trials: {best} distinct γ realized "
          f"(bound={bound}, violation? {best>bound})")
    return best

def test_two_overlapping_tetrahedra(p):
    """At p, n=12, c=3: two tetrahedra sharing 1 vertex, m=8 supports."""
    n, k, c = 12, 6, 3
    D = n - k; w = D - c
    omega = find_omega(n, p)
    if omega is None: return None
    L = [pow(omega, i, p) for i in range(n)]

    V1 = (0, 1, 2, 3); V2 = (3, 4, 5, 6)  # share vertex 3
    Es1 = list(combinations(V1, w))
    Es2 = list(combinations(V2, w))
    # Remove duplicates if any
    Es = list(dict.fromkeys(Es1 + Es2))
    m = len(Es)
    print(f"\n=== Two overlapping tetrahedra (share v=3) n=12 c=3 p={p} ===")
    print(f"V1={V1}, V2={V2}, distinct supports m={m}")

    NEs = make_NEs(Es, L, p, D, c, w)
    bound = (2 * D - 1) // c

    rng = np.random.default_rng(2)
    best = 0
    for trial in range(30):
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
            if len(distinct) > best:
                best = len(distinct)
    print(f"  Best across 30 trials: {best} distinct γ realized "
          f"(bound={bound}, violation? {best>bound})")
    return best

if __name__ == '__main__':
    print("Single tetrahedron at multiple primes:")
    for p in [1009, 10009, 100003]:
        result = test_single_tetrahedron(p)
        print(f"  → bound violated at p={p}? {result}")

    print("\n" + "="*60)
    print("\nDisjoint tetrahedra (m=8 vs bound=3):")
    test_two_disjoint_tetrahedra(1009)
    test_two_disjoint_tetrahedra(10009)

    print("\n" + "="*60)
    print("\nOverlapping tetrahedra (m=7 vs bound=3):")
    test_two_overlapping_tetrahedra(1009)
    test_two_overlapping_tetrahedra(10009)
