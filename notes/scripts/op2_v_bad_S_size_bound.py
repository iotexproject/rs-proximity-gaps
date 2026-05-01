#!/usr/bin/env python3 -u
"""Test |S*| ≤ w + floor(w/T) for V_bad witnesses across a wider (n, c) range.

Note 0119 proves this bound when |E ∪ S*| ≤ D (case (a)). For deployment
parameters case (b) dominates (|E ∪ S*| > D). This script tests whether
the bound still holds empirically in case (b).

Output columns:
  (n, c, p): RS parameters (D = n//2 + 1 - 1 = n - n//2)
  D, w, T:   derived
  bound = w + floor(w/T): proof's predicted upper bound on |S*|
  observed |S*| distribution
  pct ≤ bound: should be 100% if bound is tight even in case (b)
"""

import sys, math, numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_clique_scan import rank_mod
from op2_tet_consolidated import make_NEs, solve_for_witness


def vandermonde_full(L: list, D: int, p: int) -> np.ndarray:
    n = len(L)
    return np.array([[pow(L[v], j, p) for j in range(D)] for v in range(n)],
                    dtype=np.int64)


def find_min_joint_S_bounded(s1: np.ndarray, s2: np.ndarray,
                              V_full: np.ndarray, p: int,
                              max_size: int) -> int | None:
    """Smallest S with s1, s2 ∈ V_S, searching up to max_size only.

    Returns None if no S with |S| ≤ max_size works (i.e., |S*| > max_size).
    Useful at large n where 2^n enumeration infeasible.
    """
    n = V_full.shape[0]
    if not any(s1 % p) and not any(s2 % p):
        return 0
    for size in range(1, min(max_size, n) + 1):
        for S in combinations(range(n), size):
            mat = np.vstack([V_full[list(S)], s1.reshape(1, -1),
                             s2.reshape(1, -1)])
            if rank_mod(mat, p) == size:
                return size
    return None  # |S*| > max_size


def case_b(E_size: int, S_size: int, D: int) -> bool:
    """Worst-case |E ∪ S*| > D check (when E disjoint from S*)."""
    return E_size + S_size > D


def test(n: int, c: int, p: int, n_witnesses: int = 30, search_margin: int = 3):
    D = n - n // 2
    w = D - c
    T = (2 * D - 1) // c
    if w < 1 or T < 1:
        return
    bound = w + (w // T)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    V_full = vandermonde_full(L, D, p)
    all_supports = list(combinations(range(n), w))
    rng = np.random.default_rng(0)
    m = T + 1
    counts = {}
    over = 0  # witnesses with |S*| > bound + search_margin (definitely violations)
    found = 0
    attempts = 0
    case_b_flag = case_b(w, bound, D)
    print(f"\n=== n={n} c={c} p={p}: D={D} w={w} T={T}, bound={bound}, "
          f"case-b: {case_b_flag} ===")
    max_search = min(n, bound + search_margin)
    while found < n_witnesses and attempts < 1000:
        attempts += 1
        idx = rng.choice(len(all_supports), size=m, replace=False)
        Es = [all_supports[i] for i in idx]
        gammas = []
        seen = set()
        while len(gammas) < m:
            g = int(rng.integers(2, p))
            if g not in seen:
                gammas.append(g)
                seen.add(g)
        NEs = make_NEs(Es, L, p, D, c, w)
        try:
            A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
        except Exception:
            continue
        if not ker:
            continue
        for v in ker:
            s1 = v[:D] % p
            s2 = v[D:] % p
            if not any(s1) and not any(s2):
                continue
            min_S = find_min_joint_S_bounded(s1, s2, V_full, p, max_search)
            if min_S is None:
                over += 1
                counts['>%d' % max_search] = counts.get('>%d' % max_search, 0) + 1
            else:
                counts[min_S] = counts.get(min_S, 0) + 1
            found += 1
            if found >= n_witnesses:
                break
    pct_at_or_below = sum(v for k, v in counts.items()
                          if isinstance(k, int) and k <= bound) * 100 / max(1, found)
    print(f"  attempts={attempts}, witnesses={found}")
    print(f"  |S*| distribution: {dict(sorted(counts.items(), key=lambda kv: (isinstance(kv[0], str), kv[0])))}")
    print(f"  pct |S*| ≤ {bound}: {pct_at_or_below:.1f}%  "
          f"(violations: {over}, search range up to {max_search})")


def main():
    # All n use primes with primitive n-th root of unity (verified).
    # case (a)-friendly are smaller n; deployment-mimicking are larger n.
    print("# Wider sweep — verifying |S*| ≤ w + floor(w/T) (Note 0119 bound):")
    # (n, c, p) — test cases:
    cases = [
        (12, 3, 1009),
        (14, 3, 1009),
        (16, 4, 257),
        (16, 3, 257),
        (18, 3, 1009),
        (18, 5, 1009),
        (20, 5, 41),
        (20, 4, 41),
        (24, 4, 1009),
        (24, 6, 1009),
        (24, 5, 1009),
        (28, 4, 1009),
        (28, 6, 1009),
        (28, 7, 1009),
        # Extension to larger n (Note 0119 case-B robustness):
        (30, 3, 4051),  # D=15 w=12 T=9 bound=13
        (30, 5, 4051),  # D=15 w=10 T=5 bound=12
        (32, 4, 257),   # D=16 w=12 T=7 bound=13
        (32, 6, 257),   # D=16 w=10 T=5 bound=12
        (36, 4, 73),    # D=18 w=14 T=8 bound=15
        (36, 6, 73),    # D=18 w=12 T=5 bound=14
        (40, 5, 4001),  # D=20 w=15 T=7 bound=17
    ]
    for n, c, p in cases:
        try:
            test(n, c, p, n_witnesses=20)
        except Exception as e:
            print(f"  ERROR at n={n} c={c} p={p}: {e}")


if __name__ == '__main__':
    main()
