"""verify_rank1_lift.py — empirical verification of note 0111's constructive DFT lift.

Theorem (note 0111): If σ-rank(f) = 1 with σ(α) = P(α)·u, u = H_R · e*, wt(e*) = w,
then dist(f, C_0) ≤ 2^R · w.

The proof is constructive: it gives an explicit error e ∈ F_q^{n_0} of weight ≤ 2^R w with
f - e ∈ C_0, via positions i*_{b,s} = s + n_R · |b|_2 and coefficients μ_{b,s} solving a
2^R × 2^R DFT system per s ∈ supp(e*).

This script:
  1. Picks a witness e* ∈ F_q^{n_R} with wt = w ≤ w_R.
  2. Picks 2^R scalars p_b for the bidegree-(1,…,1) polynomial P.
  3. Constructs f via the formula (★): f̂_{j·2^R + |b|_2} = p_b · ê*_j on syndrome window;
     fills [0, k_0) with arbitrary values (so dist(f, C_0) is well-defined and "above-J-like").
  4. Computes μ_{b,s} via the inverse DFT formula.
  5. Builds e and verifies (a) wt(e) ≤ 2^R w, (b) f̂ matches ê on syndrome window.
  6. Confirms dist(f, C_0) ≤ wt(e).

Repeats over many random (e*, P) configurations.
"""
from __future__ import annotations
import sys, os, math, random
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, parity_check, dist_to_code_full

P = 97
N0 = 32
K0 = 8
R = 2
N_R = N0 // (2**R)        # 8
K_R = K0 // (2**R)        # 2
M_R = N_R - K_R           # 6
W_R_BOUND = 3             # max witness weight tested
W_J = int((1 - math.sqrt(K0/N0)) * N0)  # 16


def b_to_int(b):
    """|b|_2 = sum_r b_r 2^{r-1}, with r=1..R."""
    return sum(bi * (2**i) for i, bi in enumerate(b))


def dft_eval(coeffs, omega_pow_minus_jk_table, n, p):
    """Compute f_l = sum_{i=0}^{n-1} fhat_i * omega^{i l} via table.
    Here we just use direct DFT for clarity."""
    return None  # not used; we go directly via fhat


def ifft_via_invmatrix(omega, n, p):
    """Build the IDFT matrix entries for use later (small n, brute force OK)."""
    # IDFT: f_l = (1/n) sum_j fhat_j omega^{j l}
    return None


def build_f_from_fhat(fhat, omega, n, p):
    """f(omega^l) = sum_j fhat_j * omega^{j l}, l=0..n-1. (No 1/n normalization, so
    we are using the same convention as fri_2round_attack: fhat_i = sum_l f(omega^l) omega^{-i l},
    f(omega^l) = (1/n) sum_i fhat_i omega^{i l}.)

    To match the convention in the codebase: use 1/n.
    """
    inv_n = pow(n, p - 2, p)
    f = [0] * n
    for l in range(n):
        s = 0
        wl = pow(omega, l, p)
        # f_l = (1/n) sum_i fhat_i * omega^{i l}
        for i, c in enumerate(fhat):
            if c:
                s = (s + c * pow(wl, i, p)) % p
        f[l] = (inv_n * s) % p
    return f


def compute_fhat(f, omega, n, p):
    """Inverse: fhat_i = sum_l f_l * omega^{-i l}."""
    fhat = []
    for i in range(n):
        s = 0
        wi = pow(omega, -i % (p - 1), p)
        for l in range(n):
            if f[l]:
                s = (s + f[l] * pow(wi, l, p)) % p
        fhat.append(s)
    return fhat


def construct_f_rank1(omega, p, n0, k0, R, e_star, p_coefs):
    """Build f ∈ F_p^{n_0} satisfying:
        fhat_{j*2^R + |b|_2} = p_b · ê*_j  for j ∈ [k_R, n_R), b ∈ {0,1}^R
       with arbitrary fhat values on [0, k_0). Returns (f, fhat).

    Args:
      e_star: list of length n_R = n0 // 2^R, the witness in F_p^{n_R}.
      p_coefs: dict b_tuple -> p_b in F_p, indexed by b ∈ {0,1}^R.
    """
    n_R = n0 // (2**R)
    k_R = k0 // (2**R)
    omega_R = pow(omega, 2**R, p)  # primitive n_R-th root

    # Compute ê* (length n_R) under the same convention as the codebase.
    e_star_hat = []
    for j in range(n_R):
        s = 0
        wj = pow(omega_R, -j % (p - 1), p)
        for l in range(n_R):
            if e_star[l]:
                s = (s + e_star[l] * pow(wj, l, p)) % p
        e_star_hat.append(s)

    # Build fhat. Initialize with random values on [0, k_0); fill syndrome window per (★).
    rng = random.Random(0)  # deterministic for reproducibility within this call
    fhat = [rng.randrange(p) for _ in range(n0)]
    for b in product([0, 1], repeat=R):
        b_idx = b_to_int(b)
        p_b = p_coefs[b]
        for j in range(k_R, n_R):
            idx = j * (2**R) + b_idx
            fhat[idx] = (p_b * e_star_hat[j]) % p

    f = build_f_from_fhat(fhat, omega, n0, p)
    return f, fhat, e_star_hat


