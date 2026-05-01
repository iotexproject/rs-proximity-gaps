"""verify_K2_breach2.py — reproduce the EXACT 287-breach examples from probe_K2_with_vdelta.

Step through the rng state of the original probe to reproduce specific f's.
Then verify with rigorous |V_δ| + heavy-sampling above-J check.
"""
from __future__ import annotations
import sys, os, random
from itertools import product, combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, parity_check, matvec, gauss_rank
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
    n_pairs = 30
    n_f_per = 10

    rng = random.Random(seed)
    chain = setup_chain(P, N0, K0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, P)
    p = P
    n_R = N_R
    w_R = W_R
    m = M
    HT_perp_list = precompute_HT_perp(H_R, n_R, p, max_w=w_R)

    n_total = 0
    breaches = []

    # Replay the EXACT probe loop
    for pair_idx in range(n_pairs):
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
        if T2 == T1:
            continue
        actual_overlap = len(set(T1) & set(T2))
        if actual_overlap > 1:
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

        for f_idx in range(n_f_per):
            c = {}
            for b in product([0, 1], repeat=R):
                c[b] = (rng.randrange(p), rng.randrange(p))
            msg = [rng.randrange(p) for _ in range(K0)]
            fhat = construct_f_with_psi_in_U(u1, u2, c, msg, p)
            f = evaluate_dft(fhat, L0, p)

            corners = compute_corner_syndromes(f, chain, R, p, H_R)
            nz = [list(s) for s in corners.values() if any(x != 0 for x in s)]
            rk = gauss_rank(nz, p) if nz else 0
            if rk != 2:
                continue

            n_total += 1
            sigmas = alpha_syndromes_batch_np(f, chain, R, p, H_R, m, n_R, p)
            v_delta = count_v_delta_np(sigmas, HT_perp_list, p)
            if v_delta > 2 * p:
                # Above-J check (heavy samples)
                d_lb = dist_lower_bound_sampling(f, L0, K0, p, n_samples=200000, batch=4096, seed=seed + n_total)
                K, dim_distr, _, _ = K_classifier(f, chain, H_R, p, n_R, w_R)
                breaches.append({
                    'T1': T1, 'T2': T2, 'overlap': actual_overlap,
                    'pair_idx': pair_idx, 'f_idx': f_idx,
                    'v_delta': v_delta, 'dist_lb': d_lb,
                    'K': K, 'dim_distr': dim_distr,
                    'eps1': eps1, 'eps2': eps2, 'c': dict(c), 'msg': msg,
                    'u1': u1, 'u2': u2,
                })
                print(f"# BREACH #{len(breaches)}: pair={pair_idx}, f={f_idx}, T1={T1}, T2={T2}, "
                      f"overlap={actual_overlap}, K={K}, |V_δ|={v_delta}, dist_lb={d_lb}", flush=True)

    print()
    print(f"# Total breaches: {len(breaches)}")
    print()
    if breaches:
        # Examine first breach in detail
        br = breaches[0]
        print(f"# === Detailed analysis of first breach ===")
        print(f"# T1={br['T1']}, T2={br['T2']}, overlap={br['overlap']}")
        print(f"# eps1 = {br['eps1']}")
        print(f"# eps2 = {br['eps2']}")
        print(f"# u1 = {br['u1']}")
        print(f"# u2 = {br['u2']}")
        print(f"# c = {br['c']}")
        print(f"# msg = {br['msg']}")
        print(f"# K(f) = {br['K']}, dim_distr = {br['dim_distr']}, |V_δ| = {br['v_delta']}")
        print(f"# dist lower bound (200K samples) = {br['dist_lb']}")
        if br['dist_lb'] > W_J:
            print(f"# ✓ ABOVE Johnson confirmed (W_J = {W_J})")
        else:
            print(f"# ✗ NOT confirmed above-J — sampling artifact?")


if __name__ == '__main__':
    main()
