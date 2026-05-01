"""g3_caseB_q97.py — direct check: case (b) at q=97.

For DFT support ⊂ {16..23}, structural argument predicts count=q regardless of
coefficients. But empirical sweep at q=97 found 0 invariant case-(b) supports.

Hypothesis: at q=97, case-(b) f's are NOT strict above-J (filtered out by sweep).

Verify: compute dist(f, RS_8) and count(f) for several case-(b) examples.
"""
import sys, os, random
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from collections import Counter

from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft(fhat, L, p):
    n = len(L)
    f = [0] * n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j] != 0:
                v = (v + fhat[j] * pow(x, j, p)) % p
        f[i] = v
    return f


def dist_to_rs_full(f_arr, L_arr, n, k, D, inv_D, p, batch_size=200000):
    """Exhaustive distance computation in batches."""
    all_T = list(combinations(range(n), k))
    max_extras = 0
    for start in range(0, len(all_T), batch_size):
        batch = all_T[start:start + batch_size]
        T_arr = np.array(batch, dtype=np.int64)
        extras = batched_extras(T_arr, f_arr, L_arr, D, inv_D, p)
        m = int(extras.max())
        if m > max_extras:
            max_extras = m
    return n - k - max_extras


def main():
    p = 97
    n0, k0 = 32, 8

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1 = chain[1][0]
    L1_arr = np.array(L1, dtype=np.int64)
    n1, k1 = len(L1), k0 // 2
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    info_sets_n1 = list(combinations(range(n1), k1))
    info_sets_arr_n1 = np.array(info_sets_n1, dtype=np.int64)

    print(f"=== Case (b) supports at q={p}: dist + count ===\n")

    rng = random.Random(2026)
    test_supports = [(19, 20, 23), (16, 17, 18), (16, 17, 23), (16, 19, 22), (17, 18, 19),
                     (16, 17, 18, 19, 20, 21, 22, 23)]

    print(f"{'support':<35} {'coeffs':<35} {'dist_f':<8} {'above-J':<8} {'count':<6}")
    print("-" * 95)
    for pos in test_supports:
        for trial in range(3):
            coeffs = tuple(rng.randint(1, p-1) for _ in pos)
            fhat = [0] * n0
            for ps, c in zip(pos, coeffs):
                fhat[ps] = c
            f = evaluate_dft(fhat, L0, p)
            f_arr = np.array(f, dtype=np.int64)
            d_f = dist_to_rs_full(f_arr, L0_arr, n0, k0, D0, inv_D0, p)
            above_J = d_f > 16
            f_e, f_o = even_odd_parts(f, L0, p)
            f_e_arr = np.array(f_e, dtype=np.int64)
            f_o_arr = np.array(f_o, dtype=np.int64)
            cnt = 0
            for a in range(p):
                fold = (f_e_arr + a * f_o_arr) % p
                extras = batched_extras(info_sets_arr_n1, fold, L1_arr, D1, inv_D1, p)
                d1 = n1 - k1 - int(extras.max())
                if d1 <= 8:
                    cnt += 1
            cf = str(coeffs)[:33]
            print(f"{str(pos):<35} {cf:<35} {d_f:<8} {str(above_J):<8} {cnt:<6}")


if __name__ == "__main__":
    main()
