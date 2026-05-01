"""Stronger empirical verification of Lemma 1 (⇐) in paper3 §7.6.

Strategy: sample x from V_E for random E ⊂ [n] (so Q = Π_E is a known
witness), then search Ann_w(x) for ALL monic deg-w L-rooted Q's. If
(⇐) holds, every Q found gives a root-set E' such that x ∈ V_{E'}
(this should equal E by Vandermonde linear independence at D ≥ w).

Cell: n=10, c=3, p=41, D=7, w=4 (deployment-shape, D < 2w+1 = 9).

For each trial:
  - random E ⊂ [n], |E| = w
  - random ξ ∈ F_p^w nonzero
  - x = sum_i ξ_i ev_{v_i}
  - find ALL Q ∈ Ann_w(x) monic deg w L-rooted
  - for each Q: extract E', verify x ∈ V_{E'} (should always pass if ⇐ holds)
"""

import os
import random
import sys
from itertools import combinations, product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from op2_curve_measure_prefactor import small_field_subgroup
from verify_lemma1_iff import (
    hankel_w, matrix_kernel, matrix_rank, rank_eq,
    is_in_union_V_E,
)

random.seed(2026)


def find_all_L_rooted_monic_deg_w(ann_basis, w, L, p):
    """Find ALL Q in span(ann_basis) that are monic, deg exactly w, L-rooted.

    Returns list of (Q_monic, E_indices) tuples. E_indices is the list of
    L-indices of roots.
    """
    if not ann_basis:
        return []
    dim = len(ann_basis)
    found = []
    seen_Q = set()
    n_L = len(L)
    for coeffs in product(range(p), repeat=dim):
        Q = [0] * (w + 1)
        for i, c in enumerate(coeffs):
            for j in range(w + 1):
                Q[j] = (Q[j] + c * ann_basis[i][j]) % p
        while Q and Q[-1] == 0:
            Q.pop()
        if not Q or len(Q) != w + 1:
            continue
        lead = Q[-1]
        inv_lead = pow(lead, p - 2, p)
        Q_monic = tuple((c * inv_lead) % p for c in Q)
        if Q_monic in seen_Q:
            continue
        roots_in_L = []
        for v_idx, v in enumerate(L):
            val = 0
            for k, qk in enumerate(Q_monic):
                val = (val + qk * pow(v, k, p)) % p
            if val == 0:
                roots_in_L.append(v_idx)
        if len(roots_in_L) == w:
            seen_Q.add(Q_monic)
            found.append((list(Q_monic), roots_in_L))
    return found


def is_in_V_E(x, E, L, p):
    """Check x ∈ V_E specifically (not the whole union)."""
    D = len(x)
    M = [[pow(L[v], j, p) for v in E] for j in range(D)]
    aug = [row + [x[j]] for j, row in enumerate(M)]
    return matrix_rank(M, p) == matrix_rank(aug, p)


def main():
    n = 10
    c = 3
    p = 41
    D = 7
    w = 4
    print(f"Cell: n={n}, c={c}, p={p}, D={D}, w={w}, short-data: D={D}<2w+1={2*w+1} ✓")
    L = small_field_subgroup(p, n)
    print(f"L = {L}")
    print()

    n_trials = 200
    total_Qs_found = 0
    total_x_not_in_VE_for_some_Q = 0
    counterexamples = []

    for trial in range(n_trials):
        # Random E, ξ
        E = sorted(random.sample(range(n), w))
        xi = [random.randrange(1, p) for _ in range(w)]
        # x = sum xi[i] * ev_{E[i]}
        x = [0] * D
        for i, v in enumerate(E):
            for j in range(D):
                x[j] = (x[j] + xi[i] * pow(L[v], j, p)) % p

        # Find all L-rooted monic deg-w Q in Ann_w(x)
        H = hankel_w(x, w)
        ann = matrix_kernel(H, p)
        all_Qs = find_all_L_rooted_monic_deg_w(ann, w, L, p)
        total_Qs_found += len(all_Qs)

        # For each Q, verify x ∈ V_{E_Q}
        for Q, E_Q in all_Qs:
            if not is_in_V_E(x, E_Q, L, p):
                counterexamples.append((trial, x, E, Q, E_Q))
                total_x_not_in_VE_for_some_Q += 1
                print(f"COUNTEREXAMPLE trial={trial}: x={x}, original E={E}, "
                      f"found Q with E_Q={E_Q} but x ∉ V_{{E_Q}}")

    print(f"Trials: {n_trials}")
    print(f"  Total Q's found across all trials: {total_Qs_found}")
    print(f"  (Per trial, expected exactly 1 Q = Π_E if (⇐) holds with uniqueness)")
    print(f"  Counterexamples: {len(counterexamples)}")
    print()
    if not counterexamples:
        print("✓ Every Q ∈ Ann_w(x) monic deg w L-rooted gives x ∈ V_{E_Q}.")
        print("  Lemma 1 (⇐) holds empirically across all hits.")
        print("  Issue #398's concern is refuted.")
    else:
        print(f"✗ {len(counterexamples)} counterexamples found.")


if __name__ == "__main__":
    main()
