"""probe_18_8_structure.py — what's special about the K=2 (18,8) ov=1 case?

Examine the Fourier support, fold structure, and codeword agreement pattern
of the (18,8) breach to identify what produces 6 boundary α_1's at d_1 = 8
(in addition to the universal 1 deep).

Hypothesis to check: 6 boundary α_1's correspond to 6 distinct codewords c_α ∈ C_1
that all simultaneously achieve dist exactly 8 with fold_1(α). If so, examine
those codewords for a common structure.
"""
from __future__ import annotations
import sys, os, random
import numpy as np
from itertools import product, combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_step5_n32_studio import P, N0, K0, R, N_R, W_J, evaluate_dft
from fri_2round_attack import setup_chain, parity_check, matvec, gauss_rank, even_odd_parts
from probe_K2_construct import construct_f_with_psi_in_U
from fast_tie_robust import fast_d1
from mds_decoder import precompute_diff_inv, batched_extras

W_R = 3


def reproduce_18_8(p, chain, H_R, seed=4242):
    rng = random.Random(seed)
    L0 = chain[0][0]
    n_R, w_R = N_R, W_R
    target = (18, 8)
    for pair_idx in range(30):
        T1 = tuple(sorted(rng.sample(range(n_R), w_R)))
        overlap = rng.choice([0, 1])
        if overlap == 0:
            available = [j for j in range(n_R) if j not in T1]
            if len(available) < w_R: continue
            T2 = tuple(sorted(rng.sample(available, w_R)))
        else:
            shared = rng.choice(list(T1))
            others_pool = [j for j in range(n_R) if j not in T1]
            if len(others_pool) < w_R - 1: continue
            others = rng.sample(others_pool, w_R - 1)
            T2 = tuple(sorted([shared] + others))
        if T2 == T1 or len(set(T1) & set(T2)) > 1: continue
        eps1 = [0] * n_R
        eps2 = [0] * n_R
        for j in T1: eps1[j] = rng.randrange(1, p)
        for j in T2: eps2[j] = rng.randrange(1, p)
        u1 = matvec(H_R, eps1, p)
        u2 = matvec(H_R, eps2, p)
        if gauss_rank([u1, u2], p) != 2: continue
        for f_idx in range(10):
            c = {b: (rng.randrange(p), rng.randrange(p)) for b in product([0, 1], repeat=R)}
            msg = [rng.randrange(p) for _ in range(K0)]
            fhat = construct_f_with_psi_in_U(u1, u2, c, msg, p)
            f = evaluate_dft(fhat, L0, p)
            if (pair_idx, f_idx) == target:
                return f, T1, T2, fhat
    return None, None, None, None


def find_decoded_codeword(fold1_arr, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1):
    """Return the codeword in C_1 that achieves the minimum distance to fold1."""
    extras = batched_extras(info_sets_arr, fold1_arr, L1_arr, D1, inv_D1, p)
    best_idx = int(extras.argmax())
    info_set = info_sets_arr[best_idx]
    # Reconstruct codeword via Lagrange interpolation on info_set
    n1 = len(L1_arr)
    L1 = L1_arr.tolist()
    fold1 = fold1_arr.tolist()
    # The codeword c is the unique poly of deg < k1 matching fold1 on info_set
    # Plus the agreement extras matched outside info_set. So full codeword is
    # determined by the k1 values fold1[info_set[i]].
    def eval_lagrange(x_eval, xs, ys):
        result = 0
        for i in range(len(xs)):
            num, den = 1, 1
            for j in range(len(xs)):
                if i == j: continue
                num = (num * (x_eval - xs[j])) % p
                den = (den * (xs[i] - xs[j])) % p
            result = (result + ys[i] * num * pow(den, p - 2, p)) % p
        return result
    xs = [L1[i] for i in info_set]
    ys = [fold1[i] for i in info_set]
    codeword = [eval_lagrange(L1[i], xs, ys) for i in range(n1)]
    return codeword, info_set


def main():
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, p)
    L0 = chain[0][0]
    L1, k1, _ = chain[1]
    n1 = len(L1)

    f, T1, T2, fhat = reproduce_18_8(p, chain, H_R)
    print(f"K=2 (18,8) breach analysis")
    print(f"  T1={T1}, T2={T2}, ov=1")
    print(f"  Fourier support at level 0: f̂ has {sum(1 for v in fhat if v != 0)} nonzero positions")
    print()

    # Compute f_e, f_o
    f_e, f_o = even_odd_parts(f, L0, p)
    print(f"  f_e (level-1 even): supp_size={sum(1 for v in f_e if v != 0)}/{n1}")
    print(f"  f_o (level-1 odd):  supp_size={sum(1 for v in f_o if v != 0)}/{n1}")
    print()

    # For each exceptional α_1, extract the closest codeword
    L1_arr = np.array(L1, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    info_sets_arr = np.array(list(combinations(range(n1), k1)), dtype=np.int64)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)

    E_alphas = [13, 33, 46, 48, 56, 65, 79]  # from prior probe

    print("=" * 80)
    print("  α_1, d_1, decoded codeword (first 8 coords), agreement set")
    print("=" * 80)
    codewords = []
    for a1 in E_alphas:
        fold1_arr = (f_e_arr + a1 * f_o_arr) % p
        d = fast_d1(fold1_arr, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1)
        c, info_set = find_decoded_codeword(fold1_arr, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1)
        # Compute agreement positions
        S_alpha = [i for i in range(n1) if c[i] == fold1_arr[i] % p]
        codewords.append((a1, d, c, sorted(S_alpha)))
        print(f"  α={a1:3d}, d_1={d}, codeword[:8]={c[:8]}, |S|={len(S_alpha)}, S={S_alpha}")

    print()
    print("=" * 80)
    print("  Pairwise codeword analysis")
    print("=" * 80)
    # Are codewords at boundary α_1's related by simple operations?
    # E.g., do c_α - c_α' equal scalar multiples of some fixed codeword?
    cs = [c for a, d, c, s in codewords]

    # Compute pairwise differences
    print("  Codeword min-poly degrees (in F_p[x]):")
    for i, (a, d, c, s) in enumerate(codewords):
        # Reconstruct polynomial degree from k1 = 4 coefficients
        # via inverse Lagrange. Just check first few values.
        nz = sum(1 for v in c if v != 0)
        print(f"    α={a}: nz_coords={nz}/{n1}, d_1={d}")

    print()
    print("  Pairwise codeword differences |c_α - c_α'| (Hamming weight):")
    for i, (ai, _, ci, _) in enumerate(codewords):
        for j, (aj, _, cj, _) in enumerate(codewords):
            if i < j:
                diff = [(ci[k] - cj[k]) % p for k in range(n1)]
                hw = sum(1 for v in diff if v != 0)
                print(f"    c_{ai} - c_{aj}: HW = {hw}")

    print()
    print("=" * 80)
    print("  Agreement-set overlaps (|S_α ∩ S_α'|)")
    print("=" * 80)
    for i, (ai, _, _, si) in enumerate(codewords):
        for j, (aj, _, _, sj) in enumerate(codewords):
            if i < j:
                overlap = len(set(si) & set(sj))
                print(f"    α={ai} ∩ α={aj}: |S| ∩ = {overlap}, |S_{ai}|={len(si)}, |S_{aj}|={len(sj)}")


if __name__ == '__main__':
    main()
