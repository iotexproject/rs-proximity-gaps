#!/usr/bin/env python3 -u
"""Measure dim V_tet_sub by sampling within the 8-dim linear span Σ ker A.

V_tet_sub ⊂ Σ_γ ker A(γ) (a F_p-subspace of dim D_span).
Density |V_tet_sub| / |Σ ker A| = p^{dim V_tet_sub - D_span}.

If density ≈ 1, dim V_tet_sub = D_span.
If density ≈ p^{-k}, dim V_tet_sub = D_span - k.
"""

import sys
import numpy as np
from itertools import combinations, product
import math
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_clique_scan import rank_mod, kernel_mod
from op2_tet_consolidated import make_NEs, solve_for_witness
from op2_pattern_C_rank_structure import dim_x_gamma


def build_8dim_span(NEs, p, D, c, n_gammas=100, seed=0):
    rng = np.random.default_rng(seed)
    m = len(NEs)
    accumulated = []
    for trial in range(n_gammas):
        gammas = (rng.choice(p - 1, size=m, replace=False) + 1).tolist()
        A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
        for v in ker:
            accumulated.append(v)
    M = np.array(accumulated, dtype=np.int64) % p
    # Compute reduced basis
    M_rref = M.copy()
    R, C = M_rref.shape
    pivot_cols = []
    r = 0
    for col in range(C):
        if r >= R: break
        pv = None
        for i in range(r, R):
            if M_rref[i, col] != 0: pv = i; break
        if pv is None: continue
        M_rref[[r, pv]] = M_rref[[pv, r]]
        inv = pow(int(M_rref[r, col]), p - 2, p)
        M_rref[r] = (M_rref[r] * inv) % p
        for i in range(R):
            if i != r and M_rref[i, col] != 0:
                M_rref[i] = (M_rref[i] - M_rref[i, col] * M_rref[r]) % p
        pivot_cols.append(col); r += 1
    basis = M_rref[:r]
    return basis  # r × 2D matrix, basis of the span


def is_in_v_tet_sub(s1, s2, NEs, p, c):
    """Check if (s1, s2) is in V_tet_sub: ∃ γ_i ∈ F_p^* distinct, s_1+γ_i s_2 ∈ V_{E_i}."""
    gammas = []
    for N in NEs:
        aE = (N @ s2) % p
        bE = (N @ s1) % p
        nz = next((j for j in range(c) if aE[j] != 0), None)
        if nz is None:
            if any(bE):
                return False, None
            gammas.append('free'); continue
        g = (-int(bE[nz]) * pow(int(aE[nz]), p - 2, p)) % p
        prop = all(
            (int(aE[j_]) * int(bE[k_]) - int(aE[k_]) * int(bE[j_])) % p == 0
            for j_ in range(c) for k_ in range(c)
        )
        if not prop or g == 0:
            return False, None
        gammas.append(g)
    # Check distinct (with free positions assignable)
    fixed = [g for g in gammas if g != 'free']
    n_free = sum(1 for g in gammas if g == 'free')
    if len(set(fixed)) != len(fixed): return False, gammas
    # If any free positions, need to assign distinct values
    if n_free > 0 and len(fixed) + n_free > p - 1:
        return False, gammas
    return True, gammas


def measure_density(n, c, primes_to_test, n_samples=2000):
    print(f"=== Density of V_tet_sub in 8-dim span at c={c} sub-tet ===")
    V = [0, 1, 2, 3]
    U = [4, 5, 6, 7]
    for p in primes_to_test:
        if (p - 1) % n != 0: continue
        D = n - n // 2; w = D - c
        omega = find_omega(n, p)
        L = [pow(omega, i, p) for i in range(n)]
        Es = [tuple(sorted([v for v in V if v != V[i]] + [U[i]])) for i in range(len(V))]
        NEs = make_NEs(Es, L, p, D, c, w)

        basis = build_8dim_span(NEs, p, D, c, n_gammas=200)
        D_span = basis.shape[0]
        rng = np.random.default_rng(123)
        n_in = 0
        gamma_class = {}
        for trial in range(n_samples):
            coefs = rng.integers(0, p, D_span)
            v = (coefs @ basis) % p
            s1 = v[:D]; s2 = v[D:]
            in_v, gammas = is_in_v_tet_sub(s1, s2, NEs, p, c)
            if in_v:
                n_in += 1
        density = n_in / n_samples
        if density > 0:
            log_p_density = math.log(density) / math.log(p)
        else:
            log_p_density = -math.inf
        print(f"  p={p}: D_span={D_span}, samples={n_samples}, in V_tet_sub: {n_in} ({density:.4%})")
        if density > 0:
            print(f"    log_p(density) ≈ {log_p_density:.3f} → dim V_tet_sub ≈ {D_span + log_p_density:.3f}")


if __name__ == '__main__':
    n = 16; c = 4
    primes = [17, 97, 193, 257, 449, 577, 1009]
    measure_density(n, c, primes, n_samples=2000)
