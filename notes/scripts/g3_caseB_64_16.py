"""g3_caseB_64_16.py — verify case (b) at (n_0, k_0) = (64, 16).

Predicted case-(b) DFT support: L_0 positions ⊂ {32..47}.
Predicted: count_α = q for all such f.

Tests:
  Test 1: pos in {32..47} → expect count=q.
  Test 2: pos NOT all in {32..47} → expect count<<q.
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


def main():
    p = 1153  # 64 | 1152 ✓
    n0, k0 = 64, 16

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1 = chain[1][0]
    L1_arr = np.array(L1, dtype=np.int64)
    n1, k1 = len(L1), k0 // 2  # 32, 8
    print(f"n_0={n0}, k_0={k0}, n_1={n1}, k_1={k1}")
    s = int(np.sqrt(k1 * n1))
    print(f"s = sqrt(k_1·n_1) = {s}, threshold dist ≤ {n1 - s} = {n1-s}")

    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    # C(32,8) = 10.5M too big. We TARGET info sets in T = odd L_1 indices
    # (where structural argument predicts count=q).
    odd_indices = list(range(1, n1, 2))  # T = odd L_1 indices, |T|=16
    info_in_T = list(combinations(odd_indices, k1))  # C(16,8) = 12870 info sets in T
    info_sets_arr_n1 = np.array(info_in_T, dtype=np.int64)
    print(f"  Targeted info sets ⊂ T (= odd L_1 indices): {len(info_in_T)}")

    threshold = n1 - s

    rng = random.Random(2026)

    test_supports = [
        ('case (b) coeffs=(1,1,1)', [(35, 36, 39)]),  # known structural case
        ('case (b)', [(35, 36, 39), (32, 35, 39), (32, 35, 47)]),
        ('case (a)', [(20, 35, 50)]),
    ]
    use_fixed_coeffs = True  # use (1,1,1) for first set

    print(f"\n{'support':<60} {'count':<6}")
    print("-" * 75)
    for label, pos_list in test_supports:
        print(f"\n=== {label} ===")
        for positions in pos_list:
            in_caseB = all(32 <= ps <= 47 for ps in positions)
            n_trials = 1 if 'coeffs=' in label else 2
            for trial in range(n_trials):
                if 'coeffs=' in label:
                    coeffs = (1,) * len(positions)
                else:
                    coeffs = tuple(rng.randint(1, p-1) for _ in positions)
                fhat = [0] * n0
                for ps, c in zip(positions, coeffs):
                    fhat[ps] = c
                f = evaluate_dft(fhat, L0, p)
                f_e, f_o = even_odd_parts(f, L0, p)
                f_e_arr = np.array(f_e, dtype=np.int64)
                f_o_arr = np.array(f_o, dtype=np.int64)
                cnt = 0
                d_alpha0 = None
                for a in range(p):
                    fold = (f_e_arr + a * f_o_arr) % p
                    extras = batched_extras(info_sets_arr_n1, fold, L1_arr, D1, inv_D1, p)
                    d1 = n1 - k1 - int(extras.max())
                    if a == 0:
                        d_alpha0 = d1
                    if d1 <= threshold:
                        cnt += 1
                pred = 'count=q (case b)' if in_caseB else 'count<<q'
                print(f"  pos={str(positions)[:50]:<50} count={cnt} (d at α=0: {d_alpha0}) (pred={pred})")


if __name__ == "__main__":
    main()
