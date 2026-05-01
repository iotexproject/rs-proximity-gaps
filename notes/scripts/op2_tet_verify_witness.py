#!/usr/bin/env python3 -u
"""Two questions:
  Q1: Does the kernel (s_1, s_2) over Q with γ=[100,101,102,103] yield 4 distinct
      bad γ for the tetrahedron supports? (Direct bound violation test.)
  Q2: With L_j = n-th roots of unity at LARGE prime p, does the rank deficiency
      persist? (Tests whether RS structure rescues the bound.)
"""

import sys
from itertools import combinations
from fractions import Fraction
sys.path.insert(0, 'notes/scripts')
from op2_tetrahedron_over_Q import (
    elp_Q, make_NE_Q, build_A_Q, rank_Q, kernel_Q
)

def matvec_Q(M, v):
    return [sum(M[i][j] * v[j] for j in range(len(v))) for i in range(len(M))]

def Q1_check_bound_violation():
    print("=== Q1: Verify (s_1,s_2) ∈ ker A gives 4 distinct bad γ over Q ===")
    n, k, c = 12, 6, 3
    D = n - k; w = D - c
    Es = list(combinations((1, 4, 5, 8), w))
    L = [Fraction(j + 1) for j in range(n)]
    gammas = [Fraction(100 + i) for i in range(len(Es))]
    A = build_A_Q(Es, gammas, L, D, c)
    ker = kernel_Q(A)
    print(f"  ker dim = {len(ker)}")
    if not ker:
        print("  No kernel; nothing to test.")
        return
    # Take first kernel vector (s_1, s_2)
    v = ker[0]
    s1 = v[:D]; s2 = v[D:]
    print(f"  s_1 = {s1}")
    print(f"  s_2 = {s2}")

    # For each support E_i, compute aE = N_E·s_2, bE = N_E·s_1
    # Check proportionality, derive γ
    derived_gammas = []
    for i, E in enumerate(Es):
        N = make_NE_Q(E, L, D, c)
        aE = matvec_Q(N, s2)
        bE = matvec_Q(N, s1)
        print(f"\n  E_{i}={E}")
        print(f"    aE = N·s_2 = {aE}")
        print(f"    bE = N·s_1 = {bE}")
        # Find first nonzero in aE
        nz = None
        for j in range(c):
            if aE[j] != 0:
                nz = j; break
        if nz is None:
            print(f"    aE = 0  → γ undetermined for E_{i}; not a true bad γ")
            derived_gammas.append(None)
            continue
        gamma_derived = -bE[nz] / aE[nz]
        # Verify proportionality
        prop_ok = all(
            aE[j_] * bE[k_] == aE[k_] * bE[j_]
            for j_ in range(c) for k_ in range(c)
        )
        print(f"    derived γ = {gamma_derived}, expected {gammas[i]}, "
              f"proportional? {prop_ok}, match? {gamma_derived == gammas[i]}")
        derived_gammas.append(gamma_derived)
    # Count distinct
    distinct = set(g for g in derived_gammas if g is not None)
    print(f"\n  Distinct realized γ count = {len(distinct)} (claim: should be 4 for bound violation)")
    print(f"  → Bound violated over Q? {len(distinct) > 3}")

def Q2_check_with_rs_domain():
    """Try L_j = ω^j at a large prime p (n-th root of unity).
    Check rank A and whether (s_1, s_2) achieves 4 distinct bad γ at large p."""
    print("\n=== Q2: With L_j = roots of unity at large p ===")
    import numpy as np
    sys.path.insert(0, 'notes/scripts')
    from op2_max_bad_phase_diagram import find_omega, elp

    n, k, c = 12, 6, 3
    D = n - k; w = D - c
    Es = list(combinations((1, 4, 5, 8), w))
    m = len(Es)

    for p in [61, 109, 229, 601, 1009, 4001, 10009]:
        omega = find_omega(n, p)
        if omega is None:
            print(f"  p={p}: no primitive n-th root, skip")
            continue
        L = [pow(omega, i, p) for i in range(n)]

        # Build N_E for each support
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

        # For random γ_i: build A and compute rank mod p
        rng = np.random.default_rng(1)
        gammas = [int(rng.integers(2, p)) for _ in range(m)]
        # Ensure distinct
        while len(set(gammas)) < m:
            gammas = [int(rng.integers(2, p)) for _ in range(m)]

        A = np.zeros((m * c, 2 * D), dtype=np.int64)
        for i in range(m):
            A[i*c:(i+1)*c, :D] = NEs[i]
            A[i*c:(i+1)*c, D:] = (gammas[i] * NEs[i]) % p

        # rank mod p
        def rank_mod(M, p):
            M = M.copy() % p
            R, C = M.shape
            r = 0
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

        rA = rank_mod(A, p)
        print(f"  p={p:>5}: rank A = {rA} / min(mc,2D) = {min(m*c, 2*D)}, "
              f"deficient? {rA < min(m*c, 2*D)}")

if __name__ == '__main__':
    Q1_check_bound_violation()
    Q2_check_with_rs_domain()
