#!/usr/bin/env python3 -u
"""Verify whether Open-Set Rank Lemma holds at c=2.

Setup: n=8, k=4, D=4, c=2, w=2.
Goal: find (s_1, s_2) with m=4 distinct bad γ.
Then check the lemma: is rank A = min(mc, 2D) = 8, OR does ∃i with a_i ≡ 0?

If we find a config with m=4, rank A < 8, AND all a_i ≠ 0 → lemma DISPROVED at c=2.
"""

import sys, time
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import (
    is_prime, primes_dividing_minus1, find_omega,
    elp, precompute_NE, count_bad_gammas
)

def find_witness(n, k, c, p, n_trials=500000, seed=0):
    """Heavy random search; return the BEST (s_1, s_2) and the m supports."""
    D = n - k
    w = D - c
    omega = find_omega(n, p)
    if omega is None:
        return None
    L = [pow(omega, i, p) for i in range(n)]
    allE = list(combinations(range(n), w))
    NE = precompute_NE(allE, L, p, D, c)

    rng = np.random.default_rng(seed)
    best_m = 0
    best_data = None

    for t in range(n_trials):
        s1 = rng.integers(0, p, size=D, dtype=np.int64)
        s2 = rng.integers(0, p, size=D, dtype=np.int64)
        if not np.any(s2 != 0): continue

        # Use the same approach as count_bad_gammas
        aE = (NE @ s2) % p   # shape (nE, c)
        bE = (NE @ s1) % p   # shape (nE, c)

        # c=2: compatible iff a_E[0]*b_E[1] - a_E[1]*b_E[0] = 0
        compat = (aE[:, 0] * bE[:, 1] - aE[:, 1] * bE[:, 0]) % p == 0
        # And a_E ≠ 0 (else γ undefined)
        nonzero = (aE[:, 0] != 0) | (aE[:, 1] != 0)
        valid = compat & nonzero

        if not np.any(valid):
            continue

        # Get γ values
        idx_v = np.where(valid)[0]
        # Use first nonzero coord of aE
        first_nz_0 = aE[idx_v, 0] != 0
        gammas = np.zeros(len(idx_v), dtype=np.int64)
        # When aE[0] != 0: γ = -bE[0] / aE[0]
        first0 = idx_v[first_nz_0]
        if len(first0) > 0:
            inv = pow(int(np.prod([1])), 1, p)  # placeholder
            # Use Fermat
            inv_a = np.array([pow(int(x), p-2, p) for x in aE[first0, 0]], dtype=np.int64)
            gammas[first_nz_0] = (-bE[first0, 0] * inv_a) % p
        # When aE[0] == 0 and aE[1] != 0: γ = -bE[1] / aE[1]
        first1 = idx_v[~first_nz_0]
        if len(first1) > 0:
            inv_a = np.array([pow(int(x), p-2, p) for x in aE[first1, 1]], dtype=np.int64)
            gammas[~first_nz_0] = (-bE[first1, 1] * inv_a) % p

        unique_g, inv = np.unique(gammas, return_inverse=True)
        m = len(unique_g)
        if m > best_m:
            best_m = m
            # Save witnesses: for each unique γ, pick one E
            E_list = []
            gamma_list = []
            for g_idx in range(m):
                pos = idx_v[np.where(inv == g_idx)[0][0]]
                E_list.append(allE[pos])
                gamma_list.append(int(unique_g[g_idx]))
            best_data = {
                's1': s1.tolist(),
                's2': s2.tolist(),
                'p': p,
                'm': m,
                'E_list': E_list,
                'gamma_list': gamma_list,
                'allE': allE,
                'NE': NE,
                'L': L,
            }
            if m >= 4:
                print(f"  trial {t}: found m={m}", flush=True)
                if m >= 5:
                    break

    return best_data

