#!/usr/bin/env python3 -u
"""Comprehensive catalog of c=4 routes at n=16.

At n=16, c=4, m=4: tet route is EMPTY (w+1 = 5 > m = 4). So routes are:
- Sub-tet (w' < w = 4): w'=2 (3 sub-tet supports + 1 extra) or w'=3 (4 sub-tet)
- Pattern C analog at c=4: signature (0,0,0,1,1,1), various # shared
- Generic non-rd

For each non-sub-tet bad config, classify by:
- Pair intersection signature
- # degree-2 vertices (= # shared in star topology)
- Intersection graph topology
- dim X_γ behavior (rd vs non-rd)

Goal: find the BOTTLENECK route at c=4 contributing codim 2D-T-2 = 11
(or determine that the bound is 10 instead of 11).
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
from op2_bad_set_chars import has_tetrahedron
from op2_shifted_syzygy import shifted_syzygy_solvable


def classify_pattern(Es, n):
    """Return a structured classification key for a 4-tuple of supports."""
    deg = [0] * n
    for E in Es:
        for v in E: deg[v] += 1
    deg_dist = tuple(sorted((d, c_) for d, c_ in Counter(deg).items() if d > 0))
    sig = hypergraph_signature(Es)
    edges = intersection_graph(Es)
    topo = topology_signature(edges, len(Es))
    union_size = sum(1 for d in deg if d > 0)
    return {
        'deg_dist': deg_dist,
        'sig': sig,
        'topo': topo,
        'union_size': union_size,
        'n_shared': sum(1 for d in deg if d == 2),  # # vertices of degree 2
    }


def find_bad_configs(n, c, p, n_trials=20000):
    """Find ALL bad configurations (including sub-tet, pattern C analog)."""
    k = n // 2
    D = n - k; w = D - c
    m = (2 * D - 1) // c + 1
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    all_supports = list(combinations(range(n), w))
    rng = np.random.default_rng(2)

    bads = []
    for trial in range(n_trials):
        idx = rng.choice(len(all_supports), size=m, replace=False)
        Es = [all_supports[i] for i in idx]
        if has_tetrahedron(Es, w)[0]: continue
        gammas = []; seen = set()
        while len(gammas) < m:
            g = int(rng.integers(2, p))
            if g not in seen: gammas.append(g); seen.add(g)
        NEs = make_NEs(Es, L, p, D, c, w)
        A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
        if rA == min(m * c, 2 * D): continue
        any_i = any(shifted_syzygy_solvable(NEs, gammas, i_, p, D, c)
                    for i_ in range(m))
        if any_i: continue
        v = ker[0]
        s1 = v[:D].astype(np.int64); s2 = v[D:].astype(np.int64)
        all_realize = True
        for i_ in range(m):
            N = NEs[i_]
            aE = (N @ s2) % p; bE = (N @ s1) % p
            nz = next((j for j in range(c) if aE[j] != 0), None)
            if nz is None: all_realize = False; break
            prop = all(
                (int(aE[j_]) * int(bE[k_]) - int(aE[k_]) * int(bE[j_])) % p == 0
                for j_ in range(c) for k_ in range(c)
            )
            if not prop: all_realize = False; break
            gd = (-int(bE[nz]) * pow(int(aE[nz]), p-2, p)) % p
            if gd != gammas[i_]: all_realize = False; break
        if all_realize:
            bads.append({'Es': Es, 'gammas': gammas, 'rank': rA, 'ker_dim': len(ker)})
    return bads, L, m


def catalog_c4(n, c, p, n_trials):
    print(f"=== c=4 routes catalog at n={n} c={c} p={p} ===")
    bads, L, m = find_bad_configs(n, c, p, n_trials)
    k_ = n // 2; D = n - k_; w = D - c
    print(f"\n  Bad configs found: {len(bads)} in {n_trials} trials")
    print(f"  Target codim 2D-T-2 = {2*D - (m-1) - 2}")

    # Classify each bad
    rng = np.random.default_rng(99)
    by_class = defaultdict(list)
    for bad in bads:
        Es = bad['Es']
        cl = classify_pattern(Es, n)
        sub_tets = find_sub_tet(Es, n)
        cl['has_sub_tet'] = bool(sub_tets)
        # find_sub_tet returns list of (V_tuple, mapping)
        cl['sub_tet_w_prime'] = (max(len(st[0]) - 1 for st in sub_tets)
                                   if sub_tets else None)
        # rd test: dim X_γ stable across 3 random γ's
        rd = True
        for tg in range(3):
            gammas = (rng.choice(p - 1, size=m, replace=False) + 1).tolist()
            d = dim_x_gamma(Es, gammas, L, p, c)
            if d == 0: rd = False; break
        cl['rd'] = rd
        cl['ker_dim'] = bad['ker_dim']
        key = (cl['has_sub_tet'], cl['n_shared'], cl['topo'], cl['rd'])
        by_class[key].append((Es, cl))

    print(f"\n  Routes by (has_sub_tet, n_shared_verts, topology, rd):")
    print(f"  {'sub_tet':>8} {'n_shared':>9} {'topology':>16} {'rd':>4} {'count':>6}  example")
    for key in sorted(by_class.keys(), key=lambda k: -len(by_class[k])):
        st, ns, topo, rd = key
        configs = by_class[key]
        ex = configs[0][0]
        print(f"  {str(st):>8} {ns:>9} {topo:>16} {str(rd):>4} {len(configs):>6}  {ex}")

    # Summary by rd at non-sub-tet routes
    print(f"\n  Non-sub-tet routes summary:")
    non_st = [(k, v) for k, v in by_class.items() if k[0] is False]
    rd_count = sum(len(v) for k, v in non_st if k[3])
    nrd_count = sum(len(v) for k, v in non_st if not k[3])
    print(f"    non-sub-tet rd: {rd_count}")
    print(f"    non-sub-tet non-rd: {nrd_count}")


if __name__ == '__main__':
    n = 16; c = 4
    primes = [97, 193, 257, 449, 577, 1009, 1153, 1217, 1601, 1697]
    p = next((q for q in primes if (q - 1) % n == 0), None)
    catalog_c4(n, c, p, n_trials=50000)
