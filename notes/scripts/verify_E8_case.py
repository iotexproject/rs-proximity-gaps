"""verify_E8_case.py — verify the |E(f)|=8 case found by search_K2_double_deep.

T1=(0, 1, 6), T2=(0, 2, 5), ov=1, seed in [5000, 5060). Search reported
deep=[(85, 7)] #boundary=7, so |E(f)| = 8.
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
                return f, T1, T2, len(set(T1) & set(T2)), d_above
    return None, None, None, None, None


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

    print("Searching for case T1=(0,1,6), T2=(0,2,5) in seed range [5000, 5060)...")
    found = None
    for k in range(60):
        rng = random.Random(5000 + k)
        f, T1, T2, ov, d_above = gen_K2_above_J(rng, p, chain, H_R)
        if f is None: continue
        if T1 == target_T1 and T2 == target_T2:
            found = (f, ov, d_above, k)
            print(f"  Found at seed_offset={k}, ov={ov}, exact dist(f,C_0) = {d_above} (early_exit does full enumeration when above-J)")
            break
    if found is None:
        print("  ERROR: not found")
        return

    f, ov, d_above, _ = found

    # Compute E(f) and full d_1 distribution
    L1_arr = np.array(L1, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    info_sets_arr = np.array(list(combinations(range(n1), k1)), dtype=np.int64)
    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)

    E = []
    d_dist = {}
    for a1 in range(p):
        fold1_arr = (f_e_arr + a1 * f_o_arr) % p
        d = fast_d1(fold1_arr, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1)
        d_dist[d] = d_dist.get(d, 0) + 1
        if d <= 8:
            E.append((a1, d))

    print()
    print(f"  d_1 distribution: {sorted(d_dist.items())}")
    print(f"  |E(f)| = {len(E)}")
    print(f"  Exceptional (α_1, d_1): {E}")
    n_deep = sum(1 for a, d in E if d < 8)
    n_boundary = sum(1 for a, d in E if d == 8)
    print(f"  #deep (d_1 < 8): {n_deep}")
    print(f"  #boundary (d_1 = 8): {n_boundary}")
    print()

    if len(E) > 7:
        print(f"  ★★★ NEW EMPIRICAL MAX |E(f)| = {len(E)}, exceeding prior 7 (from K=2 (18,8))")
        print(f"     (T1, T2, ov) = ({target_T1}, {target_T2}, {ov})")
    elif len(E) == 7:
        print(f"  Matches prior max |E(f)| = 7")
    else:
        print(f"  Below prior max |E(f)| = 7")


if __name__ == '__main__':
    main()
