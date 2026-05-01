#!/usr/bin/env python3 -u
"""Pointwise-evaluation analysis: at each v ∈ [n], constrain ĥ_j(L_v) for j with v ∉ E_j.

For (ĥ_j) ∈ X_γ, evaluating both X_γ constraints at x = L_v gives:
   Σ_{j : v ∉ E_j} ĥ_j(L_v) · Λ_E_j(L_v) = 0
   Σ_{j : v ∉ E_j} γ_j ĥ_j(L_v) · Λ_E_j(L_v) = 0

Let κ_v := |{j : v ∉ E_j}| = m - |{j : v ∈ E_j}|.

This is 2 linear constraints on κ_v unknowns (the values ĥ_j(L_v) for those j).
- κ_v = 0: vacuous
- κ_v = 1: forces ĥ_j(L_v) = 0 for that single j
- κ_v = 2: 2 constraints on 2 unknowns, generically full rank → both = 0
- κ_v ≥ 3: kernel dim κ_v - 2

At a tetrahedron: κ_v = 1 for v ∈ V (force ĥ_v(L_v) = 0). For v ∉ V: κ_v = 0.
  → ĥ_j(L_{v_j}) = 0, c-1 free params per j, total (w-1)(c-1) syzygy dim.

For NON-tet supports: do many v's have κ_v ≤ 2, forcing many ĥ_j(L_v) = 0?
  If yes, ĥ_j has many roots → ĥ_j = 0 polynomially → X_γ trivial → no syzygy.

Test: for non-tet supports, count distribution of κ_v values.
"""

import sys
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_clique_scan import rank_mod
from op2_tet_consolidated import make_NEs, solve_for_witness
from op2_bad_set_chars import has_tetrahedron

def kappa_distribution(Es, n, w):
    """For each v ∈ [n], compute κ_v = m - |{j : v ∈ E_j}|."""
    m = len(Es)
    kappa = []
    for v in range(n):
        in_count = sum(1 for E in Es if v in E)
        kappa.append(m - in_count)
    return kappa

def force_zero_count(Es, n, w, c):
    """Count v's that force ĥ_j(L_v) = 0 for some j (i.e., κ_v ∈ {1, 2}).
    For ĥ_j = 0 polynomially (degree < c), need ≥ c roots."""
    kappa = kappa_distribution(Es, n, w)
    # For κ_v = 1: forces 1 specific ĥ_j(L_v) = 0
    # For κ_v = 2: forces 2 specific ĥ_j(L_v) = 0
    forced_zeros = {}  # j -> set of v's where ĥ_j(L_v) = 0
    for j in range(len(Es)):
        forced_zeros[j] = set()
    for v in range(n):
        kv = kappa[v]
        if kv > 2: continue  # kernel still nontrivial
        # Find indices j with v ∉ E_j
        Js = [j for j, E in enumerate(Es) if v not in E]
        # All Js have ĥ_j(L_v) = 0 forced (when κ_v ≤ 2 generically)
        for j in Js:
            forced_zeros[j].add(v)
    # Check: for which j does forced_zeros[j] have ≥ c elements?
    forced_to_zero_polys = sum(1 for j in forced_zeros if len(forced_zeros[j]) >= c)
    return kappa, forced_zeros, forced_to_zero_polys

def analyze_supports(Es, n, k, c, w, label=""):
    print(f"\n  {label}")
    print(f"    Es = {Es}, m={len(Es)}")
    kappa, forced, count = force_zero_count(Es, n, w, c)
    print(f"    κ distribution: {kappa}")
    has_tet, V = has_tetrahedron(Es, w)
    print(f"    has tetrahedron? {has_tet} (V={V})")
    forced_summary = {j: sorted(forced[j]) for j in forced if len(forced[j]) > 0}
    print(f"    forced ĥ_j(L_v) = 0 (j: v's): {forced_summary}")
    print(f"    # j's with ≥ c={c} forced zeros (ĥ_j ≡ 0): {count} out of {len(Es)}")
    return count, len(Es), has_tet

if __name__ == '__main__':
    n, k, c = 12, 6, 3
    D = n - k; w = D - c

    # Test 1: tetrahedron
    V = (1, 4, 5, 8)
    Es_tet = list(combinations(V, w))
    analyze_supports(Es_tet, n, k, c, w, label="Tetrahedron V={1,4,5,8}")

    # Test 2: non-tet rank-deficient (from earlier analysis)
    Es_nontet = [(4, 5, 8), (7, 8, 10), (3, 8, 11), (3, 7, 11)]
    analyze_supports(Es_nontet, n, k, c, w, label="Non-tet rank-deficient")

    # Test 3: 5 random supports
    Es_rand5 = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11), (0, 3, 6)]
    analyze_supports(Es_rand5, n, k, c, w, label="5 random supports")

    # Test 4: tet + 1 extra (m=5)
    Es_tet_extra = Es_tet + [(0, 2, 3)]
    analyze_supports(Es_tet_extra, n, k, c, w, label="Tet + extra (0,2,3)")

    # Test 5: 2 disjoint tetrahedra
    V1 = (0, 1, 2, 3); V2 = (4, 5, 6, 7)
    Es_2tet = list(combinations(V1, w)) + list(combinations(V2, w))
    analyze_supports(Es_2tet, n, k, c, w, label="2 disjoint tetrahedra")

    # Test 6: at n=16 c=3, two large tetrahedra
    n_, k_, c_ = 16, 8, 3
    w_ = (n_ - k_) - c_
    V1_ = (0, 1, 2, 3, 4, 5)  # 6-vertex set
    Es_big_tet = list(combinations(V1_, w_))
    print(f"\n  --- n={n_} c={c_} ---")
    analyze_supports(Es_big_tet, n_, k_, c_, w_,
                     label=f"Big tetrahedron V={V1_}")

    print("\n=== Summary ===")
    print("Hypothesis: rank-deficiency with X_γ ≠ 0 ⇔ supports contain a")
    print("tetrahedron sub-pattern, characterized by some j with < c forced-zero v's.")
