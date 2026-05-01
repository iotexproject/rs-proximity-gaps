"""probe_E8_structure.py — structural decomposition of the |E(f)|=8 case.

T1=(0,1,6), T2=(0,2,5), ov=1, seed_offset=46 in [5000, ...).
α_1's: 6, 45, 50, 63, 73, 75 (boundary, d_1=8), 85 (deep, d_1=7), 95 (boundary).

Test whether the universal "S^** = common stable subset" partition holds, and what size.
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
from mds_decoder import precompute_diff_inv
from exact_above_J import is_above_J_early_exit
from probe_18_8_structure import find_decoded_codeword

W_R = 3


def gen_K2_above_J(rng, p, chain, H_R, max_tries=10):
    L0 = chain[0][0]
    n_R = N_R
    for _ in range(max_tries):
        T1 = tuple(sorted(rng.sample(range(n_R), W_R)))
        overlap = rng.choice([0, 1])
        if overlap == 0:
            avail = [j for j in range(n_R) if j not in T1]
            if len(avail) < W_R: continue
            T2 = tuple(sorted(rng.sample(avail, W_R)))
        else:
            shared = rng.choice(list(T1))
            others = [j for j in range(n_R) if j not in T1]
            if len(others) < W_R - 1: continue
            T2 = tuple(sorted([shared] + rng.sample(others, W_R - 1)))
        if T2 == T1: continue
        if len(set(T1) & set(T2)) > 1: continue
        eps1 = [0] * n_R
        eps2 = [0] * n_R
        for j in T1: eps1[j] = rng.randrange(1, p)
        for j in T2: eps2[j] = rng.randrange(1, p)
        u1 = matvec(H_R, eps1, p)
        u2 = matvec(H_R, eps2, p)
        if gauss_rank([u1, u2], p) != 2: continue
        for _ in range(8):
            c = {b: (rng.randrange(p), rng.randrange(p)) for b in product([0, 1], repeat=R)}
            msg = [rng.randrange(p) for _ in range(K0)]
            fhat = construct_f_with_psi_in_U(u1, u2, c, msg, p)
            f = evaluate_dft(fhat, L0, p)
            above_J, d_above = is_above_J_early_exit(f, L0, K0, W_J, p)
            if above_J:
                return f, T1, T2, d_above
    return None, None, None, None


def main():
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, p)
    L0 = chain[0][0]
    L1, k1, _ = chain[1]
    n1 = len(L1)
    target_T1 = (0, 1, 6)
    target_T2 = (0, 2, 5)

    found = None
    for k in range(60):
        rng = random.Random(5000 + k)
        f, T1, T2, d_above = gen_K2_above_J(rng, p, chain, H_R)
        if f is None: continue
        if T1 == target_T1 and T2 == target_T2:
            found = (f, d_above)
            break
    f, d_above = found
    print(f"K=2 |E(f)|=8 case: T1={target_T1}, T2={target_T2}, dist(f,C_0)={d_above}")
    print()

    f_e, f_o = even_odd_parts(f, L0, p)
    L1_arr = np.array(L1, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    info_sets_arr = np.array(list(combinations(range(n1), k1)), dtype=np.int64)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)

    # Compute E(f)
    E = []
    d_dist = {}
    for a1 in range(p):
        fold1_arr = (f_e_arr + a1 * f_o_arr) % p
        d = fast_d1(fold1_arr, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1)
        d_dist[d] = d_dist.get(d, 0) + 1
        if d <= 8:
            E.append((a1, d))

    print(f"  d_1 distribution: {sorted(d_dist.items())}")
    print(f"  |E(f)| = {len(E)}")
    print(f"  E(f) = {E}")
    print()

    # Get codewords + agreement sets
    codewords = []
    for a1, d1 in E:
        fold1_arr = (f_e_arr + a1 * f_o_arr) % p
        c, info_set = find_decoded_codeword(fold1_arr, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1)
        S_alpha = sorted([i for i in range(n1) if c[i] == fold1_arr[i] % p])
        codewords.append((a1, d1, c, S_alpha))

    print(f"  α_1 → S_1(α_1):")
    for a1, d1, c, S in codewords:
        print(f"    α={a1:3d} (d_1={d1}): |S|={len(S)}, S={S}")

    # Compute common stable subset S^**
    S_star = set(range(n1))
    for a1, d1, c, S in codewords:
        S_star &= set(S)
    S_star = sorted(S_star)
    print()
    print(f"  S_1^** (= ∩ S_1(α_1) over E(f)) = {S_star}, size = {len(S_star)}")
    print()

    # Compute pairwise intersections
    print(f"  Pairwise |S_1(α) ∩ S_1(α')|:")
    for i, (ai, di, _, Si) in enumerate(codewords):
        for j, (aj, dj, _, Sj) in enumerate(codewords):
            if i < j:
                inter = len(set(Si) & set(Sj))
                print(f"    {ai} ∩ {aj}: |intersection| = {inter}")

    # Decomposition: stable + boundary-extensible + deep-extensible
    boundary_extensions = []
    deep_extension = []
    for a1, d1, c, S in codewords:
        extra = sorted(set(S) - set(S_star))
        if d1 == 8:
            boundary_extensions.append((a1, extra))
        else:  # deep
            deep_extension.append((a1, extra))

    print()
    print(f"  Decomposition of E(f):")
    print(f"    |S_1^**| = {len(S_star)} (stable common positions)")
    for a1, extra in boundary_extensions:
        print(f"    boundary α={a1}: extends S^** by {extra}")
    for a1, extra in deep_extension:
        print(f"    deep α={a1}: extends S^** by {extra}")

    # Sanity: are all extensions distinct singletons?
    extensions_b = [tuple(extra) for a, extra in boundary_extensions]
    print(f"  All boundary extensions distinct? {len(set(extensions_b)) == len(extensions_b)}")
    print(f"  All boundary extensions singletons? {all(len(e) == 1 for e in extensions_b)}")


if __name__ == '__main__':
    main()
