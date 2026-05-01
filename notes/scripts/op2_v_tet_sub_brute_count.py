#!/usr/bin/env python3 -u
"""Brute-force enumeration of V_tet_sub at small p.

V_tet_sub = ⋃_γ ker A(γ) for sub-tet configuration. ker A(γ) is the set of
(s_1, s_2) ∈ F_p^{2D} such that s_1 + γ_i s_2 ∈ V_{E_i} (= the row span of
restricted Vandermonde at E_i) for each i.

For fixed (E_1, ..., E_m), iterate over γ ∈ (F_p^*)^m, compute ker A(γ),
enumerate all p^{ker_dim} elements, accumulate unique (s_1, s_2) values.

The asymptotic |V_tet_sub| = p^{dim} for large p; at small p we get a finite
count and infer dim by checking against p^k for various k.
"""

import sys
import numpy as np
from itertools import combinations, product
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_clique_scan import rank_mod, kernel_mod
from op2_tet_consolidated import make_NEs, solve_for_witness


def build_sub_tet_c4(n, p, V, U, w, D, c):
    omega = find_omega(n, p); L = [pow(omega, i, p) for i in range(n)]
    Es = [tuple(sorted([v for v in V if v != V[i]] + [U[i]])) for i in range(len(V))]
    return Es, L


def enumerate_v_tet_sub(NEs, p, D, c, max_gammas=None):
    """Enumerate V_tet_sub by iterating over all γ ∈ (F_p^*)^m and collecting all
    (s_1, s_2) ∈ ker A(γ). Use a hashable key (tuple of int) to dedupe."""
    m = len(NEs)
    seen = set()
    cnt = 0
    # Iterate over all γ ∈ (F_p^*)^m with distinct values
    gammas_iter = product(range(1, p), repeat=m)
    for gammas in gammas_iter:
        if len(set(gammas)) != m: continue  # require distinct
        cnt += 1
        if max_gammas and cnt > max_gammas: break
        A, ker, rA = solve_for_witness(NEs, list(gammas), p, D, c)
        if not ker: continue
        ker_dim = len(ker)
        # Enumerate all p^{ker_dim} linear combos of basis
        if ker_dim == 0: continue
        for coefs in product(range(p), repeat=ker_dim):
            v = np.zeros(2 * D, dtype=np.int64)
            for ci, kv in zip(coefs, ker):
                v = (v + ci * kv) % p
            seen.add(tuple(v.tolist()))
    return seen, cnt


def measure_dim(n, p, V, U):
    D = n - n // 2; c = 4; w = D - c
    Es, L = build_sub_tet_c4(n, p, V, U, w, D, c)
    NEs = make_NEs(Es, L, p, D, c, w)
    print(f"\n  Sub-tet at p={p}: V={V}, U={U}, Es={Es}")
    # Distinct γ-tuples: (p-1)(p-2)(p-3)(p-4)
    n_gammas = (p - 1) * (p - 2) * (p - 3) * (p - 4)
    print(f"  Distinct γ-tuples: {n_gammas}")
    # Brute force
    seen, cnt = enumerate_v_tet_sub(NEs, p, D, c)
    print(f"  Iterated {cnt} γ-tuples; |V_tet_sub| = {len(seen)}")
    # Estimate dim: |V_tet_sub| ≈ p^dim
    if len(seen) > 1:
        dim_est = np.log(len(seen)) / np.log(p)
        print(f"  Empirical dim = log_p(|V_tet_sub|) = {dim_est:.3f}")
        for d in range(2 * D + 1):
            if abs(p ** d - len(seen)) < p ** d * 0.5:
                print(f"    closest p^d for d={d}: p^{d} = {p**d}, ratio = {len(seen)/p**d:.3f}")


def main():
    n = 16
    # Sub-tet at c=4 w'=3: V = 4 vertices, 4 supports each (V \ {v_i}) ∪ {u_i}
    V = [0, 1, 2, 3]
    U = [4, 5, 6, 7]
    p = 17
    measure_dim(n, p, V, U)


if __name__ == '__main__':
    main()
