"""probe_image_eq_Hline_fast.py — faster version using only syndrome computation.

For each above-Johnson f:
  1. Compute syndrome H g(α) for all α (no dist needed)
  2. Check linear rank r of syndrome image
  3. If r=1: check if image-line equals an H_j-line
"""
from __future__ import annotations
import sys, math, random
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


def normalize_line(v, p):
    """Normalize nonzero vector so first nonzero entry is 1."""
    for i, x in enumerate(v):
        if x != 0:
            inv = modinv(x, p)
            return tuple((y * inv) % p for y in v)
    return tuple(v)


def main():
    p = int(sys.argv[1]); n0 = int(sys.argv[2]); k0 = int(sys.argv[3])
    R = int(sys.argv[4]); delta = float(sys.argv[5])
    n_trials = int(sys.argv[6]) if len(sys.argv) > 6 else 200

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)
    H0 = chain[0][2]
    rho0 = k0 / n0
    w_J = int((1 - math.sqrt(rho0)) * n0)

    # Precompute normalized H-column lines
    H_lines = set()
    for j in range(n_R):
        H_j = [H_R[i][j] for i in range(n_R - k_R)]
        H_lines.add(normalize_line(H_j, p))

    print(f"# Setup: p={p}, n_0={n0}, k_0={k0}, R={R}, δ={delta}, w_J={w_J}")
    print(f"# H-lines (normalized, {len(H_lines)} total): {sorted(H_lines)[:5]}...")
    print()

    rng = random.Random(2026)
    n_above = 0
    n_r1 = 0  # rank-1 image cases
    n_image_eq_Hline = 0
    falsifiers = 0

    print(f"# Random fhat sweep ({n_trials} samples)...", flush=True)
    for trial in range(n_trials):
        sparsity = rng.choice([2, 3, 4, 5, 6])
        positions = rng.sample(range(k0, n0), sparsity)
        fhat = [0]*n0
        for pos in positions:
            fhat[pos] = rng.randrange(1, p)
        f = evaluate_dft(fhat, L0, p)
        d0, _ = dist_to_code_full(f, H0, n0, k0, p, max_w=w_J)
        if d0 is not None and d0 <= w_J:
            continue  # below-Johnson
        n_above += 1

        # Compute image of φ
        image_set = set()
        for alphas in product(range(p), repeat=R):
            g = true_fold_R(f, chain, list(alphas), p)
            syn = tuple(matvec(H_R, g, p))
            image_set.add(syn)

        nonzero_syns = [list(s) for s in image_set if any(x != 0 for x in s)]
        r = gauss_rank(nonzero_syns, p) if nonzero_syns else 0

        if r == 1:
            n_r1 += 1
            v_0 = nonzero_syns[0]
            v_0_norm = normalize_line(v_0, p)
            if v_0_norm in H_lines:
                n_image_eq_Hline += 1
                print(f"  ⚠ FOUND: trial {trial}, sparse_{sorted(positions)}, dist_C0={d0}, "
                      f"image_line normalized = {v_0_norm} ∈ H_lines", flush=True)

        if trial % 25 == 0:
            print(f"  trial {trial}: {n_above} above-J, {n_r1} rank-1, {n_image_eq_Hline} match", flush=True)

    print()
    print(f"# === SUMMARY ===")
    print(f"# Trials: {n_trials}, above-J: {n_above}, rank-1: {n_r1}, image=H-line: {n_image_eq_Hline}")
    if n_image_eq_Hline == 0:
        print(f"# *** No above-Johnson f with image = F_q·H_j across {n_above} above-J f's. ***")
        print(f"# *** Strong evidence: rank-1 image NEVER coincides with H-line for above-J f. ***")


if __name__ == '__main__':
    main()
