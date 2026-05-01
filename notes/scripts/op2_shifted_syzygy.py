#!/usr/bin/env python3 -u
"""Test whether non-tet supports always admit a "shifted syzygy" producing Λ_E_i.

The lemma's escape clause for support index i is:
   ∃ (p_j) ∈ (F_p[x]_<c)^m with:
     Σ p_j Λ_E_j = 0     (syzygy)
     Σ γ_j p_j Λ_E_j = Λ_E_i  (produces Λ_E_i)

If for SOME i this is solvable, the lemma holds at this configuration.

Test: for random non-tet support tuples, check if any i admits the shifted syzygy.
"""

import sys
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega, elp
from op2_clique_scan import rank_mod
from op2_tet_consolidated import make_NEs, solve_for_witness
from op2_bad_set_chars import has_tetrahedron

def shifted_syzygy_solvable(NEs, gammas, i, p, D, c):
    """Check if (b) is solvable for index i."""
    m = len(NEs)
    # Build A as before: mc × 2D
    A = np.zeros((m * c, 2 * D), dtype=np.int64)
    for j in range(m):
        A[j*c:(j+1)*c, :D] = NEs[j]
        A[j*c:(j+1)*c, D:] = (gammas[j] * NEs[j]) % p
    # Build target vector: (0, Λ_E_i) in F_p^{2D}
    # First D zeros, then last D = first row of N_E_i shifted? No, Λ_E_i directly.
    # Λ_E_i has w+1 coefficients, embed in F_p^D
    # Recall: N_E[0, j] = j-th coefficient of Λ_E for j ∈ [0, w]
    # So row 0 of N_E IS Λ_E (embedded with trailing zeros)
    target = np.zeros(2 * D, dtype=np.int64)
    target[D:] = NEs[i][0]
    # Solve A^T y = target?
    # We want: (0, Λ_E_i) ∈ row span A iff target ∈ image A^T
    # Equivalently: rank([A^T | target]) == rank A^T
    AT = A.T  # 2D × mc
    aug = np.concatenate([AT, target.reshape(-1, 1)], axis=1)
    rank_AT = rank_mod(AT, p)
    rank_aug = rank_mod(aug, p)
    return rank_aug == rank_AT

def test_shifted(n, k, c, p, n_trials=200):
    """Run trials. For each non-tet rank-deficient tuple, check if some i admits shifted syzygy."""
    D = n - k; w = D - c
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    all_supports = list(combinations(range(n), w))
    rng = np.random.default_rng(0)
    T = (2 * D - 1) // c
    m = T + 1

    nontet_count = 0
    nontet_lemma_holds = 0  # ∃i with shifted syzygy
    nontet_lemma_fails = 0  # no i admits shifted syzygy
    examples = []

    for trial in range(n_trials):
        idx = rng.choice(len(all_supports), size=m, replace=False)
        Es = [all_supports[i] for i in idx]
        gammas = []; seen = set()
        while len(gammas) < m:
            g = int(rng.integers(2, p))
            if g not in seen: gammas.append(g); seen.add(g)
        has_tet, V = has_tetrahedron(Es, w)
        if has_tet: continue
        NEs = make_NEs(Es, L, p, D, c, w)
        A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
        if rA == min(m * c, 2 * D): continue  # rank full, lemma vacuous
        nontet_count += 1
        # Check if some i admits shifted syzygy
        any_i = False
        for i in range(m):
            if shifted_syzygy_solvable(NEs, gammas, i, p, D, c):
                any_i = True; break
        if any_i:
            nontet_lemma_holds += 1
        else:
            nontet_lemma_fails += 1
            if len(examples) < 3:
                examples.append({'Es': Es, 'gammas': gammas, 'rank': rA})
    return nontet_count, nontet_lemma_holds, nontet_lemma_fails, examples

if __name__ == '__main__':
    print("=== Lemma's escape clause for non-tet rank-deficient configurations ===")
    print(f"{'n':>4} {'c':>3} {'m':>3} {'#non-tet rank-def':>18} "
          f"{'lemma holds':>12} {'lemma fails':>12}")
    for n, c in [(12, 3), (16, 3), (12, 4)]:
        k = n // 2
        D = n - k
        T = (2*D-1)//c
        m = T + 1
        result = test_shifted(n, k, c, 1009, n_trials=500)
        nt, hold, fail, ex = result
        print(f"{n:>4} {c:>3} {m:>3} {nt:>18} {hold:>12} {fail:>12}")
        if fail > 0:
            for e in ex:
                print(f"    counterexample: Es={e['Es']}")
