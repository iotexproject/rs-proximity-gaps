"""probe_K2_construct.py — directly CONSTRUCT candidate above-J f with K(f) ≥ 2.

Strategy: pick (T_1, T_2) with overlap ≤ 1, pick witnesses ε_1 ⊆ T_1, ε_2 ⊆ T_2,
form u_i = H_R · ε_i.  Construct random f with all 4 ψ_b ∈ U := span(u_1, u_2)
(this guarantees K(f) ≥ 2 by construction, since L_i = V_{T_i} ∩ U ⊇ span(u_i)).

Test: does any such f turn out above-J?  If 0/many, K=2 above-J is forbidden.

Direct parameterization (using parity_check structure H[i,j] = ω_R^{-(k_R+i)j}):
    ψ_b[i] = f̂[(k_R + i) · 2^R + |b|_2]   for i ∈ [0, m), b ∈ {0,1}^R.

So writing ψ_b = c_{b,1} u_1 + c_{b,2} u_2 directly gives f̂ at syndrome positions:
    f̂[(k_R + i) · 2^R + |b|_2]  =  c_{b,1} (u_1)[i] + c_{b,2} (u_2)[i].

Free params: 4·2 = 8 (the c_{b,k}), plus 8 message positions f̂[0..k_0).  Total 16.
"""
from __future__ import annotations
import sys, os, random, time
from itertools import product, combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, parity_check, matvec, gauss_rank
from probe_step5_n32_studio import (
    P, N0, K0, R, N_R, W_J,
    evaluate_dft, fold_at_alpha, compute_corner_syndromes,
)
from mds_decoder import is_above_johnson_sampling
from probe_rank2_struct_fast import mobius_psi
from probe_K_classifier import K_classifier, line_canonical, rref_basis, intersection_basis


W_R = 3
M = N_R - 2  # = 6 (m = n_R - k_R)
K_R = 2


