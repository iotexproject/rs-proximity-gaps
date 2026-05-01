"""probe_K1_d1_structure.py — what determines d_1 for K=1 (rank-1) above-J f?

For K=1 above-J f at our params: empirically d_1 ∈ {0, 9} with the 9 happening
for ~96/97 α_1's. We want to understand WHY d_1 = 9 (not 8 or 10) for the bulk.

Hypothesis: rank-1 image at level-2 ⟹ structured level-1 fold pattern, where
fold_1 differs from a level-1 codeword by a fixed-support error of weight 9.

Test: enumerate K=1 above-J f's. For each, check:
  1. Is d_1 constant across (almost all) α_1?
  2. What's the support of fold_1(α_1) - c(α_1) (the error)?
  3. Is the support fixed across α_1 (modulo curve)?

If yes, the "stable level-1 agreement set" hypothesis is empirically verified.

Usage: python3 probe_K1_d1_structure.py [n_samples=10] [seed=2026]
"""
from __future__ import annotations
import sys, os, random, time
from itertools import combinations

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


def get_d1_supports(f, chain, p, max_alpha=20):
    """For each α_1, compute (d_1, support of error fold_1 - c)."""
    L0, _, _ = chain[0]
    L1, k1, H1 = chain[1]
    n1 = len(L1)
    f_e, f_o = even_odd_parts(f, L0, p)
    results = []
    for a1 in range(min(p, max_alpha)):
        fold1 = [(f_e[j] + a1 * f_o[j]) % p for j in range(n1)]
        d1, S1 = dist_to_code_full(fold1, H1, n1, k1, p)
        if d1 is None:
            d1, S1 = n1, []
        T1 = tuple(sorted(j for j in range(n1) if j not in set(S1)))
        results.append((a1, d1, T1))
    return results


def main():
    n_samples = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 2026
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, p)
    m = N_R - k_R
    n1 = N0 // 2
    k1 = K0 // 2
    print(f"K=1 d_1 structure probe at p={p}, n_1={n1}, k_1={k1}")
    print(f"  Test: for K=1 above-J f, is supp(fold_1 - c) constant across α_1?")
    print(f"  Conjecture: yes, with possibly 1-2 exceptional α_1 (curves)")
    print()

    rng = random.Random(seed)
    n_found = 0
    n_tries = 0
    while n_found < n_samples and n_tries < 1000:
        n_tries += 1
        # K=1 = sparse 2-frequency rank-1 above-J
        positions = tuple(sorted(rng.sample(range(K0, N0), 2)))
        coefs = (rng.randrange(1, p), rng.randrange(1, p))
        fhat = [0] * N0
        for pos, c in zip(positions, coefs):
            fhat[pos] = c
        f = evaluate_dft(fhat, L0, p)
        d_lb = dist_lower_bound_sampling(f, L0, K0, p, n_samples=10000, batch=4096, seed=seed + n_tries)
        if d_lb <= W_J:
            continue
        corner_syns = compute_corner_syndromes(f, chain, R, p, H_R)
        rank, _, _, _ = image_rank_and_mu(corner_syns, R, p, m)
        if rank != 1:
            continue
        n_found += 1

        # Compute d_1 supports for first 30 α_1
        results = get_d1_supports(f, chain, p, max_alpha=30)
        d1_set = set()
        T_supports = {}
        for a1, d1, T1 in results:
            d1_set.add(d1)
            T_supports.setdefault(T1, []).append(a1)

        print(f"sample {n_found}: positions={positions} coefs={coefs} d_lb={d_lb}")
        print(f"  d_1 values across 30 α_1: {sorted(d1_set)}")
        print(f"  unique support sets: {len(T_supports)}")
        for T, alphas in sorted(T_supports.items(), key=lambda x: -len(x[1]))[:3]:
            print(f"    T={T}  size={len(T)}  α_1 count={len(alphas)}: first few = {alphas[:5]}")
        print()


if __name__ == '__main__':
    main()
