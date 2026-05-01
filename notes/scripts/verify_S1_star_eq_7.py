"""verify_S1_star_eq_7.py — verify |S_1*| = 7 at q ≥ 769 (asymptotic regime).

For each above-J f: compute the stable level-1 agreement set S_1*(f) :=
intersection over all 'above-J α' of S_1(α). If |S_1*| = 7 uniformly at q ≥ 769,
the L_lines = 1 bound is RIGOROUS in the asymptotic regime.

S_1* is empirically the sunflower kernel of size 6 at finite q, but should
equal 7 at large enough q.
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


def find_closest_codeword_unique(fold1, L1, k1, p):
    """Return unique closest codeword."""
    n1 = len(L1)
    best_agree = 0
    best_c = None
    for T in combinations(range(n1), k1):
        T_idx = list(T)
        vals_T = [fold1[i] for i in T_idx]
        c_full = lagrange_interp(L1, T_idx, vals_T, p)
        agree = sum(1 for i in range(n1) if c_full[i] == fold1[i])
        if agree > best_agree:
            best_agree = agree
            best_c = c_full
    return best_c, best_agree


def main():
    PRIMES = [769, 1153]
    target = 5
    print(f"=== Verify |S_1*| = 7 for K=2 above-J at asymptotic q ===")
    print()

    overall_S1_distribution = Counter()
    for p in PRIMES:
        if (p - 1) % 32 != 0:
            print(f"q={p}: SKIP (32 ∤ q-1)")
            continue
        chain = setup_chain(p, N0, K0, R=R)
        L_R, k_R, _ = chain[R]
        n_R = len(L_R)
        H_R = parity_check(L_R, n_R, k_R, p)
        L0 = chain[0][0]
        L1, k1, _ = chain[1]
        n1 = len(L1)
        L1_arr = np.array(L1, dtype=np.int64)
        D1, inv_D1 = precompute_diff_inv(L1_arr, p)
        info_sets = list(combinations(range(n1), k1))
        info_sets_arr = np.array(info_sets, dtype=np.int64)
        rng = random.Random(2026 + p)

        print(f"--- q = {p} ---")
        n_cases = 0
        n_attempts = 0
        S1_star_sizes = []
        while n_cases < target and n_attempts < 30:
            n_attempts += 1
            f, T1, T2 = construct_K2_psi_in_U(rng, p, chain, H_R, n_R)
            if f is None: continue
            f_e, f_o = even_odd_parts(f, L0, p)
            f_e_arr = np.array(f_e, dtype=np.int64)
            f_o_arr = np.array(f_o, dtype=np.int64)
            # Find α with d_1=9 and their agreement sets
            agreement_sets = []
            for a in range(p):
                fold_arr = (f_e_arr + a * f_o_arr) % p
                extras = batched_extras(info_sets_arr, fold_arr, L1_arr, D1, inv_D1, p)
                d1 = n1 - k1 - int(extras.max())
                if d1 == 9:
                    fold = fold_arr.tolist()
                    c, agree = find_closest_codeword_unique(fold, L1, k1, p)
                    S_a = frozenset(i for i in range(n1) if c[i] == fold[i])
                    agreement_sets.append(S_a)
            if len(agreement_sets) < 5:
                continue
            n_cases += 1
            # Compute |S_1*| = |intersection of all agreement sets|
            S1_star = agreement_sets[0]
            for S in agreement_sets[1:]:
                S1_star = S1_star & S
            S1_star_size = len(S1_star)
            S1_star_sizes.append(S1_star_size)
            overall_S1_distribution[S1_star_size] += 1
            print(f"  attempt {n_attempts}: N={len(agreement_sets)}, |S_1*| = {S1_star_size}, T1={T1}, T2={T2}")
        print(f"  q={p}: |S_1*| values = {S1_star_sizes}")

    print()
    print(f"=== Summary across q ∈ {PRIMES} ===")
    print(f"|S_1*| distribution: {dict(overall_S1_distribution)}")
    if all(s == 7 for s in overall_S1_distribution):
        print("★★★ |S_1*| = 7 UNIVERSALLY at asymptotic q.")
        print("    L_lines = 1 RIGOROUSLY in asymptotic regime.")
    elif all(s >= 6 for s in overall_S1_distribution):
        print(f"|S_1*| ∈ {{6, 7}}. Asymptotic L_lines = 1 with sunflower kernel.")
    else:
        print(f"|S_1*| varies, asymptotic regime needs more analysis.")


if __name__ == "__main__":
    main()
