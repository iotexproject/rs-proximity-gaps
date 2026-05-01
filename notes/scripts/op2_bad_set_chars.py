#!/usr/bin/env python3 -u
"""Characterize the rank-deficient configurations at c=3.

For random m-tuples of supports E_1,...,E_m in [n] of size w, with random
distinct γ_i, when does rank A < min(mc, 2D)?

Hypothesis: rank deficiency requires a "(w+1)-clique sub-pattern" (tetrahedron)
within the m supports. Test by:
  1. For each random m-tuple of supports, check rank deficiency
  2. If deficient, check if any (w+1) of the supports form a tetrahedron
  3. Tally: deficient & has tet vs deficient & no tet
"""

import sys
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega, elp
from op2_clique_scan import rank_mod
from op2_tet_consolidated import make_NEs, solve_for_witness

def has_tetrahedron(Es, w):
    """Check if any (w+1) of the Es are exactly all w-subsets of some (w+1)-set."""
    if len(Es) < w + 1: return False, None
    Es_set = [frozenset(E) for E in Es]
    for tet_idx in combinations(range(len(Es_set)), w + 1):
        sub_Es = [Es_set[i] for i in tet_idx]
        union = set().union(*sub_Es)
        if len(union) != w + 1: continue
        # Check all w-subsets of union are in sub_Es
        all_w_subsets = set(frozenset(s) for s in combinations(union, w))
        if all_w_subsets == set(sub_Es):
            return True, tuple(sorted(union))
    return False, None

def test_one(n, k, c, p, m, n_trials=500):
    D = n - k; w = D - c
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    all_supports = list(combinations(range(n), w))
    rng = np.random.default_rng(0)

    counts = {'rank_full': 0, 'def_with_tet': 0, 'def_without_tet': 0}
    deficient_no_tet_examples = []

    for trial in range(n_trials):
        # Pick m random supports
        idx = rng.choice(len(all_supports), size=m, replace=False)
        Es = [all_supports[i] for i in idx]
        # Random γ
        gammas = []
        seen = set()
        while len(gammas) < m:
            g = int(rng.integers(2, p))
            if g not in seen: gammas.append(g); seen.add(g)
        NEs = make_NEs(Es, L, p, D, c, w)
        A, _, rA = solve_for_witness(NEs, gammas, p, D, c)
        full = min(m * c, 2 * D)
        if rA == full:
            counts['rank_full'] += 1
        else:
            has_tet, V = has_tetrahedron(Es, w)
            if has_tet:
                counts['def_with_tet'] += 1
            else:
                counts['def_without_tet'] += 1
                if len(deficient_no_tet_examples) < 3:
                    deficient_no_tet_examples.append({
                        'trial': trial, 'Es': Es, 'rank': rA,
                        'deficit': full - rA, 'gammas': gammas,
                    })
    return counts, deficient_no_tet_examples

if __name__ == '__main__':
    print("=== Bad-set characterization: is rank-deficiency ⇔ tetrahedron sub-pattern? ===\n")
    for n, c in [(12, 3), (16, 3), (12, 4)]:
        k = n // 2
        D = n - k; w = D - c
        bound = (2 * D - 1) // c
        print(f"--- n={n} c={c} (w={w}, bound={bound}) ---")
        for m in [bound + 1, bound + 2, w + 1]:  # m at threshold + tet size
            if m * c > 2 * D + 5: continue
            counts, examples = test_one(n, k, c, 1009 if n != 20 else 1021, m, n_trials=300)
            tot = sum(counts.values())
            print(f"  m={m} ({tot} trials):")
            print(f"    rank full: {counts['rank_full']}")
            print(f"    deficient WITH tetrahedron: {counts['def_with_tet']}")
            print(f"    deficient WITHOUT tetrahedron: {counts['def_without_tet']}")
            if examples:
                print(f"    Examples of deficient-no-tet:")
                for ex in examples[:2]:
                    print(f"      Es={ex['Es']}, rank={ex['rank']}, deficit={ex['deficit']}")
        print()
