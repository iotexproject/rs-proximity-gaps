"""g3_count_q_witnesses.py — find ALL 3-pos sparse f supports at q=1153 (32,8)
that give count_alpha = q (= 1153) with random coefs.  These are at-Johnson
witnesses (not strict above-J).
"""
import sys, os, math, random
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
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
    sample = []
    for alpha in range(p):
        fold = (f_e_arr + alpha * f_o_arr) % p
        extras = batched_extras(all_T, fold, L1_arr, D1, inv_D1, p)
        d1 = n1 - k1 - int(extras.max())
        if d1 <= threshold:
            cnt += 1
            if cnt <= 5:
                sample.append((alpha, d1))
    return cnt, sample


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

    # check known count=q candidates
    candidates = [
        (19, 20, 23),
        (17, 18, 19),
    ]
    print(f"=== Verify count=q candidates ===")
    rng = random.Random(2026)
    for sup in candidates:
        for trial in range(3):
            coeffs = tuple(rng.randrange(1, p) for _ in range(3))
            cnt, sample = count_bad_alpha(sup, coeffs, p, n0, k0, threshold,
                                            L0, L1_arr, all_T, D1, inv_D1)
            print(f"  sup={sup} trial {trial} coefs={coeffs}: count={cnt}, "
                  f"sample={sample}")
        print()

    # full sweep at the (T, F, T, T) and (T, F, T, F) classes (216 + 432 = 648 supports)
    # to find all count=q witnesses
    print(f"=== Sweep classes (T, F, *, *) for count=q witnesses ===")
    # build candidates
    target_sups = []
    for sup in combinations(range(8, 32), 3):
        fe_pos = []
        fo_pos = []
        for j in sup:
            if j % 2 == 0:
                fe_pos.append(j // 2)
            else:
                fo_pos.append((j - 1) // 2)
        if not fe_pos or not fo_pos:
            continue
        fe_m4 = len(set(p_ % 4 for p_ in fe_pos)) == 1
        fo_m4 = len(set(p_ % 4 for p_ in fo_pos)) == 1
        if fe_m4 and not fo_m4:
            target_sups.append(sup)
    print(f"  {len(target_sups)} candidates in (T, F, *, *)")

    # quick scan: random coefs, check if count=q
    qcount_witnesses = []
    rng = random.Random(31415)
    for sup in target_sups:
        coeffs = tuple(rng.randrange(1, p) for _ in range(3))
        cnt, _ = count_bad_alpha(sup, coeffs, p, n0, k0, threshold,
                                  L0, L1_arr, all_T, D1, inv_D1)
        if cnt > 100:  # likely count=q
            # verify with second trial
            coeffs2 = tuple(rng.randrange(1, p) for _ in range(3))
            cnt2, _ = count_bad_alpha(sup, coeffs2, p, n0, k0, threshold,
                                       L0, L1_arr, all_T, D1, inv_D1)
            if cnt2 > 100:
                qcount_witnesses.append((sup, cnt, cnt2))
                print(f"    [witness] sup={sup}: count1={cnt}, count2={cnt2}")

    print(f"\n  Total count>100 witnesses found: {len(qcount_witnesses)}")
    if qcount_witnesses:
        print(f"  Patterns: {[(s, c1, c2) for s, c1, c2 in qcount_witnesses[:20]]}")


if __name__ == "__main__":
    main()
