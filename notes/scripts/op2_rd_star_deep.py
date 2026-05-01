#!/usr/bin/env python3 -u
"""Deep analysis of rd-Pattern-C-star: find the analytic relation in (L_v).

Strategy:
1. Collect a larger sample of rd-stars (>=50).
2. For each rd-star, extract its full structural data: E_c, leaves, U_i,
   L-values, basis vector of X_γ.
3. Look for relations across the dataset:
   - Sum/product of subsets of L-values
   - Cross-ratios
   - Polynomial relations via Groebner-style elimination
4. Test if the rd-star variety is cut out by a SINGLE polynomial in
   (L_v)_{v ∈ ⋃ E_j} (i.e., codim 1) — Schwartz-Zippel-friendly.
"""

import sys
import numpy as np
from itertools import combinations
from collections import Counter
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_pattern_C_rank_structure import (dim_x_gamma,
                                            construct_x_gamma_basis)
from op2_pattern_C_analysis import is_pattern_C
from op2_pattern_C_star_topology import intersection_graph, topology_signature
from op2_subperiod_test import find_sub_tet


def extract_star_structure(Es):
    """For a Pattern C star, identify central E_c, the 3 leaves, shared
    vertices, and extras of each leaf."""
    edges = intersection_graph(Es)
    deg = [0] * len(Es)
    for i, j in edges:
        deg[i] += 1; deg[j] += 1
    if 3 not in deg: return None
    central_idx = next(i for i, d in enumerate(deg) if d == 3)
    leaves_idx = [i for i in range(len(Es)) if i != central_idx]
    E_c = Es[central_idx]
    leaf_data = []
    for li in leaves_idx:
        E_l = Es[li]
        shared = list(set(E_c) & set(E_l))
        if len(shared) != 1: return None
        v_share = shared[0]
        extras = tuple(sorted(set(E_l) - {v_share}))
        leaf_data.append({'idx': li, 'E': E_l, 'v_share': v_share,
                           'extras': extras})
    return {'central_idx': central_idx, 'E_c': E_c, 'leaves': leaf_data}


def find_rd_stars_large(n, p, n_target=80, n_trials=500000):
    k = n // 2; c = 3
    D = n - k; w = D - c
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    all_supports = list(combinations(range(n), w))
    rng = np.random.default_rng(1)

    rd_stars = []
    n_pc = n_star = 0
    for trial in range(n_trials):
        idx = rng.choice(len(all_supports), size=4, replace=False)
        Es = [all_supports[i] for i in idx]
        if not is_pattern_C(Es, n): continue
        if find_sub_tet(Es, n): continue
        n_pc += 1
        edges = intersection_graph(Es)
        if topology_signature(edges, 4) != 'star': continue
        n_star += 1
        rd = True
        for tg in range(3):
            gammas = (rng.choice(p - 1, size=4, replace=False) + 1).tolist()
            d = dim_x_gamma(Es, gammas, L, p, c)
            if d == 0: rd = False; break
        if rd:
            rd_stars.append(Es)
            if len(rd_stars) >= n_target: break
    print(f"Trials: {trial+1}, Pattern C: {n_pc}, stars: {n_star},"
          f" rd-stars: {len(rd_stars)}")
    return rd_stars, L


def analyze_rd_star_invariants(rd_stars, L, p, n):
    """For each rd-star, compute several candidate invariants. Check if any
    is identically a fixed value or relates to the structure."""
    print(f"\n=== Invariants for {len(rd_stars)} rd-stars ===")
    print(f"{'#':>3} {'E_c':>16} {'shares':>20} {'sum_E_c':>10} "
          f"{'prod_E_c':>10} {'cross_ratio':>15}")
    sum_dist = Counter()
    prod_dist = Counter()
    cr_dist = Counter()

    for k_, Es in enumerate(rd_stars):
        s = extract_star_structure(Es)
        if s is None: continue
        E_c = s['E_c']
        L_E_c = [L[v] for v in E_c]
        shares = sorted(s['leaves'][i]['v_share'] for i in range(3))
        sum_v = sum(E_c) % n
        prod_L = 1
        for x in L_E_c: prod_L = (prod_L * x) % p
        # Cross ratio of (L_a, L_b, L_c, ?) — pick leaves' first extras
        ext_a = s['leaves'][0]['extras']
        ext_b = s['leaves'][1]['extras']
        ext_c = s['leaves'][2]['extras']
        # All 6 L's of the leaves (extras)
        leaf_extras_v = sorted(set(ext_a) | set(ext_b) | set(ext_c))
        # Try: sum of all extras' indices
        sum_ext = sum(leaf_extras_v) % n
        # Cross-ratio (L_a - L_b)(L_c - L_d) / ... — using the 3 shared verts
        # and arbitrary 4th vertex... for now just compute:
        L_v1, L_v2, L_v3 = L_E_c
        # Symmetric functions of L_E_c:
        # e1 = L_v1 + L_v2 + L_v3
        # e2 = L_v1 L_v2 + L_v1 L_v3 + L_v2 L_v3
        # e3 = L_v1 L_v2 L_v3 = prod_L
        e1 = (L_v1 + L_v2 + L_v3) % p
        e2 = (L_v1 * L_v2 + L_v1 * L_v3 + L_v2 * L_v3) % p
        e3 = prod_L
        cr = (e1, e2, e3)
        sum_dist[sum_v] += 1
        prod_dist[prod_L] += 1
        cr_dist[(e1 == 0, e2 == 0, e3 == 0)] += 1
        if k_ < 30:
            print(f"{k_:>3} {str(E_c):>16} {str(shares):>20} {sum_v:>10} "
                  f"{prod_L:>10} {str((e1,e2,e3))[:15]:>15}")
    print(f"\n  sum(E_c) mod {n} distribution: {dict(sum_dist)}")
    print(f"  prod L_E_c distribution top-5: {prod_dist.most_common(5)}")
    print(f"  (e1=0, e2=0, e3=0) joint: {dict(cr_dist)}")


