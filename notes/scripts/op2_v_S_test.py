#!/usr/bin/env python3 -u
"""Direct test: does V_S × V_S ⊂ V_bad at small (n, c)?

For each (s_1, s_2) sampled from V_S × V_S where |S| = w+1, count M:
the number of distinct γ ∈ F_p^* such that ∃ E ⊂ [n] of size w with
s_1 + γ s_2 ∈ ker N_E.

If 100% of samples have M > T, then V_S × V_S ⊂ V_bad and codim V_bad
≤ 2D - 2(w+1) = 2(c-1).

Test cases: n=16 c=4 (where Note 0103 says empirical codim 7.8, formula
predicts ≤ 6).
"""

import sys, numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_tet_consolidated import make_NEs


def vandermonde_row(L_v: int, D: int, p: int) -> np.ndarray:
    return np.array([pow(L_v, j, p) for j in range(D)], dtype=np.int64)


def in_ker_NE(v: np.ndarray, NE: np.ndarray, p: int) -> bool:
    return all((NE @ v) % p == 0)


def count_M(s1: np.ndarray, s2: np.ndarray, all_supports: list,
            L: list, p: int, D: int, c: int, w: int) -> int:
    """Count distinct γ ∈ F_p^* with ∃ E (size w) s.t. s_1 + γ s_2 ∈ ker N_E."""
    realized = set()
    for E in all_supports:
        NE = make_NEs([E], L, p, D, c, w)[0]
        # Solve for γ: NE @ s_1 + γ NE @ s_2 = 0
        a = (NE @ s2) % p   # c-vec
        b = (NE @ s1) % p   # c-vec
        # Find γ such that b + γ a = 0
        nz = next((j for j in range(c) if a[j] != 0), None)
        if nz is None:
            if all(b == 0):
                # underdetermined — every γ works; skip ambiguity for counting
                continue
            else:
                continue
        g = (-int(b[nz]) * pow(int(a[nz]), p - 2, p)) % p
        # check proportionality: b[j]·a[k] = b[k]·a[j]
        prop = all(
            (int(a[j_]) * int(b[k_]) - int(a[k_]) * int(b[j_])) % p == 0
            for j_ in range(c) for k_ in range(c)
        )
        if prop and g != 0:
            realized.add(g)
    return len(realized)


def test(n: int, c: int, p: int, n_samples: int = 30, S_size: int | None = None):
    D = n - n // 2; w = D - c; T = (2 * D - 1) // c
    omega = find_omega(n, p); L = [pow(omega, i, p) for i in range(n)]
    print(f"\n=== n={n} c={c} p={p}: D={D} w={w} T={T} ===")
    if S_size is None:
        S_size = w + 1
    # Pick a random S of size S_size, build Vandermonde basis on S
    rng = np.random.default_rng(0)
    S = sorted(rng.choice(n, size=S_size, replace=False).tolist())
    print(f"  S = {S} (|S|={S_size})")
    V_S_basis = np.array([vandermonde_row(L[u], D, p) for u in S], dtype=np.int64)
    # All supports of size w
    all_supports = list(combinations(range(n), w))
    print(f"  enumerating {len(all_supports)} supports of size {w}...")
    # Sample (s_1, s_2) from V_S × V_S
    M_values = []
    for trial in range(n_samples):
        c1 = rng.integers(0, p, S_size)
        c2 = rng.integers(0, p, S_size)
        s1 = (c1 @ V_S_basis) % p
        s2 = (c2 @ V_S_basis) % p
        M = count_M(s1, s2, all_supports, L, p, D, c, w)
        M_values.append(M)
    print(f"  M stats: min={min(M_values)}, mean={np.mean(M_values):.2f}, "
          f"max={max(M_values)}, T={T}")
    n_bad = sum(1 for M in M_values if M > T)
    print(f"  M > T (= bad witness): {n_bad}/{n_samples}")
    return n_bad, n_samples


def main():
    # Note 0103 empirical: n=16 c=4 p=1009 codim ≈ 7.8
    # Worst-case formula: codim ≤ 2(c-1) = 6, requires V_S × V_S ⊂ V_bad
    test(16, 4, 1009, n_samples=20, S_size=5)
    test(20, 5, 41,   n_samples=20, S_size=6)
    test(24, 4, 1009, n_samples=20, S_size=9)
    test(24, 5, 1009, n_samples=20, S_size=8)
    # Reduce to n=12 c=3 (w+1 = 4)
    test(12, 3, 1009, n_samples=20, S_size=4)
    # Confirm |S| > w+1 gives no realizers
    test(16, 4, 1009, n_samples=10, S_size=6)
    test(16, 4, 1009, n_samples=10, S_size=8)


if __name__ == '__main__':
    main()
