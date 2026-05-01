#!/usr/bin/env python3 -u
"""Test if tetrahedron pattern is realizable at large primes.

Setup: n=12, c=3. Tetrahedron = 4 size-3 subsets of a 4-set.
Question: does the algebraic system {N_{V\{v_i}}·s_1 = -γ_i N_{V\{v_i}}·s_2 ∀i}
have non-trivial solutions at sufficiently large primes?

If NO: lemma effectively holds at large p (no bad config).
If YES: lemma fails structurally even at large p.
"""

import sys, time
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega, elp, count_bad_gammas, precompute_NE

def test_tetrahedron(n, k, c, p, V, n_trials=2_000_000):
    """Test if 4 supports = subsets of V give 4 distinct bad γ at prime p."""
    D = n - k; w = D - c
    omega = find_omega(n, p)
    if omega is None: return None
    L = [pow(omega, i, p) for i in range(n)]

    E_tet = list(combinations(V, w))  # 4 supports if |V|=w+1

    NE_list = []
    for E in E_tet:
        lam = elp(E, L, p)
        N = np.zeros((c, D), dtype=np.int64)
        for r in range(c):
            for j in range(D):
                t = j - r
                if 0 <= t <= w:
                    N[r, j] = lam[t] % p
        NE_list.append(N)

    rng = np.random.default_rng(0)
    found = 0
    for trial in range(n_trials):
        s1 = rng.integers(0, p, size=D, dtype=np.int64)
        s2 = rng.integers(0, p, size=D, dtype=np.int64)
        if not np.any(s2 != 0): continue
        gammas = []
        ok = True
        for N in NE_list:
            aE = (N @ s2) % p; bE = (N @ s1) % p
            if not np.any(aE != 0): ok = False; break
            comp = True
            for i_ in range(c):
                for j_ in range(c):
                    if (aE[i_] * bE[j_] - aE[j_] * bE[i_]) % p != 0:
                        comp = False; break
                if not comp: break
            if not comp: ok = False; break
            for i_ in range(c):
                if aE[i_] != 0:
                    g = (-bE[i_] * pow(int(aE[i_]), p-2, p)) % p
                    gammas.append(int(g)); break
        if not ok: continue
        if len(set(gammas)) >= len(E_tet):
            found += 1
            if found == 1:
                print(f"  trial {trial}: tetrahedron achievable at p={p}, V={V}")
                return True
    return False

if __name__ == '__main__':
    n, k, c = 12, 6, 3
    print(f"=== Tetrahedron achievability test at n={n} c={c} ===")
    print(f"bound = {(2*(n-k)-1)//c} = 3, m = 4 > bound")

    # Test multiple V sets at various primes
    V_candidates = [
        (0, 1, 2, 3),
        (1, 4, 5, 8),  # the original p=61 witness
        (0, 3, 6, 9),
        (0, 2, 5, 11),
        (0, 1, 5, 8),
    ]

    for p in [61, 109, 229, 601, 1009, 4001]:
        print(f"\n--- p = {p} ---")
        any_found = False
        for V in V_candidates:
            t0 = time.time()
            r = test_tetrahedron(n, k, c, p, V, n_trials=1_000_000)
            dt = time.time() - t0
            print(f"  V={V}: tetrahedron achievable = {r}  ({dt:.0f}s)")
            if r: any_found = True
        if not any_found and p >= 1009:
            print(f"  → At p={p}, NO tetrahedron achievable. Lemma holds.")