def construct_f_with_psi_in_U(u1, u2, c, msg, p):
    """Construct f̂ ∈ F_p^{N0} with f̂[(k_R + i)·2^R + |b|_2] = c[b][0]·u1[i] + c[b][1]·u2[i].

    c: dict b_tuple → (c0, c1) for b ∈ {0,1}^R.
    msg: list of K0 values for f̂[0..K0).
    Returns f ∈ F_p^{N0} (time-domain via inverse DFT, but we just return f̂ then evaluate).
    """
    fhat = list(msg) + [0] * (N0 - K0)
    for b in product([0, 1], repeat=R):
        b_int = sum(b[r] * (2 ** r) for r in range(R))
        c0, c1 = c[b]
        for i in range(M):
            pos = (K_R + i) * (2 ** R) + b_int
            fhat[pos] = (c0 * u1[i] + c1 * u2[i]) % p
    return fhat


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 4242
    n_pairs = int(sys.argv[2]) if len(sys.argv) > 2 else 200    # # of (T1,T2,ε1,ε2)
    n_f_per = int(sys.argv[3]) if len(sys.argv) > 3 else 50     # f's per pair
    rng = random.Random(seed)

    chain = setup_chain(P, N0, K0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, P)
    H_R_cols = [list(col) for col in zip(*H_R)]
    p = P
    n_R = N_R
    w_R = W_R

    print(f"# probe_K2_construct — direct construction of candidate K≥2 above-J f")
    print(f"# Setup: p={p}, n_0={N0}, k_0={K0}, R={R}, n_R={n_R}, w_R={w_R}, w_J={W_J}")
    print(f"# Pairs (T1,T2,ε1,ε2): {n_pairs}, f's per pair: {n_f_per}, seed={seed}")
    print(f"# Total f's to test: {n_pairs * n_f_per}")
    print()

    # Stats
    n_total = 0
    n_above_J = 0
    n_K_ge_2 = 0
    n_above_J_and_K_ge_2 = 0
    n_K_eq_2 = 0
    n_K_ge_3 = 0
    K_distr = {}
    rank_distr = {}
    found_examples = []

    t0 = time.time()
    for pair_idx in range(n_pairs):
        # Pick (T1, T2) with overlap ≤ 1
        T1 = tuple(sorted(rng.sample(range(n_R), w_R)))
        # Choose overlap: 50% overlap-0, 50% overlap-1
        overlap = rng.choice([0, 1])
        if overlap == 0:
            available = [j for j in range(n_R) if j not in T1]
            if len(available) < w_R:
                continue
            T2 = tuple(sorted(rng.sample(available, w_R)))
        else:  # overlap == 1
            shared = rng.choice(list(T1))
            others_pool = [j for j in range(n_R) if j not in T1]
            if len(others_pool) < w_R - 1:
                continue
            others = rng.sample(others_pool, w_R - 1)
            T2 = tuple(sorted([shared] + others))
        if T2 == T1:
            continue
        actual_overlap = len(set(T1) & set(T2))
        if actual_overlap > 1:
            continue

        # Pick ε_1, ε_2 with full weight (= w_R)
        eps1 = [0] * n_R
        eps2 = [0] * n_R
        for j in T1:
            eps1[j] = rng.randrange(1, p)
        for j in T2:
            eps2[j] = rng.randrange(1, p)

        u1 = matvec(H_R, eps1, p)
        u2 = matvec(H_R, eps2, p)
        # Verify span 2-dim
        if gauss_rank([u1, u2], p) != 2:
            continue

        # Sample n_f_per random f's with ψ_b ∈ span(u1, u2)
        for f_idx in range(n_f_per):
            c = {}
            for b in product([0, 1], repeat=R):
                c[b] = (rng.randrange(p), rng.randrange(p))
            msg = [rng.randrange(p) for _ in range(K0)]
            fhat = construct_f_with_psi_in_U(u1, u2, c, msg, p)
            f = evaluate_dft(fhat, L0, p)

            # Check rank of σ
            corners = compute_corner_syndromes(f, chain, R, p, H_R)
            nz = [list(s) for s in corners.values() if any(x != 0 for x in s)]
            rk = gauss_rank(nz, p) if nz else 0
            rank_distr[rk] = rank_distr.get(rk, 0) + 1

            # Above-J check (use lighter sampling for speed)
            above, _, _ = is_above_johnson_sampling(
                f, L0, K0, p, W_J, n_samples=8000, batch=4096, seed=seed + n_total,
                return_evidence=True,
            )

            n_total += 1
            if above:
                n_above_J += 1

            if rk == 2:
                # Compute K
                K, dim_distr, K_full, dim_U = K_classifier(f, chain, H_R, p, n_R, w_R)
                K_distr[K] = K_distr.get(K, 0) + 1
                if K >= 2:
                    n_K_ge_2 += 1
                    if K == 2:
                        n_K_eq_2 += 1
                    else:
                        n_K_ge_3 += 1
                    if above:
                        n_above_J_and_K_ge_2 += 1
                        # Capture example
                        if len(found_examples) < 5:
                            found_examples.append({
                                'T1': T1, 'T2': T2, 'overlap': actual_overlap,
                                'K': K, 'K_full': K_full, 'dim_distr': dim_distr,
                                'pair_idx': pair_idx, 'f_idx': f_idx,
                            })

        if (pair_idx + 1) % 20 == 0:
            elapsed = time.time() - t0
            print(f"# Progress: {pair_idx+1}/{n_pairs} pairs, "
                  f"{n_total} f's, {n_above_J} above-J, "
                  f"{n_K_ge_2} K≥2, {n_above_J_and_K_ge_2} BOTH, "
                  f"elapsed {elapsed:.1f}s")

    print()
    print(f"# === Summary ===")
    print(f"# Total f's tested: {n_total}")
    print(f"# Above-J: {n_above_J} ({100.0*n_above_J/max(n_total,1):.1f}%)")
    print(f"# Rank distribution: {sorted(rank_distr.items())}")
    print(f"# K distribution (rank-2 only): {sorted(K_distr.items())}")
    print(f"# K ≥ 2: {n_K_ge_2} (K=2: {n_K_eq_2}, K≥3: {n_K_ge_3})")
    print(f"# Above-J AND K ≥ 2: {n_above_J_and_K_ge_2} ★")
    print()
    if n_above_J_and_K_ge_2 == 0:
        print(f"# ✓ HYPOTHESIS HOLDS: 0/{n_above_J} above-J f's have K ≥ 2")
        print(f"#   (over {n_pairs} (T1,T2,ε1,ε2) configs with overlap ≤ 1)")
    else:
        print(f"# ✗ HYPOTHESIS FAILS: found {n_above_J_and_K_ge_2} above-J f's with K ≥ 2")
        print(f"# Examples:")
        for ex in found_examples:
            print(f"#   T1={ex['T1']}, T2={ex['T2']}, overlap={ex['overlap']}, "
                  f"K={ex['K']}, dim_distr={ex['dim_distr']}, pair={ex['pair_idx']}, f={ex['f_idx']}")


if __name__ == '__main__':
    main()
