"""scan_K1_max_s_star.py — find max s*(f) across K=1 above-J 2-frequency f's.

For each support (i, j) with K_0 ≤ i < j < N_0 (276 cases):
  Try a few coefficient ratios (deterministic).
  For each above-J K=1 f: compute s*(f) via 30-α probe.
  Track max s*.

If max s*(f) = 7 across all K=1: confirms Lemma 2 is TIGHT for K=1.
If max s*(f) > 7: counter-example to Lemma 2 — would contradict above-J.

Then for the s*=7 cases: compute full tie_upper.

Usage: python3 scan_K1_max_s_star.py [n_ratios=5] [seed=2026]
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


def quick_s_star(f, chain, p, n_alpha=3, max_d=9):
    """Quick s* estimate: take min support size of fold_1 - c across n_alpha α_1's.
    Use max_d=9 as cap (s*≥7 means d_1 ≤ 9). If d_1 > max_d for any α_1, return s*=0."""
    L0, _, _ = chain[0]
    L1, k1, H1 = chain[1]
    n1 = len(L1)
    f_e, f_o = even_odd_parts(f, L0, p)
    # Use first n_alpha α_1's (1, 2, 3) — deterministic
    min_T_size = n1
    for a1 in range(1, n_alpha + 1):
        fold1 = [(f_e[j] + a1 * f_o[j]) % p for j in range(n1)]
        d1, S1 = dist_to_code_full(fold1, H1, n1, k1, p, max_w=max_d)
        if d1 is None:
            # d_1 > max_d, so s* < n1 - max_d = 16 - 9 = 7
            return 0, None
        T = frozenset(j for j in range(n1) if j not in set(S1))
        if len(T) < min_T_size:
            min_T_size = len(T)
    s_star = n1 - min_T_size
    return s_star, None


def compute_full_tie_upper(f, chain, p):
    L0, _, _ = chain[0]
    L1, k1, H1 = chain[1]
    L2, k2, H2 = chain[2]
    n1, n2 = len(L1), len(L2)
    f_e, f_o = even_odd_parts(f, L0, p)
    sum_PB, sum_tie = 0.0, 0.0
    for a1 in range(p):
        fold1 = [(f_e[j] + a1 * f_o[j]) % p for j in range(n1)]
        d1, _ = dist_to_code_full(fold1, H1, n1, k1, p)
        if d1 is None:
            d1 = n1
        g_e, g_o = even_odd_parts(fold1, L1, p)
        for a2 in range(p):
            fold2 = [(g_e[j] + a2 * g_o[j]) % p for j in range(n2)]
            d2, _ = dist_to_code_full(fold2, H2, n2, k2, p)
            if d2 is None:
                d2 = n2
            P_B = 1.0 - d2 / n2
            P_A_ub = 1.0 - d1 / n1
            sum_PB += P_B
            sum_tie += max(P_A_ub, P_B)
    n_pairs = p * p
    return sum_PB / n_pairs, sum_tie / n_pairs


def main():
    n_ratios = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 2026
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, p)
    m = N_R - k_R

    print(f"K=1 max s*(f) scan at p={p}, n_1={N0//2}=16")
    print(f"  Lemma 2 prediction: above-J ⟹ s*(f) ≤ 7")
    print(f"  Counter-example would be: K=1 above-J f with s*(f) > 7")
    print()

    # Try all (i, j) with K_0 ≤ i < j < N_0 = 32. = C(24, 2) = 276 supports.
    rng = random.Random(seed)
    s_star_dist = {}
    s_star_7_cases = []
    n_above_J = 0
    n_K1 = 0
    n_total = 0
    t_start = time.time()
    for positions in combinations(range(K0, N0), 2):
        for ratio_idx in range(n_ratios):
            n_total += 1
            # Random coefs (deterministic from seed)
            coefs = (rng.randrange(1, p), rng.randrange(1, p))
            fhat = [0] * N0
            for pos, c in zip(positions, coefs):
                fhat[pos] = c
            f = evaluate_dft(fhat, L0, p)
            d_lb = dist_lower_bound_sampling(f, L0, K0, p, n_samples=5000, batch=4096, seed=seed + n_total)
            if d_lb <= W_J:
                continue
            n_above_J += 1
            corner_syns = compute_corner_syndromes(f, chain, R, p, H_R)
            rank, _, _, _ = image_rank_and_mu(corner_syns, R, p, m)
            if rank != 1:
                continue
            n_K1 += 1
            s_star_min, _ = quick_s_star(f, chain, p, n_alpha=3, max_d=9)
            s_star_dist[s_star_min] = s_star_dist.get(s_star_min, 0) + 1
            if s_star_min >= 7:
                s_star_7_cases.append((positions, coefs, s_star_min, None, None))
                print(f"  s*={s_star_min}: positions={positions} coefs={coefs}", flush=True)
        if n_total % 25 == 0:
            elapsed_so_far = time.time() - t_start
            print(f"  ... {n_total}/{276*n_ratios} ({elapsed_so_far:.0f}s), {n_above_J} above-J, {n_K1} K=1, s*_dist={dict(sorted(s_star_dist.items()))}", flush=True)

    elapsed = time.time() - t_start
    print()
    print("=" * 75)
    print(f"K=1 max s* scan complete in {elapsed:.0f}s")
    print(f"  Total tries: {n_total}, above-J: {n_above_J}, K=1: {n_K1}")
    print(f"  s*(f) distribution: {dict(sorted(s_star_dist.items()))}")
    print()
    if s_star_dist:
        max_s_star = max(s_star_dist.keys())
        print(f"  MAX s*(f) observed: {max_s_star}")
        if max_s_star <= 7:
            print(f"  ✓ Lemma 2 holds: s*(f) ≤ 7 for all K=1 above-J f tested")
        else:
            print(f"  ⚠ Lemma 2 VIOLATED: s*(f) = {max_s_star} > 7")
    print()
    if s_star_7_cases:
        print(f"  K=1 with s*=7 cases: {len(s_star_7_cases)}")
        print(f"  Computing full tie_upper for first 3...")
        for positions, coefs, s_star, s_int, T in s_star_7_cases[:3]:
            t0 = time.time()
            fhat = [0] * N0
            for pos, c in zip(positions, coefs):
                fhat[pos] = c
            f = evaluate_dft(fhat, L0, p)
            P_B, tie = compute_full_tie_upper(f, chain, p)
            print(f"    positions={positions} coefs={coefs} s*={s_star}: P_B={P_B:.4f} tie_upper={tie:.4f} ({time.time()-t0:.0f}s)", flush=True)


if __name__ == '__main__':
    main()
