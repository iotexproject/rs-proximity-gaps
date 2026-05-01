"""verify_image_Hline_dist.py — verify note 0101 proof.

Construct f with image(φ) = F_q · H_{j*} for some j* (i.e., satisfy the structural
constraints) and confirm dist(f, C_0) ≤ 2^R.

Construction:
  - Pick j* ∈ [n_R]
  - Pick scalars λ_b for b ∈ {0,1}^R
  - Pick codeword constants for [0, k_R) parts (we set them to 0 for simplicity)
  - Set f̂[2^R · k + b_decoded] = λ_b · ω^{-j* k} for k ∈ [k_R, n_R)
  - Inverse DFT to get f
  - Verify dist(f, C_0)
"""
from __future__ import annotations
import sys, math, random
from itertools import product

sys.path.insert(0, '<repo>/notes/scripts')
from fri_2round_attack import (
    setup_chain, even_odd_parts, parity_check, matvec, dist_to_code_full, modinv,
    gauss_rank
)


def true_fold_R(f, chain, alphas, p):
    R = len(alphas)
    L_chain = [chain[i][0] for i in range(R + 1)]
    fold = list(f)
    for r in range(R):
        f_e, f_o = even_odd_parts(fold, L_chain[r], p)
        a = alphas[r]
        fold = [(f_e[j] + a * f_o[j]) % p for j in range(len(f_e))]
    return fold


def evaluate_dft(fhat, L0, p):
    n = len(fhat)
    return [sum(fhat[i] * pow(L0[j], i, p) for i in range(n)) % p for j in range(n)]


def main():
    p = int(sys.argv[1]); n0 = int(sys.argv[2]); k0 = int(sys.argv[3])
    R = int(sys.argv[4])

    chain = setup_chain(p, n0, k0, R=R)
    L0, _, H0 = chain[0]
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)
    rho0 = k0 / n0
    w_J = int((1 - math.sqrt(rho0)) * n0)
    bound_2R = 2**R

    # ω is primitive n_R-th root of unity used in L_R = chain[R].
    omega_R = L_R[1]  # ω = L_R[1] (first nontrivial element)

    print(f"# Setup: p={p}, n_0={n0}, k_0={k0}, R={R}")
    print(f"# n_R={n_R}, k_R={k_R}, ρ_0={rho0:.3f}, w_J={w_J}")
    print(f"# Predicted dist bound (note 0101): 2^R = {bound_2R}")
    print(f"# Above-Johnson requires dist > {w_J}")
    print(f"# Structural claim holds iff 2^R ({bound_2R}) ≤ w_J ({w_J}): {'YES' if bound_2R <= w_J else 'NO'}")
    print()

    rng = random.Random(2026)
    n_constructed = 0
    n_dist_le_2R = 0

    print(f"# Constructing f with image(φ) = F_q · H_{{j*}}: should give dist ≤ 2^R")
    print(f"# {'j*':>4s} {'λ_b':>30s} {'dist(f, C_0)':>14s} {'≤2^R?':>7s} {'image_rank':>10s}")
    print("-" * 80)

    # Try multiple j* and λ_b configurations
    for j_star in range(n_R):
        for trial in range(5):
            # Pick random nonzero λ_b for each b
            lam = [rng.randrange(1, p) for _ in range(2**R)]
            # Construct fhat
            fhat = [0] * n0
            for b_dec in range(2**R):
                for k in range(k_R, n_R):
                    pos = (1 << R) * k + b_dec
                    if pos < n0:
                        fhat[pos] = (lam[b_dec] * pow(omega_R, (-j_star * k) % n_R, p)) % p
            # Codeword part: keep zero for simplicity (so f̂[0..k_0) = 0).
            f = evaluate_dft(fhat, L0, p)

            # Compute image of φ for this f
            image_set = set()
            for alphas in product(range(p), repeat=R):
                g = true_fold_R(f, chain, list(alphas), p)
                syn = tuple(matvec(H_R, g, p))
                image_set.add(syn)
            nonzero_syns = [list(s) for s in image_set if any(x != 0 for x in s)]
            r = gauss_rank(nonzero_syns, p) if nonzero_syns else 0

            # Compute dist(f, C_0). Use max_w high enough.
            dist, _ = dist_to_code_full(f, H0, n0, k0, p, max_w=min(2**R + 2, n0))
            n_constructed += 1
            if dist is not None and dist <= bound_2R:
                n_dist_le_2R += 1
            mark = "✓" if (dist is not None and dist <= bound_2R) else "✗"
            d_str = f"{dist}" if dist is not None else f">{2**R+2}"
            print(f"  {j_star:>4d} {str(lam[:4]):>30s} {d_str:>14s} {mark:>7s} {r:>10d}")

    print("-" * 80)
    print(f"# Constructed: {n_constructed}, dist ≤ 2^R: {n_dist_le_2R}")
    if n_dist_le_2R == n_constructed:
        print(f"# *** Note 0101 proof CONFIRMED: ALL constructed f have dist ≤ 2^R = {bound_2R}. ***")
    else:
        print(f"# ★ Some f's exceeded 2^R bound — proof needs refinement.")


if __name__ == '__main__':
    main()
