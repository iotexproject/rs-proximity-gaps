#!/usr/bin/env python3 -u
"""For non-tetrahedron rank-deficient m-tuples, do their kernel (s_1, s_2)
also achieve M > T?

If yes: V_bad has additional components beyond tet varieties.
If no: tetrahedra are the ONLY violation pattern → V_bad = ∪_V V_tet (clean).
"""

import sys
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega, elp
from op2_clique_scan import rank_mod, kernel_mod
from op2_tet_consolidated import make_NEs, solve_for_witness
from op2_witness_full_M import compute_M_full
from op2_bad_set_chars import has_tetrahedron

def find_nontet_deficient(n, k, c, p, m, n_trials=2000):
    """Find m-tuples of supports that are rank-deficient AND have no tetrahedron."""
    D = n - k; w = D - c
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    all_supports = list(combinations(range(n), w))
    rng = np.random.default_rng(42)
    findings = []
    for trial in range(n_trials):
        idx = rng.choice(len(all_supports), size=m, replace=False)
        Es = [all_supports[i] for i in idx]
        gammas = []
        seen = set()
        while len(gammas) < m:
            g = int(rng.integers(2, p))
            if g not in seen: gammas.append(g); seen.add(g)
        NEs = make_NEs(Es, L, p, D, c, w)
        A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
        full = min(m * c, 2 * D)
        if rA == full: continue
        has_tet, V = has_tetrahedron(Es, w)
        if has_tet: continue
        # Found a non-tet deficient config
        findings.append({
            'Es': Es, 'gammas': gammas, 'rank': rA, 'deficit': full - rA,
            'ker_dim': len(ker), 'L': L,
        })
        if len(findings) >= 5: break
    return findings

def analyze_nontet(finding, n, k, c, p, T):
    D = n - k; w = D - c
    L = finding['L']
    Es = finding['Es']; gammas = finding['gammas']
    NEs = make_NEs(Es, L, p, D, c, w)
    A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
    print(f"\n  Non-tet config: Es={Es}")
    print(f"    rank={rA}, ker_dim={len(ker)}")

    # For each kernel basis vector, compute full M
    rng = np.random.default_rng(0)
    max_M = 0
    for i, v in enumerate(ker[:5]):
        s1 = v[:D].astype(np.int64); s2 = v[D:].astype(np.int64)
        if not np.any(s2 != 0): continue
        full_M = compute_M_full(s1, s2, L, p, n, c, w)
        if len(full_M) > max_M: max_M = len(full_M)
        print(f"    ker[{i}]: M = {len(full_M)}")
        if len(full_M) > T:
            print(f"      ⚠️ M > T={T}!  γ values: {sorted(full_M.keys())}")
            for g in sorted(full_M.keys())[:5]:
                print(f"        γ={g}: supports {full_M[g][:3]}{'...' if len(full_M[g])>3 else ''}")
    # Random combinations
    if len(ker) > 1:
        for trial in range(5):
            coefs = rng.integers(1, p, size=len(ker))
            v = np.zeros(2 * D, dtype=np.int64)
            for cf, u in zip(coefs, ker):
                v = (v + cf * u) % p
            s1 = v[:D]; s2 = v[D:]
            if not np.any(s2 != 0): continue
            full_M = compute_M_full(s1, s2, L, p, n, c, w)
            if len(full_M) > max_M: max_M = len(full_M)
    print(f"    → max M over kernel: {max_M} (T={T})")
    return max_M

if __name__ == '__main__':
    n, k, c = 12, 6, 3
    D = n - k
    T = (2 * D - 1) // c
    p = 1009
    print(f"=== Non-tet rank-deficient configs at n={n} c={c} p={p} (T={T}) ===")
    for m in [4, 5]:
        print(f"\n--- m={m} ---")
        findings = find_nontet_deficient(n, k, c, p, m, n_trials=2000)
        print(f"  Found {len(findings)} non-tet deficient configs (out of 2000 trials)")
        for f in findings:
            analyze_nontet(f, n, k, c, p, T)
