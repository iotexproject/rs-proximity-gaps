#!/usr/bin/env python3 -u
"""Measure density of V_bad ∩ {fixed E-tuple} in (s_1, s_2)-space.

For fixed (E_1, ..., E_m), V_bad-via-E := {(s_1, s_2) : ∃ γ_1, ..., γ_m
distinct in F_p^* with N_{E_j}(s_1 + γ_j s_2) = 0 ∀j}.

Sample (s_1, s_2) uniformly, count fraction in V_bad-via-E.
log_p density gives codim. Vary p to extract asymptotic codim.
"""

import sys
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_clique_scan import rank_mod, kernel_mod
from op2_tet_consolidated import make_NEs


def realizes_E(s, NE, p, c):
    """For (s_1, s_2) and N_E, return γ ∈ F_p^* with N_E(s_1 + γ s_2) = 0,
    or None if no such γ. s = stacked (s_1, s_2) of length 2D."""
    D = NE.shape[1]
    s1 = s[:D] % p
    s2 = s[D:] % p
    aE = (NE @ s2.astype(np.int64)) % p
    bE = (NE @ s1.astype(np.int64)) % p
    # Want: bE + γ aE = 0, i.e., aE * γ = -bE component-wise must be consistent.
    # Find γ such that γ * aE[j] = -bE[j] for all j.
    nz = next((j for j in range(c) if int(aE[j]) != 0), None)
    if nz is None:
        # aE = 0, then need bE = 0 too
        if all(bE == 0): return -1  # any γ works; use sentinel
        return None
    g_candidate = (-int(bE[nz]) * pow(int(aE[nz]), p-2, p)) % p
    if g_candidate == 0: return None
    # Check consistency: γ * aE[j] + bE[j] == 0 for all j
    for j in range(c):
        if (g_candidate * int(aE[j]) + int(bE[j])) % p != 0:
            return None
    return g_candidate


def density_via_E(Es, p, n, k, c, n_samples=100000, seed=0):
    """Sample (s_1, s_2), count fraction realizing all m γ's distinctly."""
    D = n - k; w = D - c
    omega = find_omega(n, p)
    if omega is None: return None
    L = [pow(omega, i, p) for i in range(n)]
    NEs = make_NEs(Es, L, p, D, c, w)
    rng = np.random.default_rng(seed)
    m = len(Es)
    n_bad = 0
    for trial in range(n_samples):
        s = rng.integers(0, p, size=2 * D)
        gammas = []
        ok = True
        for j in range(m):
            g = realizes_E(s, NEs[j], p, c)
            if g is None or g == -1:
                ok = False; break
            if g in gammas:
                ok = False; break
            gammas.append(g)
        if ok and len(set(gammas)) == m:
            n_bad += 1
    return n_bad / n_samples


def measure_route(Es, primes, n, k, c, n_samples=200000, label=""):
    """Sweep p, return list of (p, density, codim_estimate)."""
    print(f"--- {label} ---")
    print(f"  Es={Es}")
    print(f"  {'p':>8} {'density':>15} {'log_p':>10} {'codim_est':>10}")
    out = []
    for p in primes:
        if (p - 1) % n != 0: continue
        if find_omega(n, p) is None: continue
        d = density_via_E(Es, p, n, k, c, n_samples=n_samples)
        if d is None: continue
        log_d = -np.log(max(d, 1e-50)) / np.log(p)
        out.append((p, d, log_d))
        print(f"  {p:>8} {d:>15.6e} {log_d:>10.4f}")
    return out


if __name__ == '__main__':
    # Sub-task 1: n=12 c=3 m=4
    n, k, c = 12, 6, 3
    D = n - k; w = D - c
    m = (2 * D - 1) // c + 1
    target_codim = 2 * D - m - 1
    primes = [13, 37, 61, 97, 109, 157, 181, 193, 229, 277, 337, 397, 421, 457, 541, 601, 661, 757, 829, 877, 937, 1009]
    primes_n12 = [p for p in primes if (p - 1) % n == 0]
    print(f"=== n={n} c={c} m={m}, target codim = {target_codim} ===\n")

    # Tet
    V_tet = (0, 1, 2, 3)
    Es_tet = [tuple(sorted(set(V_tet) - {v})) for v in V_tet]
    measure_route(Es_tet, primes_n12, n, k, c, n_samples=300000, label="Tet route")
    print()

    # Sub-tet (Pattern A example)
    Es_A = [(1, 2, 7), (2, 4, 8), (4, 10, 11), (3, 4, 7)]
    measure_route(Es_A, primes_n12, n, k, c, n_samples=300000, label="Sub-tet (Pattern A)")
    print()

    # Pattern C example
    Es_C = [(5, 6, 8), (0, 4, 7), (2, 7, 8), (3, 8, 9)]
    measure_route(Es_C, primes_n12, n, k, c, n_samples=300000, label="Pattern C")
    print()

    # Random non-bad config (for baseline)
    Es_rand = [(0, 1, 5), (2, 3, 6), (4, 7, 8), (9, 10, 11)]
    measure_route(Es_rand, primes_n12, n, k, c, n_samples=300000, label="Random (mostly disjoint)")
