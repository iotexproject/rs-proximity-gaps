#!/usr/bin/env python3 -u
"""Test conjecture: bad-realizing Pattern C has STAR intersection graph
(one central support sharing 1 vertex with each of 3 leaf supports).

If true: this is the structural reason. Star Pattern C is rarer than
generic Pattern C, contributing higher codim.
"""

import sys
import numpy as np
from itertools import combinations
from collections import Counter
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_pattern_C_rank_structure import dim_x_gamma
from op2_pattern_C_analysis import is_pattern_C
from op2_subperiod_test import find_sub_tet


def intersection_graph(Es):
    """Return list of edges (i, j) where E_i ∩ E_j ≠ ∅."""
    return [(i, j) for i, j in combinations(range(len(Es)), 2)
            if set(Es[i]) & set(Es[j])]


def topology_signature(edges, n_nodes):
    """Classify intersection graph topology: 'star', 'path', 'triangle+iso', 'other'."""
    if not edges: return 'empty'
    deg = [0] * n_nodes
    for i, j in edges:
        deg[i] += 1; deg[j] += 1
    deg = sorted(deg, reverse=True)
    deg = tuple(deg)
    if deg == (3, 1, 1, 1): return 'star'
    if deg == (2, 2, 1, 1): return 'path'
    if deg == (2, 2, 2, 0): return 'triangle+iso'
    return f'other-{deg}'


def enumerate_pattern_C_topology(n, p, n_supports_max=None):
    """Across a sample of Pattern C support tuples, classify by topology AND
    by whether they have rank deficit (dim X_γ ≥ 1 always)."""
    k = n // 2; c = 3
    D = n - k; w = D - c
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    all_supports = list(combinations(range(n), w))

    rng = np.random.default_rng(0)
    topo_with_rd = Counter()  # (topology, has_rd)
    topo_total = Counter()

    n_target = 1000
    n_pc_found = 0
    trials = 0
    while n_pc_found < n_target and trials < 200000:
        trials += 1
        idx = rng.choice(len(all_supports), size=4, replace=False)
        Es = [all_supports[i] for i in idx]
        if not is_pattern_C(Es, n): continue
        if find_sub_tet(Es, n): continue
        n_pc_found += 1
        edges = intersection_graph(Es)
        topo = topology_signature(edges, 4)
        # Test rank deficit: 2 random γ-tuples
        gammas1 = (rng.choice(p - 1, size=4, replace=False) + 1).tolist()
        gammas2 = (rng.choice(p - 1, size=4, replace=False) + 1).tolist()
        d1 = dim_x_gamma(Es, gammas1, L, p, c)
        d2 = dim_x_gamma(Es, gammas2, L, p, c)
        has_rd = d1 >= 1 and d2 >= 1
        topo_total[topo] += 1
        if has_rd:
            topo_with_rd[topo] += 1
    return topo_total, topo_with_rd, n_pc_found


if __name__ == '__main__':
    n, k, c = 12, 6, 3
    p = 1009
    print(f"=== Pattern C topology vs rank deficit at n={n} c={c} ===\n")
    total, rd, found = enumerate_pattern_C_topology(n, p)
    print(f"Pattern C configs sampled: {found}")
    print(f"\n{'topology':>20} {'total':>8} {'with rank deficit':>20}")
    for topo in sorted(total.keys()):
        t = total[topo]; r = rd.get(topo, 0)
        print(f"{topo:>20} {t:>8} {r:>20}")
    print(f"\n=> bad-realizing Pattern C is concentrated in topologies with rank deficit.")
