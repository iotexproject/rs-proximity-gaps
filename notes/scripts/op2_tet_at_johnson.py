#!/usr/bin/env python3 -u
"""Verify tetrahedron bound-violation at c = c_J (Johnson radius).

#322 comments reported empirical max_bad ≤ 4 for n=28..40 at c=c_J.
Random search misses the tetrahedron (measure-zero kernel).
Algebraic search via kernel always finds it.

Compute c_J for rate 1/2, then test tetrahedron realizability.
"""

import sys
import math
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega, elp
from op2_clique_scan import rank_mod, kernel_mod, derive_realized_gammas

def c_johnson(n, k):
    """c_J such that w_J = D - c_J ≈ Johnson radius."""
    w_J = math.floor(n - math.sqrt(n * k))  # Johnson radius bound
    D = n - k
    c_J = D - w_J
    return max(c_J, 2)

def test_tet_at_cJ(n, k, c, p, V):
    D = n - k; w = D - c
    if len(V) != w + 1: return None
    omega = find_omega(n, p)
    if omega is None: return None
    L = [pow(omega, i, p) for i in range(n)]
    Es = list(combinations(V, w))
    m = len(Es)
    bound = (2 * D - 1) // c

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

    rng = np.random.default_rng(42)
    best = 0; best_info = None
    for trial in range(20):
        gammas = []
        seen = set()
        while len(gammas) < m:
            g = int(rng.integers(2, p))
            if g not in seen:
                gammas.append(g); seen.add(g)
        A = np.zeros((m * c, 2 * D), dtype=np.int64)
        for i in range(m):
            A[i*c:(i+1)*c, :D] = NEs[i]
            A[i*c:(i+1)*c, D:] = (gammas[i] * NEs[i]) % p
        rA = rank_mod(A, p)
        if rA >= min(m * c, 2 * D): continue
        ker = kernel_mod(A, p)
        for u in ker[:8]:
            v = np.array(u, dtype=np.int64)
            s1 = v[:D]; s2 = v[D:]
            if not np.any(s2 != 0): continue
            der = derive_realized_gammas(NEs, gammas, s1, s2, p, c)
            distinct = set(g for g in der if g is not None)
            if len(distinct) > best:
                best = len(distinct)
    return {'n': n, 'c': c, 'w': w, 'V': V, 'm': m, 'bound': bound,
            'best_realized': best}

if __name__ == '__main__':
    print("=== Tetrahedron bound-violation at c = c_J (Johnson radius) ===")
    print("These are the #322 reference cases (empirical max ≤ 4 via random)")
    print()
    print(f"{'n':>4} {'k':>4} {'c_J':>4} {'w':>4} {'m=w+1':>6} {'bound':>6} {'best':>6} {'p':>6} {'verdict'}")
    for n in [16, 20, 24, 28, 32, 36, 40]:
        k = n // 2
        c = c_johnson(n, k)
        D = n - k; w = D - c
        if w < 1: continue
        # Find a prime with primitive n-th root of unity
        p = 1009
        while p < 50000:
            if find_omega(n, p) is not None: break
            p += 2
        if find_omega(n, p) is None:
            print(f"{n:>4}: no prime found"); continue
        # Try several V choices
        best = 0
        for V in [tuple(range(w+1)),
                  tuple(range(1, w+2)),
                  tuple(i*2 for i in range(w+1) if i*2 < n),
                  tuple(i*3 for i in range(w+1) if i*3 < n)]:
            if len(V) != w + 1: continue
            r = test_tet_at_cJ(n, k, c, p, V)
            if r is None: continue
            if r['best_realized'] > best:
                best = r['best_realized']
        m = w + 1
        bound = (2 * D - 1) // c
        marker = "⚠️ violated" if best > bound else "(no violation found)"
        print(f"{n:>4} {k:>4} {c:>4} {w:>4} {m:>6} {bound:>6} {best:>6} {p:>6}  {marker}")
