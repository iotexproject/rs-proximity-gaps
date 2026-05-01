"""probe_rank2_struct_fast.py — fast structural classifier for rank-2 above-J f.

Skips brute-force |V_δ| enumeration (slow). Just computes (rank{v_b}, rank{ψ_10, ψ_01},
ψ_11=0 flag, ψ_00=0 flag, ψ_10=0 flag) and the full ψ Möbius coefficients.

Pairs with note 0112 to confirm the structural classifier:
  Saturating rank-2 (|V_δ| could reach 2q-1) ⟺ rank{ψ_10, ψ_01} ≤ 1.

For non-saturating cases (rank{ψ_10, ψ_01} = 2), we also want to verify they don't go above q.
But verifying that requires |V_δ| enumeration, which is slow — so we just classify here and
defer empirical confirmation to existing studio data.
"""
from __future__ import annotations
import sys, os, math, random
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, parity_check, gauss_rank
from mds_decoder import is_above_johnson_sampling
from probe_step5_n32_studio import (
    P, N0, K0, R, N_R, W_J,
    evaluate_dft, fold_at_alpha, compute_corner_syndromes,
)


def vec_sub(a, b, p): return [(x - y) % p for x, y in zip(a, b)]
def vec_add(a, b, p): return [(x + y) % p for x, y in zip(a, b)]
def is_zero(v): return all(x == 0 for x in v)


def mobius_psi(corners, p):
    v_00 = corners[(0, 0)]; v_10 = corners[(1, 0)]
    v_01 = corners[(0, 1)]; v_11 = corners[(1, 1)]
    return {
        (0, 0): list(v_00),
        (1, 0): vec_sub(v_10, v_00, p),
        (0, 1): vec_sub(v_01, v_00, p),
        (1, 1): vec_sub(vec_sub(vec_add(v_11, v_00, p), v_10, p), v_01, p),
    }


def analyze(positions, coefs, chain, p, H_R, label):
    fhat = [0] * N0
    for pos, c in zip(positions, coefs): fhat[pos] = c
    f = evaluate_dft(fhat, chain[0][0], p)
    corners = compute_corner_syndromes(f, chain, R, p, H_R)
    psi = mobius_psi(corners, p)

    nz_v = [list(s) for s in corners.values() if any(x != 0 for x in s)]
    rk_v = gauss_rank(nz_v, p) if nz_v else 0

    rk_psi_lin = gauss_rank([psi[(1, 0)], psi[(0, 1)]], p)
    p00z = is_zero(psi[(0, 0)])
    p10z = is_zero(psi[(1, 0)])
    p01z = is_zero(psi[(0, 1)])
    p11z = is_zero(psi[(1, 1)])

    print(f"  {label}: rk_v={rk_v}, rk{{ψ_10,ψ_01}}={rk_psi_lin}, "
          f"ψ_00=0:{int(p00z)} ψ_10=0:{int(p10z)} ψ_01=0:{int(p01z)} ψ_11=0:{int(p11z)}")
    return rk_v, rk_psi_lin, p00z, p10z, p01z, p11z


def main():
    chain = setup_chain(P, N0, K0, R=R)
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, P)

    print(f"# probe_rank2_struct_fast — structural classifier (no V_δ enum)")
    print(f"# Setup: p={P}, n_0={N0}, k_0={K0}, R={R}, w_J={W_J}")
    print()

    print("# === Falsifiers (known |V_δ| from prior probes) ===")
    falsifiers_with_Vd = [
        ((12, 18, 22), (59, 73, 36), 0),
        ((14, 18, 31), (90, 90, 88), 193),
        ((9, 19, 27),  (16, 86, 49), 193),
        ((13, 22, 30), (23, 17, 17), 97),
        ((9, 10, 22, 25, 26), (30, 38, 58, 50, 69), 97),
        ((14, 18, 28, 30), (91, 88, 70, 22), 97),
    ]
    fals_results = []
    for i, (positions, coefs, vd) in enumerate(falsifiers_with_Vd):
        r = analyze(positions, coefs, chain, P, H_R, f"falsifier#{i+1} (|V_δ|={vd})")
        fals_results.append((vd, r))

    print()
    print("# === Random rank-2 above-J ===")
    rng = random.Random(2027)
    n_done = 0; n_tried = 0
    rand_results = []
    while n_done < 80 and n_tried < 2000:
        n_tried += 1
        sparsity = rng.choice([2, 3])
        positions = tuple(sorted(rng.sample(range(K0, N0), sparsity)))
        coefs = tuple(rng.randrange(1, P) for _ in range(sparsity))
        fhat = [0] * N0
        for pos, c in zip(positions, coefs): fhat[pos] = c
        f = evaluate_dft(fhat, chain[0][0], P)
        above, _, _ = is_above_johnson_sampling(
            f, chain[0][0], K0, P, W_J, n_samples=20000, batch=4096, seed=8888,
            return_evidence=True,
        )
        if not above: continue
        corners = compute_corner_syndromes(f, chain, R, P, H_R)
        nz = [list(s) for s in corners.values() if any(x != 0 for x in s)]
        rk = gauss_rank(nz, P) if nz else 0
        if rk != 2: continue
        r = analyze(positions, coefs, chain, P, H_R, f"random#{n_done+1}: pos={positions}, c={coefs}")
        rand_results.append(r)
        n_done += 1

    # Summarize
    print()
    print(f"# === Summary ===")
    print(f"# Falsifiers: {len(fals_results)}")
    for vd, (rkv, rkl, p00z, p10z, p01z, p11z) in fals_results:
        print(f"  |V_δ|={vd:3d}, rk{{ψ_10,ψ_01}}={rkl}, ψ_00=0:{int(p00z)} ψ_10=0:{int(p10z)} ψ_01=0:{int(p01z)} ψ_11=0:{int(p11z)}")

    print(f"# Random rank-2: {len(rand_results)}")
    rkl_distr = {}
    for rkv, rkl, p00z, p10z, p01z, p11z in rand_results:
        rkl_distr[rkl] = rkl_distr.get(rkl, 0) + 1
    for rkl, cnt in sorted(rkl_distr.items()):
        print(f"  rk{{ψ_10,ψ_01}}={rkl}: {cnt} cases")


if __name__ == '__main__':
    main()
