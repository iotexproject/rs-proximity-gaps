"""sweep_K1_gap8_certified.py — (i, i+8) family sweep with EXACT above-J certification.

Two-phase:
  Phase 1: Sample 100 random coefs per (i, i+8) pair, compute tie_upper (0.4s each).
  Phase 2: For candidates with tie_upper > 0.40, exact-verify above-J via early-exit
           info-set enumeration (1-22s each).

Outputs the certified-above-J max tie_upper per pair and overall.

Usage: python3 sweep_K1_gap8_certified.py [n_coefs=100] [seed=2026]
"""
from __future__ import annotations
import sys, os, random, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_step5_n32_studio import P, N0, K0, R, N_R, W_J, evaluate_dft
from fri_2round_attack import setup_chain
from fast_tie_robust import compute_tie_robust_fast
from exact_above_J import is_above_J_early_exit


def main():
    n_coef = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 2026
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L0 = chain[0][0]

    print(f"(i, i+8) family sweep with EXACT above-J certification")
    print(f"  p={p}, n_coef={n_coef}, seed={seed}")
    print(f"  Phase 1: random coef sweep, fast tie_upper (~0.4s/candidate)")
    print(f"  Phase 2: exact above-J verification on tie_upper > 0.40")
    print()

    rng = random.Random(seed)
    overall_max_certified = 0.0
    overall_max_info = None
    pair_results = []

    for i in range(K0, N0 - 8):
        j = i + 8
        if j >= N0:
            continue
        candidates = []  # (a, b, tie)
        t0 = time.time()
        for _ in range(n_coef):
            a = rng.randrange(1, p)
            b = rng.randrange(1, p)
            fhat = [0] * N0
            fhat[i] = a
            fhat[j] = b
            f = evaluate_dft(fhat, L0, p)
            P_B, tie, _, _, _ = compute_tie_robust_fast(f, chain, p)
            candidates.append((a, b, tie))
        # Sort by tie descending; verify the top few above 0.40
        candidates.sort(key=lambda x: -x[2])
        certified = []
        for a, b, tie in candidates:
            if tie <= 0.40:
                break
            fhat = [0] * N0
            fhat[i] = a
            fhat[j] = b
            f = evaluate_dft(fhat, L0, p)
            t_v = time.time()
            above_J, d = is_above_J_early_exit(f, L0, K0, W_J, p)
            tv = time.time() - t_v
            if above_J:
                certified.append((a, b, tie, d, tv))
        elapsed = time.time() - t0
        pair_results.append(((i, j), len(candidates), certified))
        if certified:
            certified.sort(key=lambda x: -x[2])
            best = certified[0]
            print(f"  ({i:>2},{j:>2}): {len(certified):>2} certified above-J "
                  f"| top: coefs=({best[0]:>3},{best[1]:>3}) tie={best[2]:.4f} dist={best[3]} "
                  f"({elapsed:.1f}s)")
            if best[2] > overall_max_certified:
                overall_max_certified = best[2]
                overall_max_info = ((i, j), best[0], best[1], best[2], best[3])
        else:
            top_phase1 = candidates[0]
            print(f"  ({i:>2},{j:>2}): 0 certified  | phase1 top tie={top_phase1[2]:.4f} "
                  f"(below 0.40 threshold or all FPs)  ({elapsed:.1f}s)")

    print()
    print("=" * 75)
    print("CERTIFIED-ABOVE-J SUMMARY")
    print("=" * 75)
    pairs_with_cert = [(ij, c) for ij, n, c in pair_results if c]
    print(f"  Pairs with at least 1 certified above-J + tie > 0.40: {len(pairs_with_cert)}")
    print()
    print(f"  Per-pair certified maxes (sorted desc):")
    flat = []
    for ij, _, c in pair_results:
        for a, b, tie, d, _ in c:
            flat.append((ij, a, b, tie, d))
    flat.sort(key=lambda x: -x[3])
    for ij, a, b, tie, d in flat[:10]:
        print(f"    {ij}: coefs=({a},{b}) tie={tie:.4f} dist={d}")
    print()
    if overall_max_info:
        ij, a, b, tie, d = overall_max_info
        print(f"  OVERALL CERTIFIED MAX: pair={ij} coefs=({a},{b}) tie={tie:.4f} dist={d}")
    print(f"  Compare review's K=1 leader (15,23) coefs (10,17): tie=0.4490, dist=18")


if __name__ == '__main__':
    main()
