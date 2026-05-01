"""probe_image_in_Bw.py — does any above-J f have image(φ) ⊆ B_w for general w?

If 0/N for above-J f's: empirical support for Path γ structural claim.

Uses fast in-line distance check (only check if dist ≤ w_test).
"""
from __future__ import annotations
import sys, math, random
from itertools import product, combinations

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


def main():
    p = int(sys.argv[1]); n0 = int(sys.argv[2]); k0 = int(sys.argv[3])
    R = int(sys.argv[4]); w_test = int(sys.argv[5])
    n_trials = int(sys.argv[6]) if len(sys.argv) > 6 else 100

    chain = setup_chain(p, n0, k0, R=R)
    L0, _, H0 = chain[0]
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)
    rho0 = k0 / n0
    w_J = int((1 - math.sqrt(rho0)) * n0)

    print(f"# Setup: p={p}, n_0={n0}, k_0={k0}, R={R}, w_test={w_test}")
    print(f"# n_R={n_R}, k_R={k_R}, m={n_R-k_R}, w_J={w_J}")
    print(f"# Conjecture: NO above-J f has image(φ) ⊆ B_{{w_test}}")
    print()

    rng = random.Random(2026)
    n_above = 0
    n_image_in_Bw = 0

    for trial in range(n_trials):
        sparsity = rng.choice([2, 3, 4, 5, 6])
        positions = rng.sample(range(k0, n0), sparsity)
        fhat = [0]*n0
        for pos in positions:
            fhat[pos] = rng.randrange(1, p)
        f = evaluate_dft(fhat, L0, p)
        d0, _ = dist_to_code_full(f, H0, n0, k0, p, max_w=w_J)
        if d0 is not None and d0 <= w_J:
            continue
        n_above += 1

        # Test: for each α, dist(g(α), C_R) ≤ w_test?
        all_in_Bw = True
        for alphas in product(range(p), repeat=R):
            g = true_fold_R(f, chain, list(alphas), p)
            d, _ = dist_to_code_full(g, H_R, n_R, k_R, p, max_w=w_test)
            if d is None or d > w_test:
                all_in_Bw = False
                break
        if all_in_Bw:
            n_image_in_Bw += 1
            print(f"  ★ FOUND: trial {trial}, sparse_{sorted(positions)}, dist_C0>{w_J}, image ⊆ B_{w_test}", flush=True)

        if trial % 20 == 0:
            print(f"  trial {trial}: {n_above} above-J, {n_image_in_Bw} image⊆B_w", flush=True)

    print()
    print(f"# === SUMMARY ===")
    print(f"# Trials: {n_trials}, above-J: {n_above}")
    print(f"# Above-J with image ⊆ B_{w_test}: {n_image_in_Bw}")
    if n_image_in_Bw == 0:
        print(f"# *** No above-J f has image ⊆ B_{w_test}. Path γ structural claim supported. ***")


if __name__ == '__main__':
    main()
