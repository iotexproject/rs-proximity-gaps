#!/usr/bin/env python3 -u
"""For each route type at c=4, measure codim contribution empirically.

For a fixed (E_1, ..., E_m) bad config:
- Compute rank A(γ) and dim X_γ across many γ
- The "per-config codim" = 2D - max_dim_V_bad_via_this_config
- Density estimate: count (γ, s_1, s_2) realizations / p^{2D + m}

Then for each route class, multiply by # configs in that class to get the
total V_bad density contribution.
"""

import sys
import numpy as np
from itertools import combinations
from collections import Counter, defaultdict
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_pattern_C_rank_structure import dim_x_gamma
from op2_pattern_C_analysis import hypergraph_signature
from op2_pattern_C_star_topology import intersection_graph, topology_signature
from op2_subperiod_test import find_sub_tet
from op2_clique_scan import kernel_mod
from op2_tet_consolidated import make_NEs, solve_for_witness


def rank_A_distribution(Es, L, p, D, c, n_gammas=30):
    """For fixed Es, sample n_gammas random γ-tuples, return distribution of
    rank A(γ) and dim ker A in (s_1, s_2)-space."""
    m = len(Es)
    w = len(Es[0])
    NEs = make_NEs(Es, L, p, D, c, w)
    rng = np.random.default_rng(7)
    rank_dist = Counter()
    for _ in range(n_gammas):
        gammas = (rng.choice(p - 1, size=m, replace=False) + 1).tolist()
        A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
        rank_dist[(rA, len(ker))] += 1
    return rank_dist


def measure_route_codim(n, c, p, n_trials=20000):
    k = n // 2
    D = n - k; w = D - c
    m = (2 * D - 1) // c + 1
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    all_supports = list(combinations(range(n), w))
    rng = np.random.default_rng(2)
    print(f"=== c={c} per-route codim at n={n} m={m} p={p} target codim {2*D-(m-1)-2} ===")

    # Find one example per route class (sub-tet status + dim X_γ behavior)
    samples_per_class = defaultdict(list)
    for trial in range(n_trials):
        idx = rng.choice(len(all_supports), size=m, replace=False)
        Es = [all_supports[i] for i in idx]
        sub_tet = find_sub_tet(Es, n)
        sig = hypergraph_signature(Es)
        edges = intersection_graph(Es)
        topo = topology_signature(edges, m)
        deg = [0] * n
        for E in Es:
            for u in E: deg[u] += 1
        n_shared = sum(1 for d in deg if d == 2)
        # rd test
        gammas_list = []
        for tg in range(2):
            gammas = (rng.choice(p - 1, size=m, replace=False) + 1).tolist()
            gammas_list.append(gammas)
        d1 = dim_x_gamma(Es, gammas_list[0], L, p, c)
        d2 = dim_x_gamma(Es, gammas_list[1], L, p, c)
        rd = d1 >= 1 and d2 >= 1

        key = (bool(sub_tet), n_shared, topo, rd)
        if len(samples_per_class[key]) < 3:
            samples_per_class[key].append(Es)
        if all(len(v) >= 3 for v in samples_per_class.values()) and len(samples_per_class) >= 8:
            break

    # For each class, measure rank A distribution at one example
    print(f"\n  Per-class rank A behavior (30 random γ each):")
    for key, examples in sorted(samples_per_class.items(),
                                  key=lambda x: -len(x[1])):
        if not examples: continue
        Es = examples[0]
        rank_dist = rank_A_distribution(Es, L, p, D, c)
        max_ker = max(k_ for (r, k_) in rank_dist.keys())
        ker_implied_codim = 2 * D - max_ker
        st, ns, topo, rd = key
        print(f"    [sub_tet={st}, n_shared={ns}, topo={topo}, rd={rd}]")
        print(f"      example Es={Es}")
        print(f"      rank A dist: {dict(rank_dist)}")
        print(f"      max ker dim = {max_ker} → per-config codim ≈ {ker_implied_codim}")


def measure_v_bad_density_at_c4(n, c, p, n_trials=200000):
    """Direct V_bad density: sample (s_1, s_2), count realizations."""
    k = n // 2
    D = n - k; w = D - c
    m = (2 * D - 1) // c + 1
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    all_supports = list(combinations(range(n), w))
    rng = np.random.default_rng(3)
    print(f"\n=== Direct V_bad density at c={c} n={n} p={p} (sample {n_trials}) ===")
    print(f"  T = {m-1}, looking for M(s1,s2) > T")

    # For each (s_1, s_2), count # E with γ such that s_1 + γ s_2 ∈ ker N_E
    bad_count = 0
    for trial in range(n_trials):
        s1 = rng.integers(0, p, D)
        s2 = rng.integers(0, p, D)
        if all(s == 0 for s in s2): continue
        # For each support E, compute the unique γ_E (if exists) making
        # s_1 + γ_E s_2 ∈ ker N_E. Then check γ_E uniqueness across E's.
        # Actually: M(s_1, s_2) = number of γ such that ∃ E with s_1+γs_2 ∈ ker N_E.
        # Each E contributes at most c distinct γ's (where the determinant
        # of c × c minor = 0). For M > T = m-1, need T+1 = m distinct γ.

        # Quick approximation: check if s_2 is bad (rank N_E(s_2) < c) for many E.
        # This is too expensive. Skip detailed check.
        pass

    # Better: use the known route classification and count
    # # rd-star at c=4, # sub-tet at c=4, multiply by per-config density.


if __name__ == '__main__':
    n = 16; c = 4
    primes = [97, 193, 257, 449, 577, 1009, 1153, 1217, 1601, 1697]
    p = next((q for q in primes if (q - 1) % n == 0), None)
    measure_route_codim(n, c, p, n_trials=50000)

    print("\n--- compare c=3 baseline ---")
    n3 = 12; c3 = 3
    primes3 = [97, 193, 257, 449, 577, 1009, 1153, 1217, 1601, 1697]
    p3 = next((q for q in primes3 if (q - 1) % n3 == 0), None)
    measure_route_codim(n3, c3, p3, n_trials=20000)