def construct_error_e(p_coefs, e_star, p, n0, R, omega):
    """Build e = sum_{b,s} μ_{b,s} 1_{i*_{b,s}} via formula from note 0111.

    Returns e (list length n0) and weight (number of nonzero entries).
    """
    n_R = n0 // (2**R)
    omega_R = pow(omega, 2**R, p)
    zeta = pow(omega, n_R, p)  # primitive 2^R-th root
    inv_2R = pow(2**R, p - 2, p)

    S = [s for s in range(n_R) if e_star[s] != 0]
    e = [0] * n0
    for b in product([0, 1], repeat=R):
        b_idx = b_to_int(b)
        for s in S:
            # μ_{b,s} = (e*_s / 2^R) * sum_{b'} p_{b'} (omega^s · zeta^{|b|_2})^{|b'|_2}
            base = (pow(omega, s, p) * pow(zeta, b_idx, p)) % p
            total = 0
            for bp in product([0, 1], repeat=R):
                bp_idx = b_to_int(bp)
                total = (total + p_coefs[bp] * pow(base, bp_idx, p)) % p
            mu = (e_star[s] * inv_2R * total) % p
            i_star = s + n_R * b_idx
            assert e[i_star] == 0, f"position collision at {i_star}"
            e[i_star] = mu
    weight = sum(1 for x in e if x != 0)
    return e, weight


def trial(seed, omega, p, n0, k0, R, w):
    """One trial: random e* of weight w, random p_b. Verify f - e ∈ C_0."""
    rng = random.Random(seed)
    n_R = n0 // (2**R)

    # Random e* with exactly weight w (avoid trivial all-zero by ensuring nonzero coefs)
    S = sorted(rng.sample(range(n_R), w))
    e_star = [0] * n_R
    for s in S:
        e_star[s] = rng.randrange(1, p)

    # Random p_b in F_p. Don't force them all nonzero; we just want at least one nonzero.
    while True:
        p_coefs = {b: rng.randrange(p) for b in product([0, 1], repeat=R)}
        if any(p_coefs[b] != 0 for b in p_coefs):
            break

    f, fhat, e_star_hat = construct_f_rank1(omega, p, n0, k0, R, e_star, p_coefs)
    e, wt_e = construct_error_e(p_coefs, e_star, p, n0, R, omega)

    # Verify: fhat[k0:n0] == ehat[k0:n0] (e's DFT on syndrome window matches f's).
    e_hat = compute_fhat(e, omega, n0, p)
    syndrome_match = all(e_hat[i] == fhat[i] for i in range(k0, n0))

    f_minus_e = [(f[i] - e[i]) % p for i in range(n0)]
    fme_hat = compute_fhat(f_minus_e, omega, n0, p)
    in_C0 = all(fme_hat[i] == 0 for i in range(k0, n0))

    return {
        'seed': seed,
        'w': w,
        'wt_e': wt_e,
        'wt_e_bound': (2**R) * w,
        'wt_e_within_bound': wt_e <= (2**R) * w,
        'syndrome_match': syndrome_match,
        'f_minus_e_in_C0': in_C0,
    }


def main():
    chain = setup_chain(P, N0, K0, R=R)
    omega = chain[0][0][1]  # generator of L_0 = pow(g, (p-1)/n0, p)

    print(f"# verify_rank1_lift — empirical sanity check for note 0111 theorem")
    print(f"# Setup: p={P}, n_0={N0}, k_0={K0}, R={R}, n_R={N_R}, w_R={W_R_BOUND}")
    print(f"# Predicted: dist(f, C_0) ≤ 2^R · w = {2**R} · w  for all rank-1 f with witness e* of wt w")
    print(f"# omega = {omega}")
    print()

    n_trials_per_w = 30
    total_pass = 0
    total = 0
    for w in range(1, W_R_BOUND + 1):
        print(f"## Trials at w = {w}")
        passes = 0
        for k in range(n_trials_per_w):
            r = trial(seed=1000 * w + k, omega=omega, p=P, n0=N0, k0=K0, R=R, w=w)
            ok = r['wt_e_within_bound'] and r['syndrome_match'] and r['f_minus_e_in_C0']
            if ok:
                passes += 1
            else:
                print(f"  ✗ seed={r['seed']}: {r}")
        print(f"  → {passes}/{n_trials_per_w} pass; max possible wt_e = {(2**R)*w}")
        total_pass += passes
        total += n_trials_per_w

    print()
    print(f"# TOTAL: {total_pass}/{total} trials confirm constructive lift")
    if total_pass == total:
        print("# ✓ ALL PASS — note 0111 theorem holds constructively for every (e*, P) config tested.")
    else:
        print("# ✗ SOME FAILED — bug in proof or implementation.")


if __name__ == '__main__':
    main()
