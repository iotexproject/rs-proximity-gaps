"""structure_d1_eq_9.py — analyze STRUCTURE of the 10 α with d_1(α)=9.

For the dense K=2 worst case, identify the 10 α values, then check:
1. Do they form a coset of a subgroup of F_q^*?
2. Are they roots of a low-degree polynomial in α?
3. What are the corresponding agreement sets S_α ⊂ L_1?
4. Are the codewords c_α in some structured family?

If we find structure (e.g., roots of a degree-10 polynomial in α with coefficients
depending polynomially on f), that's a path to RIGOROUS bound on |{α : d_1(α) = 9}|.

The specific empirical match: |{α : d_1(α) = 9}| = 10 = C(k_1 + 1, 2) = C(5, 2).
Hypothesis: this count is bounded by a polynomial in (k_1, n_1), independent of q.
"""
from __future__ import annotations
import sys, os, random
import numpy as np
from itertools import combinations, product
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

P = 449  # use largest q where we already saw 10 d_1=9 tuples
N0 = 32
K0 = 8
R = 2

import probe_step5_n32_studio
probe_step5_n32_studio.P = P
probe_step5_n32_studio.N0 = N0
probe_step5_n32_studio.K0 = K0

import sweep_K2_q193
sweep_K2_q193.P = P
sweep_K2_q193.N0 = N0
sweep_K2_q193.K0 = K0

from fri_2round_attack import setup_chain, even_odd_parts, parity_check, gauss_rank
from sweep_K2_q193 import construct_K2_psi_in_U
from mds_decoder import precompute_diff_inv, batched_extras


def find_alphas_d1_eq_9(f, chain, p, target_d1=9):
    """Return the list of α ∈ F_q^* with d_1(α) = target_d1."""
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
        if d1 == target_d1:
            alphas.append(a1)
    return alphas, n1, k1, L1, f_e, f_o


def find_d1_eq_9_with_witness(f, chain, p, alpha_list):
    """For each α with d_1(α) = 9, find its agreement set S_α (size 7)."""
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
    out = []
    for a1 in alpha_list:
        fold1_arr = (f_e_arr + a1 * f_o_arr) % p
        extras = batched_extras(info_sets_arr, fold1_arr, L1_arr, D1, inv_D1, p)
        max_extras = int(extras.max())
        # Find info set achieving max
        best_idx = int(np.argmax(extras))
        best_T = info_sets[best_idx]
        # Reconstruct codeword: Lagrange interp on best_T values
        # The agreement set S_α is best_T ∪ {extra positions matching}.
        # Compute c via Lagrange on best_T
        T = list(best_T)
        # interpolate fold1 values at L1[T]
        c_at_L1 = lagrange_interp(L1, [int(fold1_arr[i]) for i in T], T, p)
        S_alpha = [i for i in range(n1) if c_at_L1[i] == int(fold1_arr[i])]
        out.append((a1, sorted(S_alpha), [c_at_L1[i] for i in range(n1)]))
    return out


def lagrange_interp(L, vals_T, T_idx, p):
    """Interpolate codeword from vals at L[T_idx]. Returns evaluations on full L."""
    out = []
    n = len(L)
    for x_eval in L:
        v = 0
        for j_local, j_T in enumerate(T_idx):
            num = 1
            den = 1
            for k_local, k_T in enumerate(T_idx):
                if k_local == j_local: continue
                num = (num * (x_eval - L[k_T])) % p
                den = (den * (L[j_T] - L[k_T])) % p
            term = (vals_T[j_local] * num * pow(den, p - 2, p)) % p
            v = (v + term) % p
        out.append(v)
    return out


def main():
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)
    L1 = chain[1][0]
    n1 = len(L1)

    rng = random.Random(2026)
    print(f"=== Find dense K=2 with |{{α : d_1=9}}| = 10 at q={p} ===")
    for attempt in range(20):
        f, T1, T2 = construct_K2_psi_in_U(rng, p, chain, H_R, n_R)
        if f is None: continue
        alphas, _, _, _, _, _ = find_alphas_d1_eq_9(f, chain, p, target_d1=9)
        if len(alphas) >= 8:  # close to 10
            print(f"  attempt {attempt+1}: |{{α : d_1=9}}| = {len(alphas)}, T1={T1}, T2={T2}")
            print(f"  α values: {alphas}")
            # Multiplicative structure check:
            # 1. Is the set closed under multiplication by some element?
            # 2. What's the product, sum, etc.?
            S = sorted(alphas)
            pairwise_ratios = sorted(set((b * pow(a, p-2, p)) % p for a in S for b in S if a != 0 and a != b))
            sums = sorted(set((a + b) % p for a in S for b in S))
            print(f"  Number of distinct pairwise ratios: {len(pairwise_ratios)}")
            print(f"  Number of distinct pairwise sums: {len(sums)}")

            # Polynomial passing through these alphas:
            # P(α) = ∏ (α - α_i) is a degree-10 polynomial in F_q[α]
            # If our hypothesis is right, the coefficients of P should be polynomial
            # functions of f's Fourier coefficients (independent of q).
            poly = [1]
            for a in S:
                # multiply poly by (X - a)
                new_poly = [0] * (len(poly) + 1)
                for k, c in enumerate(poly):
                    new_poly[k] = (new_poly[k] + (-a * c) % p) % p
                    new_poly[k + 1] = (new_poly[k + 1] + c) % p
                poly = new_poly
            print(f"  Vanishing polynomial coefficients: {poly}")
            # Check structure: are these alphas in a multiplicative coset?
            # Compute order of group generated by ratios mod p
            if len(S) >= 2:
                ratio = (S[1] * pow(S[0], p-2, p)) % p
                generated = {1}
                cur = ratio
                for _ in range(p):
                    if cur in generated: break
                    generated.add(cur)
                    cur = (cur * ratio) % p
                print(f"  S[0]/S[1] generates group of order {len(generated)}")

            # Witnesses:
            wits = find_d1_eq_9_with_witness(f, chain, p, alphas)
            print(f"  Agreement sets S_α (size 7) for first 5 α's:")
            for a, S_a, _ in wits[:5]:
                print(f"    α={a}: S_α = {S_a}")
            break
    else:
        print(f"  No K=2 case with ≥ 8 d_1=9 tuples found in 20 attempts.")


if __name__ == "__main__":
    main()
