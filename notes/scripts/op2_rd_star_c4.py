#!/usr/bin/env python3 -u
"""Verify rd-Pattern-C-star Lagrange characterization extends to c=4.

At n=16, k=8, D=8, w=4, c=4, m=T+1=4. Pattern C star = central E_c sharing
1 vertex with each of 3 leaves; leaves pairwise disjoint.

At c=3 each leaf ĥ_j is forced to vanish at 2 other shared vertices, so
ĥ_j ∈ span(Λ_{E_c}/(x-L_{v_j})) has dim 1. At c=4 same forced-zero count
(2), but deg ĥ_j < c = 4, so ĥ_j has 4 - 2 = 2 free coeffs.

So the basis of X_γ at c=4 should be larger than 1 even when rd holds.
"""

import sys
import numpy as np
from itertools import combinations
from collections import Counter
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_pattern_C_rank_structure import dim_x_gamma, construct_x_gamma_basis
from op2_pattern_C_analysis import hypergraph_signature
from op2_pattern_C_star_topology import intersection_graph, topology_signature
from op2_subperiod_test import find_sub_tet
from op2_rd_star_deep import extract_star_structure
from op2_rd_star_lagrange import pi_U_coeffs


def is_pattern_C_star_general(Es):
    """Pattern C signature (regardless of c): pair int (0,0,0,1,1,1), triple
    all 0, quad 0. Plus star intersection graph."""
    sig = hypergraph_signature(Es)
    if sig != ((0, 0, 0, 1, 1, 1), (0, 0, 0, 0), 0):
        return False
    edges = intersection_graph(Es)
    return topology_signature(edges, len(Es)) == 'star'


def det_mod(M, p):
    """det of np.array mod p via Gaussian elimination."""
    M = np.array(M, dtype=np.int64) % p
    n_ = M.shape[0]
    det = 1
    for i in range(n_):
        pivot = i
        while pivot < n_ and M[pivot, i] == 0:
            pivot += 1
        if pivot == n_: return 0
        if pivot != i:
            M[[i, pivot]] = M[[pivot, i]]
            det = (-det) % p
        det = (det * M[i, i]) % p
        inv = pow(int(M[i, i]), p - 2, p)
        for j in range(i + 1, n_):
            factor = (M[j, i] * inv) % p
            M[j] = (M[j] - factor * M[i]) % p
    return det


def rd_star_condition_general(Es, L, p, c):
    """For c-arity star: M is (c × c) matrix of Π_{U_j} coeffs (j over leaves).
    But we only have 3 leaves (Pattern C star = K_{1,3}). So M is c × 3, not
    c × c. Linear dependence ⇔ all 3-minors of c-rows × 3-cols = 0.

    Refined: the linear-dep condition for 3 polynomials of degree c-1 in
    F_p[x]_{<c} is: rank of (c × 3) matrix < 3. Equivalently, all
    3 × 3 minors vanish. There are C(c, 3) such minors.
    """
    s = extract_star_structure(Es)
    if s is None: return None
    leaves = s['leaves']
    cols = []
    for leaf in leaves:
        v_share = leaf['v_share']
        U = tuple(u for u in leaf['E'] if u != v_share)
        coeffs = pi_U_coeffs(U, L, p, c)
        cols.append(coeffs)  # length c each
    M = np.array(cols, dtype=np.int64).T  # (c × 3) matrix
    # Compute all 3x3 minors
    minors = []
    for rows in combinations(range(c), 3):
        sub = M[list(rows)]  # 3x3
        d = det_mod(sub, p)
        minors.append(d)
    return minors  # all should be 0 iff rank < 3


def verify_at_c4(n, p, n_target=300, n_trials=2000000):
    k = n // 2; c = n - k - (n - k - 4)  # = 4
    c = 4
    D = n - k; w = D - c
    print(f"n={n}, k={k}, D={D}, c={c}, w={w}")
    omega = find_omega(n, p)
    if omega is None:
        print("no omega"); return
    L = [pow(omega, i, p) for i in range(n)]
    all_supports = list(combinations(range(n), w))
    print(f"  total supports of size {w}: {len(all_supports)}")
    rng = np.random.default_rng(11)

    quadrants = Counter()
    examples = {q: [] for q in range(4)}
    n_star = 0
    for trial in range(n_trials):
        idx = rng.choice(len(all_supports), size=4, replace=False)
        Es = [all_supports[i] for i in idx]
        if not is_pattern_C_star_general(Es): continue
        if find_sub_tet(Es, n): continue
        n_star += 1
        minors = rd_star_condition_general(Es, L, p, c)
        if minors is None: continue
        all_zero = all(d == 0 for d in minors)
        rd = True
        for tg in range(2):
            gammas = (rng.choice(p - 1, size=4, replace=False) + 1).tolist()
            d = dim_x_gamma(Es, gammas, L, p, c)
            if d == 0: rd = False; break
        q = (1 if all_zero else 0) * 2 + (1 if rd else 0)
        quadrants[q] += 1
        if len(examples[q]) < 2:
            examples[q].append((Es, all_zero, rd, minors))
        if n_star >= n_target: break

    print(f"  Stars sampled: {n_star}")
    for q in [0, 1, 2, 3]:
        ad = (q >> 1) == 1
        rd = (q & 1) == 1
        label = f"all_minors_zero={ad}, rd={rd}"
        print(f"    {label}: {quadrants[q]}")

    if examples[3]:
        Es, _, _, minors = examples[3][0]
        print(f"\n  Example rd-star: Es={Es}")
        rng2 = np.random.default_rng(0)
        for tg in range(3):
            gammas = (rng2.choice(p - 1, size=4, replace=False) + 1).tolist()
            d = dim_x_gamma(Es, gammas, L, p, c)
            print(f"    γ={gammas}: dim X_γ = {d}")
    if examples[1]:
        Es, _, _, minors = examples[1][0]
        print(f"\n  ANOMALY (det != 0 but rd): Es={Es}, minors={minors}")
    if examples[2]:
        Es, _, _, minors = examples[2][0]
        print(f"\n  ANOMALY (det == 0 but not rd): Es={Es}, minors={minors}")


if __name__ == '__main__':
    n = 16
    primes = [97, 193, 257, 449, 577, 1009, 1153, 1217, 1601, 1697]
    valid = [p for p in primes if (p - 1) % n == 0]
    if not valid:
        print("no prime"); sys.exit()
    p = valid[0]
    print(f"=== rd-Pattern-C-star at c=4, n={n}, p={p} ===\n")
    verify_at_c4(n, p, n_target=100, n_trials=500000)
