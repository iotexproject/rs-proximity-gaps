"""g3_universal_caseB.py — verify case (b) is UNIVERSAL for DFT support ⊂ {16..23}.

Theory: at (n_0, k_0) = (32, 8), DFT positions ⊂ {16..23} → count=q always
(if strict above-J).

Proof: on T = ω_1·μ_8 ⊂ L_1 = μ_16, y^j|_T = (-1)^{⌊j/8⌋}·y^{j mod 8}.
For j on L_1 in {0..3, 8..11}, j mod 8 ∈ {0..3} → degree ≤ 3 → in RS_4|_T.
L_0 positions giving L_1 ∈ {8..11}: L_0 ∈ {16..23}.

Tests:
  (1) Random coeffs at pos=(19,20,23) → expect count=q.
  (2) Random coeffs at pos=(16,17,18,19,20,21,22,23) full → expect count=q.
  (3) Random coeffs at pos=(19,20,30) → 30 NOT in {16..23} → expect count<<q.
  (4) Different DFT subsets within {16..23}.
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


def dist_to_rs(f_arr, L_arr, n, k, D, inv_D, p):
    info_sets = list(combinations(range(n), k))
    info_sets_arr = np.array(info_sets, dtype=np.int64)
    extras = batched_extras(info_sets_arr, f_arr, L_arr, D, inv_D, p)
    return n - k - int(extras.max())


def count_bad(positions, coeffs, p, n0, k0, L0, L1_arr, D1, inv_D1, n1, k1):
    fhat = [0] * n0
    for ps, c in zip(positions, coeffs):
        fhat[ps] = c
    f = evaluate_dft(fhat, L0, p)
    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)

    threshold = 8
    info_sets = list(combinations(range(n1), k1))
    info_sets_arr = np.array(info_sets, dtype=np.int64)
    bad = []
    dist_hist = Counter()
    for a in range(p):
        fold = (f_e_arr + a * f_o_arr) % p
        extras = batched_extras(info_sets_arr, fold, L1_arr, D1, inv_D1, p)
        d1 = n1 - k1 - int(extras.max())
        dist_hist[d1] += 1
        if d1 <= threshold:
            bad.append(a)
    return len(bad), dist_hist


def main():
    p = 1153
    n0, k0 = 32, 8

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1 = chain[1][0]
    L1_arr = np.array(L1, dtype=np.int64)
    n1, k1 = len(L1), k0 // 2
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)

    rng = random.Random(42)
    test_cases = [
        ('Test 1: pos in {16..23}', [(19, 20, 23), (17, 19, 22), (16, 19, 23), (16, 17, 18, 19, 20, 21, 22, 23)]),
        ('Test 2: pos NOT all in {16..23}', [(19, 20, 30), (8, 19, 23), (18, 19, 30), (15, 16, 23), (10, 19, 22), (16, 19, 24)]),
    ]

    for label, pos_list in test_cases:
        print(f"\n=== {label} ===")
        for positions in pos_list:
            in_caseB = all(16 <= ps <= 23 for ps in positions)
            for trial in range(2):
                coeffs = tuple(rng.randint(1, p-1) for _ in positions)
                # Check above-J
                fhat = [0] * n0
                for ps, c in zip(positions, coeffs):
                    fhat[ps] = c
                f = evaluate_dft(fhat, L0, p)
                f_arr = np.array(f, dtype=np.int64)
                d_f = dist_to_rs(f_arr, L0_arr, n0, k0, D0, inv_D0, p)
                w_J = 16
                above_J = d_f > w_J
                cnt, dh = count_bad(positions, coeffs, p, n0, k0, L0, L1_arr, D1, inv_D1, n1, k1)
                pred = 'count=q (case b)' if in_caseB else 'count<<q'
                print(f"  pos={positions}, coeffs={coeffs[:3]}{'...' if len(coeffs)>3 else ''}, dist_f={d_f}, above-J={above_J}, count={cnt}, pred={pred}")


if __name__ == "__main__":
    main()
