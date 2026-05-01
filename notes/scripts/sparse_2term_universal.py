"""sparse_2term_universal.py — exhaustive enum of sparse 2-term f at toy q=97.

Goal: verify the universal polynomial-degree witness theorem for ALL sparse 2-term
above-J f, covering BOTH K=1 (same-parity) and K=2 (mixed-parity).

For f = c_1 x^i + c_2 x^j with k_0 <= i < j <= n_0 - 1, both nonzero:
- max(i, j) = j gives dist(f, C_0) >= n_0 - j (above-J iff j <= 15).
- fold_alpha(y) is poly in y of degree:
    * (j-1)/2 if both odd (K=1 odd-odd)
    *  j/2     if both even (K=1 even-even)
    *  max(i_e/2, (i_o-1)/2) if mixed parity (K=2)
  In all cases <= ceil(j/2).
- Hence d_1(alpha) >= n_1 - ceil(j/2) for alpha != 0.
"""
from __future__ import annotations
import sys, os
import numpy as np
from itertools import combinations
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

P = 97
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

    print(f"=== Sparse 2-term universal scan at q={P}, n0={N0}, k0={K0}, n1={n1}, k1={k1} ===")
    print(f"Predicted: d_1(alpha != 0) >= n_1 - ceil(j/2) = {n1} - ceil(j/2)")
    print()
    print(f"{'(i, j)':>10} {'parity':>14} {'pred d_1':>10} {'min d_1≠0':>11} {'min d_1':>9} {'above-J?':>10} {'tie_d1':>8}")
    print("-" * 80)

    results = []
    for j in range(K0 + 1, 16):
        for i in range(K0, j):
            i_par = i % 2
            j_par = j % 2
            if i_par == j_par:
                if i_par == 1:
                    parity = "odd-odd(K=1)"
                else:
                    parity = "even-even(K=1)"
            else:
                parity = "mixed(K=2)"
            pred_d1 = n1 - ((j + 1) // 2)

            coeffs = [0] * N0
            coeffs[i] = 1
            coeffs[j] = 1
            f_vals = evaluate_at_L(coeffs, L0, P)

            f_e, f_o = even_odd_parts(f_vals, L0, P)

            min_d1 = n1
            min_d1_nz = n1
            d1_counter = Counter()
            for alpha in range(P):
                fold_a = [(f_e[k] + alpha * f_o[k]) % P for k in range(n1)]
                d_a = fast_d1(fold_a, L1_arr, info_sets_arr, D1, inv_D1, P, n1, k1)
                d1_counter[d_a] += 1
                if d_a < min_d1:
                    min_d1 = d_a
                if alpha != 0 and d_a < min_d1_nz:
                    min_d1_nz = d_a

            above_J = (2 * min_d1_nz) > W_J
            tie_d1 = sum((1 - d/n1) * c for d, c in d1_counter.items()) / P

            results.append({
                "i": i, "j": j, "parity": parity,
                "pred_d1": pred_d1, "min_d1_nz": min_d1_nz, "min_d1": min_d1,
                "above_J": above_J, "tie_d1": tie_d1, "d1_counter": dict(d1_counter),
            })

            tag = "above-J" if above_J else "below-J"
            print(f"  ({i:2d}, {j:2d})  {parity:>14}  {pred_d1:>6}  {min_d1_nz:>6}  {min_d1:>6}  {tag:>10}  {tie_d1:.4f}")

    print()
    print("=== Summary ===")
    above_J_results = [r for r in results if r["above_J"]]
    print(f"Total (i, j) pairs: {len(results)}")
    print(f"Above-J: {len(above_J_results)}")
    if above_J_results:
        worst = max(above_J_results, key=lambda r: r["tie_d1"])
        print(f"Worst above-J: ({worst['i']}, {worst['j']}) {worst['parity']}")
        print(f"  tie_d1 = {worst['tie_d1']:.4f}")
        print(f"  predicted d_1 >= {worst['pred_d1']}, empirical min nonzero = {worst['min_d1_nz']}")
        print(f"  d_1 distribution: {worst['d1_counter']}")

    print()
    violations = [r for r in results if r["min_d1_nz"] < r["pred_d1"]]
    if violations:
        print(f"!!! VIOLATIONS of polynomial-degree witness: {len(violations)}")
        for v in violations[:10]:
            print(f"   ({v['i']}, {v['j']}): pred {v['pred_d1']}, emp {v['min_d1_nz']}, parity {v['parity']}")
    else:
        print(f"=== Polynomial-degree witness CONFIRMED for all {len(results)} sparse 2-term cases ===")
        print("    d_1(alpha) >= n_1 - ceil(j/2) for ALL alpha != 0 across ALL (i, j) tested.")
        print()
        print("By parity class:")
        for p_class in ["odd-odd(K=1)", "even-even(K=1)", "mixed(K=2)"]:
            cls = [r for r in results if r["parity"] == p_class]
            cls_aboveJ = [r for r in cls if r["above_J"]]
            if cls:
                tight = sum(1 for r in cls if r["min_d1_nz"] == r["pred_d1"])
                print(f"  {p_class}: {len(cls)} pairs, {len(cls_aboveJ)} above-J, {tight} tight (emp = pred)")


if __name__ == "__main__":
    main()
