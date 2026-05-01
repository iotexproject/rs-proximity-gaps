"""probe_pscan_K2_dense.py — verify asymptotic P_avg → 0.375 across multiple q.

For each p ∈ {97, 257, 449, 577}, compute P_avg for 1-3 K=2 dense ov=1 above-J f's.
This gives a direct convergence curve for the asymptotic 0.375 prediction.

Usage: python3 probe_pscan_K2_dense.py [n_per_p=2] [seed=2026]
"""
from __future__ import annotations
import sys, os, random, time, math
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import (
    setup_chain, parity_check, matvec, gauss_rank,
    even_odd_parts, dist_to_code_full,
)
from mds_decoder import dist_lower_bound_sampling
from probe_K2_construct import construct_f_with_psi_in_U


N0 = 32
K0 = 8
R = 2
N_R = N0 // (2**R)
W_J = int((1 - math.sqrt(K0/N0)) * N0)
W_R = 3


def evaluate_dft(fhat, L0, p):
    return [sum(fhat[i] * pow(L0[j], i, p) for i in range(len(fhat))) % p for j in range(len(L0))]


def P_avg_strategy_B(f, chain, p):
    L0, _, _ = chain[0]
    L1, _, _ = chain[1]
    L2, k2, H2 = chain[2]
    n1, n2 = len(L1), len(L2)
    f_e, f_o = even_odd_parts(f, L0, p)
    total_d2 = 0
    n_pairs = 0
    d2_dist = {}
    for a1 in range(p):
        fold1 = [(f_e[j] + a1 * f_o[j]) % p for j in range(n1)]
        g_e, g_o = even_odd_parts(fold1, L1, p)
        for a2 in range(p):
            fold2 = [(g_e[j] + a2 * g_o[j]) % p for j in range(n2)]
            d2, _ = dist_to_code_full(fold2, H2, n2, k2, p)
            if d2 is None:
                d2 = n2
            total_d2 += d2
            n_pairs += 1
            d2_dist[d2] = d2_dist.get(d2, 0) + 1
    return 1.0 - (total_d2 / n_pairs) / n2, d2_dist


def build_K2_overlap1(rng, p, n_R, w_R, H_R):
    T1 = tuple(sorted(rng.sample(range(n_R), w_R)))
    shared = rng.choice(list(T1))
    others_pool = [j for j in range(n_R) if j not in T1]
    others = rng.sample(others_pool, w_R - 1)
    T2 = tuple(sorted([shared] + others))
    if T2 == T1:
        return None
    eps1 = [0] * n_R
    eps2 = [0] * n_R
    for j in T1:
        eps1[j] = rng.randrange(1, p)
    for j in T2:
        eps2[j] = rng.randrange(1, p)
    u1 = matvec(H_R, eps1, p)
    u2 = matvec(H_R, eps2, p)
    if gauss_rank([u1, u2], p) != 2:
        return None
    return T1, T2, eps1, eps2, u1, u2


def main():
    n_per_p = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 2026

    primes = [97, 257, 449, 577, 769]

    print("=" * 72)
    print(f"P_avg vs q scan: K=2 dense ov=1, R=2, n_R=8, w_R=3")
    print(f"  Asymptotic prediction: P_avg → 1 - 5/8 = 0.375")
    print(f"  {n_per_p} examples per p, total {n_per_p * len(primes)} P_avg evals")
    print("=" * 72)
    print(f"{'p':>5} {'q²':>8} {'sample':>7} {'P_avg':>8} {'Δ from 0.375':>14} {'d2=0':>5} {'d2≤3':>6} {'time':>6}")
    print('-' * 72, flush=True)

    results_by_p = {}
    for p in primes:
        chain = setup_chain(p, N0, K0, R=R)
        L0 = chain[0][0]
        L_R, k_R, _ = chain[R]
        H_R = parity_check(L_R, N_R, k_R, p)
        rng = random.Random(seed + p)
        results = []
        n_above_j = 0
        n_tries = 0
        while n_above_j < n_per_p and n_tries < 50:
            n_tries += 1
            res = build_K2_overlap1(rng, p, N_R, W_R, H_R)
            if res is None:
                continue
            T1, T2, eps1, eps2, u1, u2 = res
            c = {b: (rng.randrange(p), rng.randrange(p)) for b in product([0, 1], repeat=R)}
            msg = [rng.randrange(p) for _ in range(K0)]
            fhat = construct_f_with_psi_in_U(u1, u2, c, msg, p)
            f = evaluate_dft(fhat, L0, p)
            d_lb = dist_lower_bound_sampling(f, L0, k0, p, n_samples=20000, batch=4096, seed=seed + n_tries)
            if d_lb <= W_J:
                continue
            n_above_j += 1
            t0 = time.time()
            P_avg, d2_dist = P_avg_strategy_B(f, chain, p)
            eval_time = time.time() - t0
            n_zero = d2_dist.get(0, 0)
            n_le_3 = sum(c for d, c in d2_dist.items() if d <= 3)
            results.append({
                'P_avg': P_avg, 'n_zero': n_zero, 'n_le_3': n_le_3,
                'time': eval_time, 'T1': T1, 'T2': T2,
            })
            print(f"{p:>5} {p*p:>8} {n_above_j:>7} {P_avg:>8.4f} {P_avg - 0.375:>+14.4f} "
                  f"{n_zero:>5} {n_le_3:>6} {eval_time:>5.0f}s", flush=True)
        results_by_p[p] = results

    print()
    print("=" * 72)
    print(f"SUMMARY: max P_avg per p (asymptotic prediction: 0.375)")
    print("=" * 72)
    print(f"{'p':>5} {'max P_avg':>10} {'Δ from 0.375':>14} {'predicted O(R/q)':>18}")
    print('-' * 72)
    for p in primes:
        rs = results_by_p.get(p, [])
        if rs:
            mx = max(r['P_avg'] for r in rs)
            pred_boost = 5 / p  # rough O(1/q) prediction
            print(f"{p:>5} {mx:>10.4f} {mx - 0.375:>+14.4f} {pred_boost:>18.4f}")
    print()
    print("If the boost shrinks like O(1/q), Bezout prediction confirmed.")
    print("If boost doesn't shrink, structural analysis needs revision.")


if __name__ == '__main__':
    main()
