#!/usr/bin/env python3 -u
"""Find a true c=3 lemma counterexample at small prime.

At n=12 c=3 p=61, heavy random gives max_bad=4 > 3=bound.
This means lemma FAILS here. Find specific (s_1, s_2) and analyze structure.
"""

import sys
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import (
    find_omega, elp, precompute_NE, count_bad_gammas
)

def find_witness_general(n, k, c, p, target_m, n_trials=500000):
    """Find (s_1, s_2) with at least target_m distinct bad γ. Returns supports
    and γ values for each distinct γ."""
    D = n - k; w = D - c
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    allE = list(combinations(range(n), w))
    NE = precompute_NE(allE, L, p, D, c)
    nE = len(allE)

    rng = np.random.default_rng(0)
    for t in range(n_trials):
        s1 = rng.integers(0, p, size=D, dtype=np.int64)
        s2 = rng.integers(0, p, size=D, dtype=np.int64)
        if not np.any(s2 != 0): continue
        m = count_bad_gammas(NE, s1, s2, p)
        if m >= target_m:
            # Re-extract γ and supports
            aE = (NE @ s2) % p
            bE = (NE @ s1) % p
            # For c >= 2, need a_E ∝ b_E
            # Vectorized cross-product check
            outer_ab = (aE[:, :, None] * bE[:, None, :]) % p
            outer_ba = (aE[:, None, :] * bE[:, :, None]) % p
            cross = (outer_ab - outer_ba) % p
            compatible = np.all(cross == 0, axis=(1, 2))
            # Need a_E nonzero
            nonzero = np.any(aE != 0, axis=1)
            valid = compatible & nonzero
            idx_v = np.where(valid)[0]
            if len(idx_v) == 0: continue

            # Extract γ for each compatible E
            aE_v = aE[idx_v]; bE_v = bE[idx_v]
            first_nz = np.argmax(aE_v != 0, axis=1)
            n_v = len(idx_v)
            rows = np.arange(n_v)
            a_first = aE_v[rows, first_nz]
            b_first = bE_v[rows, first_nz]
            a_inv = np.array([pow(int(x), p-2, p) for x in a_first], dtype=np.int64)
            gammas = (-b_first * a_inv) % p

            unique_g, inv = np.unique(gammas, return_inverse=True)
            m_actual = len(unique_g)
            if m_actual < target_m: continue

            # For each unique γ, get all supports
            E_per_gamma = {}
            for k_idx, g in enumerate(unique_g):
                pos_list = idx_v[np.where(inv == k_idx)[0]]
                E_per_gamma[int(g)] = [allE[p_] for p_ in pos_list]
            return {
                's1': s1.tolist(), 's2': s2.tolist(),
                'p': p, 'm': m_actual,
                'gammas': [int(g) for g in unique_g],
                'E_per_gamma': E_per_gamma,
            }
    return None

def check_lemma_general(data, n, k, c, p):
    D = n - k; w = D - c
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    s1 = np.array(data['s1'], dtype=np.int64)
    s2 = np.array(data['s2'], dtype=np.int64)
    gammas = data['gammas']
    # Pick one E per gamma
    E_list = [data['E_per_gamma'][g][0] for g in gammas]
    m = len(gammas)

    # Build N matrices
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

    # Build A
    A = np.zeros((m * c, 2 * D), dtype=np.int64)
    for i in range(m):
        A[i*c:(i+1)*c, :D] = NE_list[i]
        A[i*c:(i+1)*c, D:] = (gammas[i] * NE_list[i]) % p

    # Verify A · (s1, s2) = 0
    v = np.concatenate([s1, s2])
    Av = (A @ v) % p
    print(f"  A·v = {Av.tolist()[:6]}... (zeros expected)")
    print(f"  All zero: {np.all(Av == 0)}")

    # Compute rank
    def rank_modp(M, p):
        M = M.copy() % p
        rows, cols = M.shape
        rank = 0
        for col in range(cols):
            pv = None
            for r in range(rank, rows):
                if M[r, col] != 0: pv = r; break
            if pv is None: continue
            M[[rank, pv]] = M[[pv, rank]]
            inv = pow(int(M[rank, col]), p-2, p)
            M[rank] = (M[rank] * inv) % p
            for r in range(rows):
                if r != rank and M[r, col] != 0:
                    M[r] = (M[r] - M[r, col] * M[rank]) % p
            rank += 1
        return rank
    rank = rank_modp(A, p)
    full_rank = min(m * c, 2 * D)
    print(f"  rank A = {rank}, min(mc, 2D) = {full_rank}, deficient: {rank < full_rank}")

    # Check open conditions
    a_0_vals = []
    for i in range(m):
        n0 = NE_list[i][0]
        a0 = int((n0 @ s2) % p)
        a_0_vals.append(a0)
    print(f"  ⟨n_0(E_i), s_2⟩ = {a_0_vals}")
    all_nz = all(a != 0 for a in a_0_vals)
    print(f"  All nonzero: {all_nz}")

    if rank < full_rank and all_nz:
        print(f"  ⚠️ LEMMA DISPROVED at c={c}, p={p}, m={m}")
        return False
    return True

if __name__ == '__main__':
    n, k, c = 12, 6, 3
    bound = (2 * (n - k) - 1) // c
    print(f"=== Looking for c={c} lemma counterexample at n={n} ===")
    print(f"bound = {bound}")

    for p in [61, 73, 97, 109, 157, 181, 193, 229, 277, 313]:
        print(f"\n--- p={p} ---")
        data = find_witness_general(n, k, c, p, target_m=bound+1, n_trials=200000)
        if data is None:
            print(f"  No m >= {bound+1} found")
            continue
        print(f"  Found m = {data['m']}")
        print(f"  γ values: {data['gammas'][:bound+2]}...")
        check_lemma_general(data, n, k, c, p)
        # Stop after finding first counterexample
        if data['m'] > bound:
            break
