#!/usr/bin/env python3 -u
"""For rank-deficit Pattern C star configs, find the analytic condition.

Hypothesis: rank A = mc - 1 always for Pattern C star (det A ≡ 0) iff some
specific algebraic relation among (L_{v_a}, L_{v_b}, L_{v_d}, L_{u_*})
holds.

This is the analog of fri-conje-attack's locator-divisor closure (Note 0204):
rank deficit ↔ a polynomial identity in the L-values.
"""

import sys
import numpy as np
from itertools import combinations, permutations
from collections import Counter
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_pattern_C_rank_structure import dim_x_gamma, construct_x_gamma_basis
from op2_pattern_C_analysis import is_pattern_C
from op2_pattern_C_star_topology import intersection_graph, topology_signature
from op2_subperiod_test import find_sub_tet


def find_rank_deficit_stars(n, p, n_target=10, n_trials=200000):
    """Find rank-deficit Pattern C star configs."""
    k = n // 2; c = 3
    D = n - k; w = D - c
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    all_supports = list(combinations(range(n), w))
    rng = np.random.default_rng(0)

    rd_stars = []
    n_total = 0
    n_pc = 0
    n_star = 0
    trials_done = 0

    for trial in range(n_trials):
        trials_done += 1
        idx = rng.choice(len(all_supports), size=4, replace=False)
        Es = [all_supports[i] for i in idx]
        if not is_pattern_C(Es, n): continue
        if find_sub_tet(Es, n): continue
        n_pc += 1
        edges = intersection_graph(Es)
        if topology_signature(edges, 4) != 'star': continue
        n_star += 1
        # Check rank deficit at 3 random γ-tuples
        rd = True
        for trial_g in range(3):
            gammas = (rng.choice(p - 1, size=4, replace=False) + 1).tolist()
            d = dim_x_gamma(Es, gammas, L, p, c)
            if d == 0: rd = False; break
        if rd:
            rd_stars.append(Es)
            if len(rd_stars) >= n_target: break

    print(f"Sampled {trials_done} trials")
    print(f"  Pattern C: {n_pc}")
    print(f"  Pattern C star: {n_star}")
    print(f"  Pattern C star with rank deficit: {len(rd_stars)}")
    return rd_stars


def analyze_rd_star(Es, L, p, c):
    """For a rank-deficit Pattern C star, find the central support and
    structural relation."""
    edges = intersection_graph(Es)
    deg = [0] * len(Es)
    for i, j in edges:
        deg[i] += 1; deg[j] += 1
    # Central support has degree 3 in intersection graph
    central_idx = next(i for i, d in enumerate(deg) if d == 3)
    leaves = [i for i in range(len(Es)) if i != central_idx]
    E_c = Es[central_idx]
    # Identify shared vertices
    shared = []
    leaf_extras = []
    for leaf_idx in leaves:
        E_leaf = Es[leaf_idx]
        v_shared = set(E_c) & set(E_leaf)
        assert len(v_shared) == 1
        v = list(v_shared)[0]
        shared.append((v, leaf_idx))
        extras = tuple(sorted(set(E_leaf) - {v}))
        leaf_extras.append(extras)

    return {
        'E_c': E_c,
        'central_idx': central_idx,
        'shared_vertices': shared,
        'leaf_extras': leaf_extras,
        'L_E_c': [L[v] for v in E_c],
        'L_shared': [L[v] for v, _ in shared],
        'L_extras': [[L[u] for u in ex] for ex in leaf_extras],
    }


def look_for_relation(Es_list, L, p, c):
    """Look for a common algebraic relation among rank-deficit Pattern C stars."""
    print(f"\n=== Looking for relation among {len(Es_list)} rd-star configs ===")
    relations = []
    for Es in Es_list:
        analysis = analyze_rd_star(Es, L, p, c)
        E_c = analysis['E_c']
        L_E_c = analysis['L_E_c']
        L_shared = analysis['L_shared']
        # Test: do the 3 shared vertices satisfy a special relation?
        # E.g., sum to 0 in F_p? product = 1?
        s = sum(L_E_c) % p
        prod = 1
        for x in L_E_c: prod = (prod * x) % p
        prod_diff = 1
        for i in range(3):
            for j in range(i+1, 3):
                prod_diff = (prod_diff * (L_E_c[i] - L_E_c[j])) % p
        print(f"  E_c={E_c}: sum L = {s}, prod L = {prod}, prod (L_i - L_j) = {prod_diff}")
        relations.append((s, prod, prod_diff, analysis))
    return relations


def derive_det_A_polynomial(Es, gammas_symbolic, L, p, c):
    """Compute rank A symbolically (substitute concrete γ but track det).
    Just measure rank for many random γ as a sanity check."""
    rng = np.random.default_rng(123)
    ranks = []
    for trial in range(30):
        gammas = (rng.choice(p - 1, size=4, replace=False) + 1).tolist()
        d = dim_x_gamma(Es, gammas, L, p, c)
        ranks.append(d)
    return Counter(ranks)


if __name__ == '__main__':
    n, k, c = 12, 6, 3
    p = 1009
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    print(f"=== Pattern C star rank-deficit analysis at n={n} c={c} p={p} ===\n")

    rd_stars = find_rank_deficit_stars(n, p, n_target=15, n_trials=300000)
    if not rd_stars:
        print("No rank-deficit stars found. Try different L.")
    else:
        for Es in rd_stars[:5]:
            ranks = derive_det_A_polynomial(Es, None, L, p, c)
            print(f"\n  Es={Es}")
            print(f"    rank dim X_γ across 30 random γ: {ranks}")

        relations = look_for_relation(rd_stars, L, p, c)
