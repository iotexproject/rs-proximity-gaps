"""g3_coeff_dependence.py — test count_alpha as function of coefficients.

Hypothesis: for biquadratic-type supports (a, a+m, a+16):
  - generic coefs c_a, c_{a+m}, c_{a+16} → count = 4 (biquadratic)
  - degenerate coefs (e.g., c_a = c_{a+16}) → count = q (case-b-like collapse)

This contradicts Conjecture E in its strict form. Conjecture E refined:
  count = locally constant on coefs except on thin algebraic subvariety.
"""
import sys, os, math, random
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from collections import Counter
from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft_local(fhat, L, p):
    n = len(L)
    f = [0] * n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j] != 0:
                v = (v + fhat[j] * pow(x, j, p)) % p
        f[i] = v
    return f


def count_bad_alpha(positions, coeffs, p, n0, k0, threshold,
                    L0, L1_arr, all_T, D1, inv_D1):
    fhat = [0] * n0
    for ps, c in zip(positions, coeffs):
        fhat[ps] = c
    f = evaluate_dft_local(fhat, L0, p)
    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)
    n1 = len(L1_arr)
    k1 = k0 // 2

    cnt = 0
    bad = []
    for alpha in range(p):
        fold = (f_e_arr + alpha * f_o_arr) % p
        extras = batched_extras(all_T, fold, L1_arr, D1, inv_D1, p)
        d1 = n1 - k1 - int(extras.max())
        if d1 <= threshold:
            cnt += 1
            if cnt <= 16:
                bad.append(alpha)
    return cnt, bad


def main():
    p = 1153
    n0, k0 = 32, 8
    n1, k1 = 16, 4
    threshold = n1 - int(math.isqrt(k1 * n1))  # = 8

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L1 = chain[1][0]
    L1_arr = np.array(L1, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    all_T = np.array(list(combinations(range(n1), k1)), dtype=np.int64)

    # Test biquadratic-type supports with various coeff patterns
    bisup = [
        (8, 17, 24), (9, 16, 25), (10, 19, 26), (11, 18, 27),
        (12, 21, 28), (14, 23, 30), (15, 22, 31),
    ]

    print(f"=== Coefficient dependence at q={p}, ({n0},{k0}) ===\n")

    rng = random.Random(2026)
    for sup in bisup:
        a, b, c = sup
        print(f"--- support = ({a}, {b}, {c}) ---")

        # all-1 coefs (degenerate? c_a = c_{a+16})
        coeffs = (1, 1, 1)
        cnt, bad = count_bad_alpha(sup, coeffs, p, n0, k0, threshold,
                                    L0, L1_arr, all_T, D1, inv_D1)
        print(f"  coeffs=(1,1,1):       count = {cnt}, bad[:8] = {bad[:8]}")

        # c_a = c_{a+16} but c_b distinct (still degenerate?)
        coeffs = (1, 7, 1)
        cnt, bad = count_bad_alpha(sup, coeffs, p, n0, k0, threshold,
                                    L0, L1_arr, all_T, D1, inv_D1)
        print(f"  coeffs=(1,7,1):       count = {cnt}, bad[:8] = {bad[:8]}")

        # c_a ≠ c_{a+16}: break the y^8=-1 cancellation
        coeffs = (1, 1, 2)
        cnt, bad = count_bad_alpha(sup, coeffs, p, n0, k0, threshold,
                                    L0, L1_arr, all_T, D1, inv_D1)
        print(f"  coeffs=(1,1,2):       count = {cnt}, bad[:8] = {bad[:8]}")

        # generic random coefs (5 trials)
        for trial in range(5):
            coeffs = tuple(rng.randrange(1, p) for _ in range(3))
            cnt, bad = count_bad_alpha(sup, coeffs, p, n0, k0, threshold,
                                        L0, L1_arr, all_T, D1, inv_D1)
            print(f"  trial {trial}, coefs={coeffs}: count = {cnt}, bad[:8] = {bad[:8]}")
        print()


if __name__ == "__main__":
    main()