def check_lemma(data, n, k, c, p):
    """Given a witness with m bad γ, check the Open-Set Rank Lemma."""
    D = n - k
    w = D - c
    L = data['L']
    E_list = data['E_list']
    gamma_list = data['gamma_list']
    s1 = np.array(data['s1'], dtype=np.int64)
    s2 = np.array(data['s2'], dtype=np.int64)
    m = data['m']

    # Build matrix A: m·c × 2D, with row block i = [N_{E_i} | γ_i N_{E_i}]
    NE_list = []
    for E in E_list:
        lam = elp(E, L, p)
        N = np.zeros((c, D), dtype=np.int64)
        for r in range(c):
            for j in range(D):
                t = j - r
                if 0 <= t <= w:
                    N[r, j] = lam[t] % p
        NE_list.append(N)

    A = np.zeros((m * c, 2 * D), dtype=np.int64)
    for i in range(m):
        N_i = NE_list[i]
        A[i*c:(i+1)*c, :D] = N_i
        A[i*c:(i+1)*c, D:] = (gamma_list[i] * N_i) % p

    # Compute rank over F_p
    A_p = A % p
    rank_A = matrix_rank_modp(A_p, p)
    full_rank = min(m * c, 2 * D)

    # Compute n_0(E_i) for each i: leading row of N_{E_i}
    # In our notation, n_0(E_i) is the LEADING coefficient of the ELP of E_i
    # (the "row 0" of N matrix when N rows are shifted ELP coeffs)
    # Specifically: n_0(E_i) = N_i[0, :] (first row, the un-shifted ELP coeffs)
    # And ⟨n_0(E_i), s_2⟩ = first row · s_2
    a_0_vals = []
    for i in range(m):
        a0 = int((NE_list[i][0] @ s2) % p)
        a_0_vals.append(a0)

    # Check: are all a_0_vals nonzero?
    all_nonzero = all(a != 0 for a in a_0_vals)

    print(f"\n=== Witness data (n={n}, k={k}, c={c}, p={p}, m={m}) ===")
    print(f"s1 = {data['s1']}")
    print(f"s2 = {data['s2']}")
    print(f"γ values: {gamma_list}")
    print(f"Supports: {E_list}")
    print(f"\nMatrix A: shape {A.shape}, rank={rank_A}, min(mc, 2D)={full_rank}")
    print(f"Rank deficient: {rank_A < full_rank}")
    print(f"\n⟨n_0(E_i), s_2⟩ values: {a_0_vals}")
    print(f"All nonzero: {all_nonzero}")
    print()

    if rank_A < full_rank and all_nonzero:
        print("*** OPEN-SET RANK LEMMA DISPROVED ***")
        print("Found rank-deficient config with all a_0 nonzero")
        return False
    elif rank_A == full_rank:
        print("Lemma OK: full rank")
    else:
        print("Lemma OK: ∃i with a_0 = 0")
    return True

def matrix_rank_modp(A, p):
    """Compute rank of integer matrix A modulo prime p via Gaussian elimination."""
    M = A.copy() % p
    rows, cols = M.shape
    rank = 0
    for col in range(cols):
        # Find pivot
        pivot = None
        for r in range(rank, rows):
            if M[r, col] % p != 0:
                pivot = r
                break
        if pivot is None:
            continue
        M[[rank, pivot]] = M[[pivot, rank]]
        # Normalize pivot row
        inv = pow(int(M[rank, col]), p - 2, p)
        M[rank] = (M[rank] * inv) % p
        # Eliminate below and above
        for r in range(rows):
            if r != rank and M[r, col] % p != 0:
                M[r] = (M[r] - M[r, col] * M[rank]) % p
        rank += 1
        if rank == rows:
            break
    return rank

if __name__ == '__main__':
    # Try to find witness at n=8 c=2 with m=4
    n, k, c = 8, 4, 2
    for p in [113, 257, 449]:
        print(f"\n--- Searching at n={n} c={c} p={p} ---")
        data = find_witness(n, k, c, p, n_trials=200000)
        if data is None:
            continue
        if data['m'] >= 4:
            check_lemma(data, n, k, c, p)
            break
        else:
            print(f"  Best m at p={p}: {data['m']}")
