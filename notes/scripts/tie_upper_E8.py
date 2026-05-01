"""tie_upper_E8.py — compute tie_upper for the new |E(f)|=8 case."""
from __future__ import annotations
import sys, os, random
import numpy as np
from itertools import product, combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_step5_n32_studio import P, N0, K0, R, N_R, W_J, evaluate_dft
from fri_2round_attack import setup_chain, parity_check, matvec, gauss_rank
from probe_K2_construct import construct_f_with_psi_in_U
from fast_tie_robust import compute_tie_robust_fast
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
                return f, T1, T2, d_above
    return None, None, None, None


def main():
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, p)
    target = ((0, 1, 6), (0, 2, 5))

    print("Finding the |E(f)|=8 case...")
    found = None
    for k in range(60):
        rng = random.Random(5000 + k)
        f, T1, T2, d_above = gen_K2_above_J(rng, p, chain, H_R)
        if f is None: continue
        if (T1, T2) == target:
            found = (f, d_above)
            break
    if found is None:
        print("  ERROR: not found")
        return
    f, d_above = found

    print(f"  Computing tie_upper for the |E|=8 case (T1={target[0]}, T2={target[1]})...")
    P_B, tie, d1d, d2d, jd = compute_tie_robust_fast(f, chain, p)
    print()
    print(f"  P_B (E[1 - d_2/n_2]):     {P_B:.4f}")
    print(f"  tie_upper:                 {tie:.4f}")
    print(f"  K=1 leader tie_upper:      0.4490")
    print(f"  K=2 (18,8) tie_upper:      0.4477")
    print()
    print(f"  d_1 distribution: {sorted(d1d.items())}")
    print(f"  d_2 distribution: {sorted(d2d.items())}")
    print()
    if tie > 0.4490:
        print(f"  ★★★ NEW MAX TIE_UPPER: {tie:.4f} > 0.4490 (prior K=1 leader)")
    elif tie > 0.4477:
        print(f"  ★ Beats K=2 (18,8) but not K=1 leader")
    else:
        print(f"  Below both prior maxes — |E|=8 case has limited tie_upper impact")


if __name__ == '__main__':
    main()
