"""dense_K2_q449.py — verify dense K=2 worst-case tie SHRINKS with q to confirm
dense → sparse convergence (Question 0140.A).

Hypothesis: number of d_1=9 tuples is BOUNDED (constant), not q-proportional.
Then dense - sparse gap = (constant)/q → 0 as q → ∞.

Reuses sweep_K2_q193 infrastructure but at q=449.
"""
from __future__ import annotations
import sys, os, random, time
import numpy as np
from itertools import combinations, product
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

P = 449
N0 = 32
K0 = 8
R = 2

import probe_step5_n32_studio
probe_step5_n32_studio.P = P
probe_step5_n32_studio.N0 = N0
probe_step5_n32_studio.K0 = K0

# Reuse the q=193 module's logic
import sweep_K2_q193
sweep_K2_q193.P = P
sweep_K2_q193.N0 = N0
sweep_K2_q193.K0 = K0

from fri_2round_attack import setup_chain, parity_check, gauss_rank
from sweep_K2_q193 import construct_K2_psi_in_U, compute_tie_with_above_J_check


def main():
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)

    print(f"=== Dense K=2 random above-J at q={p} ===")
    print(f"Each tie eval: {p}^2 = {p**2:,} tuples, ~30s/case")

    rng = random.Random(2026)
    n_tested = 0
    n_above_J = 0
    max_tie_above_J = 0.0
    max_case = None
    target = 5
    t0 = time.time()
    while n_above_J < target and n_tested < 30:
        n_tested += 1
        f, T1, T2 = construct_K2_psi_in_U(rng, p, chain, H_R, n_R)
        if f is None:
            continue
        tie, d1d, min_d1, above_J = compute_tie_with_above_J_check(f, chain, p)
        status = "above-J" if above_J else "below-J"
        elapsed = time.time() - t0
        d1_low = sum(c for d, c in d1d.items() if d <= 9)
        print(f"  attempt {n_tested}: {status} (min d_1={min_d1}), tie={tie:.4f}, "
              f"d_1≤9 tuples={d1_low}, T1={T1}, T2={T2}, elapsed={elapsed:.0f}s")
        if above_J:
            n_above_J += 1
            if tie > max_tie_above_J:
                max_tie_above_J = tie
                max_case = (T1, T2, d1d, tie)

    print(f"\n=== Summary ===")
    print(f"  Tested: {n_tested} K=2 candidates")
    print(f"  Above-J: {n_above_J}")
    print(f"  Max tie among above-J at q={p}: {max_tie_above_J:.4f}")
    print(f"  Compare:")
    print(f"    q=97  K=2 max: 0.4477 (low-q artifact)")
    print(f"    q=193 K=2 max: 0.3827 (10 d_1=9 tuples)")
    print(f"    q=257 K=2 max: 0.3801 (~11 d_1=9 tuples)")
    print(f"    q=449 K=2 max: {max_tie_above_J:.4f}")
    if max_case:
        T1, T2, d1d, tie = max_case
        n9 = d1d.get(9, 0)
        d1_top = dict(sorted(d1d.items())[:6])
        print(f"  Worst d_1 distribution: {d1_top}")
        print(f"  d_1=9 tuples: {n9} (q=193: 10, q=257: ~11)")
        # Predict tie from d_1 only: (n9 * 7/16 + (p-n9) * 6/16) / p
        n1 = 16
        # Rough prediction: (n9 * 7 + (p - n9) * 6) / (16 p) = (6 + n9/p)/16
        n_d1_le_9 = sum(c for d, c in d1d.items() if d <= 9)
        tie_d1_est = (n_d1_le_9 * (1 - 9/n1) + (p - n_d1_le_9) * (1 - 10/n1)) / p
        print(f"  Predicted tie (d_1 only, assuming d_1≥10 elsewhere): {tie_d1_est:.4f}")
        print(f"  Sparse 2-term limit (asymptotic, d_2 negligible): 6/16 = 0.3750")


if __name__ == "__main__":
    main()