def study_basis_vector_structure(rd_stars, L, p):
    """For each rd-star, the basis vector of X_γ has 4 components ĥ_j.
    Examine which components are zero and what relations they satisfy."""
    print(f"\n=== X_γ basis vector structure ===")
    rng = np.random.default_rng(0)
    c = 3
    zero_pat = Counter()
    for k_, Es in enumerate(rd_stars[:20]):
        s = extract_star_structure(Es)
        gammas = (rng.choice(p - 1, size=4, replace=False) + 1).tolist()
        basis = construct_x_gamma_basis(Es, gammas, L, p, c)
        if not basis: continue
        v = basis[0]
        h = [v[j*c:(j+1)*c] for j in range(4)]
        nonzero = tuple(any(int(x) != 0 for x in h[j]) for j in range(4))
        zero_pat[nonzero] += 1
        # Identify which support is central
        cidx = s['central_idx']
        if k_ < 5:
            print(f"  rd-star #{k_}: central_idx={cidx}, ĥ nonzero pattern={nonzero}")
            for j in range(4):
                print(f"    ĥ_{j} (E={Es[j]}, {'CENTRAL' if j == cidx else 'leaf'}): "
                      f"{[int(x) for x in h[j]]}")
    print(f"\n  Nonzero patterns across 20 rd-stars: {dict(zero_pat)}")


def test_eliminate_relation(rd_stars, L, p):
    """For each rd-star, compute a candidate polynomial relation among the
    10 L-values (3 shares + 6 extras + 1 unused vertex). Test if a low-degree
    relation holds.

    Specifically: for each rd-star, fit (s_1, s_2) realizing all 4 γ's as bad,
    and check if the witness lives in a low-codim subspace.
    """
    print(f"\n=== Testing eliminating polynomial existence ===")
    # For each rd-star, assert dim X_γ = 1 for several γ-tuples
    # Compute the basis vector h, evaluate ĥ_j at L_v for all v ∈ ⋃ E_j
    # Look for "extra" zeros = forced relations
    rng = np.random.default_rng(0)
    c = 3
    for k_, Es in enumerate(rd_stars[:5]):
        gammas = (rng.choice(p - 1, size=4, replace=False) + 1).tolist()
        basis = construct_x_gamma_basis(Es, gammas, L, p, c)
        if not basis: continue
        v_basis = basis[0]
        h = [v_basis[j*c:(j+1)*c] for j in range(4)]
        # Evaluate ĥ_j(L_v) for all v ∈ [n]
        forced_zeros = []
        for v in range(len(L)):
            for j in range(4):
                val = sum(int(h[j][k]) * pow(L[v], k, p) for k in range(c)) % p
                if val == 0 and v not in Es[j]:
                    forced_zeros.append((j, v))
        print(f"  rd-star #{k_}: Es={Es}")
        print(f"    forced zeros (j, v) where ĥ_j(L_v) = 0 and v ∉ E_j:")
        for fz in forced_zeros:
            print(f"      ĥ_{fz[0]}(L_{fz[1]}) = 0   [E_{fz[0]} = {Es[fz[0]]}]")


if __name__ == '__main__':
    n = 12; p = 1009
    print(f"=== Deep rd-Pattern-C-star analysis at n={n} p={p} ===\n")
    rd_stars, L = find_rd_stars_large(n, p, n_target=50, n_trials=500000)
    if rd_stars:
        analyze_rd_star_invariants(rd_stars, L, p, n)
        study_basis_vector_structure(rd_stars, L, p)
        test_eliminate_relation(rd_stars, L, p)
