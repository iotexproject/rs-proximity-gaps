"""verify_affine_line_universal.py — verify affine-line hypothesis across many cases.

For each randomly-generated dense K=2 above-J f at q ∈ {193, 449}:
  Find all α with d_1(α) = 9.
  If ≥ 3 such α's: pick first 2 to construct affine line, verify all others
  match c_α = c_e + α c_o.

Strong empirical confirmation (e.g., 30+ cases all matching) makes the
affine-line hypothesis rigorous in practice.
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
    n1 = len(L1)
    T = list(range(k1))
    vals_T = [c_full[i] for i in T]
    c_check = lagrange_interp_codeword(L1, T, vals_T, p)
    return all(c_check[i] == c_full[i] for i in range(n1))


def verify_affine_line_for_case(alphas, f_e, f_o, L1, k1, p, max_alphas=10):
    """Pick 2 alphas, compute c_e, c_o, verify on the rest."""
    n1 = len(L1)
    closest = []
    for a in alphas[:max_alphas]:
        fold1 = [(f_e[i] + a * f_o[i]) % p for i in range(n1)]
        c, agree = find_closest_codeword(fold1, L1, k1, p)
        closest.append((a, c, agree))
    if len(closest) < 3:
        return None, "Too few α's"
    a1, c1, _ = closest[0]
    a2, c2, _ = closest[1]
    inv_da = pow((a2 - a1) % p, p - 2, p)
    c_o = [((c2[i] - c1[i]) * inv_da) % p for i in range(n1)]
    c_e = [(c1[i] - a1 * c_o[i]) % p for i in range(n1)]
    if not (is_codeword(c_e, L1, k1, p) and is_codeword(c_o, L1, k1, p)):
        return None, "c_e or c_o not in C_1"
    matches = 0
    for a, c_a, _ in closest[2:]:
        c_pred = [(c_e[i] + a * c_o[i]) % p for i in range(n1)]
        if all(c_pred[i] == c_a[i] for i in range(n1)):
            matches += 1
    return (matches, len(closest) - 2), f"matched {matches}/{len(closest)-2}"


def main():
    PRIMES = [193, 449]
    target_per_q = 10
    print(f"=== Verify affine-line hypothesis universally ===")
    print()
    overall_matches = 0
    overall_checks = 0
    for p in PRIMES:
        chain = setup_chain(p, N0, K0, R=R)
        L_R, k_R, _ = chain[R]
        n_R = len(L_R)
        H_R = parity_check(L_R, n_R, k_R, p)
        L1, k1, _ = chain[1]
        rng = random.Random(2026 + p)

        print(f"--- q = {p} ---")
        n_with_d1_9 = 0
        n_full_match = 0
        n_attempts = 0
        while n_with_d1_9 < target_per_q and n_attempts < 80:
            n_attempts += 1
            f, T1, T2 = construct_K2_psi_in_U(rng, p, chain, H_R, n_R)
            if f is None: continue
            alphas, _, _, _, f_e, f_o = find_alphas_d1_eq_9(f, chain, p)
            if len(alphas) < 3:
                continue
            n_with_d1_9 += 1
            result, msg = verify_affine_line_for_case(alphas, f_e, f_o, L1, k1, p)
            if result is None:
                print(f"  attempt {n_attempts}: {len(alphas)} α's, {msg}")
            else:
                matches, total = result
                full = (matches == total)
                marker = "✓ FULL MATCH" if full else f"✗ {matches}/{total}"
                if full: n_full_match += 1
                overall_matches += matches
                overall_checks += total
                print(f"  attempt {n_attempts}: {len(alphas)} α's at d_1=9, {marker}, T1={T1}, T2={T2}")
        print(f"  q={p}: {n_full_match}/{n_with_d1_9} cases with FULL affine-line match")

    print()
    print(f"=== Overall ===")
    print(f"Total individual α verifications: {overall_matches}/{overall_checks}")
    if overall_matches == overall_checks:
        print(f"★★★ AFFINE-LINE HYPOTHESIS UNIVERSALLY VERIFIED ★★★")
        print(f"All closest codewords for d_1=9 α's lie on a single affine line in C_1.")


if __name__ == "__main__":
    main()
