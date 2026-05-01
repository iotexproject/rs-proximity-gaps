#!/usr/bin/env python3 -u
"""Find ALL non-tet bound-violating (s_1, s_2) patterns. Characterize them.

Hypothesis: even though they're not (w+1)-cliques, they share some structural
property. Look for: vertex degree distribution, support intersection pattern,
etc.
"""

import sys
import numpy as np
from itertools import combinations
from collections import Counter
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega, elp
from op2_clique_scan import rank_mod, kernel_mod
from op2_tet_consolidated import make_NEs, solve_for_witness
from op2_bad_set_chars import has_tetrahedron
from op2_shifted_syzygy import shifted_syzygy_solvable

def find_all_nontet_realizable(n, k, c, p, m, n_trials=2000):
    """Find all rank-def + lemma-fail + realize-all-m configs that are non-tet."""
    D = n - k; w = D - c
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    all_supports = list(combinations(range(n), w))
    rng = np.random.default_rng(0)
    findings = []
    for trial in range(n_trials):
        idx = rng.choice(len(all_supports), size=m, replace=False)
        Es = [all_supports[i] for i in idx]
        gammas = []; seen = set()
        while len(gammas) < m:
            g = int(rng.integers(2, p))
            if g not in seen: gammas.append(g); seen.add(g)
        if has_tetrahedron(Es, w)[0]: continue
        NEs = make_NEs(Es, L, p, D, c, w)
        A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
        if rA == min(m * c, 2 * D): continue
        # Check if any i admits shifted syzygy
        any_i = False
        for i_ in range(m):
            if shifted_syzygy_solvable(NEs, gammas, i_, p, D, c):
                any_i = True; break
        if any_i: continue  # lemma holds → not bad
        # Verify (s_1, s_2) realizes all m γ's
        v = ker[0]
        s1 = v[:D].astype(np.int64); s2 = v[D:].astype(np.int64)
        all_realize = True
        for i_ in range(m):
            N = NEs[i_]
            aE = (N @ s2) % p; bE = (N @ s1) % p
            nz = next((j for j in range(c) if aE[j] != 0), None)
            if nz is None: all_realize = False; break
            prop = all(
                (int(aE[j_]) * int(bE[k_]) - int(aE[k_]) * int(bE[j_])) % p == 0
                for j_ in range(c) for k_ in range(c)
            )
            if not prop: all_realize = False; break
            gd = (-int(bE[nz]) * pow(int(aE[nz]), p-2, p)) % p
            if gd != gammas[i_]: all_realize = False; break
        if all_realize:
            findings.append({
                'Es': Es, 'gammas': gammas, 'rank': rA, 'ker_dim': len(ker),
            })
    return findings

def vertex_degree(Es, n):
    deg = [0] * n
    for E in Es:
        for v in E: deg[v] += 1
    return deg

def pairwise_intersections(Es):
    return [(i, j, len(set(Es[i]) & set(Es[j])))
            for i, j in combinations(range(len(Es)), 2)]

if __name__ == '__main__':
    n, k, c = 12, 6, 3
    p = 1009
    D = n - k; w = D - c
    T = (2 * D - 1) // c
    print(f"=== Non-tet realizable bound-violating configs at n={n} c={c} m={T+1} ===")
    findings = find_all_nontet_realizable(n, k, c, p, T+1, n_trials=3000)
    print(f"Found {len(findings)} non-tet realizable configs (out of 3000 trials)\n")

    for i, f in enumerate(findings):
        print(f"\n--- Config {i} ---")
        print(f"  Es={f['Es']}")
        deg = vertex_degree(f['Es'], n)
        print(f"  Vertex degrees: {deg}")
        deg_dist = Counter(deg)
        print(f"  Degree distribution: {dict(sorted(deg_dist.items()))}")
        pairs = pairwise_intersections(f['Es'])
        intsx_dist = Counter(p_[2] for p_ in pairs)
        print(f"  Pairwise intersection sizes: {dict(sorted(intsx_dist.items()))}")
        union = set().union(*f['Es'])
        print(f"  Union size: {len(union)}, kernel dim: {f['ker_dim']}")
