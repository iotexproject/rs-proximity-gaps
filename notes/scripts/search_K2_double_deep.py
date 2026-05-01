"""search_K2_double_deep.py — search for K=2 above-J f's with ≥ 2 deep α_1's.

Conjecture 130.1(1): #{α_1 : d_1(α_1) < δn_1} ≤ 1 for any K=2 above-J f.

Falsify by finding above-J f with 2 distinct α_1's both at d_1 < 8.
Use multiple seeds; report each above-J case's # deep α_1's.

Usage: python3 search_K2_double_deep.py [n_attempts=100] [seed_base=5000]
"""
from __future__ import annotations
import sys, os, random, time
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
            above_J, _ = is_above_J_early_exit(f, L0, K0, W_J, p)
            if above_J:
                return f, T1, T2, len(set(T1) & set(T2))
    return None, None, None, None


def deep_count(f, chain, p):
    L0 = chain[0][0]
    L1, k1, _ = chain[1]
    n1 = len(L1)
    L1_arr = np.array(L1, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    info_sets_arr = np.array(list(combinations(range(n1), k1)), dtype=np.int64)
    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)
    deep_alphas = []
    boundary_alphas = []
    for a1 in range(p):
        fold1_arr = (f_e_arr + a1 * f_o_arr) % p
        d = fast_d1(fold1_arr, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1)
        if d < 8:
            deep_alphas.append((a1, d))
        elif d == 8:
            boundary_alphas.append(a1)
    return deep_alphas, boundary_alphas


def main():
    n_attempts = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    seed_base = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, p)

    print(f"Search for K=2 above-J f's with 2+ DEEP α_1's (d_1 < 8)")
    print(f"  Conjecture 130.1(1): #deep ≤ 1.")
    print(f"  Counter-example would falsify; otherwise strengthens conjecture.")
    print(f"  Attempts: {n_attempts}, seed_base: {seed_base}")
    print()

    n_above_J = 0
    n_with_deep = 0
    n_with_2plus_deep = 0
    deep_distribution = {}
    examples_2plus = []
    examples_1deep = []
    t0 = time.time()
    for k in range(n_attempts):
        rng = random.Random(seed_base + k)
        f, T1, T2, ov = gen_K2_above_J(rng, p, chain, H_R)
        if f is None:
            continue
        n_above_J += 1
        deep, boundary = deep_count(f, chain, p)
        n_deep = len(deep)
        deep_distribution[n_deep] = deep_distribution.get(n_deep, 0) + 1
        if n_deep >= 1:
            n_with_deep += 1
        if n_deep >= 2:
            n_with_2plus_deep += 1
            examples_2plus.append((T1, T2, ov, deep, len(boundary)))
            print(f"  [{n_above_J}] T1={T1} T2={T2} ov={ov} #deep={n_deep} ★★ "
                  f"deep α_1's: {deep}, #boundary={len(boundary)}")
        elif n_deep == 1 and len(examples_1deep) < 5:
            examples_1deep.append((T1, T2, ov, deep, len(boundary)))
        if (k + 1) % 20 == 0:
            print(f"  progress: {k+1}/{n_attempts} attempts, "
                  f"{n_above_J} above-J, {n_with_deep} with ≥1 deep, "
                  f"{n_with_2plus_deep} with ≥2 deep, "
                  f"{time.time()-t0:.0f}s")

    print()
    print(f"  ===  RESULT ===")
    print(f"  Above-J K=2 cases: {n_above_J}/{n_attempts}")
    print(f"  Distribution of #deep α_1's: {sorted(deep_distribution.items())}")
    print(f"  Cases with ≥ 1 deep: {n_with_deep}")
    print(f"  Cases with ≥ 2 deep: {n_with_2plus_deep}")
    print()
    if n_with_2plus_deep == 0:
        print(f"  ✓ Conjecture 130.1(1) UPHELD: no K=2 above-J case has ≥ 2 deep α_1's")
        print(f"    across {n_above_J} cases tested.")
    else:
        print(f"  ✗ Conjecture 130.1(1) FALSIFIED: found {n_with_2plus_deep} counter-examples")
        for ex in examples_2plus[:5]:
            T1, T2, ov, deep, nb = ex
            print(f"    T1={T1} T2={T2} ov={ov} deep={deep} #boundary={nb}")
    print()
    print(f"  Sample 1-deep cases (for sanity):")
    for ex in examples_1deep[:3]:
        T1, T2, ov, deep, nb = ex
        print(f"    T1={T1} T2={T2} ov={ov} deep={deep} #boundary={nb}")


if __name__ == '__main__':
    main()
