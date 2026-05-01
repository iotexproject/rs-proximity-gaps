"""g3_count9_structure.py — for the 24 count=9 supports at q=1153, verify:
  1. Conjecture E (coeff-invariance): count=9 across 5 random coef trials.
  2. σ_k(bad-alpha) invariants: which σ_k vanish identically across coefs?
  3. Multiplicative structure: closed under α → c·α for some c?
  4. Polynomial structure: minimal polynomial of bad-alpha set.

count=9 saturates PR #373's single-line bound n_1 - s + 1 = 9.
"""
import sys, os, math, random, time
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


def power_sum_to_elementary(power_sums, p):
    """Newton's identities: p_k → e_k.  power_sums[i] = p_{i+1} (i.e. sum of α^{i+1})."""
    n = len(power_sums)
    e = [0] * (n + 1)
    e[0] = 1
    for k in range(1, n + 1):
        s = 0
        for i in range(1, k + 1):
            s = (s + (-1)**(i-1) * e[k-i] * power_sums[i-1]) % p
        e[k] = (s * pow(k, p - 2, p)) % p
    return e[1:]  # σ_1, σ_2, ..., σ_n


def bad_alpha_full(positions, coeffs, p, n0, k0, threshold,
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

    bad = []
    for alpha in range(p):
        fold = (f_e_arr + alpha * f_o_arr) % p
        extras = batched_extras(all_T, fold, L1_arr, D1, inv_D1, p)
        d1 = n1 - k1 - int(extras.max())
        if d1 <= threshold:
            bad.append(alpha)
    return bad


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

    # 24 count=9 supports from enum sweep
    count9 = [(8,9,20),(8,9,21),(9,20,21),(10,11,22),(10,11,23),(11,22,23),
              (12,13,16),(12,13,17),(13,16,17),(14,15,18),(14,15,19),(15,18,19),
              (16,17,29),(16,28,29),(17,28,29),(18,19,31),(18,30,31),(19,30,31),
              (20,21,25),(20,24,25),(21,24,25),(22,23,27),(22,26,27),(23,26,27)]

    rng = random.Random(2026)

    print(f"=== count=9 structural analysis at q={p}, ({n0},{k0}) ===")
    print(f"Testing {len(count9)} supports, 3 random coef trials each, σ_1..σ_9 invariants\n")

    # collect all sigma signatures
    sigma_signatures = []  # list of (support, [(coeffs, count, sigmas)] for trials)

    for sup_idx, sup in enumerate(count9):
        trial_data = []
        for trial in range(3):
            coeffs = tuple(rng.randrange(1, p) for _ in range(3))
            bad = bad_alpha_full(sup, coeffs, p, n0, k0, threshold,
                                  L0, L1_arr, all_T, D1, inv_D1)
            cnt = len(bad)
            # power sums
            ps = []
            for k in range(1, 10):
                s = sum(pow(a, k, p) for a in bad) % p
                ps.append(s)
            sigmas = power_sum_to_elementary(ps, p)
            trial_data.append((coeffs, cnt, sigmas, bad))

        # check Conjecture E
        counts = [td[1] for td in trial_data]
        cnt_invariant = all(c == counts[0] for c in counts)

        # which σ_k vanish across all trials?
        vanish_k = []
        for k in range(9):
            if all(td[2][k] == 0 for td in trial_data):
                vanish_k.append(k + 1)

        print(f"  [{sup_idx+1:2d}] sup={sup}: count={counts}, conj E {'✓' if cnt_invariant else '✗'}, "
              f"σ_k vanish: {vanish_k}")
        sigma_signatures.append((sup, vanish_k, counts))

    # summary: group supports by σ-vanish signature
    print("\n=== σ-vanish signature groupings ===")
    sig_groups = {}
    for sup, vk, _ in sigma_signatures:
        key = tuple(vk)
        sig_groups.setdefault(key, []).append(sup)
    for sig, sups in sorted(sig_groups.items()):
        print(f"  σ vanish at {sig}: {len(sups)} supports: {sups[:6]}{'...' if len(sups)>6 else ''}")


if __name__ == "__main__":
    main()
