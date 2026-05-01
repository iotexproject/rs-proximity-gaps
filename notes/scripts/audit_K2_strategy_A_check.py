"""audit_K2_strategy_A_check.py — does Strategy A ever beat Strategy B for our K=2 breaches?

The 0115 audit used Strategy B only (cheat-at-last), getting P_avg ≤ 0.385.
But the optimal cheater uses max(P_A, P_B). If Strategy A pushes P_avg higher, our
Bezout prediction needs revision.

Strategy A: closest codeword at every level.
  P_A(α₁, α₂) = (1/n_1) #{j ∈ [n_1] : j ∈ S_1(α_1) ∧ j² mod n_2 ∈ S_2(α)}

For Strategy A to beat Strategy B at d_2 = 5 (the dominant case): need
|S_1|/n_1 · |S_2|/n_2 > 1 - d_2/n_2 = 0.375 with |S_2|/n_2 = 0.375
⇒ need |S_1|/n_1 > 1, impossible. So Strategy A only matters when:
  - d_2 < 5 (then S_2 large enough that A can compete), OR
  - d_1 = 0 (fold_1 IS a codeword — possible for K=2 if γ_1(α_1)=γ_2(α_1)=0 for some α_1)

This script samples 1 of the 7 K=2 breaches and computes P_avg with max(A, B) vs B-only.

Expected: for K=2 above-J f, fold_1 generically above-J at level 1, so S_1 small, P_A
small. Strategy B dominates in 99%+ of α. P_avg_AB ≲ 1.05 · P_avg_B.
"""
from __future__ import annotations
import sys, os, random, time
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import (
    setup_chain, parity_check, matvec, gauss_rank,
    even_odd_parts, dist_to_code_full,
)
from probe_step5_n32_studio import (
    P, N0, K0, R, N_R, W_J, evaluate_dft, compute_corner_syndromes,
)
from probe_K2_construct import construct_f_with_psi_in_U


W_R = 3


def reproduce_first_breach(seed=4242):
    """Reproduce just one (the first) K=2 breach, deterministically."""
    rng = random.Random(seed)
    chain = setup_chain(P, N0, K0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, P)
    p, n_R, w_R = P, N_R, W_R
    breach_keys = {(1, 5), (2, 8), (4, 2), (8, 0), (18, 8), (25, 3), (25, 6)}

    for pair_idx in range(30):
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
        if len(set(T1) & set(T2)) > 1:
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
        for f_idx in range(10):
            c = {b: (rng.randrange(p), rng.randrange(p)) for b in product([0, 1], repeat=R)}
            msg = [rng.randrange(p) for _ in range(K0)]
            fhat = construct_f_with_psi_in_U(u1, u2, c, msg, p)
            f = evaluate_dft(fhat, L0, p)
            if (pair_idx, f_idx) in breach_keys:
                return f, chain, pair_idx, f_idx, T1, T2
    return None, None, None, None, None, None


def main():
    print("Reproducing K=2 breach #0 (pair=1, f=5)...")
    f, chain, pair_idx, f_idx, T1, T2 = reproduce_first_breach()
    print(f"Got breach: pair={pair_idx}, f={f_idx}, T1={T1}, T2={T2}")
    p = P
    L0, k0_, H0 = chain[0]
    L1, k1, H1 = chain[1]
    L2, k2, H2 = chain[2]
    n1, n2 = len(L1), len(L2)
    sq_idx = [j % n2 for j in range(n1)]

    f_e, f_o = even_odd_parts(f, L0, p)
    print(f"\nFull {p}×{p} = {p*p} α-pairs, computing P_A and P_B per pair...")
    print(f"Strategy A: round-1 cheat-at-not-last (closest cw at every level)")
    print(f"Strategy B: cheat-at-last (only g_R must be RS-cw)")

    t0 = time.time()
    sum_P_B = 0.0
    sum_P_max = 0.0
    sum_P_A = 0.0
    n_A_wins = 0  # count α where P_A > P_B
    d1_dist = {}
    d2_dist = {}
    for a1 in range(p):
        fold1 = [(f_e[j] + a1 * f_o[j]) % p for j in range(n1)]
        d1, S1 = dist_to_code_full(fold1, H1, n1, k1, p)
        if d1 is None:
            d1 = n1
            S1 = []
        d1_dist[d1] = d1_dist.get(d1, 0) + 1
        S1_set = set(S1)
        g_e, g_o = even_odd_parts(fold1, L1, p)
        for a2 in range(p):
            fold2 = [(g_e[j] + a2 * g_o[j]) % p for j in range(n2)]
            d2, S2 = dist_to_code_full(fold2, H2, n2, k2, p)
            if d2 is None:
                d2 = n2
                S2 = []
            S2_set = set(S2)
            d2_dist[d2] = d2_dist.get(d2, 0) + 1
            count = sum(1 for j in range(n1) if j in S1_set and sq_idx[j] in S2_set)
            P_A = count / n1
            P_B = 1.0 - d2 / n2
            P_max = max(P_A, P_B)
            sum_P_A += P_A
            sum_P_B += P_B
            sum_P_max += P_max
            if P_A > P_B + 1e-9:
                n_A_wins += 1

    n_pairs = p * p
    P_avg_A = sum_P_A / n_pairs
    P_avg_B = sum_P_B / n_pairs
    P_avg_AB = sum_P_max / n_pairs

    print(f"\nDone in {time.time()-t0:.0f}s.")
    print()
    print(f"Strategy A (closest cw): P_avg_A = {P_avg_A:.4f}")
    print(f"Strategy B (cheat-at-last): P_avg_B = {P_avg_B:.4f}")
    print(f"max(A, B) — optimal cheater: P_avg_AB = {P_avg_AB:.4f}")
    print()
    print(f"Δ from B-only (the 0115 audit): {P_avg_AB - P_avg_B:+.4f}")
    print(f"  → at p=97 ratio: {(P_avg_AB - P_avg_B) / P_avg_B * 100:.2f}%")
    print()
    print(f"# α where P_A > P_B: {n_A_wins} / {n_pairs} = {100*n_A_wins/n_pairs:.2f}%")
    print()
    print(f"d_1 distribution (round-1 distance to RS_4 in F_p^16):")
    for d in sorted(d1_dist.keys()):
        c = d1_dist[d]
        print(f"  d_1 = {d:>2}: {c:>4} α_1 ({100*c/p:5.2f}%)  → |S_1|/n_1 = {1-d/n1:.4f}")
    print()
    if P_avg_AB - P_avg_B > 0.05:
        print("⚠ Strategy A matters significantly. 0115 P_avg is an UNDER-estimate by >5%.")
        print("  Need to revise Bezout prediction in note 0116.")
    elif P_avg_AB - P_avg_B > 0.01:
        print("◎ Strategy A adds <5% but nonzero correction.")
    else:
        print("✓ Strategy B dominates everywhere (≤1% correction). 0115 audit stands.")


if __name__ == '__main__':
    main()
