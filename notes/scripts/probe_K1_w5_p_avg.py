"""probe_K1_w5_p_avg.py — does K=1 (rank-1) above-J f with w'=5 give P_avg ≈ 0.385?

Background: probe_step5_n32 found 25 rank-1 above-J f's with w'=5 (out of 109 rank-1
above-J cases). For w'=5, my note 0117 predicts P_avg → 0.375 + O(1/q) — same
asymptotic as K=2 dense ov=1.

If observed: K=1 w'=5 P_avg ≈ 0.385 at p=97 → confirms 0.375 is the universal cap
across multiple construction classes.

If observed > 0.5: K=1 might break our 0.375 cap (would push the true cap toward 1-δ).

Targeting positions (9, 13) which gave w*=5 in probe_step5_n32_p97.

Usage: python3 probe_K1_w5_p_avg.py [n_samples=5] [seed=2026]
"""
from __future__ import annotations
import sys, os, random, time, math
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import (
    setup_chain, parity_check, matvec, gauss_rank,
    even_odd_parts, dist_to_code_full,
)
from probe_step5_n32_studio import (
    P, N0, K0, R, N_R, W_J, evaluate_dft,
    compute_corner_syndromes, image_rank_and_mu, min_wt_via_MDS,
)
from mds_decoder import is_above_johnson_sampling, dist_lower_bound_sampling


def P_avg_strategy_B(f, chain, p):
    L0, _, _ = chain[0]
    L1, _, _ = chain[1]
    L2, k2, H2 = chain[2]
    n1, n2 = len(L1), len(L2)
    f_e, f_o = even_odd_parts(f, L0, p)
    total_d2 = 0
    n_pairs = 0
    d2_dist = {}
    for a1 in range(p):
        fold1 = [(f_e[j] + a1 * f_o[j]) % p for j in range(n1)]
        g_e, g_o = even_odd_parts(fold1, L1, p)
        for a2 in range(p):
            fold2 = [(g_e[j] + a2 * g_o[j]) % p for j in range(n2)]
            d2, _ = dist_to_code_full(fold2, H2, n2, k2, p)
            if d2 is None:
                d2 = n2
            total_d2 += d2
            n_pairs += 1
            d2_dist[d2] = d2_dist.get(d2, 0) + 1
    return 1.0 - (total_d2 / n_pairs) / n2, d2_dist


def main():
    n_samples = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 2026

    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, p)
    m = N_R - k_R

    print(f"K=1 (rank-1) above-J P_avg test: positions ∈ [k_0, n_0)")
    print(f"  Targeting w'=5 (forces bulk d_2 = 5 → P_base = 0.375)")
    print(f"  Each P_avg eval ~40s.  {n_samples} samples target.")
    print()
    print(f"{'positions':<14} {'dist_lb':>8} {'w*':>4} {'|S|':>4} {'P_avg':>8} {'d2=0':>6} {'d2≤3':>6} {'time':>6}")
    print("-" * 70, flush=True)

    rng = random.Random(seed)
    n_found = 0
    n_tries = 0
    results = []
    while n_found < n_samples and n_tries < 200:
        n_tries += 1
        # Sample 2 positions in [K0, N0) and random coefs
        pos1 = rng.randint(K0, N0 - 1)
        pos2 = rng.randint(K0, N0 - 1)
        if pos1 == pos2:
            continue
        positions = tuple(sorted([pos1, pos2]))
        coefs = (rng.randrange(1, p), rng.randrange(1, p))
        fhat = [0] * N0
        for pos, c in zip(positions, coefs):
            fhat[pos] = c
        f = evaluate_dft(fhat, L0, p)
        # Above-J check
        d_lb = dist_lower_bound_sampling(f, L0, K0, p, n_samples=20000, batch=4096, seed=seed + n_tries)
        if d_lb <= W_J:
            continue
        # Rank-1 check
        corner_syns = compute_corner_syndromes(f, chain, R, p, H_R)
        rank, mu, v0_n, S_size = image_rank_and_mu(corner_syns, R, p, m)
        if rank != 1:
            continue
        w_prime, T_min, e_min = min_wt_via_MDS(v0_n, H_R, N_R, p, max_w=m)
        if w_prime != 5:
            continue
        n_found += 1
        t0 = time.time()
        P_avg, d2_dist = P_avg_strategy_B(f, chain, p)
        eval_time = time.time() - t0
        n_zero = d2_dist.get(0, 0)
        n_le_3 = sum(c for d, c in d2_dist.items() if d <= 3)
        results.append({
            'positions': positions, 'coefs': coefs, 'dist_lb': d_lb,
            'w_prime': w_prime, 'S_size': S_size, 'P_avg': P_avg,
            'n_zero': n_zero, 'n_le_3': n_le_3, 'd2_dist': dict(d2_dist),
        })
        print(f"{str(positions):<14} {d_lb:>8} {w_prime:>4} {S_size:>4} "
              f"{P_avg:>8.4f} {n_zero:>6} {n_le_3:>6} {eval_time:>5.0f}s", flush=True)

    print()
    print("=" * 70)
    print(f"K=1 w'=5 P_avg summary ({n_found} samples, {n_tries} tries):")
    if results:
        P_avgs = [r['P_avg'] for r in results]
        print(f"  max P_avg = {max(P_avgs):.4f}")
        print(f"  min P_avg = {min(P_avgs):.4f}")
        print(f"  mean      = {sum(P_avgs)/len(P_avgs):.4f}")
        print()
        print(f"  Reference K=2 dense ov=1 at p=97: P_avg = 0.385")
        print(f"  Asymptotic prediction (P_base = 1-5/8): 0.375")
        print()
        if max(P_avgs) > 0.5:
            print("  ⚠ K=1 BREAKS 0.375 cap! New worst-case found.")
        elif max(P_avgs) > 0.40:
            print("  ◎ K=1 slightly higher than K=2 dense — needs more samples.")
        else:
            print("  ✓ K=1 caps at ≤ 0.40, consistent with universal 0.375 + O(1/q).")
    else:
        print("  No K=1 w'=5 above-J found in n_tries; try more attempts or different seed.")
    print("=" * 70, flush=True)


if __name__ == '__main__':
    main()
