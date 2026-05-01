"""sweep_K2_exceptional_set.py — bigger K=2 sweep to characterize |E(f)|.

Note 0126 found 7 K=2 above-J f's with |E(f)| ∈ {1, 7}. Most cases give 1; only
(18, 8) ov=1 gives 7. We want to:
  1. Find more K=2 cases with |E(f)| > 1 (look for patterns)
  2. Verify all stay ≤ small constant (supporting Conjecture sharpened FRI)
  3. Identify algebraic features of high-|E(f)| cases

Approach: random K=2 construction (same as note 0117 K2 audit), 100+ samples,
exact above-J via fast decoder + exact verifier.

Usage: python3 sweep_K2_exceptional_set.py [n_pairs=50] [n_per_pair=10] [seed=2026]
"""
from __future__ import annotations
import sys, os, random, time
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_step5_n32_studio import P, N0, K0, R, N_R, W_J, evaluate_dft
from fri_2round_attack import setup_chain, parity_check, matvec, gauss_rank
from probe_K2_construct import construct_f_with_psi_in_U
from fast_tie_robust import compute_tie_robust_fast
from exact_above_J import is_above_J_early_exit


W_R = 3


def gen_K2_pair_above_J(rng, p, chain, H_R, attempts_per_pair=10):
    """Generate one above-J K=2 f using random T1, T2 supports."""
    L0 = chain[0][0]
    n_R = N_R
    for _ in range(50):  # try multiple T-pair configs
        T1 = tuple(sorted(rng.sample(range(n_R), W_R)))
        overlap = rng.choice([0, 1])
        if overlap == 0:
            avail = [j for j in range(n_R) if j not in T1]
            if len(avail) < W_R: continue
            T2 = tuple(sorted(rng.sample(avail, W_R)))
        else:
            shared = rng.choice(list(T1))
            others = [j for j in range(n_R) if j not in T1]
            if len(others) < W_R - 1: continue
            T2 = tuple(sorted([shared] + rng.sample(others, W_R - 1)))
        if T2 == T1: continue
        ov_size = len(set(T1) & set(T2))
        if ov_size > 1: continue

        eps1 = [0] * n_R
        eps2 = [0] * n_R
        for j in T1: eps1[j] = rng.randrange(1, p)
        for j in T2: eps2[j] = rng.randrange(1, p)
        u1 = matvec(H_R, eps1, p)
        u2 = matvec(H_R, eps2, p)
        if gauss_rank([u1, u2], p) != 2: continue

        for _ in range(attempts_per_pair):
            c = {b: (rng.randrange(p), rng.randrange(p)) for b in product([0,1], repeat=R)}
            msg = [rng.randrange(p) for _ in range(K0)]
            fhat = construct_f_with_psi_in_U(u1, u2, c, msg, p)
            f = evaluate_dft(fhat, L0, p)
            above_J, d = is_above_J_early_exit(f, L0, K0, W_J, p)
            if above_J:
                return f, T1, T2, ov_size
    return None, None, None, None


def main():
    n_pairs = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    n_per_pair = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 2026
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, p)

    print(f"K=2 exceptional set characterization at p={p}")
    print(f"  Goal: find K=2 above-J cases, characterize |E(f)| = #{{α_1 : d_1 ≤ δn_1=8}}")
    print(f"  Reference: K=2 (18,8) ov=1 has |E(f)| = 7 (the empirical max)")
    print()

    rng = random.Random(seed)
    cases = []
    n_attempts = 0
    t0 = time.time()
    while len(cases) < n_pairs and n_attempts < n_pairs * 5:
        n_attempts += 1
        f, T1, T2, ov = gen_K2_pair_above_J(rng, p, chain, H_R, attempts_per_pair=n_per_pair)
        if f is None:
            continue
        # Compute tie + d_1 distribution
        P_B, tie, d1d, d2d, jd = compute_tie_robust_fast(f, chain, p)
        n_low = sum(c for d, c in d1d.items() if d <= 8)
        cases.append((T1, T2, ov, P_B, tie, n_low, sorted(d1d.items())))
        marker = " ★" if n_low >= 5 else ""
        if len(cases) <= 10 or len(cases) % 10 == 0 or n_low >= 5:
            print(f"  [{len(cases)}/{n_pairs}] T1={T1} T2={T2} ov={ov} "
                  f"tie={tie:.4f} #(d_1≤8)={n_low}{marker}")

    print()
    print(f"  Total above-J K=2 cases found: {len(cases)} (in {n_attempts} attempts, "
          f"{time.time()-t0:.0f}s)")
    print()

    print("=" * 75)
    print("EXCEPTIONAL SET DISTRIBUTION")
    print("=" * 75)
    n_low_dist = {}
    for *_, n_low, _ in cases:
        n_low_dist[n_low] = n_low_dist.get(n_low, 0) + 1
    for n_low in sorted(n_low_dist):
        print(f"  |E(f)| = {n_low}: {n_low_dist[n_low]} cases")
    print()
    max_low = max(c[5] for c in cases)
    print(f"  MAX |E(f)| across {len(cases)} K=2 above-J cases: {max_low}")
    if max_low <= 7:
        print(f"  ✓ Conjecture #(d_1 ≤ 8) ≤ O(R) supported (max = {max_low} ≤ 7 = empirical bound)")
    else:
        print(f"  ⚠ NEW MAX: {max_low} exceeds prior empirical bound of 7")

    # Show top 5 high-|E(f)| cases
    print()
    print(f"  TOP 5 cases by |E(f)|:")
    cases_sorted = sorted(cases, key=lambda c: -c[5])
    for T1, T2, ov, PB, tie, n_low, d1d in cases_sorted[:5]:
        print(f"    T1={T1} T2={T2} ov={ov} #(d_1≤8)={n_low} tie={tie:.4f} d_1: {d1d}")


if __name__ == '__main__':
    main()
