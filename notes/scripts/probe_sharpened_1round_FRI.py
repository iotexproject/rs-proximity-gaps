"""probe_sharpened_1round_FRI.py — verify sharpened 1-round FRI soundness empirically.

Conjecture (note 0125): For ANY above-J f at our params, #{α_1 : d_1(α_1) ≤ δn_1=8} ≤ O(R).

If true: tie_upper(f) ≤ 1-δ + O(R/q) for ALL above-J f.

Standard BCIKS gives Pr ≤ 1 - δ/2 (much weaker, allows up to (1-δ/2)q ≈ 73 α_1's).

Test: for each of 30 random above-J f's (mix of K=1, K=2, sparse), compute d_1 distribution
across all 97 α_1 and count #{d_1 ≤ 8}.

If max count ≤ small constant: conjecture supported.
If max count grows: conjecture has counter-example.

Usage: python3 probe_sharpened_1round_FRI.py [n_samples=30] [seed=2026]
"""
from __future__ import annotations
import sys, os, random, time
from itertools import combinations

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


def compute_d1_count_low(f, chain, p, threshold=8):
    """Return count of α_1 with d_1(α_1) ≤ threshold. Fast: max_w cap."""
    L0, _, _ = chain[0]
    L1, k1, H1 = chain[1]
    n1 = len(L1)
    f_e, f_o = even_odd_parts(f, L0, p)
    n_low = 0
    d1_low_dist = {}  # only track d_1 ≤ threshold
    for a1 in range(p):
        fold1 = [(f_e[j] + a1 * f_o[j]) % p for j in range(n1)]
        d1, _ = dist_to_code_full(fold1, H1, n1, k1, p, max_w=threshold)
        if d1 is not None:
            n_low += 1
            d1_low_dist[d1] = d1_low_dist.get(d1, 0) + 1
    return n_low, d1_low_dist


def gen_random_above_J_f(rng, p, K0, N0, L0, W_J, n_pos_choices=(2, 3, 4, 5)):
    """Generate one random above-J sparse f."""
    while True:
        n_pos = rng.choice(n_pos_choices)
        positions = tuple(sorted(rng.sample(range(K0, N0), n_pos)))
        coefs = tuple(rng.randrange(1, p) for _ in range(n_pos))
        fhat = [0] * N0
        for pos, c in zip(positions, coefs):
            fhat[pos] = c
        f = evaluate_dft(fhat, L0, p)
        d_lb = dist_lower_bound_sampling(f, L0, K0, p, n_samples=10000, batch=4096, seed=rng.randrange(10**9))
        if d_lb > W_J:
            return f, positions, coefs


def main():
    n_samples = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 2026
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, p)
    m = N_R - k_R

    print(f"Sharpened 1-round FRI conjecture probe at p={p}")
    print(f"  Conjecture: above-J f ⟹ #{{α_1: d_1 ≤ δn_1=8}} ≤ O(R) = O(2)")
    print(f"  Standard BCIKS: only Pr[d_1 ≤ 8] ≤ 1-δ/2 = 3/4 (allows up to {3*p//4} α_1's)")
    print(f"  Conjecture target: ≤ small constant for ALL above-J f")
    print()

    rng = random.Random(seed)
    results = []
    rank_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for i in range(n_samples):
        f, positions, coefs = gen_random_above_J_f(rng, p, K0, N0, L0, W_J)
        # Determine rank/K
        corner_syns = compute_corner_syndromes(f, chain, R, p, H_R)
        rank, _, _, _ = image_rank_and_mu(corner_syns, R, p, m)
        # Fast: only count #(d_1 ≤ 8)
        t0 = time.time()
        n_low, d1_low_dist = compute_d1_count_low(f, chain, p, threshold=8)
        elapsed = time.time() - t0
        rank_counts[rank] = rank_counts.get(rank, 0) + 1
        results.append((rank, positions, coefs, n_low, d1_low_dist))
        print(f"  {i+1}/{n_samples}: rank={rank} pos={positions[:4]}{'...' if len(positions)>4 else ''} "
              f"#d_1≤8={n_low} dist_low={dict(sorted(d1_low_dist.items()))}  ({elapsed:.0f}s)", flush=True)

    print()
    print("=" * 75)
    print(f"SUMMARY: {n_samples} above-J random f's")
    print("=" * 75)
    print(f"  Rank distribution: {dict(sorted(rank_counts.items()))}")
    print()
    n_lows = [r[3] for r in results]
    print(f"  #(d_1 ≤ 8) — distribution across samples:")
    print(f"    min: {min(n_lows)}, max: {max(n_lows)}, mean: {sum(n_lows)/len(n_lows):.2f}")
    print()
    if max(n_lows) <= 5:
        print(f"  ✓ Conjecture STRONGLY supported: max #(d_1 ≤ 8) = {max(n_lows)} ≤ 5 = O(R)")
    elif max(n_lows) <= 20:
        print(f"  ◎ Conjecture supported: max #(d_1 ≤ 8) = {max(n_lows)} ≤ 20")
    else:
        print(f"  ⚠ Conjecture VIOLATED: max #(d_1 ≤ 8) = {max(n_lows)} > 20")


if __name__ == '__main__':
    main()
