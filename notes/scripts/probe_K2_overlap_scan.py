"""probe_K2_overlap_scan.py — scan K=2 dense across overlap=0,1,2 to find the
P_avg-maximizing construction.

Original 0114 probe restricted to overlap ≤ 1 (geometric reason: we wanted rank=2
σ-image, which requires ε_1, ε_2 supported on distinct directions). overlap=2
gives |T_1 ∪ T_2| = 4 — barely above-J? Let's see.

For each overlap ∈ {0, 1, 2}: sample a few K=2 constructions, compute P_avg.
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
from mds_decoder import dist_lower_bound_sampling
from probe_K2_construct import construct_f_with_psi_in_U


W_R = 3


def fast_P_avg_and_d2_zero(f, chain, p):
    L0, _, _ = chain[0]
    L1, _, _ = chain[1]
    L2, k2, H2 = chain[2]
    n1, n2 = len(L1), len(L2)
    f_e, f_o = even_odd_parts(f, L0, p)
    total_d2 = 0
    n_pairs = 0
    n_zero = 0
    n_le_3 = 0
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
            if d2 == 0:
                n_zero += 1
            if d2 <= 3:
                n_le_3 += 1
    return 1.0 - (total_d2 / n_pairs) / n2, n_zero, n_le_3


def build_K2_with_overlap(rng, p, n_R, w_R, H_R, overlap):
    T1 = tuple(sorted(rng.sample(range(n_R), w_R)))
    if overlap == 0:
        available = [j for j in range(n_R) if j not in T1]
        if len(available) < w_R:
            return None
        T2 = tuple(sorted(rng.sample(available, w_R)))
    else:
        shared = rng.sample(list(T1), overlap)
        others_pool = [j for j in range(n_R) if j not in T1]
        if len(others_pool) < w_R - overlap:
            return None
        others = rng.sample(others_pool, w_R - overlap)
        T2 = tuple(sorted(list(shared) + others))
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
    p, n0, k0 = P, N0, K0
    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, p)

    print(f"K=2 overlap scan (n_R={N_R}, w_R={W_R}, p={p}, w_J={W_J})")
    print(f"  P_avg target: > 1-δ = {1 - W_J/n0:.4f} (improves on (1-δ)^q)")
    print()
    print(f"{'ovlap':<6} {'|T1∪T2|':<8} {'#tries':<7} {'#aboveJ':<8} {'P_avg':<8} {'#α: d2=0':<10} {'#α: d2≤3':<9}")
    print("-" * 60, flush=True)

    rng = random.Random(7777)
    n_per_overlap = 8

    for overlap in [0, 1, 2]:
        union_size = 2 * W_R - overlap
        n_above_j = 0
        best_P_avg = -1
        best_d2_zero = 0
        best_d2_le_3 = 0
        n_tries = 0
        while n_above_j < n_per_overlap and n_tries < 80:
            n_tries += 1
            res = build_K2_with_overlap(rng, p, N_R, W_R, H_R, overlap)
            if res is None:
                continue
            T1, T2, eps1, eps2, u1, u2 = res
            c = {b: (rng.randrange(p), rng.randrange(p)) for b in product([0, 1], repeat=R)}
            msg = [rng.randrange(p) for _ in range(K0)]
            fhat = construct_f_with_psi_in_U(u1, u2, c, msg, p)
            f = evaluate_dft(fhat, L0, p)
            d_lb = dist_lower_bound_sampling(f, L0, k0, p, n_samples=20000, batch=4096, seed=1234 + n_tries)
            if d_lb <= W_J:
                continue
            n_above_j += 1
            P_avg, n_zero, n_le_3 = fast_P_avg_and_d2_zero(f, chain, p)
            if P_avg > best_P_avg:
                best_P_avg = P_avg
                best_d2_zero = n_zero
                best_d2_le_3 = n_le_3
            print(f"  ov={overlap} t={n_tries:>3} aJ={n_above_j} d_lb={d_lb}: P_avg={P_avg:.4f} d2=0:{n_zero} d2≤3:{n_le_3}", flush=True)
        print(f"OV={overlap} |T1∪T2|={union_size} n_aboveJ={n_above_j}/{n_tries} best P_avg={best_P_avg:.4f} (d2=0:{best_d2_zero}, d2≤3:{best_d2_le_3})", flush=True)
        print()


if __name__ == '__main__':
    main()
