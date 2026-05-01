#!/usr/bin/env python3 -u
"""Test whether V_bad = ⋃_S V_S × V_S (up to lower-dim corrections).

Sample bad (s_1, s_2) (those with M > T) at small (n, c) where direct
enumeration is feasible, and check if each bad point lies in V_S × V_S
for some |S| = w+1 subset.

If 100% of bad points fit this pattern, the matching lower bound
codim V_bad = 2(c-1) follows (up to log poly factor).

Method:
  1. Pick random support tuple (E_1, ..., E_m) with m > T
  2. Pick random γ-tuple, find ker A(γ) (lock witnesses)
  3. For each (s_1, s_2) in ker A: extract the "support set" of s_1, s_2
     in Vandermonde basis (i.e., find S such that s_1, s_2 ∈ V_S)
  4. Report distribution of |S|.
"""

import sys, math, numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_clique_scan import rank_mod, kernel_mod
from op2_tet_consolidated import make_NEs, solve_for_witness


def vandermonde_full(L: list, D: int, p: int) -> np.ndarray:
    """Return n × D Vandermonde matrix (rows = ev_v for v ∈ [n])."""
    n = len(L)
    return np.array([[pow(L[v], j, p) for j in range(D)] for v in range(n)],
                    dtype=np.int64)


def find_min_S(s: np.ndarray, V_full: np.ndarray, p: int) -> int | None:
    """Smallest S ⊂ [n] with s ∈ V_S = span{V_full[v] : v ∈ S}.

    Returns the size of the smallest S, or None if s = 0.
    Uses brute search over subsets in increasing size.
    """
    n = V_full.shape[0]
    if not any(s % p):
        return 0
    # The minimum S size = rank of [s; V_full] - rank of V_full + ... no,
    # just: check if s is in span of any subset by minimum-rank argument.
    # Easier: dim of {s} ∪ {ev_v : v ∈ S} = |S| iff s ∈ V_S.
    # So the smallest S with s ∈ V_S satisfies |S| = rank{V_full[S], s} = |S|
    # i.e., adding s doesn't increase rank.
    # Just iterate subsets by size.
    for size in range(1, n + 1):
        for S in combinations(range(n), size):
            mat = np.vstack([V_full[list(S)], s.reshape(1, -1)])
            if rank_mod(mat, p) == size:
                return size
    return None


def find_min_joint_S(s1: np.ndarray, s2: np.ndarray, V_full: np.ndarray,
                      p: int) -> int | None:
    """Smallest S with (s_1, s_2) ∈ V_S × V_S, i.e., both in V_S."""
    n = V_full.shape[0]
    if not any(s1 % p) and not any(s2 % p):
        return 0
    for size in range(1, n + 1):
        for S in combinations(range(n), size):
            mat = np.vstack([V_full[list(S)], s1.reshape(1, -1),
                             s2.reshape(1, -1)])
            if rank_mod(mat, p) == size:
                return size
    return None


def test(n: int, c: int, p: int, n_witnesses: int = 30):
    D = n - n // 2; w = D - c; T = (2 * D - 1) // c
    print(f"\n=== n={n} c={c} p={p}: D={D} w={w} T={T}, target |S|={w+1} ===")
    omega = find_omega(n, p); L = [pow(omega, i, p) for i in range(n)]
    V_full = vandermonde_full(L, D, p)
    all_supports = list(combinations(range(n), w))
    rng = np.random.default_rng(0)
    m = T + 1
    counts = {}
    found = 0
    attempts = 0
    while found < n_witnesses and attempts < 500:
        attempts += 1
        # pick random m supports
        idx = rng.choice(len(all_supports), size=m, replace=False)
        Es = [all_supports[i] for i in idx]
        gammas = []
        seen = set()
        while len(gammas) < m:
            g = int(rng.integers(2, p))
            if g not in seen: gammas.append(g); seen.add(g)
        NEs = make_NEs(Es, L, p, D, c, w)
        A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
        if not ker: continue
        # For each kernel basis vector (s_1, s_2), check |S|
        for v in ker:
            s1 = v[:D] % p; s2 = v[D:] % p
            if not any(s1) and not any(s2): continue
            min_S = find_min_joint_S(s1, s2, V_full, p)
            counts[min_S] = counts.get(min_S, 0) + 1
            found += 1
            if found >= n_witnesses: break
    print(f"  attempts={attempts}, witnesses found={found}")
    print(f"  |S| distribution: {dict(sorted(counts.items()))}")
    target = w + 1
    pct_at_target = 100 * counts.get(target, 0) / max(1, found)
    pct_at_or_below = sum(v for k, v in counts.items() if k <= target) * 100 / max(1, found)
    print(f"  pct with |S| = {target}: {pct_at_target:.1f}%")
    print(f"  pct with |S| ≤ {target}: {pct_at_or_below:.1f}%")


def main():
    test(12, 3, 1009)  # D=6, w=3, w+1=4
    test(16, 4, 257)   # D=8, w=4, w+1=5
    test(20, 5, 41)    # D=10, w=5, w+1=6 (slow at p=1009)


if __name__ == '__main__':
    main()
