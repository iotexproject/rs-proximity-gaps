"""audit_tie_robust_sparse.py — tie-robust upper for sparse rank-r above-J f.

After audit_tie_robust_upper.py confirmed K=1 leader → 0.449 and audit_tie_robust_K2
finishing for K=2 dense, the remaining gap is sparse rank-r ≥ 2.

For sparse rank-r ≥ 2 above-J: probe_sparse_rank_p_avg (note 0118) found P_B ≤ 0.32.
Question: does tie_upper stay below 0.449 too?

For sparse rank-r ≥ 2: |U ∩ B_{w_R}| = 1 typically (note 0108) → bulk d_2 ≥ 4.
At d_2 = 4: P_B = 0.5, but those events are rare (≤ q intersections).

Sample 5 above-J sparse rank-r f's, compute tie_upper. Report joint distribution.

Usage: python3 audit_tie_robust_sparse.py [n_samples=5] [seed=2026]
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
    compute_corner_syndromes, image_rank_and_mu,
)
from mds_decoder import dist_lower_bound_sampling


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


def main():
    n_samples = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 2026
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, p)
    m = N_R - k_R

    print(f"Sparse rank-r tie_upper audit at p={p}")
    print(f"  Goal: confirm sparse rank-r ≤ 0.449 (the K=1 leader)")
    print(f"  Sampling {n_samples} sparse above-J f's, then compute tie_upper")
    print()

    rng = random.Random(seed)
    n_tries = 0
    results = []
    found_per_rank = {2: 0, 3: 0, 4: 0}

    while sum(found_per_rank.values()) < n_samples and n_tries < 5000:
        n_tries += 1
        n_pos = rng.choice([3, 4, 5])
        positions = tuple(sorted(rng.sample(range(K0, N0), n_pos)))
        coefs = tuple(rng.randrange(1, p) for _ in range(n_pos))
        fhat = [0] * N0
        for pos, c in zip(positions, coefs):
            fhat[pos] = c
        f = evaluate_dft(fhat, L0, p)
        d_lb = dist_lower_bound_sampling(f, L0, K0, p, n_samples=20000, batch=4096, seed=seed + n_tries)
        if d_lb <= W_J:
            continue
        corner_syns = compute_corner_syndromes(f, chain, R, p, H_R)
        rank, _, _, _ = image_rank_and_mu(corner_syns, R, p, m)
        if rank not in (2, 3, 4) or found_per_rank.get(rank, 0) >= max(2, n_samples // 3):
            continue
        found_per_rank[rank] += 1

        t0 = time.time()
        P_B, tie, d1d, d2d, jd = compute_tie_robust(f, chain, p)
        elapsed = time.time() - t0
        results.append((rank, positions, coefs, d_lb, P_B, tie, dict(d1d), dict(jd)))

        print(f"  rank={rank}  positions={positions}  coefs={coefs}  d_lb={d_lb}")
        print(f"    P_B={P_B:.4f}  tie_upper={tie:.4f}  ({elapsed:.0f}s)")
        print(f"    d_1: {sorted(d1d.items())}")
        top = sorted(jd.items(), key=lambda x: -x[1])[:4]
        print(f"    top joint: {top}", flush=True)
        print()

    print("=" * 75)
    print("SUMMARY: sparse rank-r tie_upper")
    print("=" * 75)
    if results:
        max_tie = max(r[5] for r in results)
        max_PB = max(r[4] for r in results)
        for r in [2, 3, 4]:
            rs = [x for x in results if x[0] == r]
            if rs:
                print(f"  rank-{r}: max P_B={max(x[4] for x in rs):.4f}  max tie_upper={max(x[5] for x in rs):.4f}  n={len(rs)}")
        print()
        print(f"  Overall max tie_upper: {max_tie:.4f}")
        print(f"  Compare K=1 leader: 0.4490")
        if max_tie < 0.449:
            print(f"  ✓ Sparse rank-r below K=1 leader — universal max remains at K=1")
        else:
            print(f"  ⚠ Sparse rank-r exceeds K=1 leader 0.449")


if __name__ == '__main__':
    main()
