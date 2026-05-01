"""verify_lift_extension.py — empirical verification of note 0112's σ-image-in-V_T lift extension.

Theorem: If σ(α) ∈ V_T for all α (where V_T = im(H_R[:, T]), |T| ≤ w_R), then
dist(f, C_0) ≤ 2^R · w_R.

Proof generalizes note 0111: witnesses {e*_b}_b ALL supported on the same T (instead of
a single e*). Construction uses positions i*_{b,s} = s + n_R |b|_2 for b ∈ {0,1}^R, s ∈ T.

This script:
  1. Pick a random support T ⊆ [n_R] with |T| = w (w ≤ w_R).
  2. Pick random witnesses e*_b ∈ F_q^{n_R} for each b ∈ {0,1}^R, all with supp ⊆ T.
  3. Construct f via (★_ext): f̂_{j·2^R + |b|_2} = (ê*_b)_j for j ∈ [k_R, n_R), with arbitrary
     fhat in [0, k_0).
  4. Solve for μ_{b,s} via the inverse DFT formula.
  5. Build e and verify f - e ∈ C_0 with wt(e) ≤ 2^R · w.

This is the case σ(α) is bidegree-(1,...,1) with image ⊆ V_T (witness varies with b).
"""
from __future__ import annotations
import sys, os, math, random
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain
# Reuse helpers from verify_rank1_lift
from verify_rank1_lift import (
    P, N0, K0, R, N_R, K_R, M_R, W_R_BOUND, W_J,
    b_to_int, build_f_from_fhat, compute_fhat,
)


def construct_f_image_in_VT(omega, p, n0, k0, R, T, e_star_b_dict):
    """Build f ∈ F_p^{n_0} satisfying:
        fhat_{j·2^R + |b|_2} = (ê*_b)_j  for j ∈ [k_R, n_R), b ∈ {0,1}^R
       where each e*_b ∈ F_p^{n_R} has supp ⊆ T.
       Arbitrary fhat values on [0, k_0).
    """
    n_R = n0 // (2**R)
    k_R = k0 // (2**R)
    omega_R = pow(omega, 2**R, p)

    # Compute ê*_b for each b (length n_R DFT under codebase convention).
    e_star_hat_b = {}
    for b in product([0, 1], repeat=R):
        e_b = e_star_b_dict[b]
        ehat = []
        for j in range(n_R):
            s = 0
            wj = pow(omega_R, -j % (p - 1), p)
            for l in range(n_R):
                if e_b[l]:
                    s = (s + e_b[l] * pow(wj, l, p)) % p
            ehat.append(s)
        e_star_hat_b[b] = ehat

    rng = random.Random(0)
    fhat = [rng.randrange(p) for _ in range(n0)]
    for b in product([0, 1], repeat=R):
        b_idx = b_to_int(b)
        for j in range(k_R, n_R):
            idx = j * (2**R) + b_idx
            fhat[idx] = e_star_hat_b[b][j]
    f = build_f_from_fhat(fhat, omega, n0, p)
    return f, fhat, e_star_hat_b


def construct_error_e_extension(e_star_b_dict, T, p, n0, R, omega):
    """Build e = sum_{b, s ∈ T} μ_{b,s} 1_{i*_{b,s}} via the extension formula.

    μ_{b,s} = (1/2^R) · sum_{b'} (e*_{b'})_s · ω^{s|b'|_2} · ζ^{|b|_2 |b'|_2}.
    """
    n_R = n0 // (2**R)
    omega_R = pow(omega, 2**R, p)
    zeta = pow(omega, n_R, p)
    inv_2R = pow(2**R, p - 2, p)

    e = [0] * n0
    for b in product([0, 1], repeat=R):
        b_idx = b_to_int(b)
        for s in T:
            total = 0
            for bp in product([0, 1], repeat=R):
                bp_idx = b_to_int(bp)
                term = (e_star_b_dict[bp][s] * pow(omega, s * bp_idx, p) * pow(zeta, b_idx * bp_idx, p)) % p
                total = (total + term) % p
            mu = (inv_2R * total) % p
            i_star = s + n_R * b_idx
            assert e[i_star] == 0, f"position collision at {i_star}"
            e[i_star] = mu
    weight = sum(1 for x in e if x != 0)
    return e, weight


def trial(seed, omega, p, n0, k0, R, w):
    """One trial: random T of size w, random witnesses e*_b supported on T per b."""
    rng = random.Random(seed)
    n_R = n0 // (2**R)

    T = sorted(rng.sample(range(n_R), w))
    # Random witnesses e*_b ∈ F_p^{n_R}, supp ⊆ T, for each b.
    # Make some witnesses nonzero to ensure non-trivial test.
    e_star_b_dict = {}
    while True:
        for b in product([0, 1], repeat=R):
            e_b = [0] * n_R
            for s in T:
                e_b[s] = rng.randrange(p)
            e_star_b_dict[b] = e_b
        if any(any(e_star_b_dict[b][s] != 0 for s in T) for b in e_star_b_dict):
            break

    f, fhat, e_star_hat_b = construct_f_image_in_VT(omega, p, n0, k0, R, T, e_star_b_dict)
    e, wt_e = construct_error_e_extension(e_star_b_dict, T, p, n0, R, omega)

    e_hat = compute_fhat(e, omega, n0, p)
    syndrome_match = all(e_hat[i] == fhat[i] for i in range(k0, n0))

    f_minus_e = [(f[i] - e[i]) % p for i in range(n0)]
    fme_hat = compute_fhat(f_minus_e, omega, n0, p)
    in_C0 = all(fme_hat[i] == 0 for i in range(k0, n0))

    return {
        'seed': seed, 'w': w, 'wt_e': wt_e, 'wt_e_bound': (2**R) * w,
        'wt_e_within_bound': wt_e <= (2**R) * w,
        'syndrome_match': syndrome_match,
        'f_minus_e_in_C0': in_C0,
    }


def main():
    chain = setup_chain(P, N0, K0, R=R)
    omega = chain[0][0][1]

    print(f"# verify_lift_extension — empirical sanity check for note 0112 lift extension")
    print(f"# Setup: p={P}, n_0={N0}, k_0={K0}, R={R}, n_R={N_R}, w_R={W_R_BOUND}")
    print(f"# Theorem: σ image ⊆ V_T (any |T| ≤ w_R) ⇒ dist(f, C_0) ≤ 2^R · w_R = {2**R * W_R_BOUND}")
    print()

    n_trials_per_w = 30
    total_pass = 0; total = 0
    for w in range(1, W_R_BOUND + 1):
        print(f"## Trials at w = {w}")
        passes = 0
        for k in range(n_trials_per_w):
            r = trial(seed=2000 * w + k, omega=omega, p=P, n0=N0, k0=K0, R=R, w=w)
            ok = r['wt_e_within_bound'] and r['syndrome_match'] and r['f_minus_e_in_C0']
            if ok: passes += 1
            else: print(f"  ✗ seed={r['seed']}: {r}")
        print(f"  → {passes}/{n_trials_per_w} pass; max possible wt_e = {(2**R)*w}")
        total_pass += passes; total += n_trials_per_w

    print()
    print(f"# TOTAL: {total_pass}/{total} trials confirm lift extension")
    if total_pass == total:
        print("# ✓ ALL PASS — lift extension theorem (note 0112) holds for all (T, {e*_b}) configs.")
    else:
        print("# ✗ SOME FAILED — bug in proof or implementation.")


if __name__ == '__main__':
    main()
