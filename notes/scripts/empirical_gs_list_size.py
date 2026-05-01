"""empirical_gs_list_size.py — measure empirical GS list size at d_1 = 9 (Johnson + 1).

For each K=2 above-J case at multiple q:
1. Find all α with d_1(α) = 9.
2. For each α, find the closest codeword c_α (agreement 7).
3. Cluster the c_α's into "affine lines" — group together if (α_i, c_i), (α_j, c_j)
   determine a line that fits c_k for all members.
4. Number of clusters = empirical GS list size at this level.

Across 30+ random K=2 above-J cases, what's the max empirical L_GS?
The classical bound is √(n_1/k_1) = √4 = 2 for RS_4 length 16. Sudan bound at
Johnson + 1 is also small. Our hypothesis: L_GS ≤ 2 universally.

If confirmed, Theorem 0141.E sharpens to N ≤ 2 · n_1 = 32, q-independent.
"""
from __future__ import annotations
import sys, os, random
import numpy as np
from itertools import combinations
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

N0 = 32
K0 = 8
R = 2

import probe_step5_n32_studio
import sweep_K2_q193

from fri_2round_attack import setup_chain, even_odd_parts, parity_check, gauss_rank
from sweep_K2_q193 import construct_K2_psi_in_U
from mds_decoder import precompute_diff_inv, batched_extras


def find_alphas_d1_eq_9(f, chain, p):
    L0 = chain[0][0]
    L1, k1, _ = chain[1]
    n1 = len(L1)
    L1_arr = np.array(L1, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    info_sets = list(combinations(range(n1), k1))
    info_sets_arr = np.array(info_sets, dtype=np.int64)
    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)
    alphas = []
    for a1 in range(p):
        fold1_arr = (f_e_arr + a1 * f_o_arr) % p
        extras = batched_extras(info_sets_arr, fold1_arr, L1_arr, D1, inv_D1, p)
        d1 = n1 - k1 - int(extras.max())
        if d1 == 9:
            alphas.append(a1)
    return alphas, n1, k1, L1, f_e, f_o


def lagrange_interp_codeword(L, T_idx, vals_T, p):
    out = []
    for x_eval in L:
        v = 0
        for j_loc, j_T in enumerate(T_idx):
            num = 1; den = 1
            for k_loc, k_T in enumerate(T_idx):
                if k_loc == j_loc: continue
                num = (num * (x_eval - L[k_T])) % p
                den = (den * (L[j_T] - L[k_T])) % p
            term = (vals_T[j_loc] * num * pow(den, p - 2, p)) % p
            v = (v + term) % p
        out.append(v)
    return out


def find_closest_codeword(fold1, L1, k1, p):
    n1 = len(L1)
    best_agree = 0
    best_c = None
    for T in combinations(range(n1), k1):
        T_idx = list(T)
        vals_T = [fold1[i] for i in T_idx]
        c_full = lagrange_interp_codeword(L1, T_idx, vals_T, p)
        agree = sum(1 for i in range(n1) if c_full[i] == fold1[i])
        if agree > best_agree:
            best_agree = agree
            best_c = c_full
    return best_c, best_agree


def is_codeword(c_full, L1, k1, p):
    T = list(range(k1))
    vals_T = [c_full[i] for i in T]
    c_check = lagrange_interp_codeword(L1, T, vals_T, p)
    return all(c_check[i] == c_full[i] for i in range(len(L1)))


