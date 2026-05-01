"""probe_sparse_rank_p_avg.py — does any sparse rank-r above-J f beat 0.375?

Note 0118 conjecture: P_avg ≤ 0.375 + O(1/q) UNIVERSALLY across all above-J f.
Already verified for K=1 (rank-1) and K=2 dense at our chain dims.

Remaining: SPARSE rank-2/3/4 above-J f's (the 443 + 162 + 8 cases from probe_step5_n32_p97).
For sparse rank ≥ 2: |U ∩ B_3| = 1 empirically (note 0108) → bulk d_2 ≥ 4.

If bulk d_2 = 4 ever for sparse rank-r above-J: P_avg → 0.5 — saturates (1-δ)!
That would make the UNIVERSAL 0.375 cap claim FALSE (only K=1, K=2 dense saturate at 0.375).

This probe samples 5 sparse f's of each rank (2, 3, 4) and computes P_avg.

Usage: python3 probe_sparse_rank_p_avg.py [n_per_rank=5] [seed=2026]
"""
from __future__ import annotations
import sys, os, random, time, math
from itertools import product, combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import (
    setup_chain, parity_check, matvec, gauss_rank,
    even_odd_parts, dist_to_code_full,
)
from probe_step5_n32_studio import (
    P, N0, K0, R, N_R, W_J, evaluate_dft,
    compute_corner_syndromes, image_rank_and_mu,
)
from mds_decoder import dist_lower_bound_sampling


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
    n_per_rank = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 2026
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, p)
    m = N_R - k_R

    print(f"Sparse rank-r above-J P_avg probe: positions ⊂ [k_0, n_0)")
    print(f"  Conjecture: P_avg ≤ 0.375 + O(1/q) for ALL above-J f")
    print(f"  Threshold: 0.5 = 1-δ (above this: 0.375 cap FAILS for sparse rank-r)")
    print()
    print(f"{'rank':>4} {'positions':<24} {'dist_lb':>8} {'P_avg':>8} {'#d2=0':>6} {'#d2≤3':>6} {'#d2=4':>6} {'time':>5}")
    print("-" * 80, flush=True)

    rng = random.Random(seed)
    n_found = {2: 0, 3: 0, 4: 0}
    n_tries = 0
    results = []

    while sum(n_found.values()) < 3 * n_per_rank and n_tries < 5000:
        n_tries += 1
        # Sparse construction: pick n_pos ∈ {3, 4, 5} positions in [K0, N0)
        n_pos = rng.choice([3, 4, 5])
        positions = tuple(sorted(rng.sample(range(K0, N0), n_pos)))
        coefs = tuple(rng.randrange(1, p) for _ in range(n_pos))
        fhat = [0] * N0
        for pos, c in zip(positions, coefs):
            fhat[pos] = c
        f = evaluate_dft(fhat, L0, p)
        # Above-J check
        d_lb = dist_lower_bound_sampling(f, L0, K0, p, n_samples=20000, batch=4096, seed=seed + n_tries)
        if d_lb <= W_J:
            continue
        # Rank check
        corner_syns = compute_corner_syndromes(f, chain, R, p, H_R)
        rank, _, _, _ = image_rank_and_mu(corner_syns, R, p, m)
        if rank not in (2, 3, 4) or n_found.get(rank, 0) >= n_per_rank:
            continue
        n_found[rank] += 1
        t0 = time.time()
        P_avg, d2_dist = P_avg_strategy_B(f, chain, p)
        eval_time = time.time() - t0
        n_zero = d2_dist.get(0, 0)
        n_le_3 = sum(c for d, c in d2_dist.items() if d <= 3)
        n_4 = d2_dist.get(4, 0)
        results.append({
            'rank': rank, 'positions': positions, 'd_lb': d_lb,
            'P_avg': P_avg, 'n_zero': n_zero, 'n_le_3': n_le_3, 'n_4': n_4,
            'd2_dist': dict(d2_dist),
        })
        print(f"{rank:>4} {str(positions):<24} {d_lb:>8} {P_avg:>8.4f} "
              f"{n_zero:>6} {n_le_3:>6} {n_4:>6} {eval_time:>4.0f}s", flush=True)

    print()
    print("=" * 80)
    print(f"Sparse rank-r P_avg summary ({sum(n_found.values())} samples, {n_tries} tries):")
    for r in [2, 3, 4]:
        rs = [x for x in results if x['rank'] == r]
        if rs:
            print(f"  rank-{r}: max P_avg = {max(x['P_avg'] for x in rs):.4f}, "
                  f"mean = {sum(x['P_avg'] for x in rs)/len(rs):.4f}, n = {len(rs)}")
    print()
    if results:
        all_max = max(x['P_avg'] for x in results)
        if all_max > 0.45:
            print(f"⚠ SPARSE RANK-r BREAKS 0.375 CAP: max = {all_max:.4f} > 0.45!")
            print(f"  Universal claim of note 0118 NEEDS REVISION.")
        elif all_max > 0.40:
            print(f"◎ Sparse rank-r reaches {all_max:.4f}, slightly above K=2 dense cap 0.385.")
        else:
            print(f"✓ Sparse rank-r caps at {all_max:.4f} ≤ 0.40 — universal 0.375 cap holds.")
    print("=" * 80)


if __name__ == '__main__':
    main()
