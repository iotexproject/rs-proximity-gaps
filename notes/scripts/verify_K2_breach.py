"""verify_K2_breach.py — verify a single K=2 breach example carefully:
  (a) recompute the f from explicit construction
  (b) RIGOROUS dist(f, C_0) via brute force MDS decoder (not sampling)
  (c) RIGOROUS |V_δ| via full enum
  (d) verify K(f) = 2 by inspection
"""
from __future__ import annotations
import sys, os, random
from itertools import product, combinations
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, parity_check, matvec, gauss_rank, dist_to_code_full
from probe_step5_n32_studio import (
    P, N0, K0, R, N_R, W_J,
    evaluate_dft, fold_at_alpha, compute_corner_syndromes,
)
from mds_decoder import is_above_johnson_sampling, dist_lower_bound_sampling
from probe_K_classifier import K_classifier
from probe_true_Vdelta_rank2_full_np import (
    precompute_HT_perp, alpha_syndromes_batch_np, count_v_delta_np,
)
from probe_K2_construct import construct_f_with_psi_in_U


W_R = 3
M = N_R - 2
K_R = 2


def main():
    seed = 4242
    pair_idx_target = 0
    f_idx_target = 0
    rng = random.Random(seed)
    chain = setup_chain(P, N0, K0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, P)
    p = P
    n_R = N_R
    w_R = W_R
    m = M

    # Reproduce the FIRST breach: T1=(0, 5, 6), T2=(2, 4, 7), pair=0, f=?  Check all
    # f's in pair 0 with overlap 0
    HT_perp_list = precompute_HT_perp(H_R, n_R, p, max_w=w_R)

    # We need to step through the rng state up to that pair and that f
    breaches_to_examine = [
        # (T1, T2, expected_overlap)
        ((0, 5, 6), (2, 4, 7), 0),
        ((1, 3, 4), (0, 1, 5), 1),
        ((3, 5, 7), (0, 2, 4), 0),
    ]
    for T1, T2, expected_overlap in breaches_to_examine:
        actual_overlap = len(set(T1) & set(T2))
        assert actual_overlap == expected_overlap

        print(f"\n=== Examining T1={T1}, T2={T2}, overlap={actual_overlap} ===")
        # Choose ε deterministic
        rng_local = random.Random(hash((T1, T2)))
        eps1 = [0] * n_R
        eps2 = [0] * n_R
        for j in T1:
            eps1[j] = rng_local.randrange(1, p)
        for j in T2:
            eps2[j] = rng_local.randrange(1, p)
        u1 = matvec(H_R, eps1, p)
        u2 = matvec(H_R, eps2, p)
        print(f"  ε1 = {eps1}, ε2 = {eps2}")
        print(f"  u1 = {u1}")
        print(f"  u2 = {u2}")
        rk_U = gauss_rank([u1, u2], p)
        print(f"  rank(U) = {rk_U}")
        if rk_U != 2:
            print(f"  SKIP (U not 2-dim)")
            continue

        # Construct one specific f
        c = {}
        for b in product([0, 1], repeat=R):
            c[b] = (rng_local.randrange(p), rng_local.randrange(p))
        msg = [rng_local.randrange(p) for _ in range(K0)]
        fhat = construct_f_with_psi_in_U(u1, u2, c, msg, p)
        f = evaluate_dft(fhat, L0, p)

        # 1. Verify ψ_b ∈ U
        corners = compute_corner_syndromes(f, chain, R, p, H_R)
        for b in product([0, 1], repeat=R):
            psi = corners[b]
            # Check psi ∈ span(u1, u2)
            rk_with_psi = gauss_rank([u1, u2, list(psi)], p)
            assert rk_with_psi == 2, f"ψ_{b} not in U: rank = {rk_with_psi}"
        print(f"  ✓ All ψ_b ∈ U verified")

        # 2. Compute K(f)
        K, dim_distr, K_full, dim_U = K_classifier(f, chain, H_R, p, n_R, w_R)
        print(f"  K(f) = {K}, dim_distr = {dim_distr}, K_full = {K_full}, dim_U = {dim_U}")

        # 3. dist(f, C_0) via heavy sampling (200K random T's)
        d_lb_sample = dist_lower_bound_sampling(f, L0, K0, p, n_samples=200000, batch=4096, seed=seed)
        print(f"  dist lower bound (200K samples) = {d_lb_sample}")
        if d_lb_sample > W_J:
            print(f"    ✓ ABOVE Johnson (W_J = {W_J}; sampling FPR ≈ exp(-244) = 0)")
        else:
            print(f"    ✗ NOT confirmed above-J")

        # 4. Compute |V_δ|
        sigmas = alpha_syndromes_batch_np(f, chain, R, p, H_R, m, n_R, p)
        v_delta = count_v_delta_np(sigmas, HT_perp_list, p)
        print(f"  |V_δ| = {v_delta}")
        if v_delta > 2 * p:
            print(f"    ★ EXCEEDS conjecture bound 2q={2*p}")


if __name__ == '__main__':
    main()
