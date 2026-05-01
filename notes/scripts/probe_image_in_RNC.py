"""probe_image_in_RNC.py — test whether ANY above-Johnson f has image(φ) ⊂ Cone(RNC).

If image ⊆ Cone(RNC) AND image NOT confined to a single H-line, then
  V_δ = φ^{-1}(image ∩ B_1) could be larger than V_exact.
But empirically image ⊆ Cone(RNC) fully would violate the 2R q^{R-1} SZ bound
ONLY if image ⊆ B_1 (= H-lines).

Test: 1000 random above-J f's. For each, check if image(φ) ⊂ Cone(RNC) by testing
all 2x2 Hankel minors at all syndrome values.
"""
from __future__ import annotations
import sys, math, random
from itertools import product

sys.path.insert(0, '<repo>/notes/scripts')
from fri_2round_attack import (
    setup_chain, even_odd_parts, parity_check, matvec, dist_to_code_full
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


def all_hankel_minors_zero(syn, p):
    """Test if all 2x2 Hankel-style minors of syn vanish (i.e., syn ∈ Cone(RNC))."""
    m = len(syn)
    # σ_i σ_j - σ_k² for i + j = 2k
    for s in range(0, 2*(m-1) + 1):
        if s % 2 == 0:
            k = s // 2
            for a in range(max(0, s-m+1), min(m, s)+1):
                b = s - a
                if 0 <= a < b < m:
                    if (syn[a] * syn[b] - syn[k] * syn[k]) % p != 0:
                        return False
        # σ_a σ_b - σ_c σ_d for a+b = c+d, {a,b} ≠ {c,d}
        pairs = [(a, s-a) for a in range(max(0, s-m+1), min(m, s)+1) if 0 <= a < s-a < m]
        for i in range(len(pairs)):
            for j in range(i+1, len(pairs)):
                (a1, b1), (a2, b2) = pairs[i], pairs[j]
                if (syn[a1] * syn[b1] - syn[a2] * syn[b2]) % p != 0:
                    return False
    return True


def main():
    p = int(sys.argv[1]); n0 = int(sys.argv[2]); k0 = int(sys.argv[3])
    R = int(sys.argv[4])
    n_trials = int(sys.argv[5]) if len(sys.argv) > 5 else 200

    chain = setup_chain(p, n0, k0, R=R)
    L0, _, H0 = chain[0]
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)
    rho0 = k0 / n0
    w_J = int((1 - math.sqrt(rho0)) * n0)

    print(f"# Setup: p={p}, n_0={n0}, k_0={k0}, R={R}")
    print(f"# n_R={n_R}, k_R={k_R}, w_J={w_J}, m={n_R-k_R}")
    print(f"# Test: image(φ) ⊆ Cone(RNC)? Random above-J f sweep.")
    print()

    rng = random.Random(2026)
    n_above = 0
    n_image_in_RNC = 0
    n_image_in_RNC_above_J = 0

    for trial in range(n_trials):
        sparsity = rng.choice([2, 3, 4, 5, 6])
        positions = rng.sample(range(k0, n0), sparsity)
        fhat = [0]*n0
        for pos in positions:
            fhat[pos] = rng.randrange(1, p)
        f = evaluate_dft(fhat, L0, p)
        d0, _ = dist_to_code_full(f, H0, n0, k0, p, max_w=w_J)
        if d0 is not None and d0 <= w_J:
            continue  # below-J
        n_above += 1

        # Compute image and check if entirely in Cone(RNC)
        all_in_RNC = True
        for alphas in product(range(p), repeat=R):
            g = true_fold_R(f, chain, list(alphas), p)
            syn = matvec(H_R, g, p)
            if not all_hankel_minors_zero(syn, p):
                all_in_RNC = False
                break
        if all_in_RNC:
            n_image_in_RNC += 1
            n_image_in_RNC_above_J += 1
            print(f"  ★ FOUND: trial {trial}, sparse_{sorted(positions)}, dist_C0>{w_J}, image ⊆ Cone(RNC)", flush=True)

        if trial % 20 == 0:
            print(f"  trial {trial}: {n_above} above-J, {n_image_in_RNC_above_J} image⊆RNC", flush=True)

    print()
    print(f"# === SUMMARY ===")
    print(f"# Trials: {n_trials}, above-J: {n_above}")
    print(f"# Above-J with image ⊆ Cone(RNC): {n_image_in_RNC_above_J}")
    if n_image_in_RNC_above_J == 0:
        print(f"# *** No above-J f has image ⊆ Cone(RNC). RNC argument fully unconditional. ***")


if __name__ == '__main__':
    main()
