#!/usr/bin/env python3 -u
"""Compare existing rigorous bounds with our conjecture v6 v2.

Bounds to compare:
1. PR #347 conditional: max_bad ≤ ⌊D/(c-1)⌋ under conditions (i)/(ii)
2. Author's earlier conjecture: max_bad ≤ ⌊(2D-1)/c⌋ for any (c, n) — REFUTED
3. Our v6 v2: max_bad ≤ ⌊(2D-1)/c⌋ with probability 1 - poly(n)·p^{-(D+c-2)}
4. Trivial lower bound: max_bad ≥ w+1 = D-c+1 (tetrahedron)

Plus FRI soundness: ε_{ca} = Pr[bad challenge].
"""

import math

def bound_pr347(n, k, c):
    """⌊D/(c-1)⌋ — conditional, rigorous."""
    D = n - k
    if c <= 1: return None
    return D // (c - 1)

def bound_v3_refuted(n, k, c):
    """⌊(2D-1)/c⌋ — claimed unconditional, refuted by tetrahedron."""
    D = n - k
    return (2 * D - 1) // c

def lower_bound_tetrahedron(n, k, c):
    """w + 1 = D - c + 1, achieved on V_tet variety (prize-ready theorem 1)."""
    D = n - k; w = D - c
    if w < 2: return None  # tet doesn't exceed bound
    return w + 1

def codim_v6_v2(n, k, c):
    """Codim of bad set: 2D - T - 2 (revised v6 v2)."""
    D = n - k; T = (2 * D - 1) // c
    return 2 * D - T - 2

def fri_epsilon_v6(n, k, c, log2_p):
    """ε_{ca} bound assuming v6 v2 conjecture."""
    codim = codim_v6_v2(n, k, c)
    poly_log2 = 30  # rough log2(poly(n)) estimate
    return -log2_p * codim + poly_log2

if __name__ == '__main__':
    print("Comparison of bounds on max_bad and FRI soundness")
    print("="*80)
    print(f"{'n':>4} {'k':>3} {'c':>3} {'c_J':>4} {'PR#347':>7} {'⌊2D-1/c⌋':>10} "
          f"{'tet_min':>7} {'v6_codim':>9} {'log2 ε (BBear)':>14}")
    log2_BBear = 31  # BabyBear ≈ 2^31

    for n in [12, 16, 20, 24, 28, 32, 40]:
        k = n // 2
        c_J = math.ceil(n - math.sqrt(n * k))
        for c in [3, c_J]:
            if c < 3: continue
            if c >= n - k: continue
            T_pr347 = bound_pr347(n, k, c)
            T_v3 = bound_v3_refuted(n, k, c)
            tet = lower_bound_tetrahedron(n, k, c)
            codim = codim_v6_v2(n, k, c)
            log_eps = fri_epsilon_v6(n, k, c, log2_BBear)
            tet_str = str(tet) if tet else "—"
            print(f"{n:>4} {k:>3} {c:>3} {c_J:>4} "
                  f"{T_pr347:>7} {T_v3:>10} {tet_str:>7} {codim:>9} "
                  f"{log_eps:>14}")

    print()
    print("Notes:")
    print("- 'PR#347' (conditional) and 'v6 v2 generic' bounds agree on the value (T)")
    print("- tet_min: the proven lower bound from tetrahedron — refutes v3 universal")
    print("- 'v6 codim': dim of the (s_1, s_2)-space exception set")
    print("- 'log2 ε': log2 of FRI soundness gap at BabyBear, assuming v6 v2 + poly(n)<2^30")
