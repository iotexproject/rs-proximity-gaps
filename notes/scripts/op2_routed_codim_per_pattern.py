#!/usr/bin/env python3 -u
"""Per-route codim measurement at varying p.

For each route (Tet, Sub-tet/A, Sub-tet/B, Sub-tet/D, Pattern-C):
- Pick a representative (E_1, ..., E_m) configuration
- Sample (s_1, s_2) randomly
- Count fraction with M > T realized via that specific route
- Vary p ∈ {97, 257, 1009, 4001} to extract codim asymptotically
"""

import sys
import numpy as np
from itertools import combinations, permutations
from collections import Counter
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_clique_scan import rank_mod, kernel_mod
from op2_tet_consolidated import make_NEs, solve_for_witness
from op2_bad_set_chars import has_tetrahedron
from op2_subperiod_test import find_sub_tet


def find_p_with_omega(n, primes):
    """Pick primes ≡ 1 mod n with available omega."""
    valid = [p for p in primes if (p - 1) % n == 0]
    return valid


def compute_v_rd_density(Es, p, n, k, c, n_samples=200000, seed=0):
    """Sample (γ_1, ..., γ_m) ∈ (F_p^*)^m and measure
    Pr[rank A(γ) < min(mc, 2D)] = density of V_rd.
    Returns (density, mean_rank_deficit).
    """
    D = n - k; w = D - c
    m = len(Es)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    NEs = make_NEs(Es, L, p, D, c, w)
    rng = np.random.default_rng(seed)
    full_rank = min(m * c, 2 * D)
    n_rd = 0
    rd_dim_sum = 0
    for trial in range(n_samples):
        # Sample distinct γ_j ∈ F_p^*
        gammas = rng.choice(p - 1, size=m, replace=False) + 1
        gammas = gammas.tolist()
        A = np.zeros((m * c, 2 * D), dtype=np.int64)
        for j in range(m):
            A[j*c:(j+1)*c, :D] = NEs[j]
            A[j*c:(j+1)*c, D:] = (int(gammas[j]) * NEs[j]) % p
        rA = rank_mod(A, p)
        if rA < full_rank:
            n_rd += 1
            rd_dim_sum += full_rank - rA
    return n_rd / n_samples, (rd_dim_sum / max(n_rd, 1)) if n_rd > 0 else 0


def compute_route_codim(Es, primes_list, n, k, c, n_samples=200000):
    """Measure V_rd density at each p in primes_list, derive codim."""
    print(f"  Es={Es}")
    print(f"  {'p':>8} {'V_rd density':>15} {'avg deficit':>12} {'log_p density':>15}")
    densities = []
    for p in primes_list:
        if find_omega(n, p) is None: continue
        d, deficit = compute_v_rd_density(Es, p, n, k, c, n_samples=n_samples)
        log_d = -np.log(d) / np.log(p) if d > 0 else float('inf')
        densities.append((p, d, log_d))
        print(f"  {p:>8} {d:>15.6e} {deficit:>12.2f} {log_d:>15.4f}")
    return densities


def find_one_realizable_config(pattern_name, has_sub_tet_required, n, k, c, p, m, n_trials=10000):
    """Find one realizable bad config of given pattern (sub-tet or not)."""
    D = n - k; w = D - c
    omega = find_omega(n, p)
    if omega is None: return None
    L = [pow(omega, i, p) for i in range(n)]
    all_supports = list(combinations(range(n), w))
    rng = np.random.default_rng(0)
    for trial in range(n_trials):
        idx = rng.choice(len(all_supports), size=m, replace=False)
        Es = [all_supports[i] for i in idx]
        if has_tetrahedron(Es, w)[0]: continue
        sub_tets = find_sub_tet(Es, n)
        if has_sub_tet_required and not sub_tets: continue
        if not has_sub_tet_required and sub_tets: continue
        gammas = []; seen = set()
        while len(gammas) < m:
            g = int(rng.integers(2, p))
            if g not in seen: gammas.append(g); seen.add(g)
        NEs = make_NEs(Es, L, p, D, c, w)
        A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
        if rA == min(m * c, 2 * D): continue
        return Es
    return None


if __name__ == '__main__':
    # Test at n=12, c=3 first
    n, k, c = 12, 6, 3
    D = n - k; w = D - c
    m = (2 * D - 1) // c + 1
    target_codim = 2 * D - m - 1  # 2D - T - 2 with T = m - 1, so 2D - m - 1

    primes = [97, 193, 257, 1009, 4001]
    valid_primes = [p for p in primes if (p - 1) % n == 0]
    print(f"=== Routed codim measurement at n={n} c={c} m={m} ===")
    print(f"Target codim: 2D - T - 2 = {target_codim}")
    print(f"Valid primes (p ≡ 1 mod {n}): {valid_primes}\n")

    print("--- Tet route (full w+1 clique) ---")
    # Standard tet on V = {0, 1, 2, 3}
    V_tet = (0, 1, 2, 3)
    Es_tet = [tuple(sorted(set(V_tet) - {v})) for v in V_tet]
    # But these are size w' = w = 3 ✓
    print(f"  Es_tet={Es_tet} (V = {V_tet})")
    compute_route_codim(Es_tet, valid_primes, n, k, c, n_samples=100000)
    print()

    print("--- Sub-tet route (Pattern A): 3 of 4 supports cover w'=2 sub-tet ---")
    Es_A = find_one_realizable_config("A", True, n, k, c, valid_primes[0], m, n_trials=10000)
    if Es_A:
        compute_route_codim(Es_A, valid_primes, n, k, c, n_samples=100000)
    else:
        print("  No Pattern A config found.")
    print()

    print("--- Pattern C route: no sub-tet ---")
    Es_C = find_one_realizable_config("C", False, n, k, c, valid_primes[0], m, n_trials=20000)
    if Es_C:
        compute_route_codim(Es_C, valid_primes, n, k, c, n_samples=100000)
    else:
        print("  No Pattern C config found.")
    print()
