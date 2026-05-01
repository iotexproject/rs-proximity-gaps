#!/usr/bin/env python3 -u
"""How DENSE are tetrahedron witnesses?

For n=12 c=3 p=1009, with V={1,4,5,8} fixed, count:
  - dim of solution space (s_1, s_2, γ_1, γ_2, γ_3, γ_4) over F_p
  - This determines the measure of bad (s_1, s_2).

For a fixed (γ_1, γ_2, γ_3, γ_4) distinct: kernel A has dim 4 (we computed).
Each kernel point gives ONE (s_1, s_2). So #(s_1, s_2) for fixed γ tuple is p^4.

But we need (s_1, s_2) that realizes ALL 4 γ's distinctly. This is an OPEN
condition (each E_i must have N_E·s_2 ≠ 0 vector + γ_i distinct).

Total #(γ_1, ..., γ_4) distinct = p(p-1)(p-2)(p-3) ≈ p^4
Total #(s_1, s_2) realizing tetrahedron = sum over (γ tuple) of (open ker)

Vs total #(s_1, s_2) ≠ 0 ≈ p^{12}.

If density is p^{-c'} for some c', soundness picture changes accordingly.
"""

import sys
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega, elp
from op2_clique_scan import rank_mod, kernel_mod, derive_realized_gammas

def measure_density(n, k, c, p, V, n_trials=50000, log_every=10000):
    """For random (s_1, s_2), check if it gives 4 distinct realized γ on
    tetrahedron supports."""
    D = n - k; w = D - c
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    Es = list(combinations(V, w))
    m = len(Es)

    NEs = []
    for E in Es:
        lam = elp(E, L, p)
        N = np.zeros((c, D), dtype=np.int64)
        for r in range(c):
            for j in range(D):
                t2 = j - r
                if 0 <= t2 <= w:
                    N[r, j] = lam[t2] % p
        NEs.append(N)

    rng = np.random.default_rng(0)
    counts = np.zeros(m + 2, dtype=np.int64)  # counts[k] = # trials with k realized γ
    for trial in range(n_trials):
        s1 = rng.integers(0, p, size=D, dtype=np.int64)
        s2 = rng.integers(0, p, size=D, dtype=np.int64)
        if not np.any(s2 != 0): continue
        # For each E_i: derive γ_i (consistency check via proportionality)
        gammas = []
        for N in NEs:
            aE = (N @ s2) % p
            bE = (N @ s1) % p
            nz = None
            for j in range(c):
                if aE[j] != 0: nz = j; break
            if nz is None: gammas.append(None); continue
            prop = all(
                (int(aE[j_]) * int(bE[k_]) - int(aE[k_]) * int(bE[j_])) % p == 0
                for j_ in range(c) for k_ in range(c)
            )
            if not prop: gammas.append(None); continue
            gd = (-int(bE[nz]) * pow(int(aE[nz]), p-2, p)) % p
            gammas.append(gd)
        distinct = set(g for g in gammas if g is not None)
        counts[len(distinct)] += 1
        if (trial + 1) % log_every == 0:
            print(f"  trial {trial+1}: counts so far = {counts.tolist()}")
    return counts

if __name__ == '__main__':
    n, k, c = 12, 6, 3
    p = 1009
    V = (1, 4, 5, 8)
    print(f"=== Density of tetrahedron-realizing (s_1, s_2) ===")
    print(f"n={n} k={k} c={c} p={p} V={V}")
    print(f"Total |F_p^{{2D}}| = {p}^12 ≈ {p**12:.2e}")
    print()
    counts = measure_density(n, k, c, p, V, n_trials=50000)
    print(f"\nDistribution of #realized-γ across 50000 random (s_1, s_2):")
    for k_, ct in enumerate(counts):
        if ct > 0:
            print(f"  {k_} realized γ : {ct:>6} ({100*ct/50000:.3f}%)")
    print(f"\nFraction achieving ≥4 (bound violation) = "
          f"{counts[4:].sum()}/{50000} = {counts[4:].sum()/50000:.6f}")
    print(f"Predicted dimension drop p^{{-?}}: ker dim = 4, total = 12, "
          f"so dim drop = 8. Predicted fraction = p^{{-8}} = {p**-8:.2e}")
