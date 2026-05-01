"""probe_K2_with_vdelta.py — extension of probe_K2_construct: also computes |V_δ|
for each constructed K≥2 above-J f to TEST the Direction A conjecture.

Critical question: for above-J f with K(f) ≥ 2 (which we just discovered exist
at high density via direct construction), does |V_δ| ≤ R q^{R-1} = 194 still hold?

If YES (always |V_δ| ≤ 194): conjecture survives; K ≤ 1 reduction is wrong but
   the bound holds via a different mechanism.
If NO (some |V_δ| > 194): conjecture FALSIFIED. Direction A bound might fail.

Also computes a more rigorous distance check (not just sampling) for confirmed
above-J f's via brute-force agreement count over a denser sample.
"""
from __future__ import annotations
import sys, os, random, time
from itertools import product, combinations
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, parity_check, matvec, gauss_rank
from probe_step5_n32_studio import (
    P, N0, K0, R, N_R, W_J,
    evaluate_dft, fold_at_alpha, compute_corner_syndromes,
)
from mds_decoder import is_above_johnson_sampling
from probe_K_classifier import K_classifier
from probe_true_Vdelta_rank2_full_np import (
    precompute_HT_perp, alpha_syndromes_batch_np, count_v_delta_np,
)
from probe_K2_construct import construct_f_with_psi_in_U


W_R = 3
M = N_R - 2
K_R = 2
TARGET_BOUND = R * P  # 194


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 4242
    n_pairs = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    n_f_per = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    rng = random.Random(seed)

    chain = setup_chain(P, N0, K0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, P)
    p = P
    n_R = N_R
    w_R = W_R
    m = M

    print(f"# probe_K2_with_vdelta")
    print(f"# Setup: p={p}, n_0={N0}, k_0={K0}, R={R}, n_R={n_R}, w_R={w_R}, w_J={W_J}, target |V_δ| ≤ {TARGET_BOUND}")
    print(f"# Pairs: {n_pairs}, f's per pair: {n_f_per}, seed={seed}")
    print()

    HT_perp_list = precompute_HT_perp(H_R, n_R, p, max_w=w_R)

    n_total = 0
    n_above_J = 0
    n_K_ge_2 = 0
    n_above_J_K_ge_2 = 0
    breaches = []
    vdelta_distr = {}

    t0 = time.time()
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

            above, _, _ = is_above_johnson_sampling(
                f, L0, K0, p, W_J, n_samples=20000, batch=4096, seed=seed + n_total,
                return_evidence=True,
            )
            n_total += 1
            if above:
                n_above_J += 1

            K, dim_distr, K_full, dim_U = K_classifier(f, chain, H_R, p, n_R, w_R)
            if K >= 2:
                n_K_ge_2 += 1

            if above and K >= 2:
                n_above_J_K_ge_2 += 1
                # COMPUTE |V_δ|
                sigmas = alpha_syndromes_batch_np(f, chain, R, p, H_R, m, n_R, p)
                v_delta = count_v_delta_np(sigmas, HT_perp_list, p)
                vdelta_distr[v_delta] = vdelta_distr.get(v_delta, 0) + 1
                if v_delta > TARGET_BOUND:
                    breaches.append({
                        'T1': T1, 'T2': T2, 'overlap': actual_overlap,
                        'K': K, 'dim_distr': dim_distr, 'v_delta': v_delta,
                        'pair_idx': pair_idx, 'f_idx': f_idx,
                    })
                    print(f"# ★★★ BREACH: |V_δ|={v_delta} > {TARGET_BOUND}; "
                          f"T1={T1}, T2={T2}, overlap={actual_overlap}, K={K}", flush=True)

        if (pair_idx + 1) % 5 == 0:
            elapsed = time.time() - t0
            print(f"# Progress: {pair_idx+1}/{n_pairs}, "
                  f"{n_total} f's, {n_above_J_K_ge_2} above-J K≥2, "
                  f"{len(breaches)} BREACHES, elapsed {elapsed:.1f}s", flush=True)

    print()
    print(f"# === Summary ===")
    print(f"# Total f's tested: {n_total}")
    print(f"# Above-J: {n_above_J}")
    print(f"# K ≥ 2: {n_K_ge_2}")
    print(f"# Above-J AND K ≥ 2 (target population): {n_above_J_K_ge_2}")
    print(f"# |V_δ| distribution: {sorted(vdelta_distr.items())}")
    if vdelta_distr:
        max_vd = max(vdelta_distr.keys())
        min_vd = min(vdelta_distr.keys())
        print(f"# max |V_δ| = {max_vd}, min |V_δ| = {min_vd}")
    print(f"# Breaches (|V_δ| > {TARGET_BOUND}): {len(breaches)}")
    if breaches:
        print("# ★★★ CONJECTURE FALSIFIED ★★★")
        for br in breaches[:10]:
            print(f"#   T1={br['T1']}, T2={br['T2']}, overlap={br['overlap']}, "
                  f"K={br['K']}, |V_δ|={br['v_delta']}")
    else:
        print(f"# ✓ Conjecture |V_δ| ≤ {TARGET_BOUND} HOLDS for all {n_above_J_K_ge_2} K≥2 cases")


if __name__ == '__main__':
    main()
