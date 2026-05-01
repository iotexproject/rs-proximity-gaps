"""sweep_K1_gap8_family.py — exhaustive coef sweep over (i, i+8) family.

Note 0123 characterized K=1 worst-case as (i, i+8) gap-8 pairs.
Note 0127 confirmed (15,23) coefs (10,17) gives tie_upper = 0.4490.

This script enumerates ALL (i, i+8) pairs with i ∈ [8, 24) and samples
random (a, b) coefs to find the MAX tie_upper across the algebraic family.

Goal: confirm 0.449 is the family max (no (i,j,a,b) beats it).

Usage: python3 sweep_K1_gap8_family.py [n_coef_samples=200] [seed=2026]
"""
from __future__ import annotations
import sys, os, random, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_step5_n32_studio import P, N0, K0, R, N_R, W_J, evaluate_dft
from fri_2round_attack import setup_chain
from mds_decoder import dist_lower_bound_sampling
from fast_tie_robust import compute_tie_robust_fast


def main():
    n_coef = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 2026
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L0 = chain[0][0]

    print(f"Exhaustive (i, i+8) family sweep at p={p}")
    print(f"  i ∈ [{K0}, {N0-8}), n_coef_samples per (i,j) = {n_coef}")
    print(f"  Compare: K=1 leader (15,23)/(10,17) → tie_upper = 0.4490")
    print()

    rng = random.Random(seed)
    overall_max = 0.0
    overall_max_info = None
    pair_records = []

    for i in range(K0, N0 - 8):
        j = i + 8
        if j >= N0:
            continue
        pair_max = 0.0
        pair_max_info = None
        n_above_J = 0
        t0 = time.time()
        for _ in range(n_coef):
            a = rng.randrange(1, p)
            b = rng.randrange(1, p)
            fhat = [0] * N0
            fhat[i] = a
            fhat[j] = b
            f = evaluate_dft(fhat, L0, p)
            d_lb = dist_lower_bound_sampling(f, L0, K0, p, n_samples=2000, batch=2048,
                                              seed=rng.randrange(10**9))
            if d_lb <= W_J:
                continue
            n_above_J += 1
            P_B, tie, _, _, _ = compute_tie_robust_fast(f, chain, p)
            if tie > pair_max:
                pair_max = tie
                pair_max_info = (a, b, P_B, tie)
            if tie > overall_max:
                overall_max = tie
                overall_max_info = ((i, j), a, b, P_B, tie)
        elapsed = time.time() - t0
        pair_records.append(((i, j), n_above_J, pair_max, pair_max_info))
        if pair_max_info:
            a, b, pb, t = pair_max_info
            print(f"  ({i:>2},{j:>2}): {n_above_J:>3}/{n_coef} above-J | max coefs=({a:>3},{b:>3}) "
                  f"P_B={pb:.4f} tie={t:.4f}  ({elapsed:.0f}s)")
        else:
            print(f"  ({i:>2},{j:>2}): 0 above-J found  ({elapsed:.0f}s)")

    print()
    print("=" * 75)
    print("SUMMARY")
    print("=" * 75)
    n_above_J_total = sum(r[1] for r in pair_records)
    print(f"  Total above-J samples across {len(pair_records)} (i,j) pairs: {n_above_J_total}")
    print()
    print(f"  Per-pair maxes (sorted desc):")
    for (i, j), n_aJ, pmax, info in sorted(pair_records, key=lambda r: -r[2])[:10]:
        if info:
            a, b, pb, t = info
            print(f"    ({i:>2},{j:>2}): max tie={pmax:.4f} (coefs=({a},{b}))")
    print()
    if overall_max_info:
        ij, a, b, pb, t = overall_max_info
        print(f"  OVERALL MAX: pair={ij} coefs=({a},{b}) P_B={pb:.4f} tie={t:.4f}")
    if overall_max > 0.4490:
        print(f"  ⚠ NEW MAX beats K=1 leader 0.4490 by {overall_max - 0.4490:.4f}")
    else:
        print(f"  ✓ K=1 leader 0.4490 remains family max")


if __name__ == '__main__':
    main()
