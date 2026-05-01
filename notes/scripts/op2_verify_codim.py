#!/usr/bin/env python3 -u
"""Verify codim formula 2D - T - 2 by measuring # bad patterns at various (n, c).

For each (n, c, m=T+1):
  Sample N random (E, γ) tuples
  Count # bad: rank-deficient AND lemma-fails AND realizes m γ's distinctly
  Bad fraction f_bad = bad / total
  Bad patterns total ≈ C(C(n, w), m) · p^m · f_bad
  Each bad pattern contributes (kernel dim) p^d witnesses
  Total bad set size ≈ # patterns · p^d
  Density = total / p^{2D}
  Codim = -log_p(density)

Formula: codim = 2D - m - d ≈ 2D - T - 1 - 1 = 2D - T - 2 (for d=1).
"""

import sys
import numpy as np
from itertools import combinations
from collections import Counter
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_clique_scan import rank_mod, kernel_mod
from op2_tet_consolidated import make_NEs, solve_for_witness
from op2_bad_set_chars import has_tetrahedron
from op2_shifted_syzygy import shifted_syzygy_solvable

import math

def measure_density(n, k, c, p, n_trials=2000):
    """Sample (E, γ) tuples; count bad fraction."""
    D = n - k; w = D - c
    if w < 1: return None
    omega = find_omega(n, p)
    if omega is None: return None
    L = [pow(omega, i, p) for i in range(n)]
    all_supports = list(combinations(range(n), w))
    rng = np.random.default_rng(0)
    T = (2 * D - 1) // c
    m = T + 1
    n_supp = len(all_supports)

    counts = Counter()  # 'tet' / 'nontet_bad' / 'rank_full' / 'rank_def_lemma_holds'

    for trial in range(n_trials):
        idx = rng.choice(n_supp, size=m, replace=False)
        Es = [all_supports[i] for i in idx]
        gammas = []; seen = set()
        while len(gammas) < m:
            g = int(rng.integers(2, p))
            if g not in seen: gammas.append(g); seen.add(g)

        has_tet, V = has_tetrahedron(Es, w)
        NEs = make_NEs(Es, L, p, D, c, w)
        A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
        full = min(m * c, 2 * D)

        if rA == full:
            counts['rank_full'] += 1
        elif has_tet:
            counts['tet'] += 1
        else:
            # Non-tet rank-deficient — check lemma
            lemma_holds = False
            for i_ in range(m):
                if shifted_syzygy_solvable(NEs, gammas, i_, p, D, c):
                    lemma_holds = True; break
            if lemma_holds:
                counts['rank_def_lemma_holds'] += 1
            else:
                counts['nontet_bad'] += 1

    return counts, n_trials, T, m, n_supp, D, w

def estimate_codim(n, k, c, p, n_trials=2000):
    result = measure_density(n, k, c, p, n_trials)
    if result is None: return None
    counts, total, T, m, n_supp, D, w = result
    f_bad = counts['nontet_bad'] / total

    # Estimated # bad non-tet patterns (over all (E, γ))
    # # m-tuples of supports = C(n_supp, m)
    # # γ-tuples ≈ p^m
    # # bad ≈ f_bad × C(n_supp, m) × p^m × (correction)
    # For codim purpose, take log base p
    log_n_tuples = math.log(math.comb(n_supp, m)) / math.log(p)
    # Each bad pattern: kernel dim 1 → p witnesses
    # Total bad size ≈ # bad patterns × p
    # Density = total / p^{2D}
    # Codim = 2D - m - 1 - log_p(C(n_supp, m) × f_bad)

    log_f_bad = math.log(max(f_bad, 1e-10)) / math.log(p) if f_bad > 0 else -1000
    nontet_codim_actual = 2 * D - m - 1 - log_n_tuples - log_f_bad
    nontet_codim_formula = 2 * D - T - 2

    # Also tetrahedron contribution
    tet_codim = 2 * D - (w + 1)  # = w + 2c - 1

    return {
        'n': n, 'c': c, 'D': D, 'w': w, 'T': T, 'm': m, 'n_supp': n_supp,
        'counts': dict(counts),
        'f_bad': f_bad,
        'log_C_n_supp_m': log_n_tuples,
        'tet_codim': tet_codim,
        'nontet_codim_actual': nontet_codim_actual,
        'nontet_codim_formula': nontet_codim_formula,
        'min_codim': min(tet_codim, nontet_codim_actual),
    }

if __name__ == '__main__':
    print("=== Codim verification across (n, c) ===")
    print()
    print(f"{'n':>4} {'c':>3} {'T':>3} {'m':>3} {'#tet':>5} {'#nontet':>7} "
          f"{'#L':>5} {'#R_def_OK':>10} {'tet_co':>7} {'nontet_co':>10} "
          f"{'formula':>8} {'agrees':>7}")
    cases = [(12, 3), (12, 4), (16, 3), (16, 4), (20, 3), (20, 5), (24, 3), (24, 5)]
    for n, c in cases:
        k = n // 2
        p = 1009 if n != 20 else 1021
        result = estimate_codim(n, k, c, p, n_trials=1500)
        if result is None: continue
        r = result
        agrees = "≈" if abs(r['nontet_codim_actual'] - r['nontet_codim_formula']) < 2 else "?"
        print(f"{r['n']:>4} {r['c']:>3} {r['T']:>3} {r['m']:>3} "
              f"{r['counts'].get('tet', 0):>5} {r['counts'].get('nontet_bad', 0):>7} "
              f"{r['counts'].get('rank_full', 0):>5} "
              f"{r['counts'].get('rank_def_lemma_holds', 0):>10} "
              f"{r['tet_codim']:>7} {r['nontet_codim_actual']:>10.1f} "
              f"{r['nontet_codim_formula']:>8} {agrees:>7}")
