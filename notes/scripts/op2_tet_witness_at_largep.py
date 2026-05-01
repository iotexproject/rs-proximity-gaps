#!/usr/bin/env python3 -u
"""Verify the tetrahedron witness gives a TRUE bound violation at LARGE primes
with L = n-th roots of unity (the actual RS evaluation domain).

If confirmed: the bound `m ≤ ⌊(2D-1)/c⌋` is FALSE for c=3 even at large p.
This refutes our "conjecture v5" and demands a new conjecture / understanding.
"""

import sys
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega, elp

def rank_mod(M, p):
    M = M.copy() % p
    R, C = M.shape; r = 0
    for col in range(C):
        pv = None
        for i in range(r, R):
            if M[i, col] != 0: pv = i; break
        if pv is None: continue
        M[[r, pv]] = M[[pv, r]]
        inv = pow(int(M[r, col]), p-2, p)
        M[r] = (M[r] * inv) % p
        for i in range(R):
            if i != r and M[i, col] != 0:
                M[i] = (M[i] - M[i, col] * M[r]) % p
        r += 1
    return r

def kernel_mod(M, p):
    """Return basis of right null space mod p."""
    M = M.copy() % p
    R, C = M.shape
    pivot_col = -np.ones(R, dtype=np.int64)
    r = 0
    for col in range(C):
        if r >= R: break
        pv = None
        for i in range(r, R):
            if M[i, col] != 0: pv = i; break
        if pv is None: continue
        M[[r, pv]] = M[[pv, r]]
        inv = pow(int(M[r, col]), p-2, p)
        M[r] = (M[r] * inv) % p
        for i in range(R):
            if i != r and M[i, col] != 0:
                M[i] = (M[i] - M[i, col] * M[r]) % p
        pivot_col[r] = col
        r += 1
    pivots = set(int(c) for c in pivot_col[:r] if c >= 0)
    free_cols = [c for c in range(C) if c not in pivots]
    basis = []
    for fc in free_cols:
        v = np.zeros(C, dtype=np.int64)
        v[fc] = 1
        for i in range(r):
            pc = int(pivot_col[i])
            if pc >= 0:
                v[pc] = (-int(M[i, fc])) % p
        basis.append(v)
    return basis

def test_tet_at_p(p):
    n, k, c = 12, 6, 3
    D = n - k; w = D - c
    omega = find_omega(n, p)
    if omega is None: return None
    L = [pow(omega, i, p) for i in range(n)]
    Es = list(combinations((1, 4, 5, 8), w))
    m = len(Es)

    # Build N_E
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

    # Pick distinct γ_i (small integers > 0)
    rng = np.random.default_rng(0)
    while True:
        gammas = sorted(set(int(rng.integers(2, p)) for _ in range(m * 2)))[:m]
        if len(gammas) == m: break

    # Build A
    A = np.zeros((m * c, 2 * D), dtype=np.int64)
    for i in range(m):
        A[i*c:(i+1)*c, :D] = NEs[i]
        A[i*c:(i+1)*c, D:] = (gammas[i] * NEs[i]) % p

    rA = rank_mod(A, p)
    full = min(m * c, 2 * D)
    print(f"\n  p={p}: rank A = {rA} / {full}")

    if rA >= full:
        print(f"  Full rank. Tetrahedron not realizable here.")
        return False

    ker = kernel_mod(A, p)
    print(f"  ker dim = {len(ker)}")

    # Take (s_1, s_2) ∈ ker
    v = ker[0]
    s1 = v[:D].astype(np.int64)
    s2 = v[D:].astype(np.int64)
    print(f"  s_1 = {s1.tolist()}")
    print(f"  s_2 = {s2.tolist()}")

    # Verify A · v = 0
    Av = (A @ v) % p
    assert np.all(Av == 0), f"A·v ≠ 0 mod p! Av = {Av.tolist()}"

    # For each E_i, derive γ from (s_1, s_2)
    derived = []
    for i, E in enumerate(Es):
        N = NEs[i]
        aE = (N @ s2) % p
        bE = (N @ s1) % p
        # Find first nonzero in aE
        nz = None
        for j in range(c):
            if aE[j] != 0: nz = j; break
        if nz is None:
            print(f"    E_{i}={E}: aE = 0 (DEGENERATE — not a true bad γ)")
            derived.append(None); continue
        gd = (-int(bE[nz]) * pow(int(aE[nz]), p-2, p)) % p
        # Check proportionality
        prop = all(
            (int(aE[j_]) * int(bE[k_]) - int(aE[k_]) * int(bE[j_])) % p == 0
            for j_ in range(c) for k_ in range(c)
        )
        ok = (gd == gammas[i]) and prop
        print(f"    E_{i}={E}: derived γ = {gd}, expected {gammas[i]}, ok? {ok}")
        derived.append(gd if (prop and gd is not None) else None)

    distinct = set(g for g in derived if g is not None)
    bound = (2 * D - 1) // c
    print(f"  → distinct realized γ count = {len(distinct)} > bound {bound}? "
          f"{len(distinct) > bound}")
    if len(distinct) > bound:
        print(f"  ⚠️ BOUND VIOLATED at p={p} with tetrahedron!")
        return True
    return False

if __name__ == '__main__':
    print("=== Tetrahedron bound-violation test at large primes ===")
    print("n=12 k=6 c=3, V={1,4,5,8}, supports = all 3-subsets of V")
    print("Bound = ⌊(2·6-1)/3⌋ = 3, tetrahedron gives m=4")
    found_any = False
    for p in [61, 109, 229, 601, 1009, 10009, 100003]:
        result = test_tet_at_p(p)
        if result: found_any = True
    print(f"\n=== Summary: bound violated at some large p? {found_any} ===")
