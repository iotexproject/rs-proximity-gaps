#!/usr/bin/env python3 -u
"""Empirical density of V_bad ∩ V_S × V_S for |S| > w+1 — Note 0119 Approach 4.

For (n, c, p) and varying |S|, sample (s_1, s_2) uniformly from V_S × V_S
and compute M(s_1, s_2) = #{γ : ∃ E with x_γ ∈ V_E}. Report:
  - bad fraction: # samples with M > T over total
  - mean M, max M

Theory (Note 0119 §"Sub-leading volume analysis"):
  For |S|=w+1: V_S × V_S ⊂ V_bad (codim 0 within V_S × V_S, codim 2(c-1) globally).
  For |S|=w+1+δ (δ ≥ 1): bad fraction should be ≤ q^{-(δ(T-2)+δ)} = q^{-δ(T-1)}.

If empirical bad fraction is ≈ q^{-δ(T-1)}: matches sub-leading prediction.
If significantly larger: possible Conjecture B violation or larger component.
"""

import sys, numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_tet_consolidated import make_NEs


def vandermonde_row(L_v: int, D: int, p: int) -> np.ndarray:
    return np.array([pow(L_v, j, p) for j in range(D)], dtype=np.int64)


def count_M(s1: np.ndarray, s2: np.ndarray, all_supports: list,
            L: list, p: int, D: int, c: int, w: int) -> int:
    realized = set()
    for E in all_supports:
        NE = make_NEs([E], L, p, D, c, w)[0]
        a = (NE @ s2) % p
        b = (NE @ s1) % p
        nz = next((j for j in range(c) if a[j] != 0), None)
        if nz is None:
            continue
        g = (-int(b[nz]) * pow(int(a[nz]), p - 2, p)) % p
        prop = all(
            (int(a[j_]) * int(b[k_]) - int(a[k_]) * int(b[j_])) % p == 0
            for j_ in range(c) for k_ in range(c)
        )
        if prop and g != 0:
            realized.add(g)
    return len(realized)


def test(n: int, c: int, p: int, S_size: int, n_samples: int = 100):
    D = n - n // 2
    w = D - c
    T = (2 * D - 1) // c
    delta_S = S_size - (w + 1)  # how much beyond w+1
    omega = find_omega(n, p)
    if omega is None:
        print(f"  no primitive root for n={n}, p={p}")
        return
    L = [pow(omega, i, p) for i in range(n)]
    all_supports = list(combinations(range(n), w))
    rng = np.random.default_rng(0)
    bad_count = 0
    M_values = []
    print(f"\n=== n={n} c={c} p={p} D={D} w={w} T={T} |S|={S_size} (δ={delta_S}) ===")
    for trial in range(n_samples):
        # pick random S of size S_size
        S = sorted(rng.choice(n, size=S_size, replace=False).tolist())
        V_S_basis = np.array([vandermonde_row(L[u], D, p) for u in S],
                             dtype=np.int64)
        c1 = rng.integers(0, p, S_size)
        c2 = rng.integers(0, p, S_size)
        s1 = (c1 @ V_S_basis) % p
        s2 = (c2 @ V_S_basis) % p
        M = count_M(s1, s2, all_supports, L, p, D, c, w)
        M_values.append(M)
        if M > T:
            bad_count += 1
    bad_frac = bad_count / n_samples
    pred_subleading = p ** (-(delta_S * (T - 1))) if delta_S >= 1 else 1.0
    print(f"  M stats: min={min(M_values)} mean={np.mean(M_values):.2f} "
          f"max={max(M_values)} T={T}")
    print(f"  bad fraction (M > T): {bad_frac:.4f} ({bad_count}/{n_samples})")
    if delta_S >= 1:
        print(f"  Note 0119 sub-leading prediction: ≤ p^{{-δ(T-1)}} = "
              f"p^{{-{delta_S*(T-1)}}} = {pred_subleading:.2e}")


def main():
    print("# Density of V_bad ∩ V_S × V_S for varying |S|")
    # baseline: |S| = w+1 (should be ~100% bad, M ~ w+1)
    print("\n## |S| = w+1 (leading component, expected ~100% bad)")
    for n, c, p in [(12, 3, 1009), (16, 4, 257), (20, 5, 41)]:
        D = n - n // 2; w = D - c
        test(n, c, p, S_size=w + 1, n_samples=30)

    # case (b) deeper: |S| = w+2, w+3
    print("\n## |S| = w+2 (sub-leading δ=1, expected very rare bad)")
    for n, c, p in [(12, 3, 1009), (16, 4, 257), (20, 5, 41)]:
        D = n - n // 2; w = D - c
        test(n, c, p, S_size=w + 2, n_samples=200)

    print("\n## |S| = w+3 (sub-leading δ=2)")
    for n, c, p in [(12, 3, 1009), (16, 4, 257)]:
        D = n - n // 2; w = D - c
        test(n, c, p, S_size=w + 3, n_samples=200)


if __name__ == '__main__':
    main()
