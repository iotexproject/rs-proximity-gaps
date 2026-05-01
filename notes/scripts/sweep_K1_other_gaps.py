"""sweep_K1_other_gaps.py — explore K=1 (i, i+gap) families beyond gap 8.

Algebraic intuition (n_0=32, R=2):
  - gap 8:  fold_1 keeps modes apart (8 mod 16), fold_2 collapses (8 mod 8 = 0)
  - gap 16: fold_1 collapses (16 mod 16 = 0)
  - gap 4:  fold_1 differs by 4, fold_2 differs by 4
  - gap 12: fold_1 differs by 12, fold_2 differs by 4

Tests: gap ∈ {4, 12, 16}, 50 random coefs each + exact above-J certify.

Expected: gap 16 should also have algebraic resonance (collapses at level 1).

Usage: python3 sweep_K1_other_gaps.py [n_coefs=50] [seed=2026]
"""
from __future__ import annotations
import sys, os, random, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_step5_n32_studio import P, N0, K0, R, N_R, W_J, evaluate_dft
from fri_2round_attack import setup_chain
from fast_tie_robust import compute_tie_robust_fast
from exact_above_J import is_above_J_early_exit


def sweep_gap(gap, n_coef, rng, p, chain, L0, threshold=0.40):
    """Sweep one gap value, exact-verify above 0.40, return (overall_max_certified, max_info, n_certified)."""
    overall_max = 0.0
    overall_info = None
    n_cert = 0
    for i in range(K0, N0 - gap):
        j = i + gap
        if j >= N0:
            continue
        candidates = []
        for _ in range(n_coef):
            a = rng.randrange(1, p)
            b = rng.randrange(1, p)
            fhat = [0] * N0
            fhat[i] = a
            fhat[j] = b
            f = evaluate_dft(fhat, L0, p)
            P_B, tie, _, _, _ = compute_tie_robust_fast(f, chain, p)
            candidates.append((a, b, tie))
        candidates.sort(key=lambda x: -x[2])
        for a, b, tie in candidates:
            if tie <= threshold:
                break
            fhat = [0] * N0
            fhat[i] = a
            fhat[j] = b
            f = evaluate_dft(fhat, L0, p)
            above_J, d = is_above_J_early_exit(f, L0, K0, W_J, p)
            if above_J:
                n_cert += 1
                if tie > overall_max:
                    overall_max = tie
                    overall_info = ((i, j), a, b, tie, d)
    return overall_max, overall_info, n_cert


def main():
    n_coef = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 2026
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L0 = chain[0][0]

    print(f"Other gap families sweep at p={p}")
    print(f"  Comparing tie_upper across (i, i+gap) for gap ∈ {{4, 12, 16}}")
    print(f"  Reference: gap 8 max = 0.4490 (K=1 leader (15,23) coefs (10,17))")
    print()

    rng = random.Random(seed)
    results = []
    for gap in [4, 12, 16]:
        t0 = time.time()
        max_t, info, n_cert = sweep_gap(gap, n_coef, rng, p, chain, L0)
        elapsed = time.time() - t0
        results.append((gap, max_t, info, n_cert))
        if info:
            ij, a, b, tie, d = info
            print(f"  gap={gap:>2}: {n_cert} certified above-J, max tie={max_t:.4f} "
                  f"(pair={ij}, coefs=({a},{b}), dist={d})  ({elapsed:.0f}s)")
        else:
            print(f"  gap={gap:>2}: 0 certified above-J  ({elapsed:.0f}s)")

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  gap   max_tie  pair      coefs      dist")
    for gap, mt, info, _ in results:
        if info:
            ij, a, b, _, d = info
            print(f"  {gap:>3}    {mt:.4f}  {ij}  ({a:>3},{b:>3})  {d}")
    print(f"  ref 8: 0.4490  (15,23)   ( 10, 17)   18")
    overall_max = max(r[1] for r in results)
    print()
    if overall_max > 0.4490:
        print(f"  ⚠ NEW MAX from other gaps: {overall_max:.4f} > gap-8 max 0.4490")
    else:
        print(f"  ✓ No other gap family beats gap-8 max 0.4490")


if __name__ == '__main__':
    main()
