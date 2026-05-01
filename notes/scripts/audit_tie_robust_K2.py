"""audit_tie_robust_K2.py — tie-robust upper for K=2 dense breaches only.

The (a) validation in audit_tie_robust_upper.py confirmed tie_upper = 0.449
for the rank-1 leader (15,23) coefs (10,17). This script focuses on K=2 dense:
does K=2 dense (P_B = 0.385) reach tie_upper > 0.449?

Two competing forces:
  - K=2 has HIGHER P_B (0.385 vs K=1's 0.265) → larger contribution from d_2 side
  - K=2 has LARGER d_1 (typically 10-11) → smaller P_A_ub (≤ 0.375)

If K=2 d_1 mostly = 10-11, then for "bulk" α_1: P_A_ub ≤ 0.375 = P_B(d_2=5),
so max(P_A, P_B) = P_B and tie_upper ≈ P_B = 0.385.

If K=2 has a "stable level-1" α_1 with d_1 = 6 or smaller (P_A_ub ≥ 0.625),
then those α_1's contribute more to tie_upper.

Usage: python3 audit_tie_robust_K2.py
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
    P, N0, K0, R, N_R, W_J, evaluate_dft,
)
from probe_K2_construct import construct_f_with_psi_in_U


W_R = 3


def compute_tie_robust(f, chain, p):
    L0, _, _ = chain[0]
    L1, k1, H1 = chain[1]
    L2, k2, H2 = chain[2]
    n1, n2 = len(L1), len(L2)
    f_e, f_o = even_odd_parts(f, L0, p)
    sum_PB, sum_tie = 0.0, 0.0
    d1_dist, d2_dist, joint = {}, {}, {}
    for a1 in range(p):
        fold1 = [(f_e[j] + a1 * f_o[j]) % p for j in range(n1)]
        d1, _ = dist_to_code_full(fold1, H1, n1, k1, p)
        if d1 is None:
            d1 = n1
        d1_dist[d1] = d1_dist.get(d1, 0) + 1
        g_e, g_o = even_odd_parts(fold1, L1, p)
        for a2 in range(p):
            fold2 = [(g_e[j] + a2 * g_o[j]) % p for j in range(n2)]
            d2, _ = dist_to_code_full(fold2, H2, n2, k2, p)
            if d2 is None:
                d2 = n2
            d2_dist[d2] = d2_dist.get(d2, 0) + 1
            joint[(d1, d2)] = joint.get((d1, d2), 0) + 1
            P_B = 1.0 - d2 / n2
            P_A_ub = 1.0 - d1 / n1
            sum_PB += P_B
            sum_tie += max(P_A_ub, P_B)
    n_pairs = p * p
    return (sum_PB / n_pairs, sum_tie / n_pairs, d1_dist, d2_dist, joint)


def reproduce_K2_breaches(seed=4242, p=P):
    rng = random.Random(seed)
    chain = setup_chain(p, N0, K0, R=R)
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, p)
    n_R, w_R = N_R, W_R
    breach_keys = {(1, 5), (2, 8), (4, 2), (8, 0), (18, 8), (25, 3), (25, 6)}
    found = {}
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
        if T2 == T1 or len(set(T1) & set(T2)) > 1:
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
            f = evaluate_dft(fhat, L0:=chain[0][0], p)
            if (pair_idx, f_idx) in breach_keys:
                found[(pair_idx, f_idx)] = (f, T1, T2)
    return chain, found


def main():
    p = P
    print(f"K=2 dense ov=1 tie-robust audit at p={p}")
    print(f"  Question: does any K=2 breach reach tie_upper > 0.449 (the K=1 max)?")
    print(f"  Goal: tie_upper < 0.5 for all above-J f")
    print()
    chain, found = reproduce_K2_breaches(seed=4242, p=p)
    print(f"  Reproduced {len(found)}/7 breaches")
    print()
    K2_results = []
    for key in sorted(found.keys()):
        f, T1, T2 = found[key]
        t0 = time.time()
        P_B, tie, d1d, d2d, jd = compute_tie_robust(f, chain, p)
        elapsed = time.time() - t0
        union_size = len(set(T1) | set(T2))
        K2_results.append((key, T1, T2, union_size, P_B, tie, dict(d1d), dict(jd)))
        print(f"  {key}: T1={T1} T2={T2} |T∪|={union_size}")
        print(f"    P_B={P_B:.4f}  tie_upper={tie:.4f}  ({elapsed:.0f}s)")
        print(f"    d_1: {sorted(d1d.items())}")
        top = sorted(jd.items(), key=lambda x: -x[1])[:4]
        print(f"    top joint (d_1,d_2): {top}", flush=True)
        print()

    print("=" * 75)
    print("SUMMARY: K=2 dense ov=1 breaches")
    print("=" * 75)
    print(f"  {'breach':<10} {'|T∪|':<5} {'P_B':>8} {'tie_upper':>10}")
    for key, T1, T2, us, PB, tie, _, _ in K2_results:
        marker = ""
        if tie > 0.449:
            marker = " ⚠ exceeds K=1 leader (0.449)"
        elif tie > 0.5:
            marker = " ⚠⚠ exceeds 1/2"
        print(f"  {str(key):<10} {us:<5} {PB:>8.4f} {tie:>10.4f}{marker}")
    if K2_results:
        max_tie = max(r[5] for r in K2_results)
        print()
        print(f"  Max K=2 tie_upper: {max_tie:.4f}")
        print(f"  Compare K=1 leader: 0.4490")
        if max_tie < 0.5:
            print(f"  ✓ K=2 dense tie_upper ≤ {max_tie:.4f} < 1/2 — joint-distance bound holds")


if __name__ == '__main__':
    main()
