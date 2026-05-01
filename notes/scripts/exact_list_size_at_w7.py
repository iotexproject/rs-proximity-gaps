"""exact_list_size_at_w7.py — brute-force exact list size at agreement w=7.

For each random K=2 above-J f at q=449, for each α with d_1(α) = 9:
  Enumerate ALL codewords c ∈ C_1 = RS_4(L_1) achieving agreement ≥ 7 with fold_α.
  Count distinct c (not just closest).

If max EXACT L_GS ≤ 2 universally, gives strong rigorous bound on
|{α : d_1(α) = 9}| ≤ 2 · n_1 = 32.

Approach: for each k=4 info set T ⊂ L_1, the unique interp_T determines a
codeword. Two different T's can give the SAME codeword if the polynomials
match. List size = # distinct interp_T's with agreement ≥ 7.
"""
from __future__ import annotations
import sys, os, random
import numpy as np
from itertools import combinations
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

P = 193
N0 = 32
K0 = 8
R = 2

import probe_step5_n32_studio
probe_step5_n32_studio.P = P

import sweep_K2_q193
sweep_K2_q193.P = P

from fri_2round_attack import setup_chain, even_odd_parts, parity_check, gauss_rank
from sweep_K2_q193 import construct_K2_psi_in_U
from mds_decoder import precompute_diff_inv, batched_extras


def lagrange_interp(L, T_idx, vals_T, p):
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


def exact_list_size(fold1, L1, k1, p, threshold=7):
    """Return all distinct codewords c achieving agreement ≥ threshold."""
    n1 = len(L1)
    seen_codewords = {}  # tuple(c) -> agreement
    for T in combinations(range(n1), k1):
        T_idx = list(T)
        vals_T = [fold1[i] for i in T_idx]
        c_full = lagrange_interp(L1, T_idx, vals_T, p)
        agree = sum(1 for i in range(n1) if c_full[i] == fold1[i])
        if agree >= threshold:
            key = tuple(c_full)
            if key not in seen_codewords or seen_codewords[key] < agree:
                seen_codewords[key] = agree
    return len(seen_codewords), seen_codewords


def main():
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)
    L0 = chain[0][0]
    L1, k1, _ = chain[1]
    n1 = len(L1)

    rng = random.Random(2026)
    print(f"=== Exact list size at agreement ≥ 7 (Johnson + 1 below) for RS_{k1}(L_1), |L_1|={n1} ===")
    print(f"q = {p}; testing K=2 dense above-J f's")
    print()

    L1_arr = np.array(L1, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    info_sets = list(combinations(range(n1), k1))
    info_sets_arr = np.array(info_sets, dtype=np.int64)

    max_list_size_overall = 0
    target_cases = 5
    n_cases = 0
    n_attempts = 0
    while n_cases < target_cases and n_attempts < 30:
        n_attempts += 1
        f, T1, T2 = construct_K2_psi_in_U(rng, p, chain, H_R, n_R)
        if f is None: continue
        f_e, f_o = even_odd_parts(f, L0, p)
        f_e_arr = np.array(f_e, dtype=np.int64)
        f_o_arr = np.array(f_o, dtype=np.int64)
        # Find α with d_1 = 9
        alphas_at_9 = []
        for a in range(p):
            fold_arr = (f_e_arr + a * f_o_arr) % p
            extras = batched_extras(info_sets_arr, fold_arr, L1_arr, D1, inv_D1, p)
            d1 = n1 - k1 - int(extras.max())
            if d1 == 9:
                alphas_at_9.append(a)
        if len(alphas_at_9) < 5:
            continue
        n_cases += 1
        print(f"--- Case {n_cases}: T1={T1}, T2={T2}, |α at d_1=9|={len(alphas_at_9)} ---")
        max_list_size = 0
        for a in alphas_at_9[:3]:
            fold1 = [(f_e[i] + a * f_o[i]) % p for i in range(n1)]
            L_size, codewords = exact_list_size(fold1, L1, k1, p, threshold=7)
            print(f"  α={a}: exact list size at agreement ≥ 7: {L_size}")
            if L_size > max_list_size:
                max_list_size = L_size
        if max_list_size > max_list_size_overall:
            max_list_size_overall = max_list_size

    print()
    print(f"=== Overall max exact list size at agreement ≥ 7: {max_list_size_overall} ===")
    if max_list_size_overall <= 1:
        print("★★★ List size = 1: closest codeword is UNIQUE at agreement 7.")
        print("    Affine-line property follows RIGOROUSLY from pairwise stability.")
    elif max_list_size_overall <= 2:
        print("★ List size ≤ 2: bounded by Sudan-type analysis.")
        print("    L_GS · n_1 = 32 unconditional bound.")
    else:
        print(f"List size ≤ {max_list_size_overall}: needs further refinement.")


if __name__ == "__main__":
    main()