def cluster_into_lines(alphas, codewords, L1, k1, p):
    """Cluster (α, c_α) pairs into affine lines.
    Two pairs (α_1, c_1), (α_2, c_2) define a line c(α) = c_1 + (α-α_1)·(c_2-c_1)/(α_2-α_1).
    A third pair (α_3, c_3) is on this line iff c_3 = c_1 + (α_3-α_1)·(c_2-c_1)/(α_2-α_1).
    """
    n1 = len(L1)
    pairs = list(zip(alphas, codewords))
    if len(pairs) < 2:
        return [pairs]
    clusters = []
    used = [False] * len(pairs)
    for i in range(len(pairs)):
        if used[i]: continue
        seed_idx = [i]
        # Find another pair to define a line
        for j in range(i+1, len(pairs)):
            if used[j]: continue
            a1, c1 = pairs[i]
            a2, c2 = pairs[j]
            inv_da = pow((a2 - a1) % p, p - 2, p)
            c_o = [((c2[k] - c1[k]) * inv_da) % p for k in range(n1)]
            c_e = [(c1[k] - a1 * c_o[k]) % p for k in range(n1)]
            # Check if c_e, c_o ∈ C_1
            if not (is_codeword(c_e, L1, k1, p) and is_codeword(c_o, L1, k1, p)):
                continue
            # Check which other pairs lie on this line
            line_pairs = [i, j]
            for k in range(len(pairs)):
                if k in line_pairs or used[k]: continue
                ak, ck = pairs[k]
                c_pred = [(c_e[m] + ak * c_o[m]) % p for m in range(n1)]
                if all(c_pred[m] == ck[m] for m in range(n1)):
                    line_pairs.append(k)
            clusters.append([pairs[idx] for idx in line_pairs])
            for k in line_pairs:
                used[k] = True
            break
        if not used[i]:
            # i wasn't paired — singleton cluster
            clusters.append([pairs[i]])
            used[i] = True
    return clusters


def main():
    PRIMES = [193, 449]
    target_per_q = 15
    print(f"=== Empirical GS list size at d_1 = 9 across K=2 above-J cases ===")
    print()
    max_lgs_overall = 0
    for p in PRIMES:
        chain = setup_chain(p, N0, K0, R=R)
        L_R, k_R, _ = chain[R]
        n_R = len(L_R)
        H_R = parity_check(L_R, n_R, k_R, p)
        L1, k1, _ = chain[1]
        rng = random.Random(2026 + p)

        print(f"--- q = {p} ---")
        n_cases = 0
        n_attempts = 0
        max_lgs = 0
        lgs_distribution = Counter()
        N_distribution = []
        while n_cases < target_per_q and n_attempts < 60:
            n_attempts += 1
            f, T1, T2 = construct_K2_psi_in_U(rng, p, chain, H_R, n_R)
            if f is None: continue
            alphas, _, _, _, f_e, f_o = find_alphas_d1_eq_9(f, chain, p)
            if len(alphas) < 3:
                continue
            n_cases += 1
            n1 = len(L1)
            codewords = []
            for a in alphas:
                fold1 = [(f_e[i] + a * f_o[i]) % p for i in range(n1)]
                c, agree = find_closest_codeword(fold1, L1, k1, p)
                codewords.append(c)
            clusters = cluster_into_lines(alphas, codewords, L1, k1, p)
            lgs = len(clusters)
            lgs_distribution[lgs] += 1
            cluster_sizes = sorted([len(cl) for cl in clusters], reverse=True)
            N_distribution.append(len(alphas))
            print(f"  attempt {n_attempts}: N={len(alphas)}, L_GS={lgs}, cluster sizes={cluster_sizes}")
            if lgs > max_lgs: max_lgs = lgs
            if lgs > max_lgs_overall: max_lgs_overall = lgs
        print(f"  q={p}: tested={n_cases}, max L_GS = {max_lgs}, distribution = {dict(lgs_distribution)}")
        print()

    print(f"=== Final Summary ===")
    print(f"Max empirical L_GS across all tests: {max_lgs_overall}")
    if max_lgs_overall <= 2:
        print(f"★ Empirical L_GS ≤ 2, so refined bound: N ≤ 2 · n_1 = 32")
    elif max_lgs_overall <= 4:
        print(f"Empirical L_GS ≤ 4, classical √(n/k) bound holds.")
    else:
        print(f"L_GS exceeds √(n/k) — needs investigation.")


if __name__ == "__main__":
    main()
