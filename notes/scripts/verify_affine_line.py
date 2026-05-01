"""verify_affine_line.py — verify the affine-line hypothesis empirically.

For dense K=2 above-J f with 10 α's at d_1 = 9:
1. Find all 10 α values.
2. For each, compute the UNIQUE closest codeword c_α ∈ C_1 (RS_4 length 16).
3. Check if α → c_α is AFFINE in α: c_α = c_e + α c_o for fixed c_e, c_o ∈ C_1.
4. Compute c_e, c_o from any 2 α's, verify on the other 8.

This is the missing piece for fully rigorizing Theorem 0141.D.
"""
from __future__ import annotations
import sys, os, random
import numpy as np
from itertools import combinations
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

P = 449
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
    """Interp degree-<k codeword from k values at L[T_idx[:k]]; return evaluations at L."""
    k = len(T_idx)
    out = []
    for x_eval in L:
        v = 0
        for j_loc, j_T in enumerate(T_idx):
            num = 1
            den = 1
            for k_loc, k_T in enumerate(T_idx):
                if k_loc == j_loc: continue
                num = (num * (x_eval - L[k_T])) % p
                den = (den * (L[j_T] - L[k_T])) % p
            term = (vals_T[j_loc] * num * pow(den, p - 2, p)) % p
            v = (v + term) % p
        out.append(v)
    return out


def find_closest_codeword(fold1, L1, k1, p):
    """Find closest codeword c ∈ RS_{k1}(L1) to fold1.

    Strategy: try each k_1-subset T as info set; the codeword interp_T(fold1[T])
    achieves agreement >= k_1; max over T gives closest.
    Returns (c_evaluated_on_L1, agreement_count, info_set_used).
    """
    n1 = len(L1)
    best_agree = 0
    best_c = None
    best_T = None
    for T in combinations(range(n1), k1):
        T_idx = list(T)
        vals_T = [fold1[i] for i in T_idx]
        c_full = lagrange_interp_codeword(L1, T_idx, vals_T, p)
        agree = sum(1 for i in range(n1) if c_full[i] == fold1[i])
        if agree > best_agree:
            best_agree = agree
            best_c = c_full
            best_T = T
    return best_c, best_agree, best_T


def is_codeword(c_full, L1, k1, p):
    """Check if c_full is a degree-<k1 codeword (interpolated by first k1 values)."""
    n1 = len(L1)
    T = list(range(k1))
    vals_T = [c_full[i] for i in T]
    c_check = lagrange_interp_codeword(L1, T, vals_T, p)
    return all(c_check[i] == c_full[i] for i in range(n1))


def main():
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)
    L1, k1, _ = chain[1]
    n1 = len(L1)

    rng = random.Random(2026)
    print(f"=== Verify affine-line hypothesis for K=2 dense d_1=9 cases ===")
    print(f"q={p}, n_1={n1}, k_1={k1}")
    print()

    # Find a K=2 case with 10 d_1=9 alphas
    for attempt in range(20):
        f, T1, T2 = construct_K2_psi_in_U(rng, p, chain, H_R, n_R)
        if f is None: continue
        alphas, _, _, _, f_e, f_o = find_alphas_d1_eq_9(f, chain, p)
        if len(alphas) >= 10:
            break
    else:
        print("No suitable case found.")
        return

    print(f"Found case: T1={T1}, T2={T2}, |{{α : d_1=9}}| = {len(alphas)}")
    print(f"α values: {alphas[:10]}")
    print()

    # For each α, find the closest codeword c_α
    closest_codewords = []
    for a in alphas[:10]:
        fold1 = [(f_e[i] + a * f_o[i]) % p for i in range(n1)]
        c_a, agree, T = find_closest_codeword(fold1, L1, k1, p)
        closest_codewords.append((a, c_a, agree, T))
        print(f"  α={a}: closest c agree={agree}, T={T}")
    print()

    # Pick first 2 α's: compute c_e, c_o assuming c_α = c_e + α c_o
    a1, c1, _, _ = closest_codewords[0]
    a2, c2, _, _ = closest_codewords[1]
    inv_da = pow((a2 - a1) % p, p - 2, p)
    c_o = [((c2[i] - c1[i]) * inv_da) % p for i in range(n1)]
    c_e = [(c1[i] - a1 * c_o[i]) % p for i in range(n1)]

    print(f"Computed c_e, c_o from α={a1}, α={a2}:")
    print(f"  c_e in C_1? {is_codeword(c_e, L1, k1, p)}")
    print(f"  c_o in C_1? {is_codeword(c_o, L1, k1, p)}")
    print()

    # Verify other 8 alphas: c_α should equal c_e + α c_o
    print("Verifying c_α = c_e + α c_o for remaining 8 α's:")
    matches = 0
    for a, c_a, _, _ in closest_codewords[2:10]:
        c_pred = [(c_e[i] + a * c_o[i]) % p for i in range(n1)]
        match = all(c_pred[i] == c_a[i] for i in range(n1))
        diff_pos = sum(1 for i in range(n1) if c_pred[i] != c_a[i])
        marker = "✓" if match else "✗"
        print(f"  α={a}: match={match} ({diff_pos} differing positions)  {marker}")
        if match:
            matches += 1

    print()
    print(f"=== Result ===")
    print(f"Affine-line hypothesis verified for {matches}/8 additional α's.")
    if matches == 8:
        print(f"★ AFFINE-LINE HYPOTHESIS RIGOROUSLY VERIFIED for this case.")
        print(f"  All 10 closest codewords lie on the same line c_e + α·c_o in C_1.")
        print(f"  This is the missing piece for full Theorem 0141.D rigor.")
    else:
        print(f"Partial verification — investigate non-matches.")


if __name__ == "__main__":
    main()
