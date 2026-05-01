#!/usr/bin/env python3 -u
"""Empirical: count alternative supports T' ⊂ L for case-B realizers.

For case-B realizer (γ, E) with x_γ ∈ V_E and x_γ ∈ V_{S*}, T_γ is the
V_{S*}-support of x_γ. If E ≠ T_γ (case B), there's a "structural
dependency" Σ c_v ev_v = 0 with v ∈ T_γ ∪ E (an RS-codeword vanishing
outside T_γ ∪ E).

This script: at small (n, c, p), enumerate all bad witnesses (s_1, s_2)
∈ V_S × V_S with |S|=w+1, check whether their realizers (γ, E) are
case A or case B, and for case B, count the L-dependencies.

Key question: is the count of structural L-dependencies bounded
poly(n), or does it grow combinatorially?
"""

import sys, numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_clique_scan import rank_mod
from op2_tet_consolidated import make_NEs


def vandermonde_full(L: list, D: int, p: int) -> np.ndarray:
    n = len(L)
    return np.array([[pow(L[v], j, p) for j in range(D)] for v in range(n)],
                    dtype=np.int64)


def vandermonde_row(L_v: int, D: int, p: int) -> np.ndarray:
    return np.array([pow(L_v, j, p) for j in range(D)], dtype=np.int64)


def solve_realizer_gamma(s1: np.ndarray, s2: np.ndarray, NE: np.ndarray,
                          c: int, p: int) -> int | None:
    """Return γ such that NE @ (s1 + γ s2) = 0, or None if no consistent γ."""
    a = (NE @ s2) % p
    b = (NE @ s1) % p
    nz = next((j for j in range(c) if a[j] != 0), None)
    if nz is None:
        return None
    g = (-int(b[nz]) * pow(int(a[nz]), p - 2, p)) % p
    if g == 0: return None
    prop = all(
        (int(a[j_]) * int(b[k_]) - int(a[k_]) * int(b[j_])) % p == 0
        for j_ in range(c) for k_ in range(c)
    )
    return g if prop else None


def main():
    cases = [(12, 3, 1009), (16, 4, 257)]
    for n, c, p in cases:
        D = n - n // 2; w = D - c; T = (2 * D - 1) // c
        omega = find_omega(n, p); L = [pow(omega, i, p) for i in range(n)]
        all_supports = list(combinations(range(n), w))
        rng = np.random.default_rng(0)
        print(f"\n=== n={n} c={c} p={p}: D={D} w={w} T={T} ===")
        # Sample (s_1, s_2) ∈ V_S × V_S for |S|=w+1
        S_size = w + 1
        S = sorted(rng.choice(n, size=S_size, replace=False).tolist())
        V_S_basis = np.array([vandermonde_row(L[u], D, p) for u in S],
                             dtype=np.int64)
        n_samples = 5
        case_A_total = 0; case_B_total = 0
        for trial in range(n_samples):
            c1 = rng.integers(0, p, S_size)
            c2 = rng.integers(0, p, S_size)
            s1 = (c1 @ V_S_basis) % p
            s2 = (c2 @ V_S_basis) % p
            # Find all realizers
            realizers = []
            for E in all_supports:
                NE = make_NEs([E], L, p, D, c, w)[0]
                g = solve_realizer_gamma(s1, s2, NE, c, p)
                if g is not None:
                    realizers.append((g, E))
            # Compute T_gamma and check case A/B per realizer
            n_caseA, n_caseB = 0, 0
            for (g, E) in realizers:
                # T_γ = {v ∈ S : c1[i] + g·c2[i] ≠ 0 for v = S[i]}
                T_g = [S[i] for i in range(S_size)
                       if (int(c1[i]) + g * int(c2[i])) % p != 0]
                # Case A iff |T_g ∪ E| ≤ D, equivalently T_g ⊂ E (within S∪E)
                union_size = len(set(T_g) | set(E))
                if union_size <= D:
                    n_caseA += 1
                else:
                    n_caseB += 1
            print(f"  trial {trial}: M={len(realizers)} (case A: {n_caseA}, "
                  f"case B: {n_caseB}, T={T})")
            case_A_total += n_caseA
            case_B_total += n_caseB
        print(f"  Total across {n_samples} trials: "
              f"case A={case_A_total}, case B={case_B_total}")


if __name__ == '__main__':
    main()
