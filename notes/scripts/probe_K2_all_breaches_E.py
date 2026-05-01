"""probe_K2_all_breaches_E.py — compute |E(f)| for ALL 7 K=2 dense breaches.

Following audit_tie_robust_K2.reproduce_K2_breaches, extract each of the 7 (pair, f)
indices and characterize |E(f)|. Tests whether the worst-case |E|=7 is unique to
(18,8) or shared across breaches.
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

W_R = 3


def reproduce_all_breaches(p, chain, H_R, seed=4242):
    """Reconstruct all 7 K=2 dense breaches from audit_tie_robust_K2."""
    rng = random.Random(seed)
    L0 = chain[0][0]
    n_R = N_R
    w_R = W_R
    breach_keys = {(1, 5), (2, 8), (4, 2), (8, 0), (18, 8), (25, 3), (25, 6)}
    found = {}
    for pair_idx in range(30):
        T1 = tuple(sorted(rng.sample(range(n_R), w_R)))
        overlap = rng.choice([0, 1])
        if overlap == 0:
            available = [j for j in range(n_R) if j not in T1]
            if len(available) < w_R:
                continue
            T2 = tuple(sorted(rng.sample(available, w_R)))
        else:
            shared = rng.choice(list(T1))
            others_pool = [j for j in range(n_R) if j not in T1]
            if len(others_pool) < w_R - 1:
                continue
            others = rng.sample(others_pool, w_R - 1)
            T2 = tuple(sorted([shared] + others))
        if T2 == T1 or len(set(T1) & set(T2)) > 1:
            continue
        eps1 = [0] * n_R
        eps2 = [0] * n_R
        for j in T1:
            eps1[j] = rng.randrange(1, p)
        for j in T2:
            eps2[j] = rng.randrange(1, p)
        u1 = matvec(H_R, eps1, p)
        u2 = matvec(H_R, eps2, p)
        if gauss_rank([u1, u2], p) != 2:
            continue
        for f_idx in range(10):
            c = {b: (rng.randrange(p), rng.randrange(p)) for b in product([0, 1], repeat=R)}
            msg = [rng.randrange(p) for _ in range(K0)]
            fhat = construct_f_with_psi_in_U(u1, u2, c, msg, p)
            f = evaluate_dft(fhat, L0, p)
            if (pair_idx, f_idx) in breach_keys:
                ov = len(set(T1) & set(T2))
                found[(pair_idx, f_idx)] = (f, T1, T2, ov)
    return found


def compute_E(f, chain, p):
    L0 = chain[0][0]
    L1, k1, _ = chain[1]
    n1 = len(L1)
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
    return E, d_dist


def main():
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, p)

    print(f"All 7 K=2 dense breaches: |E(f)| profile at p={p}")
    print()

    found = reproduce_all_breaches(p, chain, H_R)
    print(f"  Reproduced {len(found)}/7 breaches")
    print()

    print("=" * 80)
    print(f"  {'breach':<10} {'T1':<14} {'T2':<14} {'ov':<3} {'|E|':<5} {'d_1 dist':<30}")
    print("=" * 80)
    results = []
    for key in sorted(found.keys()):
        f, T1, T2, ov = found[key]
        E, d_dist = compute_E(f, chain, p)
        d_dist_str = ", ".join(f"{d}:{c}" for d, c in sorted(d_dist.items()))
        print(f"  {str(key):<10} {str(T1):<14} {str(T2):<14} {ov:<3} {len(E):<5} {d_dist_str}")
        results.append((key, T1, T2, ov, E, d_dist))
    print()

    print("=" * 80)
    print("  α_1 ∈ E(f) per breach")
    print("=" * 80)
    for key, T1, T2, ov, E, _ in results:
        alphas = sorted(a for a, d in E)
        print(f"  {str(key):<10}: {alphas}  (with d_1: {[d for a, d in sorted(E)]})")
    print()

    print("=" * 80)
    print("  SUMMARY")
    print("=" * 80)
    counts = [len(r[4]) for r in results]
    print(f"  |E(f)| values across 7 breaches: {sorted(counts, reverse=True)}")
    print(f"  Max: {max(counts)} | Min: {min(counts)} | Mean: {sum(counts)/len(counts):.2f}")
    n_ge_5 = sum(1 for c in counts if c >= 5)
    print(f"  # breaches with |E(f)| ≥ 5: {n_ge_5}/7")
    print()

    # Check: is the 7 max unique to (18,8), or shared?
    if max(counts) == 7:
        max_keys = [r[0] for r in results if len(r[4]) == 7]
        print(f"  Breaches achieving max |E|=7: {max_keys}")


if __name__ == '__main__':
    main()
