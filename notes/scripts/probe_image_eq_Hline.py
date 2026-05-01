"""probe_image_eq_Hline.py — search for above-Johnson f with image(φ) = F_q · H_j
for some j ∈ [n_R]. Such f would FALSIFY the V_δ ≤ 2R q^{R-1} bound.

Construction: solve linear system on fhat enforcing each Q_b ∈ C_R + F_q · e_j*.
Then check: does this subspace contain any above-Johnson f?
"""
from __future__ import annotations
import sys, math
from itertools import product

sys.path.insert(0, '<repo>/notes/scripts')
from fri_2round_attack import (
    setup_chain, even_odd_parts, parity_check, matvec, gauss_rank, modinv,
    dist_to_code_full
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
    R = int(sys.argv[4]); delta = float(sys.argv[5])

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)
    H0 = chain[0][2]
    w_R = int(delta * n_R)
    qR = p ** R
    rho0 = k0 / n0
    w_J = int((1 - math.sqrt(rho0)) * n0)

    print(f"# Setup: p={p}, n_0={n0}, k_0={k0}, R={R}, δ={delta}")
    print(f"# n_R={n_R}, k_R={k_R}, w_R={w_R}, w_J={w_J}, q^R={qR}")
    print(f"# Searching for f with image(φ) = F_q · H_{{j*}} for some j*")
    print()

    # For each j*: enumerate fhat such that Q_b ∈ C_R + F_q · e_{j*} for each b.
    # This is a linear constraint on fhat. We'll set up the constraint matrix
    # and find its kernel, then sample for above-Johnson elements.

    # Brute approach: random fhat with sparsity, compute true image dim, check if = 1
    # AND if image-line coincides with F_q · H_j for some j.
    import random
    rng = random.Random(2026)
    n_tested = 0
    n_above = 0
    n_image_eq_Hline = 0
    falsifiers = 0
    max_above_J_match = 0

    print(f"# Random fhat sweep ({200} samples)...", flush=True)
    for trial in range(200):
        sparsity = rng.choice([2, 3, 4, 5, 6])
        positions = rng.sample(range(k0, n0), sparsity)
        fhat = [0]*n0
        for pos in positions:
            fhat[pos] = rng.randrange(1, p)
        f = evaluate_dft(fhat, L0, p)
        # Quick above-Johnson check: dist > w_J means we don't find any low-weight error
        d0, _ = dist_to_code_full(f, H0, n0, k0, p, max_w=w_J)
        if d0 is None:
            d0_str = f">{w_J}"
            n_above += 1
        else:
            continue  # below-Johnson
        n_tested += 1
        if trial % 20 == 0:
            print(f"  trial {trial}: above-J found ({n_tested} so far)", flush=True)

        # Compute image of φ
        image_set = set()
        v_delta = 0
        for alphas in product(range(p), repeat=R):
            g = true_fold_R(f, chain, list(alphas), p)
            syn = tuple(matvec(H_R, g, p))
            image_set.add(syn)
            d, _ = dist_to_code_full(g, H_R, n_R, k_R, p, max_w=w_R)
            if d is not None and d <= w_R:
                v_delta += 1

        # Linear rank of image
        nonzero_syns = [list(s) for s in image_set if any(x != 0 for x in s)]
        r = gauss_rank(nonzero_syns, p) if nonzero_syns else 0

        # If r=1: check if image-line equals an H-line
        if r == 1:
            # Image is F_q · v_0 for some nonzero v_0
            v_0 = nonzero_syns[0]
            # Normalize v_0 (make first nonzero entry = 1)
            for i, x in enumerate(v_0):
                if x != 0:
                    inv = modinv(x, p)
                    v_0_norm = tuple((y * inv) % p for y in v_0)
                    break
            # Check if v_0_norm coincides with any normalized H_j
            for j in range(n_R):
                H_j = [H_R[i][j] for i in range(n_R - k_R)]
                for i, x in enumerate(H_j):
                    if x != 0:
                        inv = modinv(x, p)
                        H_j_norm = tuple((y * inv) % p for y in H_j)
                        break
                if v_0_norm == H_j_norm:
                    n_image_eq_Hline += 1
                    print(f"  ⚠ FOUND: trial {trial}, f sparse_{sorted(positions)} (dist {d0}), "
                          f"image = F_q · H_{j}, V_δ = {v_delta}", flush=True)
                    if v_delta > 2 * R * p**(R-1):
                        falsifiers += 1
                        print(f"    ★ FALSIFIES 2R q^{{R-1}} bound: {v_delta} > {2*R*p**(R-1)} ★", flush=True)
                    break

    print()
    print(f"# === SUMMARY ===")
    print(f"# Random samples: 1000")
    print(f"# Above-Johnson: {n_tested}")
    print(f"# Image = H-line: {n_image_eq_Hline}")
    print(f"# Falsifiers of 2R q^{{R-1}}: {falsifiers}")
    if n_image_eq_Hline == 0:
        print(f"# *** No above-Johnson f with image = F_q·H_j found across {n_tested} trials. ***")


if __name__ == '__main__':
    main()
