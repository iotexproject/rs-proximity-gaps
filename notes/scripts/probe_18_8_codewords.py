"""probe_18_8_codewords.py — check whether all codewords agree on common S_1^*."""
from __future__ import annotations
import sys, os, random
import numpy as np
from itertools import product, combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_step5_n32_studio import P, N0, K0, R, N_R, W_J, evaluate_dft
from fri_2round_attack import setup_chain, parity_check, matvec, gauss_rank, even_odd_parts
from probe_K2_construct import construct_f_with_psi_in_U
from mds_decoder import precompute_diff_inv, batched_extras
from probe_18_8_structure import reproduce_18_8, find_decoded_codeword
from fast_tie_robust import fast_d1


def main():
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, p)
    L0 = chain[0][0]
    L1, k1, _ = chain[1]
    n1 = len(L1)

    f, T1, T2, fhat = reproduce_18_8(p, chain, H_R)
    f_e, f_o = even_odd_parts(f, L0, p)
    L1_arr = np.array(L1, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    info_sets_arr = np.array(list(combinations(range(n1), k1)), dtype=np.int64)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)

    E_alphas = [13, 33, 46, 48, 56, 65, 79]
    S_star = [0, 4, 5, 8, 12, 13, 15]  # the common 7

    print(f"K=2 (18,8) — checking whether all codewords agree on S_1^* = {S_star}")
    print()

    codewords = {}
    for a1 in E_alphas:
        fold1_arr = (f_e_arr + a1 * f_o_arr) % p
        c, info_set = find_decoded_codeword(fold1_arr, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1)
        codewords[a1] = c

    # Print codeword values on S_1^*
    print(f"  Position:    {' '.join(f'y[{i:2d}]' for i in S_star)}")
    for a1 in E_alphas:
        c = codewords[a1]
        vals = [c[i] for i in S_star]
        print(f"  α={a1:3d}: c =  {' '.join(f'{v:5d}' for v in vals)}")

    print()
    print(f"  fold_1 values on S_1^* per α_1:")
    for a1 in E_alphas:
        fold1 = [(f_e[i] + a1 * f_o[i]) % p for i in range(n1)]
        vals = [fold1[i] for i in S_star]
        print(f"  α={a1:3d}: fold = {' '.join(f'{v:5d}' for v in vals)}")

    print()
    print(f"  f_e values on S_1^*: {[f_e[i] for i in S_star]}")
    print(f"  f_o values on S_1^*: {[f_o[i] for i in S_star]}")

    # Test: are all codewords equal on S_1^*?
    c_ref = codewords[13]
    all_same = all(all(codewords[a][i] == c_ref[i] for i in S_star) for a in E_alphas)
    print()
    print(f"  All 7 codewords agree on S_1^*? {all_same}")

    if all_same:
        # Then f_o must vanish on S_1^*
        f_o_S = [f_o[i] for i in S_star]
        print(f"  Therefore f_o vanishes on S_1^*: {f_o_S}")
        print(f"  All zero? {all(v == 0 for v in f_o_S)}")


if __name__ == '__main__':
    main()
