"""probe_psi11_structure.py — investigate WHY G_f(α) is degree-2 (not bidegree-(2,2)) for rank-2 above-J f.

The syndrome map σ(α) = ψ̃_00 + α₁ ψ̃_10 + α₂ ψ̃_01 + α₁α₂ ψ̃_11 is bidegree (1,1) in α.
Generically a vanishing polynomial of σ pulled back has bidegree (2,2) → degree 4 in α.
But empirically G_f has degree 2. WHY?

Hypothesis: for rank-2 above-J f, ψ̃_11 ≡ 0 (the bilinear part vanishes), making σ LINEAR
in α. Then any linear subspace condition pulls back to a linear-in-α condition.

This script:
1. For each falsifier (and additional rank-2 above-J f's), compute ψ̃_b for b ∈ {0,1}^2.
2. Check whether ψ̃_11 = 0.
3. Tabulate.
"""
from __future__ import annotations
import sys, os, random
from itertools import product
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, parity_check, gauss_rank, matvec
from mds_decoder import is_above_johnson_sampling
from probe_step5_n32_studio import (
    P, N0, K0, R, N_R, W_J,
    evaluate_dft, fold_at_alpha, compute_corner_syndromes,
)


CANDIDATES = [
    ((12, 18, 22), (59, 73, 36)),
    ((14, 18, 31), (90, 90, 88)),
    ((9, 19, 27),  (16, 86, 49)),
    ((13, 22, 30), (23, 17, 17)),
    ((9, 10, 22, 25, 26), (30, 38, 58, 50, 69)),
    ((14, 18, 28, 30), (91, 88, 70, 22)),
]


def vec_sub(a, b, p):
    return [(x - y) % p for x, y in zip(a, b)]


def vec_add(a, b, p):
    return [(x + y) % p for x, y in zip(a, b)]


def is_zero(v):
    return all(x == 0 for x in v)


def mobius_psi(corners, p):
    """corners: dict b in {0,1}^2 -> v_b vector. Returns dict b -> ψ̃_b (Möbius coeffs)."""
    v_00 = corners[(0, 0)]
    v_10 = corners[(1, 0)]
    v_01 = corners[(0, 1)]
    v_11 = corners[(1, 1)]
    psi_00 = list(v_00)
    psi_10 = vec_sub(v_10, v_00, p)
    psi_01 = vec_sub(v_01, v_00, p)
    psi_11 = vec_sub(vec_sub(vec_add(v_11, v_00, p), v_10, p), v_01, p)
    return {(0, 0): psi_00, (1, 0): psi_10, (0, 1): psi_01, (1, 1): psi_11}


def analyze(positions, coefs, chain, p, H_R, label):
    fhat = [0] * N0
    for pos, c in zip(positions, coefs):
        fhat[pos] = c
    f = evaluate_dft(fhat, chain[0][0], p)
    corner_syns = compute_corner_syndromes(f, chain, R, p, H_R)
    psi = mobius_psi(corner_syns, p)
    psi_00, psi_10, psi_01, psi_11 = psi[(0,0)], psi[(1,0)], psi[(0,1)], psi[(1,1)]
    psi_11_zero = is_zero(psi_11)

    nz = [s for s in corner_syns.values() if any(x != 0 for x in s)]
    rk_v = gauss_rank([list(s) for s in nz], p) if nz else 0

    nz_psi = [s for s in psi.values() if any(x != 0 for x in s)]
    rk_psi = gauss_rank([list(s) for s in nz_psi], p) if nz_psi else 0

    print(f"\n=== {label}: positions={positions}, coefs={coefs} ===")
    print(f"  rank(v_b) = {rk_v}, rank(ψ̃_b) = {rk_psi}")
    print(f"  ψ̃_11 = {psi_11}  (is zero: {psi_11_zero})")
    if not psi_11_zero:
        # Check whether ψ̃_11 ∈ span{ψ̃_00, ψ̃_10, ψ̃_01}
        spans = [psi_00, psi_10, psi_01]
        rk_with = gauss_rank([list(s) for s in spans + [psi_11]], p)
        rk_without = gauss_rank([list(s) for s in spans], p)
        in_span = rk_with == rk_without
        print(f"  ψ̃_11 ∈ span{{ψ̃_00, ψ̃_10, ψ̃_01}}: {in_span} (rank with={rk_with}, without={rk_without})")
        # Also check span{ψ̃_10, ψ̃_01, ψ̃_11}
        spans2 = [psi_10, psi_01]
        rk_with2 = gauss_rank([list(s) for s in spans2 + [psi_11]], p)
        rk_without2 = gauss_rank([list(s) for s in spans2], p)
        print(f"  ψ̃_11 ∈ span{{ψ̃_10, ψ̃_01}}: {rk_with2 == rk_without2}")


def main():
    chain = setup_chain(P, N0, K0, R=R)
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, P)

    print("# Investigation: is ψ̃_11 = 0 for rank-2 above-J f?")
    print("#   (would explain why G_f is degree 2, not bidegree (2,2) = deg 4)")

    for i, (positions, coefs) in enumerate(CANDIDATES):
        analyze(positions, coefs, chain, P, H_R, f"falsifier #{i+1}")

    # Add a few additional rank-2 above-J cases
    print("\n\n# === Additional rank-2 above-J ===")
    rng = random.Random(7777)
    n_done = 0
    n_tried = 0
    while n_done < 6 and n_tried < 80:
        n_tried += 1
        sparsity = rng.choice([2, 3])
        positions = tuple(sorted(rng.sample(range(K0, N0), sparsity)))
        coefs = tuple(rng.randrange(1, P) for _ in range(sparsity))
        fhat = [0] * N0
        for pos, c in zip(positions, coefs):
            fhat[pos] = c
        f = evaluate_dft(fhat, chain[0][0], P)
        above, _, _ = is_above_johnson_sampling(
            f, chain[0][0], K0, P, W_J, n_samples=20000, batch=4096, seed=8888,
            return_evidence=True,
        )
        if not above:
            continue
        corner_syns = compute_corner_syndromes(f, chain, R, P, H_R)
        nz = [s for s in corner_syns.values() if any(x != 0 for x in s)]
        rk = gauss_rank([list(s) for s in nz], P) if nz else 0
        if rk != 2:
            continue
        analyze(positions, coefs, chain, P, H_R, f"extra rank-2 #{n_done+1}")
        n_done += 1

    # And a few rank-3 cases for comparison
    print("\n\n# === Rank-3 cases (for comparison) ===")
    rng = random.Random(9999)
    n_done = 0
    n_tried = 0
    while n_done < 4 and n_tried < 80:
        n_tried += 1
        sparsity = rng.choice([3, 4, 5])
        positions = tuple(sorted(rng.sample(range(K0, N0), sparsity)))
        coefs = tuple(rng.randrange(1, P) for _ in range(sparsity))
        fhat = [0] * N0
        for pos, c in zip(positions, coefs):
            fhat[pos] = c
        f = evaluate_dft(fhat, chain[0][0], P)
        above, _, _ = is_above_johnson_sampling(
            f, chain[0][0], K0, P, W_J, n_samples=20000, batch=4096, seed=8888,
            return_evidence=True,
        )
        if not above:
            continue
        corner_syns = compute_corner_syndromes(f, chain, R, P, H_R)
        nz = [s for s in corner_syns.values() if any(x != 0 for x in s)]
        rk = gauss_rank([list(s) for s in nz], P) if nz else 0
        if rk != 3:
            continue
        analyze(positions, coefs, chain, P, H_R, f"rank-3 #{n_done+1}")
        n_done += 1


if __name__ == '__main__':
    main()
