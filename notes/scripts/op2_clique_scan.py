#!/usr/bin/env python3 -u
"""Scan: how big can the bound violation get?

Given c, w, take a (w+t)-vertex set V; consider all C(w+t, w) size-w subsets.
Build A with these as supports + random distinct γ_i. Compute rank(A) and
kernel. From kernel, derive how many distinct γ are jointly realizable.

Claim: m_max = #(distinct γ realizable simultaneously) gives a bound-violator
when m_max > ⌊(2D-1)/c⌋.

Goal: find the worst-case ratio m_max/bound across (n, c, t) settings.
"""

import sys
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega, elp

def rank_mod(M, p):
    M = M.copy() % p
    R, C = M.shape; r = 0
    for col in range(C):
        pv = None
        for i in range(r, R):
            if M[i, col] != 0: pv = i; break
        if pv is None: continue
        M[[r, pv]] = M[[pv, r]]
        inv = pow(int(M[r, col]), p-2, p)
        M[r] = (M[r] * inv) % p
        for i in range(R):
            if i != r and M[i, col] != 0:
                M[i] = (M[i] - M[i, col] * M[r]) % p
        r += 1
    return r

def kernel_mod(M, p):
    M = M.copy() % p
    R, C = M.shape
    pivot_col = -np.ones(R, dtype=np.int64); r = 0
    for col in range(C):
        if r >= R: break
        pv = None
        for i in range(r, R):
            if M[i, col] != 0: pv = i; break
        if pv is None: continue
        M[[r, pv]] = M[[pv, r]]
        inv = pow(int(M[r, col]), p-2, p)
        M[r] = (M[r] * inv) % p
        for i in range(R):
            if i != r and M[i, col] != 0:
                M[i] = (M[i] - M[i, col] * M[r]) % p
        pivot_col[r] = col; r += 1
    pivots = set(int(c) for c in pivot_col[:r] if c >= 0)
    free_cols = [c for c in range(C) if c not in pivots]
    basis = []
    for fc in free_cols:
        v = np.zeros(C, dtype=np.int64); v[fc] = 1
        for i in range(r):
            pc = int(pivot_col[i])
            if pc >= 0: v[pc] = (-int(M[i, fc])) % p
        basis.append(v)
    return basis

def derive_realized_gammas(NEs, gammas, s1, s2, p, c):
    """For (s_1, s_2), return list of γ_i actually realized (None if E_i degenerate)."""
    out = []
    for i, N in enumerate(NEs):
        aE = (N @ s2) % p
        bE = (N @ s1) % p
        nz = None
        for j in range(c):
            if aE[j] != 0: nz = j; break
        if nz is None: out.append(None); continue
        gd = (-int(bE[nz]) * pow(int(aE[nz]), p-2, p)) % p
        prop = all(
            (int(aE[j_]) * int(bE[k_]) - int(aE[k_]) * int(bE[j_])) % p == 0
            for j_ in range(c) for k_ in range(c)
        )
        out.append(gd if prop else None)
    return out

def test_clique(n, k, c, t, p, n_trials=20):
    D = n - k; w = D - c
    if w + t > n: return None
    omega = find_omega(n, p)
    if omega is None: return None
    L = [pow(omega, i, p) for i in range(n)]
    V = tuple(range(w + t))  # use first w+t vertices
    Es = list(combinations(V, w))
    m = len(Es)
    bound = (2 * D - 1) // c

    # Build N_E for each support
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
    best = 0
    best_info = None
    for trial in range(n_trials):
        gammas = []
        seen = set()
        while len(gammas) < m:
            g = int(rng.integers(2, p))
            if g not in seen:
                gammas.append(g); seen.add(g)
        # Build A
        A = np.zeros((m * c, 2 * D), dtype=np.int64)
        for i in range(m):
            A[i*c:(i+1)*c, :D] = NEs[i]
            A[i*c:(i+1)*c, D:] = (gammas[i] * NEs[i]) % p
        rA = rank_mod(A, p)
        full = min(m * c, 2 * D)
        if rA >= full: continue
        ker = kernel_mod(A, p)
        # Try each kernel basis vector + a few random combinations
        for u in ker[:8] + [
            (rng.integers(1, 5) * ker[0] + rng.integers(1, 5) * ker[1]) % p
            if len(ker) >= 2 else ker[0]
            for _ in range(5)
        ]:
            v = np.array(u, dtype=np.int64)
            s1 = v[:D]; s2 = v[D:]
            if not np.any(s2 != 0): continue
            der = derive_realized_gammas(NEs, gammas, s1, s2, p, c)
            distinct = set(g for g in der if g is not None)
            if len(distinct) > best:
                best = len(distinct)
                best_info = {
                    'trial': trial, 'kerdim': len(ker),
                    'realized_count': len(distinct),
                    's2_nz': int(np.sum(s2 != 0)),
                }
    return {'n': n, 'c': c, 't': t, 'm_supports': m, 'bound': bound,
            'best_realized': best, 'ratio': best / max(bound, 1),
            'info': best_info}

if __name__ == '__main__':
    print("=== Clique pattern bound-violation scan ===")
    print("Tests (w+t)-vertex sets with all C(w+t, w) size-w supports.")
    print("t=1 → tetrahedron (w+1 supports).")
    print("t=2 → larger clique (C(w+2, w) supports).")
    print()
    print(f"{'n':>4} {'c':>3} {'t':>3} {'m':>4} {'bound':>6} {'best':>6} {'ratio':>7}")
    for c in [3, 4, 5]:
        for n in [12, 16, 20, 24]:
            k = n // 2
            D = n - k; w = D - c
            if w < 1: continue
            for t in [1, 2, 3]:
                if w + t > n: continue
                # Need a prime large enough to have primitive n-th root
                p = 1009
                while p < 5000:
                    if find_omega(n, p) is not None: break
                    p += 2
                if find_omega(n, p) is None: continue
                r = test_clique(n, k, c, t, p, n_trials=10)
                if r is None: continue
                marker = " ⚠️" if r['best_realized'] > r['bound'] else ""
                print(f"{n:>4} {c:>3} {t:>3} {r['m_supports']:>4} {r['bound']:>6} "
                      f"{r['best_realized']:>6} {r['ratio']:>7.2f}{marker}")
