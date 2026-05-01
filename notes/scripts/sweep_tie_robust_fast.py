"""sweep_tie_robust_fast.py — broad above-J sweep with fast tie_robust_upper.

With ~0.4s per candidate (review's fast decoder), we can audit 200+ above-J f's
in ~2 min total. Tests whether the K=1 leader's 0.4490 is truly universal.

Mix:
  - 50 random K=1 sparse (2-position above-J)
  - 50 random K=2 sparse (3-position)
  - 50 random K=3+ sparse (4-5 position)
  - Specific test: K=2 dense 24-pos (review note 0114)

Reports max tie_upper across all and any candidates beating 0.449.

Usage: python3 sweep_tie_robust_fast.py [n_per_class=50] [seed=2026]
"""
from __future__ import annotations
import sys, os, random, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_step5_n32_studio import P, N0, K0, R, N_R, W_J, evaluate_dft
from fri_2round_attack import setup_chain
from mds_decoder import dist_lower_bound_sampling
from fast_tie_robust import compute_tie_robust_fast


def gen_above_J(rng, p, L0, n_pos, max_tries=50):
    """Generate one random above-J sparse f with n_pos nonzero positions in [K_0, N_0)."""
    for _ in range(max_tries):
        positions = tuple(sorted(rng.sample(range(K0, N0), n_pos)))
        coefs = tuple(rng.randrange(1, p) for _ in range(n_pos))
        fhat = [0] * N0
        for pos, c in zip(positions, coefs):
            fhat[pos] = c
        f = evaluate_dft(fhat, L0, p)
        d_lb = dist_lower_bound_sampling(f, L0, K0, p, n_samples=2000, batch=2048,
                                          seed=rng.randrange(10**9))
        if d_lb > W_J:
            return f, positions, coefs
    return None, None, None


def main():
    n_per_class = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 2026
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L0 = chain[0][0]

    print(f"Broad above-J sweep with fast tie_robust_upper")
    print(f"  p={p}, n_0={N0}, w_J={W_J}, n_per_class={n_per_class}, seed={seed}")
    print(f"  Universal cap to beat: 0.4490 (K=1 leader (15,23) coefs (10,17))")
    print()

    rng = random.Random(seed)
    results = []  # (class, positions, coefs, P_B, tie)

    classes = [
        ("K=1 sparse (2-pos)", 2),
        ("K=2 sparse (3-pos)", 3),
        ("rank-3 sparse (4-pos)", 4),
        ("rank-3 sparse (5-pos)", 5),
    ]

    for cls_name, n_pos in classes:
        print(f"--- {cls_name}: {n_per_class} samples ---")
        n_done = 0
        n_fail = 0
        cls_max = 0.0
        cls_max_info = None
        t_class = time.time()
        while n_done < n_per_class:
            f, positions, coefs = gen_above_J(rng, p, L0, n_pos)
            if f is None:
                n_fail += 1
                if n_fail > n_per_class * 5:
                    print(f"  too many failures, breaking after {n_done}")
                    break
                continue
            P_B, tie, _, _, _ = compute_tie_robust_fast(f, chain, p)
            results.append((cls_name, positions, coefs, P_B, tie))
            if tie > cls_max:
                cls_max = tie
                cls_max_info = (positions, coefs, P_B, tie)
            n_done += 1
            if n_done <= 5 or n_done % 10 == 0:
                print(f"  [{n_done}/{n_per_class}] pos={positions} P_B={P_B:.4f} tie={tie:.4f}")
        if cls_max_info:
            pos, c, pb, t = cls_max_info
            print(f"  CLASS MAX: pos={pos} coefs={c} P_B={pb:.4f} tie={t:.4f}")
        print(f"  ({time.time()-t_class:.1f}s for class)")
        print()

    # K=2 dense 24-pos (from review note 0114)
    print("--- K=2 dense 24-pos (review note 0114) ---")
    FHAT_NONZERO_K2_DENSE = [
        (8, 85), (9, 73), (10, 61), (11, 25), (12, 53), (13, 9),
        (14, 62), (15, 80), (16, 21), (17, 42), (18, 63), (19, 22),
        (20, 4), (21, 8), (22, 12), (23, 91), (24, 63), (25, 29),
        (26, 92), (27, 13), (28, 6), (29, 12), (30, 18), (31, 89),
    ]
    fhat = [0] * N0
    for idx, val in FHAT_NONZERO_K2_DENSE:
        fhat[idx] = val
    f = evaluate_dft(fhat, L0, p)
    P_B, tie, _, _, _ = compute_tie_robust_fast(f, chain, p)
    results.append(("K=2 dense 24-pos", "ALL", "from-review", P_B, tie))
    print(f"  P_B={P_B:.4f} tie={tie:.4f}")
    print()

    # K=1 leader (15,23) coefs (10,17) — known max
    print("--- K=1 leader (15,23) coefs (10,17) — known max 0.449 ---")
    fhat = [0] * N0
    fhat[15] = 10
    fhat[23] = 17
    f = evaluate_dft(fhat, L0, p)
    P_B, tie, _, _, _ = compute_tie_robust_fast(f, chain, p)
    results.append(("K=1 leader", (15, 23), (10, 17), P_B, tie))
    print(f"  P_B={P_B:.4f} tie={tie:.4f}")
    print()

    # Summary
    print("=" * 75)
    print("SUMMARY")
    print("=" * 75)
    cls_summary = {}
    for cls, _, _, pb, tie in results:
        cls_summary.setdefault(cls, []).append((pb, tie))
    for cls in sorted(cls_summary):
        ts = [t for _, t in cls_summary[cls]]
        pbs = [p for p, _ in cls_summary[cls]]
        print(f"  {cls:<28}: n={len(ts)}, max_tie={max(ts):.4f}, max_PB={max(pbs):.4f}")
    print()
    overall_max = max(t for _, _, _, _, t in results)
    print(f"  OVERALL MAX tie_upper = {overall_max:.4f}")
    breakers = [(c, p, co, pb, t) for c, p, co, pb, t in results if t > 0.4490]
    if breakers:
        print(f"  ⚠ {len(breakers)} candidates beat the 0.449 cap:")
        for c, p, co, pb, t in breakers:
            print(f"    {c}: pos={p} coefs={co} tie={t:.4f}")
    else:
        print(f"  ✓ NO candidate beats 0.4490 — K=1 leader remains universal")


if __name__ == '__main__':
    main()
