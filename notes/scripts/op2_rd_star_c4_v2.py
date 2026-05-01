#!/usr/bin/env python3 -u
"""Verify rd-Pattern-C-star Lagrange form at c=4 with larger sample.

At c=4: M is 4×3 matrix (3 leaves × 4 coeffs of Π_{U_j} of degree c-1=3).
rd-star ⇔ rank M < 3 ⇔ all 3×3 minors vanish (codim 2 in matrix space,
4 such minors). Generically rare: rate ~1/p^2.

Strategy:
1. Build a large sample of Pattern C star configs at c=4.
2. Compute the 4 minors and check if all = 0 ⇔ dim X_γ ≥ 1.
3. If matched, Lemma 3.1 generalizes to c=4 (codim-2 instead of codim-1).
4. Additionally check forced-zero pattern of basis vector to confirm
   Lagrange-form persists.
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
    sig = hypergraph_signature(Es)
    if sig != ((0, 0, 0, 1, 1, 1), (0, 0, 0, 0), 0):
        return False
    edges = intersection_graph(Es)
    return topology_signature(edges, len(Es)) == 'star'


def det_mod(M, p):
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


def all_minors_zero(M_4x3, p):
    """For 4×3 matrix M (each col is Pi_{U_j} coefs at c=4), check rank < 3.
    Compute 4 minors of size 3×3 (skipping each row in turn)."""
    M = np.array(M_4x3, dtype=np.int64) % p
    minors = []
    for skip_row in range(4):
        sub = np.delete(M, skip_row, axis=0)  # 3x3
        d = det_mod(sub, p)
        minors.append(d)
    return all(d == 0 for d in minors), minors


def rd_star_condition_c4(Es, L, p, c=4):
    s = extract_star_structure(Es)
    if s is None: return None, None
    leaves = s['leaves']
    cols = []
    for leaf in leaves:
        v_share = leaf['v_share']
        U = tuple(u for u in leaf['E'] if u != v_share)
        coeffs = pi_U_coeffs(U, L, p, c)  # length c
        cols.append(coeffs)
    M = np.array(cols, dtype=np.int64).T  # (c × 3)
    return all_minors_zero(M, p), M


def verify_at_c4_large(n, p, n_target_stars=2000, n_trials=2000000):
    k = n // 2; c = 4
    D = n - k; w = D - c
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    all_supports = list(combinations(range(n), w))
    print(f"=== rd-Pattern-C-star at c=4 n={n} p={p}, target {n_target_stars} stars ===")
    rng = np.random.default_rng(42)

    quadrants = Counter()
    examples = {q: [] for q in range(4)}
    n_star = 0

    for trial in range(n_trials):
        idx = rng.choice(len(all_supports), size=4, replace=False)
        Es = [all_supports[i] for i in idx]
        if not is_pattern_C_star_general(Es): continue
        if find_sub_tet(Es, n): continue
        n_star += 1
        result = rd_star_condition_c4(Es, L, p, c)
        if result[0] is None: continue
        all_zero, minors = result[0]
        # rd test: 2 random γ tuples
        rd = True
        for tg in range(2):
            gammas = (rng.choice(p - 1, size=4, replace=False) + 1).tolist()
            d = dim_x_gamma(Es, gammas, L, p, c)
            if d == 0: rd = False; break
        q = (1 if all_zero else 0) * 2 + (1 if rd else 0)
        quadrants[q] += 1
        if len(examples[q]) < 2:
            examples[q].append((Es, all_zero, rd, minors))
        if n_star >= n_target_stars: break

    print(f"  Stars sampled: {n_star}")
    for q in [0, 1, 2, 3]:
        ad = (q >> 1) == 1
        rd_ = (q & 1) == 1
        label = f"all_3x3_minors_zero={ad}, rd={rd_}"
        print(f"    {label}: {quadrants[q]}")
    if examples[3]:
        for Es, _, _, minors in examples[3][:2]:
            print(f"  rd-star example: Es={Es}")
            print(f"    minors: {minors}")


if __name__ == '__main__':
    n = 16
    primes = [97, 193, 257, 449, 577, 1009]
    p = next((q for q in primes if (q - 1) % n == 0), None)
    verify_at_c4_large(n, p, n_target_stars=2000, n_trials=3000000)
