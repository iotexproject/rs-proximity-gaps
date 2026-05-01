"""sparse_2term_q193.py — verify polynomial-degree witness extends to q=193.

The witness `d_1(alpha) >= n_1 - floor(j/2)` is a PURE COMBINATORIAL bound
(polynomial degree → root count), so it should hold for ALL q.

This script:
1. Repeats sparse 2-term scan at q=193.
2. Confirms the polynomial-degree bound RIGOROUSLY across all (i, j).
3. Finds worst above-J tie among sparse 2-term at q=193.
4. Compares to the q=193 K=2 dense leader (0.3827).

If sparse 2-term worst < 0.3827, then dense f IS the q=193 worst case
and the polynomial-degree witness alone doesn't cover it.
"""
from __future__ import annotations
import sys, os
import numpy as np
from itertools import combinations
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

P = 193
N0 = 32
K0 = 8
R = 2
W_J = 16

import probe_step5_n32_studio
probe_step5_n32_studio.P = P
probe_step5_n32_studio.N0 = N0
probe_step5_n32_studio.K0 = K0

from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_at_L(coeffs, L, p):
    n = len(L)
    out = [0] * n
    for i, x in enumerate(L):
        v = 0
        for k, c in enumerate(coeffs):
            if c != 0:
                v = (v + c * pow(x, k, p)) % p
        out[i] = v
    return out


def fast_d1(fold1, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1):
    fold1_arr = np.array(fold1, dtype=np.int64)
    extras = batched_extras(info_sets_arr, fold1_arr, L1_arr, D1, inv_D1, p)
    return n1 - k1 - int(extras.max())


def main():
    chain = setup_chain(P, N0, K0, R=R)
    L0, _, _ = chain[0]
    L1, k1, _ = chain[1]
    n0, n1 = len(L0), len(L1)
    L1_arr = np.array(L1, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, P)
    info_sets = list(combinations(range(n1), k1))
    info_sets_arr = np.array(info_sets, dtype=np.int64)

    print(f"=== Sparse 2-term universal scan at q={P} ===")
    print(f"Comparing to q=193 K=2 dense leader: tie = 0.3827")
    print()
    print(f"{'(i, j)':>10} {'parity':>14} {'pred d_1':>10} {'min d_1≠0':>11} {'above-J?':>10} {'tie_d1':>8}")
    print("-" * 70)

    results = []
    for j in range(K0 + 1, 16):
        for i in range(K0, j):
            i_par = i % 2
            j_par = j % 2
            if i_par == j_par:
                parity = "odd-odd(K=1)" if i_par == 1 else "even-even(K=1)"
            else:
                parity = "mixed(K=2)"
            pred_d1 = n1 - ((j + 1) // 2)

            coeffs = [0] * N0
            coeffs[i] = 1
            coeffs[j] = 1
            f_vals = evaluate_at_L(coeffs, L0, P)
            f_e, f_o = even_odd_parts(f_vals, L0, P)

            min_d1_nz = n1
            d1_counter = Counter()
            for alpha in range(P):
                fold_a = [(f_e[k] + alpha * f_o[k]) % P for k in range(n1)]
                d_a = fast_d1(fold_a, L1_arr, info_sets_arr, D1, inv_D1, P, n1, k1)
                d1_counter[d_a] += 1
                if alpha != 0 and d_a < min_d1_nz:
                    min_d1_nz = d_a

            above_J = (2 * min_d1_nz) > W_J
            tie_d1 = sum((1 - d/n1) * c for d, c in d1_counter.items()) / P

            results.append({
                "i": i, "j": j, "parity": parity,
                "pred_d1": pred_d1, "min_d1_nz": min_d1_nz,
                "above_J": above_J, "tie_d1": tie_d1,
            })

            tag = "above-J" if above_J else "below-J"
            print(f"  ({i:2d}, {j:2d})  {parity:>14}  {pred_d1:>6}  {min_d1_nz:>6}  {tag:>10}  {tie_d1:.4f}")

    print()
    print("=== Summary ===")
    above_J_results = [r for r in results if r["above_J"]]
    print(f"Above-J: {len(above_J_results)}/{len(results)}")
    if above_J_results:
        worst = max(above_J_results, key=lambda r: r["tie_d1"])
        print(f"\nWorst sparse 2-term above-J at q={P}:")
        print(f"  ({worst['i']}, {worst['j']}) {worst['parity']}: tie_d1 = {worst['tie_d1']:.4f}")
        print(f"  predicted d_1 >= {worst['pred_d1']}, empirical min = {worst['min_d1_nz']}")
        print(f"\n  Compare q=193 K=2 dense leader: 0.3827")
        if worst['tie_d1'] >= 0.3827:
            print(f"  ★ Sparse 2-term EXCEEDS dense — polynomial-degree witness covers worst case!")
        else:
            gap = 0.3827 - worst['tie_d1']
            print(f"  Sparse 2-term BELOW dense by {gap:.4f} — need separate argument for dense K=2.")

    violations = [r for r in results if r["above_J"] and r["min_d1_nz"] < r["pred_d1"]]
    if violations:
        print(f"\n!!! ABOVE-J violations: {len(violations)}")
    else:
        print(f"\n=== Polynomial-degree witness holds for ALL above-J sparse 2-term at q={P} ===")


if __name__ == "__main__":
    main()
